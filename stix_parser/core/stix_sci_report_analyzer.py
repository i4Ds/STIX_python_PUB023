import sys
import numpy as np
from . import stix_datatypes as sdt
from . import stix_datetime
from . import stix_logger
logger = stix_logger.get_logger()


class StixCalibrationReportAnalyzer(object):
    """
      Capture calibration reports and fill calibration information into a MongoDB collection

    """

    def __init__(self, collection):
        self.report = None
        self.sbspec_counts = np.zeros((8,12*32), dtype=np.int32)
        self.packet_index= np.zeros((8,12*32), dtype=np.int32)
        self.db_collection = None
        self.current_calibration_run_id = 0
        self.db_collection = collection
        self.spectra=[]
        #self.background_spectra=[[] for x in range(0,12*32)]
        try:
            self.current_calibration_run_id = self.db_collection.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_calibration_run_id = 0

    def capture(self, run_id, packet_id, pkt):
        if not self.db_collection:
            return
        packet = sdt.Packet(pkt)
        if packet.SPID != 54124:
            return


        detector_mask=packet[10]
        pixel_mask=packet[12]



        detector_ids = packet.get('NIX00159/NIXD0155')[0]
        pixel_ids = packet.get('NIX00159/NIXD0156')[0]
        subspc_ids=packet.get('NIX00159/NIXD0157')[0]
        sbspec_spectra = packet.get('NIX00159/NIX00146/*.eng')[0]
        sbspec_formats=[(packet[i*4+15].raw, packet[i*4+16].raw, packet[i*4+17].raw) for i in range(0,8)]

        for i in range(0, len(detector_ids)):
            sbspec_id=subspc_ids[i]
            detector_id=detector_ids[i]
            pixel_id=pixel_ids[i]
            sbspec_spectrum=sbspec_spectra[i]
            self.spectra.append((sbspec_id, detector_id, pixel_id,sbspec_spectrum))
            num_counts=0
            try:
                num_counts=sum(sbspec_spectrum)
            except TypeError:
                logger.warning("Counts not decompressed. File id: {}, Packet id:{}".format(run_id, 
                    packet_id))
            self.sbspec_counts[sbspec_id][detector_id*12+pixel_id] = num_counts
            self.packet_index[sbspec_id][detector_id*12+pixel_id]= packet_id


        if packet['seg_flag'] in [1, 3]:
            #first or standalone packet
            sbspec_mask=packet[13].raw
            sbspec_status=[False for i in range(0,8)]
            for i in range(0,8):
                if sbspec_mask & (1<<i) !=0:
                    sbspec_status[i]=True

            self.report = {
                'run_id': run_id,
                'packet_ids': [packet_id],
                'sbspec_formats':sbspec_formats,
                'sbspec_status':sbspec_status,
                'sbspec_mask':sbspec_mask,
                'header_unix_time': packet['unix_time'],
                '_id': self.current_calibration_run_id,
            }
        else:
            #continuation packet
            if not self.report:
                logger.warning('The first calibration report is missing!')
            else:
                self.report['packet_ids'].append(packet_id)

        if packet['seg_flag'] in [2, 3]:
            if not self.report:
                logger.warning(
                        'A calibration run (last packet ID:{}) is'
                        ' not recorded due to missing the first packet!'.format(packet_id)
                )
                return

            param_dict = packet.children_as_dict()
            self.report['duration'] = param_dict['NIX00122'][0].raw
            scet = param_dict['NIX00445'][0].raw
            self.report['SCET'] = scet
            self.report['start_unix_time'] = stix_datetime.scet2unix(scet)
            self.report['auxiliary'] = packet['parameters'][0:14]
            #Don't copy repeaters 
            self.report['sbspec_counts_sum']=np.sum(self.sbspec_counts,axis=1).tolist()
            
            self.report['counts'] = self.sbspec_counts.tolist()
            self.report['spectra'] = self.spectra;
            self.report['packet_index'] = self.packet_index.tolist()
            #spectra
            self.db_collection.insert_one(self.report)

            self.current_calibration_run_id += 1
            self.report = None
            self.spectra=[]
            self.counts= np.zeros((8,12*32), dtype=np.int32)
            self.packet_index= np.zeros((8,12*32), dtype=np.int32)


class StixQLBackgroundAnalyzer(object):
    """
    capture quicklook reports and dump information into database

    """

    def __init__(self, collection):
        self.db_collection = collection
        self.report = None
        try:
            self.current_report_id = self.db_collection.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_report_id = 0

    def capture(self, run_id, packet_id, pkt):
        if not self.db_collection:
            return
        packet = sdt.Packet(pkt)
        if packet.SPID not in [54119]:
            return

        start_coarse_time = packet[1].raw
        start_fine_time = packet[2].raw
        integrations = packet[3].raw
        start_unix_time = stix_datetime.scet2unix(start_coarse_time, 
            start_fine_time)

        #self.analyzer.load(packet)

        num_points = packet[15].raw
        duration = num_points * 0.1 * (integrations + 1)
        report = {
            '_id': self.current_report_id,
            'run_id': run_id,
            'packet_id': packet_id,
            'start_unix_time': start_unix_time,
            'packet_header_time': packet['unix_time'],
            'integrations': integrations,
            'duration': duration,
            'stop_unix_time': start_unix_time + duration
        }
        self.db_collection.insert_one(report)
        self.current_report_id += 1


class StixQLLightCurveAnalyzer(object):
    """
    capture quicklook reports and fill packet information into a MongoDB collection

    """

    def __init__(self, collection):
        self.db_collection = collection
        self.report = None
        try:
            self.current_report_id = self.db_collection.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_report_id = 0

    def capture(self, run_id, packet_id, pkt):
        if not self.db_collection:
            return
        packet = sdt.Packet(pkt)
        if packet.SPID not in [54118]:
            return

        start_coarse_time = packet[1].raw
        start_fine_time = packet[2].raw
        integrations = packet[3].raw
        detector_mask = packet[4].raw
        pixel_mask = packet[6].raw
        start_unix_time = stix_datetime.scet2unix(start_coarse_time , start_fine_time)

        #self.analyzer.load(packet)

        points = packet.get('NIX00270/NIX00271')[0][0]
        duration = points * 0.1 * (integrations + 1)
        report = {
            '_id': self.current_report_id,
            'run_id': run_id,
            'packet_id': packet_id,
            'start_unix_time': start_unix_time,
            'packet_header_time': packet['unix_time'],
            'integrations': integrations,
            'duration': duration,
            'stop_unix_time': start_unix_time + duration,
            'detector_mask': detector_mask,
            'pixel_mask': pixel_mask
        }
        self.db_collection.insert_one(report)
        self.current_report_id += 1


class StixScienceReportAnalyzer(object):
    def __init__(self, db):
        self.calibration_analyzer = StixCalibrationReportAnalyzer(
            db['calibration_runs'])
        self.qllc_analyzer = StixQLLightCurveAnalyzer(db['ql_lightcurves'])
        self.qlbkg_analyzer = StixQLBackgroundAnalyzer(db['ql_background'])
        #self.qllc_analyzer = StixQLSpecificSpectrumAnalyzer(db['ql_spectra'])

    def start(self, run_id, packet_id, packet):
        self.calibration_analyzer.capture(run_id, packet_id, packet)
        self.qllc_analyzer.capture(run_id, packet_id, packet)
        self.qlbkg_analyzer.capture(run_id, packet_id, packet)
