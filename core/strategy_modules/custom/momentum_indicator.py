"""
Momentum Indicator (MOM)
=========================

Classic momentum oscillator - rate of price change.

Formula:
Momentum = Close - Close[n periods ago]

Or percentage:
Momentum % = ((Close - Close[n]) / Close[n]) * 100

Features:
- Simple rate of change
- Positive = upward momentum
- Negative = downward momentum
- Zero line crosses signal trend changes
- Divergences predict reversals
- Leading indicator

Entry Logic:
- LONG: Momentum > 0 AND rising
- SHORT: Momentum < 0 AND falling

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class MomentumIndicatorModule(BaseModule):
    """Momentum Indicator module"""
    
    @property
    def name(self) -> str:
        return "Momentum"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Momentum Indicator - rate of price change"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200,
                    "default": 14,
                    "description": "Lookback period (typical: 10-14)"
                },
                "use_percentage": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use percentage change instead of absolute"
                },
                "source": {
                    "type": "string",
                    "enum": ["close", "high", "low", "hlc3"],
                    "default": "close",
                    "description": "Price source"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Momentum indicator"""
        period = config.get('period', 14)
        use_pct = config.get('use_percentage', False)
        source = config.get('source', 'close')
        
        # Get source price
        if source == 'hlc3':
            prices = (data['high'] + data['low'] + data['close']) / 3
        elif source == 'high':
            prices = data['high']
        elif source == 'low':
            prices = data['low']
        else:
            prices = data['close']
        
        # Calculate momentum
        if use_pct:
            # Percentage momentum
            price_prev = prices.shift(period)
            mom = ((prices - price_prev) / price_prev.replace(0, np.nan)) * 100
        else:
            # Absolute momentum
            mom = prices - prices.shift(period)
        
        # Add to dataframe
        data[f'mom_{period}'] = mom
        
        # Momentum state
        data[f'mom_{period}_positive'] = mom > 0
        data[f'mom_{period}_rising'] = mom > mom.shift(1)
        
        # Zero line crosses
        data[f'mom_{period}_cross_up'] = (mom > 0) & (mom.shift(1) <= 0)
        data[f'mom_{period}_cross_down'] = (mom < 0) & (mom.shift(1) >= 0)
        
        # Momentum strength (normalized)
        mom_abs = mom.abs()
        mom_avg = mom_abs.rolling(window=period).mean()
        data[f'mom_{period}_strength'] = mom_abs / mom_avg.replace(0, np.nan)
        
        # Add smoothed momentum (SMA)
        mom_sma = mom.rolling(window=int(period / 2)).mean()
        data[f'mom_{period}_sma'] = mom_sma
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Momentum entry condition is met"""
        period = config.get('period', 14)
        
        mom_col = f'mom_{period}'
        rising_col = f'mom_{period}_rising'
        
        if mom_col not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        
        mom = current[mom_col]
        mom_rising = current[rising_col]
        
        if pd.isna(mom) or pd.isna(mom_rising):
            return False
        
        if direction == 'LONG':
            # Momentum positive and rising
            return mom > 0 and mom_rising
        else:  # SHORT
            # Momentum negative and falling
            return mom < 0 and not mom_rising