# nppretty - a pretty printer for Numpy arrays

## Install

Get the repo, `cd` into it, and then run

`pip install .`

## Use

### General purpose array formatting function

`nppretty` provides a general array formatting function, called `formatArray`:
```python
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
```

The default values of the `formatArray` keyword arguments are:
```python
('addbrackets', False),
('delimiter',   ', '),
('fmt',         None),    # if None, fmt is set based on `arr.dtype`
('newline',     '\n'),
('precision',   6),
('squeeze',     True),
('truncate',    None),

('blank',  ' '),
('gutter', '  '),
```

### Specialized array formatting functions

Also provides a number of specialized array formatting functions. These all accept the same keyword arguments as `formatArray(...)`:
```python
def formatArrayAsArray(*arr, **kwargs):
    """Formats array as text that can be copied and pasted directly into python code.
    Might need a vertical mode in your code editor to deal with multiple arrays side-by-side, though.
    """
```

```python
def formatArrayBinary(*arr, **kwargs):
    """Converts all elems to 0 (if elem <= 0) or 1 (if elem > 1) then formats the results as dense as possible.
    """
```

```python
def formatArrayCompact(*arr, **kwargs):
    """Displays only two significant figures from each number and removes all possible whitespace.
    """
```

```python
def formatArrayTex(*arr, **kwargs):
    """Prints arr in a TeX/LaTeX tabular environment compatible format.
    """
```

```python
def formatArrayTrinary(*arr, **kwargs):
    """Converts all elems to -1 (if elem < 0), 0 (if elem == 0), or 1 (if elem > 1) then formats the results as densely as possible.
    """
```

### Format an array as a visual plot, instead of text

If you have the `seaborn` plotting package installed, a function for formatting an array as an image is also provided:
```python
def heatmapArray(arr, annot=None, ax=None, cbar_ax=None, fmt='.2g', linthresh=None, scale=None, vmin=None, vmax=None, **kwargs):
    """Convenience function for calling `seaborn.heatmap`.
    
    :scale: can be one of (None, 'log', 'symlog'). If set, scales the colormap used for plotting the heatmap appropriately.
    :linthresh: when `scale='symlog'` is passed, the linear threshold is determined automatically. This arg is a manual override.
    
    The rest of the args all get passed directly to `seaborn.heatmap`.
    """
```
