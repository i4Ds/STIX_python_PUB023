#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is a tool to convert Microsoft access database file mdb to sqlite3 database
Please run the following commands before using it
pip3 install sqlalchemy pandas_access
sudo apt install mdbtools

Created on Thu Aug 29 22:28:14 2019
@author: xiaohl
"""

import pandas_access as mdb
from sqlalchemy import create_engine
import sys
import os

if len(sys.argv) != 3:
    print("{0} <MDB File> <Sqlite3 File>".format(sys.argv[0]))
    sys.exit(-1)

if os.path.isfile(sys.argv[2]):
    print("Refusing to modify existing database!")
    sys.exit(-1)

engine = create_engine('sqlite:///{0}'.format(sys.argv[2]), echo=False)
tlist = [tbl for tbl in mdb.list_tables(sys.argv[1])]
print('Tables')
print(tlist)
tables = [{tbl: mdb.read_table(sys.argv[1], tbl)} for tbl in tlist]

#for k in tables:
#  tables[k].to_sql(k, con=engine)
