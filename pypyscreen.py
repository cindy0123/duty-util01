#!/usr/bin/env python

import os, time, socket
import re
## user module
#import shlex
from optimer import timer
from opmsg import opmsg
from opDISPLAY import DISPLAY
from opprocess import opprocess
from opfilehandle import tailf, filetail
#from oplsf import oplsf
###
# from issue
XTERM_BG           = 'SeaGreen'
XTERM_BG           = 'Black'
SCREEN_LS_COLORS     = 'no=00:fi=02;31:di=02;34:ln=02;36:pi=40;33:so=02;31:bd=40;34;01:cd=40;33;01:or=40;35;01:ex=40;33:*.tar=02;35:*.tgz=02;35:*.arj=02;35:*.taz=02;35:*.lzh=02;35:*.zip=02;35:*.z=02;35:*.Z=02;35:*.gz=02;35:*.bz2=02;35:*.deb=02;35:*.rpm=02;35:*.jpg=02;35:*.png=02;35:*.gif=02;35:*.bmp=02;35:*.ppm=02;35:*.tga=02;35:*.xbm=02;35:*.xpm=02;35:*.tif=02;35:*.png=02;35:*.mpg=02;35:*.avi=02;35:*.fli=02;35:*.gl=02;35:*.dl=02;35'

ADV_SCREEN_VERSION = ['4.03.01', '4.01.00devel']

def list_screens():
    """List all the existing screens and build a Screen instance for each
    """
    screen_names = [ ".".join(l.split(".")[1:]).split("\t")[0] for l in opprocess().getoutput("screen -ls | grep -P '\t'", quiet=True) if ".".join(l.split(".")[1:]).split("\t")[0] ]
    #print screen_names
    return [ screen(name=l) for l in screen_names ]

#---------------
#- screen
#---------------
class screen(DISPLAY, opprocess, opmsg):
    def __init__(self, *args, **kwargs):
        self.name          = kwargs.get('name', '')
        self.remotehost    = kwargs.get('remotehost', socket.gethostname())
        self.en_lsf        = kwargs.get('en_lsf', True)
        
        super(screen, self).__init__(*args, **kwargs)

        self.screen_log       = './.screen/%s.log' % (self.name)
        self.timeout_thr   = 20
        self.hostname      = socket.gethostname()
        self.currenthost   = ''
        self.DISP          = self.original
        self.check()
        
    @property
    def exists(self):
        self.check()
        lines = self.getoutput("screen -ls | grep " + self.name, quiet=True)
#        print 22, "screen -ls | grep " + self.name
#        print 11, lines
        if self.name in [".".join(l.split(".")[1:]).split("\t")[0] for l in lines]:
            return True
        return False

    @property
    def created(self):
        ti=timer(thr=self.timeout_thr)
        while not ti.timeout:
            if self.exists:
                return True
        self.err('Check Screen \'' + self.name + '\' Timeout: '+str(self.timeout_thr)+'!' )
        return False

    @property
    def status(self):
        if not self.exists:
            return 'NotExists'
            
        line = filetail(self.screen_log)
        ## id
        _m = re.search( r'\[screen-(\S+)\]%\s+$', line)
        if _m:
            self.currenthost   = _m.group(1)
            return 'idle'
        if re.search(r'Are you sure you want to continue connecting \(yes/no\)\?', line):
            return 'confirm_ssh_key'
        ## logining
        line = filetail(self.screen_log,-2)
        if re.search( r'\[screen-\S+\]\s+ssh\s+', line):
            return 'logining'
        return 'busy'

    @property
    def pid(self):
        """set the screen information related parameters"""
        if self.exists:
            infos = self.getoutput("screen -ls | grep %s" % (self.name), quiet=True)
            return infos[0].split('.')[0]
        else:
            return None

    @property
    def ttch(self):
        """set the screen information related parameters"""
        if self.exists:
            infos = self.getoutput("screen -ls | grep %s" % (self.name), quiet=True)
            return infos[0].split()[-1]
        else:
            return None
        
    def attach(self):
        #cmd = "xterm -bg %s -T %s -e screen -r %s" % (XTERM_BG, self.name, self.name)
        cmd = "xterm -T %s -e screen -r %s" % (self.name, self.name)
        self.getoutput(cmd, wait=False, quiet=True)

    def detach(self):
        cmd = "screen -d " + self.name
        self.getoutput(cmd, quiet=True)
        time.sleep(0.1)

    def cd(self, dir=''):
        self.sendcommands('unalias cd')
        #self.sendcommands('setenv LS_COLORS \\\'%s\\\'' % (SCREEN_LS_COLORS))
        if dir == '':
            dir = os.getcwd()
            self.sendcommands('cd '+ dir)
        else:
            self.sendcommands('cd '+ dir) 


    def login_remote(self):
        if self.remotehost == self.currenthost:
            self.info('Screen %s login "%s" Successfully.' % (self.name, self.remotehost) )
            return True
        if self.DISP == None:
            self.sendcommands('ssh -X ' + self.remotehost)
        else:
            self.sendcommands('ssh ' + self.remotehost)
        self.sendcommands('/bin/sync')
    
        ti=timer(thr=self.timeout_thr)
        while not ti.timeout:
            if self.status == 'confirm_ssh_key':
                self.sendcommands('yes')
            elif self.status != 'logining':
                break
            time.sleep(0.5)
        if ti.timeout:
            self.msg.err('Create Screen \'' + self.name + '\' Timeout: '+str(self.timeout_thr)+'!' )
            return False
        self.prompt()
        if self.remotehost == self.currenthost:
            self.info('Screen "%s" login "%s" Successfully.' % (self.name, self.remotehost) )
            if self.DISP != None:
                self.sendcommands('setenv DISP ' + self.DISP)
            return True
        else:
            self.err('Screen %s login "%s" Failed!' % (self.name, self.remotehost) )
            return False

    def create(self):
        self.check()
        if self.exists:
            self.err('Screen \'' + self.name + '\' Exists!')
            return False
        #print 'create new'
        ## create screen
        if self.screen_version in ADV_SCREEN_VERSION:
            cmd = 'screen -t %s -dmS %s' % (self.name, self.name)
        else:
            cmd = 'xterm -e screen -t %s -S %s &' % (self.name, self.name)
        #print cmd
        self.getoutput(cmd, quiet=True, wait=False)
        ## check if created
        if self.created:
            self.info('Screen "' + self.name + '" Created.')
            self.detach()
        else:
            self.err('Screen \'' + self.name + '\' Created Failed!')
            return False
        self.enable_logs()
        ## login
        if not self.prompt(): return False
        if not self.en_lsf:
            if not self.login_remote(): return False
        ## set directory
        self.cd()
        return True

    def close(self):
        if self.status != 'idle':
            self.info('Screen \'' + self.name + '\' is ' + self.status + '; Skip Exit.')
            return False
        ti=timer(thr=3)
        while not ti.timeout:
            if self.exists:
                pass
            else:
                self.info('Close Screen "%s"' % (self.name))
                return True
            if self.status == 'idle':
                self.sendcommands('exit')
                time.sleep(0.2)

    def prompt(self):
        ti=timer(thr=self.timeout_thr)
        while not ti.timeout:
            if self.status == 'idle':
                return True
            else:
                #cmd = 'set hostname = \`hostname\`'
                #self.sendcommands(cmd)
                #time.sleep(0.2)
                if self.screen_version in ADV_SCREEN_VERSION:
                    cmd = 'set prompt=\\\\\"[screen-`hostname`]%  \\\\\"'
                else:
                    cmd = 'set prompt=\\"[screen-`hostname`]%  \\"'
                self.sendcommands(cmd)
                time.sleep(1)
        self.err('Set Prompt Failed: \'' + self.name + '\' Timeout: '+str(self.timeout_thr)+'!' )
        return False
    
    def enable_logs(self):
        self.getoutput('mkdir -p '+os.path.dirname(self.screen_log), quiet=True)
        self._screen_commands('termcapinfo xterm ti@:te@', "logfile " + self.screen_log, "log on", "logfile flush 0")
        
        self.getoutput('touch '+self.screen_log, quiet=True)
        self.logs=tailf(self.screen_log)
        self.logs.next()

    def disable_logs(self):
        self._screen_commands("log off")
        self.logs=None

    def _screen_commands(self, *commands):
        """allow to insert generic screen specific commands
        a glossary of the existing screen command in `man screen`"""
        for command in commands:
            cmd = 'screen -x ' + self.name + ' -X eval \"' + command + '\"'
            #print cmd
            self.getoutput(cmd, quiet=True)
            time.sleep(0.02)

    def sendcommands(self, *commands):
        for cmd in commands:
            #screen -S session_name -X eval 'stuff "$cmd"\015'.
            
            screenCmd = 'stuff "%s"\\015' % (cmd)
            completeCmd = 'screen -S %s -X eval \'%s\'' % (self.name,screenCmd)
            #screenCmd = "stuff \'"+cmd+"\015\'"
            #completeCmd = "screen -S %s -X eval \"%s\"" % (self.name,screenCmd)
            #print completeCmd
            #args = shlex.split(completeCmd)
            self.getoutput(completeCmd, quiet=True)
            time.sleep(0.1)
          
    def ctrl_c(self):
        screenCmd = "stuff \'"+"\003\'"
        completeCmd = "screen -S %s -X eval \"%s\"" % (self.name,screenCmd)
        #args = shlex.split(completeCmd)
        self.getoutput(completeCmd, quiet=True)
        time.sleep(0.1)
    
    @property
    def screen_version(self):
         return self.getoutput('screen -v', quiet=True)[0].split()[2]

class screens(opprocess, opmsg):
    def __init__(self, *args, **kwargs):
        super(screens, self).__init__(*args, **kwargs)
        self.basedir    = os.getcwd().split('/')[-1]

    @property
    def screens_objects(self):
        try:
            scrn_list = []
            for scrn in list_screens():
                try:
                    if scrn.name.split('#')[0] == 'OP4':
                        scrn_list.append(scrn)
                except:
                    pass
            return scrn_list
        except IndexError:
            return []

    @property
    def current_screens(self):
        screen_names = {}
        for scrn in self.screens_objects:
            screen_info = scrn.name.split('#')[-1].split(':')
            screen_names[scrn.name] = {}
            screen_names[scrn.name]['pid']       = scrn.pid
            screen_names[scrn.name]['stage']     = screen_info[0]
            screen_names[scrn.name]['scenario']  = screen_info[1]
            screen_names[scrn.name]['dir']       = screen_info[2]
            screen_names[scrn.name]['server']    = screen_info[3]
            screen_names[scrn.name]['status']    = scrn.status
        return screen_names

    @property
    def all(self):
        return self.current_screens

    @property
    def idle_lists(self):
        return [  scrn for scrn in self.screens_objects if scrn.status == 'idle' ]

    @property
    def busy_lists(self):
        return [  scrn for scrn in self.screens_objects if scrn.status != 'idle' ]

    def wipe_all(self):
        p=self.getoutput('screen -ls', quiet=True)
        for line in p.stdout.readlines():
            m = re.match( r'^\s+(\d+)\.(\S+)\s+\(Dead\s+\?\?\?\)', line )
            if m:
                self.war('Remove Deaded Screen %s' % (m.group(1)))
                self.getoutput('screen -wipe ' + m.group(1), quiet=True)

    def screen_filter(self, name='all', status='all'):
        screen_lists = []
        if name == 'all' or name == 'current':
            screen_lists.extend(self.screens_objects)
        else:
            screen_lists.extend([ scrn for scrn in self.screens_objects if scrn.name == name ])
            screen_lists.extend([ scrn for scrn in self.screens_objects if re.match(r'.*%s.*' % (name),  scrn.name) ])
            
        if status == 'busy':
            screen_lists = [ scrn for scrn in screen_lists if scrn.status != 'idle' ]
        elif status == 'idle':
            screen_lists = [ scrn for scrn in screen_lists if scrn.status == 'idle' ]
        else:
            screen_lists = screen_lists
        
        screen_names = []
        uniq         = []
        for scrn in screen_lists:
            if scrn.name not in screen_names:
                uniq.append(scrn)
                screen_names.append(scrn.name)
        screen_lists = uniq
        if len(screen_lists) == 0:
            self.warn('No Screen selected.')
        return screen_lists
        
    def open(self, name='all', status='all'):
        screen_lists = self.screen_filter(name, status)
        #print screen_lists
        
        #total_heigth = 834
        width = 415
        h_number = 3
        #v_number = 5
        ### compute how many line
        heigth = 152
    
        cnt_h = 0;
        cnt   = 0;
        for scrn in screen_lists:
            scrn.detach()
            if not scrn.exists:
                continue
            self.info('Open Screen: "%s"' % (scrn.name) ) 
            h = int(heigth * int( cnt / h_number ) )
            w = int(width  * cnt_h)
            cnt_h += 1
            cnt += 1
            if cnt_h == h_number:
                cnt_h = 0
            time.sleep(1)
            #cmd = "xterm -bg %s -geometry 64x9+%d+%d -T %s -e screen -r %s " % (XTERM_BG, w,h,scrn.name, scrn.pid)
            cmd = "xterm -geometry 64x9+%d+%d -T %s -e screen -r %s " % (w,h,scrn.name, scrn.pid)
            #print cmd
            #cmd = "xterm -bg %s -T %s -e screen -r %s &" % (XTERM_BG, scrn.name, scrn.name)
            self.getoutput(cmd, wait=False, quiet=True)

    def hide(self, name='all', status='all'):
        screen_lists = self.screen_filter(name, status)
            
        for scrn in screen_lists:
            scrn.detach()

    def list(self):
        self.info()

    def close(self, name='all', status='all'):
        screen_lists = self.screen_filter(name, status)
        for scrn in screen_lists:
            scrn.close()

    def send(self,cmd):
        for scrn in self.screens_objects:
            scrn.sendcommands(cmd)

    def lsitinfo(self):
        self.info('#------------------------------------------------------- All Screen Information ----------------------------------------------------------------')
        self.info('#- %-120s %10s' % ('Screen Name'.center(120), 'status'.center(10)) )
        self.info('#- %-120s %10s' % ('-' * 110, '-'*8) )
        for scrn in self.idle_lists:
            self.info('#- %-120s %10s%10s' % (scrn.name, 'idle', scrn.ttch) )

        for scrn in self.busy_lists:
            self.info('#- %-120s %10s%10s' % (scrn.name, 'busy', scrn.ttch) )
        self.info('#-------------------------------------------------------------------------------------------------------------------------------------------\n')

#if __name__ == '__main__':
#    disp = DISPLAY()
#    disp.show()
#    if screen().screen_version == '4.03.01':
#        print 11
#        os.chdir('/home/marshals')
#    print os.getcwd()
#    for server in ['utah', 'canton', 'boston']:
#        sc = screen(name ='OP4#'+'sujielei:'+'cworst:'+'screenutils:'+server, remotehost = server)
#        #sc.timeout_thr = 2
#        sc.screen_version
#        sc.create()
#        sc.sendcommands('ls')
#        #sc.attach()
#        #print 'PID', sc.pid
#        #time.sleep(1)
#        #sc.attach()
#        #sc.prompt()
#    scs = screens()
#    scs.basedir = 'screenutils'
#    scs.open()
#    time.sleep(3)
#    scs.close()
#    for sc in scs.idle_lists:
#        screen(sc).close()
    #os.chdir('/media/sf_D_DRIVE/workspace/onepiece4/pyop4/opbase')

#      screen_names[scrn.name]['stage']     = screen_info[0]
#      screen_names[scrn.name]['scenario']  = screen_info[1]
#      screen_names[scrn.name]['dir']       = screen_info[2]
#      screen_names[scrn.name]['server']    = screen_info[3]
#      screen_names[scrn.name]['status']    = scrn.status
#
