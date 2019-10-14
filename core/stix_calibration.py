from core import stix_packet_analyzer as sta
from core import stix_datetime
class StixCalibration(object):
    """
      Checking if a packet is a calibration packet.
    """

    def __init__(self,  collection):
        self.collection_calibration=collection
        self.report=None
        self.total_counts=[]

        self.analyzer = sta.analyzer()

        try:
            self.current_calibration_run_id = self.collection_calibration.find(
            ).sort('_id', -1).limit(1)[0]['_id'] + 1
        except IndexError:
            self.current_calibration_run_id = 0




    def capture(self, run_id, packet_id, packet):
        if not self.collection_calibration:
            return 
        header=packet['header']
        if header['SPID'] != 54124:
            return

        
        self.analyzer.load(packet)
        detector_ids = self.analyzer.to_array('NIX00159/NIXD0155')[0]
        pixels_ids = self.analyzer.to_array('NIX00159/NIXD0156')[0]
        spectra = self.analyzer.to_array('NIX00159/NIX00146/*')[0]
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
        elif header['seg_flag'] == 0 :
            #continuation packet
            if not self.report:
                STIX_LOGGER.warn('The first calibration report is missing!')
            else:
                self.report['packet_ids'].append(packet_id)

        if header['seg_flag'] in [2,3]:
            #last or single packet
            # extract the information from
            param_dict=self.analyzer.to_dict()
            self.report['duration']=param_dict['NIX00122'][0]
            scet=param_dict['NIX00445'][0]
            self.report['SCET']=scet
            self.report['start_unix_time']=stix_datetime.convert_SCET_to_unixtimestamp(scet)
            self.report['auxiliary']=param_dict
            #Fill calibration configuration into the report
            self.report['total_counts']=self.total_counts
            
            self.collection_calibration.insert_one(self.report)
            self.current_calibration_run_id += 1
            self.report=None
            self.total_counts=[]

            

