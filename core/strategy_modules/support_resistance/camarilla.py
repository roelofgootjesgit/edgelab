"""
camarilla.py - Camarilla Pivots
Intraday support/resistance levels
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class CamarillaModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Camarilla Pivots"
    
    @property
    def category(self) -> str:
        return "support_resistance"
    
    @property
    def description(self) -> str:
        return "Intraday pivots. H3/L3 = key breakout levels."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "lookback", "label": "Lookback Period", "type": "number",
                 "default": 1, "min": 1, "max": 5}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        lookback = config.get('lookback', 1)
        
        # Previous period values
        prev_high = df['high'].shift(lookback)
        prev_low = df['low'].shift(lookback)
        prev_close = df['close'].shift(lookback)
        
        # Calculate range
        range_val = prev_high - prev_low
        
        # Camarilla resistance levels
        df['h4'] = prev_close + (range_val * 1.1 / 2)
        df['h3'] = prev_close + (range_val * 1.1 / 4)
        df['h2'] = prev_close + (range_val * 1.1 / 6)
        df['h1'] = prev_close + (range_val * 1.1 / 12)
        
        # Camarilla support levels
        df['l1'] = prev_close - (range_val * 1.1 / 12)
        df['l2'] = prev_close - (range_val * 1.1 / 6)
        df['l3'] = prev_close - (range_val * 1.1 / 4)
        df['l4'] = prev_close - (range_val * 1.1 / 2)
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 2:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['h3']) or pd.isna(curr['l3']):
            return False
        
        price = curr['close']
        prev_price = prev['close']
        
        if direction == 'LONG':
            # Break above H3 (key resistance)
            return prev_price <= prev['h3'] and price > curr['h3']
        
        else:
            # Break below L3 (key support)
            return prev_price >= prev['l3'] and price < curr['l3']