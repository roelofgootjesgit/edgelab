"""
ad_line.py - Accumulation/Distribution Line
Volume-weighted price momentum
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class ADLineModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "A/D Line"
    
    @property
    def category(self) -> str:
        return "volume"
    
    @property
    def description(self) -> str:
        return "Accumulation/Distribution. Rising = buying pressure."
    
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
        
        # Money Flow Multiplier
        clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        clv = clv.fillna(0)  # Handle div by zero
        
        # Money Flow Volume
        df['mfv'] = clv * df['volume']
        
        # A/D Line (cumulative)
        df['ad_line'] = df['mfv'].cumsum()
        
        # Signal line
        df['ad_signal'] = df['ad_line'].ewm(span=signal_period, adjust=False).mean()
        
        # Cleanup
        df = df.drop(columns=['mfv'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['ad_line']) or pd.isna(curr['ad_signal']):
            return False
        
        if direction == 'LONG':
            # A/D crosses above signal
            return (curr['ad_line'] > curr['ad_signal'] and 
                    prev['ad_line'] <= prev['ad_signal'])
        
        else:
            # A/D crosses below signal
            return (curr['ad_line'] < curr['ad_signal'] and 
                    prev['ad_line'] >= prev['ad_signal'])