#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 11:08:23 2017

@author: marshals
"""

import sys
import json, re

def load(fn, handle_index=True, handle_v=False):
    fp=open(fn, 'r')
    return handel_value(handle_index_on_key(json.load(fp), handle_index), handle_v)

def loads(s, handle_index=True, handle_v=False):
    return handel_value(handle_index_on_key(json.loads(s), handle_index), handle_v)

def dump(s, fn, indent=4):
    fp=open(fn, 'w')
    json.dump(merge_index_on_key(s), fp, indent=indent, sort_keys=True, ensure_ascii=False)
    return fn

def dumps(s, indent=4):
    return json.dumps(merge_index_on_key(s), indent=indent, sort_keys=True, ensure_ascii=False)

def handel_value(d, handle=False):
    if not handle:
        return d
    for key, value in d.iteritems():
        if type(value) is dict:
            value = handel_value(value, handle)
        else:
            if key=='value':
                if type(value) in [str, unicode] and len(value.split('\n')) > 1:
                        value = [ re.sub('^\s+', '', i) for i in value.split('\n') ]
                else:
                    value = value
        d[key] = value
    return d
                    
        
def handle_index_on_key(d, handle_index=True):
    if not handle_index:
        return d
    new = {}
    for key, value in d.iteritems():
        #print key, value
        m = re.match(r'^(\d+)\.(\S+.*)', key)
        if m:
            index     = m.group(1)
            new_key   = m.group(2)
            new[new_key] = {}
            new[new_key]['index']   = index
        else:
            new_key   = key
            new[new_key] = {}
        if type(value) is dict:
            value = handle_index_on_key(value, handle_index)
            new[new_key].update(value)
        else:
            new[new_key] = value
    return new
    
def merge_index_on_key(d, merge_index=True):
    if not merge_index:
        return d
    if type(d) != dict:
        return d
    new = {}

    for key, value in d.iteritems():
        #print key, value
        new_key   = key
        if type(value) == dict:
            if value.has_key('index'):
                index = value['index']
                new_key   = '%s.%s' % (index, key)
                del value['index']
        else:
            new_key   = key
        new[new_key] = {}
        if type(value) is dict:
            value = merge_index_on_key(value, merge_index)
            new[new_key].update(value)
        else:
            new[new_key] = value
    return new

def itervalue(d):
    new = {}
    for key, value in d.iteritems():
        #print key, value
        if type(value) == dict:
            if value.has_key('value'):
                new[key] = value['value']
            value = itervalue(value)
            new.update(value)
    return new
    
if __name__ == "__main__":
#    sys.path.append("../")
#    a = ['a', 'b', 0]
#    print dumps(a)
#    print dumps(load('/proj/OP4/TEMPLATES/config/400_flow_control.json', handle_v=True))
     d= load('/media/sf_depot/onepiece4/examples/200_user_setup.json')
     print itervalue(d)

#    for ff in iterfind('../').file('*.conf'):
#        print "INFO: find config", ff
#        conf = config()
#        conf.read(ff)
#        dict = conf.config_dic()
#        #print json.dumps(dict, indent=4, sort_keys=True, ensure_ascii=False)
#        json_file = '%s.%s' % (os.path.splitext(ff)[0], "json")
#        print json_file
#        fp = open(json_file, 'w')
#        json.dump(dict, fp, indent=4, sort_keys=True, ensure_ascii=False)

