#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @title        : print_data_structure
# @description  : print data structure as in ICD
# @author       : Hualin Xiao
# @date         : March. 15, 2019
#
from PyQt4.QtSql import QSqlQueryModel,QSqlDatabase,QSqlQuery
from PyQt4.QtGui import QTableView,QApplication
import sys

if len(sys.argv) == 1:
    print('Print the description of a parameter')
    print('Usage:')
    print('parameter_description  <parameter name>')
else:
    spid=sys.argv[1]
    app = QApplication(sys.argv)
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("idb/idb.sqlite")
    db.open()

    projectModel = QSqlQueryModel()
    projectModel.setQuery('select * from PCF',db)
    projectView = QTableView()
    projectView.setModel(projectModel)
    projectView.show()
    app.exec_()


