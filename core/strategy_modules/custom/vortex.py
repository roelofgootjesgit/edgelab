"""
Vortex Indicator (VI)
=====================

Identifies trend direction and strength based on vortex movement.

Formula:
VI+ = SUM(|High - Low[1]|, n) / SUM(True Range, n)
VI- = SUM(|Low - High[1]|, n) / SUM(True Range, n)

Where:
- n = period (typically 14)
- VI+ above VI- = uptrend
- VI- above VI+ = downtrend
- Crossovers signal trend changes

Features:
- Two oscillating lines
- Crossovers signal trends
- Distance measures trend strength
- Leading indicator
- Works in trending markets

Entry Logic:
- LONG: VI+ crosses above VI-
- SHORT: VI- crosses above VI+

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class VortexModule(BaseModule):
    """Vortex Indicator module"""
    
    @property
    def name(self) -> str:
        return "Vortex Indicator"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Vortex Indicator - trend direction and strength"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 200,
                    "default": 14,
                    "description": "VI period (typical: 14)"
                },
                "min_distance": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 0.5,
                    "default": 0.02,
                    "description": "Minimum VI distance for entry"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Vortex Indicator"""
        period = config.get('period', 14)
        
        # Vortex movements
        vm_plus = np.abs(data['high'] - data['low'].shift(1))
        vm_minus = np.abs(data['low'] - data['high'].shift(1))
        
        # True Range
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift(1))
        low_close = np.abs(data['low'] - data['close'].shift(1))
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # Calculate VI+ and VI-
        vm_plus_sum = vm_plus.rolling(window=period).sum()
        vm_minus_sum = vm_minus.rolling(window=period).sum()
        tr_sum = tr.rolling(window=period).sum()
        
        # Avoid division by zero
        tr_sum = tr_sum.replace(0, np.nan)
        
        vi_plus = vm_plus_sum / tr_sum
        vi_minus = vm_minus_sum / tr_sum
        
        # Add to dataframe
        data[f'vi_plus_{period}'] = vi_plus
        data[f'vi_minus_{period}'] = vi_minus
        
        # VI difference (trend strength)
        data[f'vi_diff_{period}'] = vi_plus - vi_minus
        
        # Trend state
        data[f'vi_{period}_uptrend'] = vi_plus > vi_minus
        
        # Crossovers
        data[f'vi_{period}_cross_up'] = (vi_plus > vi_minus) & (vi_plus.shift(1) <= vi_minus.shift(1))
        data[f'vi_{period}_cross_down'] = (vi_plus < vi_minus) & (vi_plus.shift(1) >= vi_minus.shift(1))
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Vortex entry condition is met"""
        period = config.get('period', 14)
        min_distance = config.get('min_distance', 0.02)
        
        vi_plus_col = f'vi_plus_{period}'
        vi_minus_col = f'vi_minus_{period}'
        diff_col = f'vi_diff_{period}'
        
        if vi_plus_col not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        prev = data.iloc[index - 1]
        
        vi_plus = current[vi_plus_col]
        vi_minus = current[vi_minus_col]
        vi_diff = current[diff_col]
        
        vi_plus_prev = prev[vi_plus_col]
        vi_minus_prev = prev[vi_minus_col]
        
        if pd.isna(vi_plus) or pd.isna(vi_minus):
            return False
        
        if direction == 'LONG':
            # VI+ crosses above VI- with sufficient distance
            crossed_up = (vi_plus > vi_minus) and (vi_plus_prev <= vi_minus_prev)
            strong_enough = vi_diff > min_distance
            return crossed_up or (vi_plus > vi_minus and strong_enough)
        else:  # SHORT
            # VI- crosses above VI+ with sufficient distance
            crossed_down = (vi_minus > vi_plus) and (vi_minus_prev <= vi_plus_prev)
            strong_enough = vi_diff < -min_distance
            return crossed_down or (vi_minus > vi_plus and strong_enough)