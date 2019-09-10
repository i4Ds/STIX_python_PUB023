#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# @title        : stix_parameter.py
# @date         : Feb. 11, 2019
# @description:
#               decompression of compressed parameters

from core import stix_logger
STIX_LOGGER = stix_logger.stix_logger()

SKM_GROUPS = {
    'EACC': ("NIXD0007", "NIXD0008", "NIXD0009"),
    'ETRIG': ("NIXD0010", "NIXD0011", "NIXD0012"),
    'LC': ("NIXD0101", "NIXD0102", "NIXD0103"),
    'TriggerSSID30': ("NIXD0104", "NIXD0105", "NIXD0106"),
    'BKG': ("NIXD0108", "NIXD0109", "NIXD0110"),
    'TRIG': ("NIXD0112", "NIXD0113", "NIXD0114"),
    'SPEC': ("NIXD0115", "NIXD0116", "NIXD0117"),
    'VAR': ("NIXD0118", "NIXD0119", "NIXD0120"),
    'CALI': ("NIXD0126", "NIXD0127", "NIXD0128")
}
PACKETS_WITH_COMPRESSION = set(
    (54112, 54113, 54114, 54115, 54116, 54117, 54118, 54119, 54120, 54121,
     54122, 54123, 54124, 54125, 54142, 54143, 54110, 54111))
SCHEMAS = {
    54120: {
        'SKM_Groups': ['SPEC', 'TRIG'],
        'parameters': {
            'NIX00452': SKM_GROUPS['SPEC'],
            'NIX00453': SKM_GROUPS['SPEC'],
            'NIX00454': SKM_GROUPS['SPEC'],
            'NIX00455': SKM_GROUPS['SPEC'],
            'NIX00456': SKM_GROUPS['SPEC'],
            'NIX00457': SKM_GROUPS['SPEC'],
            'NIX00458': SKM_GROUPS['SPEC'],
            'NIX00459': SKM_GROUPS['SPEC'],
            'NIX00460': SKM_GROUPS['SPEC'],
            'NIX00461': SKM_GROUPS['SPEC'],
            'NIX00462': SKM_GROUPS['SPEC'],
            'NIX00463': SKM_GROUPS['SPEC'],
            'NIX00464': SKM_GROUPS['SPEC'],
            'NIX00465': SKM_GROUPS['SPEC'],
            'NIX00466': SKM_GROUPS['SPEC'],
            'NIX00467': SKM_GROUPS['SPEC'],
            'NIX00468': SKM_GROUPS['SPEC'],
            'NIX00469': SKM_GROUPS['SPEC'],
            'NIX00470': SKM_GROUPS['SPEC'],
            'NIX00471': SKM_GROUPS['SPEC'],
            'NIX00472': SKM_GROUPS['SPEC'],
            'NIX00473': SKM_GROUPS['SPEC'],
            'NIX00474': SKM_GROUPS['SPEC'],
            'NIX00475': SKM_GROUPS['SPEC'],
            'NIX00476': SKM_GROUPS['SPEC'],
            'NIX00477': SKM_GROUPS['SPEC'],
            'NIX00478': SKM_GROUPS['SPEC'],
            'NIX00479': SKM_GROUPS['SPEC'],
            'NIX00480': SKM_GROUPS['SPEC'],
            'NIX00481': SKM_GROUPS['SPEC'],
            'NIX00482': SKM_GROUPS['SPEC'],
            'NIX00483': SKM_GROUPS['SPEC'],
            'NIX00484': SKM_GROUPS['TRIG']
        }
    },
    54124: {
        'SKM_Groups': ['CALI'],
        'parameters': {
            'NIX00158': SKM_GROUPS['CALI']
        }
    },
    54118: {
        'SKM_Groups': ['LC', 'TriggerSSID30'],
        'parameters': {
            'NIX00272': SKM_GROUPS['LC'],
            'NIX00274': SKM_GROUPS['TriggerSSID30']
        }
    },
    54119: {
        'SKM_Groups': ['BKG', 'TRIG'],
        'parameters': {
            'NIX00278': SKM_GROUPS['BKG'],
            'NIX00274': SKM_GROUPS['TRIG']
        }
    },
    54121: {
        'SKM_Groups': ['VAR'],
        'parameters': {
            'NIX00281': SKM_GROUPS['VAR']
        }
    },
    54110: {
        'SKM_Groups': ['EACC', 'ETRIG'],
        'parameters': {
            'NIX00065': SKM_GROUPS['EACC'],
            'NIX00408': SKM_GROUPS['ETRIG'],
            'NIX00409': SKM_GROUPS['ETRIG'],
            'NIX00410': SKM_GROUPS['ETRIG'],
            'NIX00411': SKM_GROUPS['ETRIG'],
            'NIX00412': SKM_GROUPS['ETRIG'],
            'NIX00413': SKM_GROUPS['ETRIG'],
            'NIX00414': SKM_GROUPS['ETRIG'],
            'NIX00415': SKM_GROUPS['ETRIG'],
            'NIX00416': SKM_GROUPS['ETRIG'],
            'NIX00417': SKM_GROUPS['ETRIG'],
            'NIX00418': SKM_GROUPS['ETRIG'],
            'NIX00419': SKM_GROUPS['ETRIG'],
            'NIX00420': SKM_GROUPS['ETRIG'],
            'NIX00421': SKM_GROUPS['ETRIG'],
            'NIX00422': SKM_GROUPS['ETRIG'],
            'NIX00423': SKM_GROUPS['ETRIG']
        }
    },
    54111: {
        'SKM_Groups': ['EACC', 'ETRIG'],
        'parameters': {
            'NIX00260': SKM_GROUPS['EACC'],
            'NIX00242': SKM_GROUPS['ETRIG'],
            'NIX00243': SKM_GROUPS['ETRIG'],
            'NIX00244': SKM_GROUPS['ETRIG'],
            'NIX00245': SKM_GROUPS['ETRIG'],
            'NIX00246': SKM_GROUPS['ETRIG'],
            'NIX00247': SKM_GROUPS['ETRIG'],
            'NIX00248': SKM_GROUPS['ETRIG'],
            'NIX00249': SKM_GROUPS['ETRIG'],
            'NIX00250': SKM_GROUPS['ETRIG'],
            'NIX00251': SKM_GROUPS['ETRIG'],
            'NIX00252': SKM_GROUPS['ETRIG'],
            'NIX00253': SKM_GROUPS['ETRIG'],
            'NIX00254': SKM_GROUPS['ETRIG'],
            'NIX00255': SKM_GROUPS['ETRIG'],
            'NIX00256': SKM_GROUPS['ETRIG'],
            'NIX00257': SKM_GROUPS['ETRIG']
        }
    },
    54112: {
        'SKM_Groups': ['EACC', 'ETRIG'],
        'parameters': {
            'NIX00260': SKM_GROUPS['EACC'],
            'NIX00242': SKM_GROUPS['ETRIG'],
            'NIX00243': SKM_GROUPS['ETRIG'],
            'NIX00244': SKM_GROUPS['ETRIG'],
            'NIX00245': SKM_GROUPS['ETRIG'],
            'NIX00246': SKM_GROUPS['ETRIG'],
            'NIX00247': SKM_GROUPS['ETRIG'],
            'NIX00248': SKM_GROUPS['ETRIG'],
            'NIX00249': SKM_GROUPS['ETRIG'],
            'NIX00250': SKM_GROUPS['ETRIG'],
            'NIX00251': SKM_GROUPS['ETRIG'],
            'NIX00252': SKM_GROUPS['ETRIG'],
            'NIX00253': SKM_GROUPS['ETRIG'],
            'NIX00254': SKM_GROUPS['ETRIG'],
            'NIX00255': SKM_GROUPS['ETRIG'],
            'NIX00256': SKM_GROUPS['ETRIG'],
            'NIX00257': SKM_GROUPS['ETRIG']
        }
    }
    #54113:{},
    #54142:{},

    #54114:{
    #         SKM_GROUPS['EACC']
    #         SKM_GROUPS['ETRIG']
    #         },
    # 54115:{},
    # 54116:{},
    # 54117:{},
    # 54143:{},
}

DESCRIPTIONS = {
    "NIX00158": "Compressed Calibration spectral point",
    "NIX00242": "Compressed Trigger accumulator 0",
    "NIX00243": "Compressed Trigger accumulator 1",
    "NIX00244": "Compressed Trigger accumulator 2",
    "NIX00245": "Compressed Trigger accumulator 3",
    "NIX00246": "Compressed Trigger accumulator 4",
    "NIX00247": "Compressed Trigger accumulator 5",
    "NIX00248": "Compressed Trigger accumulator 6",
    "NIX00249": "Compressed Trigger accumulator 7",
    "NIX00250": "Compressed Trigger accumulator 8",
    "NIX00251": "Compressed Trigger accumulator 9",
    "NIX00252": "Compressed Trigger accumulator 10",
    "NIX00253": "Compressed Trigger accumulator 11",
    "NIX00254": "Compressed Trigger accumulator 12",
    "NIX00255": "Compressed Trigger accumulator 13",
    "NIX00256": "Compressed Trigger accumulator 14",
    "NIX00257": "Compressed Trigger accumulator 15",
    "NIX00260": "Compressed pixels counts",
    "NIX00267": "Compressed combined trigger accumulator",
    "NIX00268": "Compressed summed counts",
    "NIX00272": "Compressed lightcurves",
    "NIX00274": "Compressed triggers",
    "NIX00278": "Compressed background",
    "NIX00281": "Compressed Variance",
    "NIX00452": "Compressed Spectrum (E = 0)",
    "NIX00453": "Compressed Spectrum (E = 1)",
    "NIX00454": "Compressed Spectrum (E = 2)",
    "NIX00455": "Compressed Spectrum (E = 3)",
    "NIX00456": "Compressed Spectrum (E = 4)",
    "NIX00457": "Compressed Spectrum (E = 5)",
    "NIX00458": "Compressed Spectrum (E = 6)",
    "NIX00459": "Compressed Spectrum (E = 7)",
    "NIX00460": "Compressed Spectrum (E = 8)",
    "NIX00461": "Compressed Spectrum (E = 9)",
    "NIX00462": "Compressed Spectrum (E = 10)",
    "NIX00463": "Compressed Spectrum (E = 11)",
    "NIX00464": "Compressed Spectrum (E = 12)",
    "NIX00465": "Compressed Spectrum (E = 13)",
    "NIX00466": "Compressed Spectrum (E = 14)",
    "NIX00467": "Compressed Spectrum (E = 15)",
    "NIX00468": "Compressed Spectrum (E = 16)",
    "NIX00469": "Compressed Spectrum (E = 17)",
    "NIX00470": "Compressed Spectrum (E = 18)",
    "NIX00471": "Compressed Spectrum (E = 19)",
    "NIX00472": "Compressed Spectrum (E = 20)",
    "NIX00473": "Compressed Spectrum (E = 21)",
    "NIX00474": "Compressed Spectrum (E = 22)",
    "NIX00475": "Compressed Spectrum (E = 23)",
    "NIX00476": "Compressed Spectrum (E = 24)",
    "NIX00477": "Compressed Spectrum (E = 25)",
    "NIX00478": "Compressed Spectrum (E = 26)",
    "NIX00479": "Compressed Spectrum (E = 27)",
    "NIX00480": "Compressed Spectrum (E = 28)",
    "NIX00481": "Compressed Spectrum (E = 29)",
    "NIX00482": "Compressed Spectrum (E = 30)",
    "NIX00483": "Compressed Spectrum (E = 31)",
    "NIX00484": "Compressed Trigger Accumulator",
    "NIXD0007": "Compression schema EACC S-parameter",
    "NIXD0008": "Compression schema EACC K-parameter",
    "NIXD0009": "Compression schema EACC M-parameter",
    "NIXD0010": "Compression schema ETRIG S-parameter",
    "NIXD0011": "Compression schema ETRIG K-parameter",
    "NIXD0012": "Compression schema ETRIG M-parameter",
    "NIXD0101": "Compression Schema Lightcurves S-parameter",
    "NIXD0102": "Compression schema Lightcurves K-parameter",
    "NIXD0103": "Compression schema Lightcurves M-parameter",
    "NIXD0104": "Compression Schema Trigger accum S-parameter SSID 30",
    "NIXD0105": "Compression schema Trigger accum K-parameter SSID 30",
    "NIXD0106": "Compression schema Trigger accum M-parameter SSID 30",
    "NIXD0108": "Compression Schema Background S-parameter",
    "NIXD0109": "Compression schema Background K-parameter",
    "NIXD0110": "Compression schema Background M-parameter",
    "NIXD0112": "Compression Schema Trigger accum S-parameter",
    "NIXD0113": "Compression schema Trigger accum K-parameter",
    "NIXD0114": "Compression schema Trigger accum M-parameter",
    "NIXD0115": "Compression Schema Spectrum accum S-parameter",
    "NIXD0116": "Compression schema Spectrum accum K-parameter",
    "NIXD0117": "Compression schema Spectrum accum M-parameter",
    "NIXD0118": "Compression Schema Variance S-parameter",
    "NIXD0119": "Compression schema Variance K-parameter",
    "NIXD0120": "Compression schema Variance M-parameter",
    "NIXD0126": "Compression Schema Calib accum S-parameter",
    "NIXD0127": "Compression schema Calib accum K-parameter",
    "NIXD0128": "Compression schema Calib accum M-parameter",
    "NIXG0160": "Compression Schema Calib accum"
}


def decompress(x, S, K, M):
    if S + K + M > 8 or S not in (0, 1) or K > 7 or M > 7:
        STIX_LOGGER.warn('Invalid SKM values: {}{}{}'.format(S, K, M))
        return None
    sign = 1
    if S == 1:
        MSB = x & (1 << 7)
        if MSB != 0:
            sign = -1
        x = x & ((1 << 7) - 1)

    x0 = 1 << (M + 1)
    if x < x0:
        return x
    mask1 = (1 << M) - 1
    mask2 = (1 << M)
    mantissa1 = x & mask1
    exponent = (x >> M) - 1
    # number of shifted bits during  compression
    mantissa2 = mask2 | mantissa1  #add 1 before mantissa
    low = mantissa2 << exponent  #minimal value
    high = low | ((1 << exponent) - 1)  #maxima value
    mean = (low + high) >> 1  #mean value
    return sign * mean


class StixDecompressor(object):
    def __init__(self, spid):
        self.enabled = False
        self.spid = spid
        self.SKM_parameters_names = []
        self.SKM_values = dict()
        self.compressed_parameter_names = []
        try:
            if self.spid in PACKETS_WITH_COMPRESSION:
                self.enabled = True
        except KeyError:
            return
        if spid not in SCHEMAS:
            self.enabled = False
        self.schema = SCHEMAS[spid]
        SKM_Groups = schema['SKM_Groups']
        for grp_name in SKM_Groups:
            self.SKM_parameters_names.extend(SKM_GROUPS[grp_name])


    def set_SKM(self,param_name, raw):
        if param_name in self.SKM_parameters_names:
            self.SKM_values[param_name]=raw
            return True
        return False

    def get_SKM(self, param_name):
        if not param_name  in self.schema['parameters']:
            return None
        try:
            SKM_parameter_names = self.schema['parameters'][param_name]
            return (self.SKM_values[SKM_parameter_names[0]],
                    self.SKM_values[SKM_parameter_names[1]],
                    self.SKM_values[SKM_parameter_names[2]])
        except KeyError:
            return None

    def get_decompressed_value(self,param_name, raw):
        if not self.set_SKM(param_name,raw):
            skm=self.get_SKM(param_name)
            if skm:
                return decompress(raw, skm[0],skm[1],skm[2])
        return None




