"""
chande_kroll.py - Chande Kroll Stop
Volatility-based trailing stop system
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class ChandeKrollModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Chande Kroll Stop"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return "Trailing stop. Price above long stop = bullish."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Period", "type": "number",
                 "default": 10, "min": 5, "max": 30},
                {"name": "multiplier", "label": "ATR Multiplier", "type": "number",
                 "default": 1.0, "min": 0.5, "max": 3.0, "step": 0.5}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        period = config.get('period', 10)
        multiplier = config.get('multiplier', 1.0)
        
        # Calculate ATR
        df['h-l'] = df['high'] - df['low']
        df['h-pc'] = abs(df['high'] - df['close'].shift(1))
        df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=period).mean()
        
        # Long stop (below price)
        highest_high = df['high'].rolling(window=period).max()
        df['long_stop'] = highest_high - (df['atr'] * multiplier)
        
        # Short stop (above price)
        lowest_low = df['low'].rolling(window=period).min()
        df['short_stop'] = lowest_low + (df['atr'] * multiplier)
        
        # Cleanup
        df = df.drop(columns=['h-l', 'h-pc', 'l-pc', 'tr'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['long_stop']) or pd.isna(curr['short_stop']):
            return False
        
        if direction == 'LONG':
            # Price crosses above long stop
            return (curr['close'] > curr['long_stop'] and 
                    prev['close'] <= prev['long_stop'])
        
        else:  # SHORT
            # Price crosses below short stop
            return (curr['close'] < curr['short_stop'] and 
                    prev['close'] >= prev['short_stop'])