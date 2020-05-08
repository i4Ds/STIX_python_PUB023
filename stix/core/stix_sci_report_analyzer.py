import sys
import numpy as np
from . import stix_datatypes as sdt
from . import stix_datetime
from . import stix_logger
logger = stix_logger.get_logger()
DATA_REQUEST_REPORT_SPIDS=[54114, 54115, 54116,54117, 54143, 54125]
DATA_REQUEST_REPORT_NAME={54114:'L0', 54115:'L1',54116:'L2', 54117:'L3', 54143:'L4', 54125:'ASP'}

class StixScienceReportAnalyzer(object):
    def __init__(self, db):
        self.calibration_analyzer = StixCalibrationReportAnalyzer(
            db['calibration_runs'])
        self.qllc_analyzer = StixQLLightCurveAnalyzer(db['ql_lightcurves'])
        self.qlbkg_analyzer = StixQLBackgroundAnalyzer(db['ql_background'])
        self.user_request_analyzer=StixUserDataRequestReportAnalyzer(db['data_requests'])
        #self.bsdl0_analyzer = StixBSDL0Analyzer(db['bsd_l0'])
        #self.qllc_analyzer = StixQLSpecificSpectrumAnalyzer(db['ql_spectra'])

    def start(self, run_id, packet_id, packet):
        self.calibration_analyzer.capture(run_id, packet_id, packet)
        self.qllc_analyzer.capture(run_id, packet_id, packet)
        self.qlbkg_analyzer.capture(run_id, packet_id, packet)
        self.user_request_analyzer.capture(run_id,packet_id,packet)
        #self.bsdl0_analyzer.capture(run_id, packet_id, packet)
    def get_calibration_run_ids(self):
        return self.calibration_analyzer.get_calibration_run_ids()


class StixCalibrationReportAnalyzer(object):
    """
      Capture calibration reports and fill calibration information into MongoDB 

    """
    def __init__(self, collection):
        self.report = None
        self.sbspec_counts = np.zeros((8, 12 * 32), dtype=np.int32)
        self.packet_index = np.zeros((8, 12 * 32), dtype=np.int32)
        self.db_collection = None
        self.current_calibration_run_id = 0
        self.db_collection = collection
        self.calibration_run_ids=[]
        self.spectra = []
        #self.background_spectra=[[] for x in range(0,12*32)]
        try:
            self.current_calibration_run_id = self.db_collection.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_calibration_run_id = 0

    def get_calibration_run_ids(self):
        return self.calibration_run_ids

    def capture(self, run_id, packet_id, pkt):
        if not self.db_collection:
            return
        packet = sdt.Packet(pkt)
        if packet.SPID != 54124:
            return

        detector_mask = packet.get_one('NIX00407')[1] #raw value
        pixel_mask = packet.get_one('NIXD0407')[1] #raw value

        detector_ids = packet.get('NIX00159/NIXD0155')[0]
        pixel_ids = packet.get('NIX00159/NIXD0156')[0]
        subspc_ids = packet.get('NIX00159/NIXD0157')[0]
        sbspec_spectra = packet.get('NIX00159/NIX00146/*.eng')[0]

        start_index=packet.index('NIXD0129')

        sbspec_formats = [(packet[i * 4 + start_index].raw, packet[i * 4 + start_index+1].raw,
                           packet[i * 4 + start_index+2].raw) for i in range(0, 8)]

        for i in range(0, len(detector_ids)):
            sbspec_id = subspc_ids[i]
            detector_id = detector_ids[i]
            pixel_id = pixel_ids[i]
            sbspec_spectrum = sbspec_spectra[i]
            try:
                self.spectra.append(
                    (detector_id, pixel_id, sbspec_id,
                     sbspec_formats[sbspec_id][2],
                     int(sbspec_formats[sbspec_id][1]) + 1, sbspec_spectrum))
            except Exception as e:
                logger.warning(
                    'Error occurred when formatting spectra: {}'.format(
                        str(e)))

            num_counts = 0
            try:
                num_counts = sum(sbspec_spectrum)
            except TypeError:
                logger.warning(
                    "Counts not decompressed. File id: {}, Packet id:{}".
                    format(run_id, packet_id))
            self.sbspec_counts[sbspec_id][detector_id * 12 +
                                          pixel_id] = num_counts
            self.packet_index[sbspec_id][detector_id * 12 +
                                         pixel_id] = packet_id

        if packet['seg_flag'] in [1, 3]:
            sbspec_mask = packet[13].raw
            sbspec_status = [False for i in range(0, 8)]
            for i in range(0, 8):
                if sbspec_mask & (1 << i) != 0:
                    sbspec_status[i] = True

            self.report = {
                'run_id': run_id,
                'packet_ids': [packet_id],
                'sbspec_formats': sbspec_formats,
                'sbspec_status': sbspec_status,
                'sbspec_mask': sbspec_mask,
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
                    ' not recorded due to missing the first packet!'.format(
                        packet_id))
                return

            param_dict = packet.children_as_dict()
            self.report['duration'] = param_dict['NIX00122'][0].raw
            scet = param_dict['NIX00445'][0].raw
            self.report['SCET'] = scet
            self.report['start_unix_time'] = stix_datetime.scet2unix(scet)
            spectra_index = packet.index('NIX00159')
            self.report['auxiliary'] = packet['parameters'][0:spectra_index]
            #Don't copy repeaters
            self.report['sbspec_counts_sum'] = np.sum(self.sbspec_counts,
                                                      axis=1).tolist()
            self.report['counts'] = self.sbspec_counts.tolist()
            self.report['spectra'] = self.spectra
            self.report['packet_index'] = self.packet_index.tolist()
            #packet id, used by web applications
            #spectra
            self.db_collection.insert_one(self.report)
            self.calibration_run_ids.append(self.current_calibration_run_id)

            #reset report
            self.current_calibration_run_id += 1
            self.report = None
            self.spectra = []
            self.counts = np.zeros((8, 12 * 32), dtype=np.int32)
            self.packet_index = np.zeros((8, 12 * 32), dtype=np.int32)


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
        start_unix_time = stix_datetime.scet2unix(start_coarse_time,
                                                  start_fine_time)

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

class  StixUserDataRequestReportAnalyzer(object):
    def __init__(self,db):
        self.db=db
        self.last_unique_id=-1
        self.last_request_spid=-1
        self.packet_ids=[]
        self.start_time=0
        self.stop_time=0
        try:
            self.current_id= self.db.find().sort('_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_id= 0

        
    def capture(self, run_id, packet_id, pkt):
        if not self.db:
            return
        packet = sdt.Packet(pkt)
        if packet.SPID not in DATA_REQUEST_REPORT_SPIDS:
            return
        if packet.SPID == 54125: 
            #aspect data
            self.process_aspect(run_id,packet_id,packet)
        else:
            self.process_bulk_science(run_id,packet_id,packet)
    def process_bulk_science(self, run_id,packet_id,packet):
        try:
            unique_id=packet[3].raw
            start= packet[12].raw
        except Exception as e:
            logger.warning(str(e))
            return
        if packet['seg_flag'] in [1, 3]:
            self.packet_ids=[]
        self.packet_ids.append(packet_id)
        
        if self.last_unique_id!=unique_id or self.last_request_spid != packet['SPID']  or packet['seg_flag'] in [2, 3]:
            #the last or standalone
            if self.db:
                report={
                        'start_unix_time':stix_datetime.scet2unix(start),
                        'unique_id':unique_id,
                        'packet_ids':self.packet_ids,
                        'run_id':run_id,
                        'SPID': packet['SPID'],
                        'name': DATA_REQUEST_REPORT_NAME[packet['SPID']],
                        'header_unix_time': packet['unix_time'],
                        '_id':self.current_id,
                        }
                self.db.insert_one(report)
                self.current_id+=1
                self.packet_ids=[]

        self.last_unique_id=unique_id
        self.last_request_spid=packet['SPID']
            


        


    def process_aspect(self,run_id,packet_id,packet):
        start_obt=packet[1].raw+packet[2].raw/65536
        summing=packet[3].raw
        samples=packet[4].raw
        duration=samples/64.*summing

        if packet['seg_flag'] in [1,3]:
            self.packet_ids=[]
            self.start_obt_time=start_obt
        self.packet_ids.append(packet_id)

        end_time=start_obt+duration



        if packet['seg_flag'] in [2, 3]:
            #the last or standalone
            if self.db:

                report={
                        'start_unix_time':stix_datetime.scet2unix(self.start_obt_time),
                        'end_unix_time':stix_datetime.scet2unix(end_time),
                        'packet_ids':self.packet_ids,
                        'SPID':packet['SPID'],
                        'run_id':run_id,
                        'name': DATA_REQUEST_REPORT_NAME[packet['SPID']],
                        'header_unix_time': packet['unix_time'],
                        '_id':self.current_id,
                        }
                self.db.insert_one(report)
                self.current_id+=1




        

        




'''
class StixBSDL0Analyzer(object):
    def __init__(self, db):
        self.db = db
        self.current_report_id = -1
        try:
            self.current_report_id = self.db.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_report_id = 0

        self.reset()

    def reset(self):
        self.time = []
        self.rcr = []
        self.dt = []
        self.pixel_mask = []
        self.detector_mask = []
        self.triggers = []
        self.hits = []
        self.hits_time_int = np.zeros((33, 12, 32))  #total hits
        self.hits_time_ene_int = np.zeros(
            (33, 12))  # energy integrated total hits
        #self.T0=[]
        self.eacc_SKM = ()
        self.trig_SKM = ()
        self.packet_ids = []
        self.run_id = -1
        self.request_id = -1
        self.packet_unix = 0

    def insert_report(self):
        report = {
            '_id': self.current_report_id,
            'run_id': self.run_id,
            'packet_ids': self.packet_ids,
            'request_id': self.request_id,
            'packet_unix': self.packet_unix,
            'time': self.time,
            'dt': self.dt,
            'rcr': self.rcr,
            'pixel_mask': self.pixel_mask,
            'detector_mask': self.detector_mask,
            'triggers': self.triggers,
            'hits': self.hits,  #data
            'hits_time_int': self.hits_time_int.tolist(),
            'hits_time_ene_int': self.hits_time_ene_int.tolist(),
            'eacc_SKM': self.eacc_SKM,
            'bsd_level': 0,
            'trig_SKM': self.trig_SKM,
        }
        if (self.db):
            self.db.insert_one(report)
            self.current_report_id+=1

    def capture(self, run_id, packet_id, pkt):
        packet = sdt.Packet(pkt)
        if not packet.isa(54114):
            return

        if packet['seg_flag'] in [1, 3]:
            self.reset()

        self.request_id = packet[3].raw
        self.run_id = run_id
        self.packet_ids.append(packet_id)
        self.packet_unix = packet['unix_time']
        T0 = packet[12].raw
        num_structures = packet[13].raw
        self.eacc_SKM = (packet[5].raw, packet[6].raw, packet[7].raw)
        self.trig_SKM = (packet[9].raw, packet[10].raw, packet[11].raw)

        trig_idx = 1
        #uncompressed counts
        if sum(self.trig_SKM) > 0:
            trig_idx = 2

        counts_idx = 1  #raw value
        if sum(self.eacc_SKM) > 0:
            counts_idx = 2
        children = packet[13].children

        for i in range(0, num_structures):
            offset = i * 23
            self.time.append(children[offset][1] * 0.1 + T0)
            self.rcr.append(children[offset + 1][1])
            self.dt.append(children[offset + 2][1] * 0.1)
            self.pixel_mask.append(children[offset + 4][1])
            self.detector_mask.append(children[offset + 5][1])
            spectrum = np.zeros((32, 12, 32))
            self.triggers.append(
                [children[k + 6][trig_idx] for k in range(0, 16)])
            #id 6-22, 16 trigger accumulators
            num_samples = children[22][1]
            samples = children[22][3]
            for j in range(0, num_samples):
                k = j * 5
                pixel = samples[k+ 1][1]
                detector = samples[k+ 2][1]
                energy_bin = samples[k+ 3][1]
                num_bits = samples[k+ 4][1]
                continous_counts = samples[k+ 4][3]
                counts = 1
                if num_bits == 1:
                    counts = continous_counts[0][counts_idx]
                if num_bits == 2:
                    counts = continous_counts[0][counts_idx] << 8
                    counts += continous_counts[1][counts_idx]
                spectrum[detector][pixel][energy_bin] = counts
                self.hits_time_int[detector][pixel][energy_bin] += counts
                self.hits_time_ene_int[detector][pixel] += counts
            self.hits.append(spectrum.tolist())

        if packet['seg_flag'] in [2, 3]:
            #the last or standalone
            self.insert_report()

class StixBSDL1Analyzer(object):
    def __init__(self, db):
        self.db = db
        self.current_report_id = -1
        try:
            self.current_report_id = self.db.find().sort(
                '_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_report_id = 0

        self.reset()

    def reset(self):
        self.time = []
        self.rcr = []
        self.dt = []
        self.pixel_mask = []
        self.detector_mask = []
        self.triggers = []
        self.hits = []
        self.hits_time_int = np.zeros((33, 12, 32))  #total hits
        self.hits_time_ene_int = np.zeros(
            (33, 12))  # energy integrated total hits
        #self.T0=[]
        self.eacc_SKM = ()
        self.trig_SKM = ()
        self.packet_ids = []
        self.run_id = -1
        self.request_id = -1
        self.packet_unix = 0
        self.groups=[]

    def insert_report(self):
        report = {
            '_id': self.current_report_id,
            'run_id': self.run_id,
            'packet_ids': self.packet_ids,
            'request_id': self.request_id,
            'packet_unix': self.packet_unix,
            #'time': self.time,
            #'rcr': self.rcr,
            #'pixel_mask': self.pixel_mask,
            #'detector_mask': self.detector_mask,
            #'triggers': self.triggers,
            'eacc_SKM': self.eacc_SKM,
            'bsd_level': 1,
            'trig_SKM': self.trig_SKM,
            'groups':self.groups
        }
        if (self.db):
            self.db.insert_one(report)

    def capture(self, run_id, packet_id, pkt):
        packet = sdt.Packet(pkt)
        if not packet.isa(54115):
            return

        if packet['seg_flag'] in [1, 3]:
            self.reset()

        self.request_id = packet[3].raw
        self.run_id = run_id
        self.packet_ids.append(packet_id)
        self.packet_unix = packet['unix_time']
        T0 = packet[12].raw
        num_structures = packet[13].raw
        self.eacc_SKM = (packet[5].raw, packet[6].raw, packet[7].raw)
        self.trig_SKM = (packet[9].raw, packet[10].raw, packet[11].raw)

        trig_idx = 1
        #uncompressed counts
        if sum(self.trig_SKM) > 0:
            trig_idx = 2

        counts_idx = 1  #raw value
        if sum(self.eacc_SKM) > 0:
            counts_idx = 2
        children = packet[13].children
        group={}

        for i in range(0, num_structures):
            offset = i * 23
            time=children[offset][1] * 0.1 + T0
            rcr=children[offset + 1][1]
            pixel_mask=[e[1] for e in children[offset + 2].children]
            detector_mask=children[offset + 5][1]
            triggers=[children[k + 6][trig_idx] for k in range(0, 16)]
            #id 6-22, 16 trigger accumulators
            num_samples = children[21][1]
            samples = children[21][3]
            energies=[]
            for j in range(0, num_samples):
                k= j * 3
                E1_low = samples[k+ 1][1]
                E2_high = samples[k+ 2][1]
                pixel_counts = [ e[counts_idx] for e in  samples[k+ 3][3] ]
                #extract raw or eng. value of NIX00259's children
                energies.append([E1_low,E2_high, pixel_counts)
            group={
                'time':time,
                'rcr':rcr,
                'pixel_mask':pixel_mask,
                'detector_mask':detector_mask,
                'triggers':triggers,
                'energies':energies
                }

            self.groups.append(group)

        if packet['seg_flag'] in [2, 3]:
            #the last or standalone
            self.insert_report()
'''
