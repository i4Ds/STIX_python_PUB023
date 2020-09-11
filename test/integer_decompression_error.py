def decompress(x, S, K, M):
    """
    decompress x 
    S, K, M
    """
    if S + K + M > 8 or S not in (0, 1) or K > 7 or M > 7:
        logger.warning('Invalid SKM values: {}{}{}'.format(S, K, M))
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
        return x
    mask1 = (1 << M) - 1
    mask2 = (1 << M)
    mantissa1 = x & mask1
    exponent = (x >> M) - 1
    # number of shifted bits
    mantissa2 = mask2 | mantissa1  #add 1 before mantissa
    low = mantissa2 << exponent  #minimal possible value
    high = low | ((1 << exponent) - 1)  #maximal possible value
    mean = (low + high) >> 1  #mean value

    if mean > 1e8:
        return float(mean)

    return sign * mean

