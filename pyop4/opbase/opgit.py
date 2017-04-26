#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 21:38:27 2017

@author: marshals
"""

import os, sys, re
from opmsg import opmsg
from pypyscreen import getoutput, getstderr

class basegit(opmsg):
    def __init__(self, *args, **kwargs):
        super(basegit,self).__init__(*args, **kwargs)
        self.opgit_setenv()

    def checkout(self, src='', dst='', src_branch='master', dst_branch=''):
        '''
        check out is the "git clone + git checkout"
        '''
        if dst_branch == '':
            self.info('dst_branch will be %s' % (src_branch))
            dst_branch=src_branch
        if src=='' or dst=='':
            self.err('Must define src/dst')
            return False
        current_dir = os.getcwd()
        self.dbg( 'Current Directory: %s' % ( current_dir ) )
        #- if not exists checkout
        checkout_cmd = 'git clone -b %s %s %s' % (src_branch, src, dst)
        self.stdout = getoutput(checkout_cmd)
        if self.no_src:
            self.err('No source repo \'%s\'.' % (src) )
            return False
        elif self.no_src_branch:
            self.err('No source Branch in repo \'%s\'.' % (src_branch, src) )
            return False
        elif self.cloned or self.initialized_empty_repo:
            self.info('Checkout Successful!')
            return self.new_branch(dst=dst, dst_branch=dst_branch)
        elif self.exists_local_repo:
            self.warn('destination repo \'%s\' already exists' % (dst) )
            return self.new_branch(dst=dst, dst_branch=dst_branch)
        else:
            self.err('Unknown Status!')
            return False
   
    def commit(self, repo_path=os.getcwd(), comment_in='' ):
        cwd = os.getcwd()
        os.chdir(repo_path)
        self.info('Switch into repo: "%s"' % (repo_path))
        if not self.clean:
            comment = ''
            for f in self.new_files:
                cmd = 'git add %s' % (f)
                #print cmd
                comment += 'add: %s; ' % (f)
                getoutput(cmd)
            for f in self.modified_files:
                cmd = 'git add %s' % (f)
                #print cmd
                comment += 'modified: %s; ' % (f)
                getoutput(cmd)
            for f in self.deleted_files:
                cmd = 'git rm %s' % (f)
                #print cmd
                comment += 'deleted: %s; ' % (f)
                getoutput(cmd)
            if comment_in != '': comment = comment_in
            cmd = 'git commit -m \'%s\'' % (comment)
            #print cmd
            getoutput(cmd)
            self.info('Commit Finished.')
        else:
            self.info('Repository is Clean. Nothing Commit.')

        os.chdir(cwd)
        
    def new_branch(self, dst='scripts', dst_branch='new'):
        if not os.path.exists(dst):
            self.info('No repo found. Will checkout a new one')
            self.checkout(dst)
        cwd=os.getcwd()
        os.chdir(dst)            
        #- checkout or new created
        if not self.exists_branch(dst_branch):
            self.info('Create a new branch %s' % (dst_branch))
            cmd = 'git checkout -b %s' % (dst_branch)
            self.stdout = getoutput(cmd)
        else:
            if self.current_branch != dst_branch:
                self.info('Checkout branch %s' % (dst_branch))
                cmd = 'git checkout %s' % (dst_branch)
                self.stdout = getoutput(cmd)
        # check if checkout successfully
        if self.current_branch == dst_branch:
            self.info('Current Branch: %s' % (dst_branch) )
            cmd = 'git config receive.denyCurrentBranch ignore'
            self.stdout = getoutput(cmd)
            os.chdir(cwd)
            return True
        else:
            os.chdir(cwd)
            return False

    @property
    def no_src(self):
        comp = re.compile(r'fatal: repository \'(.*)\' does not exist')
        if len(comp.findall(self.stdout[0])):
            return True
        comp = re.compile(r'fatal: (\S+) does not appear to be a git repository')
        for line in self.stdout:
            if len(comp.findall(line)):
                return True       
        return False
    
    @property
    def no_src_branch(self):
        comp = re.compile(r'warning: Remote branch (.*) not found in upstream origin')
        try:
            if len(comp.findall(self.stdout[-1])) or len(comp.findall(self.stdout[-2])):
                return True
            return False
        except:
            return False

    @property
    def exists_local_repo(self):
        comp = re.compile(r'fatal: destination path \'(.*)\' already exists and is not an empty directory.')
        if len(comp.findall(self.stdout[0])):
            return True
        return False

    @property
    def cloned(self):
        comp = re.compile(r'done.')
        if len(comp.findall(self.stdout[-1])):
            return True
        return False
    
    @property
    def initialized_empty_repo(self):
        comp = re.compile(r'Initialized empty Git repository in (.*)')
        if len(comp.findall(self.stdout[0])):
            return True
        return False   
    
    @property
    def current_branch(self):
        return [ i.split()[1] for i in getoutput('git branch', quiet=True) if re.match(r'^\*\s.*', i)][0]
    
    @property
    def modified_files(self):
        cmd = 'git status'
        self.stdout = getoutput(cmd, quiet=True)
        comp = re.compile(r'^#*\s*modified:\s+(\S+)$')
        lists = []
        for line in self.stdout:
            if line == '#': continue
            f = comp.findall(line)
            if len(f):
                lists.append(f[0])
        return lists

    @property
    def deleted_files(self):
        cmd = 'git status'
        self.stdout = getoutput(cmd, quiet=True)
        comp = re.compile(r'^#*\s*deleted:\s+(\S+)$')
        lists = []
        for line in self.stdout:
            if line == '#': continue
            f = comp.findall(line)
            if len(f):
                lists.append(f[0])
        return lists

    @property
    def new_files(self):
        cmd = 'git status'
        self.stdout = getoutput(cmd, quiet=True)
        comp = re.compile(r'^#*\s*(\S+)$')
        lists = []
        for line in self.stdout:
            if line == '#': continue
            f = comp.findall(line)
            if len(f):
                lists.append(f[0])
        return lists
    
    @property
    def clean(self):
        cmd = 'git status'
        self.stdout = getoutput(cmd, quiet=True)
        comp = re.compile(r'^nothing to commit, working directory clean$')
        if len(comp.findall(self.stdout[-1])):
            return True
        return False
    
    def exists_branch(self, branch):
        for i in getoutput('git branch', quiet=True):
            if re.match(r'^\**\s*%s'%(branch), i):
                return True
        return False
    
    def opgit_setenv(self):
        #git config --global core.editor vim
        cmd = 'git config --global user.name "%s"' % (os.getenv('USER'))
        getoutput(cmd, quiet=True)
        cmd = 'git config --global user.email "%s@alchip.com"' % (os.getenv('USER'))
        getoutput(cmd, quiet=True)

if __name__ == '__main__':
    os.chdir('/media/sf_D_DRIVE/workspace/onepiece4/pyop4/TEMPLATES/config/global')
    os.chdir('/media/sf_D_DRIVE/workspace/onepiece4/pyop4/TEMPLATES/flow')
    print basegit().modified_files
    print basegit().deleted_files
    print basegit().new_files
    print basegit().clean
    basegit().commit(repo_path='/media/sf_D_DRIVE/workspace/onepiece4/pyop4/TEMPLATES/config/global')
   
    
