import sys
import pprint
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
        self.total_counts = []
        self.db_collection = None
        self.current_calibration_run_id = 0
        self.db_collection = collection
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

        detector_ids = packet.get('NIX00159/NIXD0155')[0]
        pixels_ids = packet.get('NIX00159/NIXD0156')[0]
        spectra = packet.get('NIX00159/NIX00146/*.eng')[0]

        for ispec, spectrum in enumerate(spectra):

            total_counts=0
            try:
                total_counts=sum(spectrum)
            except TypeError:
                logger.warning("Counts not decompressed. File id: {}, Packet id:{}".format(run_id, 
                    packet_id))
                
            self.total_counts.append([
                packet_id, detector_ids[ispec], pixels_ids[ispec],
                total_counts
            ])

        if packet['seg_flag'] in [1, 3]:
            #first or standard alone packet
            self.report = {
                'run_id': run_id,
                'packet_ids': [packet_id],
                'header_unix_time': packet['unix_time'],
                '_id': self.current_calibration_run_id
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
                    'One calibration run is not recorded due to missing the first packet!'
                )
                return

            param_dict = packet.children_as_dict()
            self.report['duration'] = param_dict['NIX00122'][0].raw
            scet = param_dict['NIX00445'][0].raw
            self.report['SCET'] = scet
            self.report['start_unix_time'] = stix_datetime.scet2unix(scet)
            self.report['auxiliary'] = packet['parameters'][0:14]
            #not to copy repeaters 

            self.report['total_counts'] = self.total_counts

            self.db_collection.insert_one(self.report)
            self.current_calibration_run_id += 1
            self.report = None
            self.total_counts = []


class StixQLBackgroundAnalyzer(object):
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
