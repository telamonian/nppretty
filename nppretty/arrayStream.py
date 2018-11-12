from .formatArray import *

__all__ = ['ArrayStream']

class ArrayStream(object):
    def __init__(self, path, mode='a', name='array', **kwargs):
        self.f = None
        self.open(path=path, mode=mode, name=name, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.f.write(']\n')
        self.f.close()
        self.f = None

    def open(self, path, mode='a', name='array', **kwargs):
        if self.f is not None:
            self.close()

        self.f = open(str(path), mode, **kwargs)
        self.f.write('%s = [\n' % name)

    def write(self, arr, end=None, outerbrackets=False, **kwargs):
        if end is None:
            end = ',\n' if arr.ndim < 2 else '\n'

        fmt = formatArrayAsArray(arr, outerbrackets=outerbrackets, **kwargs)
        self.f.write(fmt + end)
