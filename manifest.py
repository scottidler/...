#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import pwd
import sys
sys.dont_write_bytecode = True

from copy import deepcopy
from ruamel import yaml
from pathlib import Path

from argparse import ArgumentParser
from contextlib import contextmanager

sys.path.insert(0, os.path.expanduser('~/repos/scottidler'))
from utils.dbg import dbg

SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_NAME = os.path.basename(SCRIPT_FILE)
SCRIPT_PATH = os.path.dirname(SCRIPT_FILE)
if os.path.islink(__file__):
    REAL_FILE = os.path.abspath(os.readlink(__file__))
    REAL_NAME = os.path.basename(REAL_FILE)
    REAL_PATH = os.path.dirname(REAL_FILE)

SECTIONS = [
    'links',
    'ppa',
    'pkg',
    'apt',
    'dnf',
    'npm',
    'pip3',
    'github',
]

UID = os.getuid()
GID = pwd.getpwuid(UID).pw_gid
USER = pwd.getpwuid(UID).pw_name

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

class ManifestType():
    def __repr__(self):
        return f'{type(self).__name__}(items = {self.items})'

    __str__ = __repr__

class Links(ManifestType):
    def __init__(self, spec, cwd=None, user=None, **kwargs):
        self.cwd = cwd
        self.user = user
        self.recursive = spec.pop('recursive', False)
        def interpolate_rootpath(filepath, rootpath):
            return os.path.realpath(re.sub(f'^{srcpath}', rootpath, filepath))
        def interpolate_user(filepath, user):
            return re.sub(f'USER', user, filepath)
        if self.recursive:
            with cd(cwd):
                self.items = []
                for srcpath, dstpath in spec.items():
                    for item in [item for item in Path(srcpath).rglob('*') if not item.is_dir()]:
                        src = item.as_posix()
                        dst = interpolate_rootpath(src, dstpath)
                        dst = interpolate_user(dst, user)
                        self.items += [(src, dst)]
        else:
            self.items = [(src, interpolate_user(dst, user)) for src, dst in spec.items()]

    def __repr__(self):
        return f'{type(self).__name__}(recursive={self.recursive}, items={self.items})'

    __str__ = __repr__

    @property
    def render_links(self):
        return '\n'.join([f'{src} {dst}' for src, dst in self.items])

    def render(self):
        return f'''
echo "links:"
cd {self.cwd}
while read -r file link; do
    file=$(realpath $file)
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
done<<EOM
{self.render_links}
EOM
        '''.strip()

class PKGS(ManifestType):
    def __init__(self, pkgs_spec, **kwargs):
        self.items = pkgs_spec

    @property
    def render_items(self):
        return '\n'.join(self.items)

    def render(self):
        pass

class APTS(PKGS):
    def __init__(self, spec, **kwargs):
        self.items = spec.get('items', None)

    def __repr__(self):
        return f'{type(self).__name__}(items={self.items})'

    __str__ = __repr__

    def render(self):
        return f'''
echo "apts:"
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y software-properties-common
while read pkg; do
    sudo apt-get install $pkg
done<<EOM
{self.render_items}
EOM
        '''.strip()

class DNFS(ManifestType):
    def __init__(self, spec, **kwargs):
        self.items = spec.get('items', None)

    def __repr__(self):
        return f'{type(self).__name__}(items={self.items})'

    __str__ = __repr__

    def render(self):
        raise NotImplementedError

class PPAS(PKGS):
    def __init__(self, ppas_spec, **kwargs):
        self.items = ppas_spec.get('items', [])

    def __repr__(self):
        return f'{type(self).__name__}(items={self.items})'

    __str__ = __repr__

    def render(self):
        if not self.items:
            return ''
        return f'''
echo "ppas:"
while read ppa; do
    ppas=`find /etc/apt/ -name *.list | xargs cat | grep ^[[:space:]]*deb | grep -v deb-src`
    if [[ $ppas != *"$ppa"* ]]; then
        sudo add-apt-repository -y "ppa:$ppa"
    fi
done<<EOM
{self.render_items}
EOM
        '''.strip()

class NPMS(ManifestType):
    def __init__(self, spec, **kwargs):
        self.items = spec.get('items', None)

    def __repr__(self):
        return f'{type(self).__name__}(items={self.items})'

    __str__ = __repr__

    def render(self):
        if not self.items:
            return ''
        return f'''
echo "npms:"
while read pkg; do
    sudo npm install -g $pkg
done<<EOM
{self.render_items}
EOM
        '''.strip()

class PIP3S(ManifestType):
    def __init__(self, spec, **kwargs):
        self.items = spec.get('items', None)

    def __repr__(self):
        return f'{type(self).__name__}(items={self.items})'

    __str__ = __repr__

    def render(self):
        if not self.items:
            return ''
        return f'''
echo "npms:"
sudo -H pip3 install --upgrade pip setuptools
while read pkg; do
    sudo -H pip3 install --upgrade $pkg
done<<EOM
{self.render_items}
EOM
        '''.strip()

class Repo():
    def __init__(self, baseurl, reponame, spec, repopath, **kwargs):
        self.baseurl = baseurl
        self.reponame = reponame
        self.repopath = repopath
        self.links = Links(spec.get('links', None))

    def __repr__(self):
        return f'{type(self).__name__}(baseurl={self.baseurl}, reponame={self.reponame}, repopath={self.repopath}, links={self.links})'

    __str__ = __repr__

    def render(self):
        return f'''
git clone --recursive {self.baseurl}/{self.reponame} {self.repopath}/{self.reponame}
(cd {self.repopath}/{self.reponame} && pwd && git pull && git checkout HEAD)

{self.links.render()}
    '''.strip()

class Github(ManifestType):
    def __init__(self, spec, **kwargs):
        repopath = spec.pop('repopath', 'repos')
        self.repos = [Repo('https://github.com', reponame, repospec, repopath) for reponame, repospec in spec.items()]

    def __repr__(self):
        return f'{type(self).__name__}(repos={self.repos})'

    __str__ = __repr__

    def render(self):
        return 'github:\n ' + '\n'.join([repo.render() for repo in self.repos])

class Manifest():
    def __init__(self, sections=None, spec=None, pkgmgr=None, **kwargs):
        self.verbose = spec.pop('verbose', False)
        self.errors = spec.pop('errors', False)
        self.sections = []
        if 'links' in sections:
            self.sections += [Links(spec['links'], **kwargs)]
        if 'ppa' in sections:
            self.sections += [PPAS(spec['ppa'], **kwargs)]
        pkgs = spec.get('pkg', {}).get('items', []) if 'pkg' in sections else []
        apts = pkgs + spec.get('apt', {}).get('items', []) if 'apt' in sections else []
        dnfs = pkgs + spec.get('dnf', {}).get('items', []) if 'dnf' in sections else []
        if pkgmgr == 'deb' and apts:
            self.sections += [APTS(dict(items=apts), **kwargs)]
        elif pkgmgr == 'rpm' and dnfs:
            self.sections += [DNFS(dict(items=dnfs), **kwargs)]
        if 'npm' in sections:
            self.sections += [NPMS(spec['npm'], **kargs)]
        if 'pip3' in sections:
            self.sections += [PIP3S(spec['pip3'], **kwargs)]
        if 'github' in sections:
            self.sections += [Github(spec['github'], **kwargs)]

    def __repr__(self):
        return f'{type(self).__name__}(verbose={self.verbose}, errors={self.errors}, sections={self.sections})'

    def render(self):
        if not self.sections:
            return ''
        body = '\n\n'.join([section.render() for section in self.sections])
        return '''
#!/bin/bash
# manfest.py generated file

{body}
        '''.format(body=body).strip()

    __str__ = __repr__

def load_manifest(config=None, **kwargs):
    spec = yaml.safe_load(open(config))
    manifest = Manifest(spec=spec, **kwargs)
    return manifest

def main(args):
    parser = ArgumentParser()
    parser.add_argument(
        '-C', '--config',
        default=f'{SCRIPT_PATH}/manifest.yml',
        help='default=%(default)s; specify the config path')
    parser.add_argument(
        '-d', '--cwd',
        default=os.getcwd(),
        help='default=%(default)s; set the cwd')
    parser.add_argument(
        '-u', '--user',
        default=USER,
        help='default=%(default)s; specify user if not current')
    parser.add_argument(
        '-p', '--pkgmgr',
        default=get_pkgmgr(),
        help=f'default=%(default)s; override pkgmgr')
    parser.add_argument(
        '-s', '--sections',
        metavar='SEC',
        nargs='+',
        choices=SECTIONS,
        default=SECTIONS,
        help=f'choices={SECTIONS}; choose which sections to run')
    ns = parser.parse_args()
    manifest = load_manifest(**ns.__dict__)
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

