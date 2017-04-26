#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 12:58:54 2017

@author: marshals
"""
import re, os
from opmsg import opmsg

class opErrCtl(opmsg):
    def __init__(self, *args, **kwargs):
        super(opErrCtl, self).__init__(*args, **kwargs)
        pass
    
    def get_log_info(self, log_path, waive_list=[], fatal_list=[], warn_list=[]):
        
        if not os.path.exists(log_path):
            return {}
        
        dict = {}
        fo = open(log_path)
        waive = []
        fatal = []
        warning = []
        error = []
        for line in fo:
            line = line.strip()
            WarCheck = re.search('^(Warning|WARNING|SNPS_WARNING)\s*:\s*(.*)', line)
            ErrCheck = re.search('^(Error|ERROR|SNPS_ERROR)\s*:\s*(.*)', line)
            tag_waive = False
            tag_fatal = False
#            print waive_list
#            print fatal_list
#            print warn_list
            for lw in waive_list:
                if lw == '' or lw == ' ': continue
                if re.search(lw, line):
                    tag_waive = True
                    break
            for lf in fatal_list:
                if lf == '' or lf == ' ': continue
                if re.search(lf, line):
                    tag_fatal = True
                    break
            if tag_waive:
                waive.append(line)
            else:
                if tag_fatal:
                    fatal.append(line)
                else:
                    pass
                    if WarCheck:
                        warning.append(line)
                    if ErrCheck:
                        error.append(line)
        fo.close()
        
        dict['waive']   = waive
        dict['warning'] = warning
        dict['error']   = error
        dict['fatal']   = fatal
        
        return dict
    