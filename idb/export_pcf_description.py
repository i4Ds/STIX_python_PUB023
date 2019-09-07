from core import stix_idb

idb=stix_idb.stix_idb()

sql='select PCF_NAME, PCF_DESCR from PCF'
sql2='select SCOS_NAME, SW_DESCR from sw_para'

pcf={row[0]:row[1] for row in idb.execute(sql,None, 'list')}
soc={row[0]:row[1] for row in idb.execute(sql2,None, 'list')}

print(soc)
