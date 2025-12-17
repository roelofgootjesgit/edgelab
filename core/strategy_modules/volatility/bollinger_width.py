"""
bollinger_width.py - Bollinger Bands Width
Volatility squeeze indicator
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class BollingerWidthModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Bollinger Width"
    
    @property
    def category(self) -> str:
        return "volatility"
    
    @property
    def description(self) -> str:
        return "Volatility squeeze. Low width = breakout imminent."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Period", "type": "number",
                 "default": 20, "min": 10, "max": 50},
                {"name": "std_dev", "label": "Std Dev", "type": "number",
                 "default": 2.0, "min": 1.0, "max": 3.0, "step": 0.5},
                {"name": "squeeze_threshold", "label": "Squeeze %", "type": "number",
                 "default": 5.0, "min": 2.0, "max": 10.0, "step": 0.5}
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
        std_dev = config.get('std_dev', 2.0)
        
        # Calculate Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=period).mean()
        bb_std = df['close'].rolling(window=period).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * std_dev)
        df['bb_lower'] = df['bb_middle'] - (bb_std * std_dev)
        
        # Bollinger Width (as percentage)
        df['bb_width'] = ((df['bb_upper'] - df['bb_lower']) / df['bb_middle']) * 100
        
        # Width percentile (0-100)
        df['bb_width_percentile'] = df['bb_width'].rolling(window=100).apply(
            lambda x: (x.iloc[-1] <= x).sum() / len(x) * 100, raw=False
        )
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 2:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['bb_width']) or pd.isna(curr['bb_upper']):
            return False
        
        squeeze_threshold = config.get('squeeze_threshold', 5.0)
        
        # Check if in squeeze (low width)
        in_squeeze = curr['bb_width'] < squeeze_threshold
        
        if not in_squeeze:
            return False
        
        price = curr['close']
        
        if direction == 'LONG':
            # Break above upper band during squeeze
            return price > curr['bb_upper'] and prev['close'] <= prev['bb_upper']
        
        else:  # SHORT
            # Break below lower band during squeeze
            return price < curr['bb_lower'] and prev['close'] >= prev['bb_lower']