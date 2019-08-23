import pickle, gzip
import numpy as np
import math
import os
import pprint
#from matplotlib import pyplot as plt
from ROOT import TGraph, TFile,TCanvas,TH1F
from array import array 
from core import stix_parser
from core import stix_logger
import datetime
_stix_logger= stix_logger._stix_logger

raw_dir='GU/raw/'
l0_dir='GU/l0/'
l1_dir='GU/l1/'
l2_dir='GU/l2/'
proc_log='GU/log/processing.log'
ana_log='GU/log/calibration.log'

def drawMap(detector, pixel, counts):
    pass


def graph2(x,y, title, xlabel, ylabel):
    n=len(x)
    g=TGraph(n,array('d',x),array('d',y))
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.SetTitle(title)
    return g

def hist(k,y, title, xlabel, ylabel):
    n=len(y)
    total=sum(y)
    h2=TH1F("h%d"%k,"%s; %s; %s"%(title,xlabel,ylabel),n,0,n)
    for i,val in enumerate(y):
        for j in range(val):
            h2.Fill(i)
            #to correct the histogram wrong entries
        #h2.SetBinContent(i+1,val)
    h2.GetXaxis().SetTitle(xlabel)
    h2.GetYaxis().SetTitle(ylabel)
    h2.SetTitle(title)
    #h2.SetEntries(sum)

    return h2 

def search(data, name):
    if type(data) is list:
        return [element for element in data if element['name'] == name]
    return None

def get_raw(data, name):
    return [int(item['raw'][0]) for item in data if item['name']==name]

def get_calibration_spectra(packet):
    param=packet['parameters']
    search_res=search(param, 'NIX00159')
    if not search_res:
        return []
    calibration=search_res[0]

    cal=calibration['children']
    nstruct=int(calibration['raw'][0])
    detectors=get_raw(cal, 'NIXD0155')
    pixels=get_raw(cal, 'NIXD0156')
    spectra=[[int(it['raw'][0]) for it in  item['children']] for item in cal if item['name']=='NIX00146']
    #kspectra=[item['children'] for item in cal if item['name']=='NIX00146']
    counts=[]
    for e in spectra:
        counts.append(sum(e))
    result=[]
    for i in range(nstruct):
        result.append({'detector':detectors[i],
            'pixel':pixels[i],
            'counts':counts[i],
            'spec':spectra[i]})
    return result


 

def analysis(file_in, root_filename,
        pdf_filename, spec_log):
    alog=open(ana_log,'a+')
    slog=open(spec_log,'w')
    alog.write('-'*20+'\n')
    now=datetime.datetime.now()
    alog.write(str(now)+'\n')
    alog.write(file_in+'\n')
    f=None
    if file_in.endswith('.pklz'):
        f=gzip.open(file_in,'rb')
    else:
        f=open(file_in,'rb')

    data=pickle.load(f)['packet']
    detector_id=[]
    triggers=[]
    print('Number of packets:')
    print(len(data))
    ip=1
    cc=TCanvas()
    fr=TFile(root_filename,"recreate")
    h=TH1F("h","Triggers; Pixel #; Counts",12*32,0,12*32)
    ipage=0
    for i, d in enumerate(data):
        results=get_calibration_spectra(d)
        spec=pprint.pformat(results)
        slog.write(spec)
        slog.write('\n')
        for row in results:
            if row['counts']>0:
                alog.write('packet %d: %d events in Detector %d Pixel %d\n' %(i, row['counts'], row['detector'], row['pixel']))
                print('Detector %02d Pixel %02d: %0d event(s)' %(row['detector'], row['pixel'],row['counts']))
                xlabel=('ADC channel')
                ylabel=('Counts')
                title=('Detector %d Pixel %d'%(row['detector'], row['pixel']))
                g=hist(ip, row['spec'],title,xlabel,ylabel)
                cc.cd()
                ip+=1
                g.Draw("hist")
                if ipage==0:
                    cc.Print(pdf_filename+'(')
                else:
                    cc.Print(pdf_filename)
                ipage += 1
                fr.cd()
                cc.Write(("c_d_{}_{}_p_{}").format(ip,row['detector'],row['pixel']))
                h.Fill(12*row['detector']+row['pixel'], row['counts'])
                     

    cc.cd()
    h.Draw("hist")
    cc.Write('triggers')
    cc.Print(pdf_filename+')')
    ipage += 1
    print("Total pages: {}".format(ipage))
    #g.Write("trigger")
    fr.Close()
    slog.close()
    alog.close()


    


def main():
    print('opening log file...')
    log=open(proc_log,'r+')
    log_content=log.read()
    for f in os.listdir(raw_dir):
        if f.endswith(".dat"):
            raw_filename=(os.path.join(raw_dir, f))
            if raw_filename in log_content:
                #print('Processed already: %s '%raw_filename)
                continue
            filename=os.path.splitext(f)[0]+'.pkl'
            spec_fname=os.path.splitext(f)[0]+'.spec'
            l0_filename=os.path.join(l0_dir,filename)
            spec_log=os.path.join(l0_dir,spec_fname)
            root_filename=os.path.splitext(f)[0]+'.root'
            l1_filename=os.path.join(l1_dir,root_filename)

            pdf_filename=os.path.splitext(f)[0]+'.pdf'
            l2_filename=os.path.join(l2_dir,pdf_filename)

            print('Parsing file %s -> %s'%( raw_filename, l0_filename))
            log.write(raw_filename+'\n')

            #stix_telemetry_parser.parse_stix_raw_file(raw_filename, 
            #    l0_filename, 54124, 'array')

            stix_logger._stix_logger.set_logger('log/process.log', 2)

            parser = stix_parser.StixTCTMParser()
            parser.parse_file(raw_filename, 
                    l0_filename, 54124, 
                    'binary', 'calibration run')
            analysis(l0_filename, l1_filename,l2_filename, spec_log)


main()
#analysis('GU/l0/calibration_asw154_laszlo.pkl','GU/l1/calibration_asw15_laszlo.root', 'GU/l0/calibration_asw154_1.log')

