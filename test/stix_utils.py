from matplotlib import pyplot as plt


def compression_decode(in_value, M):
    #k m should k+m<8  k<=7,m<=7
    temp = 1 << (M + 1)
    if in_value < temp:
        return in_value
    mask = (1 << M) - 1
    mantissa = in_value & mask
    exponent = in_value >> M
    return mantissa << (exponent - 1)


def compression_encode(in_val, M, K):
    if in_val < (1 << (M + 1)):
        return in_val
    exponent = 1
    #while (in_val >  ((1 << (M + 1)) - 1)):
    while in_val >= (1 << (M + 1)):
        in_val >>= 1
        exponent += 1

    if exponent > int((1 << K) - 1):
        return 0xff

    mantissa = in_val & ((1 << M) - 1)
    out_val = mantissa + (exponent << M)
    return out_val


def plot(M, K):
    x = range(0, 1000)
    y = []
    for i in x:
        code = compression_encode(i, M, K)
        y.append(compression_decode(code, M))
    plt.subplot(3, 2, M)
    plt.plot(x, y)
    plt.title('M = {}, K={}'.format(M, K))
    plt.xlabel('Input value')
    plt.ylabel('Reproduced value')


if __name__ == '__main__':
    for M in range(1, 7):
        K = 8 - M
        plot(M, K)
    plt.tight_layout()
    plt.show()
    #plt.savefig('compression_test.pdf')
