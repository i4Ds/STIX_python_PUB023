import requests
import pprint
import json
spid=54102   #HK2 packet
start_unix_time=1569830400  #2019-09-09 08:00 am
time_span=600   # 600 seconds
url='http://108.61.164.149/request/packets/spid-tw?spid={}&start={}&span={}'.format(spid, start_unix_time, 
                                                                                    time_span)
print(url)

res=requests.get(url).json()
status=res['status']
packets=res['packets']
print('Number of packets return:{}'.format(len(packets)))
print('First packet header:')
pprint.pprint(packets[0]['header'])



