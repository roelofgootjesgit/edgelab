"""
Choppiness Index
================

Measures market choppiness vs trending behavior.

Formula:
CHOP = 100 * LOG10(SUM(ATR, n) / (MAX(High, n) - MIN(Low, n))) / LOG10(n)

Where:
- n = period (typically 14)
- Values 0-38.2: Strong trend
- Values 38.2-61.8: Choppy/ranging
- Values 61.8-100: Very choppy

Features:
- Identifies trending vs ranging markets
- Not directional (doesn't predict direction)
- Low CHOP = good for trend strategies
- High CHOP = good for mean reversion
- Use to filter trades

Entry Logic:
- LONG: CHOP < 38.2 (trending) AND price trending up
- SHORT: CHOP < 38.2 (trending) AND price trending down

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class ChoppinessModule(BaseModule):
    """Choppiness Index indicator module"""
    
    @property
    def name(self) -> str:
        return "Choppiness Index"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Choppiness Index - measures trending vs ranging market"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 200,
                    "default": 14,
                    "description": "Lookback period (typical: 14)"
                },
                "trend_threshold": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "default": 38.2,
                    "description": "Below = trending (typical: 38.2)"
                },
                "chop_threshold": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "default": 61.8,
                    "description": "Above = very choppy (typical: 61.8)"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Choppiness Index"""
        period = config.get('period', 14)
        
        # Calculate ATR
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift(1))
        low_close = np.abs(data['low'] - data['close'].shift(1))
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr_sum = tr.rolling(window=period).sum()
        
        # Calculate high-low range
        highest_high = data['high'].rolling(window=period).max()
        lowest_low = data['low'].rolling(window=period).min()
        range_hl = highest_high - lowest_low
        
        # Avoid division by zero
        range_hl = range_hl.replace(0, np.nan)
        
        # Calculate CHOP
        chop = 100 * np.log10(atr_sum / range_hl) / np.log10(period)
        
        # Add to dataframe
        data[f'chop_{period}'] = chop
        
        # Market state
        trend_threshold = config.get('trend_threshold', 38.2)
        chop_threshold = config.get('chop_threshold', 61.8)
        
        data[f'chop_{period}_trending'] = chop < trend_threshold
        data[f'chop_{period}_ranging'] = (chop >= trend_threshold) & (chop <= chop_threshold)
        data[f'chop_{period}_choppy'] = chop > chop_threshold
        
        # Price trend (for entry filtering)
        sma = data['close'].rolling(window=period).mean()
        data[f'chop_{period}_price_uptrend'] = data['close'] > sma
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Choppiness entry condition is met"""
        period = config.get('period', 14)
        
        chop_col = f'chop_{period}'
        trending_col = f'chop_{period}_trending'
        uptrend_col = f'chop_{period}_price_uptrend'
        
        if chop_col not in data.columns:
            return False
        
        if index < 1:
            return False
        
        current = data.iloc[index]
        
        trending = current[trending_col]
        price_uptrend = current[uptrend_col]
        
        if pd.isna(trending):
            return False
        
        # Only enter in trending markets
        if not trending:
            return False
        
        if direction == 'LONG':
            # Trending market with price uptrend
            return price_uptrend
        else:  # SHORT
            # Trending market with price downtrend
            return not price_uptrend