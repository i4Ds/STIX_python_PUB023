import sys
from datetime import datetime
from core import idb
from stix_io import odb
from core  import stix_plotter
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from tools import packet_stat

class Report:

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
        timestamp=[float(e[0])-t0  for e in self.operation_modes]
        mode=[eval(e[1])[0]  for e in self.operation_modes]
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





    def run(self):
        if self.pdf:
            self.create_title_page()
            self.create_packet_stat_page()
        self.plot_headers()
        self.plot_operation_modes()
        self.done()




if __name__=='__main__':
    pdf_filename=None
    if len(sys.argv)!=3 and len(sys.argv)!=2:
        print('plot_operation_mode  <input> [pdf file]')
    if len(sys.argv)==3:
        pdf_filename=sys.argv[2]

    process=Report(sys.argv[1],pdf_filename)
    process.run()

