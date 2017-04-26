#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 14:51:01 2017

@author: marshals
"""
from openv import op4env
from opgit import basegit
from opErrCtl import opErrCtl
import re, os, time, sys
import glob
from opstage import opstage

class opflowcontrol(opstage):
    def __init__(self, *args, **kwargs):
        super(opflowcontrol, self).__init__(*args, **kwargs)
           
    def opflowcontrol_check_args(self, *args, **kwargs):
        self.from_stage   = kwargs.get('from_stage', None)
        self.to_stage     = kwargs.get('to_stage', None)
        self.over_write   = bool(kwargs.get('over_write', False))
        self.no_exit      = bool(kwargs.get('no_exit', False))
        self.memory_req   = kwargs.get('memory_req', 30000)
        self.cpu_req      = kwargs.get('cpu_req', 4)
        self.keyword_scenario = kwargs.get('keyword_scenario', '')
        self.through_stage    = kwargs.get('through_stage', [])
        self.repl_debug  = bool(kwargs.get('repl_debug', False))
        self.run_task    = bool(kwargs.get('run_task', False))
        self.DEBUG       = self.repl_debug
        self.quiet       = not self.repl_debug

        self.parse_current_run_dir(quiet=False, *args, **kwargs)
        self.set_config_location(quiet=self.quiet)

        if not self.parse_flow_stage(to_stage=self.to_stage, from_stage=self.from_stage, thr_stage=self.through_stage):
            return False

        if not self.pase_stage_option(self.from_stage, self.to_stage):
            return False

        self.userpattern = self.eco_string
        self.stage       = self.dst_stage
        self.to_stage    = self.to_stage.split('.')[0]
        self.from_stage  = self.from_stage.split('.')[0]
#        self.from_stage  = '%s.%s.%s' % (self.src_stage, self.src_branch, self.src_eco)
#        self.to_stage    = '%s.%s.%s' % (self.dst_stage, self.branch_name, self.eco_string)
        return True

    def parse_flow_stage(self, from_stage=None, thr_stage=[], to_stage=None ):
        if not from_stage and not to_stage and len(thr_stage) == 0:
            self.err('Option: -from|-thr|-to are Required!')
            return False
        if from_stage:
            src_tool = self.get_tool(from_stage)
        else:
            src_tool = ''
        if len(thr_stage):
            thr_tool = [ self.get_tool(t) for t in thr_stage ]
        else:
            thr_tool = []
        if to_stage:
            to_tool = self.get_tool(to_stage)
        else:
            to_tool = ''

        if from_stage:
            src_tool = self.get_tool(from_stage)
        else:
            src_tool = ''
        if len(thr_stage):
            thr_tool = [ self.get_tool(t) for t in thr_stage ]
        else:
            thr_tool = []
        if to_stage:
            to_tool = self.get_tool(to_stage)
        else:
            to_tool = ''
            
        print src_tool, thr_tool, to_tool
        return True

    def get_tool(self, stage_name):
        if re.match(r'^\d+', stage_name.split('_')[0]):
            return stage_name.split('_')[1]
        else:
            return stage_name.split('_')[0]
        
    def init_flow(self, *args, **kwargs):
        self.info('%s Flow: %s' % ( 'default', self.allvar['icc2.default'] ) )
        self.info('From : %s' % (self.from_stage))
        self.info('To   : %s' % (self.to_stage))
        
        prestage = self.from_stage
        begin_index = self.allvar['icc2.default'].split().index(self.from_stage)
        end_index   = self.allvar['icc2.default'].split().index(self.to_stage)
        #print begin_index, end_index
        if self.username != 'marshals': sys.exit(1)
        for stage in self.allvar['icc2.default'].split()[begin_index:end_index+1]:
            kwargs['source_stage'] = '%s.%s.%s' % (prestage, self.src_branch, self.src_eco)
            kwargs['current_stage'] = '%s.%s.%s' % (stage, self.branch_name, self.eco_string)
            self.info('-'*100)
            prestage = stage
            self.opstage_check_args(*args, **kwargs)
            self.init_stage(*args, **kwargs)
            #print kwargs['src_stage'], kwargs['dst_stage'] 
            
    def run_flow(self, *args, **kwargs):
        pass
