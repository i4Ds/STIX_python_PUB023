from . import stix_packet_analyzer as sta
from . import stix_datetime
import sys
import pprint
class StixCalibrationReportAnalyzer(object):
    """
      Capture calibration reports and fill calibration information into a MongoDB collection
    

    """

    def __init__(self, collection ):
        self.report=None
        self.total_counts=[]
        self.analyzer = sta.analyzer()
        self.db_collection=None
        self.current_calibration_run_id=0
        self.db_collection=collection
        try:
            self.current_calibration_run_id = self.db_collection.find(
            ).sort('_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_calibration_run_id = 0



    def capture(self, run_id, packet_id, packet):
        if not self.db_collection:
            return 
        header=packet['header']
        if header['SPID'] != 54124:
            return

        
        self.analyzer.load(packet)
        detector_ids = self.analyzer.to_array('NIX00159/NIXD0155')[0]
        pixels_ids = self.analyzer.to_array('NIX00159/NIXD0156')[0]
        spectra = self.analyzer.to_array('NIX00159/NIX00146/*', eng_param='*')[0]

        for ispec, spectrum in enumerate(spectra):
            self.total_counts.append([packet_id, detector_ids[ispec],pixels_ids[ispec],  sum(spectrum)]) 

        if header['seg_flag'] in [1,3]:
            #first or standard alone packet
            self.report={
                    'run_id':run_id,
                    'packet_ids':[packet_id],
                    'header_unix_time':header['unix_time'],
                    '_id':self.current_calibration_run_id 
                    }
        else:
            #continuation packet
            if not self.report:
                STIX_LOGGER.warn('The first calibration report is missing!')
            else:
                self.report['packet_ids'].append(packet_id)

        if header['seg_flag'] in [2,3]:
            #last or single packet
            # extract the information from
            if not self.report:
                STIX_LOGGER.warn('One calibration run is not recorded due to missing the first packet!')
                return

            param_dict=self.analyzer.to_dict()
            self.report['duration']=param_dict['NIX00122'][0]
            scet=param_dict['NIX00445'][0]
            self.report['SCET']=scet
            self.report['start_unix_time']=stix_datetime.convert_SCET_to_unixtimestamp(scet)
            self.report['auxiliary']=param_dict
            #Fill calibration configuration into the report
            self.report['total_counts']=self.total_counts
            
            self.db_collection.insert_one(self.report)
            self.current_calibration_run_id += 1
            self.report=None
            self.total_counts=[]

            

class StixQLLightCurveAnalyzer(object):
    """
    capture quicklook reports and fill packet information into a MongoDB collection

    """

    def __init__(self,  collection):
        self.db_collection=collection
        self.report=None
        self.analyzer = sta.analyzer()
        try:
            self.current_report_id = self.db_collection.find(
            ).sort('_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_report_id= 0

    def capture(self, run_id, packet_id, packet):
        if not self.db_collection:
            return 
        header=packet['header']
        parameters=packet['parameters']
        if header['SPID'] not in [54118]:
            return

        
        start_coarse_time=parameters[1][1][0]
        start_fine_time=parameters[2][1][0]
        integrations=parameters[3][1][0]
        detector_mask=parameters[4][1][0]
        pixel_mask=parameters[5][1][0]
        start_unix_time=stix_datetime.convert_SCET_to_unixtimestamp(start_coarse_time+start_fine_time/65536.)

        self.analyzer.load(packet)
        points=self.analyzer.to_array('NIX00270/NIX00271',once=True)[0][0]
        duration=points*0.1*(integrations+1)
        report={
                '_id': self.current_report_id,
                'run_id':run_id,
                'packet_id':packet_id,
                'start_unix_time': start_unix_time,
                'packet_header_time':header['unix_time'],
                'integrations':integrations,
                'duration':duration,
                'stop_unix_time':start_unix_time+duration,
                'detector_mask':detector_mask,
                'pixel_mask':pixel_mask
                }
        self.db_collection.insert_one(report)
        self.current_report_id+=1


            

class StixScienceReportAnalyzer(object):

    def __init__(self , db):
        self.calibration_analyzer=StixCalibrationReportAnalyzer(db['calibration_runs'])
        self.qllc_analyzer=StixQLLightCurveAnalyzer(db['ql_lightcurves'])

    def start(self, run_id, packet_id,packet):
        self.calibration_analyzer.capture(run_id,packet_id,packet)
        self.qllc_analyzer.capture(run_id,packet_id,packet)
