import pprint
from core import idb

stix_idb = idb.STIX_IDB
tspid = [
         54320,
         54321,
         54322,
         54323,
         54324,
         54325,
         54326,
         54327,
         54328,
         54332,
         54333,
         54334,
         54335,
         54336,
         54337,
         54338,
         54339,
         54340,
         54341]


for e in tspid:
    sql='select  PCF_NAME, VPD_GRPSIZE , VPD_POS, PCF_WIDTH, VPD_OFFSET from PCF join VPD on VPD_NAME=PCF_NAME and VPD_TPSD= {} order by VPD_POS asc'.format(e)
    res=stix_idb.execute(sql)
    if res:
        print('{}'.format(e))
        print pprint.pprint(res)
    else:
        print('{}, Not in database'.format(e))

