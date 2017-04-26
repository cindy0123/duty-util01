#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 15:57:19 2017

@author: marshals
"""
import smtplib  
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.mime.image import MIMEImage  
from opmsg import opmsg
import os, getpass

class opmail(opmsg):
    def __init__(self, *args, **kwargs):
        super(opmail, self).__init__(*args, **kwargs)
        
    def send(self, *args, **kwargs):
        sender     = kwargs.get('sender'      , 'op4_admin@alchip.com')
        receiver   = kwargs.get('receiver'    , '%s@alchip.com' % (getpass.getuser()) )
        sub_prefix = kwargs.get('sub_prefix'  , '[OP4-Platform]')
        subject    = kwargs.get('subject'     , 'OP4 email test')
        smtpserver = kwargs.get('smtpserver'  , 'sh.alchip.com')
        username   = kwargs.get('username'    , 'marshals')
        password   = kwargs.get('password'    , '811225')
        text       = kwargs.get('text'        , 'Some HTML text')
        imgs       = kwargs.get('img'         , [ '/user/home/marshals/WorkSpace/aa/1.jpg' , '/user/home/marshals/WorkSpace/aa/1.jpg'])

        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = '%s %s' % (sub_prefix, subject)

        content = ['<ul>']
        if text != '':
            content.append('<li><strong>%s</strong></li>' % (text))
        if len(imgs):
            content.append('<li><strong>Snapshot</strong></li>')
            cnt = 1
            for img in imgs:
                if os.path.exists(img):
                    content.append('<img src="cid:image%s"><br />' % (cnt))
                    fp = open(img, 'rb')
                    msgImage = MIMEImage(fp.read())
                    fp.close()
                    msgImage.add_header('Content-ID', '<image%s>'%(cnt)) 
                    if 'msgImage' in dir(): msgRoot.attach(msgImage)
                    cnt += 1
        content.append('</ul>')

        msgText = MIMEText('\n'.join(content),'html','utf-8')
        msgRoot.attach(msgText)
        
        
        
        smtp = smtplib.SMTP()  
        smtp.connect(smtpserver)
        smtp.login(username, password)  
        smtp.sendmail(sender, receiver, msgRoot.as_string())
        smtp.quit()  

if __name__ == '__main__':
    opmail().send()