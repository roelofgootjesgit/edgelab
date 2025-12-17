"""
HMA - Hull Moving Average
==========================

Fast and smooth moving average developed by Alan Hull.
Designed to reduce lag while maintaining smoothness.

Formula:
1. WMA1 = WMA(period/2)
2. WMA2 = WMA(period)
3. Raw HMA = 2*WMA1 - WMA2
4. HMA = WMA(sqrt(period)) of Raw HMA

Features:
- Very low lag
- Excellent smoothness
- Fast response to price changes
- Trend direction detection
- Popular for fast-moving markets

Entry Logic:
- LONG: price > HMA AND HMA rising strongly
- SHORT: price < HMA AND HMA falling strongly
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class HMAModule(BaseModule):
    """Hull Moving Average indicator module"""
    
    @property
    def name(self) -> str:
        return "HMA"
    
    @property
    def category(self) -> str:
        return "moving_averages"
    
    @property
    def description(self) -> str:
        return "Hull Moving Average - fast and smooth, reduced lag"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 500,
                    "default": 20,
                    "description": "HMA period (typical: 9, 16, 20)"
                },
                "source": {
                    "type": "string",
                    "enum": ["close", "open", "high", "low"],
                    "default": "close",
                    "description": "Price source for calculation"
                }
            },
            "required": ["period"]
        }
    
    def _wma(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate WMA helper"""
        def wma_calc(window):
            if len(window) < period:
                return np.nan
            weights = np.arange(1, period + 1)
            return np.sum(weights * window) / weights.sum()
        
        return series.rolling(window=period).apply(wma_calc, raw=True)
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate HMA indicator"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        prices = data[source]
        
        # Calculate WMAs
        half_period = int(period / 2)
        sqrt_period = int(np.sqrt(period))
        
        wma_half = self._wma(prices, half_period)
        wma_full = self._wma(prices, period)
        
        # Raw HMA
        raw_hma = 2 * wma_half - wma_full
        
        # Final HMA
        hma = self._wma(raw_hma, sqrt_period)
        
        # Add to dataframe
        data[f'hma_{period}'] = hma
        
        # Calculate trend strength (rate of change)
        data[f'hma_{period}_rising'] = hma > hma.shift(1)
        data[f'hma_{period}_slope'] = hma - hma.shift(1)
        
        # Distance from price (%)
        data[f'hma_{period}_dist_pct'] = ((prices - hma) / hma * 100)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if HMA entry condition is met"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        hma_col = f'hma_{period}'
        rising_col = f'hma_{period}_rising'
        slope_col = f'hma_{period}_slope'
        
        if hma_col not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        prev = data.iloc[index - 1]
        
        price = current[source]
        hma = current[hma_col]
        rising = current[rising_col]
        slope = current[slope_col]
        
        if pd.isna(hma) or pd.isna(rising) or pd.isna(slope):
            return False
        
        if direction == 'LONG':
            # Price above HMA, HMA rising, positive slope
            return price > hma and rising and slope > 0
        else:  # SHORT
            # Price below HMA, HMA falling, negative slope
            return price < hma and not rising and slope < 0
