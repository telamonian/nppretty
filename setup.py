#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='nppretty',
    description='Pretty printer for numpy arrays.',
    long_description="""Pretty printer for numpy arrays. Among other things, 
    provides a `formatArrayTex` function for converting a numpy array to a 
    TeX/LaTeX table. Allows for more control over things like spacing, 
    delimiters, and brackets than the built-in `numpy.set_printoptions`.
    """,
    version='1.0.0',

    author='Max Klein',
    url='https://github.com/telamonian/nppretty',
    license='BSD',
    platforms="Linux, Mac OS X, Windows",
    keywords=['Array', 'Formatting', 'Printing', 'Numpy'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    install_requires = [
        'numpy',
        'six',
    ],
    extras_require = {
        'heatmap': ['seaborn'],
    },

    packages=find_packages(),
)
