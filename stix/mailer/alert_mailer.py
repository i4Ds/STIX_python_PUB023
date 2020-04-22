#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This script is used to send stix instrument alerts (e.g. TM(5,2)) to STIX team
    parser daemon writes alerts to a file whose filename defined in core/config.py (default path is /opt/stix/log)
    As pub023 is not able to send email, the log is rsync to gfts by /opt/stix/rsync-pub023.
    This script thus runs on gfts server. The work flow is as below
    1) parser_daemon write message to /opt/stix/log/stix_alerts.log on pub023
    2) rsync running on gfts fetches the file and delete it from pub023 after rsync every 1 minute
    3) mailer send message to STIX team
    4) mailer delete the file on GFTS

"""
import sys
import os
import smtplib
import socket
import time
import datetime
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import logging


Receivers=['hualin.xiao@fhnw.ch']#, 'laszlo.etesi@fhnw.ch', 'shane.maloney@tcd.ie','ghurford@ssl.berkeley.edu','stefan.koegl@fhnw.ch', 'krucker@ssl.berkeley.edu']
config={
'Email_from':'stix_obs@fhnw.ch',
'Email_user':'',
'Email_pwd':'',
'Email_server':'lmailer.fhnw.ch',
'logger':'/opt/stix/log/stix_mailer.log',
'port':465,
'stix_alerts':'/opt/stix/log/stix_alerts.log',
'Email_receivers':Receivers
}

timeout=60
socket.setdefaulttimeout(timeout)

logging.basicConfig(
    format="%(asctime)s   %(message)s",
    level=logging.INFO,
    filename=config['logger'])

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




def main():
        alert_file=config['stix_alerts']
        if not os.path.exists(alert_file):
            print('no alert')
            return
        with open(alert_file) as f:
            content=f.read()
            if content:
                subject='STIX instrument critical message'
                
                if send_email(subject,content,logging,config):
                    f.close()
                    os.remove(alert_file)
                else:
                    loging.warning('Failed to send the notice to emails')
            else:
                logging.info('No new alerts')





if __name__ == "__main__":
    main()
