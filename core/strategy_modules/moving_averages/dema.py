"""
DEMA - Double Exponential Moving Average
=========================================

Double smoothed EMA that reduces lag compared to traditional EMA.

Formula:
DEMA = (2 × EMA1) − EMA2

Where:
- EMA1 = EMA(price, period)
- EMA2 = EMA(EMA1, period)

Features:
- Reduced lag vs single EMA
- Good balance of smoothness and responsiveness
- Less aggressive than TEMA
- Trend confirmation
- Popular for swing trading

Entry Logic:
- LONG: price > DEMA AND DEMA rising
- SHORT: price < DEMA AND DEMA falling
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class DEMAModule(BaseModule):
    """Double Exponential Moving Average indicator module"""
    
    @property
    def name(self) -> str:
        return "DEMA"
    
    @property
    def category(self) -> str:
        return "moving_averages"
    
    @property
    def description(self) -> str:
        return "Double EMA - reduced lag, balanced smoothness"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 500,
                    "default": 20,
                    "description": "DEMA period (typical: 9, 20, 50)"
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
        """Calculate DEMA indicator"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        prices = data[source]
        
        # Calculate double EMA
        ema1 = prices.ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        
        # DEMA formula
        dema = (2 * ema1) - ema2
        
        # Add to dataframe
        data[f'dema_{period}'] = dema
        
        # Calculate trend
        data[f'dema_{period}_rising'] = dema > dema.shift(1)
        data[f'dema_{period}_slope'] = dema - dema.shift(1)
        
        # Distance from price (%)
        data[f'dema_{period}_dist_pct'] = ((prices - dema) / dema * 100)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if DEMA entry condition is met"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        dema_col = f'dema_{period}'
        rising_col = f'dema_{period}_rising'
        
        if dema_col not in data.columns:
            return False
        
        if index < 1:
            return False
        
        current = data.iloc[index]
        
        price = current[source]
        dema = current[dema_col]
        rising = current[rising_col]
        
        if pd.isna(dema) or pd.isna(rising):
            return False
        
        if direction == 'LONG':
            # Price above DEMA and DEMA rising
            return price > dema and rising
        else:  # SHORT
            # Price below DEMA and DEMA falling
            return price < dema and not rising

