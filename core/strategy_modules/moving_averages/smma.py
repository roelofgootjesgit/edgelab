"""
SMMA - Smoothed Moving Average (Wilder's Moving Average)
=========================================================

Smoothed MA developed by J. Welles Wilder Jr., used in RSI and other indicators.
Also called RMA (Running Moving Average) or Modified Moving Average (MMA).

Formula:
First SMMA = SMA(period)
Next SMMA = (Prev SMMA × (period - 1) + Current Price) / period

Features:
- Very smooth, minimal whipsaws
- Slower than SMA and EMA
- Heavily dampens noise
- Good for long-term trends
- Used in Wilder's indicators (RSI, ATR)

Entry Logic:
- LONG: price > SMMA AND SMMA rising steadily
- SHORT: price < SMMA AND SMMA falling steadily
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class SMMAModule(BaseModule):
    """Smoothed Moving Average (Wilder's) indicator module"""
    
    @property
    def name(self) -> str:
        return "SMMA"
    
    @property
    def category(self) -> str:
        return "moving_averages"
    
    @property
    def description(self) -> str:
        return "Smoothed MA (Wilder's) - very smooth, minimal noise"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 500,
                    "default": 20,
                    "description": "SMMA period (typical: 14, 20, 50)"
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
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate SMMA indicator"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        prices = data[source].values
        
        # Calculate SMMA
        smma = np.zeros_like(prices, dtype=float)
        
        # First SMMA = SMA
        smma[:period-1] = np.nan
        smma[period-1] = np.mean(prices[:period])
        
        # Subsequent SMMA values
        for i in range(period, len(prices)):
            smma[i] = (smma[i-1] * (period - 1) + prices[i]) / period
        
        # Add to dataframe
        data[f'smma_{period}'] = smma
        
        # Calculate trend (slower response expected)
        data[f'smma_{period}_rising'] = data[f'smma_{period}'] > data[f'smma_{period}'].shift(1)
        data[f'smma_{period}_slope'] = data[f'smma_{period}'] - data[f'smma_{period}'].shift(1)
        
        # Distance from price (%)
        data[f'smma_{period}_dist_pct'] = ((data[source] - data[f'smma_{period}']) / data[f'smma_{period}'] * 100)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if SMMA entry condition is met"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        smma_col = f'smma_{period}'
        rising_col = f'smma_{period}_rising'
        
        if smma_col not in data.columns:
            return False
        
        if index < 3:
            return False
        
        current = data.iloc[index]
        prev = data.iloc[index - 1]
        prev2 = data.iloc[index - 2]
        
        price = current[source]
        smma = current[smma_col]
        rising = current[rising_col]
        
        # Check trend consistency (last 3 candles)
        rising_prev = prev[rising_col]
        rising_prev2 = prev2[rising_col]
        
        if pd.isna(smma) or pd.isna(rising):
            return False
        
        if direction == 'LONG':
            # Price above SMMA with steady uptrend
            trend_consistent = rising and rising_prev and rising_prev2
            return price > smma and trend_consistent
        else:  # SHORT
            # Price below SMMA with steady downtrend
            trend_consistent = not rising and not rising_prev and not rising_prev2
            return price < smma and trend_consistent
