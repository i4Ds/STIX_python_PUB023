import pickle, gzip
import numpy as np
import math
import os
import pprint
#from matplotlib import pyplot as plt
from ROOT import TGraph, TFile,TCanvas
from array import array 
from core import stix_telemetry_parser
from core import stix_logger
import datetime
LOGGER = stix_logger.LOGGER
LOGGER.set_level(1)

raw_dir='GU/raw/'
l0_dir='GU/l0/'
l1_dir='GU/l1/'
proc_log='GU/log/processing.log'
ana_log='GU/log/calibration.log'



def graph2(x,y, title, xlabel, ylabel):
    n=len(x)
    
    g=TGraph(n,array('d',x),array('d',y))
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.SetTitle(title)
    return g

def graph(y, title, xlabel, ylabel):
    n=len(y)
    x=array('d',range(0,n))
    g=TGraph(n,x,array('d',y))
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.SetTitle(title)
    return g


def analysis(file_in, file_out):
    alog=open(ana_log,'a+')
    alog.write('-'*20+'\n')
    now=datetime.datetime.now()
    alog.write(str(now)+'\n')
    alog.write(file_in+'\n')

    f=gzip.open(file_in,'rb')
    data=pickle.load(f)['packet']
    detector_id=[]
    triggers=[]
    print('Number of packets:')
    print(len(data))
    ip=1
    cc=TCanvas()
    fr=TFile(file_out,"recreate")
    for i, d in enumerate(data):
        param=d['parameter']
        spectra=param['NIX00158']
        nstruct=param['NIX00159']
        nbins=param['NIXG0403']
        #print('spectra length:')
        #print(len(spectra))
        detectors=param['NIXD0155']
        pixels=param['NIXD0156']
        
        for det, pix in zip(detectors,pixels):
            #print(det,pix)
            detector_id.append((int(det))*12+int(pix))
        sub_spectra=[spectra[0:1024], spectra[1024:2048], spectra[2048:3072]]
        counts=[np.sum(sub_spectra[0]), np.sum(sub_spectra[1]), np.sum(sub_spectra[2])]
        for n, c in enumerate(counts):
            if c>0:
                alog.write('%d events in Detector %s Pixel %s\n' %(c, detectors[n], pixels[n]))
                print('%d events in Detector %s Pixel %s\n' %(c, detectors[n], pixels[n]))
                #plt.subplot(nrow,1, ip)
                xlabel=('ADC channel')
                ylabel=('Counts')
                title=('Detector %s Pixel %s'%(detectors[n], pixels[n]))
                g=graph(sub_spectra[n],title,xlabel,ylabel)

                cc.cd()
                g.Draw("ALP")
                fr.cd()
                cc.Write("c%d"%ip)
                g.Write("g%d"%ip)
                ip += 1
                     
        triggers.extend(counts)
    g=graph2(detector_id,triggers,'Triggers','Pixel #', 'Counts')
    cc.cd()
    g.Draw("ALP")
    cc.Write('triggers')
    g.Write("trigger_g%d"%ip)
    fr.Close()

    


def main():
    print('opening log file...')
    log=open(proc_log,'r+')
    log_content=log.read()
    print(log_content)
    return
    for f in os.listdir(raw_dir):
        if f.endswith(".dat"):
            raw_filename=(os.path.join(raw_dir, f))
            if raw_filename in log_content:
                print('Processed already: %s '%raw_filename)
                continue
            filename=os.path.splitext(f)[0]+'.pkl'
            l0_filename=os.path.join(l0_dir,filename)
            filename=os.path.splitext(f)[0]+'.root'
            l1_filename=os.path.join(l1_dir,filename)
            print('Parsing file %s -> %s'%( raw_filename, l0_filename))
            log.write(raw_filename+'\n')

            stix_telemetry_parser.parse_stix_raw_file(raw_filename,LOGGER, 
                l0_filename, 54124, 'array')
            analysis(l0_filename, l1_filename)


main()

