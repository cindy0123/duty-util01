#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  1 13:48:04 2017

@author: marshals
"""

import os, re
import opConfigParser
from opfileformat import opfileformat
from opfilehandle import is_writeable
from collections import OrderedDict

## user module

class opconfig(opfileformat):
    def __init__(self, *args, **kwargs):
        super(opconfig, self).__init__(*args, **kwargs)
        self._config = opConfigParser.ConfigParser()
        self.comment_length = 120
        self.single_comment = '#'*self.comment_length+'\n'
        self.description = OrderedDict()

    def config2script(self, input_file, output, script_type='tcl'):
        self.check()
        if not os.path.exists(input_file):
            self.err('File: %s Not Found!' % (input_file))
            return False
        if not is_writeable(output, check_parent=True):
            self.err('No permission: %s' % (output))
            return False  
        self.read_conf(input_file)
        d = self.get_section(os.path.basename(input_file))        
        self.dict_write(d, output, script_type)

    def clean_conf(self):
        self._config = opConfigParser.ConfigParser()
        
    def read_conf(self, config_file):
        self.check()
        if os.path.exists(config_file):
            self._config.read(config_file)
            self.description.update(self.parse_description(config_file))
            return True
        else:
            self.err('%-15s : %s' % ( 'No such file', config_file ) )
            return False
        
    def write_conf(self, d, output_file, quiet=False):
        self.check()
        if not quiet: self.info('Write       : %s' % output_file, info_color=True)
        self.dict_write(d, output_file,  script_type='conf')
        
    def parse_description(self, config_file):
        self.check()
        of = open(config_file, 'r')
        group_name = 'default'
        var_name = ''
        d = OrderedDict()
        section = ''
        for line in of.readlines():
            if re.match('^\s*#+$', line): continue
            m_section = re.match('^\s*\[\s*(\S+)\s*\]', line)
            m_group = re.match('^\s*#+\s*(.*\S+)\s*#$', line)
            m_group_description = re.match('^\s*#\-\s*(.*)\s*#$', line)
            m_var   = re.match('^\s*(\S+)\s*:.*;# (.*)$', line)
            m_var_m = re.match('^\s*(\S+)\s*:\s*(.*)\s*$', line)
            m_des   = re.match('^\s*.* ;# (.*)$', line)
            
            if m_group_description:
                m_group_description.group(1)
                d[group_name]['description'] += '\n'+m_group_description.group(1)
            elif m_section:
                section = m_section.group(1)
            elif m_group:
                group_name = m_group.group(1)
                if not d.has_key(group_name):
                    d[group_name] = OrderedDict()
                    d[group_name]['description'] = ''
                pass
            elif m_var:
                var_name = m_var.group(1)
                if not d[group_name].has_key(var_name):
                    d[group_name][var_name] = OrderedDict()
                d[group_name][var_name]['description'] = m_var.group(2)
            elif m_var_m:
                var_name = m_var_m.group(1)
                #print var_name
                if not d[group_name].has_key(var_name):
                    d[group_name][var_name] = OrderedDict()
                d[group_name][var_name]['description'] = ''                    
            elif m_des:
                d[group_name][var_name]['description'] += '\n'+m_des.group(1) 
        of.close()
        rd = OrderedDict()
        rd[section] = d
        return rd
        
    def get_section(self, section):
        dict1 = OrderedDict()
        _options = self._config.options(section)
#        print self._config.sections()
#        print self.description
        for _option in _options:
            group = self.get_group(section, _option)
            description = self.get_description(section, _option)
            g_description = self.description[section][group].get('description', '')
            
            if group:
                if not dict1.has_key(group):
                    dict1[group]=OrderedDict()
            else:
                print _option
            try:
                dict1[group]['description'] = g_description
                dict1[group][_option] = OrderedDict()
                dict1[group][_option]['value'] = self.format_value(self._config.get(section, _option))
                dict1[group][_option]['description'] = description
            except:
                self.err("exception on %s!" % _option)
                dict1[group][_option] = OrderedDict()
        return dict1
    
    def get_section_vars(self, section):
        dict1 = OrderedDict()
        _options = self._config.options(section)
        for _option in _options:
            try:
                dict1[_option] = self.format_value(self._config.get(section, _option))
            except:
                self.err("exception on %s!" % _option)
                dict1[_option] = OrderedDict()
        return dict1

    def get_group(self, section, var_name):
        for group, g_dict in self.description[section].iteritems():
            if g_dict=='description': continue
            if g_dict.get(var_name, None) != None:
                return group
        return False

    def get_section_by_var(self, var_name):
        all_dict = self.config_dic()
        for _section, section_dict in all_dict.iteritems():
            if section_dict.has_key(var_name):
                return _section
        return None
            
    def get_description(self, section, var_name):
        for group, g_dict in self.description[section].iteritems():
            if g_dict=='description': continue
            var_dict = g_dict.get(var_name, None)
            if var_dict != None:
                return var_dict.get('description', '')
        return False
    
    def all_config(self):
        '''flatten gorup name'''
        dict1 = OrderedDict()
        _sections = self._config.sections()
        for _section in _sections:
            _options = self._config.options(_section)
            for _option in _options:
                try:                    
                    dict1[_option] = self.format_value(self._config.get(_section, _option))
                except:
                    self.err("exception on %s!" % _option)
                    dict1[_option] = None
        return dict1

    def format_value(self, value):
        #print value
        value = re.sub( r'\n', " ", value)
        value = re.sub( r'\s+', " ", value)
        value = re.sub( r'^"', '', value)
        value = re.sub( r'^\'', '', value)
        value = re.sub( r'\'$', '', value)
        value = re.sub( r'\s*;\s*#\s*.*', '', value)
        value = re.sub( r'"\s*$', '', value)
        lowcase = value.lower()
        if lowcase in ['true', 'false']:
            if lowcase == 'true':
                value = True
            if lowcase == 'false':
                value = False
        return value
    
    def config_dic(self):
        '''dict by session name'''
        _sections = self._config.sections()
        dict1 = OrderedDict()
        for _section in _sections:
            dict1[_section] = self.get_section(_section)
        return dict1
    
    def set_group_var(self, d, var, value):
        has_set = False
        for g, g_dict in d.iteritems():
            if type(g_dict) not in [ OrderedDict, dict ] : continue
            if g_dict.has_key(var):
                d[g][var]['value'] = value
                has_set = True
        if not has_set:
            if var != '':
                self.warn('set new variable "%s"' % (var))
                d[g][var] = OrderedDict()
                d[g][var]['value'] = value
        return d
    

if __name__ == '__main__':
    import opjson
    conf = opconfig()
    #conf.read_conf('/media/sf_depot/onepiece4/pyop4/opbase/example/scripts/system_user.conf')
    #conf.read_conf('/media/sf_depot/onepiece4/pyop4/opbase/example/scripts/common_setting.conf')
    conf.read_conf('/media/sf_depot/onepiece4/pyop4/opbase/bb.tcl')
    print opjson.dump(conf.description, 'des.conf')
    conf.write_conf(conf.get_section('bb.tcl'), 'tt.conf')
    #print opjson.dumps(conf.all_config())
    #conf.parse_description('/media/sf_depot/onepiece4/pyop4/opbase/bb.tcl')



