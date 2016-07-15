#!/usr/bin/env python

import os
import re
import sys
from pprint import pprint
from contextlib import contextmanager
from subprocess import Popen, PIPE

sys.dont_write_bytecode = True

@contextmanager
def cd(*args, **kwargs):
    '''
    helper change dir function to be used with 'with' expressions
    '''
    mkdir = kwargs.pop('mkdir', True)
    verbose = kwargs.pop('verbose', False)
    path = os.path.sep.join(args)
    path = os.path.normpath(path)
    path = os.path.expanduser(path)
    prev = os.getcwd()
    if path != prev:
        if mkdir:
            run('mkdir -p %(path)s' % locals(), verbose=verbose)
        os.chdir(path)
        curr = os.getcwd()
        sys.path.append(curr)
        if verbose:
            print 'cd %s' % curr
    try:
        yield
    finally:
        if path != prev:
            sys.path.remove(curr)
            os.chdir(prev)
            if verbose:
                print 'cd %s' % prev

def run(*args, **kwargs):
    '''
    thin wrapper around Popen; returns exitcode, stdout and stderr
    '''
    nerf = kwargs.pop('nerf', False)
    verbose = kwargs.pop('verbose', False)
    if (verbose or nerf) and args[0]:
        print args[0]
    if nerf:
        return (None, 'nerfed', 'nerfed')
    process = Popen(
        shell=kwargs.pop('shell', True),
        stdout=kwargs.pop('stdout', PIPE),
        stderr=kwargs.pop('stderr', PIPE),
        *args, **kwargs)


    stdout, stderr = process.communicate()
    stdout, stderr = stdout.strip(), stderr.strip()
    exitcode = process.poll()
    if verbose and stdout:
        print stdout
    return exitcode, stdout, stderr

def expand(path):
    if path:
        return os.path.expanduser(path)

def clone(giturl, reponame, commit, clonepath, mirrorpath, versioning=False):
    clonepath = expand(clonepath)
    mirrorpath = expand(mirrorpath)
    mirror = ''
    if mirrorpath:
        mirror = '--reference %(mirrorpath)s/%(reponame)s.git' % locals()
    path = os.path.join(clonepath, reponame)
    repopath = reponame
    if versioning:
        repopath = os.path.join(repopath, commit)
    with cd(clonepath, mkdir=True):
        if not os.path.isdir(repopath):
            run('git clone %(mirror)s %(giturl)s%(reponame)s %(repopath)s' % locals())
        with cd(repopath):
            run('git clean -xfd')
            run('git checkout %(commit)s' % locals())
    return os.path.join(clonepath, repopath)
