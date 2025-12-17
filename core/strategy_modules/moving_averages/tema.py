"""
TEMA - Triple Exponential Moving Average
=========================================

Triple smoothed EMA that reduces lag significantly.

Formula:
TEMA = (3 × EMA1) − (3 × EMA2) + EMA3

Where:
- EMA1 = EMA(price, period)
- EMA2 = EMA(EMA1, period)
- EMA3 = EMA(EMA2, period)

Features:
- Very low lag
- Smooth but responsive
- Reduces noise significantly
- Fast trend detection
- Popular for scalping

Entry Logic:
- LONG: price > TEMA AND TEMA rising
- SHORT: price < TEMA AND TEMA falling
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class TEMAModule(BaseModule):
    """Triple Exponential Moving Average indicator module"""
    
    @property
    def name(self) -> str:
        return "TEMA"
    
    @property
    def category(self) -> str:
        return "moving_averages"
    
    @property
    def description(self) -> str:
        return "Triple EMA - very low lag, smooth and responsive"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 500,
                    "default": 20,
                    "description": "TEMA period (typical: 9, 20, 50)"
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
        """Calculate TEMA indicator"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        prices = data[source]
        
        # Calculate triple EMA
        ema1 = prices.ewm(span=period, adjust=False).mean()
        ema2 = ema1.ewm(span=period, adjust=False).mean()
        ema3 = ema2.ewm(span=period, adjust=False).mean()
        
        # TEMA formula
        tema = (3 * ema1) - (3 * ema2) + ema3
        
        # Add to dataframe
        data[f'tema_{period}'] = tema
        
        # Calculate trend
        data[f'tema_{period}_rising'] = tema > tema.shift(1)
        data[f'tema_{period}_slope'] = tema - tema.shift(1)
        
        # Distance from price (%)
        data[f'tema_{period}_dist_pct'] = ((prices - tema) / tema * 100)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if TEMA entry condition is met"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        tema_col = f'tema_{period}'
        rising_col = f'tema_{period}_rising'
        
        if tema_col not in data.columns:
            return False
        
        if index < 1:
            return False
        
        current = data.iloc[index]
        
        price = current[source]
        tema = current[tema_col]
        rising = current[rising_col]
        
        if pd.isna(tema) or pd.isna(rising):
            return False
        
        if direction == 'LONG':
            # Price above TEMA and TEMA rising
            return price > tema and rising
        else:  # SHORT
            # Price below TEMA and TEMA falling
            return price < tema and not rising
