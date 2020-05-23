#!/usr/bin/python
import sys
import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart



timeout=60
socket.setdefaulttimeout(timeout)

def send_email(subject, content,logging, conf):
    msg=MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] =conf['Email_from']
    msg['To'] = ", ".join(conf['Email_receivers'])
    text= MIMEText(content,'text')
    logging.info("sending email ")
    msg.attach(text)
    username=conf['Email_user']
    password=conf['Email_pwd']
    try:
	server = smtplib.SMTP_SSL(port=conf['port'])
        server.connect(conf['Email_server'])
    except socket.error as e:
	logging.error('Failed to connect to the email server')
	return False
    except socket.timeout:
	logging.error('server connection timeout')
	return False
    #server.starttls()
    #server.login(username,password)
    server.sendmail(conf['Email_from'], conf['Email_receivers'], msg.as_string())
    logging.info("done!")
    server.quit()
    return True

