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
    tm5_log=config['tm5_log']

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
