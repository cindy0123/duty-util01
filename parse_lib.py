#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:40:05 2017

@author: marshals
"""

from openv import op4env
from opfilehandle import myreadline
import re, os, sys
import opjson

class parse_lib(op4env):
    def __init__(self, *args, **kwargs):
        super(parse_lib, self).__init__(*args, **kwargs)
        self.lib_file = kwargs.get('lib_file', None)
        #--- change to config file
        if getattr(self, 'LIB_PATTERN'):
            self.lib_pattern = self.LIB_PATTERN
        else:
            self.lib_pattern_config = kwargs.get('lib_pattern', None)
            if not os.path.exists(self.lib_pattern_config):
                self.err('lib_pattern_config is required')
                sys.exit(1)
            self.lib_pattern = opjson.load(self.lib_pattern_config)

    @property
    def vth(self):
        basename = os.path.basename(self.lib_file)
        for th in self.lib_pattern['vth'].keys():
            for pattern in self.lib_pattern['vth'][th]:
                if re.match(r'\S+%s\S+' % (pattern), basename) and pattern != '':
                    return th
        for th in self.lib_pattern['vth'].keys():
            if self.lib_pattern['vth'][th][0] == '': return th
        return None

    @property
    def track(self):
        basename = os.path.basename(self.lib_file)
        for t in self.lib_pattern['track'].keys():
            for pattern in self.lib_pattern['track'][t]:
                if re.match(r'\S+%s\S+' % (pattern), basename) and pattern != '':
                    return t
        for t in self.lib_pattern['track'].keys():
            if self.lib_pattern['track'][t][0] == '': return t
        return None

    @property
    def model_type(self):
        basename = os.path.basename(self.lib_file)
        for t in self.lib_pattern['model_type'].keys():
            for pattern in self.lib_pattern['model_type'][t]:
                if re.match(r'\S+%s\S+' % (pattern), basename) and pattern != '':
                    return t
        for t in self.lib_pattern['model_type'].keys():
            if self.lib_pattern['model_type'][t][0] == '': return t
        return None

    @property    
    def name(self):
        for line in myreadline(self.lib_file):
            m = re.match(r'^\s*library\s*\(\s*(\S+)\s*\)\s*{\s*', line)
            if m:
               return m.group(1)
        return None

    @property
    def process(self):
        for line in myreadline(self.lib_file):
            m = re.match(r'^\s*nom_process\s*:\s*(\S+)\s*;', line)
            if m:
               return m.group(1)
        return None

    @property
    def version(self):
        for line in myreadline(self.lib_file):
            m = re.match(r'^\s*\*\s*Version:\s*(\S+)', line)
            if m:
               return m.group(1)
        return None

    @property
    def temperature(self):
        for line in myreadline(self.lib_file):
            m = re.match(r'^\s*nom_temperature\s*:\s*(\S+)\s*;', line)
            if m:
               return m.group(1)
        return None

    @property
    def voltage(self):
        for line in myreadline(self.lib_file):
            m = re.match(r'^\s*nom_voltage\s*:\s*(\S+)\s*;', line)
            if m:
               return m.group(1)
        return None

    @property
    def operating_conditions(self):
        for line in myreadline(self.lib_file):
            m = re.match(r'^\s*operating_conditions\s*\(\s*\"(\S+)\"\s*\)\s*{\s*', line)
            if m:
               return m.group(1)
        return None

    @property
    def voltage_map(self):
        voltage_map={}
        for line in myreadline(self.lib_file):
            m = re.match(r'^\s*voltage_map\s*\(\s*(\S+)\s*,\s*(\S+)\s*\)\s*;', line)
            if m:
                voltage_map[m.group(1)] = m.group(2)
            if re.match(r'^\s*cell\s*\(\s*\S+\s*\)\s*', line):
                return voltage_map
        return None

    @property
    def all_cells(self):
        all_cells = {}
        cell_name = ''
        for line in myreadline(self.lib_file):
            m = re.match(r'^\s*cell\s*\(\s*(\S+)\s*\)\s*', line)
            m_area = re.match(r'^\s*area\s*:\s*(\S+)\s*;\s*', line)
            m_footprint = re.match(r'^\s*cell_footprint\s*:\s*"(\S+)"\s*;\s*', line)
            if m:
                cell_name = m.group(1)
                all_cells[cell_name] = {}
            elif m_area:
                all_cells[cell_name]['area'] = m_area.group(1)
            elif m_footprint:
                all_cells[cell_name]['footprint'] = m_footprint.group(1)
        return all_cells
    
if __name__ == '__main__':
    a = "cell ( aa ) {"
    from pyparsing import alphas,alphanums,Word, nums
    import pyparsing
    # identifier
    var_identifier = Word(alphas,alphanums+'_')
    num_identifier   = Word(nums+'.')
    assignmentExpr = var_identifier + "=" +(var_identifier|num_identifier)
    assignmentTokens = assignmentExpr.parseString("pi=3.14159") 
    print assignmentTokens
    
    
    
    
    