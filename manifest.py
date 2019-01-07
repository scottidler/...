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

#class LNK():
#    @classmethod
#    def create(cls, path, name, body):
#        cls.path = path
#        recursive = body.pop('recursive', False)
#        return [LNK(src, dst, recursive=recursive) for src, dst in body.items()]
#
#    def __init__(self, src, dst, recursive=False):
#        self.src = src
#        self.dst = dst
#        self.recursive = recursive
#
#    def __repr__(self):
#        return f'{type(self).__name__}(src={self.src}, dst={self.dst}, recursive={self.recursive})'
#
#    __str__ = __repr__
#
#class PPA():
#    @classmethod
#    def create(cls, path, name, body):
#        cls.path = path
#        return [PPA(ppa) for ppa in body]
#
#    def __init__(self, ppa):
#        self.ppa = ppa
#
#    def __repr__(self):
#        return f'{type(self).__name__}(ppa = {self.ppa})'
#
#class PKG():
#    @classmethod
#    def create(cls, path, name, body):
#        cls.path = path
#        mgr = {
#            'pkg': get_pkgmgr,
#            'apt': lambda: 'deb',
#            'dnf': lambda: 'rpm',
#        }[name]()
#        return [PKG(mgr, pkg) for pkg in body]
#
#    def __init__(self, mgr, pkg):
#        self.mgr = mgr
#        self.pkg = pkg
#
#    def __repr__(self):
#        return f'{type(self).__name__}(mgr = {self.mgr}, pkg = {self.pkg})'
#
#    __str__ = __repr__
#
#class NPM():
#    @classmethod
#    def create(cls, path, name, body):
#        cls.path = path
#        return [NPM(pkg) for pkg in body]
#
#    def __init__(self, pkg):
#        self.pkg = pkg
#
#    def __repr__(self):
#        return f'{type(self).__name__}(pkg = {self.pkg})'
#
#    __str__ = __repr__
#
#class PIP3():
#    @classmethod
#    def create(cls, path, name, body):
#        cls.path = path
#        return [PIP3(pkg) for pkg in body]
#
#    def __init__(self, pkg):
#        self.pkg = pkg
#
#    def __repr__(self):
#        return f'{type(self).__name__}(pkg = {self.pkg})'
#
#    __str__ = __repr__
#
#class Github():
#    @classmethod
#    def create(cls, path, name, body):
#        cls.path = path
#        githubs = []
#        for reponame, repobody in body.items():
#            recursive = repobody.pop('recursive', False)
#            links = repobody.pop('links', [])
#            links = [LNK(src, dst, recursive=recursive) for src, dst in links.items()]
#            githubs += [Github(reponame, links)]
#        return githubs
#
#    def __init__(self, reponame, items):
#        self.reponame = reponame
#        self.items = items
#
#    def __repr__(self):
#        return f'{type(self).__name__}(reponame = {self.reponame}, items = {self.items})'
#
#def factory(path, name, body):
#    return {
#        'links': LNK.create,
#        'ppa': PPA.create,
#        'pkg': PKG.create,
#        'apt': PKG.create,
#        'dnf': PKG.create,
#        'npm': NPM.create,
#        'pip3': PIP3.create,
#        'github': Github.create,
#    }[name](path, name, body)
#    return {
#        'links': LNK(path, body)
#    }
#
class ManifestType():
    def __repr__(self):
        return f'{type(self).__name__}(items = {self.items})'

    __str__ = __repr__

class Links(ManifestType):
    def __init__(self, links_spec):
        self.recursive = links_spec.pop('recursive', False)
        self.items = [(key,val) for key,val in links_spec.items()]

    def __repr__(self):
        return f'{type(self).__name__}(recursive={self.recursive}, items={self.items})'

    __str__ = __repr__

class PPAS(ManifestType):
    def __init__(self, ppas_spec):
        self.items = ppas_spec

class PKGS(ManifestType):
    def __init__(self, pkgs, apts, dnfs):
        self.pkgs = pkgs
        self.apts = apts
        self.dnfs = dnfs

    def __repr__(self):
        return f'{type(self).__name__}(pkgs={self.pkgs}, apts={self.apts}, dnfs={self.dnfs})'

    __str__ = __repr__

class NPMS(ManifestType):
    def __init__(self, npms_spec):
        self.items = npms_spec

class PIP3S(ManifestType):
    def __init__(self, pip3s_spec):
        self.items = pip3s_spec

class Repo():
    def __init__(self, reponame, repo_spec):
        self.reponame = reponame
        self.links = Links(repo_spec.get('links', None))

    def __repr__(self):
        return f'{type(self).__name__}(reponame={self.reponame}, links={self.links})'

    __str__ = __repr__

class Github(ManifestType):
    def __init__(self, github_spec):
        self.repos = [Repo(reponame, repospec) for reponame, repospec in github_spec.items()]

    def __repr__(self):
        return f'{type(self).__name__}(repos={self.repos})'

    __str__ = __repr__

class Manifest():
    def __init__(self, path, sections, spec):
        self.path = path
        self.verbose = spec.pop('verbose', False)
        self.errors = spec.pop('errors', False)
        self.links = Links(spec.get('links', None)) if 'links' in sections else None
        self.ppas = PPAS(spec.get('ppa', None)) if 'ppa' in sections else None
        self.pkgs = PKGS(
            spec.get('pkg', None) if 'pkg' in sections else None,
            spec.get('apt', None) if 'apt' in sections else None,
            spec.get('dnf', None) if 'dnf' in sections else None
        )
        self.npms = NPMS(spec.get('npm', None)) if 'npm' in sections else None
        self.pip3s = PIP3S(spec.get('pip3', None)) if 'pip3' in sections else None
        self.github = Github(spec.get('github', None)) if 'github' in sections else None

    def __repr__(self):
        return f'{type(self).__name__}(path={self.path}, verbose={self.verbose}, errors={self.errors}, links={self.links}, ppas={self.ppas}, pkgs={self.pkgs}, npms={self.npms}, pip3s={self.pip3s}, github={self.github})'

    __str__ = __repr__

def load_manifest(path, config, sections):
    spec = yaml.safe_load(open(config))
    manifest = Manifest(path, sections, spec)
    return manifest
#    verbose = yml.pop('verbose', False)
#    allow_errors = yml.pop('allow_errors', True)
#    manifest = []
#    for name, body in yml.items():
#        if name in sections:
#            manifest += factory(path, name, body)
#    return manifest

def main(args):
    parser = ArgumentParser()
    parser.add_argument(
        '-C', '--config',
        default=[
            '~/.config/'+SCRIPT_NAME+'/'+SCRIPT_NAME+'.yml',
            SCRIPT_PATH+'/'+SCRIPT_NAME+'.yml',
        ],
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
    manifest = load_manifest(ns.path, ns.config, ns.sections)
    from pprint import pprint
    pprint(manifest)

if __name__ == '__main__':
    main(sys.argv[1:])

