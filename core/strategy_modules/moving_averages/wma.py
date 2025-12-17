"""
WMA - Weighted Moving Average
==============================

Linear-weighted moving average that gives more weight to recent prices.

Formula:
WMA = (P1*n + P2*(n-1) + P3*(n-2) + ... + Pn*1) / (n + (n-1) + (n-2) + ... + 1)

Where:
- P1 = most recent price
- n = period length
- Weights sum = n * (n+1) / 2

Features:
- Linear weighting (newest = n, oldest = 1)
- More responsive than SMA
- Less lag than EMA
- Trend direction detection
- Distance from price

Entry Logic:
- LONG: price > WMA AND WMA rising
- SHORT: price < WMA AND WMA falling
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class WMAModule(BaseModule):
    """Weighted Moving Average indicator module"""
    
    @property
    def name(self) -> str:
        return "WMA"
    
    @property
    def category(self) -> str:
        return "moving_averages"
    
    @property
    def description(self) -> str:
        return "Weighted Moving Average - linear weighted, more responsive than SMA"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 500,
                    "default": 20,
                    "description": "WMA period (typical: 20, 50)"
                },
                "source": {
                    "type": "string",
                    "enum": ["close", "open", "high", "low", "hl2", "hlc3", "ohlc4"],
                    "default": "close",
                    "description": "Price source for calculation"
                }
            },
            "required": ["period"]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate WMA indicator"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        # Get source price
        if source == 'hl2':
            prices = (data['high'] + data['low']) / 2
        elif source == 'hlc3':
            prices = (data['high'] + data['low'] + data['close']) / 3
        elif source == 'ohlc4':
            prices = (data['open'] + data['high'] + data['low'] + data['close']) / 4
        else:
            prices = data[source]
        
        # Calculate WMA using rolling window
        def wma_calc(window):
            """Calculate WMA for a rolling window"""
            if len(window) < period:
                return np.nan
            weights = np.arange(1, period + 1)
            return np.sum(weights * window) / weights.sum()
        
        wma = prices.rolling(window=period).apply(wma_calc, raw=True)
        
        # Add to dataframe
        data[f'wma_{period}'] = wma
        
        # Calculate trend direction
        data[f'wma_{period}_rising'] = wma > wma.shift(1)
        
        # Distance from price (%)
        data[f'wma_{period}_dist_pct'] = ((prices - wma) / wma * 100)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if WMA entry condition is met"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        wma_col = f'wma_{period}'
        rising_col = f'wma_{period}_rising'
        
        if wma_col not in data.columns or rising_col not in data.columns:
            return False
        
        if index < 1:
            return False
        
        current = data.iloc[index]
        
        # Get price
        if source == 'hl2':
            price = (current['high'] + current['low']) / 2
        elif source == 'hlc3':
            price = (current['high'] + current['low'] + current['close']) / 3
        elif source == 'ohlc4':
            price = (current['open'] + current['high'] + current['low'] + current['close']) / 4
        else:
            price = current[source]
        
        wma = current[wma_col]
        rising = current[rising_col]
        
        if pd.isna(wma) or pd.isna(rising):
            return False
        
        if direction == 'LONG':
            # Price above WMA and WMA rising
            return price > wma and rising
        else:  # SHORT
            # Price below WMA and WMA falling
            return price < wma and not rising
