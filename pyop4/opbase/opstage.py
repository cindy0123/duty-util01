#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 14:51:01 2017

@author: marshals
"""
from openv import op4env
from opErrCtl import opErrCtl
from opgit import basegit
import re, os, time, sys
from pypyscreen import screen, getoutput
import glob
from opconfig2script import opconfig2script
import shutil, socket
from pypyscreen import getoutput, getstderr

class opstage(opconfig2script, op4env, opErrCtl):
    def __init__(self, *args, **kwargs):
        super(opstage, self).__init__(*args, **kwargs)
        self.error_append=[]
        self.fatal_append = []
        self.is_ready          = False
        self.is_early_complete = False
        self.is_failed         = False
        self.remotehost        = kwargs.get('remotehost', socket.gethostname())


    def opstage_check_args(self, *args, **kwargs):
        self.src_stage   = kwargs.get('source_stage', None)
        self.dst_stage   = kwargs.get('current_stage', None)
        self.over_write  = bool(kwargs.get('over_write', False))
        self.no_exit     = bool(kwargs.get('no_exit', False))
        self.memory_req  = kwargs.get('memory_req', 30000)
        self.cpu_req     = kwargs.get('cpu_req', 4)
        self.repl_debug  = bool(kwargs.get('repl_debug', False))
        self.run_task    = bool(kwargs.get('run_task', False))
        self.scenario    = kwargs.get('scenario', '')
        self.DEBUG       = self.repl_debug
        self.quiet       = not self.repl_debug

        self.parse_current_run_dir(quiet=False, *args, **kwargs)

        if not self.src_stage or not self.dst_stage :
            self.err('Option: -src|-dst are Required!')
            return False

        if not self.pase_stage_option(self.src_stage, self.dst_stage):
            return False

        self.userpattern = self.eco_string
        self.stage       = self.dst_stage
        
        
        return True

    def parse_scenario(self, scenario, check_tool=['pt']):

#        self.allvar={}
#        self.allvar['ALL_SCENARIO_LIST'] = 'func.wcl.cworst_ccworst_m40c.setup func.wcl.cworst_ccworst_m40c.hold func.ml.cworst_ccworst_m40c.hold func.wcl.cworst_ccworst_125c.setup'
        
        all_scenario_list = self.allvar.get('ALL_SCENARIO_LIST', '').split()
        
        if self.tool not in check_tool:
            self.lib_cond    = ''
            self.rc_cond     = ''
            self.mode_name   = ''
            self.sta_cond    = '' 
            self.corner_name = ''
            if self.scenario != '':
                self.warn('No meaning when define scenario in tool %s' % (self.tool))
            return True
        else:
            if scenario == '':
                self.warn('scenario name must define in tool %s' % (self.tool))
                return False
            else:
                if len(scenario.split('.')) != 4 and scenario not in all_scenario_list:
                    self.err('Invilid scenario name %s' % (scenario))
                    self.info('Acceptable Scenario: %s' % (self.allvar['ALL_SCENARIO_LIST']))
                    return False
                self.mode_name   = scenario.split('.')[0]
                self.lib_cond    = scenario.split('.')[1]
                self.rc_cond     = scenario.split('.')[2]
                self.sta_cond    = scenario.split('.')[3]
                self.corner_name = '%s.%s.%s' % (self.lib_cond, self.rc_cond, self.sta_cond)
                print self.corner_name
                return True
        
    def pase_stage_option(self, src_stage, dst_stage):
        src_splited_name = src_stage.split('.')
        dst_splited_name = dst_stage.split('.')
        if len(src_splited_name) == 3:
            self.src_stage, self.src_branch, self.src_eco = src_splited_name
        elif len(src_splited_name) == 1:
            self.src_stage = src_splited_name[0]
        else:
            self.err('Illegal -src format. Should be "src_stage_name" or "src_stage_name.src_branch.src_eco"')
            return False            
            
        if len(dst_splited_name) == 3:
            self.dst_stage, self.branch_name, self.eco_string = dst_splited_name
        elif len(dst_splited_name) == 1:
            self.dst_stage = dst_splited_name[0]
        else:
            self.err('Illegal -dst format. Should be "dst_stage_name" or "dst_stage_name.dst_branch.dst_eco"')
            return False

        if getattr(self, 'eco_string', None) == None and getattr(self, 'src_eco', None) == None:
            self.eco_string = time.strftime("%Y%m%d", time.localtime())
            self.warn('Default ECO string used for src/dst: %s' % (self.eco_string))
            self.src_eco = self.eco_string
        elif getattr(self, 'eco_string', None) != None and getattr(self, 'src_eco', None) != None:
            pass
        elif getattr(self, 'eco_string', None) != None:
            self.src_eco = self.eco_string
        elif getattr(self, 'src_eco', None) != None:
            self.eco_string = self.src_eco

        if getattr(self, 'branch_name', None) == None and getattr(self, 'src_branch', None) == None:   
            self.branch_name = 'default'
            self.warn('Default branch name used for src/dst: %s' % (self.branch_name))
            self.src_branch = self.branch_name
        if getattr(self, 'branch_name', None) != None and getattr(self, 'src_branch', None) != None:
            pass
        elif getattr(self, 'branch_name', None) != None:
            self.src_branch = self.branch_name
        elif getattr(self, 'src_branch', None) != None:
            self.branch_name = self.src_branch
        return True

    def opstage_repl_var(self, *args, **kwargs):
        self.allvar['NO_EXIT']     = self.no_exit
        self.allvar['OP4_SESSION'] = self.session_name
        self.allvar['OP4_src']     = self.src_stage
        self.allvar['OP4_dst']     = self.dst_stage
        self.allvar['OP4_eco']     = self.eco_string
        self.allvar['OP4_src_branch']  = self.src_branch
        self.allvar['OP4_src_eco']     = self.src_eco
        self.allvar['OP4_dst_branch']  = self.branch_name
        self.allvar['OP4_dst_eco']    = self.eco_string
        
        self.allvar['MODE']           = self.mode_name
        self.allvar['LIB_CORNER']     = self.lib_cond
        self.allvar['RC_CORNER']      = self.rc_cond
        self.allvar['DELAY_TYPE']     = self.sta_cond
        self.allvar['SCENARIO_NAME']  = '%s.%s.%s.%s' % (self.mode_name, self.lib_cond, self.rc_cond, self.sta_cond)


    def init_task_env(self, *args, **kwargs):
        if not os.path.exists('./scr/flow/%s' % (self.tool_scr_branch) ):
            self.set_config_location(flow_branch=self.branch_name, overwrite=True, quiet=self.quiet)
        else:
            self.set_config_location(flow_branch=self.branch_name, overwrite=self.over_write, quiet=self.quiet)
            
        self.paser_task_dirs(tool_name=self.tool, branch_name=self.branch_name, eco_string=self.eco_string, quiet=self.quiet)
        
    def init_stage(self, *args, **kwargs):
        self.init_task_env(*args, **kwargs)
        
        if not self.parse_scenario(self.scenario):
            self.err('Parse scenario failed!')
            return -1
        self.screen            = screen()
        self.logmsg = ''
        self.stage_status = ''
        self.logfile      = '%s/%s.log' % (self.log_dir, self.session_name)
        self.screen_name  = 'OP4#%s#%s#%s' % (self.init_task_version, self.session_name, self.remotehost)
        self.screen.name         = self.screen_name
        self.screen.screen_log   = self.logfile
        
        if os.path.exists(self.lock_file):
            if self.run_task:
                 self.warn('Current Stage locked: %s' % (self.lock_file) )
                 if self.screen.exists:
                     return self.monitor()
            else:
                 self.err('Current Stage locked: %s' % (self.lock_file) )
                 return -1
        
        if os.path.exists(self.ready_file):
            self.err('Skip Finished Stage: %s' % (self.ready_file) )
            return -1

        print self.src_stage , self.dst_stage
        if self.run_task and not (self.src_stage == self.dst_stage):
            if os.path.exists(self.src_lock_file) and not os.path.exists(self.src_early_complete_file):
                self.err('Source stage is running: %s' % (self.src_lock_file) )
                return -1
    
            if os.path.exists(self.src_failed_file):
                self.err('Source stage Failed: %s' % (self.src_failed_file) )
                return -1
    
            if not os.path.exists(self.src_ready_file) and not os.path.exists(self.src_early_complete_file):
                self.err('Source stage not ready. Unknown status of source stage. (no .fail, no .ready, no .early_complete, no .lock)')
                return -1
            
        #- remove 
        for d in [ self.sum_dir, self.log_dir, self.rpt_dir, self.data_dir ]:
            for f in glob.glob('%s/*%s*' % (d, self.session_name)):
                self.dbg('remove %s' % (f))
                if os.path.isdir(f):
                    shutil.rmtree(f)
                else:
                    os.unlink(f)
            
        self.convert_configs()
        self.set_config_location(flow_branch=self.branch_name, quiet=self.quiet, overwrite=False, update_user_setup=True)


        
        self.opstage_repl_var()
        if not self.check_stage_env():
            return -1
        self.info('Current Stage : %s' % (self.session_name))    
        self.info('logfile       : %s' % (self.logfile)) 
        self.info('screen_name   : %s' % (self.screen_name))
        self.info('Tool Name     : %s' % (self.tool))
        self.info('tempt file    : %s' % (self.src_template))
        self.info('    ==>       : %s' % (self.dst_template))
        self.convert_config_to_tcl_file(self.FLOW_CONFIG)
        self.convert_config_to_tcl_file(self.GLOBAL_VAR_CONFIG)
        self.convert_config_to_tcl_file(self.SYSTEM_CONFIG)
        #- convert stage
        self.convert_eda_scripts(self.src_template, self.dst_template)
        
        self.copy_tempt_dir()
        #- convert other setting files
        return 1

    def convert_config_file(self, config_type):
        dst_config_file = os.path.join(self.dst_branch_config, os.path.basename(getattr(self, '%s_CONFIG' % (config_type))))
        config_dict     = getattr(self, config_type)
        
        is_convert = False
        if os.path.exists(dst_config_file):
            if self.over_write:
                self.warn('%s : %s' % ( 'Overwrite'.ljust(11),  dst_config_file))
                is_convert = True
            else:
                self.dbg('%s : %s' % ('Skip'.ljust(11), dst_config_file))
        else:
            is_convert = True
            self.info('%s : %s' % ('Create'.ljust(11), dst_config_file), info_color=True)
        if is_convert: self.write_conf(config_dict, dst_config_file, quiet=True)

    def convert_config_to_tcl_file(self, config):
        filename, extname = os.path.splitext(os.path.basename(config))
        newfile = [self.block_name, filename, 'tcl']
        filepath = os.path.join(self.stage_scr_dir, '.'.join(newfile))
        is_convert = False
        if os.path.exists(filepath):
            if self.over_write:
                self.warn('%s : %s' % ( 'Overwrite'.ljust(11),  filepath))
                is_convert = True
            else:
                self.dbg('%s : %s' % ('Skip'.ljust(11), filepath))
        else:
            is_convert = True
            self.info('%s : %s' % ('Create'.ljust(11), filepath), info_color=True)
        
        if is_convert: self.convert_tempt(config_files=config, output_file=filepath, tcl_config=True, quiet=True)
        
            
    def convert_configs(self):
        self.branch_config     = self.branch_config
        self.dst_branch_config = os.path.join(self.config_repo, self.branch_name+'.'+self.eco_string)
        self.mkdir(self.dst_branch_config)
        
        for item in ['FLOW', 'GLOBAL_VAR', 'INPUT_DATA', 'SYSTEM']:
            self.convert_config_file(item)        
        
    def convert_eda_scripts(self, src, dst):
        is_convert = False
        if os.path.exists(dst):
            if self.over_write:
                self.warn('%s : %s' % ( 'Overwrite'.ljust(11),  dst))
                is_convert = True
            else:
                self.dbg('%s : %s' % ('Skip'.ljust(11), dst))
        else:
            is_convert = True
            self.info('%s : %s' % ('Create'.ljust(11), dst), info_color=True)
        if is_convert: self.convert_tempt(allvar=self.allvar, input_file=src, output_file=dst, quiet=True, repl_debug=self.repl_debug)
    
    def copy_tempt_dir(self):
        
        dirs  =  [ f for f in glob.glob('%s/*' % (self.stage_tempt_dir) ) if os.path.isdir(f) ]
        files =  [ f for f in glob.glob('%s/*' % (self.stage_tempt_dir) ) if not os.path.isdir(f) ]

        #- dirs      
        for f in files:
            basename = os.path.basename(f)
            mastername, extname = os.path.splitext(basename)
            #print mastername, extname
            dst_filename = [self.block_name, mastername]
            if mastername.split('_')[0] == self.tool: continue
            dst_filename.append(self.branch_name)
            if extname == '.tempt':
                if dst_filename[-1] == self.branch_name:
                    dst_filename = dst_filename[:-1]
                dst_filename.append(self.tool)
            elif extname == '.tempt~':
                continue
            else:
                dst_filename.append(extname.lstrip('.'))
            dst_filename = '.'.join(dst_filename)
            dst = os.path.join(self.stage_scr_dir, dst_filename)
            self.convert_eda_scripts(f, dst)  
            
        for f in dirs:
            basename = os.path.basename(f)
            dst = os.path.join(self.stage_scr_dir, basename)
            if os.path.exists(dst):
                if self.over_write:
                    self.warn('%s : %s/*' % ( 'Remove'.ljust(11),  dst))
                    shutil.rmtree(dst)
                    self.warn('%s : %s/*' % ( 'Create'.ljust(11),  dst))
                    shutil.copytree(f, dst)
                else:
                    self.dbg('%s : %s' % ('Skip'.ljust(11), dst))
            else:
                self.info('%s : %s/*' % ('Create'.ljust(11), dst), info_color=True)
                shutil.copytree(f, dst)
                
        self.link_file('./'+'/'.join(self.dst_branch_config.split('/')[-3:]), 'config.'+os.path.basename(self.dst_branch_config))
        dst=os.path.join('./scr/flow', self.tool_scr_branch, 'config.'+os.path.basename(self.dst_branch_config))
        self.link_file('../../'+'/'.join(self.dst_branch_config.split('/')[-2:]), dst)
        if not os.path.exists(self.user_scr_dir):
            self.mkdir(self.user_scr_dir)

    def link_file(self, src, dst):
        if not os.path.exists(src):
            #self.warn('source path does not exists for link from: %s' % (src) )
            pass
#        if not os.path.exist(dst):
#            self.warn('destination path does not exists for link to: %s' % (dst) )
        if os.path.islink(dst):
            self.dbg('relink %s from %s' % (dst, src) )
            os.unlink(dst)
        os.symlink(src, dst)

    @property
    def tool(self):
        if re.match(r'^\d+', self.stage.split('_')[0]):
            return self.stage.split('_')[1]
        else:
            return self.stage.split('_')[0]

    @property
    def op4_session(self):    
        session_pattern = []
        session_pattern = [ i for i in [ self.mode_name, self.corner_name, self.branch_name, self.userpattern] if i not in ['', None ] ]
        return '.'.join(session_pattern)
        
    @property
    def session_name(self):
        session_pattern = []
        session_pattern = [ i for i in [ self.stage, self.mode_name, self.corner_name, self.branch_name, self.userpattern] if i not in ['', None ] ]
        return '.'.join(session_pattern)
    
    @property
    def ready_file(self):
        return '%s/%s.%s.ready' % (self.sum_dir, self.block_name, self.session_name)

    @property
    def early_complete_file(self):
        return '%s/%s.%s.early_complete' % (self.sum_dir, self.block_name, self.session_name)

    @property
    def failed_file(self):
        return '%s/%s.%s.failed' % (self.sum_dir, self.block_name, self.session_name)

    @property
    def lock_file(self):
        return '%s/%s.%s.lock' % (self.sum_dir, self.block_name, self.session_name)

    @property
    def monitor_file(self):
        return '%s/%s.%s.monitor' % (self.sum_dir, self.block_name, self.session_name)
    
    @property
    def src_session_name(self):
        session_pattern = []
        session_pattern = [ i for i in [ self.src_stage, self.mode_name, self.corner_name, self.src_branch, self.src_eco] if i not in ['', None ] ]
        return '.'.join(session_pattern)
    
    @property
    def src_ready_file(self):
        return '%s/%s.%s.ready' % (self.sum_dir, self.block_name, self.src_session_name)

    @property
    def src_early_complete_file(self):
        return '%s/%s.%s.early_complete' % (self.sum_dir, self.block_name, self.src_session_name)

    @property
    def src_failed_file(self):
        return '%s/%s.%s.failed' % (self.sum_dir, self.block_name, self.src_session_name)

    @property
    def src_lock_file(self):
        return '%s/%s.%s.lock' % (self.sum_dir, self.block_name, self.src_session_name)    
    
    @property
    def tool_tempt_branch(self):
        return '%s.%s' % (self.tool, self.branch_name)
    
    @property
    def tool_scr_branch(self):
        return '%s.%s.%s' % (self.tool, self.branch_name, self.eco_string)

    @property
    def stage_tempt_dir(self):
        path = os.path.join(self.local_flow_repo, self.tool_tempt_branch)
        if not os.path.exists(path):
            self.err('INFO: No such branch in local flow repo. : %s' % (self.branch_name) )
            sys.exit(1)
        return path
    
    @property
    def stage_scr_dir(self):
        path = os.path.join(self.local_flow_repo, self.tool_scr_branch)
        if not os.path.exists(path):
            self.mkdir(path)
        return path
    
    @property
    def src_template(self):
        tempt_name = '%s.%s.%s' % (self.stage, self.branch_name, 'tempt')
        return os.path.join(self.stage_tempt_dir, tempt_name)

    @property
    def dst_template(self):
        scr_name = '%s.%s.%s' % (self.block_name, self.session_name, self.tool)
        return os.path.join(self.stage_scr_dir, scr_name)        
        
    def mkdir(self, dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            #print dirname
            self.info('mkdir "%s"' % (dirname))
    
    def submit(self):
        self.info('Start %s ...' % (self.session_name) )
        self.screen.name    = self.screen_name
        self.screen.screen_log = self.logfile
        #print 11
        if not self.screen.exists:
            if os.path.exists(self.logfile):
                os.unlink(self.logfile)
            create_status = self.screen.create()
            if create_status == 1:
                self.info('Switch to EDA tool run directory: %s' % (self.init_task_version))
                self.screen.cd(self.init_task_version)
                if self.repl_debug:
                    check_lic_level = 'Warning'
                else:
                    check_lic_level = 'Error'
                self.start_eda_tool(check_lic_level=check_lic_level)
            elif create_status == 0:
                self.err('create screen %s failed: screen already exists.' % (self.screen_name))
            elif create_status == -1:
                self.err('create screen %s failed: check screen status timeout' % (self.screen_name))
            elif create_status == -2:
                self.err('create screen %s failed: set prompt failed.' % (self.screen_name))
            elif create_status == -3:
                self.err('create screen %s failed: login remote server failed.' % (self.screen_name))                    
        else:
            self.info('screen %s exists' % (self.screen_name))
        #self.open(self.name)
        #self.lsitinfo()
        pass

    def check_stage_env(self):
        if not self.check_stage_tool() or not self.check_screen_name():
            return False
        return True
    
    def check_stage_tool(self):
        # check tool
        if not self.allvar.has_key('%s_version' % (self.tool)):
            self.err('un-register tool name: %s' % (self.tool))
            return False
        #self.info('Tool Name   : %s' % (self.tool))
        return True

    def check_screen_name(self):
#        status = self.status
#        if self.status == 'NotExists':
#            status = ''
        #self.info('Screen Name : %s %s' % (self.screen_name, status))
        #if self.exists:
        return True

    def start_eda_tool(self, check_lic_level='Error'):
        if self.tool != '':
            # load moudule config
            if self.allvar['MODULE_FILES'] != '' and not os.path.exists(self.allvar['MODULE_FILES']):
                self.dbg('echo %s : %s Not Found' % (check_lic_level, self.allvar['MODULE_FILES']))
                self.screen.sendcommands( 'echo %s : %s Not Found' % (check_lic_level, self.allvar['MODULE_FILES']))
            else:
                self.dbg('module use %s' % (self.allvar['MODULE_FILES']))
                self.screen.sendcommands( 'module use %s' % (self.allvar['MODULE_FILES']) )
            # load global lic
            if not os.path.exists(self.allvar['lic']):
                self.dbg('echo %s : %s Not Found' % (check_lic_level, self.allvar['lic']) )
                self.screen.sendcommands('echo %s : %s Not Found' % (check_lic_level, self.allvar['lic']) )
            else:
                self.dbg('%s %s' % ('source', self.allvar['lic']))
                self.screen.sendcommands('%s %s' % ('source', self.allvar['lic']) )
            # load tool env
            if self.allvar['%s_load' % (self.tool)] == 'source' and not os.path.exists(self.allvar['%s_version' % (self.tool)]):
                self.dbg('echo %s : %s Not Found' % (check_lic_level, self.allvar['%s_version' % (self.tool)]))
                self.screen.sendcommands('echo %s : %s Not Found' % (check_lic_level, self.allvar['%s_version' % (self.tool)]))
            else:
                self.dbg('%s %s' % (self.allvar['%s_load' % (self.tool)], self.allvar['%s_version' % (self.tool)]))
                self.screen.sendcommands('%s %s' % (self.allvar['%s_load' % (self.tool)], self.allvar['%s_version' % (self.tool)]))
            self.mkdir(self.lock_file)
            self.dbg('%s %s' % (self.allvar['%s_exec' % (self.tool)],  self.dst_template ) )
            self.screen.sendcommands('%s %s' % (self.allvar['%s_exec' % (self.tool)],  self.dst_template ) )      
            return True              
        else:
            return False

    def monitor(self):
        self.info('Start Monitor task : %s' % (self.session_name))
        
        if not os.path.exists(self.monitor_file):
            self.mkdir(self.monitor_file)
        else:
            self.warn('Monitor Lock file exists: %s' % (self.monitor_file))
            self.warn('Maybe another client is under monitor. Or, another client is crashed.')
            confirm = raw_input('Continue Monitor? Y|[N]')
            if confirm.lower() == 'y':
                self.info('Contiue Monitor...')
            else:
                return -1
            
        self.screen.attach()
        while True:
            time.sleep(5)
            
            if self.encounter_errors():
                
                if not self.DEBUG:
                    self.is_failed = True
                    self.err('Stage "%s" Failed!' % (self.session_name))
                    self.quit_screens()
                    
                    getoutput('touch %s' % (self.failed_file), quiet=True)
                    self.clean_lock_file()
                    return False
                
                if self.screen.status == 'idle':
                    self.is_ready = True
                    self.err('Stage "%s" Finished Failed!' % (self.session_name))
                    self.quit_screens()
                    
                    getoutput('touch %s' % (self.ready_file), quiet=True)
                    getoutput('touch %s.debug_mode' % (self.failed_file), quiet=True)  
                    self.clean_lock_file()
                    return False

            if os.path.exists(self.early_complete_file):
                self.is_early_complete = True  
                
            if self.screen.status == 'idle':
                self.is_ready = True
                self.is_early_complete = True 
                self.info('Stage "%s" Finished successfully.' % (self.session_name), info_color=True)
                self.quit_screens()
                
                getoutput('touch %s' % (self.ready_file), quiet=True) 
                self.clean_lock_file()
                return True
   
            if not self.screen.exists:
                self.warn('Unknown Task status.')
                self.clean_lock_file()
                return None

    def clean_lock_file(self):
        if os.path.exists(self.lock_file):
            os.removedirs(self.lock_file)
        if os.path.exists(self.monitor_file):
            os.removedirs(self.monitor_file)
            
    def encounter_errors(self, ignore_err='False'):
        is_err = False
        loginfo = {}
        
        #print os.getcwd()
        #print glob.glob(r'%s/log/*%s*log' % (self.init_version, self.session_name))
        for f in glob.glob(r'./log/*%s*log' % (self.session_name)):
            #file = '%s/%s' % (logdir, file)
            self.dbg('#- %-15s : %s' % ('Check LOG' , f ) )
            _loginfo = self.get_log_info(f, waive_list = self.allvar['Waived'].split(), fatal_list = self.allvar['Fatal'].split(), warn_list= self.allvar['Warning'].split())
            loginfo[f] = _loginfo
            if len(_loginfo['error']) or len(_loginfo['fatal']):
                # self.err('#- %-15s : %s' % ('Error happened in Logfile' , f ) )
                if len(_loginfo['error']):  self.logmsg = self.logmsg + '%s\n' % ( _loginfo['error'][0].rstrip() )
                if len(_loginfo['fatal']):  self.logmsg = self.logmsg + '%s\n' % ( _loginfo['fatal'][0].rstrip() )
                
                pre_fatal_len = len(self.fatal_append)
                
                for err in _loginfo['fatal'][pre_fatal_len:]:
                    self.err('%s (Fatal)' % (err) )
                
                self.fatal_append=_loginfo['fatal'][:]

                pre_error_len = len(self.error_append)
                for err in _loginfo['error'][pre_error_len:]:
                    self.err('%s (Error)' % (err) )
                self.error_append = _loginfo['error'][:]
                is_err = True
            else:
                pass
#        if os.path.exists(self.failed): is_err = True
#        if is_err:
#            self.sendmail('Error %s' % (self.workdir), '%s %s\n%s' % (self.stage, self.scenario, self.logmsg))
#        self.dump_log(loginfo)
        return is_err

    def kill_task(self):
        while self.screen.status != 'idle':
            self.screen.ctrl_c()
            time.sleep(1)
            #self.sc.sendcommands('exit')
            #time.sleep(0.5)
        if self.stage_status != 'Stop': self.stage_status = 'Killed'
        #easyprocess('touch ' + self.failed)
        self.stage_status = 'Killed'

    def quit_screens(self, kill=True):
        while self.screen.exists:
          if self.screen.status == 'idle':
            self.screen.close()
          else:
            if kill: self.kill_task()
          time.sleep(1)
        #self.release_all_server()

