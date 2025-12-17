"""
trend indicators
================

QuantMetrics indicator modules for trend analysis
"""

from .adx import ADXModule
from .parabolic_sar import ParabolicSARModule
from .supertrend import SuperTrendModule
from .aroon import AroonModule
from .ichimoku import IchimokuModule
from .linear_regression import LinearRegressionModule
from .zigzag import ZigzagModule
from .chande_kroll import ChandeKrollModule

__all__ = [
    'ADXModule',
    'ParabolicSARModule', 
    'SuperTrendModule',
    'AroonModule',
    'IchimokuModule',
    'LinearRegressionModule',
    'ZigzagModule',
    'ChandeKrollModule'
]