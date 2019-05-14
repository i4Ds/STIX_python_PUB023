from core import stix_parser
from core import idb
import struct as st
from core import header as stix_header
from core import stix_global
from core import stix_logger
_stix_logger=stix_logger._stix_logger
import pprint
_stix_idb = idb._stix_idb
class StixTelecommandParser(stix_parser.StixTelemetryParser):
    def __init__(self, stix_idb=_stix_idb, logger_filename=None, logger_level=10):
        super().__init__(stix_idb, logger_filename, logger_level)
    def parse_telecommand_header(self, packet):
        # see STIX ICD-0812-ESC  (Page
        # 56)
        if packet[0] != 0x1D:
            return stix_global._header_first_byte_invalid, None
        header_raw = st.unpack('>HHHBBBB', packet[0:10])
        header = {}
        for h, s in zip(header_raw, stix_header._telecommand_raw_structure):
            header.update(stix_parser.unpack_integer(h, s))
        status= self.check_header(header,'tc')
        info=self.idb.get_telecommand_characteristics(header['service_type'],
                header['service_subtype'], header['source_id'])
        header['DESCR']=info['CCF_DESCR']+' - ' +info['CCF_DESCR2']
        header['SPID']=''
        header['name']=info['CCF_CNAME']
        if status == stix_global._ok:
            try:
                header['ACK_DESC']=stix_header._ACK_mapping[header['ACK']]
            except KeyError:
                status=stix_global._header_key_error
        return status, header

    def parse_telecommand_parameter(self,header,packet):
        pass
    def parse_telecommand_packet(self, buf):
        header_status,header=self.parse_telecommand_header(buf)
        if header_status != stix_global._ok:
            _stix_logger.warn('Bad telecommand header ')
        else:
            pprint.pprint(header)
        return header,None

