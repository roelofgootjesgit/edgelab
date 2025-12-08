# core/strategy_modules/indicators/rsi.py
"""
RSI (Relative Strength Index) Module

Classic momentum oscillator measuring speed and magnitude of price changes.
Overbought/oversold conditions for mean reversion strategies.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class RSIModule(BaseModule):
    """
    Relative Strength Index indicator module.
    
    Identifies overbought (>70) and oversold (<30) conditions.
    Popular for mean reversion strategies.
    
    Entry signals:
    - Bullish: RSI crosses above oversold threshold
    - Bearish: RSI crosses below overbought threshold
    """
    
    @property
    def name(self) -> str:
        return "RSI (Relative Strength Index)"
    
    @property
    def category(self) -> str:
        return "indicator"
    
    @property
    def description(self) -> str:
        return "Momentum oscillator identifying overbought/oversold conditions"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "Period",
                    "type": "number",
                    "default": 14,
                    "min": 2,
                    "max": 200,
                    "help": "Number of periods for RSI calculation"
                },
                {
                    "name": "overbought",
                    "label": "Overbought Level",
                    "type": "number",
                    "default": 70,
                    "min": 50,
                    "max": 90,
                    "help": "RSI above this = overbought (SHORT signal)"
                },
                {
                    "name": "oversold",
                    "label": "Oversold Level",
                    "type": "number",
                    "default": 30,
                    "min": 10,
                    "max": 50,
                    "help": "RSI below this = oversold (LONG signal)"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Calculate RSI indicator.
        
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss over period
        """
        period = config.get('period', 14)
        
        # Calculate price changes
        delta = data['close'].diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses (Wilder's smoothing)
        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        # Add to dataframe
        data['rsi'] = rsi
        
        # Mark overbought/oversold
        data['rsi_overbought'] = rsi > config.get('overbought', 70)
        data['rsi_oversold'] = rsi < config.get('oversold', 30)
        
        return data
    
    def check_entry_condition(self, data: pd.DataFrame, index: int, config: Dict[str, Any], strategy_direction: str) -> bool:
        """
        Check if RSI entry condition met based on strategy direction.
        
        LONG strategy: Only check oversold bounces (RSI crosses back above oversold)
        SHORT strategy: Only check overbought drops (RSI crosses back below overbought)
        
        This aligns with mean reversion trading:
        - Oversold (< 30) suggests bounce up → LONG opportunity
        - Overbought (> 70) suggests drop down → SHORT opportunity
        """
        if index < 1:  # Need previous candle
            return False
        
        oversold = config.get('oversold', 30)
        overbought = config.get('overbought', 70)
        
        current_rsi = data.loc[index, 'rsi']
        prev_rsi = data.loc[index - 1, 'rsi']
        
        # Check for NaN (not enough data yet)
        if pd.isna(current_rsi) or pd.isna(prev_rsi):
            return False
        
        # LONG strategy: Check for oversold bounce
        if strategy_direction == 'LONG':
            # RSI crosses back above oversold level
            return (prev_rsi < oversold and current_rsi > oversold)
        
        # SHORT strategy: Check for overbought drop
        elif strategy_direction == 'SHORT':
            # RSI crosses back below overbought level
            return (prev_rsi > overbought and current_rsi < overbought)
        
        return False