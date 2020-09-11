schemes=[[0,3,5],[0,5,3],[0,4,4],[1,4,3]]
from ROOT import TGraphErrors, TCanvas,TGraph
import matplotlib.pyplot as plt
def to_array(x):
    return array('f',x)
def decompress(x, S, K, M):
    """
    decompress x 
    S, K, M
    """
    if S + K + M > 8 or S not in [0, 1] or K > 7 or M > 7:
        print('Invalid SKM values: {}{}{}'.format(S, K, M))
        return None
    if K == 0 or M == 0:
        return None

    sign = 1
    if S == 1:  #signed
        MSB = x & (1 << 7)
        if MSB != 0:
            sign = -1
        x = x & ((1 << 7) - 1)

    x0 = 1 << (M + 1)
    if x < x0:
        #return [0, 0, 0]
        print('here')
        return [x, 0]
    mask1 = (1 << M) - 1
    mask2 = (1 << M)
    mantissa1 = x & mask1
    exponent = (x >> M) - 1
    # number of shifted bits
    mantissa2 = mask2 | mantissa1  #add 1 before mantissa
    low = mantissa2 << exponent  #minimal possible value
    high = low | ((1 << exponent) - 1)  #maximal possible value
    mean = (low + high) >> 1  #mean value

    diff=abs(high-low)/(2*mean)

    return [sign* mean, diff]
    #return [(high-mean)/ mean,0,0]

#for i in range(0,255):
#    mean,diff=decompress(i, 0, 4, 4)
#    print(i, mean, diff)


x=[[],[],[],[]]
xe=[[],[],[],[]]
y=[[],[],[],[]]
ye=[[],[],[],[]]

plt.subplots(4, 1)
for i in range(0,255):
    for k in range(0,4):
        mean, diff=decompress(i, schemes[k][0], schemes[k][1], schemes[k][2])
        x[k].append(mean)
        y[k].append(diff)
        #ye[k].append(mean-low)
        #xe[k].append(0)

for i in range(0,4):
    label='SKM:'+str(schemes[i])
    #axs[i].errorbar(x[i], y[i],  ye[i], label=label)
    plt.subplot(4,1,i+1)
    if i==3:
        xy=sorted(zip(x[3],y[3]))
        x3=[a[0] for a in xy]
        y3=[a[1] for a in xy]
        plt.plot(x3,y3)

    else:
        plt.plot(x[i], y[i])
        plt.xscale('log')

    plt.title(label)
    plt.xlabel('Decompressed value')
    plt.ylabel('Max.relative diff.')

plt.tight_layout()
plt.show()
