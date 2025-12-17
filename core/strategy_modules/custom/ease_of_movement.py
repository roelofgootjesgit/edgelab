"""
Ease of Movement (EMV)
=======================

Richard Arms' Ease of Movement - price movement efficiency.

Formula:
Distance = ((High + Low) / 2) - ((High[1] + Low[1]) / 2)
Box Ratio = (Volume / 100,000,000) / (High - Low)
EMV = Distance / Box Ratio
EMV Smoothed = SMA(EMV, period)

Features:
- Relates price movement to volume
- Positive = easy upward movement
- Negative = easy downward movement
- Large values = efficient moves
- Zero line crosses signal trends
- Smoothing for clearer signals

Entry Logic:
- LONG: EMV > 0 AND rising
- SHORT: EMV < 0 AND falling

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class EaseOfMovementModule(BaseModule):
    """Ease of Movement indicator module"""
    
    @property
    def name(self) -> str:
        return "Ease of Movement"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Ease of Movement - price movement efficiency vs volume"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 14,
                    "description": "SMA smoothing period (typical: 14)"
                },
                "divisor": {
                    "type": "number",
                    "minimum": 1,
                    "maximum": 1000000000,
                    "default": 100000000,
                    "description": "Volume divisor for scaling"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Ease of Movement"""
        period = config.get('period', 14)
        divisor = config.get('divisor', 100000000)
        
        # Distance moved (midpoint change)
        mid_point = (data['high'] + data['low']) / 2
        mid_point_prev = mid_point.shift(1)
        distance = mid_point - mid_point_prev
        
        # Box ratio (volume relative to range)
        high_low = data['high'] - data['low']
        high_low = high_low.replace(0, np.nan)  # Avoid division by zero
        box_ratio = (data['volume'] / divisor) / high_low
        
        # EMV (raw)
        emv_raw = distance / box_ratio.replace(0, np.nan)
        
        # Smooth with SMA
        emv = emv_raw.rolling(window=period).mean()
        
        # Add to dataframe
        data[f'emv_{period}'] = emv
        data[f'emv_{period}_raw'] = emv_raw
        
        # EMV state
        data[f'emv_{period}_positive'] = emv > 0
        data[f'emv_{period}_rising'] = emv > emv.shift(1)
        
        # Zero line crosses
        data[f'emv_{period}_cross_up'] = (emv > 0) & (emv.shift(1) <= 0)
        data[f'emv_{period}_cross_down'] = (emv < 0) & (emv.shift(1) >= 0)
        
        # Movement strength
        emv_abs = emv.abs()
        emv_avg = emv_abs.rolling(window=period).mean()
        data[f'emv_{period}_strength'] = emv_abs / emv_avg.replace(0, np.nan)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if EMV entry condition is met"""
        period = config.get('period', 14)
        
        emv_col = f'emv_{period}'
        rising_col = f'emv_{period}_rising'
        
        if emv_col not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        
        emv = current[emv_col]
        emv_rising = current[rising_col]
        
        if pd.isna(emv) or pd.isna(emv_rising):
            return False
        
        if direction == 'LONG':
            # EMV positive and rising (easy upward movement)
            return emv > 0 and emv_rising
        else:  # SHORT
            # EMV negative and falling (easy downward movement)
            return emv < 0 and not emv_rising