#plugin example
import pprint
from matplotlib import pyplot as plt
def get_raw(parameters, name):
    return [int(item['raw'][0]) for item in parameters if item['name']==name][0]
def get_eng_text(parameters, name):
    return [item['value'] for item in parameters if item['name']==name][0]

SPID=54277

class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        plt.ion()
        # your code goes here
        line0_timestamp=[]
        line1_timestamp=[]
        line0_old_state=[]
        line0_new_state=[]
        line1_old_state=[]
        line1_new_state=[]
        last_time=0

        T0=0
        for packet in self.packets:
            if int(packet['header']['SPID']) != SPID:
                continue
            header=packet['header']
            time=float(header['time'])
            if T0 == 0:
                T0=time

            parameters=packet['parameters']

            HV_line=get_raw(parameters,'NIX00181')
            old_stat_text=get_eng_text(parameters,'NIX00182')
            new_stat_text=get_eng_text(parameters,'NIX00183')

            old_stat_raw=get_raw(parameters,'NIX00182')
            new_stat_raw=get_raw(parameters,'NIX00183')


            if HV_line== 0 :
                line0_timestamp.append(time-T0)
                line0_old_state.append(old_stat_raw)
                line0_new_state.append(new_stat_raw)
            else:
                line1_timestamp.append(time-T0)
                line1_old_state.append(old_stat_raw)
                line1_new_state.append(new_stat_raw)

                field_time=header['utc']
                print('{}, {}, {}, {}, {}'.format(HV_line, field_time,old_stat_text,new_stat_text,time-last_time))
                last_time=time

        plt.figure(1)

        plt.subplot(411)
        plt.step(line0_timestamp,line0_old_state,where='post', label='HV line 0 old state')
        plt.plot(line0_timestamp,line0_old_state, 'C0o',alpha=0.5)
        plt.xlabel('Time -T0 (s)')
        plt.ylabel('State (0: OFF, 1: ON)')
        plt.legend()
        plt.subplot(412)
        plt.step(line0_timestamp,line0_new_state,where='post', label='HV line 0 new state')
        plt.plot(line0_timestamp,line0_new_state, 'C1o',alpha=0.5)
        plt.xlabel('Time -T0 (s)')
        plt.ylabel('State (0: OFF, 1: ON)')

        plt.legend()
        plt.subplot(413)
        plt.step(line1_timestamp,line1_old_state,where='post', label='HV line 1 old state')
        plt.plot(line1_timestamp,line1_old_state, 'C0o',alpha=0.5)
        plt.xlabel('Time -T0 (s)')
        plt.ylabel('State (0: OFF, 1: ON)')

        plt.legend()
        plt.subplot(414)
        plt.step(line1_timestamp,line1_new_state,where='post', label='HV line 1 new state')
        plt.plot(line1_timestamp,line1_new_state, 'C1o',alpha=0.5)
        plt.xlabel('Time -T0 (s)')
        plt.ylabel('State (0: OFF, 1: ON)')
        plt.legend()

        plt.show()
        







            
