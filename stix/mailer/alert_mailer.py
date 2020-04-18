#!/usr/bin/python
import sys
import os
import smtplib
import socket
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




def main_loop():
    while True:
        alert_file=config['stix_alerts']
        with open(alert_file) as f:
            content=f.read()
            if content:
                subject='STIX instrument critical message'
                content+='*** This is an automatically generated email, please do not reply ***'
                if send_email(subject,content,logging,config):
                    f.close()
                    f.open(alert_file,'w').close()
                else:
                    loging.warning('Failed to send the notice to emails')
            else:
                logging.info('No new alerts')

        time.sleep(600)




if __name__ == "__main__":
    main_loop()
