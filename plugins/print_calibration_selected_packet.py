#plot calibration spectra, whose counts are still compressed

#from ROOT import TGraph, TFile,TCanvas,TH1F, gROOT,TBrowser

def search(data, name):
    if type(data) is list:
        return [element for element in data if element['name'] == name]
    return None

def get_raw(data, name):
    return [int(item['raw'][0]) for item in data if item['name']==name]


"""
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
"""

def get_calibration_spectra(packet):
    param=packet['parameters']
    search_res=search(param, 'NIX00159')
    if not search_res:
        return []
    num_struct=int(search_res[0]['raw'][0])
    #number of structure
    cal=search_res[0]['children']
    detectors=get_raw(cal, 'NIXD0155')
    pixels=get_raw(cal, 'NIXD0156')
    spectra=[[int(it['raw'][0]) for it in  item['children']] for item in cal if item['name']=='NIX00146']
    counts=[]
    for e in spectra:
        counts.append(sum(e))
    result=[]
    for i in range(num_struct):
        result.append({'detector':detectors[i],
            'pixel':pixels[i],
            'counts':counts[i],
            'spec':spectra[i]})
    return result

SPID=54124

class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        # your code goes here
        timestamp=[]
        spectra=[]
        packet=self.packets[self.current_row]
        #for packet in self.packets:
        if int(packet['header']['SPID']) != SPID:
            print('The selected packet is not a calibration report')
            return
        header=packet['header']
        spectra.extend(get_calibration_spectra(packet))

        num_spectra=len(spectra)
        
        #fout=TFile('~/Desktop/calibration.root','recreate')
        #hcounts=TH1F("hcounts","Channel counts; Pixel #; Counts",12*32,0,12*32)
        #fout.cd()

        #cc=TCanvas()
        tot_num_spec = 0
        for i,spec in enumerate(spectra):
            if spec['counts']>0:
                print('Detector %d Pixel %d, counts: %d '%(spec['detector'], spec['pixel'], spec['counts']))
                #xlabel=('ADC channel')
                #ylabel=('Counts')
                #title=('Detector %d Pixel %d '%(spec['detector'], spec['pixel']))
                #g=hist(i, spec['spec'],title,xlabel,ylabel)
                #cc.cd()
                #g.Draw("hist")
                #cc.Write(("spec_det_{}_{}_p_{}").format(i,spec['detector'],spec['pixel']))
                #hcounts.Fill(12*spec['detector']+spec['pixel'], spec['counts'])
                tot_num_spec += 1
        #hcounts.Write('hcounts')
        print('Total number of non-empty spectra:%d'%tot_num_spec)
        #print('spectra saved to calibration.root')
        #gROOT.ProcessLine('new TBrowser()')





        







            
