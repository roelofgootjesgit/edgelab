"""
Elder Ray Index
================

Alexander Elder's Bull and Bear Power indicator.

Formula:
Bull Power = High - EMA(13)
Bear Power = Low - EMA(13)

Features:
- Measures buying and selling pressure
- Bull Power: bulls' ability to push price above average
- Bear Power: bears' ability to push price below average
- Used with trend direction (EMA slope)
- Divergences signal reversals

Entry Logic:
- LONG: Bull Power > 0 AND Bear Power rising AND EMA rising
- SHORT: Bear Power < 0 AND Bull Power falling AND EMA falling

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class ElderRayModule(BaseModule):
    """Elder Ray Bull/Bear Power indicator module"""
    
    @property
    def name(self) -> str:
        return "Elder Ray"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Alexander Elder's Bull and Bear Power indicator"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 200,
                    "default": 13,
                    "description": "EMA period (typical: 13)"
                },
                "source": {
                    "type": "string",
                    "enum": ["close", "hlc3", "ohlc4"],
                    "default": "close",
                    "description": "Price source for EMA"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Elder Ray indicator"""
        period = config.get('period', 13)
        source = config.get('source', 'close')
        
        # Get source price for EMA
        if source == 'hlc3':
            prices = (data['high'] + data['low'] + data['close']) / 3
        elif source == 'ohlc4':
            prices = (data['open'] + data['high'] + data['low'] + data['close']) / 4
        else:
            prices = data['close']
        
        # Calculate EMA
        ema = prices.ewm(span=period, adjust=False).mean()
        
        # Calculate Bull and Bear Power
        bull_power = data['high'] - ema
        bear_power = data['low'] - ema
        
        # Add to dataframe
        data[f'elder_ema_{period}'] = ema
        data[f'elder_bull_{period}'] = bull_power
        data[f'elder_bear_{period}'] = bear_power
        
        # Trend direction
        data[f'elder_ema_rising'] = ema > ema.shift(1)
        
        # Power trends
        data[f'elder_bull_rising'] = bull_power > bull_power.shift(1)
        data[f'elder_bear_rising'] = bear_power > bear_power.shift(1)
        
        # Signals
        data[f'elder_bull_positive'] = bull_power > 0
        data[f'elder_bear_negative'] = bear_power < 0
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Elder Ray entry condition is met"""
        period = config.get('period', 13)
        
        bull_col = f'elder_bull_{period}'
        bear_col = f'elder_bear_{period}'
        ema_rising_col = f'elder_ema_rising'
        
        if bull_col not in data.columns or bear_col not in data.columns:
            return False
        
        if index < 2:
            return False
        
        current = data.iloc[index]
        
        bull_power = current[bull_col]
        bear_power = current[bear_col]
        ema_rising = current[ema_rising_col]
        bull_rising = current[f'elder_bull_rising']
        bear_rising = current[f'elder_bear_rising']
        
        if pd.isna(bull_power) or pd.isna(bear_power):
            return False
        
        if direction == 'LONG':
            # Bull Power positive, Bear Power rising, EMA uptrend
            return bull_power > 0 and bear_rising and ema_rising
        else:  # SHORT
            # Bear Power negative, Bull Power falling, EMA downtrend
            return bear_power < 0 and not bull_rising and not ema_rising