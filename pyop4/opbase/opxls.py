#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 11:03:51 2017

@author: marshals
"""

from openpyxl import Workbook
from openpyxl import load_workbook
from openv import op4env
from opjson import dump, dumps
import sys, time, os, re
from collections import OrderedDict


class opxls (op4env):
    def __init__(self, *args, **kwargs):
        super(opxls, self).__init__(*args, **kwargs)
        self.check()

        msg_path = os.path.join(os.getcwd(), '.op4log')
        if not os.path.exists(msg_path):
            os.makedirs(msg_path)
    
    def load(self, filename, sheetname=''):
        try:
            return load_workbook(filename).get_sheet_by_name(sheetname)
        except:
            return None
    
    def parse_var_sheet(self, filename, sheetname, keys=['group', 'item', 'value', 'description']):
        ws = self.load(filename, sheetname=sheetname)
        if not ws:
            return OrderedDict()
        d = OrderedDict()
        cnt = 0
        cnt_group = 0
        section=''
        value_dict = OrderedDict()
        for r in ws.rows:
            if cnt == 0:
                cnt += 1
                continue
            i = 0
            for k in keys:
                value_dict[k]=self.get_clean_ch_string(r[i].value)
                i += 1
            if value_dict[keys[0]]:
                cnt_group += 1
                cnt = 1
                section = '%s.%s' % (self.format_index(cnt_group), value_dict[keys[0]])
                section = value_dict[keys[0]]
                d[section]=OrderedDict()
                if value_dict['description']:
                    d[section]['description'] = value_dict['description']
            else:
                item = '%s.%s' % (self.format_index(cnt), value_dict[keys[1]])
                item = '%s' % (value_dict[keys[1]])
                d[section][item] = OrderedDict()
                for k in keys[2:]:
                    if value_dict[k] == None:
                        value_dict[k] = ''
                    d[section][item][k] = value_dict[k]
                cnt += 1
        return d
            
    def parse_repo_sheet(self, filename, sheetname='OP4_Repository', 
                         keys=['group', 'item', 'value', 'description']):
        return self.parse_var_sheet(filename, sheetname, keys)
    
    def parse_EDA_TOOLS(self, filename, sheetname='EDA_TOOLS', 
                        keys=['group','item', 'version', 'exec', 'lic_method', 'description' ]):
        d = self.parse_var_sheet(filename, sheetname, keys)
        #print d
        new = OrderedDict()
        new['Global Env'] = OrderedDict()
        for var, var_dict in d['Global Env'].iteritems():
            new['Global Env'][var] = OrderedDict()
            new['Global Env'][var]['value'] = var_dict['version']
            new['Global Env'][var]['description'] = var_dict['description']
        new['EDA Tools Version'] = OrderedDict()
        new['EDA Tools Execute Method'] = OrderedDict()
        new['EDA Tools License Load Method'] = OrderedDict()
        
        for tool, tool_dict in d['EDA Tools'].iteritems():
            new['EDA Tools Version']['%s_version'%(tool)] = OrderedDict()
            new['EDA Tools Version']['%s_version'%(tool)] = OrderedDict()
            new['EDA Tools Execute Method']['%s_exec'%(tool)] = OrderedDict()
            new['EDA Tools License Load Method']['%s_load'%(tool)] = OrderedDict()

            new['EDA Tools Version']['%s_version'%(tool)]['value'] = tool_dict['version']
            new['EDA Tools Version']['%s_version'%(tool)]['description']  = tool_dict['description']
            new['EDA Tools Execute Method']['%s_exec'%(tool)]['value']  = tool_dict['exec']
            new['EDA Tools License Load Method']['%s_load'%(tool)]['value']  = tool_dict['lic_method']
        return new
                

    def parse_PROJECT(self, filename, sheetname='PROJECT', 
                        keys=['group','item', 'value', 'level', 'type', 'tool', 'description' ]):
        return self.parse_var_sheet(filename, sheetname, keys)
    
    def parse_OP4_SYS_ENV(self, filename, sheetname='OP4_SYS_ENV', 
                          keys=['group','item', 'value', 'level', 'type', 'tool', 'description' ]):
        return self.parse_var_sheet(filename, sheetname, keys)
    
    def get_all_var_names(self, var_dict=OrderedDict()):
        all_VARS=[]
        for g, d in var_dict.iteritems():
            for var, i in d.iteritems():
                all_VARS.append(var.split('.')[-1])
        return all_VARS
    
    def parse_EDA_VAR(self, filename, sheetname='ICC2', 
                          keys=['group','item', 'value', 'level', 'type', 'tool', 'description' ]):
        return self.parse_var_sheet(filename, sheetname, keys)

    def parse_FLOW(self, filename, sheetname='FLOW_CONTROL', 
                          keys=['group','name', 'value', 'level', 'description' ]):
        return self.parse_var_sheet(filename, sheetname, keys)
    
    def get_EDA_VAR(self, filename, tool_list=['ICC2', 'INNVOS', 'EDI', 'STAR', 'PT']):
        EDA_VAR=OrderedDict()
        for tool in tool_list:
            d = self.parse_EDA_VAR(filename, sheetname=tool)
            if len(d.keys()):
                EDA_VAR[tool] = self.parse_EDA_VAR(filename, sheetname=tool)
        return EDA_VAR
    
    def split_eda_var_by_level(self, filename):
        self.check()
        EDA_VAR = self.get_EDA_VAR(filename)
        OP4_VAR = self.parse_OP4_SYS_ENV(filename)
        EDA_VARS_DICT = OrderedDict()
        EDA_VARS_DICT['op4'] = OP4_VAR
        EDA_VARS_DICT.update(EDA_VAR)
        
        BLOCK_VARS  = []
        SYS_VARS    = []
        GLOBAL_VARS = []
        BLOCK_VAR_DICT   = OrderedDict()
        SYS_VAR_DICT     = OrderedDict()
        GLOBAL_VAR_DICT = OrderedDict()
        group_names      = []
        for eda, eda_var_dict in EDA_VARS_DICT.iteritems():
            for group, group_dict in eda_var_dict.iteritems():
                group_names.append('.'.join(group.split('.')[1:]))
                
        for eda, eda_var_dict in EDA_VARS_DICT.iteritems():
            for group, group_dict in eda_var_dict.iteritems():
                gn = '.'.join(group.split('.')[1:])
                gn = '%s.%s' % (self.format_index(group_names.index(gn)+1), gn)
                gn = group
                for var, var_dict in group_dict.iteritems():
                    if var == 'description': continue
                    level = var_dict['level']

                    var = var.split('.')[-1]
                    if level == 'blk':
                        defined_tool=''
                        if var in BLOCK_VARS:
                            gn = self.get_group_name_by_var(BLOCK_VAR_DICT, var)
                            defined_tool= BLOCK_VAR_DICT[gn][var]['tool']
                            
                        if not BLOCK_VAR_DICT.has_key(gn):
                            BLOCK_VAR_DICT[gn] = OrderedDict()
                            BLOCK_VAR_DICT[gn]['description'] = group_dict.get('description', '')
                        if BLOCK_VAR_DICT[gn].has_key(var):
                            var_dict['tool'] = '%s/%s' % (defined_tool, var_dict['tool'])
                        else:
                            BLOCK_VAR_DICT[gn][var] = OrderedDict()
                        del var_dict['level']
                        del var_dict['type']
                        BLOCK_VAR_DICT[gn][var] = var_dict
         
                        if var not in BLOCK_VARS:
                            BLOCK_VARS.append(var)
                    elif level == 'sys':
                        defined_tool=''
                        if var in SYS_VARS:
                            gn = self.get_group_name_by_var(SYS_VAR_DICT, var)
                            defined_tool= SYS_VAR_DICT[gn][var]['tool']
                        
                        if not SYS_VAR_DICT.has_key(gn):
                            SYS_VAR_DICT[gn] = OrderedDict()
                            SYS_VAR_DICT[gn]['description'] = group_dict.get('description', '')
                        if SYS_VAR_DICT[gn].has_key(var):
                            var_dict['tool'] = '%s/%s' % (defined_tool, var_dict['tool'])
                        else:
                            SYS_VAR_DICT[gn][var] = OrderedDict()
                        del var_dict['level']
                        del var_dict['type']
                        SYS_VAR_DICT[gn][var] = var_dict
         
                        if var not in SYS_VARS:
                            SYS_VARS.append(var)
                    elif level == 'global':
                        defined_tool=''
                        if var in GLOBAL_VARS:
                            gn = self.get_group_name_by_var(GLOBAL_VAR_DICT, var)
                            defined_tool= GLOBAL_VAR_DICT[gn][var]['tool']
                        
                        if not GLOBAL_VAR_DICT.has_key(gn):
                            GLOBAL_VAR_DICT[gn] = OrderedDict()
                            GLOBAL_VAR_DICT[gn]['description'] = group_dict.get('description', '')
                        if GLOBAL_VAR_DICT[gn].has_key(var):
                            var_dict['tool'] = '%s/%s' % (defined_tool, var_dict['tool'])
                        else:
                            GLOBAL_VAR_DICT[gn][var] = OrderedDict()
                        del var_dict['level']
                        del var_dict['type']
                        GLOBAL_VAR_DICT[gn][var] = var_dict
         
                        if var not in GLOBAL_VARS:
                            GLOBAL_VARS.append(var)                         
                    else:
                        self.err('Unknown Level: %s in %s %s' % (level, var_dict['level'], gn))
        self.BLOCK_VAR_DICT   = BLOCK_VAR_DICT
        self.SYS_VAR_DICT     = SYS_VAR_DICT
        self.GLOBAL_VAR_DICT  = GLOBAL_VAR_DICT
        
    def get_group_name_by_var(self, group_dcit, var):
        for group, v_dict in group_dcit.iteritems():
            for v in v_dict.keys():
                if v == var:
                    return group
        return None
                
    def format_index(self, cnt):
        index_list = list(str(cnt))
        if len(index_list) == 1:
            return '00'+str(cnt)
        elif len(index_list) == 2:
            return '0'+str(cnt)
        elif len(index_list) == 3:
            return str(cnt)
        
    def get_clean_ch_string(self, chstring):
        """Remove annoying seperators from the Chinese string.
    
        Usage:
            cleanstring = get_clean_ch_string(chstring)
        """
        if chstring == None:
            return None
        chstring = re.sub('^\s+', '', unicode(chstring))
        cleanstring = chstring
        for sep in [u'\u2026']:
            #if re.match(sep, cleanstring):
            #    print cleanstring
            cleanstring = cleanstring.replace(sep, u'...')
        return cleanstring 
    
#if __name__ == '__main__':
#    xls = opxls()    
#    print dump(xls.get_EDA_VAR('/media/sf_depot/onepiece4/release/OP4_Variable_spec_0.2.xlsx'), 'test.json')
#    sys.exit(1)   
      
if __name__ == '__main__':
    import argparse
    xls = opxls()
    #---------------------------- parser args ---------------------------------------------------------
    parser = argparse.ArgumentParser(description='''
    Initialize the project directory for OP4 platform.
    Run it in /proj/{project name} which should be created by IT.
    ''')
    #---------------------------- define args ---------------------------------------------------------
    parser.add_argument("--repo", dest='parse_repo',
                        help="",
                        action="store_true")
    parser.add_argument("--tool", dest='parse_tool',
                        help="",
                        action="store_true")    
    parser.add_argument("--block", dest='parse_block',
                        help="",
                        action="store_true")    
    parser.add_argument("--sys", dest='parse_sys',
                        help="",
                        action="store_true")  
    parser.add_argument("--global", dest='parse_global',
                        help="",
                        action="store_true")
    parser.add_argument("--proj", dest='parse_project',
                        help="",
                        action="store_true")
    parser.add_argument("--flow", dest='parse_flow',
                        help="",
                        action="store_true") 
    parser.add_argument("-o", "--output", dest='output_file',
                        help="",
                        action="store")
    parser.add_argument("-i", "--input", dest='input_file',
                        help="",
                        action="store")
    parser.add_argument("-type", dest='output_type', default='conf', 
                        help="",
                        action="store")
    
    args = parser.parse_args()
    from opconfig import opconfig
    xls.info('Output format: %s' % ( args.output_type ) )
    output_file = os.path.splitext(args.output_file)[0] + '.' + args.output_type
    if args.parse_repo and args.input_file and args.output_file:
        xls.info('Paser %s for repository' % (args.input_file))
        xls.info('Output %s' % (output_file))
        if args.output_type == 'conf':
            opconfig().write_conf(xls.parse_repo_sheet(args.input_file), output_file)
        else:
            dump(xls.parse_repo_sheet(args.input_file), output_file)
        xls.info("Finished.\n")
        
    if args.parse_tool and args.input_file and args.output_file:
        xls.info('Paser %s for Tool' % (output_file))
        xls.info('Output %s' % (output_file))  
        if args.output_type == 'conf':
            opconfig().write_conf(xls.parse_EDA_TOOLS(args.input_file), output_file)        
        else:
            dump(xls.parse_EDA_TOOLS(args.input_file), output_file)
        xls.info("Finished.\n")
        
    if args.parse_block and args.input_file and args.output_file:
        xls.info('Paser %s for Block Level Varibale' % (args.input_file))
        xls.info('Output %s' % (output_file))        
        xls.split_eda_var_by_level(args.input_file)
        if args.output_type == 'conf':
            opconfig().write_conf(xls.BLOCK_VAR_DICT, output_file)
        else:
            dump(xls.BLOCK_VAR_DICT, output_file)
        xls.info("Finished.\n")
        
    if args.parse_sys and args.input_file and args.output_file:
        xls.info('Paser %s for System Level Varibale' % (args.input_file))
        xls.info('Output %s' % (output_file))        
        xls.split_eda_var_by_level(args.input_file)
        if args.output_type == 'conf':
            opconfig().write_conf(xls.SYS_VAR_DICT, output_file)
        else:
            dump(xls.SYS_VAR_DICT, output_file)
        xls.info("Finished.\n")
        
    if args.parse_global and args.input_file and args.output_file:
        xls.info('Paser %s for Global Level EDA TOOL Varibale' % (args.input_file))
        xls.info('Output %s' % (output_file))
        xls.split_eda_var_by_level(args.input_file)
        if args.output_type == 'conf':
            opconfig().write_conf(xls.GLOBAL_VAR_DICT, output_file)
        else:
            dump(xls.GLOBAL_VAR_DICT, output_file)
        xls.info("Finished.\n")

    if args.parse_project and args.input_file and args.output_file:
        xls.info('Paser %s for Proect Level Varibale' % (args.input_file))
        xls.info('Output %s' % (output_file))
        if args.output_type == 'conf':
            opconfig().write_conf(xls.parse_PROJECT(args.input_file),  output_file)
        else:
            dump(xls.parse_PROJECT(args.input_file),  output_file)
        xls.info("Finished.\n")
        
    if args.parse_flow and args.input_file and args.output_file:
        xls.info('Paser %s for Flow Config' % (args.input_file))
        xls.info('Output %s' % (output_file))
        if args.output_type == 'conf':
            opconfig().write_conf(xls.parse_FLOW(args.input_file),  output_file)
        else:
            dump(xls.parse_FLOW(args.input_file),  output_file)
        xls.info("Finished.\n")        
    #print dumps(d)
    #print dump(xls.get_EDA_VAR('/media/sf_D_DRIVE/ICC2_variables_3.1.xlsx'), 'test.json')
    #print xls.split_eda_var_by_level('/media/sf_D_DRIVE/ICC2_variables_3.1.xlsx')



