"""
atr.py - ATR (Average True Range)
Pure volatility measure
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class AtrModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "ATR"
    
    @property
    def category(self) -> str:
        return "volatility"
    
    @property
    def description(self) -> str:
        return "Average True Range. High ATR = high volatility."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Period", "type": "number",
                 "default": 14, "min": 7, "max": 30},
                {"name": "volatility_threshold", "label": "High Vol Threshold", "type": "number",
                 "default": 2.0, "min": 1.0, "max": 5.0, "step": 0.5,
                 "help": "Enter when ATR > avg_atr * threshold"}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        period = config.get('period', 14)
        
        # Calculate True Range
        df['h-l'] = df['high'] - df['low']
        df['h-pc'] = abs(df['high'] - df['close'].shift(1))
        df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        
        # ATR (Wilder's smoothing)
        df['atr'] = df['tr'].ewm(alpha=1/period, adjust=False).mean()
        
        # ATR as percentage of price
        df['atr_percent'] = (df['atr'] / df['close']) * 100
        
        # Average ATR (for comparison)
        df['atr_average'] = df['atr'].rolling(window=50).mean()
        
        # Volatility state
        df['volatility_state'] = np.where(df['atr'] > df['atr_average'], 'high', 'low')
        
        # Cleanup
        df = df.drop(columns=['h-l', 'h-pc', 'l-pc', 'tr'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['atr']) or pd.isna(curr['atr_average']):
            return False
        
        threshold = config.get('volatility_threshold', 2.0)
        
        # Entry when volatility increases above threshold
        volatility_spike = curr['atr'] > (curr['atr_average'] * threshold)
        
        if not volatility_spike:
            return False
        
        # Both directions use same logic (high volatility + price momentum)
        if direction == 'LONG':
            # High volatility + price rising
            return curr['close'] > prev['close']
        
        else:  # SHORT
            # High volatility + price falling
            return curr['close'] < prev['close']