#!/usr/bin/env python
"""
Created on Tue Feb 07 11:20:47 2017

@author: Marshal Su
"""
from opfilehandle import is_writeable
import os, time, sys, stat
from optcl import optcl
   
class opmsg(optcl):
  """
  example:
    from msg import *
    message = msg(debug)
    message.info(xxx)
    message.warn(xxx)
    message.err(xxx)
    message.dbg(xxx)
  """
  
  def __init__(self, *args, **kwargs):
      super(opmsg, self).__init__(*args, **kwargs)
      self.TIMESTAMP   = time.strftime("%Y%m%d%H%M", time.localtime())
#      if not os.path.exists('%s/.Onepiece4/op4log/' % (os.getenv('HOME'))):
#          os.makedirs('%s/.Onepiece4/op4log/' % (os.getenv('HOME')))
#      self.msglog      = '%s/.Onepiece4/op4log/%s_%s.log' %  ( os.getenv('HOME'), 'onepiece4', self.TIMESTAMP )
      if not os.path.exists('%s/.op4log/' % (os.getcwd())):
          os.makedirs('%s/.op4log/' % (os.getcwd()))
          permission=stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH
          os.chmod('%s/.op4log/' % (os.getcwd()), permission)
      self.msglog      = '%s/.op4log/%s_%s.log' % (os.getcwd(), 'onepiece4', self.TIMESTAMP)
      self.check()
      self.DEBUG       = kwargs.get('debug', False)
              
  def format_message(self, message, position = '', length = 0 ):
    message = str(message)
    if position == 'center':
      message = message.center(length)
      pass
    elif position == 'right':
      message = message.rjust(length)
      pass
    else:
      message = message.ljust(length)
      pass
    return message

  def printline (self, message, type='', info_color=False):
    log_message = ''
    read_color = '\033[0;31m'
    purple_color = '\033[35m'
    color_end    = '\033[0m'
    green_color  = '\033[32m'
    self.check()
    if type != '':
      if type == 'ERROR' or type == 'DEBUG':
        print_message = "%s%-7s : %s%s" % ( read_color, type, message, color_end )
      elif type == 'WARNING':
        print_message = "%s%-7s : %s%s" % ( purple_color, type, message, color_end )
      else:
        if not info_color:
          print_message = "%-7s : %s" % ( type, message )
        else:
          print_message = "%s%-7s : %s%s" % ( green_color, type, message, color_end )
      log_message = "%-7s : %s" % ( type, message )
    else:
      print_message = "%s" % ( message )
      log_message = message
    print print_message
    if self.msglog != '':
      fo = open(self.msglog, 'a')
      fo.write(log_message+'\n')
      fo.close()

  def info(self, message = '', with_head = True, position = '', length = 0, info_color=False):
    message = self.format_message(message , position , length )
    self.check()
    type = 'INFO'
    if not with_head:
      type = ''
    self.printline ( message, type, info_color)

  def shellinfo(self, message = '', with_head = True, position = '', length = 0 ):
    message = self.format_message(message , position , length )
    self.check()
    type = 'SHELL'
    if not with_head:
      type = ''
    self.printline ( message, type)
    
  def warn(self, message = '', with_head = True, position = '', length = 0 ):
    message = self.format_message(message , position , length )
    self.check()
    type = 'WARNING'
    if not with_head:
      type = ''
    self.printline ( message, type)

  def err(self, message = '', with_head = True, position = '', length = 0 ):
    message = self.format_message(message , position , length )
    self.check()
    type = 'ERROR'
    if not with_head:
      type = ''
    self.printline (message, type)

  def dbg(self, message = '', with_head = True, position = '', length = 0 ):
    if self.DEBUG:
      message = self.format_message(message , position , length )
      type = 'DEBUG'
      if not with_head:
        type = ''
      self.printline (message, type)


if __name__ == "__main__":
    TIMESTAMP     = time.strftime("%Y%m%d%H%M", time.localtime())
    opmsg().err("message")