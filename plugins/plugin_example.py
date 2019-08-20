#plugin example
import pprint
class Plugin:
    def __init__(self, data=[], current_row=0):
        self.data=data
        self.current_row=current_row
        print("Plugin  loaded ...")
    def run(self):
        #your analysis code goes here
        print('data length: {}'.format(len(self.data)))
        print('current row: {}'.format(self.current_row))
        if len(self.data)>1:
            pprint.pprint(self.data[0])
            
