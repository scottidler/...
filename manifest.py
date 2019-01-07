#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from copy import deepcopy
from ruamel import yaml

SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_NAME = os.path.basename(SCRIPT_FILE)
SCRIPT_PATH = os.path.dirname(SCRIPT_FILE)
if os.path.islink(__file__):
    REAL_FILE = os.path.abspath(os.readlink(__file__))
    REAL_NAME = os.path.basename(REAL_FILE)
    REAL_PATH = os.path.dirname(REAL_FILE)

from argparse import ArgumentParser

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

class UnknownPkgmgrError(Exception):
    def __init__(self):
        super(UnknownPkgmgrError, self).__init__('unknown pkgmgr!')

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
    def __init__(self, links_spec):
        self.recursive = links_spec.pop('recursive', False)
        if self.recursive:
            raise NotImplementedError
        else:
            self.items = [(key,val) for key,val in links_spec.items()]

    def __repr__(self):
        return f'{type(self).__name__}(recursive={self.recursive}, items={self.items})'

    __str__ = __repr__

    def render(self, path):
        print(f'Links: path={path}, items={self.items}')

class PPAS(ManifestType):
    def __init__(self, ppas_spec):
        self.items = ppas_spec

    def render(self, path):
        print(f'PPAS: path={path}, items={self.items}')

class PKGS(ManifestType):
    def __init__(self, pkgs_spec):
        self.items = pkgs_spec

    def render(self, path):
        print(f'PKGS: path={path}, items={self.items}')

class NPMS(ManifestType):
    def __init__(self, npms_spec):
        self.items = npms_spec

    def render(self, path):
        print(f'NPMS: path={path}, items={self.items}')

class PIP3S(ManifestType):
    def __init__(self, pip3s_spec):
        self.items = pip3s_spec

    def render(self, path):
        print(f'PIP3S: path={path}, items={self.items}')

class Repo():
    def __init__(self, reponame, repo_spec):
        self.reponame = reponame
        self.links = Links(repo_spec.get('links', None))

    def __repr__(self):
        return f'{type(self).__name__}(reponame={self.reponame}, links={self.links})'

    __str__ = __repr__

    def render(self, path):
        print(f'Repo: path={path}, reponame={self.reponame}')
        self.links.render(path)

class Github(ManifestType):
    def __init__(self, github_spec):
        self.repos = [Repo(reponame, repospec) for reponame, repospec in github_spec.items()]

    def __repr__(self):
        return f'{type(self).__name__}(repos={self.repos})'

    __str__ = __repr__

    def render(self, path):
        print(f'Github: path={path}')
        for repo in self.repos:
            repo.render(path)

class Manifest():
    def __init__(self, sections, spec, pkgmgr):
        self.verbose = spec.pop('verbose', False)
        self.errors = spec.pop('errors', False)
        self.sections = []
        if 'links' in sections:
            self.sections += [Links(spec['links'])]
        if 'ppa' in sections:
            self.sections += [PPAS(spec['ppa'])]
        pkgs = spec.get('pkg', []) if 'pkg' in sections else []
        apts = pkgs + (spec.get('apt', []) if 'apt' in sections else [])
        dnfs = pkgs + (spec.get('dnf', []) if 'dnf' in sections else [])
        if pkgmgr == 'deb' and apts:
            self.sections += [PKGS(apts)]
        elif pkgmgr == 'rpm' and dnfs:
            self.sections += [PKGS(dnfs)]
        if 'npm' in sections:
            self.sections += [NPMS(spec['npm'])]
        if 'pip3' in sections:
            self.sections += [PIP3S(spec['pip3'])]
        if 'github' in sections:
            self.sections += [Github(spec['github'])]

    def __repr__(self):
        return f'{type(self).__name__}(verbose={self.verbose}, errors={self.errors}, sections={self.sections})'

    def render(self, path):
        print(f'Manifest: path={path}')
        for section in self.sections:
            section.render(path)

    __str__ = __repr__

def load_manifest(config, sections):
    spec = yaml.safe_load(open(config))
    manifest = Manifest(sections, spec, get_pkgmgr())
    return manifest

def main(args):
    parser = ArgumentParser()
    parser.add_argument(
        '-C', '--config',
        default=f'{SCRIPT_PATH}/manifest.yml',
        help='default=%(default)s; specify the config path')
    parser.add_argument(
        '-p', '--path',
        default=SCRIPT_PATH,
        help=f'default="{SCRIPT_PATH}"; choose path that all relative paths will be based upon')
    parser.add_argument(
        '--sections',
        metavar='SEC',
        nargs='+',
        choices=SECTIONS,
        default=SECTIONS,
        help=f'choices={SECTIONS}; choose which sections to run')
    ns = parser.parse_args()
    print(ns)
    manifest = load_manifest(ns.config, ns.sections)
    print(manifest)
    manifest.render(ns.path)

if __name__ == '__main__':
    main(sys.argv[1:])

