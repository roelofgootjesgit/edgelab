"""
donchian_channels.py
====================

Donchian Channels - Price breakout system
Shows highest high and lowest low over period

Developed by Richard Donchian
Used by Turtle Traders for breakouts

Components:
- Upper band: Highest high over N periods
- Lower band: Lowest low over N periods
- Middle line: Average of upper and lower

Signals:
- Price breaks above upper = Bullish breakout
- Price breaks below lower = Bearish breakout

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class DonchianChannelsModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Donchian Channels"
    
    @property
    def category(self) -> str:
        return "volatility"
    
    @property
    def description(self) -> str:
        return "Breakout system. Price breaks = trend signal. Used by Turtle Traders."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "Channel Period",
                    "type": "number",
                    "default": 20,
                    "min": 10,
                    "max": 100,
                    "step": 10,
                    "help": "Lookback period for high/low"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        required = ['high', 'low']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        
        period = config.get('period', 20)
        
        # Upper band: Highest high
        df['donchian_upper'] = df['high'].rolling(window=period).max()
        
        # Lower band: Lowest low
        df['donchian_lower'] = df['low'].rolling(window=period).min()
        
        # Middle line: Average
        df['donchian_middle'] = (df['donchian_upper'] + df['donchian_lower']) / 2
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['donchian_upper']) or pd.isna(curr['donchian_lower']):
            return False
        
        if direction == 'LONG':
            # Price breaks above upper channel
            return (prev['close'] <= prev['donchian_upper'] and
                    curr['close'] > curr['donchian_upper'])
        
        elif direction == 'SHORT':
            # Price breaks below lower channel
            return (prev['close'] >= prev['donchian_lower'] and
                    curr['close'] < curr['donchian_lower'])
        
        return False