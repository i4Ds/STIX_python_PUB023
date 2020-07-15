import logging
from collections import defaultdict
from datetime import datetime
from itertools import chain
from pathlib import Path
from time import perf_counter

from stix_parser.core import stix_datatypes as sdt
from stix_parser.core.stix_parser import StixTCTMParser
from stix_parser.datetime import datetime_to_scet
from stix_parser.products.housekeeping import MiniReport, MaxiReport
from stix_parser.products.quicklook import LightCurve, Background, Spectra, Variance, \
    FlareFlagAndLocation, CalibrationSpectra, TMManagementAndFlareList
from stix_parser.products.science import XrayL0
from stix_parser.utils.logger import get_logger


logger = get_logger(__name__)


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
        ('DATE', datetime.now().isoformat(timespec='milliseconds'),
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


def generate_filename(level, product_name, observation_date, version):
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
    return f'solo_{level}_stix-{product_name.replace("_", "-")}_{dateobs}_V{version:02d}.fits'


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
    if not spids:
        spids = set([x['header']['SPID'] for x in packet_list if x['header']['SPID'] != ''])

    for value in spids:
        filtered_packets[value] = list(filter(
            lambda x: x['header']['SPID'] == value and x['header']['TMTC'] == 'TM', packet_list))

    complete = defaultdict(list)
    incomplete = defaultdict(list)

    for key, packets in filtered_packets.items():

        # Data fits in a stand-alone packet
        stand_alone_indices = [i for i in range(len(packets))
                               if packets[i]['header']['segmentation'] == 'stand-alone packet']
        for stand_alone_index in stand_alone_indices:
            complete[key].append([packets[stand_alone_index]])

        # Data is spread across a number of packets
        start_indices = [i for i in range(len(packets))
                         if packets[i]['header']['segmentation'] == 'first packet']
        end_indices = [i for i in range(len(packets))
                       if packets[i]['header']['segmentation'] == 'last packet']

        if len(start_indices) == len(end_indices):
            for start_index, end_index in zip(start_indices, end_indices):
                complete[key].append(packets[start_index:end_index + 1])
        else:
            Warning(f'Incompatible number of first {len(start_indices)} and last {len(end_indices)}'
                    f' packet segmentation values possibly incomplete data')
            for start_index, end_index in zip(start_indices[:-1], start_indices[1:]):
                incomplete[key].append(packets[start_index:end_index])

    return complete, incomplete


def process_packets(packet_lists, spid, product, basepath=None, overwrite=False):
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
                type = 'housekeeping'
            elif product == 'hk_maxi':
                prod = MaxiReport(parsed_packets)
                type = 'housekeeping'
            elif product == 'ql_light_curves':
                prod = LightCurve(parsed_packets)
                type = 'quicklook'
            elif product == 'ql_background':
                prod = Background(parsed_packets)
                type = 'quicklook'
            elif product == 'ql_spectrogram':
                prod = Spectra(parsed_packets)
                type = 'quicklook'
            elif product == 'ql_variance':
                prod = Variance(parsed_packets)
                type = 'quicklook'
            elif product == 'flareflag_location':
                prod = FlareFlagAndLocation(parsed_packets)
                type = 'quicklook'
            elif product == 'calibration_spectrum':
                prod = CalibrationSpectra(parsed_packets)
                type = 'quicklook'
            elif product == 'tm_status_and_flare_list':
                prod = TMManagementAndFlareList(parsed_packets)
                type = 'quicklook'
            elif product == 'xray_l0_user':
                prod = XrayL0(parsed_packets)
                type = 'science'
            else:
                logger.info('Not implemented %s, SPID %d.', product, spid)
                continue

            filename = generate_filename('L1', product, prod.obs_beg, 1)
            primary_header = generate_primary_header(filename, prod.scet_coarse, prod.scet_fine,
                                                     prod.obs_beg, prod.obs_avg, prod.obs_end)
            hdul = prod.to_hdul()

            hdul[0].header.update(primary_header)
            hdul[0].header.update({'HISTORY': 'Processed by STIX LLDP VM'})

            path = basepath.joinpath(type)
            path.mkdir(exist_ok=True)
            hdul.writeto(path / filename, checksum=True, overwrite=overwrite)
        except Exception as e:
            logger.error('error', exc_info=True)


def process_products(products, type, basepath, overwrite=False):
    for spid, data in products.items():
        logger.debug('Processing %s products SPID %d',  type, spid)
        product = SPID_MAP.get(spid, 'unknown')
        if spid:
            path = basepath / type
            path.mkdir(exist_ok=True, parents=True)
            try:
                process_packets(data, spid, product, path, overwrite=overwrite)
            except Exception as e:
                logger.error('error', exc_info=True)


if __name__ == '__main__':

    tstart = perf_counter()

    raw_tmtc = Path('/Users/shane/Projects/STIX/dataview/data/raw')
    tmtc_files = sorted(list(raw_tmtc.glob('*.ascii')))

    for tmtc_file in tmtc_files:

        basepath = Path('/Users/shane/Projects/STIX/dataview/data') / 'L1' / tmtc_file.stem
        if not basepath.exists():
            basepath.mkdir(exist_ok=True, parents=True)
            fh = logging.FileHandler(filename=basepath / 'tm_to_fis.log', mode='w')
            formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s - %(name)s',
                                          datefmt='%Y-%m-%dT%H:%M:%SZ')
            fh.setFormatter(formatter)
            fh.setLevel(logging.DEBUG)
            logging.root.addHandler(fh)

            parser = StixTCTMParser()
            packets = parser.parse_moc_ascii(tmtc_file)

            complete_products, incomplete_products = get_products(packets)  # SPID_MAP.keys())

            logger.info(f'Complete {[(k, len(v)) for k, v in complete_products.items()]}')
            logger.info(f'Incomplete {[(k, len(v)) for k, v in incomplete_products.items()]}')

            process_products(complete_products, 'complete', basepath, overwrite=True)
            process_products(incomplete_products, 'incomplete', basepath, overwrite=True)
        else:
            logger.info('Skipping %s as it already exists', tmtc_file.name)

    tend = perf_counter()
    logger.info('Time taken %f', tend-tstart)