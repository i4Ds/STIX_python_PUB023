import pprint
from core import stix_idb

stix_idb = idb.STIX_IDB
TPSD = [54111, 54112, 54113, 54115, 54116, 54117, 54121, 54124, 54126, 54144]

for e in TPSD:
    sql = 'select  PCF_NAME, PCF_DESCR, PCF_WIDTH, PCF_CATEG, PCF_NATUR, PCF_PTC, PCF_PFC, PCF_CURTX, PCF_UNIT, VPD_GRPSIZE , VPD_POS, VPD_OFFSET from PCF join VPD on VPD_NAME=PCF_NAME and VPD_TPSD= {} order by VPD_POS asc'.format(
        e)
    res = stix_idb.execute(sql, 'dict')
    if res:
        pprint(res)
    else:
        print('{}, Not in database'.format(e))
