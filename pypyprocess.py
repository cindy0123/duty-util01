#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 12:51:38 2017

@author: marshals
"""
from subprocess import Popen, PIPE, STDOUT
import re

class pypyprocess(object):
    def __init__(self, *args, **kwargs):
        #super(pypyprocess, self).__init__(*args, **kwargs) 
        pass
    
    def getoutput(self, cmd, wait=True, quiet=False, empty_thr = 5):
        lines = []
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, executable='/bin/csh')
        cnt = 0
        while p.stdout and wait:
            line = p.stdout.readline().strip()
            if line != '':
                lines.append(line)
                if not quiet: print ("SHELL : %s" % (line) )
                cnt = 0
            else:
                cnt += 1
            #p.stdout.flush()
            if cnt > empty_thr:
                break
        return lines

    def getstderr(self, cmd, quiet=False):
        lines = []
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
        while p.stdout:
            line = p.stdout.readline().strip()
            if re.match('^Error', line):
                lines.append(line)
                if not quiet: print("SHELL : %s" % (line) )
            #p.stdout.flush()
            if not line: break
        return lines

