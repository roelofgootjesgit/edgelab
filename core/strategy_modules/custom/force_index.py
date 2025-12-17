"""
Force Index
===========

Alexander Elder's Force Index - measures buying/selling pressure.

Formula:
Force Index = (Close - Close[1]) * Volume
Force Index (smoothed) = EMA(Force Index, period)

Features:
- Combines price change with volume
- Positive = buying pressure
- Negative = selling pressure
- Divergences signal reversals
- Zero line crosses for entries
- Smoothing reduces noise

Entry Logic:
- LONG: Force Index > 0 AND rising
- SHORT: Force Index < 0 AND falling

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class ForceIndexModule(BaseModule):
    """Force Index indicator module"""
    
    @property
    def name(self) -> str:
        return "Force Index"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Alexander Elder's Force Index - price × volume momentum"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 13,
                    "description": "EMA smoothing period (typical: 13)"
                },
                "use_raw": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use raw FI (true) or smoothed (false)"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Force Index"""
        period = config.get('period', 13)
        use_raw = config.get('use_raw', False)
        
        # Calculate raw Force Index
        price_change = data['close'] - data['close'].shift(1)
        fi_raw = price_change * data['volume']
        
        # Smooth with EMA if requested
        if use_raw:
            fi = fi_raw
        else:
            fi = fi_raw.ewm(span=period, adjust=False).mean()
        
        # Add to dataframe
        data[f'fi_{period}'] = fi
        data[f'fi_{period}_raw'] = fi_raw
        
        # Force Index state
        data[f'fi_{period}_positive'] = fi > 0
        data[f'fi_{period}_rising'] = fi > fi.shift(1)
        
        # Zero line crosses
        data[f'fi_{period}_cross_up'] = (fi > 0) & (fi.shift(1) <= 0)
        data[f'fi_{period}_cross_down'] = (fi < 0) & (fi.shift(1) >= 0)
        
        # Strength (normalized by recent average)
        fi_abs = fi.abs()
        fi_avg = fi_abs.rolling(window=period).mean()
        data[f'fi_{period}_strength'] = fi_abs / fi_avg.replace(0, np.nan)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Force Index entry condition is met"""
        period = config.get('period', 13)
        
        fi_col = f'fi_{period}'
        rising_col = f'fi_{period}_rising'
        
        if fi_col not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        
        fi = current[fi_col]
        fi_rising = current[rising_col]
        
        if pd.isna(fi) or pd.isna(fi_rising):
            return False
        
        if direction == 'LONG':
            # Force Index positive and rising (buying pressure)
            return fi > 0 and fi_rising
        else:  # SHORT
            # Force Index negative and falling (selling pressure)
            return fi < 0 and not fi_rising