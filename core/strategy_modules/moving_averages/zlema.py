"""
ZLEMA - Zero Lag Exponential Moving Average
============================================

Modified EMA that attempts to eliminate lag by adjusting for price momentum.

Formula:
1. Lag = (period - 1) / 2
2. Adjusted Price = Price + (Price - Price[Lag])
3. ZLEMA = EMA(Adjusted Price, period)

Features:
- Minimal lag compared to traditional EMA
- Responds quickly to price changes
- Maintains good smoothness
- Momentum-aware
- Popular for fast entries

Entry Logic:
- LONG: price > ZLEMA AND ZLEMA rising sharply
- SHORT: price < ZLEMA AND ZLEMA falling sharply
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class ZLEMAModule(BaseModule):
    """Zero Lag Exponential Moving Average indicator module"""
    
    @property
    def name(self) -> str:
        return "ZLEMA"
    
    @property
    def category(self) -> str:
        return "moving_averages"
    
    @property
    def description(self) -> str:
        return "Zero Lag EMA - minimal lag, momentum-aware"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 500,
                    "default": 20,
                    "description": "ZLEMA period (typical: 9, 20, 50)"
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
        """Calculate ZLEMA indicator"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        prices = data[source]
        
        # Calculate lag
        lag = int((period - 1) / 2)
        
        # Adjusted price (add momentum)
        adjusted_price = prices + (prices - prices.shift(lag))
        
        # Calculate ZLEMA (EMA of adjusted price)
        zlema = adjusted_price.ewm(span=period, adjust=False).mean()
        
        # Add to dataframe
        data[f'zlema_{period}'] = zlema
        
        # Calculate trend strength
        data[f'zlema_{period}_rising'] = zlema > zlema.shift(1)
        data[f'zlema_{period}_slope'] = zlema - zlema.shift(1)
        
        # Distance from price (%)
        data[f'zlema_{period}_dist_pct'] = ((prices - zlema) / zlema * 100)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if ZLEMA entry condition is met"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        zlema_col = f'zlema_{period}'
        rising_col = f'zlema_{period}_rising'
        slope_col = f'zlema_{period}_slope'
        
        if zlema_col not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        
        price = current[source]
        zlema = current[zlema_col]
        rising = current[rising_col]
        slope = current[slope_col]
        
        if pd.isna(zlema) or pd.isna(rising) or pd.isna(slope):
            return False
        
        if direction == 'LONG':
            # Price above ZLEMA, rising with positive slope
            return price > zlema and rising and slope > 0
        else:  # SHORT
            # Price below ZLEMA, falling with negative slope
            return price < zlema and not rising and slope < 0
