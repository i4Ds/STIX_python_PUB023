
import sys
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
from stix.fits.products.science import XrayL0
from stix.utils.logger import get_logger



from core import mongodb_api 
db= mongodb_api.MongoDB()
logger = get_logger(__name__)

FITS_FILE_DIRECTORY='/data/fits/'

SPID_MAP = {
    # Bulk Science
    54110: 'xray_l0_auto',
    54111: 'xray_l1_auto',
    54112: 'xray_l2_auto',
    54113: 'xray_l3_auto',
    54142: 'spectrogram_auto',
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
        ('DATE', datetime.utcnow().isoformat(timespec='milliseconds'),
         'FITS file creation date in UTC'),
        ('OBT_BEG', f'{scet_coarse}:{scet_fine}'),
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


def generate_filename(level, product_name, observation_date, unique_id):
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
    return f'solo_{level}_stix-{product_name.replace("_", "-")}_{dateobs}_{unique_id:05d}.fits'


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
    for pkt in packet_list:
        if pkt['header']['TMTC'] != 'TM':
            continue
        if 'SPID' in pkt['header']:
            if pkt['header']['SPID'] not in filtered_packets:
                filtered_packets[ pkt['header']['SPID']]=[]
            filtered_packets[pkt['header']['SPID']].append(pkt)



    complete = defaultdict(list)
    incomplete = defaultdict(list)

    for key, packets in filtered_packets.items():

        # Data fits in a stand-alone packet
        stand_alone_indices = [i for i in range(len(packets))
                               if packets[i]['header']['seg_flag'] == 3 ] #standalone
        for stand_alone_index in stand_alone_indices:
            complete[key].append([packets[stand_alone_index]])

        # Data is spread across a number of packets
        start_indices = [i for i in range(len(packets))
                         if packets[i]['header']['seg_flag'] == 1] # first
        end_indices = [i for i in range(len(packets))
                       if packets[i]['header']['seg_flag'] == 2] #last_packet

        if len(start_indices) == len(end_indices):
            for start_index, end_index in zip(start_indices, end_indices):
                complete[key].append(packets[start_index:end_index + 1])
        else:
            Warning(f'Incompatible number of first {len(start_indices)} and last {len(end_indices)}'
                    f' packet segmentation values possibly incomplete data')
            for start_index, end_index in zip(start_indices[:-1], start_indices[1:]):
                incomplete[key].append(packets[start_index:end_index])

    return complete, incomplete


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
    if spid in [54101, 54102]:
        packet_lists = [list(chain.from_iterable(packet_lists))]

    for packets in packet_lists:
        parsed_packets = sdt.Packet.merge(packets, spid)
        try:
            if product == 'hk_mini':
                prod = MiniReport(parsed_packets)
                prod_type = 'housekeeping'

            elif product == 'hk_maxi':
                prod = MaxiReport(parsed_packets)
                prod_type = 'housekeeping'
            elif product == 'ql_light_curves':
                prod = LightCurve(parsed_packets)
                prod_type = 'quicklook'
            elif product == 'ql_background':
                prod = Background(parsed_packets)
                prod_type = 'quicklook'
            elif product == 'ql_spectrogram':
                prod = Spectra(parsed_packets)
                prod_type = 'quicklook'
            elif product == 'ql_variance':
                prod = Variance(parsed_packets)
                prod_type = 'quicklook'
            elif product == 'flareflag_location':
                prod = FlareFlagAndLocation(parsed_packets)
                prod_type = 'quicklook'
            elif product == 'calibration_spectrum':
                prod = CalibrationSpectra(parsed_packets)
                prod_type = 'quicklook'
            elif product == 'tm_status_and_flare_list':
                prod = TMManagementAndFlareList(parsed_packets)
                prod_type = 'quicklook'
            elif product == 'xray_l0_user':
                prod = XrayL0(parsed_packets)
                prod_type = 'science'
            else:
                logger.info('Not implemented %s, SPID %d.', product, spid)
                #continue
                return


            unique_id=db.get_next_fits_id()

            filename = generate_filename('L1', product, prod.obs_beg, unique_id)
            primary_header = generate_primary_header(filename, prod.scet_coarse, prod.scet_fine,
                                                     prod.obs_beg, prod.obs_avg, prod.obs_end)
            complete=report_status=='complete'
            
            hdul = prod.to_hdul()

            hdul[0].header.update(primary_header)
            hdul[0].header.update({'HISTORY': 'Processed by STIX LLDP VM'})

            full_path=os.path.join(basepath, filename)
            hdul.writeto(full_path, checksum=True, overwrite=overwrite)

            record={
                    '_id':unique_id,
                    'file_id':file_id, 
                    'type':product, 
                    'data_start_unix':prod.obs_beg.timestamp(),
                    'data_end_unix':prod.obs_end.timestamp(),
                    'scet_coarse':prod.scet_coarse,
                    'scet_fine':prod.scet_fine,
                    'complete':complete,
                    'filename':filename,
                    'creation_time':datetime.utcnow(),
                    'path':basepath,
                    }
            db.write_fits_index_info(record)
            logger.info('created  fits file: %s ', full_path)

        except Exception as e:
            logger.error('error', exc_info=True)


def process_products(file_id, products, report_status, basepath, overwrite=False):
    for spid, packets in products.items():
        logger.debug('Processing %s products SPID %d',  report_status, spid)
        if spid not in SPID_MAP:
            logger.debug('Not supported spid : %d',   spid)
            continue
        product = SPID_MAP[spid]
        if spid:
            try:
                process_packets(file_id, data, spid, product, report_status, basepath, overwrite=overwrite)
            except Exception as e:
                logger.error('error', exc_info=True)


def create_fits(file_id, output_path):
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

