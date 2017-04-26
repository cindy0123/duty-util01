#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 16:58:52 2017

@author: marshals
"""

import os
from opconfig import opconfig

class opconfig2script(opconfig):
    def __init__(self, *args, **kwargs):
        super(opconfig2script, self).__init__(*args, **kwargs)
        
    def opconfig2script_check_args(self, *args, **kwargs):
        confs     = kwargs.get('config_files'   , None)
        infile    = kwargs.get('input_file'     , None)
        tcl_conf  = kwargs.get('tcl_config'    , None)
        allvar    = kwargs.get('allvar'    , None)

        if confs == None and allvar == None:
            self.err('Must define confs file')
            return False
        
        if infile==None and tcl_conf == None:
            self.err('Must define input file or use --tcl for generate tcl format config')
            return False
        
        if infile!=None and tcl_conf != None:
            self.err('-in and --tcl are exclusive')
            return False
        
        if infile and not os.path.exists(infile):
            self.err('Can not find file: %s' % (infile))
            return False
        
        return True
            
    def convert_tempt(self, *args, **kwargs):
        tcl_conf  = kwargs.get('tcl_config'    , None)

        if not self.opconfig2script_check_args(*args, **kwargs):
            return False

        if tcl_conf:
            return self.__2tcl(*args, **kwargs)
        else:
            return self.__Ftempt(*args, **kwargs)

    def __2tcl(self, *args, **kwargs): 
        confs     = kwargs.get('config_files'   , None)
        outfile   = kwargs.get('output_file'    , None)
        quiet     = kwargs.get('quiet', False)
        if len(confs.split()) > 1:
            outfile = None
        out = outfile

        for conf in confs.split():
            conf = os.path.realpath(conf)
            if not os.path.exists(conf):
                self.err('No such file: %s' % (conf))
            if out==None:
                outfile = os.path.splitext(conf)[0] + '.' + 'tcl'
            self.config2script(conf, outfile)
            if not quiet: self.info('Finished: %s' % (outfile) )
        return True
    
    def __Ftempt(self, *args, **kwargs): 
        confs     = kwargs.get('config_files'   , None)
        infile    = kwargs.get('input_file'     , None)
        ext_name  = kwargs.get('ext_name'       , None)
        outfile   = kwargs.get('output_file'    , None)
        allvar    = kwargs.get('allvar'    , None)
        quiet     = kwargs.get('quiet', False)
        repl_debug = kwargs.get('repl_debug', False)

        if outfile==None:
            if ext_name == None:
                outfile = os.path.splitext(infile)[0] + '.' + 'tcl'
            else:
                outfile = os.path.splitext(infile)[0] + '.' + ext_name
        if allvar == None:
            allvar = self.get_ALLVAR(confs)
        self.repl_op4var(infile, outfile, allvar, repl_debug=repl_debug)
        if not quiet: self.info('Finished: %s' % (outfile) )
        return True
    
    def get_ALLVAR(self, confs):
        for f in confs.split():
            if not os.path.exists(f):
                self.err('No such file: %s' % (f) )
                continue
            self.read_conf(f)
        #print self.all_config()
        return self.all_config()
       

    
    #parser.print_help()
    #/media/sf_depot/onepiece4/examples/in.tempt
    #/media/sf_depot/onepiece4/examples/200_user_setup.json
