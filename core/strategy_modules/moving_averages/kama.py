"""
KAMA - Kaufman Adaptive Moving Average
=======================================

Adaptive moving average that adjusts smoothing based on market noise.
Developed by Perry Kaufman.

Formula:
1. ER (Efficiency Ratio) = |Change| / Sum(|Daily Changes|)
2. SC (Smoothing Constant) = [ER × (FastSC - SlowSC) + SlowSC]²
3. KAMA = KAMA[prev] + SC × (Price - KAMA[prev])

Where:
- FastSC = 2/(fast+1)
- SlowSC = 2/(slow+1)
- ER measures trending vs noise
- High ER = trending (faster response)
- Low ER = choppy (slower response)

Features:
- Adapts to market conditions
- Fast in trends, slow in chop
- Reduces whipsaws
- Self-adjusting smoothing
- Popular for volatile markets

Entry Logic:
- LONG: price > KAMA AND ER > threshold (trending)
- SHORT: price < KAMA AND ER > threshold (trending)
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class KAMAModule(BaseModule):
    """Kaufman Adaptive Moving Average indicator module"""
    
    @property
    def name(self) -> str:
        return "KAMA"
    
    @property
    def category(self) -> str:
        return "moving_averages"
    
    @property
    def description(self) -> str:
        return "Kaufman Adaptive MA - adapts to market conditions"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 500,
                    "default": 10,
                    "description": "ER calculation period (typical: 10)"
                },
                "fast": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 50,
                    "default": 2,
                    "description": "Fast EMA period for trending markets"
                },
                "slow": {
                    "type": "integer",
                    "minimum": 5,
                    "maximum": 100,
                    "default": 30,
                    "description": "Slow EMA period for choppy markets"
                },
                "er_threshold": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "default": 0.3,
                    "description": "ER threshold for entry (0.3 = trending)"
                },
                "source": {
                    "type": "string",
                    "enum": ["close", "open", "high", "low"],
                    "default": "close",
                    "description": "Price source"
                }
            },
            "required": ["period"]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate KAMA indicator"""
        period = config.get('period', 10)
        fast = config.get('fast', 2)
        slow = config.get('slow', 30)
        source = config.get('source', 'close')
        
        prices = data[source].values
        
        # Calculate ER (Efficiency Ratio)
        change = np.abs(prices - np.roll(prices, period))
        volatility = pd.Series(np.abs(prices - np.roll(prices, 1))).rolling(window=period).sum().values
        
        # Avoid division by zero
        volatility = np.where(volatility == 0, 1e-10, volatility)
        er = change / volatility
        
        # Calculate smoothing constants
        fast_sc = 2.0 / (fast + 1)
        slow_sc = 2.0 / (slow + 1)
        
        # SC = [ER × (FastSC - SlowSC) + SlowSC]²
        sc = np.power(er * (fast_sc - slow_sc) + slow_sc, 2)
        
        # Calculate KAMA
        kama = np.zeros_like(prices)
        kama[period] = prices[period]  # Initialize
        
        for i in range(period + 1, len(prices)):
            kama[i] = kama[i-1] + sc[i] * (prices[i] - kama[i-1])
        
        # Set early values to NaN
        kama[:period] = np.nan
        
        # Add to dataframe
        data[f'kama_{period}'] = kama
        data[f'kama_{period}_er'] = er
        
        # Calculate trend
        data[f'kama_{period}_rising'] = data[f'kama_{period}'] > data[f'kama_{period}'].shift(1)
        
        # Distance from price (%)
        data[f'kama_{period}_dist_pct'] = ((data[source] - data[f'kama_{period}']) / data[f'kama_{period}'] * 100)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if KAMA entry condition is met"""
        period = config.get('period', 10)
        er_threshold = config.get('er_threshold', 0.3)
        source = config.get('source', 'close')
        
        kama_col = f'kama_{period}'
        er_col = f'kama_{period}_er'
        
        if kama_col not in data.columns or er_col not in data.columns:
            return False
        
        if index < 1:
            return False
        
        current = data.iloc[index]
        
        price = current[source]
        kama = current[kama_col]
        er = current[er_col]
        
        if pd.isna(kama) or pd.isna(er):
            return False
        
        # Only enter when market is trending (high ER)
        if er < er_threshold:
            return False
        
        if direction == 'LONG':
            # Price above KAMA in trending market
            return price > kama
        else:  # SHORT
            # Price below KAMA in trending market
            return price < kama

