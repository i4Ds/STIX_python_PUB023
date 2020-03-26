
import os
import sys
sys.path.append('../../')
import numpy as np
from array import array
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from datetime import datetime
from stix.core import stix_datatypes as sdt 
from stix.core import mongo_db  as db


from ROOT import TGraph, TFile, TCanvas, TH1F, gROOT, TBrowser, gSystem, TH2F, gPad, TF1

FIT_MIN_X=260
FIT_MAX_X=550
FIT_LEFT_DELTA_X=15
FIT_RIGHT_DELTA_X=30

mdb = db.MongoDB()

MIN_COUNTS_PEAK_FIND=100

spectrum_mc=[13,14,12,18,20,17,13,18,13,12,20,12,18,11,22,17,20,11,16,12,22,26,17,23,27,15,10,22,44,102,225,611,1457,3091,5867,10085,15395,20816,25295,26842,25283,21478,16208,10544,6187,3176,1462,661,439,522,974,1650,2550,3742,4639,5153,5385,4940,4065,3002,1986,1332,751,384,202,104,41,25,25,23,13,20,17,19,18,17,16,13,10,13,14,22,11,15,17,11,23,18,15,13,16,23,13,13,17,11,18,13,16,20,12,16,21,17,21,14,16,20,20,24,20,22,28,27,40,39,44,51,61,103,150,227,320,384,485,559,497,489,382,246,161,97,38,24,19,13,12,8,16,18,8,10,15,11,12,9,15,12,11,13,16,14,21,33,45,73,108,112,134,125,99,88,62,39,21,19,11,13,16,29,40,44,70,104,112,119,107,112,68,54,58,35,33,16,20,9,22,12,9,12,6,22,20,22,27,40,46,69,104,153,190,210,302,339,344,395,392,439,390,472,495,532,524,538,590,653,685,760,778,799,899,1051,1093,1223,1358,1599,1833,2065,2399,2852,3378,3761,4122,4301,4068,3283,2553,1860,1171,608,324,145,74,33,17,22,23,14,17,12,12,11,10,4,7,5,15,6,5,11,10,12,8,13,11,9,10,14,13,7,11,11,12,10,13,19,9,11,15]
#realistic spectrum from Monte Carlo simulation

def specfun(x, par):
    index=int(((x[0]-par[0])*par[1]-20)*4)
    #print(x[0],par[0], par[1], par[2], index)
    try:
        return spectrum_mc[index] * par[2]
    except IndexError:
        return 0



def graph2(x, y, title="", xlabel="x", ylabel="y"):
    n = len(x)
    g = TGraph(n, array('d', x), array('d', y))
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.SetTitle(title)
    return g


def hist(x, y, title, xlabel, ylabel):
    h2 = TH1F("h%d" % k, "%s; %s; %s" % (title, xlabel, ylabel), len(x), min(x), max(x))
    for i, val in enumerate(y):
        h2.SetBinContent(i + 1, val)
    h2.GetXaxis().SetTitle(xlabel)
    h2.GetYaxis().SetTitle(ylabel)
    h2.SetTitle(title)

    return h2



def find_peaks(detector, pixel, subspec, start, num_summed, spec, fo):
    x_full=[start+i*num_summed+0.5*num_summed for i in range(0,len(spec))]
    x=[]
    y=[]
    for ix, iy in zip(x_full,spec):
        if ix>FIT_MIN_X and ix<FIT_MAX_X:
            x.append(ix)
            y.append(iy)
    max_y=max(y)
    max_x=x[y.index(max_y)]

    max_x2=0
    max_y2=0
    for ix, iy in zip(x,y):
        if ix<max_x+FIT_RIGHT_DELTA_X:
            continue
        if iy>max_y2:
            max_x2=ix
            max_y2=iy
            
    g1 = TF1( 'g1_{}_{}_{}'.format(detector, pixel, subspec), 'gaus',  max_x-15,  max_x+ 15)
    g2 = TF1( 'g2_{}_{}_{}'.format(detector, pixel, subspec), 'gaus', max_x+5, max_x+30)
    g3 = TF1( 'g3_{}_{}_{}'.format(detector, pixel, subspec), 'gaus', max_x2-3, max_x2+15)

    total = TF1( 'total_{}_{}_{}'.format(detector, pixel, subspec), 'gaus(0)+gaus(3)', max_x-15, max_x+30)
    g=graph2(x,y, 'g_{}_{}_{}'.format(detector, pixel, subspec))
    g.Fit(g1,'R')
    g.Fit(g2,'R+')
    g.Fit(g3,'R+')
    g.Fit(total,'R+')
    par = array( 'd', 9*[0.] )
    par1 = g1.GetParameters()
    par2 = g2.GetParameters()
    par3 = g3.GetParameters()
    par[0], par[1], par[2] = par1[0], par1[1], par1[2]
    par[3], par[4], par[5] = par2[0], par2[1], par2[2]
    total.SetParameters(par)
    g.Fit( total, 'R+' )

    fo.cd()
    g.Write()
    total.Write()
    #g1.Write()
    #g2.Write()
    #g3.Write()
    
    parameters=[]
    try:
        parameters=[p  for p in par]
    except: 
        pass
    return parameters

def fit_mc(detector, pixel, subspec, start, num_summed, spec, fo):
    x_full=[start+i*num_summed+0.5*num_summed for i in range(0,len(spec))]
    x=[]
    y=[]
    for ix, iy in zip(x_full,spec):
        if ix>FIT_MIN_X and ix<FIT_MAX_X:
            x.append(ix)
            y.append(iy)
    max_y=max(y)
    total = TF1( 'total_{}_{}_{}'.format(detector, pixel, subspec), specfun, FIT_MIN_X, FIT_MAX_X,3)
    nor=max(spectrum_mc)/max_y
    total.SetParLimits(0,200,400)
    total.SetParLimits(1,0.2, 1)
    #total.SetParLimits(2,0.1*nor, 1.1*nor)

    g=graph2(x,y, 'g_{}_{}_{}'.format(detector, pixel, subspec))
    g.Fit(total,'R')
    fo.cd()
    g.Write()
    par = array( 'd', 3*[0.] )
    return total.GetParameters()
    #return [p for p in par]

    

class Analyzer(object):
    def __init__(self, calibration_id):
        self.data=mdb.get_calibration_run_data(calibration_id)[0]
        sbspec_formats=self.data['sbspec_formats']
        spectra=self.data['spectra']
        f=TFile("test.root","recreate")
        for spec in spectra:
            if sum(spec[5]) <MIN_COUNTS_PEAK_FIND:
                continue
            start=spec[3]
            num_summed=spec[4]
            end=start+num_summed*len(spec[5])
            if start >FIT_MAX_X  or end<FIT_MIN_X:
                #print('Ignored sub-spectra:',spec[3], start, end)
                continue
            par=find_peaks(spec[0], spec[1], spec[2], start, num_summed,  spec[5], f)
            #par=fit_mc(spec[0], spec[1], spec[2], start, num_summed,  spec[5], f)
        f.Close()
            #print(par)

        




#if __name__=='__main__':
analyzer=Analyzer(134)
