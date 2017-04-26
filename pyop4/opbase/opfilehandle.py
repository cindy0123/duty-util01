# -*- coding: utf-8 -*-
"""
Created on Tue Feb 07 11:20:47 2017

@author: Marshal Su
"""

import os, fnmatch
import sys
import hashlib
from os.path import isfile, getsize


class iterfind(object):
  def __init__(self, findpath='./', *args, **kwargs):
    self.findpath = findpath

  def file(self, fnexp, findpath=''):
      if findpath=='':
          findpath = self.findpath
          pass
      for root, dirs, files in os.walk(findpath, followlinks=True):
          for filename in fnmatch.filter(files, fnexp):
              yield os.path.join(root, filename)

  def dir(self, fnexp, findpath=''):
      if findpath=='':
          findpath = self.findpath
      for root, dirs, files in os.walk(findpath, followlinks=True):
          for filename in fnmatch.filter(dirs, fnexp):
              yield os.path.join(root, filename)
              
def myreadline( filename):
    f = open(filename, 'r')
    line = f.readline()
    while line :
        yield line
        line = f.readline()
    f.close()
    #yield None

        
def is_writeable(path, check_parent=False):
    '''
    Check if a given path is writeable by the current user.

    :param path: The path to check
    :param check_parent: If the path to check does not exist, check for the
           ability to write to the parent directory instead
    :returns: True or False
    '''

    if os.access(path, os.F_OK) and os.access(path, os.W_OK):
        # The path exists and is writeable
        return True

    if os.access(path, os.F_OK) and not os.access(path, os.W_OK):
        # The path exists and is not writeable
        return False

    # The path does not exists or is not writeable

    if check_parent is False:
        # We're not allowed to check the parent directory of the provided path
        return False

    # Lets get the parent directory of the provided path
    parent_dir = os.path.dirname(path)

    if not os.access(parent_dir, os.F_OK):
        # Parent directory does not exit
        return False

    # Finally, return if we're allowed to write in the parent directory of the
    # provided path
    return os.access(parent_dir, os.W_OK)

def is_readable(path):
    '''
    Check if a given path is readable by the current user.

    :param path: The path to check
    :returns: True or False
    '''

    if os.access(path, os.F_OK) and os.access(path, os.R_OK):
        return True

    return False

def sumfile(fobj): 
    m = hashlib.new('md5')
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()


def md5sum(fname, ret=''):
    if fname == '-':
        m = hashlib.new('md5')
        m.update(ret)
        ret = m.hexdigest()
    else:
        try:
            f = file(fname, 'rb')
        except:
            return 'Failed to open file'
        ret = sumfile(f)
        f.close()
    return ret


def tailf(file_):
    last_size = getsize(file_)
    while True:
        cur_size = getsize(file_)
        if ( cur_size != last_size ):
            f = open(file_, 'r')
            if cur_size > last_size: f.seek(last_size)
            else: f.seek(0)
            text = f.read()
            f.close()
            last_size = cur_size
            yield text
        else:
            yield ""

def filetail(file,num=-1):
    try:
        fp = open(file,'rU')
        line = fp.readlines()
        fp.close()
        return line[num]
    except:
        return ""

if __name__ == '__main__':
    for f in iterfind('/home/marshals/log').file('*'):
        print f
    #print is_writeable('../db/test.db1', True)
    #print is_readable('db/test.db')
    #print md5sum('__init__.py')

