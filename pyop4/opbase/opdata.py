#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 12:47:04 2017

@author: marshals
"""

from opmsg import opmsg
import os,re
from opfilehandle import iterfind

class opdata(iterfind, opmsg):
    def __init__(self, *args, **kwargs):
        super(opdata, self).__init__(*args, **kwargs)
        
    def get_released_data(self, *args, **kwargs):
        pass
    
    def get_released_vent(self, *args, **kwargs):
        gz_type = ['', '.gz']
        formats = ['*.v', '*.vg']
        files   = []
        super(opdata, self).check_release_dir(*args, **kwargs)
        for gz in gz_type:
            for file_format in formats:        
                findpath = self.release_dir
                for f in self.file('%s%s' % (file_format, gz), findpath=findpath):
                    files.append(f)
        return files
                    
    def check_release_dir(self, *args, **kwargs):
        self.release_dir = kwargs.get('release_dir', '')
        block_name  = kwargs.get('block_name', '')
        version     = kwargs.get('version', '')    
        file_type   = kwargs.get('file_type', '')    
        self.release_dir = os.path.join(self.release_dir, block_name, file_type, version)
        if not os.path.exists(self.release_dir):
            self.err('No such release Dir. : %s' % (self.release_dir))
            return None

if __name__ == '__main__':
    data = opdata()
    print data.get_released_vent(release_dir='/proj/OP4/WORK/marshals/proj/pll_div/RELEASE/IDR', block_name='ORCA_TOP', file_type = 'VNET', version='11')
        
        
    