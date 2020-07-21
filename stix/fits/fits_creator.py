import sys
sys.path.append('.')
import os
import logging
from collections import defaultdict
from datetime import datetime
from itertools import chain
from pathlib import Path
from time import perf_counter

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
           f'_{dateobs}_{status}{user_req}_{unique_id}.fits'


def get_products(packet_list, spids=None):
    """
    Filter and split TM packet by SPID and status complete or incomlete

    Complete product are stand-alone packets, or a packet sequence with with with 1 start,
    n continuation packets and 1 end packet, where n = 0, 1, 2

    Parameters
    ----------
    packet_list : `list`
        List of packets
    spids : `list` (optional)
        List of SPIDs if set only process theses SPID other wise process all

    Returns
    -------
    `tuple`
        Two dictionaries containing the complete and incomplete products
    """
    filtered_packets = {}
    num = 0 
    num_tc=0
    for pkt in packet_list:
        if pkt['header']['TMTC'] != 'TM':
            num_tc += 1
            continue
        if 'SPID' in pkt['header']:
            if pkt['header']['SPID'] not in filtered_packets:
                filtered_packets[ pkt['header']['SPID']]=[]
            filtered_packets[pkt['header']['SPID']].append(pkt)
            num += 1
    logger.info(f'Number of telemetry packets: {num}')
    logger.info(f'Number of telecommands: {num_tc}')



    complete = defaultdict(list)
    incomplete = defaultdict(list)


    for key, packets in filtered_packets.items():
        sequences = extract_sequences(packets[:])
        for seq in sequences:
            if len(seq) == 1 and seq[0]['header']['seg_flag'] == 3: #'stand-alone packet':
                complete[key].append(seq)
            elif seq[0]['header']['seg_flag'] == 1  and seq[-1]['header']['seg_flag'] ==  2: #'last packet'):
                complete[key].append(seq)
            else:
                incomplete[key].append(seq)
                logger.warning(f'Incomplete sequence for {key}')

    return complete, incomplete


def extract_sequences(packets):
    """
    Extract complete and incomplete sequences of packets.

    Packets can be either stand-alone, first ,continuation or last when TM is downloaded maybe
    missing some packet so we we try to extract complete and incomplete sequences.

    Parameters
    ----------
    packets : list
        List of packets

    Returns
    -------
    list
        A list of packet packets
    """
    out = []
    i = 0
    cur_seq = None
    while i < len(packets):
        cur_packet = packets.pop(i)
        cur_flag = cur_packet['header']['segmentation']
        if cur_flag == 'stand-alone packet':
            out.append([cur_packet])
        elif cur_flag == 'first packet':
            cur_seq = [cur_packet]
        if cur_flag == 'continuation packet':
            if cur_seq:
                cur_seq.append(cur_packet)
            else:
                cur_seq = [cur_packet]
        if cur_flag == 'last packet':
            if cur_seq:
                cur_seq.append(cur_packet)
                out.append(cur_seq)
            else:
                out.append([cur_packet])
            cur_seq = None

    if cur_seq:
        out.append(cur_seq)

    return out


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
                    'file_id':file_id, 
                    'type':product, 
                    'data_start_unix':prod.obs_beg.timestamp(),
                    'data_end_unix':prod.obs_end.timestamp(),
                    #'scet_coarse':prod.scet_coarse,
                    #'scet_fine':prod.scet_fine,
                    'complete':complete,
                    'filename':filename,
                    'creation_time':datetime.utcnow(),
                    'path':basepath,
                    }
            try:
                user_req = getattr(product, 'request_id', '')
                doc['request_id']=user_req
            except AttributeError:
                pass
            print(doc)

            db.write_fits_index_info(doc)
            logger.info(f'created  fits file:  {full_path}')

        except Exception as e:
            logger.error('error', exc_info=True)


def process_products(file_id, products, report_status, basepath, overwrite=False):
    for spid, packets in products.items():
        logger.info('Processing {report_status} products SPID {spid}')
        if spid not in SPID_MAP:
            logger.warning('Not supported spid : {spid}')
            continue
        product = SPID_MAP[spid]
        try:
            process_packets(file_id, packets, spid, product, report_status, basepath, overwrite=overwrite)
        except Exception as e:
            logger.error('error', exc_info=True)


def create_fits(file_id, output_path):
    logger.info(f'Requesting packets of file {file_id} from MongoDB')
    packets = db.select_packets_by_run(file_id)
    complete_products, incomplete_products = get_products(packets)  # SPID_MAP.keys())
    process_products(file_id, complete_products, 'complete', output_path, overwrite=True)
    process_products(file_id, incomplete_products, 'incomplete', output_path, overwrite=True)


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

