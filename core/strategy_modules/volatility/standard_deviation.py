"""
standard_deviation.py - Standard Deviation
Pure volatility measure
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class StandardDeviationModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Standard Deviation"
    
    @property
    def category(self) -> str:
        return "volatility"
    
    @property
    def description(self) -> str:
        return "Price volatility. High std dev = high volatility."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Period", "type": "number",
                 "default": 20, "min": 10, "max": 100},
                {"name": "threshold", "label": "High Vol Threshold", "type": "number",
                 "default": 1.5, "min": 1.0, "max": 3.0, "step": 0.5}
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
        
        # Standard deviation
        df['std_dev'] = df['close'].rolling(window=period).std()
        
        # As percentage of price
        df['std_dev_pct'] = (df['std_dev'] / df['close']) * 100
        
        # Average std dev
        df['std_dev_avg'] = df['std_dev'].rolling(window=50).mean()
        
        # Volatility state
        df['volatility_state'] = np.where(
            df['std_dev'] > df['std_dev_avg'], 'high', 'low'
        )
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['std_dev']) or pd.isna(curr['std_dev_avg']):
            return False
        
        threshold = config.get('threshold', 1.5)
        
        # High volatility condition
        high_vol = curr['std_dev'] > (curr['std_dev_avg'] * threshold)
        
        if not high_vol:
            return False
        
        # Entry with momentum in high volatility
        if direction == 'LONG':
            return curr['close'] > prev['close']
        else:
            return curr['close'] < prev['close']