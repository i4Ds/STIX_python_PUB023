import sys
sys.path.append('.')
import os
from collections import defaultdict
from datetime import datetime
from itertools import chain
from pathlib import Path

from stix.core import stix_datatypes as sdt
from stix.core.stix_parser import StixTCTMParser
from stix.core.stix_datetime import datetime_to_scet
from stix.fits.products.housekeeping import MiniReport, MaxiReport
from stix.fits.products.quicklook import LightCurve, Background, Spectra, Variance, \
    FlareFlagAndLocation, CalibrationSpectra, TMManagementAndFlareList
from stix.fits.products.science import XrayL0, Aspect, XrayL1, XrayL2, XrayL3, Spectrogram
#from stix.utils.logger import get_logger


from stix.core import mongo_db, stix_logger
logger = stix_logger.get_logger()


db= mongo_db.MongoDB()
#logger = get_logger(__name__)

FITS_FILE_DIRECTORY='/data/fits/'

SPID_MAP = {
    # Bulk Science
    #54110: 'xray_l0_auto',
    #54111: 'xray_l1_auto',
    #54112: 'xray_l2_auto',
    #54113: 'xray_l3_auto',
    #54142: 'spectrogram_auto',
    54114: 'xray_l0_user',
    54115: 'xray_l1_user',
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
    54123: 'tm_status_and_flare_list',
    54124: 'calibration_spectrum',
    # House keeping
    54101: 'hk_mini',
    54102: 'hk_maxi'
}


def generate_primary_header(filename, scet_coarse, scet_fine, obs_beg, obs_avg, obs_end):
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
        ('OBT_BEG', f'{scet_coarse[0]}:{scet_fine[0]}'),
        ('OBT_END', datetime_to_scet(obs_end)),
        ('TIMESYS', 'UTC', 'System used for time keywords'),
        ('LEVEL', 'L1', 'Processing level of the data'),
        ('ORIGIN', 'STIX Team, FHNW', 'Location where file has been generated'),
        ('CREATOR', 'STIX-SWF', 'FITS creation software'),
        ('VERSION', 1, 'Version of data product'),
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

def generate_filename(level, product_name, product, status, unique_id):
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
    #dateobs = observation_date.strftime("%Y%m%dT%H%M%S")
    #return f'solo_{level}_stix-{product_name.replace("_", "-")}_{dateobs}_{unique_id:05d}.fits'
    if status:
        status = f'_{status}'
    user_req = getattr(product, 'request_id', '')
    if user_req:
        user_req = f'_{user_req}'

    dateobs = product.obs_beg.strftime("%Y%m%dT%H%M%S")
    return f'solo_{level}_stix-{product_name.replace("_", "-")}' \
            f'_{dateobs}_{status}{user_req}_{unique_id:05d}.fits'





def process_packets(file_id, packet_lists, spid, product, report_status,  basepath=FITS_FILE_DIRECTORY, overwrite=False):
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
    basepath : pathlib.Path
        Path
    pacekt_type:
        complete packets or incomplete packets
    overwrite : bool (optional)
        False (default) will raise error if fits file exits, True overwrite existing file
    """

    """
    Process a sequence containing one or more packets for a given product.

    Parameters
    ----------
    packet_lists : list
        List of packet sequences
    spid : int
        SPID
    product : basestring
        Product name
    basepath : pathlib.Path
        Path
    overwrite : bool (optional)
        False (default) will raise error if fits file exits, True overwrite existing file
    """
    # For HK merge all stand alone packets in request
    if spid in [54101, 54102]:
        packet_lists = [list(chain.from_iterable(packet_lists))]

    for packets in packet_lists:
        if not packets:
            continue
        parsed_packets = sdt.Packet.merge(packets, spid, value_type='raw')
        e_parsed_packets = sdt.Packet.merge(packets, spid, value_type='eng')


        try:
            if product == 'hk_mini':
                prod = MiniReport(parsed_packets)
                product_type = 'housekeeping'
            elif product == 'hk_maxi':
                prod = MaxiReport(parsed_packets)
                product_type = 'housekeeping'
            elif product == 'ql_light_curves':
                prod = LightCurve(parsed_packets, e_parsed_packets)
                product_type = 'quicklook'
            elif product == 'ql_background':
                prod = Background(parsed_packets, e_parsed_packets)
                product_type = 'quicklook'
            elif product == 'ql_spectrogram':
                prod = Spectra(parsed_packets, e_parsed_packets)
                product_type = 'quicklook'
            elif product == 'ql_variance':
                prod = Variance(parsed_packets, e_parsed_packets)
                product_type = 'quicklook'
            elif product == 'flareflag_location':
                prod = FlareFlagAndLocation(parsed_packets)
                product_type = 'quicklook'
            elif product == 'calibration_spectrum':
                prod = CalibrationSpectra(parsed_packets, e_parsed_packets)
                product_type = 'quicklook'
            elif product == 'tm_status_and_flare_list':
                prod = TMManagementAndFlareList(parsed_packets)
                product_type = 'quicklook'
            elif product == 'xray_l0_user':
                prod = XrayL0(parsed_packets, e_parsed_packets)
                product_type = 'science'
            elif product == 'xray_l1_user':
                prod = XrayL1(parsed_packets, e_parsed_packets)
                product_type = 'science'
            elif product == 'xray_l2_user':
                prod = XrayL2(parsed_packets, e_parsed_packets)
                product_type = 'science'
            elif product == 'xray_l3_user':
                prod = XrayL3(parsed_packets, e_parsed_packets)
                product_type = 'science'
            elif product == 'spectrogram_user':
                prod = Spectrogram(parsed_packets, e_parsed_packets)
                product_type = 'science'
            elif product == 'aspect':
                prod = Aspect(parsed_packets, e_parsed_packets)
                product_type = 'science'
            else:
                logger.warning(f'Not implemented {product}, SPID {spid}.')
                continue



            Path(basepath).mkdir(parents=True, exist_ok=True)
            unique_id=db.get_next_fits_id()
            filename = generate_filename('L1', product, prod, status=report_status,unique_id=unique_id)
            primary_header = generate_primary_header(filename, prod.scet_coarse, prod.scet_fine,
                                                         prod.obs_beg, prod.obs_avg, prod.obs_end)
            complete=report_status=='complete'
            hdul = prod.to_hdul()
            hdul[0].header.update(primary_header)
            hdul[0].header.update({'HISTORY': 'Processed by STIX LLDP VM'})

            full_path=os.path.join(basepath, filename)
            hdul.writeto(full_path, checksum=True, overwrite=overwrite)
            doc={
                    '_id':unique_id,
                    'packet_id_start': packets[0]['_id'],
                    'packet_id_end': packets[-1]['_id'],
                    'num_packets': len(packets),
                    'file_id':int(file_id), 
                    'product_type':product, 
                    'product_group':product_type,
                    'data_start_unix':prod.obs_beg.timestamp(),
                    'data_end_unix':prod.obs_end.timestamp(),
                    'complete':complete,
                    'filename':filename,
                    'creation_time':datetime.utcnow(),
                    'path':basepath,
                    }
            if hasattr(prod, 'get_request_id'):
                doc['request_id']=prod.get_request_id()



            db.write_fits_index_info(doc)
            logger.info(f'created  fits file:  {full_path}')

        except Exception as e:
            logger.error(str(e))




def create_fits(file_id, output_path):
    raw_info=db.get_raw_info(file_id)
    if not raw_info:
        logger.info(f"File {file_id} doesn't exist")
        return
    spid_packets=raw_info['summary']['spid']
    for spid in spid_packets:
        spid=int(spid)
        logger.info(f'Requesting packets of file {file_id} from MongoDB')
        if spid not in SPID_MAP:
            logger.warning(f'Not supported spid : {spid}')
            continue
        cursor= db.select_packets_by_run(file_id, [spid])
        logger.info(f'Number of packets selected for {spid}: {cursor.count()}')
        product = SPID_MAP[spid]
        report_status='complete'
        if spid in [54101, 54102]:
            packets=[list(cursor)]
            process_packets(file_id, packets, spid, product, report_status, output_path, overwrite=True)
            continue
        packets=[]
        for i, pkt in enumerate(cursor):
            seg_flag = int(pkt['header']['seg_flag'])
            if seg_flag == 3: #'stand-alone packet':
                packets=[pkt]
            elif seg_flag == 1:# 'first packet':
                packets= [pkt]
            elif seg_flag == 0: #'continuation packet':
                if packets:
                    packets.append(pkt)
                else:
                    packets= [pkt]
            elif seg_flag ==2: # 'last packet':
                if packets:
                    packets.append(pkt)
                else:
                    packets= [pkt]
            if seg_flag in [3,2]:
                try:
                    process_packets(file_id, [packets], spid, product, report_status, output_path, overwrite=True)
                except Exception as e:
                    raise
                    logger.error(str(e))



if  __name__ == '__main__':
    if len(sys.argv) == 1:
        print('''STIX L1 FITS writer
                   It reads packets from mongodb and write them into fits
                Usage:
                packets_to_fits   <file_id>
                ''')
    elif len(sys.argv)==2:
        create_fits(sys.argv[1], FITS_FILE_DIRECTORY)
    else:
        create_fits(sys.argv[1], sys.argv[2])

