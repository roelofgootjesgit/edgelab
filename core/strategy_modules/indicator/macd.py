# core/strategy_modules/indicators/macd.py
"""
MACD (Moving Average Convergence Divergence) Module

Trend following momentum indicator.
Signals from MACD line crossing signal line.
"""

from typing import Dict, Any
import pandas as pd
from core.strategy_modules.base import BaseModule


class MACDModule(BaseModule):
    """
    MACD - Trend and momentum indicator.
    
    Components:
    - MACD Line = EMA(12) - EMA(26)
    - Signal Line = EMA(9) of MACD
    - Histogram = MACD - Signal
    
    Entry signals:
    - Bullish: MACD crosses above signal line
    - Bearish: MACD crosses below signal line
    """
    
    @property
    def name(self) -> str:
        return "MACD"
    
    @property
    def category(self) -> str:
        return "indicator"
    
    @property
    def description(self) -> str:
        return "Trend momentum indicator with crossover signals"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "fields": [
                {
                    "name": "fast_period",
                    "label": "Fast EMA",
                    "type": "number",
                    "default": 12,
                    "min": 1,
                    "max": 100,
                    "help": "Fast EMA period (standard: 12)"
                },
                {
                    "name": "slow_period",
                    "label": "Slow EMA",
                    "type": "number",
                    "default": 26,
                    "min": 1,
                    "max": 200,
                    "help": "Slow EMA period (standard: 26)"
                },
                {
                    "name": "signal_period",
                    "label": "Signal EMA",
                    "type": "number",
                    "default": 9,
                    "min": 1,
                    "max": 50,
                    "help": "Signal line EMA period (standard: 9)"
                },
                {
                    "name": "signal_type",
                    "label": "Signal Type",
                    "type": "select",
                    "options": ["crossover", "zero_line", "both"],
                    "default": "crossover",
                    "help": "Trigger on crossover, zero line cross, or both"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate MACD indicator"""
        fast = config.get('fast_period', 12)
        slow = config.get('slow_period', 26)
        signal = config.get('signal_period', 9)
        
        # Calculate EMAs
        ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        data['macd'] = ema_fast - ema_slow
        
        # Calculate signal line
        data['macd_signal'] = data['macd'].ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any], 
        strategy_direction: str
    ) -> bool:
        """
        Check MACD entry conditions.
        
        LONG: MACD crosses above signal (and optionally above zero)
        SHORT: MACD crosses below signal (and optionally below zero)
        """
        if index < 1:
            return False
        
        if 'macd' not in data.columns or 'macd_signal' not in data.columns:
            return False
        
        current_macd = data.loc[index, 'macd']
        prev_macd = data.loc[index - 1, 'macd']
        current_signal = data.loc[index, 'macd_signal']
        prev_signal = data.loc[index - 1, 'macd_signal']
        
        if pd.isna(current_macd) or pd.isna(prev_macd) or pd.isna(current_signal) or pd.isna(prev_signal):
            return False
        
        signal_type = config.get('signal_type', 'crossover')
        
        # Check crossover
        crossover_bullish = prev_macd <= prev_signal and current_macd > current_signal
        crossover_bearish = prev_macd >= prev_signal and current_macd < current_signal
        
        if signal_type == 'crossover':
            if strategy_direction == 'LONG':
                return crossover_bullish
            else:
                return crossover_bearish
        
        elif signal_type == 'zero_line':
            if strategy_direction == 'LONG':
                return prev_macd <= 0 and current_macd > 0
            else:
                return prev_macd >= 0 and current_macd < 0
        
        elif signal_type == 'both':
            if strategy_direction == 'LONG':
                return crossover_bullish and current_macd > 0
            else:
                return crossover_bearish and current_macd < 0
        
        return False