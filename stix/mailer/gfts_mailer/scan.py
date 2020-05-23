#!/usr/bin/python
import sys
import os
import smtplib
import sqlite3
import datetime

from gfts_config  import config
import gfts_db as db

import logging
import mailer
timeout=60
logging.basicConfig(
    format="%(asctime)s   %(message)s",
    level=logging.INFO,
    filename=config['logger'])

def start():
    gfts_db=db.GFTSDB()
    directories=config['ScanDirectories']
    new_files=[]
    new_filetypes=[]
    for directory in directories:
        for root, dirs, files in os.walk(directory['dir']):
            for filename in files:
                filename=(os.path.join(root, filename))
                filetype=directory['type']
                try:
                    if not gfts_db.exist(filename):
                        new_files.append(filename)
                        new_filetypes.append(filetype)
			logging.info('New: %s'%filename)
                except sqlite3.ProgrammingError:
                    loging.warning('Ignored: %s  '%filename)
    if new_files:
        subject='STIX GFTS received new files'
        content='\n'.join(new_files)
        content+='\n'
        content+='*** This is an automatically generated email, please do not reply ***'
        if mailer.send_email(subject,content,logging,config):
            try:
                for filename,filetype in zip(new_files,new_filetypes):
                    gfts_db.insert(filename,filetype)

            except sqlite3.ProgrammingError:
                loging.warning('Not inserted into database: %s  '%filename)
        else:
            loging.warning('Failed to send the notice to emails')

    else:
	logging.info('No new files')




if __name__ == "__main__":
    start()
