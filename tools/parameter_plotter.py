import sys
from datetime import datetime
import numpy as np
from core import idb
from stix_io import odb
from core  import stix_plotter
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from tools import packet_stat

class ParmeterPlotter:
    def __init__(self,filename, output_pdf=None):
        self.filename=filename
        self.odb=odb.ODB(filename)
        self.pdf=None
        self.operation_modes=None
        self.headers=None
        self.db_queries()
        if output_pdf:
            try:
                self.pdf=PdfPages(output_pdf)
            except Exception as e: 
                print(e.message)

    def db_queries(self):
        if not self.odb:
            return 
        self.operation_modes=self.odb.get_operation_modes()
        self.headers=self.odb.get_headers()

    #def __del__(self):
    #    self.done()
    def done(self):
        if self.pdf:
            self.pdf.close()
    def plot_operation_modes(self):
        print('plotting operation modes...')
        t0=float(self.operation_modes[0][0])
        timestamp=np.array([float(e[0])-t0  for e in self.operation_modes])
        mode=np.array([eval(e[1])[0]  for e in self.operation_modes])
        stix_plotter.plot_operation_mode_timeline(timestamp,mode,self.pdf)
    def plot_headers(self):
        print('plotting header information ...')
        t0=float(self.headers[0][0])
        timestamps=[float(e[0])-t0  for e in self.headers]
        spids=[e[1]  for e in self.headers]
        stix_plotter.plot_packet_header_timeline(timestamps,spids,self.pdf)
    def create_title_page(self):
        print('creating title page')
        first_page = plt.figure(figsize=(11.69,8.27))
        first_page.clf()
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        txt = 'STIX file {} analysis report \n {}'.format(self.filename,date_time)
        first_page.text(0.5,0.5,txt, transform=first_page.transFigure, size=24, ha="center")
        self.pdf.savefig()
        plt.close() 
    def create_packet_stat_page(self):
        if self.pdf:
            print('creating packet statistic page')
            spids=[e[1] for e in self.headers]
            text=packet_stat.get_packet_type_stat_text(spids)
            page = plt.figure(figsize=(11.69,8.27))
            page.clf()
            page.text(0.1,0.1,text, transform=page.transFigure)
            self.pdf.savefig()
            plt.close() 
    def plot_temperatures(self):
        temperature_sensors={
                "NIXD0024":		"PSU temperature",
                "NIXD0025":		"IDPU temperature 1",
                "NIXD0026":		"IDPU temperature 2",
                "NIXD0040":		"Aspect temperature 1",
                "NIXD0041":		"Aspect temperature 2",
                "NIXD0042":		"Aspect temperature 3",
                "NIXD0043":		"Aspect temperature 4",
                "NIXD0044":		"Aspect temperature 5",
                "NIXD0045":		"Aspect temperature 6",
                "NIXD0046":		"Aspect temperature 7",
                "NIXD0047":		"Aspect temperature 8",
                "NIXD0051":		"Attenuator temperature",
                "NIXD0054":		"Detectors temperature Q1",
                "NIXD0055":		"Detectors temperature Q2",
                "NIXD0056":		"Detectors temperature Q3",
                "NIXD0057":		"Detectors temperature Q4",
                "NIXG0251":		"IDPU temperature",
                "NIXG0256":		"Aspect temperature",
                "NIXG0260":		"Detectors temperature"
                }
        for key, value in temperature_sensors.items():
            self.plot_parameter(key, value, value, self.pdf)

    def plot_all_parameters_of_spid(self, spid):
        if self.odb:
            parameters=self.odb.get_parameter_names_of_spid(spid)
            for par in parameters:
                name=par[0]
                self.plot_parameter(name, pdf=self.pdf)


    def plot_parameter(self,name, pdf=None):
        if self.odb:
            data=self.odb.get_parameter_values(name)
            descr=data[0]['descr']
            eng_value_type=data[0]['eng_value_type']
            is_string=False
            try:
                x=np.array([float(t['header_time']) for t in data if t['raw']])
                title=descr+' ('+eng_value_type+')'
                print('plotting:{}'.format(title))
                y=np.array([])
                if eng_value_type == 'I':
                    y=np.array([float(eval(t['raw'])[0]) for t in data if t['raw']])
                elif eng_value_type =='F':
                    y=np.array([t['eng_value'] for t in data if t['raw']])
                elif eng_value_type == 'S':
                    y=np.array([t['eng_value'] for t in data if t['raw']])
                    is_string=True

                if y.size > 0 and not is_string:
                    stix_plotter.plot_parameter_timeline(x,y,title=title, ylabel=descr, pdf=self.pdf)
                if y.size >0 and is_string:
                    stix_plotter.plot_text_timeline(x,y,title=title, ylabel=descr, reset_t0=True, pdf=self.pdf)
            #else:
            except:
                print('parameter {} not plotted'.format(name))



    def make_pdf(self):
        if self.pdf:
            self.create_title_page()
            self.create_packet_stat_page()
        print('plotting header info')
        self.plot_headers()
        print('plotting operation mode')
        self.plot_operation_modes()
        self.plot_temperatures()
        print('plotting temperature sensors')
        self.plot_all_parameters_of_spid(54101)
        self.plot_all_parameters_of_spid(54102)
        self.done()




if __name__=='__main__':
    pdf_filename=None
    if len(sys.argv)!=3 and len(sys.argv)!=2:
        print('make_report <input> <parameter name>')
    if len(sys.argv)==3:
        pdf_filename=sys.argv[2]

    process=ParmeterPlotter(sys.argv[1],pdf_filename)
    process.make_pdf()

