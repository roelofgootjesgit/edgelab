"""
obv.py - OBV (On Balance Volume)
Cumulative volume indicator
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class OBVModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "OBV"
    
    @property
    def category(self) -> str:
        return "volume"
    
    @property
    def description(self) -> str:
        return "On Balance Volume. Rising OBV = accumulation."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "signal_period", "label": "Signal MA Period", "type": "number",
                 "default": 20, "min": 10, "max": 50}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        signal_period = config.get('signal_period', 20)
        
        # Calculate OBV
        df['obv'] = 0.0
        df.loc[df['close'] > df['close'].shift(1), 'obv'] = df['volume']
        df.loc[df['close'] < df['close'].shift(1), 'obv'] = -df['volume']
        df['obv'] = df['obv'].cumsum()
        
        # Signal line (EMA of OBV)
        df['obv_signal'] = df['obv'].ewm(span=signal_period, adjust=False).mean()
        
        # Trend
        df['obv_trend'] = np.where(df['obv'] > df['obv_signal'], 'up', 'down')
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['obv']) or pd.isna(curr['obv_signal']):
            return False
        
        if direction == 'LONG':
            # OBV crosses above signal
            return (curr['obv'] > curr['obv_signal'] and 
                    prev['obv'] <= prev['obv_signal'])
        
        else:
            # OBV crosses below signal
            return (curr['obv'] < curr['obv_signal'] and 
                    prev['obv'] >= prev['obv_signal'])