#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 11:17:30 2017

@author: marshals
"""

from parse_lib import parse_lib
from opfilehandle import iterfind
import re, os
import opjson

class oplibs(parse_lib):
    def __init__(self, process='tcbn16ff', lib_type='', *args, **kwargs):
        super(oplibs, self).__init__(*args, **kwargs)
        self.process_name = process

    def get_frontend_lib_files(self, root_location='/proj/Mars2/lib/01_SC', lib_type='SC'):
        patterns = self.lib_pattern['dir']
        frontend_libs={}
        self.all_lib_version = []
        self.all_lib_model   = []
        self.all_lib_track   = []
        self.all_lib_cond    = []
        self.all_lib_vth     = []
        self.all_lib_voltage = []
        for f in iterfind(root_location).file('*.lib'):
            for pattern in patterns:
                if re.match(r'\S+%s\S+' % (pattern), f):
                    self.info('Parse lib: "%s"' % (f) )
                    self.lib_file = f
                    lib_type    = lib_type
                    lib_version = self.version
                    lib_model   = self.model_type
                    lib_track   = self.track
                    lib_cond    = self.operating_conditions
                    lib_vth     = self.vth
                    lib_voltage = self.voltage
                    self.all_lib_version.append(lib_version)
                    self.all_lib_model.append(lib_model)
                    self.all_lib_track.append(lib_track)
                    self.all_lib_cond.append(lib_cond)
                    self.all_lib_vth.append(lib_vth)
                    self.all_lib_voltage.append(lib_voltage)                   
                    if not frontend_libs.has_key(lib_version):
                        frontend_libs[lib_version] = {}
                    if not frontend_libs[lib_version].has_key(lib_model):
                        frontend_libs[lib_version][lib_model] = {}
                    if not frontend_libs[lib_version][lib_model].has_key(lib_track):
                        frontend_libs[lib_version][lib_model][lib_track] = {}
                    if not frontend_libs[lib_version][lib_model][lib_track].has_key(lib_cond):
                        frontend_libs[lib_version][lib_model][lib_track][lib_cond] = {}    
                    if not frontend_libs[lib_version][lib_model][lib_track][lib_cond].has_key(lib_vth):
                        frontend_libs[lib_version][lib_model][lib_track][lib_cond][lib_vth] = {}                          
                    if not frontend_libs[lib_version][lib_model][lib_track][lib_cond][lib_vth].has_key(lib_voltage):
                        frontend_libs[lib_version][lib_model][lib_track][lib_cond][lib_vth][lib_voltage] = []
                    frontend_libs[lib_version][lib_model][lib_track][lib_cond][lib_vth][lib_voltage].append(f)
        self.frontend_libs = {}
        self.frontend_libs[self.process_name] = {}
        self.frontend_libs[self.process_name][lib_type] = {}
        self.frontend_libs[self.process_name][lib_type] = frontend_libs
        self.all_lib_version = sorted(list(set(self.all_lib_version)))
        self.all_lib_model   = sorted(list(set(self.all_lib_model)))
        self.all_lib_track   = sorted(list(set(self.all_lib_track)))
        self.all_lib_cond    = sorted(list(set(self.all_lib_cond)))
        self.all_lib_vth     = sorted(list(set(self.all_lib_vth)))
        self.all_lib_voltage = sorted(list(set(self.all_lib_voltage)))
        return self.frontend_libs
    
    def get_frontend_db_files(self, frontend_libs={}):
        frontend_dbs = frontend_libs
        for process_name in frontend_dbs.keys():
            for lib_type in frontend_dbs[process_name].keys():
                for version in frontend_dbs[process_name][lib_type].keys():
                    for lib_model in frontend_dbs[process_name][lib_type][version].keys():
                        for lib_track in frontend_dbs[process_name][lib_type][version][lib_model].keys():
                            for lib_cond in frontend_dbs[process_name][lib_type][version][lib_model][lib_track].keys():
                                for lib_vth in frontend_dbs[process_name][lib_type][version][lib_model][lib_track][lib_cond].keys():
                                    for lib_voltage in frontend_dbs[process_name][lib_type][version][lib_model][lib_track][lib_cond][lib_vth].keys():
                                        dbs = []
                                        for lib in frontend_dbs[process_name][lib_type][version][lib_model][lib_track][lib_cond][lib_vth][lib_voltage]:
                                            dbs.append(self.get_db_name_from_lib_filename(lib))
                                        frontend_dbs[process_name][lib_type][version][lib_model][lib_track][lib_cond][lib_vth][lib_voltage] = dbs
        self.frontend_dbs = frontend_dbs
        return frontend_dbs
    
    def get_db_name_from_lib_filename(self, frontend_lib):
        db = frontend_lib
        for p in self.lib_pattern['db_replace'].keys():
            db = re.sub(p, self.lib_pattern['db_replace'][p], db )
        if not os.path.exists(db):
            self.err('Can not find such db "%s"' % (db))
        else:
            return db
        return None
    
    def dump_info(self, filename=''):
        libinfo = {}
        print self.all_lib_version
        libinfo['lib_versions'] = self.all_lib_version
        libinfo['lib_models']   = self.all_lib_model
        libinfo['lib_tracks']   = self.all_lib_track
        libinfo['lib_conds']    = self.all_lib_cond
        libinfo['lib_vths']     = self.all_lib_vth
        libinfo['lib_voltages'] = self.all_lib_voltage 
        opjson.dump(libinfo, filename)

if __name__ == '__main__':
    lib = oplibs()
    libs = lib.get_frontend_lib_files()
    dbs  = lib.get_frontend_db_files(libs)
    opjson.dump(libs, 'libs.json')
    opjson.dump(dbs, 'db.json')
    lib.dump_info('lib_info.json')
    #for f in oplib().get_frontend_lib_files():
    #    print parse_lib(f).version
#    print parse_lib().version
#    print parse_lib().name
#    print parse_lib().process
#    print parse_lib().temperature               
#    print parse_lib().voltage
#    print parse_lib().voltage_map
    #print parse_lib().all_cells