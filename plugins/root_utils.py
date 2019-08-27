from ROOT import TGraph, TFile,TCanvas,TH1F, gROOT,TBrowser,gSystem
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

