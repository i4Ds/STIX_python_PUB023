import logging
import time
from collections import defaultdict
from datetime import datetime
from itertools import chain
from pathlib import Path
from time import perf_counter

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

from stix.core import stix_datatypes as sdt
from stix.core.stix_parser import StixTCTMParser
from stix.core.stix_datetime import datetime_to_scet
from stix.fits.products.housekeeping import MiniReport, MaxiReport
from stix.fits.products.quicklook import LightCurve, Background, Spectra, Variance, \
    FlareFlagAndLocation, CalibrationSpectra, TMManagementAndFlareList
from stix.fits.products.science import XrayL0, Aspect, XrayL1, XrayL2, XrayL3, Spectrogram
from stix.utils.logger import get_logger

logger = get_logger(__name__)


SPID_MAP = {
    # Bulk Science
    # 54110: 'xray_l0_auto',
    # 54111: 'xray_l1_auto',
    # 54112: 'xray_l2_auto',
    # 54113: 'xray_l3_auto',
    # 54142: 'spectrogram_auto',
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
    scet_coarse : numpy.ndarray
        SCET coarse time
    scet_fine : numpy.ndarray
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


def generate_filename(level, product_name, product, version, status=''):
    """
    Generate fits file name with SOLO conventions.

    Parameters
    ----------
    level : str
        Data level e.g L0, L1, L2
    product_name : str
        Name of the product eg. lightcruve spectra
    product : stix_parser.product.BaseProduct
        Product
    version : int
        Version of this product

    Returns
    -------
    str
        The filename
    """
    if status:
        status = f'_{status}'

    user_req = getattr(product, 'request_id', '')
    if user_req:
        user_req = f'_{user_req}'

    dateobs = product.obs_beg.strftime("%Y%m%dT%H%M%S")
    return f'solo_{level}_stix-{product_name.replace("_", "-")}' \
           f'_{dateobs}_V{version:02d}{status}{user_req}.fits'


def get_products(packet_list, spids=None):
    """
    Filter and split TM packet by SPID and status complete or incomplete

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
        sequences = extract_sequences(packets[:])
        for seq in sequences:
            if len(seq) == 1 and seq[0]['header']['segmentation'] == 'stand-alone packet':
                complete[key].append(seq)
            elif (seq[0]['header']['segmentation'] == 'first packet'
                  and seq[-1]['header']['segmentation'] == 'last packet'):
                complete[key].append(seq)
            else:
                incomplete[key].append(seq)
                logger.warning('Incomplete sequence for %d', key)

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


def process_packets(packet_lists, spid, product, basepath=None, status='', overwrite=False,
                    use_name=False):
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
        if packets:
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
                    # logger.debug('Not implemented %s, SPID %d.', product, spid)
                    continue

                filename = generate_filename('L1', product, prod, 1, status=status)
                primary_header = generate_primary_header(filename, prod.scet_coarse, prod.scet_fine,
                                                         prod.obs_beg, prod.obs_avg, prod.obs_end)
                hdul = prod.to_hdul()

                hdul[0].header.update(primary_header)
                hdul[0].header.update({'HISTORY': 'Processed by STIX'})

                if use_name:
                    path = basepath
                else:
                    path = basepath.joinpath(*[format(prod.obs_beg.year, '04d'),
                                               format(prod.obs_beg.month, '02d'),
                                               format(prod.obs_beg.day, '02d'), product_type])
                path.mkdir(exist_ok=True, parents=True)
                logger.debug(f'Writing {path / filename}')
                hdul.writeto(path / filename, checksum=True, overwrite=overwrite)
            except Exception as e:
                logger.error('error', exc_info=True)
                # raise e


def process_products(products, basepath, type='', overwrite=False, use_name=False):
    """

    Parameters
    ----------
    products
    type
    basepath
    overwrite

    Returns
    -------

    """
    for spid, data in products.items():
        logger.debug('Processing %s products SPID %d',  type, spid)
        product = SPID_MAP.get(spid, 'unknown')
        if spid:
            path = basepath
            path.mkdir(exist_ok=True, parents=True)
            try:
                process_packets(data, spid, product, path, status=type, overwrite=overwrite,
                                use_name=use_name)
            except Exception as e:
                logger.error('error %d, %s', spid, product, exc_info=True)


def process_tmtcfile(tmtc_file, basedir, use_name=False):
    """
    Process a tmtc file creating the fits files.

    By default the fists files will stored in a 'yyyy/mm/dd' structure relative to the
    base directory based on the start date for the fits file.

    Parameters
    ----------
    tmtc_file : pathlib.Path
        Path to tmtc file

    basedir : str or pathlib.Path
        The base directory to start the output

    use_name : bool
        If set to True use the name of the tmtc file to store the fits files

    """
    basepath = basedir
    if use_name:
        basepath = basedir / tmtc_file.stem

    if not (basepath.exists() and use_name):
        basepath.mkdir(exist_ok=True, parents=True)
        fh = logging.FileHandler(filename=basepath / 'tm_to_fis.log', mode='w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s - %(name)s',
                                      datefmt='%Y-%m-%dT%H:%M:%SZ')
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logging.root.addHandler(fh)

        parser = StixTCTMParser()
        packets = parser.parse_file(tmtc_file)

        # Filter keeping only TM packets
        packets = list(filter(lambda x: x['header']['TMTC'] == 'TM', packets))

        # Packet ordering is not guaranteed so sort by courser time then seq count
        packets.sort(key=lambda x: (x['header']['coarse_time'], x['header']['seq_count']))

        complete_products, incomplete_products = get_products(packets, SPID_MAP.keys())

        logger.info(f'Complete {[(k, len(v)) for k, v in complete_products.items()]}')
        logger.info(f'Incomplete {[(k, len(v)) for k, v in incomplete_products.items()]}')

        process_products(complete_products, basepath, overwrite=True, use_name=use_name)
        process_products(incomplete_products, basepath, 'IC', overwrite=True, use_name=use_name)
    else:
        logger.info('Skipping %s as it already exists', tmtc_file.name)


class TMTCFileHandler(FileSystemEventHandler):
    def __init__(self, func, output_path, use_name):
        self.func = func
        self.output_path = output_path
        self.use_name = use_name

    def on_moved(self, event):
        if isinstance(event, FileMovedEvent):
            if 'PktTmRaw' in event.dest_path and event.dest_path.endswith('.xml'):
                time.sleep(2)
                self.func(Path(event.dest_path), self.output_path, use_name=self.use_name)


if __name__ == '__main__':
    tstart = perf_counter()

    real_observer = Observer()
    op = Path('/home/maloneys/data')
    #op = Path('/tmp/out')

    mp = '/opt/stix/gfts/solmoc/from_moc/'
    #mp = '/tmp/in'
    real_event_handler = TMTCFileHandler(process_tmtcfile, op, use_name=False)
    real_observer.schedule(real_event_handler, mp,
                           recursive=True)
    real_observer.start()
   
    try:
        while True:
             time.sleep(100)
    except KeyboardInterrupt:
        real_observer.stop()
    real_observer.join()

    # Ground unit
    # raw_tmtc = Path('/Users/shane/Projects/STIX/dataview/data/ground_unit')
    # tmtc_files = sorted(list(raw_tmtc.glob('*.ascii')))
    # bd = Path('/Users/shane/Projects/STIX/dataview/data/out/ground_unit')
    # for tmtc_file in tmtc_files:
    #     process_tmtcfile(tmtc_file, bd, use_name=True)


    # Real data
    #raw_tmtc = Path('/Users/shane/Projects/STIX/dataview/data/real')
    #tmtc_files = sorted(list(raw_tmtc.glob('*.xml')))
    #bd = Path('/Users/shane/Projects/STIX/dataview/data/out')
    #for tmtc_file in tmtc_files[57:58]:
    # for tmtc_file in tmtc_files[57:58]:
    #    process_tmtcfile(tmtc_file, bd, use_name=False)

    tend = perf_counter()
    logger.info('Time taken %f', tend-tstart)
