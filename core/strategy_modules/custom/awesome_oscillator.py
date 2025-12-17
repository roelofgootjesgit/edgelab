"""
Awesome Oscillator (AO)
========================

Bill Williams' Awesome Oscillator - momentum indicator based on SMA difference.

Formula:
AO = SMA(Median Price, 5) - SMA(Median Price, 34)

Where:
- Median Price = (High + Low) / 2
- Green bars = AO increasing (momentum up)
- Red bars = AO decreasing (momentum down)

Features:
- Simple momentum measurement
- Shows acceleration/deceleration
- Crosses zero line for trend changes
- Twin peaks pattern (divergence)
- Saucer pattern (reversal)

Entry Logic:
- LONG: AO > 0 AND AO rising (green bars)
- SHORT: AO < 0 AND AO falling (red bars)

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class AwesomeOscillatorModule(BaseModule):
    """Awesome Oscillator indicator module"""
    
    @property
    def name(self) -> str:
        return "Awesome Oscillator"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Bill Williams' Awesome Oscillator - momentum from SMA difference"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "fast_period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 50,
                    "default": 5,
                    "description": "Fast SMA period (typical: 5)"
                },
                "slow_period": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 200,
                    "default": 34,
                    "description": "Slow SMA period (typical: 34)"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Awesome Oscillator"""
        fast = config.get('fast_period', 5)
        slow = config.get('slow_period', 34)
        
        # Median price
        median = (data['high'] + data['low']) / 2
        
        # Calculate AO
        sma_fast = median.rolling(window=fast).mean()
        sma_slow = median.rolling(window=slow).mean()
        
        ao = sma_fast - sma_slow
        
        # Add to dataframe
        data['ao'] = ao
        data['ao_rising'] = ao > ao.shift(1)
        data['ao_color'] = data['ao_rising'].map({True: 'green', False: 'red'})
        
        # Zero line crosses
        data['ao_above_zero'] = ao > 0
        data['ao_cross_up'] = (ao > 0) & (ao.shift(1) <= 0)
        data['ao_cross_down'] = (ao < 0) & (ao.shift(1) >= 0)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if AO entry condition is met"""
        if 'ao' not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        prev = data.iloc[index - 1]
        
        ao = current['ao']
        ao_rising = current['ao_rising']
        
        if pd.isna(ao) or pd.isna(ao_rising):
            return False
        
        if direction == 'LONG':
            # AO above zero and rising (green bars)
            return ao > 0 and ao_rising
        else:  # SHORT
            # AO below zero and falling (red bars)
            return ao < 0 and not ao_rising