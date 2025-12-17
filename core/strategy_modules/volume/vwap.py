"""
vwap.py - VWAP (Volume Weighted Average Price)
Intraday volume-weighted price anchor
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class VWAPModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "VWAP"
    
    @property
    def category(self) -> str:
        return "volume"
    
    @property
    def description(self) -> str:
        return "Volume Weighted Average Price. Price above VWAP = bullish."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Rolling Period", "type": "number",
                 "default": 20, "min": 10, "max": 100,
                 "help": "Use rolling VWAP instead of session reset"}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        period = config.get('period', 20)
        
        # Typical price
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        
        # Volume * Price
        df['vp'] = df['typical_price'] * df['volume']
        
        # Rolling VWAP
        df['vwap'] = (
            df['vp'].rolling(window=period).sum() / 
            df['volume'].rolling(window=period).sum()
        )
        
        # Distance from VWAP (percentage)
        df['vwap_distance'] = ((df['close'] - df['vwap']) / df['vwap']) * 100
        
        # Cleanup
        df = df.drop(columns=['typical_price', 'vp'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['vwap']):
            return False
        
        if direction == 'LONG':
            # Price crosses above VWAP
            return curr['close'] > curr['vwap'] and prev['close'] <= prev['vwap']
        
        else:
            # Price crosses below VWAP
            return curr['close'] < curr['vwap'] and prev['close'] >= prev['vwap']