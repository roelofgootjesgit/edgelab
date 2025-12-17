"""
aroon.py - Aroon Indicator
Trend strength and direction (time since high/low)
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class AroonModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Aroon"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return "Trend strength. Aroon Up >70 bullish, Down >70 bearish."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Period", "type": "number", 
                 "default": 25, "min": 10, "max": 50},
                {"name": "threshold", "label": "Threshold", "type": "number",
                 "default": 70, "min": 50, "max": 90}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        period = config.get('period', 25)
        
        df['aroon_up'] = 100 * df['high'].rolling(window=period + 1).apply(
            lambda x: period - x.argmax(), raw=True) / period
        
        df['aroon_down'] = 100 * df['low'].rolling(window=period + 1).apply(
            lambda x: period - x.argmin(), raw=True) / period
        
        df['aroon_oscillator'] = df['aroon_up'] - df['aroon_down']
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        threshold = config.get('threshold', 70)
        curr = data.iloc[index]
        
        if pd.isna(curr['aroon_up']) or pd.isna(curr['aroon_down']):
            return False
        
        if direction == 'LONG':
            return curr['aroon_up'] > threshold and curr['aroon_up'] > curr['aroon_down']
        else:
            return curr['aroon_down'] > threshold and curr['aroon_down'] > curr['aroon_up']