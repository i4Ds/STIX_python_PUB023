#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A program to perform energy calibration. 
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
from datetime import datetime
from stix.core import stix_datatypes as sdt 
from stix.core import mongo_db  as db
from ROOT import TGraph, TFile, TCanvas, TH1F, gROOT, TBrowser, gSystem, TH2F, gPad, TF1, TGraphErrors, gStyle, TSpectrum, gRandom, TPaveLabel




FIT_MIN_X=260
FIT_MAX_X=550
FIT_LEFT_DELTA_X=15
FIT_RIGHT_DELTA_X=50
MAX_ALLOWED_SIGMA_ERROR = 20  #maximum allowed peak error



DEFAULT_OUTPUT_DIR='/data/'
mdb = db.MongoDB()
MIN_COUNTS_PEAK_FIND=50
ELUT_ENERGIES=[
4, 5, 6, 7,
8, 9, 10,11,
12, 13,14, 15,
16,18, 20, 22,
25, 28, 32,36,
40, 45, 50,56,
63, 70, 76, 84,
100,120, 150]

gROOT.SetBatch(True)


def compute_elut(baseline, slope):
    elut=[]
    for det in range(0,32):
        for pix in range(0,12):
            p0=baseline[det][pix]
            p1=slope[det][pix]
            #print(det, pix, p0, p1)


            if p0>0 and p1>0:
                row=[det,pix]
                Elows=[int(4*(p0+p1*x)) for x in ELUT_ENERGIES]
                row.extend(Elows)
                elut.append(row)
    return elut

def find_peaks2(detector, pixel, subspec, start, num_summed, spec, fo, pdf):
    #find peaks using TSpectrum
    x_full=[start+i*num_summed+0.5*num_summed for i in range(0,len(spec))]
    nbins=len(subspec)
    sigma=2
    threshold=10
    background_remove=True
    decon_interations=1000
    markov=True
    averg_window=3

    #print(threshold)

    y=array('d',subspec)
    des=array('d',[0]*nbins)
    s=TSpectrum()
    num_found=s.SearchHighRes(y, des,nbins,sigma, threshold, background_remove, decon_interations,
            markov, averg_window)
    xp=s.GetPositionX()
    xpeaks=[]
    for i in range(num_found):
        xpeaks.append(x_full[xp[i]])

def sub_bkg(spec):
    bkg=array('d',spec)
    s=TSpectrum()
    nbins=len(spec)
    back_decreasing_window=1
    back_order_2=0
    back_smoothing=3
    num_interations=6
    s.Background(bkg, nbins, num_interations, back_decreasing_window, 
            back_order_2, False, back_smoothing, False)
    bkgsub=np.array(spec)-np.array(bkg)
    return bkg,  bkgsub.tolist()



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
#def graph(y):
#    n=len(y)
#    x = range(0,n)
#    g = TGraph(n, array('d', x), array('d', y))
#    return g
#
#
#def hist(x, y, title, xlabel, ylabel):
#    h2 = TH1F("h%d" % k, "%s; %s; %s" % (title, xlabel, ylabel), len(x), min(x), max(x))
#    for i, val in enumerate(y):
#        h2.SetBinContent(i + 1, val)
#    h2.GetXaxis().SetTitle(xlabel)
#    h2.GetYaxis().SetTitle(ylabel)
#    h2.SetTitle(title)
#    return h2

def heatmap(arr, htitle, title, xlabel='detector', ylabel='pixel', zlabel='value'):
    h2=TH2F(title, '{};{};{};{}'.format(title,xlabel, ylabel, zlabel),  32, 0, 32, 12, 0, 12)
    for i in range(0,32):
        for j in range(0,12):
            h2.SetBinContent(i+1, j+1, arr[i][j])
    return h2


def get_subspec(x, y, xmin, xmax):
    a=[]
    b=[]
    for ix, iy in zip(x,y):
        if ix>xmin and ix<xmax:
            a.append(ix)
            b.append(iy)
    return a,b

def add_test_background(spectrum):
    bkg=TF1("fbkg","0.5e3*exp(-x/400)",0,1024);
    s=[]
    for i in range(0,len(spectrum)):
        spectrum[i]=(spectrum[i]+bkg.Eval(i)+gRandom.Uniform(10));



def find_peaks(detector, pixel, subspec, start, num_summed, spectrum, fo):

    gStyle.SetOptFit(111)
    #add_test_background(spectrum)

    x0=[start+i*num_summed+0.5*num_summed for i in range(0,len(spectrum))]
    x, y_all=get_subspec(x0, spectrum, FIT_MIN_X, FIT_MAX_X)
    if not x:
        print('Can not find sub spectrum of ERROR:', detector, pixel)
        return

    bkg, y=sub_bkg(y_all)
    name='{}_{}_{}'.format(detector, pixel, subspec)
    title='detector {} pixel {} subspec {}'.format(detector, pixel, subspec)


    gsig=graph2(x,y_all, 'Original spec - {}'.format(name), 'ADC channel','Counts')
    gbkg=graph2(x,bkg, 'Background - {}'.format(name), 'ADC channel','Counts')


    max_y=max(y)
    max_x=x[y.index(max_y)]

    max_x2=0
    max_y2=0
    for ix, iy in zip(x,y):
        if ix< max_x+FIT_RIGHT_DELTA_X:
            continue
        if iy>max_y2:
            max_x2=ix
            max_y2=iy
            
    g1 = TF1( 'g1_{}'.format(name), 'gaus',  max_x-15,  max_x+ 15)
    g2 = TF1( 'g2_{}'.format(name), 'gaus', max_x+5, max_x+30)
    g3 = TF1( 'g3_{}'.format(name), 'gaus', max_x2-3, max_x2+15)

    total = TF1( 'total_{}'.format(name), 'gaus(0)+gaus(3)', max_x-15, max_x+30, 6)

    g=graph2(x,y, 'Bkg subtracted - {}'.format(title), 'ADC channel','Counts')


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
    g.Fit( total, 'RQ+' )
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
    peak_x=[]
    peak_ex=[]
    peak_y=[]
    peak_ey=[]

    if param_errors[2]<MAX_ALLOWED_SIGMA_ERROR:
        peak_x.append(30.8)
        peak_ex.append(0.)
        peak_y.append(param[1])
        peak_ey.append(param_errors[1])

    if param_errors[5]<MAX_ALLOWED_SIGMA_ERROR:
        peak_x.append(34.9)
        peak_ex.append(0.)
        peak_y.append(param[4])
        peak_ey.append(param_errors[4])

    if par3_errors[2]<MAX_ALLOWED_SIGMA_ERROR:
        peak_x.append(81)
        peak_ex.append(0.)
        peak_y.append(par3[1])
        peak_ey.append(par3_errors[1])
    #peak_x=[30.8, 34.9, 81]
    #peak_ex=[.0, 0., 0.]
    gpeaks=None
    if len(peak_x)>=2:
        gpeaks=graph_errors(peak_x, peak_y, peak_ex,peak_ey,
                title,
                'Energy (keV)', 'Peak position (ADC)')
        gpeaks.Fit('pol1','Q')
        gpeaks.GetYaxis().SetRangeUser(0.9*peak_y[0], peak_y[-1]*1.1)
        gpeaks.Write('gpeaks_{}'.format(name))
        
        calibration_params=gpeaks.GetFunction('pol1').GetParameters()
        chisquare=gpeaks.GetFunction('pol1').GetChisquare()
        result['fcal']={'p0':calibration_params[0],'p1':calibration_params[1], 'chi2':chisquare}
    

    return result, [gsig, g, gpeaks]
    


def analyze(calibration_id, output_dir='./'):
    data=mdb.get_calibration_run_data(calibration_id)[0]
    if not data:
        print("Calibration run {} doesn't exist".format(calibration_id))
        return

    sbspec_formats=data['sbspec_formats']
    spectra=data['spectra']

    fname_out=os.path.abspath(os.path.join(output_dir, 'calibration_{}'.format(calibration_id)))

    f=TFile("{}.root".format(fname_out),"recreate")


    is_top=True

    slope = np.zeros((32,12))
    baseline = np.zeros((32,12))

    
    report={}
    report['fit_parameters']=[]
    print('Processing calibration run {} ...'.format(calibration_id))

    canvas=TCanvas("c","canvas", 1200, 500)
    pdf='{}.pdf'.format(fname_out)
    canvas.Print(pdf+'[')
    canvas.Divide(3,2)
    last_plots=None

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
            #break
            continue

        par,plots=find_peaks(detector, pixel, sbspec_id,  start, num_summed,  spectrum, f)




        if last_plots:
            canvas.cd(1)
        
            if last_plots[0]:
                last_plots[0].Draw("AL")
            canvas.cd(2)
            if last_plots[1]:
                last_plots[1].Draw("AL")
            canvas.cd(3)
            if last_plots[2]:
                last_plots[2].Draw("ALP")
            canvas.cd(4)
            if plots[0]:
                plots[0].Draw("AL")
            canvas.cd(5)
            if plots[1]:
                plots[1].Draw("AL")
            canvas.cd(6)
            if plots[2]:
                plots[2].Draw("ALP")
            canvas.Print(pdf)
            last_plots=[]
        else:
            last_plots=plots


    


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
    canvas.Print(pdf+']')

    h2slope.Write("h2slop")
    h2baseline.Write("h2baseline")

    print('done.\nFile {} generated'.format(pdf))

    f.Close()
    #print(par)
def daemon():
    while True:
        calibration_run_ids=mdb.get_calibration_runs_for_processing()
        print(calibration_run_ids)
        for run_id in calibration_run_ids:
            analyze(run_id, DEFAULT_OUTPUT_DIR)
        print('waiting for new data...')
        time.sleep(600)




if __name__=='__main__':
    #output_dir=DEFAULT_OUTPUT_DIR
    output_dir='./'

    if len(sys.argv)==1:
        daemon()
    elif len(sys.argv)>=2:
        if len(sys.argv)>=3:
            output_dir=sys.argv[2]
        analyze(int(sys.argv[1]), output_dir)

