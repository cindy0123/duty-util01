#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 09:58:48 2017

@author: marshals
"""

from openv import op4env
from opprocess import opprocess
import os, re

class oplsf(op4env, opprocess):
    def __init__(self, *args, **kwargs):
        super(oplsf, self).__init__(*args, **kwargs)
        self.lsfenv = self.SYSENV['LSF_ENV']['value']
    
    @property
    def bqueues(self):
        p = self.getoutput('source %s; %s' % (self.lsfenv, 'bqueues'), quiet=True )
        #QUEUE_NAME     PRIO      STATUS      MAX  JL/U JL/P JL/H NJOBS  PEND  RUN  SUSP
        #normal          30    Open:Active      -    -    -    -     0     0     0     0
        d = {}
        for line in p:
            m = re.match(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$', line)
            if m:
                if m.group(1) == 'QUEUE_NAME':
                    item_list = m.groups()
                else:
                    queue_name = m.group(1)
                    d[queue_name]={}
                    for i in range(2, 12):
                        d[queue_name][item_list[i-1]] = m.group(i)
            else:
                self.err('Unknow bqueues output "%s"' %  line)
        return d
    
    @property
    def bhosts(self):
        #HOST_NAME          STATUS       JL/U    MAX  NJOBS    RUN  SSUSP  USUSP    RSV 
        #utah               ok              -     24      0      0      0      0      0
        p = self.getoutput('source %s; %s' % (self.lsfenv, 'bhosts'), quiet=True )
        d = {}
        for line in p:
            m = re.match(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$', line)
            if m:
                if m.group(1) == 'HOST_NAME':
                    item_list = m.groups()
                else:
                    hostname = m.group(1)
                    d[hostname]={}
                    for i in range(2, 10):
                        d[hostname][item_list[i-1]] = m.group(i)                    
            else:
                self.err('Unknow bqueues output "%s"' %  line)
        return d
                   
    @property
    def bjobs(self):
        #JOBID   USER    STAT  QUEUE      FROM_HOST   EXEC_HOST   JOB_NAME   SUBMIT_TIME  PROJ_NAME CPU_USED MEM SWAP PIDS START_TIME FINISH_TIME
        #110     marshals RUN   normal     utah        utah        ping 10.1.1.106 03/09-12:24:34 default    000:00:01.00 3556   38020  30272,30274,30275 03/09-12:24:40 - 
        p = self.getoutput('source %s; %s' % (self.lsfenv, 'bjobs -a -W'), quiet=True )
        d = {}
        for line in p:
            m = re.match(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$', line)
            if m:
                if m.group(1) == 'JOBID':
                    item_list = m.groups()
                else:
                    JOBID = m.group(1)
                    d[JOBID]={}
                    for i in range(2, 16):
                        d[JOBID][item_list[i-1]] = m.group(i)                    
            else:
                self.err('Unknow bqueues output "%s"' %  line)
        return d
                
    @property
    def brunnings(self):
        bjobs = self.bjobs
        d = {}
        for i,j in bjobs.items():
            if bjobs[i]['STAT'] == 'RUN':
                d[i] = j
        return d

    def bkill(self, jobid):
        p = self.getoutput('source %s; %s' % (self.lsfenv, 'bjobs -a -W'), quiet=True )
        for line in p:
            if re.match(r'^Job <%s> is being terminated' % (jobid), line):
                return True
        return False
    
    def bsub_cmd(self, *args, **kwargs):
        interative_mode = kwargs.get('interative', True)
        number_of_cpu   = kwargs.get('cpu_num', 1)
        memory_usage    = kwargs.get('mem', 30000)
        job_name        = kwargs.get('job_name', 'default')
        q_name          = kwargs.get('queue_name', 'normal')
        p_name          = kwargs.get('project_name', 'normal')
        exec_cmd        = kwargs.get('exec', 'ping 10.1.1.106')
        
        options         = ['bsub']
        if interative_mode:
            options.append('-Ip')
        if type(number_of_cpu) is int:
            if number_of_cpu > 0:
                options.append('-n %s' % (number_of_cpu))
            else:
                self.err('bsub option error, -n must be > 0')
        else:
            self.err('bsub option error, -n must be an int and > 0')
            
        if type(memory_usage) is int:
            if memory_usage > 0:
                options.append('-R \'rusage[mem=%s] select[type==any]\'' % (memory_usage))
            else:
                self.err('bsub option error, mem must be > 0')
        else:
            self.err('bsub option error, mem must be float type and > 0')
            
        if job_name != '':
            options.append('-J %s' % (job_name))
        
        if q_name != '':
            options.append('-q %s' % (q_name))
            
        if p_name != '':
            options.append('-P %s' % (p_name))
            
        options.append(exec_cmd)
            
        return ' '.join(options)
        
if __name__ == '__main__':
    os.chdir('/proj/OP4/WORK/marshals/proj/div_5/SDR/WORK/marshals/div_5')
    lsf = oplsf()
    from opjson import dumps
    print dumps(lsf.bqueues)
    print dumps(lsf.bhosts)
    print dumps(lsf.bjobs)
    print dumps( lsf.brunnings)
    print lsf.bsub_cmd()
    