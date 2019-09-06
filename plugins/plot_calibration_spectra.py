#plot calibration spectra, whose counts are still compressed

import os
import sys
sys.path.append('..')
sys.path.append('.')

from PyQt5 import QtWidgets, QtCore, QtGui

from core import stix_packet_analyzer as sta
analyzer=sta.analyzer()


from ROOT import TGraph, TFile,TCanvas,TH1F, gROOT,TBrowser,gSystem
def graph2(x,y, title, xlabel, ylabel):
    n=len(x)
    g=TGraph(n,array('d',x),array('d',y))
    g.GetXaxis().SetTitle(xlabel)
    g.GetYaxis().SetTitle(ylabel)
    g.SetTitle(title)
    return g

def hist(k,y, title, xlabel, ylabel):
    h2=TH1F("h%d"%k,"%s; %s; %s"%(title,xlabel,ylabel),len(y),0,max(y))
    for i,val in enumerate(y):
        for j in range(val):
            h2.Fill(i)
    h2.GetXaxis().SetTitle(xlabel)
    h2.GetYaxis().SetTitle(ylabel)
    h2.SetTitle(title)
    #h2.SetEntries(sum)

    return h2 



SPID=54124

class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        # your code goes here
        filename = str(
                QtWidgets.QFileDialog.getSaveFileName(None, "Save to file",'', 
                                                      "ROOT(*.root)")[0])
        dirname=os.path.dirname(filename)
        if not filename.endswith('.root'):
            print('Invalid filename')
            return 
        

        fout=TFile(filename,'recreate')
        fout.cd()
        hcounts=TH1F("hcounts","Channel counts; Pixel #; Counts",12*32,0,12*32)
        num=0
        for packet in self.packets:
            try:
                if int(packet['header']['SPID']) != SPID:
                    continue
            except ValueError:
                continue
            analyzer.load_packet(packet)
            detector_ids=analyzer.find_all('NIX00159>NIXD0155')
            pixels_ids=analyzer.find_all('NIX00159>NIXD0156')
            spectra=analyzer.find_all_children('NIX00159>NIX00146')
            for i,spec in enumerate(spectra):
                if sum(spec)>0:
                    num+=1
                    det=detector_ids[i]
                    pixel=pixels_ids[i]
                    print('Detector %d Pixel %d, counts: %d '%(det, pixel, sum(spec)))

                    xlabel= 'Energy channel'
                    ylabel= 'Counts'
                    title=('Detector %d Pixel %d '%(det, pixel))
                    g=hist(i, spec,title,xlabel,ylabel)
                    #cc.cd(current_idx+1)
                    g.Draw("hist")
                    g.Write()
                    hcounts.Fill(12*det+pixel, spec)
                    #current_idx+=1
        hcounts.Write('hcounts')
        print('spectra saved to calibration.root')
        fout.Close()
        gROOT.ProcessLine('new TBrowser()')
        gROOT.ProcessLine('new TFile("{}")'.format(filename))


        print('Total number of non-empty spectra:%d'%num)



        







            
