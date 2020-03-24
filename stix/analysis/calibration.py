
import os
import sys
sys.path.append('../../')
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from datetime import datetime
from stix_parser.core import stix_datatypes as sdt 
from stix_parser.core import mongo_db  as db


from ROOT import TGraph, TFile, TCanvas, TH1F, gROOT, TBrowser, gSystem, TH2F, gPad

mdb = db.MongoDB()

MIN_COUNTS_PEAK_FIND=100


def find_peaks(spectrum):
    pass

class Analyzer(object):
    def __init__(self, calibration_id):
        self.data=mdb.get_calibration_run_data(calibration_id)[0]
        sbspec_formats=self.data['sbspec_formats']
        spectra=self.data['spectra']
        for spec in spectra:
            if sum(spec[5]) <MIN_COUNTS_PEAK_FIND:
                continue
            start=spec[3]
            end=start+spec[4]*len(spec[5])
            if start >550 or end<300:
                continue
            print('sub-spectra:',spec[3], start, end)

        




if __name__=='__main__':
    analyzer=Analyzer(134)
