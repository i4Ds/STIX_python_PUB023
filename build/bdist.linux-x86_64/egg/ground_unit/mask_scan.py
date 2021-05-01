from detector import *
ON_DEMAND_READOUT_TC='ZIX39005 {{PIX00248 {detector_mask} }} {{PIX00053  {pixel_mask} }} {{PIX00054 100}}' 
#Execute on-demand ASIC ADC readout
#PIX00248 - Detector mask
#PIX00053 - Channel mas
#PIX00054 - Average count

WAIT_TIME=10
info('#MASK Scan tcl script')


info('Pixel scan:')
detector4_mask=0x00000010
total_time=0
for ch, mask in  enumerate(PIXEL_MASK):
    syslog("detector 4, pixel: {} ".format(ch))
    send_tc(ON_DEMAND_READOUT_TC.format(detector_mask=detector4_mask, pixel_mask=mask))
    wait(10)
    total_time+=10
    

syslog('Detector scan:')
all_pixel_mask=0xffffffff
for det, mask in  DETECTOR_MASKS.items():
    syslog('detector: {}'.format( det+1))
    send_tc(ON_DEMAND_READOUT_TC.format(detector_mask=mask, pixel_mask=all_pixel_mask))
    wait(10)
    total_time+=10
    
info("Total time to finish:{}".format( total_time))



