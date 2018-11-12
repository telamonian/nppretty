from nppretty import *

if __name__=='__main__':
    import numpy as np

    with ArrayStream('arraystream.txt', 'w', name='arr1D') as f:
        for i in range(10):
            arr = np.arange(10*i, 10*(i + 1))
            f.write(arr)

    with ArrayStream('arraystream.txt', name='arr2D') as f:
        for i in range(10):
            arr = np.arange(10*i, 10*(i + 1))
            f.write(arr.reshape(2,5))
