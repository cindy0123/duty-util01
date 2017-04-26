#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 12:14:42 2017

@author: marshals
"""

import os, sys, re
from opjson import load
from opmsg import opmsg
from opfilehandle import is_writeable
from collections import OrderedDict

class opfileformat(opmsg):
    def __init__(self, *args, **kwargs):
        super(opfileformat, self).__init__(*args, **kwargs)
        self.comment_length = 120
        self.single_comment = '#'*self.comment_length+'\n'
        
    def json_write(self, input_file, output, script_type='conf'):
        if not os.path.exists(input_file):
            self.err('File: %s Not Found!' % (input_file))
            return False
        if not is_writeable(output, check_parent=True):
            self.err('No permission: %s' % (output))
            return False 
        d = load(input_file)  
        self.dict_write(d, output, script_type)
        
    def dict_write(self, d, output, script_type='tcl'):
        of = open(output, 'w')
        if script_type == 'conf':
            of.write('[%s]\n' % ( os.path.basename(output)))
        for g, g_dict in d.iteritems():
            of.write(self.single_comment)
            of.write('#'+g.center(self.comment_length-2)+'#\n')
            of.write(self.single_comment)  
            g_description = d[g].get('description', '')
            if g_description != '':
                for l in g_description.split('\n'):
                    of.write('#- %s\n'% (l))

            max_var_len = 0
            if type(g_dict) not in [ OrderedDict, dict ]:
                continue
            for v, v_dict in g_dict.iteritems():
                if v=='description': continue
                var_len = len(list(v))
                if var_len > max_var_len:
                    max_var_len = var_len
            for v, v_dict in g_dict.iteritems():
                if v=='index': continue
                if v=='description': continue
                description = v_dict.get('description', '')
                value       = v_dict.get('value', '')
                if type(value) in [list]:
                    value = ' '.join(value)
                value = str(value).replace('\n', ' ')
                if script_type=='tcl':
                    cmd = 'set %s "' % (v.ljust(max_var_len))
                    #cmd_len = max_var_len + 5
                elif script_type=='conf':
                    cmd = '%s : ' % (v.ljust(max_var_len))
                    #cmd_len = max_var_len + 3
                else:
                    cmd = 'set %s = "' % (v.ljust(max_var_len))
                    #cmd_len = max_var_len + 6
                if value != '':
                    cmd = self.join_value(cmd, value, script_type=script_type)
                if script_type in [ 'tcl', 'csh' ]:
                    cmd +='"'    
                else:
                    if value == '':
                        cmd += '""'
                body_len = len(list(cmd.split('\n')[-1]))
                des_list = description.split('\n')
                cmd = cmd+' ;# '+des_list[0]+'\n'
                if len(des_list) > 1:
                    for l in des_list[1:]:
                        cmd = cmd+'%s;# %s\n'%(''.ljust(body_len+1), l)
                of.write(cmd)
        of.close()
    
    def join_value(self, cmd, value, script_type):
        line = cmd
        cmd_len = len(list(cmd))
        new_line = line
        for value in value.split():
            if len(list(new_line)) <= self.comment_length/2:
                line += value + ' '
                new_line += value + ' '
            else:
                if script_type in [ 'tcl', 'csh' ]:
                    line += ' \\'
                line += '\n' + ' '.rjust(cmd_len) +value+ ' ' 
                new_line = ' '.rjust(cmd_len) + value+ ' ' 
        #print line
        return re.sub('\s+$', '', line)
        
    def repl_op4var_line(self, ALLVAR, line = 'set abc ${project_root}/\\$ccc/$ccc', is_rep=True, repl_debug=False):
        if not is_rep:
            return line
            
        rep_backslash = '#lklfsenionsef49i90!s566u778'
        comp = re.compile(r'\${([A-Za-z_]+[A-Za-z_0-9]*)}', )
        # replate \$ to internal pattern
        line = re.sub(r'\\\$', rep_backslash, line)
        line = line.rstrip()
        # replace normal $var to ${var}
        line = re.sub(r'\$([A-Za-z_]+[A-Za-z_0-9]+)', '${\g<1>}', line)
        # replace line
        for i in comp.findall(line):
            value = ALLVAR.get(i, None)
            if value == None:
                self.err('Can not find the value of Variable: %s' % (i))
                if not repl_debug: sys.exit(1)
#            print i
            #print value
            line=re.sub(r'\${(%s)}' % (i), str(value), line)
            src_conf = self.get_section_by_var(i)
            if src_conf == None:
                src_conf = 'OP4_options'
            if repl_debug:
                line = '%s ;# replaced by "%s : %s" in "%s"' % (line, i, str(value), src_conf)
            else:
                line = '%s' % (line)
        line = re.sub(r'%s' % (rep_backslash), '$', line)
        return line+'\n'
    
    def repl_op4var(self, infile, outfile, ALLVAR, repl_debug=False):
        of  = open(infile, 'r')
        out = open(outfile, 'w')
        start_rep = False
        cnt = 0
        for line in of.readlines():
            cnt += 1
            if re.match(r'^\s*\%REPL_OP4\s*$', line.rstrip()):
                if start_rep:
                    self.err('Found %%REPL_OP4 again without "OP4_REPL" at line %d' % (cnt))
                start_rep = True
            elif re.match(r'^\s*\REPL_OP4\%\s*$', line.rstrip()):
                start_rep = False
            else:
                new_line = self.repl_op4var_line(ALLVAR=ALLVAR, line=line, is_rep=start_rep, repl_debug=repl_debug)
                out.writelines(new_line)
        of.close()
        out.close()
        return True
        
if __name__ == '__main__' :
    j=opfileformat()
    ALLVAR={}
    ALLVAR['project_root'] = '/proj'
    ALLVAR['ccc']        = 'div_5'
    print j.repl_op4var_line(ALLVAR)
    j.repl_op4var('./test.tmpt', 'test.tcl', ALLVAR)
    j.dict_write(load('/media/sf_depot/onepiece4/examples/200_user_setup.json'), 'aa.tcl', script_type='conf')
    j.dict_write(load('./test.json'), 'bb.tcl', script_type='conf')
    #j.json2tclcsh_write(input_file='/proj/OP4/TEMPLATES/config/global/300_global_tool_var.json', output='./11.csh', script_type='csh')
#    from pyparsing import Word, Optional, OneOrMore, Group, ParseException, alphanums, alphas
#    import pyparsing
#
#    var_identifier    = Word(alphas,alphanums+'_')
#    refvar_identifier = Word('$') + Optional(Word('{')) + Word(alphas,alphanums+'_') + Optional(Word('}'))
#    
#    
#    assignmentExpr = (refvar_identifier).setResultsName("var") 
#    assignmentTokens = assignmentExpr.parseString("${bbb}")
#    print ''.join(assignmentTokens.var)


    
    
    
    
    
    
    
    
    
    