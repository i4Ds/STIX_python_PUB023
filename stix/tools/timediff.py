import sys
import math
def to_seconds(t):
    try:
        sec=int(t)
    except ValueError:
        n=0
        sec=0
        for field in t.split(':').reverse():
            sec+=int(field)*math.pow(10,n)
            n+=1
    return sec

def convert_back(sec):
    hours=int(sec/3600)
    se=sec-hours*3600
    minutes=int(se/60.)
    seconds=sec%60
    print('{} *  {}:{}:{}'.format(sec, hours,minutes,seconds))
    



def parse(expression):
    if '+' in expression:
        items=expression.split('+')
        convert_back(to_seconds(items[0])+to_seconds(items[1]))

    elif '-' in expression:
        items=expression.split('-')
        convert_back(to_seconds(items[0])-to_seconds(items[1]))




parse(sys.argv[1])
