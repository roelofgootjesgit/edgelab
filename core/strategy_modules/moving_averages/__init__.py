"""
moving_averages indicators
===========================

QuantMetrics indicator modules for moving average analysis
"""

from .wma import WMAModule
from .hma import HMAModule
from .tema import TEMAModule
from .dema import DEMAModule
from .zlema import ZLEMAModule
from .kama import KAMAModule
from .vwma import VWMAModule
from .smma import SMMAModule

__all__ = [
    'WMAModule',
    'HMAModule',
    'TEMAModule',
    'DEMAModule',
    'ZLEMAModule',
    'KAMAModule',
    'VWMAModule',
    'SMMAModule'
]