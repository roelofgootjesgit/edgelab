"""
Accelerator Oscillator (AC)
============================

Bill Williams' Accelerator Oscillator - acceleration/deceleration of momentum.

Formula:
AC = AO - SMA(AO, 5)

Where:
- AO = Awesome Oscillator
- Measures acceleration of momentum
- Green bars = AC rising
- Red bars = AC falling

Features:
- Earlier signal than AO
- Shows momentum acceleration
- Detects trend changes faster
- Used with AO for confirmation
- Part of Bill Williams' system

Entry Logic:
- LONG: AC > 0 AND AC rising (2+ green bars)
- SHORT: AC < 0 AND AC falling (2+ red bars)

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class AcceleratorOscillatorModule(BaseModule):
    """Accelerator Oscillator indicator module"""
    
    @property
    def name(self) -> str:
        return "Accelerator Oscillator"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Bill Williams' Accelerator - momentum acceleration indicator"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ao_fast": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 50,
                    "default": 5,
                    "description": "AO fast period"
                },
                "ao_slow": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 200,
                    "default": 34,
                    "description": "AO slow period"
                },
                "signal_period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 20,
                    "default": 5,
                    "description": "AC signal period (typical: 5)"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Accelerator Oscillator"""
        ao_fast = config.get('ao_fast', 5)
        ao_slow = config.get('ao_slow', 34)
        signal = config.get('signal_period', 5)
        
        # Calculate AO first
        median = (data['high'] + data['low']) / 2
        sma_fast = median.rolling(window=ao_fast).mean()
        sma_slow = median.rolling(window=ao_slow).mean()
        ao = sma_fast - sma_slow
        
        # Calculate AC
        ao_signal = ao.rolling(window=signal).mean()
        ac = ao - ao_signal
        
        # Add to dataframe
        data['ac'] = ac
        data['ac_rising'] = ac > ac.shift(1)
        data['ac_color'] = data['ac_rising'].map({True: 'green', False: 'red'})
        
        # Count consecutive bars
        data['ac_green_count'] = 0
        data['ac_red_count'] = 0
        
        green_count = 0
        red_count = 0
        
        for i in range(len(data)):
            if i == 0:
                continue
            
            if data['ac_rising'].iloc[i]:
                green_count += 1
                red_count = 0
            else:
                red_count += 1
                green_count = 0
            
            data.loc[data.index[i], 'ac_green_count'] = green_count
            data.loc[data.index[i], 'ac_red_count'] = red_count
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if AC entry condition is met"""
        if 'ac' not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        
        ac = current['ac']
        green_count = current['ac_green_count']
        red_count = current['ac_red_count']
        
        if pd.isna(ac):
            return False
        
        if direction == 'LONG':
            # AC above zero with 2+ green bars
            return ac > 0 and green_count >= 2
        else:  # SHORT
            # AC below zero with 2+ red bars
            return ac < 0 and red_count >= 2