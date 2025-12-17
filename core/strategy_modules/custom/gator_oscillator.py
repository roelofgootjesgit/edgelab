"""
Gator Oscillator
================

Bill Williams' Gator Oscillator - visualizes Alligator convergence/divergence.

Formula:
Based on Alligator indicator (3 SMAs):
- Jaw (blue) = SMMA(Median, 13) shifted 8 bars
- Teeth (red) = SMMA(Median, 8) shifted 5 bars  
- Lips (green) = SMMA(Median, 5) shifted 3 bars

Upper Bar = |Jaw - Teeth|
Lower Bar = |Teeth - Lips|

Features:
- Shows Alligator line distance
- Bars increase = Alligator opening (trending)
- Bars decrease = Alligator closing (ranging)
- Green bars = increasing
- Red bars = decreasing
- Used with Alligator for confirmation

Entry Logic:
- LONG: Both bars increasing (Alligator opening) AND Lips > Teeth > Jaw
- SHORT: Both bars increasing (Alligator opening) AND Lips < Teeth < Jaw

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class GatorOscillatorModule(BaseModule):
    """Gator Oscillator indicator module"""
    
    @property
    def name(self) -> str:
        return "Gator Oscillator"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Bill Williams' Gator - Alligator convergence/divergence"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "jaw_period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 200,
                    "default": 13,
                    "description": "Jaw (blue line) period"
                },
                "jaw_offset": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 50,
                    "default": 8,
                    "description": "Jaw shift forward"
                },
                "teeth_period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 200,
                    "default": 8,
                    "description": "Teeth (red line) period"
                },
                "teeth_offset": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 50,
                    "default": 5,
                    "description": "Teeth shift forward"
                },
                "lips_period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 200,
                    "default": 5,
                    "description": "Lips (green line) period"
                },
                "lips_offset": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 50,
                    "default": 3,
                    "description": "Lips shift forward"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Gator Oscillator"""
        jaw_period = config.get('jaw_period', 13)
        jaw_offset = config.get('jaw_offset', 8)
        teeth_period = config.get('teeth_period', 8)
        teeth_offset = config.get('teeth_offset', 5)
        lips_period = config.get('lips_period', 5)
        lips_offset = config.get('lips_offset', 3)
        
        # Median price
        median = (data['high'] + data['low']) / 2
        
        # Calculate SMMA (Smoothed MA - Wilder's)
        def smma(series, period):
            alpha = 1.0 / period
            return series.ewm(alpha=alpha, adjust=False).mean()
        
        jaw = smma(median, jaw_period).shift(jaw_offset)
        teeth = smma(median, teeth_period).shift(teeth_offset)
        lips = smma(median, lips_period).shift(lips_offset)
        
        # Gator bars (absolute differences)
        upper_bar = np.abs(jaw - teeth)
        lower_bar = np.abs(teeth - lips)
        
        # Add to dataframe
        data['gator_jaw'] = jaw
        data['gator_teeth'] = teeth
        data['gator_lips'] = lips
        data['gator_upper'] = upper_bar
        data['gator_lower'] = lower_bar
        
        # Bar direction (increasing/decreasing)
        data['gator_upper_rising'] = upper_bar > upper_bar.shift(1)
        data['gator_lower_rising'] = lower_bar > lower_bar.shift(1)
        
        # Alligator state
        data['gator_uptrend'] = (lips > teeth) & (teeth > jaw)
        data['gator_downtrend'] = (lips < teeth) & (teeth < jaw)
        data['gator_opening'] = data['gator_upper_rising'] & data['gator_lower_rising']
        data['gator_closing'] = ~data['gator_upper_rising'] & ~data['gator_lower_rising']
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Gator entry condition is met"""
        if 'gator_upper' not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        
        opening = current['gator_opening']
        uptrend = current['gator_uptrend']
        downtrend = current['gator_downtrend']
        
        if pd.isna(opening):
            return False
        
        # Only enter when Alligator is opening (trending)
        if not opening:
            return False
        
        if direction == 'LONG':
            # Alligator opening in uptrend
            return uptrend
        else:  # SHORT
            # Alligator opening in downtrend
            return downtrend