#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script relies on pyroot
It can downloaded from http://root.cern.ch
As the pre-compiled version doesn't support python3, one needs to download the source code and compile on your local PC according to steps as below:
1. cmake 
cmake ../source   -Dpython3=ON -DPYTHON_EXECUTABLE=/usr/bin/python3 
-DPYTHON_INCLUDE_DIR=/usr/include/python3.8 -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.8.so -DCMAKE_INSTALL_PREFIX=/opt/root6_python3/
2. make 
3. make install

"""

import os
import sys
sys.path.append('../../')
import numpy as np
import time
from array import array
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
from datetime import datetime
from stix.core import stix_datatypes as sdt 
from stix.core import mongo_db  as db
from ROOT import TGraph, TFile, TCanvas, TH1F, gROOT, TBrowser, gSystem, TH2F, gPad, TF1, TGraphErrors, gStyle



FIT_MIN_X=260
FIT_MAX_X=550
FIT_LEFT_DELTA_X=15
FIT_RIGHT_DELTA_X=30

mdb = db.MongoDB()

MIN_COUNTS_PEAK_FIND=100
ELUT_ENERGIES=[
4, 5, 6, 7,
8, 9, 10,11,
12, 13,14, 15,
16,18, 20, 22,
25, 28, 32,36,
40, 45, 50,56,
63, 70, 76, 84,
100,120, 150]
def compute_elut(baseline, slope):
    elut=[]
    for det in range(0,32):
        for pix in range(0,12):
            p0=baseline[det][pix]
            p1=slope[det][pix]
            if p0>0 and p1>0:
                row=[det,pix]
                Elows=[int(4*(p0+p1*x)) for x in ELUT_ENERGIES]
                row.extend(Elows)
                elut.append(row)
    return elut





def graph_errors(x,y,ex,ey, title, xlabel="x", ylabel="y"):
    n = len(x)
    g = TGraphErrors(n, array('d', x), array('d', y), array('d',ex), array('d',ey))
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.SetTitle(title)
    return g


def graph2(x, y, title="", xlabel="x", ylabel="y"):
    n = len(x)
    g = TGraph(n, array('d', x), array('d', y))
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.SetTitle(title)
    return g
def graph(y):
    n=len(y)
    x = range(0,n)
    g = TGraph(n, array('d', x), array('d', y))
    return g



def hist(x, y, title, xlabel, ylabel):
    h2 = TH1F("h%d" % k, "%s; %s; %s" % (title, xlabel, ylabel), len(x), min(x), max(x))
    for i, val in enumerate(y):
        h2.SetBinContent(i + 1, val)
    h2.GetXaxis().SetTitle(xlabel)
    h2.GetYaxis().SetTitle(ylabel)
    h2.SetTitle(title)
    return h2

def heatmap(arr, htitle, title, xlabel='detector', ylabel='pixel', zlabel='value'):
    h2=TH2F(title, '{};{};{};{}'.format(title,xlabel, ylabel, zlabel),  32, 0, 32, 12, 0, 12)
    for i in range(0,32):
        for j in range(0,12):
            h2.SetBinContent(i+1, j+1, arr[i][j])
    return h2



def find_peaks(detector, pixel, subspec, start, num_summed, spec, fo, pdf):
    gStyle.SetOptFit(111)
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

    total = TF1( 'total_{}_{}_{}'.format(detector, pixel, subspec), 'gaus(0)+gaus(3)', max_x-15, max_x+30, 6)
    g=graph2(x,y, 'detector {} pixel {} sbspec {}'.format(detector, pixel, subspec), 'ADC channel','Counts')
    g.Fit(g1,'RQ')
    g.Fit(g2,'RQ+')
    g.Fit(g3,'RQ')
    g.Fit(total,'RQ+')
    par = array( 'd', 6*[0.] )
    par1 = g1.GetParameters()
    par2 = g2.GetParameters()
    par3 = g3.GetParameters()
    par3_errors = g3.GetParErrors()
    par[0], par[1], par[2] = par1[0], par1[1], par1[2]
    par[3], par[4], par[5] = par2[0], par2[1], par2[2]
    total.SetParameters(par)
    g.Fit( total, 'R+' )
    param=total.GetParameters()
    param_errors=total.GetParErrors()

    fo.cd()
    g.Write()
    total.Write()
    result={
            'detector':detector,
            'pixel':pixel,
            'sbspec_id':subspec
            }
    try:
        result['peaks']={
                'peak1':(param[0],param[1],param[2]), 
                'peak2':(param[3],param[4],param[5]),
                'peak3':(par3[0],par3[1],par3[2]),

                'peak1error':(param_errors[0],param_errors[1],param_errors[2]), 
                'peak2error':(param_errors[3],param_errors[4],param_errors[5]),
                'peak3error':(par3_errors[0],par3_errors[1],par3_errors[2])
                }
    except Exception as e:
        print(str(e))
    peak_y=[param[1],param[4],par3[1]]
    peak_ey=[param_errors[1],param_errors[4],par3_errors[1]]

    peak_x=[30.8, 34.9, 81]
    peak_ex=[.1, 0., 0.]
    gpeaks=None
    if result:
        gpeaks=graph_errors(peak_x, peak_y, peak_ex,peak_ey,
                'Detector {} pixel {} sbspec {}'.format(detector, pixel, subspec),
                'Energy (keV)', 'Peak position (ADC)')
        gpeaks.Fit('pol1')
        gpeaks.GetYaxis().SetRangeUser(0.9*peak_y[0], peak_y[-1]*1.1)
        gpeaks.Write('gpeaks_{}_{}_{}'.format(detector, pixel, subspec))
        
        calibration_params=gpeaks.GetFunction('pol1').GetParameters()
        chisquare=gpeaks.GetFunction('pol1').GetChisquare()
        result['fcal']={'p0':calibration_params[0],'p1':calibration_params[1], 'chi2':chisquare}
    if pdf:
        c=TCanvas()
        c.Divide(2,1)
        c.cd(1)
        g.Draw("ALP")
        c.cd(2)
        if gpeaks:
            gpeaks.Draw()
        c.Print(pdf)

    return result
    

class Analyzer(object):
    def __init__(self, output_dir='./'):
        self.output_dir=output_dir
        gROOT.SetBatch(True)

    def run(self,calibration_id):
        self.data=mdb.get_calibration_run_data(calibration_id)[0]
        if not self.data:
            print("Calibration run {} doesn't exist".format(calibration_id))
            return

        sbspec_formats=self.data['sbspec_formats']
        spectra=self.data['spectra']

        fname_out=os.path.abspath(os.path.join(self.output_dir, 'calibration_{}'.format(calibration_id)))

        f=TFile("{}.root".format(fname_out),"recreate")
        c=TCanvas()
        pdf='{}.pdf'.format(fname_out)
        c.Print(pdf+'[')

        slope = np.zeros((32,12))
        baseline = np.zeros((32,12))

        
        report={}
        report['fit_parameters']=[]

        for spec in spectra:
            if sum(spec[5]) <MIN_COUNTS_PEAK_FIND:
                continue
            detector=spec[0]
            pixel=spec[1]
            sbspec_id=spec[2]
            start=spec[3]
            num_summed=spec[4]
            end=start+num_summed*len(spec[5])
            spectrum=spec[5]


            if start >FIT_MAX_X  or end<FIT_MIN_X:
                #print('Ignored sub-spectra:',spec[3], start, end)
                continue
            par=find_peaks(detector, pixel, sbspec_id,  start, num_summed,  spectrum, f, pdf)
            report['fit_parameters'].append(par)
            if par:
                if 'fcal' in par:
                    slope[detector][pixel]=par['fcal']['p1']
                    baseline[detector][pixel]=par['fcal']['p0']


        report['pdf']=pdf
        report['elut']=compute_elut(baseline,slope)
        
        mdb.update_calibration_analysis_report(calibration_id, report)

        h2slope=heatmap(slope, 'Energy conversion factor', 'Conversion factor', 'Detector', 'Pixel', 'Energy conversion factor (ADC/keV)')
        h2baseline=heatmap(baseline,'baseline', 'baseline', 'Detector', 'Pixel', 'baseline (E=0)')
        c2=TCanvas()
        c2.Divide(2,1)
        c2.cd(1)
        h2baseline.Draw("colz")
        c2.cd(2)
        h2slope.Draw("colz")
        c2.Print(pdf)
        


        c.Print(pdf+']')

        f.Close()
            #print(par)
    def daemon(self):
        while True:
            calibration_run_ids=mdb.get_calibration_runs_for_processing()
            print(calibration_run_ids)
            for run_id in calibration_run_ids:
                self.run(run_id)
            time.sleep(60)
            break



        




if __name__=='__main__':
    if len(sys.argv)==1:
        analyzer=Analyzer()
        analyzer.daemon()
    else:
        analyzer=Analyzer()
        analyzer.run(int(sys.argv[1]))

