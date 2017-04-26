#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 09:36:53 2017

@author: marshals
"""

import os, time
from opmsg import opmsg
from opprocess import opprocess

class DISPLAY(opprocess, opmsg):
    def __init__(self, *args, **kwargs):
        self.original      = os.environ["DISPLAY"]
        self.new           = kwargs.get('port', 'canton:47.0')
        
        super(DISPLAY, self).__init__( *args, **kwargs )
        #self.TIMESTAMP   = time.strftime("%Y%m%d%H%M", time.localtime())
        #self.DEBUG       = os.getenv('DEBUG')

    def check(self):
        p = opprocess().getstderr("xclock -help", quiet=True)
        if len(p) == 0:
            return True
        self.err( 'Error: Can not access display port \'%s\'' % (os.environ["DISPLAY"]) )
        return False

    def show(self):
        os.environ["DISPLAY"] = self.original
        self.dbg(os.environ["DISPLAY"])

    def hide(self):
        if self.check():
            os.environ["DISPLAY"] = self.new
        else:
            self.show()

    @property
    def is_show(self):
        if os.environ["DISPLAY"] == self.original:
            return True
        else:
            return False

    def is_hide(self):
        if os.environ["DISPLAY"] != self.original:
            return False
        else:
            return True
#        
##!/bin/bash
##
##Start X-windows frame buffer server in background Xvfb should be in the $PATH
#A=`id -u $USERNAME`    # first part is the unique user ID
#B=`date +%S`           # second part time in seconds
#VP=`echo ":"$A$B`      # build the "port string"
#Xvfb -nolisten inet6 $VP -screen 0 1280x1024x24 -ac -terminate > /dev/null 2>&1 &  # start in backround
#XVFB_PID=$!
#export DISPLAY=$VP.0   #Set X-windows display
#...
#...  # now execute what ever you need
#...
#kill -9 $XVFB_PID      # normally Xvfb should end, when the prog stops, just as back up ...
            
if __name__ == '__main__':
    a = DISPLAY()
    a.show()
    print a.new
    print a.original
    print a.check()
    print a.original
