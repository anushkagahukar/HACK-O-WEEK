"""
Admin Building Weekend Dip Analysis Package
============================================
Package for analyzing energy consumption patterns and detecting weekend dips.
"""

__version__ = '1.0.0'
__author__ = 'Energy Analysis Team'

from . import data_loader
from . import clustering
from . import regression
from . import utils

__all__ = ['data_loader', 'clustering', 'regression', 'utils']
