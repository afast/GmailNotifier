#!/usr/bin/env python

import sys
import gtk
import appindicator
import pynotify

import imaplib
import re
import email.header
import ezPyCrypto
import quopri
import os

PING_FREQUENCY = 10 # seconds

class CheckGMail:
    def __init__(self):
        directory= os.path.dirname(os.path.realpath(__file__))
        self.ind = appindicator.Indicator("new-gmail-indicator", directory+"/normal.png" , appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_attention_icon(directory+"/new.png")

        self.menu_setup()
        self.ind.set_menu(self.menu)
        self.last_count=0

        fd = open(directory+"/.ex_mykey.priv","rb")
        k = ezPyCrypto.key(fd.read())
        fd.close()

        fd=open(directory+"/email", "rb")
        self.email= k.decString(fd.read())
        fd.close()
        fd=open(directory+"/pwd", "rb")
        self.pwd= k.decString(fd.read())
        fd.close()

    def menu_setup(self):
        self.menu = gtk.Menu()

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        self.check_mail()
        gtk.timeout_add(PING_FREQUENCY * 1000, self.check_mail)
        gtk.main()

    def quit(self, widget):
        sys.exit(0)

    def unir(self, arreglo):
        res=[]
        for i in arreglo:
            if i[1] != None:
                res.append(i[0].decode(i[1]))
            else:
                res.append(i[0])
        return ''.join(res)

    def get_first_text_part(self, msg):
        maintype = msg.get_content_maintype()
        if maintype == 'multipart':
            for part in msg.get_payload():
                print part.get_content_charset(part.get_payload())
                if part.get_content_maintype() == 'text':
                    resp= ' '
                    if part['Content-Transfer-Encoding'] == 'quoted-printable':
                        resp= quopri.decodestring(part.get_payload())
                    if part.get_content_charset(False):
                        resp = part.get_payload().decode(part.get_content_charset())
                        print resp
                    return resp
            for part in msg.get_payload():             
                return self.get_first_text_part(part)
        elif maintype == 'text':
            resp= ''
            print msg.get_content_charset(msg.get_payload())
            if msg['Content-Transfer-Encoding'] == 'quoted-printable':
                resp= quopri.decodestring(msg.get_payload())
            if msg.get_content_charset(False):
                resp = msg.get_payload().decode(msg.get_content_charset())
            print resp
            return resp
        else:
            return ' '

    def check_mail(self):
        messages, unread, msg_notify = self.gmail_checker(self.email, self.pwd)
        print ''.join(msg_notify)
        if unread > 0:
            self.ind.set_status(appindicator.STATUS_ATTENTION)
	    if unread > self.last_count:
	    	n = pynotify.Notification(str(unread)+" new e-mail(s)", ''.join(msg_notify), "notification")
    		n.show()
        else:
            self.ind.set_status(appindicator.STATUS_ACTIVE)
    	self.last_count= unread
        return True

    def gmail_checker(self, username, password):
        i = imaplib.IMAP4_SSL('imap.gmail.com')
        i.login(username, password)
        x, y = i.status('INBOX', '(MESSAGES UNSEEN)')
        i.select('INBOX','readonly')
        typ, data = i.search(None,'UNSEEN')
        msg_notify= []
        messages=0
        unseen=0
        if typ == 'OK':
            for msg_num in data[0].split():
                typ, msg = i.fetch(str(msg_num), "RFC822")
                if typ == 'OK':
                    mail_msg = email.message_from_string(msg[0][1])
                    aux= email.header.decode_header(mail_msg['from'])
                    fr=self.unir(aux)
                    if len(fr) > 40:
                        fr= fr[:37]+'...'
                    try:
                        msg_notify.append('From: '+ fr.encode('utf-8') +'\n')
                    except:
                        msg_notify.append('From: ##Encode error##\n')
                    aux=email.header.decode_header(mail_msg['subject'])
                    sub=self.unir(aux)
                    if len(sub) > 40:
                        sub= sub[:37]+'...'
                    try:
                        msg_notify.append('Subject: ' + sub.encode('utf-8') +'\n')
                    except:
                        msg_notify.append('From: ##Encode error##\n')
                    bod=self.get_first_text_part(mail_msg)
                    print bod.__class__
                    if not isinstance(bod, str) and not type(bod).__name__ == 'unicode':
                        bod='(No content)'
                    bod=re.sub('[ \t\n\r]+',' ', bod)
                    if re.search("<html>", bod.lower()):
                        bod=re.sub('<.*?>', '', bod)
                    if len(bod) > 40:
                        bod=(bod[:37]+'...')
                    #print bod
                    try:
                        msg_notify.append('Msg: '+ bod.encode('utf-8') + '\n')
                    except:
                        msg_notify.append('Msg: ##Encode error##\n')
            messages = int(re.search('MESSAGES\s+(\d+)', y[0]).group(1))
            unseen = int(re.search('UNSEEN\s+(\d+)', y[0]).group(1))
        return (messages, unseen, msg_notify)

if __name__ == "__main__":
    indicator = CheckGMail()
    indicator.main()

