from stix_parser.core import stix_idb
idb = stix_idb.stix_idb()
def get_telemetry_length(spid):
    rows=idb.get_fixed_packet_structure(spid)
    last_row=rows[-1]
    return last_row['PLF_OFFBY']+last_row['PCF_WIDTH']/8

def get_all_fixed_length_telcommand():
    sql='select PID_TPSD, PID_DESCR from PID where PID_TPSD>0'
    res = idb.execute(sql, None, 'dict')
    print(res)

get_all_fixed_length_telcommand()
