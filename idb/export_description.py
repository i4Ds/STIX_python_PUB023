import sys
sys.path.append('../')
from core import stix_idb
from pprint import pprint

idb=stix_idb.stix_idb()

sql='select PCF_NAME, PCF_DESCR from PCF'
sql2='select SCOS_NAME, SW_DESCR from sw_para'
sql3='select PID_SPID, PID_DESCR from PID'

pcf={row[0]:row[1] for row in idb.execute(sql,None, 'list')}
soc={row[0]:row[1] for row in idb.execute(sql2,None, 'list')}
spid={row[0]:row[1] for row in idb.execute(sql3,None, 'list')}

print('PCF_DESC=')
pprint(pcf)
print('SCOS_DESC=')
pprint(soc)
print('SPID_DESC=')
pprint(spid)
