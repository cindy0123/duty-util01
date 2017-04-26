#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 14:35:11 2017

@author: marshals
"""

import time, os, getpass, stat
from opmsg import opmsg
from optcl import optcl
from opconfig import opconfig
import re, sys
from opfilehandle import iterfind
from opgit import basegit
from pypyscreen import getoutput, getstderr



OP4_VERSION         = '2017.03'



class op4env (basegit, opconfig, iterfind):
    def __init__(self, *args, **kwargs):
        super(op4env, self).__init__(*args, **kwargs)
        
        self.username    = getpass.getuser()
        self.home_root   = os.path.dirname(os.getenv("HOME"))
        self.home        = os.getenv("HOME")
        self.HOME        = os.getenv("HOME")
        self.op4_home    = os.path.join(self.home, '.Onepiece4')
        self.version()
        self.check_env()
        
    def init_repo_loction(self, *args, **kwargs):
        quiet                    = kwargs.get('quiet', False)
        
        # gloden
        self.ref_flow_repo           = self.allvar['flow']
        self.ref_config_repo         = self.allvar['config']
        self.ref_signoff_check_repo  = self.allvar['signoff_check']
        # project
        self.project_flow_repo           = os.path.join(self.project_template_dir, 'flow')
        self.project_config_repo         = os.path.join(self.project_template_dir, 'config')
        self.project_signoff_check_repo  = os.path.join(self.project_template_dir, 'signoff_check')
        
        if not quiet:
            self.info('----------------------------- Platform Repository Configure --------------------------')
            self.info('Repository Config  : %s' % (self.REPO_CONFIG))
            self.info('Flow repo          : %s' % (self.ref_flow_repo))
            self.info('Config repo        : %s' % (self.ref_config_repo))
            self.info('Signoff-check repo : %s' % (self.ref_signoff_check_repo))
            self.info('')
            self.info('----------------------------- Project Repository Configure --------------------------')
            self.info('Flow repo          : %s' % (self.project_flow_repo))
            self.info('Config repo        : %s' % (self.project_config_repo)) 
            self.info('Signoff-check repo : %s' % (self.project_signoff_check_repo))
            self.info('--------------------------------------------------------------------------------------\n')
            
    def set_config_location(self, *args, **kwargs):
        '''
        A. config directory required:
            1. when init project diectory: get the config files in /project/xx/TEMPLATE
            2. when init run dir: get the config file in local scr dir
        B. REPO dir:
            1. when init dir, no project repo_setting.conf. will use the one in OP_PATH
        '''
        flow_branch   = kwargs.get('flow_branch', 'default')
        update_var    = kwargs.get('update_var',  True)
        quiet         = kwargs.get('quiet', False)
        exclude       = kwargs.get('exclude', [])
        repo_file     = kwargs.get('repository_config_file', None)
        update_user_setup = kwargs.get('update_user_setup', False)
        eco_string    = getattr(self, 'eco_string', '')
        overwrite     = kwargs.get('overwrite', True)
        
        dir_list = []
        if hasattr(self, 'project_dir'):
            dir_list.append('%s/TEMPLATES'% (self.project_dir))
        if hasattr(self, 'scr_dir'):
            dir_list.append('%s'% (self.scr_dir))
        if len(dir_list) == 0:
            self.err('Can not find scr_dir or project_dir')
            sys.exit(1)
            
        if not overwrite:
            flow_branch = '.'.join( [ n for n in [ flow_branch, eco_string ] if n != '' ] )
        else:
            flow_branch = '.'.join( [ n for n in [ flow_branch ] if n != '' ] )

        for d in dir_list:
            #- repo file
            self.REPO_CONFIG         = '%s/config/system/repo_setting.conf'        % (d)
            if not os.path.exists(self.REPO_CONFIG):
                if repo_file != None:
                    if not os.path.exists(repo_file):
                        self.err('repo file: %s Not Exists!' (repo_file) )
                        sys.exit(1)
                    self.REPO_CONFIG     = repo_file
                else:
                    self.REPO_CONFIG     = os.path.join(self.op_sys_dir, 'repo_setting.conf')
            self.config_repo         = '%s/config'                                 % (d)
            self.LIB_PATTERN_CONFIG  = '%s/config/dp/lib_pattern.conf'             % (d)
            self.PROJ_CONFIG         = '%s/config/100_project_info.conf'           % (d)
            self.EDA_TOOL_CONFIG     = '%s/config/200_eda_tool.conf'               % (d)     
            self.FLOW_CONTROL_CONFIG = '%s/config/300_flow_control.conf'           % (d)
            self.ERROR_CONFIG        = '%s/config/999_error_control.conf'          % (d)
            
            #- scr settings
            self.branch_config       = '%s/config/%s'                    % (d, flow_branch) 
            self.SYSTEM_CONFIG       = '%s/sys_setting.conf'             % (self.branch_config)
            self.GLOBAL_VAR_CONFIG   = '%s/100_common_setup.conf'        % (self.branch_config)
            if not hasattr(self, 'FLOW_CONFIG') or update_user_setup:
                self.FLOW_CONFIG         = '%s/200_user_setup.conf'          % (self.branch_config)
            self.INPUT_DATA_CONFIG   = '%s/300_input_data.conf'          % (self.branch_config)
                        
        if not quiet:
            self.info('----------------------------- Platform Configs Location ------------------------------')
            self.info('Repository Config           : %s' % (self.REPO_CONFIG) )
            self.info('Lib pattern Config          : %s' % (self.LIB_PATTERN_CONFIG) )
            self.info('Project Config              : %s' % (self.PROJ_CONFIG) )
            self.info('EDA Tool Config             : %s' % (self.EDA_TOOL_CONFIG) )
            self.info('Error Control Config        : %s' % (self.ERROR_CONFIG) )
            self.info('Global EDA Tool Var. Config : %s' % (self.GLOBAL_VAR_CONFIG) )
            self.info('Flow Config                 : %s' % (self.FLOW_CONFIG) )
            self.info('Input Data Config           : %s' % (self.INPUT_DATA_CONFIG))
            self.info('System Config               : %s' % (self.SYSTEM_CONFIG) )
            self.info('--------------------------------------------------------------------------------------\n')
        self.clean_conf()
        if update_var:
            for conf in ['REPO', 'LIB_PATTERN', 'PROJ', 'EDA_TOOL', 'ERROR', 'FLOW_CONTROL',  'GLOBAL_VAR', 'FLOW', 'INPUT_DATA', 'SYSTEM', ]:
                if conf in exclude: continue
                conf_file = eval('self.%s_CONFIG' % (conf))
                #self.info(conf_file)
                if os.path.exists(conf_file):
                    if not quiet: self.info('read %s ...' % (conf_file))
                    self.read_conf(conf_file)
                    setattr(self, conf, self.get_section(os.path.basename(conf_file)))
            self.allvar = self.all_config()

    def paser_system_dirs(self, quiet=False):
        if not hasattr(self,'project_dir'):
            self.project_dir            = self.allvar['PROJECT_DIR']
        if not hasattr(self,'project_name'):
            self.project_name           = self.allvar['PROJECT_NAME']
            
        self.project_template_dir   = os.path.join(self.project_dir, 'TEMPLATES')
        self.lib_dir                = os.path.join(self.project_dir, 'LIB')
        self.sc_lib_dir             = os.path.join(self.lib_dir, 'SC')
        self.io_lib_dir             = os.path.join(self.lib_dir, 'IO')
        self.mem_lib_dir            = os.path.join(self.lib_dir, 'MEM')
        self.ip_lib_dir             = os.path.join(self.lib_dir, 'IP')
        self.techfile_dir           = os.path.join(self.lib_dir, 'Techfile')
        self.project_config_dir     = os.path.join(self.project_template_dir, 'config')
        if not quiet:
            self.info('----------------------------- System Dir Info ----------------------------------------')
            self.info('Project Dir             : %s' % (self.project_dir) )
            self.info('Project Template Dir    : %s' % (self.project_template_dir) )
            self.info('--------------------------------------------------------------------------------------\n')
        
        
    def paser_user_dirs(self, quiet=False):
        #self.design_phase_dir = os.path.join(self.project_dir, self.design_phase)
        self.work_dir         = os.path.join(self.project_dir, 'WORK')
        self.release_dir      = os.path.join(self.project_dir, 'RELEASE', self.design_phase)
        self.release_vnet_dir = os.path.join(self.release_dir, self.block_name, 'VNET')
        self.release_sdc_dir  = os.path.join(self.release_dir, self.block_name, 'SDC')
        self.release_fp_dir   = os.path.join(self.release_dir, self.block_name, 'FP')
        self.release_upf_dir  = os.path.join(self.release_dir, self.block_name, 'UPF')
        self.release_scandef_dir  = os.path.join(self.release_dir, self.block_name, 'SCANDEF')
        self.user_dir         = os.path.join(self.work_dir, getpass.getuser())
        self.block_dir        = os.path.join(self.user_dir, self.block_name)

    def paser_task_dirs(self, quiet=False, tool_name = '', branch_name='default', eco_string=''):
        self.init_task_version  = "V%s_S%s_F%s" % (self.init_vnet_version, self.init_sdc_version, self.init_fp_version)
        self.design_phase     = self.allvar['design_phase']
        self.block_name       = self.allvar['BLOCK_NAME']
        self.project_dir      = self.allvar['PROJECT_DIR']
        #self.design_phase_dir = os.path.join(self.project_dir, self.design_phase)
        self.paser_user_dirs()
        self.task_dir               = os.path.join(self.block_dir, self.init_task_version )
        self.run_dir                = self.task_dir
        self.log_dir                = os.path.join(self.run_dir, 'log')
        self.sum_dir                = os.path.join(self.run_dir, 'sum')
        self.data_dir               = os.path.join(self.run_dir, 'data')
        self.rpt_dir                = os.path.join(self.run_dir, 'rpt')
        self.scr_dir                = os.path.join(self.run_dir, 'scr')
        
        self.local_config_repo      = os.path.join(self.scr_dir, 'config')
        self.local_flow_repo        = os.path.join(self.scr_dir, 'flow')
        self.local_signoff_check_repo        = os.path.join(self.scr_dir, 'signoff_check')
        
        self.branch_scr_dir          = os.path.join(self.local_flow_repo, tool_name+'.'+branch_name+'.'+eco_string)
        self.local_proc_dir         = os.path.join(self.branch_scr_dir, 'proc')
        self.local_plugins_dir      = os.path.join(self.branch_scr_dir, 'plugin')
        self.local_setup_dir        = os.path.join(self.branch_scr_dir, 'setups')
        self.user_scr_dir           = os.path.join(self.branch_scr_dir, 'user_scripts')
        if tool_name == '':
            self.local_proc_dir         = ""
            self.local_plugins_dir      = ""
            self.local_setup_dir        = ""
            self.user_scr_dir           = self.local_plugins_dir    
        
        self.branch_proc_dir         = self.local_proc_dir
        self.branch_plugins_dir      = self.local_plugins_dir
        self.branch_setup_dir        = self.local_setup_dir
        
        #self.SYSTEM = self.set_group_var(self.SYSTEM, '', self.branch_proc_dir)
        self.SYSTEM = self.set_group_var(self.SYSTEM, 'PROC_DIR', self.local_proc_dir)
        self.SYSTEM = self.set_group_var(self.SYSTEM, 'COMMON_SET_DIR', self.local_setup_dir)
        self.SYSTEM = self.set_group_var(self.SYSTEM, 'PLUGIN_DIR', self.local_plugins_dir)
        self.SYSTEM = self.set_group_var(self.SYSTEM, 'USER_SCRIPTS_DIR', self.user_scr_dir)
        self.SYSTEM = self.set_group_var(self.SYSTEM, 'FLOW_BRANCH_DIR', os.path.join(self.local_flow_repo, tool_name+'.'+branch_name+'.'+eco_string))
        self.SYSTEM = self.set_group_var(self.SYSTEM, 'CONF_BRANCH_DIR', os.path.join(self.local_flow_repo, tool_name+'.'+branch_name+'.'+eco_string, 'config'))

        self.branch_setup_conf      = os.path.join(self.local_config_repo, 'flow_setup.json')
        self.setup_tcl              = os.path.join(self.local_setup_dir  , 'flow_setup.tcl')
        self.setup_csh              = os.path.join(self.local_setup_dir  , 'flow_setup.csh')
        self.system_tcl             = os.path.join(self.local_setup_dir  , 'system.tcl')
        self.system_csh             = os.path.join(self.local_setup_dir  , 'system.csh')
        self.input_data_tcl         = os.path.join(self.local_setup_dir  , 'input_data.tcl')
        self.input_data_csh         = os.path.join(self.local_setup_dir  , 'input_data.csh')
            
        if not quiet:
            self.info('----------------------------- User Work Info ----------------------------------------')
            self.info('RELEASE Dir (%s Phase)  : %s' % (self.design_phase, self.release_dir) )
            self.info('Task run Dir            : %s' % (self.run_dir) )
            self.info('Task Log Dir            : %s' % (self.log_dir) )
            self.info('Task summary Dir (DP)   : %s' % (self.sum_dir) )
            self.info('Task Inter-Data Dir     : %s' % (self.data_dir) )
            self.info('Task Report Dir         : %s' % (self.rpt_dir) )
            self.info('Task Script Dir         : %s' % (self.scr_dir) )
            self.info('Task Config Dir         : %s' % (self.local_config_repo) )
            self.info('Task Flow script Dir    : %s' % (self.local_flow_repo) )
            if tool_name != '':
                self.info('Stage Script Dir        : %s' % (self.branch_scr_dir) )
                self.info('Stage Proc Dir          : %s' % (self.branch_proc_dir) )
                self.info('Stage plugin Dir        : %s' % (self.branch_plugins_dir) )
                self.info('Stage setup Dir         : %s' % (self.branch_setup_dir) )
                self.info('Stage User script Dir   : %s' % (self.user_scr_dir) )
            self.info()
            self.info('----------------------------- Task Repository Configure --------------------------')
            self.info('Flow repo          : %s' % (self.local_flow_repo))
            self.info('Config repo        : %s' % (self.local_config_repo))
            self.info('Signoff-check repo : %s' % (self.local_signoff_check_repo))            
            self.info('--------------------------------------------------------------------------------------\n')
    
    def parse_init_version(self, quiet=False):
        gz_type   = ['', '.gz']
        VNET_type = ['*.v', '*.vg']
        SDC_type  = ['*.tcl', '*.sdc']
        FP_type   = ['*.def', '*.tcl']
        UPF_type   = ['*.upf']
        SCANDEF_type   = ['*.scandef']
        get_type  = ['VNET', 'SDC', 'FP', 'UPF', 'SCANDEF']
        vnet_list = []
        sdc_list = []
        fp_list = []
        upf_list = []
        scandef_list = []
        self.init_upf_version = self.allvar['UPF_VERSION']
        self.init_scandef_version = self.allvar['SCANDEF_VERSION']
        for gz in gz_type:
            for g in get_type:
                formats = eval('%s_type'%(g))
                for file_format in formats:
                    findpath = os.path.join(getattr(self, 'release_%s_dir'  %(g.lower())), 
                                            getattr(self, 'init_%s_version' %(g.lower()))
                                            )
                    for f in self.file('%s%s' % (file_format, gz), findpath=findpath):
                        eval('%s_list.append("%s")' % (g.lower(), f) )
        self.init_vnet = ' '.join(sorted(vnet_list))
        self.init_sdc  = ' '.join(sorted(sdc_list))
        self.init_fp   = ' '.join(sorted(fp_list))
        self.init_upf   = ' '.join(sorted(upf_list))
        self.init_scandef   = ' '.join(sorted(scandef_list))
        self.INPUT_DATA = {}
        self.INPUT_DATA['Initial Data']={}
        self.INPUT_DATA['Initial Data']['VNET_LIST']={}
        self.INPUT_DATA['Initial Data']['SDC_LIST']={}            
        self.INPUT_DATA['Initial Data']['FP_LIST']={}
        self.INPUT_DATA['Initial Data']['UPF_LIST']={}
        self.INPUT_DATA['Initial Data']['SCANDEF_LIST']={}
        self.INPUT_DATA['Initial Data']['VNET_LIST']['value'] = self.init_vnet
        self.INPUT_DATA['Initial Data']['SDC_LIST']['value'] = self.init_sdc
        self.INPUT_DATA['Initial Data']['FP_LIST']['value'] = self.init_fp
        self.INPUT_DATA['Initial Data']['UPF_LIST']['value'] = self.init_upf
        self.INPUT_DATA['Initial Data']['SCANDEF_LIST']['value'] = self.init_scandef
        
        modes = []
        for f in self.init_sdc.split():
            fname = os.path.basename(f)
            m = re.match(r'%s.(\S+).sdc' % (self.block_name), fname)
            if m:
                mode = m.group(1)
                if mode not in modes:
                    modes.append(mode)
                if not hasattr(self, 'init_sdc_%s' % (mode)):
                    setattr(self, 'init_sdc_%s' % (mode), f)
                    self.INPUT_DATA['Initial Data']['SDC_%s'%(mode)] = {}
                    self.INPUT_DATA['Initial Data']['SDC_%s'%(mode)]['value'] = f
                else:
                    s = getattr(self, 'init_sdc_%s' % (mode))
                    setattr(self, 'init_sdc_%s' % (mode), s+' '+f)
                    self.INPUT_DATA['Initial Data']['SDC_%s'%(mode)]['value'] = s+' '+f
                    
        if not quiet:        
            self.info('----------------------------- Initial Data ------------------------------------------')
            self.info('Initial Data Version   : %s' % (self.init_task_version))        
            self.info('Netlist                : %s' % (self.init_vnet))
            for mode in modes:
                sdcs = getattr(self, 'init_sdc_%s' % (mode))
                self.info('%s : %s' % ('SDC_%s'%(mode).ljust(18), sdcs))
            self.info('Floorplan              : %s' % (self.init_fp))
            self.info('--------------------------------------------------------------------------------------\n')

    def parse_current_run_dir(self, *args, **kwargs):
        quiet = kwargs.get('quiet', False)
        cwd = os.getcwd()
        work_dir_pattern =  '^V(\S+)_S(\S+)_F(\S+)$'
        #print work_dir_pattern
        op4_dir_recomplile = re.compile(work_dir_pattern)
        results = op4_dir_recomplile.findall(os.path.basename(cwd))
        #print results
        if len(results) == 0:
            self.err('Current running path (%s) is an illegal format' % (os.getcwd()) )
            self.err('Please start under Vxxx_Sxxx_Fxxx' )
            sys.exit(1)
        else:
            self.op4_dir = results[0]
            #print results[0]
            self.init_vnet_version, self.init_sdc_version, self.init_fp_version = results[0]
        
        #print self.init_vnet_version, self.init_sdc_version, self.init_fp_version
        self.info('Current Working Direcory: "%s"' % (cwd))  
        #self.FLOW_CONFIG = os.path.join(cwd, '%s.json' % (os.path.basename(cwd)) )
        #self.FLOW        = opjson.load(self.FLOW_CONFIG)
        #self.project_dir = self.FLOW['Project Common Dir']['PROJECT_DIR']['value']
        self.scr_dir     = os.path.join(cwd, 'scr')

    def handle_json_var(self, p):
        newp = p
        for i in re.compile(r'\$\#\{(\S+?)\}', re.M).findall(p):
            if self.SYSENV.get(i):
                newp=newp.replace(r'$#{%s}'%(i), self.SYSENV.get(i))
            elif len(i.split('/')) == 2:
                s = i.split('/')
                value = self.SYSENV.get(s[0]).get(s[1])
                if value:
                    #print self.SYSENV.get(s[0]).get(s[1])
                    newp=newp.replace(r'$#{%s}'%(i), value)
        return newp

    def mkdir(self, dirname, permission='OWNER'):
#        stat.S_ISUID: Set user ID on execution.
#        stat.S_ISGID: Set group ID on execution.
#        stat.S_ENFMT: Record locking enforced.
#        stat.S_ISVTX: Save text image after execution.
#        stat.S_IREAD: Read by owner.
#        stat.S_IWRITE: Write by owner.
#        stat.S_IEXEC: Execute by owner.
#        stat.S_IRWXU: Read, write, and execute by owner.
#        stat.S_IRUSR: Read by owner.
#        stat.S_IWUSR: Write by owner.
#        stat.S_IXUSR: Execute by owner.
#        stat.S_IRWXG: Read, write, and execute by group.
#        stat.S_IRGRP: Read by group.
#        stat.S_IWGRP: Write by group.
#        stat.S_IXGRP: Execute by group.
#        stat.S_IRWXO: Read, write, and execute by others.
#        stat.S_IROTH: Read by others.
#        stat.S_IWOTH: Write by others.
#        stat.S_IXOTH: Execute by others.
        if permission == 'OWNER':
            permission=stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH
        elif permission == 'ALL':
            permission=stat.S_IRWXU|stat.S_IRWXG|stat.S_IROTH|stat.S_IXOTH
        else:
            permission=stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            #print dirname
            self.dbg('mkdir "%s"' % (dirname))
            os.chmod(dirname, permission)

    def version(self):
        time.strftime("%Y%m%d%H%M", time.localtime())
        head_middle=[
        "OnePiece4 Platform (R)",
        "Version %s" % (OP4_VERSION),
        "Copyright (c) 2003-2017 by Alchip Technologies, Limited.",
        "ALL RIGHTS RESERVED",
        "",
        "By : Marshal Su (marshals@alchip.com)",
        "Support : op4_support@alchip.com",
        ]
        head_normal=[
        "",
        "This program is proprietary and confidential information of Alchip Technologies, Limited.",
        "and may be used and disclosed only as authorized in a license agreement",
        "controlling such use and disclosure.",
        ""
        ]
        for line in head_middle:
          self.printline(line.center(89))
        
        for line in head_normal:
          self.printline(line)
        return OP4_VERSION
    
    def check_env(self):
        if not ( self.__check_op_path() and self.__check_required_program() ):
            self.err('Check OP Env Failed')
            sys.exit(1)
        self.__check_vim_syntax(ext='conf')
        self.dbg('libc Version: %s' % ( self.__libc_version() ))
            
    def __check_op_path(self):
        if not os.getenv('OP_PATH'):
            self.err('Please "setenv OP_PATH /proj/OP4/RELEASE/Onepiece4_%s"' % (OP4_VERSION) )
            return False
        else:
            self.op_sys_dir = os.getenv('OP_PATH')
            if not os.path.exists(self.op_sys_dir):
                self.err('OP_PATH : "%s" not found!' % (self.op_sys_dir))
                return False
        return True
    
    def __check_required_program(self):
        required = ['git', 'screen', 'xterm', 'module']
        return self.__has_program(' '.join(required))
    
    def __libc_version(self):
        libcs = [ '/lib/x86_64-linux-gnu/libc.so.6', 
                 '/lib64/libc.so.6',
                ]
        for f in libcs:
            if not os.path.exists(f): continue
            comp = re.compile(r'release version (\S+),')
            for line in getoutput(f, quiet=True):
                f = comp.findall(line)
                if len(f):
                    return f[0]
        return 'Unknown'
    
    def __has_program(self, program):
        cmd = 'which %s' % (program)
        self.stdout = getoutput(cmd, quiet=True)
        comp = re.compile(r'^(\S+): Command not found\.')
        check_ok = True
        for line in self.stdout:
            f = comp.findall(line)
            if len(f):
                self.err('OP4 Requried Linux command "%s" Not Found. Please ask IT to install on Current Server.' % f[0])
                check_ok=False
        return check_ok
            
    def __check_vim_syntax(self, ext='conf'):
        pass
#        syntax = os.path.join(self.home, '.vim/syntax', '%s.vim' % (ext))
#        src    = os.path.join(self.home_root, 'marshals', '.vim/syntax', '%s.vim' % (ext))
#        if not os.path.exists(syntax):
#            if not os.path.exists(os.path.driname(syntax)):
#                os.path.mkdirs(os.path.driname(syntax))
#            return True
            
    def set_aliases(self):
        of = open('%s/.alias' % self.op4_home, 'r')
        
        of.close()
        
        
if __name__ == '__main__':
    os.chdir('/home/marshals/proj/pll_div')
    
    env=op4env()
#    #print env.logdir
#    for key, value in sorted(env.__dict__.iteritems()):
#        if type(value) == int or type(value) == str or type(value) == float or type(value)==unicode:
#            print '%-30s: %s' % (key, value)
#        else:
#            print '%-30s: %s' % (key, type(value))
    
