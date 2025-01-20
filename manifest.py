#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import pwd
import sys
sys.dont_write_bytecode = True

from copy import deepcopy
from pathlib import Path
from fnmatch import fnmatch
from contextlib import contextmanager
from argparse import ArgumentParser, Action
from ruamel.yaml import YAML

from leatherman.fuzzy import fuzzy
from leatherman.repr import __repr__

REAL_FILE = os.path.abspath(__file__)
REAL_NAME = os.path.basename(REAL_FILE)
REAL_PATH = os.path.dirname(REAL_FILE)
if os.path.islink(__file__):
    LINK_FILE = REAL_FILE; REAL_FILE = os.path.abspath(os.readlink(__file__))
    LINK_NAME = REAL_NAME; REAL_NAME = os.path.basename(REAL_FILE)
    LINK_PATH = REAL_PATH; REAL_PATH = os.path.dirname(REAL_FILE)

SECTIONS = [
    'link',
    'ppa',
    'apt',
    'dnf',
    'npm',
    'pip3',
    'pipx',
    'flatpak',
    'cargo',
    'github',
    'script',
]

UID = os.getuid()
GID = pwd.getpwuid(UID).pw_gid
USER = pwd.getpwuid(UID).pw_name
HOME = pwd.getpwuid(UID).pw_dir

DEBUG = r'''
if [ -n "$DEBUG" ]; then
    PS4=':${LINENO}+'
    set -x
fi
'''.lstrip('\n').rstrip()

LINKER = r'''
linker() {
    file=$(realpath "$1")
    link="${2/#\~/$HOME}"
    echo "$link -> $file"
    if [ -f "$link" ] && [ "$file" != "$(readlink $link)" ]; then
        orig="$link.orig"
        $VERBOSE && echo "backing up $orig"
        mv $link $orig
    elif [ ! -f "$link" ] && [ -L "$link" ]; then
        $VERBOSE && echo "removing broken link $link"
        unlink $link
    fi
    if [ -f "$link" ]; then
        echo "[exists] $link"
    else
        echo "[create] $link -> $file"
        mkdir -p $(dirname $link); ln -s $file $link
    fi
}
'''.lstrip('\n').rstrip()

LATEST = r'''
latest() {
    PATTERN="$1"
    LATEST="$2"
    NAME="${3:-"$PATTERN"}"
    echo "Fetching latest release from: $LATEST"
    echo "Using pattern: $PATTERN"
    # Correctly quote the pattern within the jq command
    URL="$(curl -sL "$LATEST" | jq -r ".assets[] | select(.name | test(\\\"$PATTERN\\\")) | .browser_download_url")"
    if [[ -z "$URL" ]]; then
        echo "No URL found for pattern: $PATTERN"
        exit 1
    fi
    echo "Downloading from URL: $URL"
    FILENAME=$(basename "$URL")
    TMPDIR=$(mktemp -d /tmp/manifest.XXXXXX)
    pushd "$TMPDIR"
    curl -sSL "$URL" -o "$FILENAME"
    echo "Downloaded $FILENAME"
    # Adjust the extraction command based on file extension
    if [[ "$FILENAME" =~ \.tar\.gz$ ]]; then
        tar xzf "$FILENAME"
        echo "Extracted $FILENAME using tar xzf"
    elif [[ "$FILENAME" =~ \.tbz$ ]]; then
        tar xjf "$FILENAME"
        echo "Extracted $FILENAME using tar xjf"
    fi
    # Use find to locate the binary and ensure it's executable
    BINARY=$(find . -type f -name "$NAME" -exec chmod a+x {} + -print)
    if [[ -z "$BINARY" ]]; then
        echo "No binary found named $NAME"
        exit 1
    fi
    mv "$BINARY" ~/bin/
    echo "Moved $BINARY to ~/bin/"
    popd
    rm -rf "$TMPDIR"
    echo "Cleaned up temporary directory $TMPDIR"
}
'''.lstrip('\n').rstrip()

class UnknownPkgmgrError(Exception):
    def __init__(self):
        super(UnknownPkgmgrError, self).__init__('unknown pkgmgr!')

@contextmanager
def cd(*args, **kwargs):
    mkdir = kwargs.pop('mkdir', True)
    verbose = kwargs.pop('verbose', False)
    path = os.path.sep.join(args)
    path = os.path.normpath(path)
    path = os.path.expanduser(path)
    prev = os.getcwd()
    if path != prev:
        if mkdir:
            os.system(f'mkdir -p {path}')
        os.chdir(path)
        curr = os.getcwd()
        sys.path.append(curr)
        if verbose:
            print(f'cd {curr}')
    try:
        yield
    finally:
        if path != prev:
            sys.path.remove(curr)
            os.chdir(prev)
            if verbose:
                print('cd {prev}')

def check_hash(program):
    from subprocess import check_call, CalledProcessError, PIPE
    try:
        check_call(f'hash {program}', shell=True, stdout=PIPE, stderr=PIPE)
        return True
    except CalledProcessError:
        return False

def get_pkgmgr():
    if check_hash('dpkg'):
        return 'deb'
    elif check_hash('rpm'):
        return 'rpm'
    elif check_hash('brew'):
        return 'brew'
    raise UnknownPkgmgrError

def render_item(item):
    if isinstance(item, tuple):
        return ' '.join(item)
    return str(item)

class ManifestType():
    def __repr__(self):
        return f'{type(self).__name__}(items = {self.items})'

    __str__ = __repr__

    def functions(self):
        return ''

    def render(self):
        raise NotImplementedError

class PackageType(ManifestType):
    def __init__(self, spec, patterns, **kwargs):
        self.items = fuzzy(spec.get('items', {})).include(*patterns)

    def __repr__(self):
        return f'{type(self).__name__}(items={self.items})'

    __str__ = __repr__

    def render_header(self):
        return f'''
echo "{type(self).__name__.lower()}s:"
        '''.lstrip('\n').rstrip()

    def render_block(self):
        raise NotImplementedError

class HeredocPackageType(PackageType):
    def render_items(self):
        return '\n'.join([render_item(item) for item in self.items])

    def render(self):
        return f'''
{self.render_header()}

while read pkg; do
{self.render_block()}
done<<EOM
{self.render_items()}
EOM
        '''.lstrip('\n').rstrip()

class ContinuePackageType(PackageType):
    def render_items(self):
        return ' \\\n    '.join([render_item(item) for item in self.items])

    def render(self):
        return f'''
{self.render_header()}

{self.render_block()} {self.render_items()}
        '''.lstrip('\n').rstrip()

def path2str(func):
    def wrapper(*args, **kwargs):
        args = map(lambda p: p.as_posix() if isinstance(p, Path) else p, args)
        return func(*args, **kwargs)
    return wrapper

@path2str
def divine_src(filepath, cwd):
    return os.path.join(cwd, filepath)
@path2str
def divine_dst(filepath, srcpath, dstpath):
    return re.sub(srcpath, dstpath, filepath)
@path2str
def interpolate_home(filepath, home):
    return re.sub(r'\$HOME', home, filepath)
@path2str
def interpolate_root(filepath, root='/'):
    return re.sub('ROOT', root, filepath)

class Link(HeredocPackageType):
    def __init__(self, spec, patterns, cwd=None, root='/', home=None, **kwargs):
        self.cwd = cwd
        self.root = root
        self.home = home
        self.recursive = spec.pop('recursive', False)
        if self.recursive:
            self.items = []
            for srcpath, dstpath in spec.items():
                items = [
                    item.relative_to(self.cwd)
                    for item in Path(os.path.join(self.cwd, srcpath)).rglob('*')
                    if not item.is_dir()
                ]
                for item in items:
                    src = divine_src(item, cwd)
                    dst = divine_dst(item, srcpath, dstpath)
                    dst = interpolate_root(dst, root)
                    dst = interpolate_home(dst, home)
                    self.items += [(src, dst)]
        else:
            self.items = [(os.path.join(cwd, src), interpolate_home(dst, home)) for src, dst in spec.items()]

    def __repr__(self):
        return f'{type(self).__name__}(recursive={self.recursive}, items={self.items})'

    __str__ = __repr__

    def functions(self):
        return LINKER

    def render(self):
        return f'''
echo "links:"
while read -r file link; do
    linker $file $link
done<<EOM
{self.render_items()}
EOM
        '''.lstrip('\n').rstrip()

class APT(ContinuePackageType):
    def render_header(self):
        return f'''
{PackageType.render_header(self)}

sudo apt update && sudo apt upgrade -y && sudo apt install -y software-properties-common
        '''.lstrip('\n').rstrip()

    def render_block(self):
        return '''
sudo apt install -y
        '''.lstrip('\n').rstrip()

class DNF(ContinuePackageType):
    def render_block(self):
        return '''
    sudo dnf install -y $pkg
        '''.lstrip('\n').rstrip()

class PPA(HeredocPackageType):
    def render_block(self):
        if not self.items:
            return ''
        return f'''
    ppas=$(find /etc/apt/ -name *.list | xargs cat | grep ^[[:space:]]*deb | grep -v deb-src)
    if [[ $ppas != *"$pkg"* ]]; then
        sudo add-apt-repository -y "ppa:$pkg"
    fi
'''.lstrip('\n').rstrip()

class NPM(ContinuePackageType):
    def render_block(self):
        return f'''
sudo npm install -g
'''.lstrip('\n').rstrip()

class PIP3(ContinuePackageType):
    def render_header(self):
        return f'''
{PackageType.render_header(self)}

sudo apt-get install -y python3-dev
sudo -H pip3 install --upgrade pip setuptools
'''.lstrip('\n').rstrip()

    def render_block(self):
        return f'''
sudo -H pip3 install --upgrade
'''.lstrip('\n').rstrip()

class PIPX(HeredocPackageType):
    def render_block(self):
        if not self.items:
            return ''
        return '''
    pipx install $pkg
'''.lstrip('\n').rstrip()

class FLATPAK(ContinuePackageType):
    def render_block(self):
        return f'''
flatpak install --assumeyes --or-update
'''.lstrip('\n').rstrip()

class Cargo(ContinuePackageType):
    def render_block(self):
        return f'''
cargo install
'''.lstrip('\n').rstrip()

class Repo():
    def __init__(self, baseurl, reponame, spec, repopath, **kwargs):
        self.baseurl = baseurl
        self.reponame = reponame
        self.repopath = repopath
        self.cwd = kwargs.pop('cwd')
        cwd = os.path.join(self.cwd, repopath, reponame)
        self.link = Link(
            spec.get('link'),
            None,
            cwd=os.path.join(self.cwd, 'repos', self.reponame),
            **kwargs) if 'link' in spec else None
        self.script = Script(
            dict(reponame=spec.get('script')),
            None,
            **kwargs) if 'script' in spec else None

    __repr__ = __repr__

    __str__ = __repr__

    def render(self):
        link = self.link.render() + '\n' if self.link else ''
        script = self.script.render() + '\n' if self.script else ''
        fullpath = os.path.join(self.cwd, self.repopath, self.reponame)
        return f'''
echo "{self.reponame}:"
git clone --recursive {self.baseurl}/{self.reponame} {fullpath}
(cd {fullpath} && pwd && git pull && git checkout HEAD)
{link}
{script}
'''.lstrip('\n').rstrip()

class Github(ManifestType):
    def __init__(self, spec, patterns, **kwargs):
        repopath = spec.pop('repopath', 'repos')
        self.repos = [
            Repo('https://github.com', reponame, repobody, repopath, **kwargs)
            for reponame, repobody in fuzzy(spec).include(*patterns).items()
        ]

    def __repr__(self):
        return f'{type(self).__name__}(repos={self.repos})'

    __str__ = __repr__

    def functions(self):
        return LINKER

    def render(self):
        if not self.repos:
            return ''
        return 'echo "github repos:"\n\n' + '\n\n'.join([repo.render() for repo in self.repos]).strip()

class Script(ManifestType):
    def __init__(self, spec, patterns, **kwargs):
        self.items = fuzzy(spec).include(*patterns)

    def __repr__(self):
        return f'{type(self).__name__}(items={self.items})'

    __str__ = __repr__

    def functions(self):
        return LATEST

    def render(self):
        if not self.items:
            return ''
        return 'echo "scripts:"\n\n' +  '\n\n'.join([f"echo \"{name}:\"\n{script}\n" for name, script in self.items.items()])

class Manifest():
    def __init__(
            self,
            spec=None,
            complete=True,
            pkgmgr=None,
            link=None,
            ppa=None,
            apt=None,
            dnf=None,
            npm=None,
            pip3=None,
            pipx=None,
            flatpak=None,
            cargo=None,
            github=None,
            script=None,
            **kwargs):
        self.verbose = spec.pop('verbose', False)
        self.errors = spec.pop('errors', False)
        self.sections = []
        if complete or link != None:
            cwd = kwargs.pop('cwd')
            self.sections += [Link(spec['link'], link, cwd=REAL_PATH, **kwargs)]
        if complete or ppa != None:
            self.sections += [PPA(spec['ppa'], ppa, **kwargs)]
        pkgs = spec.get('pkg', {}).get('items', [])
        apts = pkgs + spec.get('apt', {}).get('items', []) if complete or apt != None else []
        dnfs = pkgs + spec.get('dnf', {}).get('items', []) if complete or dnf != None else []
        if pkgmgr == 'deb' and apts:
            self.sections += [APT(dict(items=apts), apt, **kwargs)]
        elif pkgmgr == 'rpm' and dnfs:
            self.sections += [DNF(dict(items=dnfs), dnf, **kwargs)]
        if complete or npm != None:
            self.sections += [NPM(spec['npm'], npm, **kwargs)]
        if complete or pip3 != None:
            self.sections += [PIP3(spec['pip3'], pip3, **kwargs)]
        if complete or pipx != None:
            self.sections += [PIPX(spec['pipx'], pipx, **kwargs)]
        if complete or flatpak != None:
            self.sections += [FLATPAK(spec['flatpak'], flatpak, **kwargs)]
        if complete or cargo != None:
            self.sections += [Cargo(spec['cargo'], cargo, **kwargs)]
        if complete or github != None:
            self.sections += [Github(spec['github'], github, **kwargs)]
        if complete or script != None:
            self.sections += [Script(spec['script'], script, **kwargs)]

    def __repr__(self):
        return f'{type(self).__name__}(verbose={self.verbose}, errors={self.errors}, sections={self.sections})'

    def render_header(self):
        return f'''
#!/bin/bash
# generated file by manifest.py
# src: https://github.com/scottidler/.../blob/master/manifest.py

{DEBUG}

'''.lstrip('\n')


    def render_functions(self, sep='\n\n', prefix=None, suffix='\n\n'):
        if not self.sections:
            return ''
        result = sep.join(set([section.functions() for section in self.sections])).lstrip('\n').rstrip()
        if result:
            if prefix:
                result = prefix + result
            if suffix:
                result += suffix
        return result

    def render_body(self, sep='\n\n', prefix=None, suffix='\n\n'):
        if not self.sections:
            return ''
        result = sep.join([section.render() for section in self.sections]).lstrip('\n').rstrip()
        if result:
            if prefix:
                result = prefix + result
            if suffix:
                result += suffix
        return result

    def render_footer(self):
        return ''

    def render(self):
        return ''.join([
            self.render_header(),
            self.render_functions(),
            self.render_body(),
            self.render_footer(),
        ])

    __str__ = __repr__

def load_manifest(complete=True, config=None, **kwargs):
    yaml = YAML(typ='safe', pure=True)
    with open(config, 'r') as f:
        spec = yaml.load(f)
        manifest = Manifest(spec=spec, complete=complete, **kwargs)
        return manifest

def complete(ns):
    return not any([getattr(ns, sec) for sec in SECTIONS])

class ManifestAction(Action):
    def __call__(self, parser, namespace, values, option_strings=None):
        setattr(namespace, self.dest, values if values else ['*'])

def main(args):
    parser = ArgumentParser()
    parser.add_argument(
        '-C', '--config',
        default=f'{REAL_PATH}/manifest.yml',
        help='default="%(default)s"; specify the config path')
    parser.add_argument(
        '-D', '--cwd',
        default=REAL_PATH,
        help='default="%(default)s"; set the cwd')
    parser.add_argument(
        '-H', '--home',
        default=HOME,
        help='default="%(default)s"; specify HOME if not current')
    parser.add_argument(
        '-M', '--pkgmgr',
        default=get_pkgmgr(),
        help=f'default="%(default)s"; override pkgmgr')
    parser.add_argument(
        '-l', '--link',
        metavar='LINK',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match links')
    parser.add_argument(
        '-p', '--ppa',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match ppa items')
    parser.add_argument(
        '-a', '--apt',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match apt items')
    parser.add_argument(
        '-d', '--dnf',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match dnf items')
    parser.add_argument(
        '-n', '--npm',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match npm items')
    parser.add_argument(
        '-P', '--pip3',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match pip3 items')
    parser.add_argument(
        '-x', '--pipx',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match pipx items')
    parser.add_argument(
        '-f', '--flatpak',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patters to match flatpak items')
    parser.add_argument(
        '-c', '--cargo',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match cargo crate names')
    parser.add_argument(
        '-g', '--github',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match github repos')
    parser.add_argument(
        '-s', '--script',
        metavar='SCRIPT',
        action=ManifestAction,
        nargs='*',
        help='specify list of glob patterns to match script names')
    ns = parser.parse_args()
    manifest = load_manifest(complete=complete(ns), **ns.__dict__)
    try:
        print(manifest.render())
        sys.stdout.flush()
    except IOError:
        sys.stderr.write("on running: " + str(sys.exc_info()))
    try:
        sys.stdout.close()
    except IOError:
        sys.stderr.write("on closing: " + str(sys.exc_info()))


if __name__ == '__main__':
    main(sys.argv[1:])
