import os
import logging as log

from collections import defaultdict
from datetime import datetime
from itertools import chain
from time import perf_counter

from core import stix_datatypes as sdt
from spice.stix_datetime import datetime_to_scet
from fits.products.housekeeping import MiniReport, MaxiReport
from fits.products.quicklook import LightCurve, Background, Spectra, Variance, \
    FlareFlagAndLocation, CalibrationSpectra, TMManagementAndFlareList
from fits.products.science import XrayL0
#from stix_parser.utils.logger import get_logger

from core import mongodb_api 

db= mongodb_api.MongoDB()


#logger = get_logger(__name__)
QL_REPORT_SPIDS=[54118, 54119, 54121,54120, 54122]
BSD_SPIDS=[54114, 54115, 54116,54117, 54143, 54125]
QL_TYPE={54118:'lc',54119:'bkg', 54120:'qlspec', 54121:'var', 54122:'flare'}
CALIBRATION_SPID=54124

SPID_MAP = {
    # Bulk Science
    #54110: 'xray_l0_auto',
    #54111: 'xray_l1_auto',
    #54112: 'xray_l2_auto',
    #54113: 'xray_l3_auto',
    #54142: 'spectrogram_auto',  #not supported by the web tool
    54114: 'xray_l0_user',
    54115: 'xray_l1_use',
    54116: 'xray_l2_user',
    54117: 'xray_l3_user',
    54143: 'spectrogram_user',
    54125: 'aspect',
    # Quick look
    54118: 'ql_light_curves',
    54119: 'ql_background',
    54120: 'ql_spectrogram',
    54121: 'ql_variance',
    54122: 'flareflag_location',
    #54123: 'tm_status_and_flare_list',
    54124: 'calibration_spectrum',
    # House keeping
    54101: 'hk_mini',
    54102: 'hk_maxi'
}




def generate_primary_header(filename, scet_coarse, scet_fine, obs_beg, obs_avg, obs_end, uid):
    """
    Generate primary header cards.

    Parameters
    ----------
    filename : str
        Filename
    scet_coarse : int
        SCET coarse time
    scet_fine : int
        SCET fine time
    obs_beg : datetime.datetime
        Begging of observation
    obs_avg : datetime.datetime
       Averagea of observation
    obs_end : datetime.datetime
        End of observation

    Returns
    -------
    tuple
        List of header cards as tuples (name, value, comment)
    """
    headers = (
        # Name, Value, Comment
        ('TELESCOP', 'SOLO/STIX', 'Telescope/Sensor name'),
        ('INSTRUME', 'STIX', 'Instrument name'),
        ('OBSRVTRY', 'Solar Orbiter', 'Satellite name'),
        ('FILENAME', filename, 'FITS filename'),
        ('DATE', datetime.now().isoformat(timespec='milliseconds'),
         'FITS file creation date in UTC'),
        ('OBT_BEG', f'{scet_coarse}:{scet_fine}'),
        ('OBT_END', datetime_to_scet(obs_end)),
        ('TIMESYS', 'UTC', 'System used for time keywords'),
        ('LEVEL', 'L1', 'Processing level of the data'),
        ('ORIGIN', 'STIX Team, FHNW', 'Location where file has been generated'),
        ('CREATOR', 'STIX-SWF', 'FITS creation software'),
        ('VERSION', 1, 'Version of data product'),
        ('UID', uid, 'FITS file unique ID'),
        ('OBS_MODE', 'Nominal '),
        ('VERS_SW', 1, 'Software version'),
        ('DATE_OBS', obs_beg.isoformat(timespec='milliseconds'),
         'Start of acquisition time in UT'),
        ('DATE_BEG', obs_beg.isoformat(timespec='milliseconds')),
        ('DATE_AVG', obs_avg.isoformat(timespec='milliseconds')),
        ('DATE_END', obs_end.isoformat(timespec='milliseconds')),
        ('OBS_TYPE', 'LC'),
        # TODO figure out where this info will come from
        ('SOOP_TYP', 'SOOP'),
        ('OBS_ID', 'obs_id'),
        ('TARGET', 'Sun')
    )
    return headers


def generate_filename(level, product_name, observation_date, version, file_uid):
    """
    Generate fits file name with SOLO conventions.

    Parameters
    ----------
    level : str
        Data level e.g L0, L1, L2
    product_name : str
        Name of the product eg. lightcruve spectra
    observation_date : datetime.datetime
        Date of the observation
    version : int
        Version of this product

    Returns
    -------
    str
        The filename
    """
    dateobs = observation_date.strftime("%Y%m%dT%H%M%S")
    return f'solo_{level}_stix-{product_name.replace("_", "-")}_{dateobs}_{file_uid:05d}_V{version:02d}.fits'

def process_packets(packets, spid, file_uid,  folder='./', overwrite=False):
    """
    Process a sequence containing one or more packets for a given product.

    Parameters
    ----------
    packet_lists : list
        Packets
    spid : int
        SPID
    product : basestring
        Product name
    overwrite : bool (optional)
        False (default) will raise error if fits file exits, True overwrite existing file
    """
    #if spid in [54101, 54102]:
    #    packet_lists = [list(chain.from_iterable(packet_lists))]

    print('merging packets')
    parsed_packets = sdt.Packet.merge(packets, spid, remove_duplicates=True)
    print('creating fits')
    product = SPID_MAP.get(spid, 'unknown')
    #try:
    if True:
        if product == 'hk_mini':
            prod = MiniReport(parsed_packets)
            product_type = 'housekeeping'
        elif product == 'hk_maxi':
            prod = MaxiReport(parsed_packets)
            product_type = 'housekeeping'
        elif product == 'ql_light_curves':
            prod = LightCurve(parsed_packets)
            product_type = 'quicklook'
        elif product == 'ql_background':
            prod = Background(parsed_packets)
            product_type = 'quicklook'
        elif product == 'ql_spectrogram':
            prod = Spectra(parsed_packets)
            product_type = 'quicklook'
        elif product == 'ql_variance':
            prod = Variance(parsed_packets)
            product_type = 'quicklook'
        elif product == 'flareflag_location':
            prod = FlareFlagAndLocation(parsed_packets)
            product_type = 'quicklook'
        elif product == 'calibration_spectrum':
            prod = CalibrationSpectra(parsed_packets)
            product_type = 'quicklook'
        elif product == 'tm_status_and_flare_list':
            prod = TMManagementAndFlareList(parsed_packets)
            product_type = 'quicklook'
        elif product == 'xray_l0_user':
            prod = XrayL0(parsed_packets)
            product_type = 'science'
        else:
            #logger.info('Not implemented %s, SPID %d.', product, spid)
            return {'status':False, 'message': 'Not implemented SPID type:{}'.format(spid)}

        filename = generate_filename('L1', product, prod.obs_beg, 1, file_uid)
        print(filename)
        primary_header = generate_primary_header(filename, prod.scet_coarse, prod.scet_fine,
                                                 prod.obs_beg, prod.obs_avg, prod.obs_end, file_uid)
        hdul = prod.to_hdul()

        hdul[0].header.update(primary_header)
        hdul[0].header.update({'HISTORY': 'Processed by STIX online fits creator'})
        abs_filename=os.path.join(folder, filename)
        hdul.writeto(abs_filename, checksum=True, overwrite=overwrite)
        return {'filename':abs_filename,'status':True}
    #except Exception as e:
    #    return {'status':False, 'message': str(e)}

def get_packets_list_by_time(spid, start_unix_time, duration):
    packets = []
    if spid in [54101, 54102]:
        status, packets=db.select_packets_by_SPIDs(spid, start_unix_time, duration, False, 'header.unix_time') 
    elif spid in QL_REPORT_SPIDS:
        packets=db.get_quicklook_packets(QL_TYPE[spid], start_unix_time, duration, sort_field='header.unix_time')
    elif spid == CALIBRATION_SPID:
        runs=db.select_calibration_runs_by_tw(start_unix_time, duration)
        for run in runs:
            packet_ids= run['packet_ids']
            packets=db.select_packets_by_ids(packet_ids)
            break
            #always return one report
    elif spid  in BSD_SPIDS:
        bsd_list=db.select_data_request_info_by_time(start_unix_time, start_unix_time+duration, False, spid)
        for bsd in bsd_list:
            packets.extend(bsd['packet_ids'])
    return packets
def get_packets_list_by_id(spid, record_id):
    log.debug('Requesting packets from database...')
    packets=[]
    if spid == CALIBRATION_SPID:
        status, packets=db.select_packets_by_calibration(record_id, header_only=False)
    elif spid in BSD_SPIDS: 
        packets=db.get_packets_of_bsd_request(record_id, header_only=False)
    log.debug('Creating fits ..')
    return packets

def create_fits_for_file(file_id):
    packets=db.select_packets_by_run(file_id)




def create_fits_for_request(config):
    #tstart = perf_counter()
    print(config)
    if 'folder' not in config  or 'uid' not in config or 'spid' not in config:
        return {'status':False, 'message': 'Invalid request'}

    packets=[]
    folder=config['folder']
    uid=config['uid']
    spid=config['spid']
    if config['type'] == 'time':
        start_unix_time=config['conditions']['start_unix_time']
        duration=config['conditions']['duration']
        packets=get_packets_list_by_time(spid, start_unix_time, duration)
    elif config['type'] == 'id':
        record_id=config['conditions']['id']
        packets=get_packets_list_by_id(spid, record_id)
        uid=record_id
    if packets:
        return process_packets(packets, spid, uid,  folder, overwrite=True)
    else:
        return {'status':False, 'message': 'No packet found'}

if __name__=='__main__':
    config={
            'folder':'/data/',
            'uid': 123456,
            'type':'id',
            'spid':54124,
            'conditions':{'id':992}
            }
    result=create_fits(config)
    print(result)



