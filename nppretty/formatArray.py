import itertools
import numpy as np
from six import BytesIO
import types

# optional support for seaborn heatmap to visualize arrays
_hasSeaborn = False
try:
    import seaborn as sns
    _hasSeaborn = True

    # import some matplotlib stuff to help with the seaborn heatmap
    from matplotlib.colors import LogNorm, Normalize, SymLogNorm
except ImportError:
    pass

__all__ = ['formatArray', 'formatArrayAsArray', 'formatArrayBinary', 'formatArrayCompact', 'formatArrayTex',
           'formatArrayTrinary']

if _hasSeaborn:
    __all__ += ['heatmapArray']

def _coerceArray(array):
    """Basically the same thing as np.asanyarray, but also appropriately coerces generators into arrays
    """
    if isinstance(array, types.GeneratorType):
        return np.asanyarray(tuple(array))
    else:
        return np.asanyarray(array)

def _formatArray(arr, addbrackets, delimiter, fmt, newline, outerbrackets, precision, squeeze, truncate):
    """Private func that does the heavy needed by formatArray on a single array at a time.
    """
    # figure out proper bracket characters
    if isinstance(addbrackets, str):
        b = itertools.cycle(addbrackets)
        leftBrac,rightBrac,leftInsideBrac,rightInsideBrac = (next(b) for i in range(4))
        rightInsideBrac += ','
    else:
        leftBrac,rightBrac,leftInsideBrac,rightInsideBrac = '[',']','[','],'

    # coerce appropriate sequence types (like list) to an actual numpy array
    arr = _coerceArray(arr)

    # determine if the array is empty
    empty = not arr.shape

    # squeeze arr, if requested.
    if squeeze and not empty and (np.prod(arr.shape) <= np.max(arr.shape)):
        # no more than 1 element of shape was greater than 1.
        arr = arr.flat

        # for some reason, np.savetxt inserts newline in between each value instead of delimiter for flat arrays. Fix this
        newline = delimiter
        delimiter = None

    elif addbrackets:
        # if requested (and the array is not flat), ensure that the proper internal brackets get inserted by modifying the delimiter
        if not newline.startswith(rightInsideBrac): newline = rightInsideBrac + newline
        if not newline.endswith(leftInsideBrac): newline = newline + leftInsideBrac

    # pick a default format based on whether or not the array is of a floating point type
    if fmt is None:
        try:
            dtype = arr.dtype
        except AttributeError:
            # flatiters don't have dtypes, but their .base does
            dtype = arr.base.dtype

        if issubclass(dtype.type, (float, np.floating)):
            fmt = ('%%.%dg' % precision)
        elif issubclass(dtype.type, (int, np.integer)):
            fmt = '%d'
        else:
            fmt = '%s'

    # initialize a BytesIO (numpy doesn't play nice with StringIO)
    arrIO = BytesIO()

    if not empty:
        np.savetxt(arrIO, arr[slice(None, truncate)], fmt=fmt, newline=newline, delimiter=delimiter)
    else:
        arrIO.write(b'')
    arFmt = arrIO.getvalue().decode('utf-8')

    if addbrackets:
        try:
            shape = arr.shape
        except AttributeError:
            # flatiters don't have a shape/size, but their .base does
            shape = (arr.base.size,)

        # the test for the extra newline substr covers edge cases that pop up (when eg. squeeze==True)
        if arFmt.endswith(newline):
            arFmt = arFmt[:-len(newline)]

        # add double enclosing backets
        arFmt = (len(shape) - 1)*leftInsideBrac + arFmt + (len(shape) - 1)*rightInsideBrac
        if outerbrackets:
            arFmt = leftBrac + arFmt + rightBrac

    return arFmt

def _joinFormattedArrays(arrFmt, newline, squeeze, blank, gutter):
    """Joins a list of pre-formatted arrays together and returns a single `str`.
    """
    # deal with edge cases
    if len(arrFmt)==0:
        return ''
    elif len(arrFmt)==1:
        return arrFmt[0]

    # handle 2 or more pre-formatted arrays
    if squeeze:
        # just cat the 1D array representations together
        return gutter.join(arrFmt)
    else:
        # split up the formatted arrays at their newline chars
        arrFmtSplit = [arFmt.split(newline) for arFmt in arrFmt]

        # figure out the line count of the array with the most lines
        linecount = max(len(arFmtSplit) for arFmtSplit in arrFmtSplit)

        # add spaces such that each array is formatted as a rectangle, add extra lines so that all of the rectangles are the same height, then cat the arrays together line-by-line (separated by delimiterMulti)
        arrFmtCat = newline.join(gutter.join(lines) for lines in zip(*(_formatArraySplitWiden(arFmtSplit=arFmtSplit, blank=blank, linecount=linecount) for arFmtSplit in arrFmtSplit)))

        return arrFmtCat

def _formatArraySplitWiden(arFmtSplit, blank, linecount):
    """Private func that gets iterated over as part of enjambing multiple formatted arrays side-by-side.
    Adds spaces such that the mutable sequence arFmtSplit (if joined by `\n`) will print as a rectangle.
    Optionally also extends the "height" of the rectangle to match lineCount. If lineCount <= len(arFmtSplit), nothing happens.
    """
    width = max(len(line) for line in arFmtSplit)
    for i in range(len(arFmtSplit)):
        arFmtSplit[i] = arFmtSplit[i].ljust(width)

    if linecount > len(arFmtSplit):
        arFmtSplit.extend([blank*width]*(linecount - len(arFmtSplit)))

    return arFmtSplit

def formatArray(*arr, **kwargs):
    """Converts array(s) into a parsimonious string. Useful for saving a concise version of an array as a plaintext list.
    Accepts a number of different optional keyword arguments:

    :addbrackets: boolean or sequence of (leftBrac,rightBrac,leftInsideBrac,rightInsideBrac)
    :delimiter: separator between individual elements in an array
    :fmt: format string use to convert individual elements of the array
    :newline: separator between compound elements (eg rows) in a single array
    :precision: the precision with which numbers are printed. Only has an effect if `fmt` is not used
    :squeeze: if True, flatten arrays with one or less non-trivial dimensions before formatting them. For example, (2,1) and (1,1,2) would be treated as 1D.
    :truncate: if set, only format first `truncate` elements of array

    There are some specialized keyword args for formatting multiple arrays together:

    :blank: vertical separator between different arrays
    :gutter: horizontal separator between different arrays
    """
    # ensure that default values are used for any kwarg that is set to None (by removing them)
    for key in list(kwargs.keys()):
        if kwargs[key] is None:
            kwargs.pop(key)
    
    # use kwargsDefault for py2 compatibility (keyword args not allowed after `*arr` in py2)
    kwargsDefault = dict([
        ('addbrackets', False),
        ('delimiter',   ', '),
        ('fmt',         None),    # if None, fmt is set based on `arr.dtype`
        ('newline',     '\n'),
        ('precision',   6),
        ('squeeze',     True),
        ('outerbrackets', False),
        ('truncate',    None),

        ('blank',  ' '),
        ('gutter', '  '),
    ])

    # override default kwargs with passed in kwargs
    kwargsDefault.update(kwargs)

    # call the internal func that does the heavy lifting
    faKwargs = dict((k, kwargsDefault[k])
                    for k in ('addbrackets', 'delimiter', 'fmt', 'newline', 'precision', 'squeeze', 'outerbrackets', 'truncate'))
    arrFmt = [_formatArray(arr=ar, **faKwargs)
              for ar in arr]

    # _formatArray returns a list of formatted arrays, join them into a single string
    jfaKwargs = dict((k, kwargsDefault[k])
                    for k in ('newline', 'squeeze', 'blank', 'gutter'))
    return _joinFormattedArrays(arrFmt, **jfaKwargs)

def formatArrayAsArray(*arr, **kwargs):
    """Formats array as text that can be copied and pasted directly into python code.
    Might need a vertical mode in your code editor to deal with multiple arrays side-by-side, though.
    """
    # default arg vals are specified a little weird for py2 compatibility
    defaults = dict([
        ('addbrackets', True),
        ('delimiter',   ', '),
        ('newline',     '\n'),
    ])
    
    # override defaults with any kwargs that have been explicitly set
    defaults.update(kwargs)
    
    return formatArray(*arr, **defaults)

def formatArrayBinary(*arr, **kwargs):
    """Converts all elems to 0 (if elem <= 0) or 1 (if elem > 1) then formats the results as dense as possible.
    """
    defaults = dict([
        ('delimiter', ','),
        ('fmt',       '%d'),
    ])
    defaults.update(kwargs)
    
    arrBinary = [(ar > 0).astype(int) for ar in arr]
    return formatArray(*arrBinary, **defaults)

def formatArrayCompact(*arr, **kwargs):
    """Displays only two significant figures from each number and removes all possible whitespace.
    """
    defaults = dict([
        ('delimiter', ','),
        ('fmt',       '%.2g'),
        ('squeeze',   False),
    ])
    defaults.update(kwargs)
    
    return formatArray(*arr, **defaults)

def formatArrayTex(*arr, **kwargs):
    """Prints arr in a TeX/LaTeX tabular environment compatible format.
    """
    defaults = dict([
        ('delimiter', ' \t& '),
        ('fmt',       '%2.3g'),
        ('newline',   ' \\\\\n'),
        ('squeeze',   False),
    ])
    defaults.update(kwargs)

    return formatArray(*arr, **defaults)

def formatArrayTrinary(*arr, **kwargs):
    """Converts all elems to -1 (if elem < 0), 0 (if elem == 0), or 1 (if elem > 1) then formats the results as densely as possible.
    """
    defaults = dict([
        ('delimiter', ','),
        ('fmt',       '%1d'),
        ('newline',   '\n'),
        ('squeeze',   False),
    ])
    defaults.update(kwargs)

    arrTrinary = [(ar > 0).astype(int) - (ar < 0).astype(int) for ar in arr]
    return formatArray(*arrTrinary, **defaults)

if _hasSeaborn:
    def heatmapArray(arr, annot=None, ax=None, cbar_ax=None, fmt='.2g', linthresh=None, scale=None, vmin=None, vmax=None, **kwargs):
        """Convenience function for calling `seaborn.heatmap`.

        :scale: can be one of (None, 'log', 'symlog'). If set, scales the colormap used for plotting the heatmap appropriately.
        :linthresh: when `scale='symlog'` is passed, the linear threshold is determined automatically. This arg is a manual override.

        The rest of the args all get passed directly to `seaborn.heatmap`.
        """
        if scale=='log':
            kwargs['norm'] = LogNorm()
        elif scale=='symlog':
            if linthresh is None:
                linthresh = np.min(np.abs(arr))

            kwargs['norm'] = SymLogNorm(linthresh)
        else:
            kwargs['norm'] = Normalize()

        ax = sns.heatmap(arr, annot=annot, ax=ax, cbar_ax=cbar_ax, fmt=fmt, vmin=vmin, vmax=vmax, **kwargs)
        from matplotlib import colorbar
        return ax
