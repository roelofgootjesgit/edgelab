"""
keltner_channels.py
===================

Keltner Channels - Volatility bands using ATR
Similar to Bollinger Bands but uses ATR instead of std dev

Components:
- Middle line: EMA of price
- Upper band: Middle + (ATR × multiplier)
- Lower band: Middle - (ATR × multiplier)

Signals:
- Price above upper = Overbought/Strong trend
- Price below lower = Oversold/Strong trend
- Band squeezes = Breakout coming

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class KeltnerChannelsModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Keltner Channels"
    
    @property
    def category(self) -> str:
        return "volatility"
    
    @property
    def description(self) -> str:
        return "ATR-based volatility bands. Price outside bands = strong trend."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "ema_period",
                    "label": "EMA Period",
                    "type": "number",
                    "default": 20,
                    "min": 5,
                    "max": 50,
                    "step": 5
                },
                {
                    "name": "atr_period",
                    "label": "ATR Period",
                    "type": "number",
                    "default": 10,
                    "min": 5,
                    "max": 30,
                    "step": 5
                },
                {
                    "name": "multiplier",
                    "label": "ATR Multiplier",
                    "type": "number",
                    "default": 2.0,
                    "min": 1.0,
                    "max": 5.0,
                    "step": 0.5
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
        
        required = ['high', 'low', 'close']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        
        ema_period = config.get('ema_period', 20)
        atr_period = config.get('atr_period', 10)
        multiplier = config.get('multiplier', 2.0)
        
        # Calculate ATR
        df['h-l'] = df['high'] - df['low']
        df['h-pc'] = abs(df['high'] - df['close'].shift(1))
        df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=atr_period).mean()
        
        # Middle line (EMA)
        df['keltner_middle'] = df['close'].ewm(span=ema_period, adjust=False).mean()
        
        # Upper and lower bands
        df['keltner_upper'] = df['keltner_middle'] + (multiplier * df['atr'])
        df['keltner_lower'] = df['keltner_middle'] - (multiplier * df['atr'])
        
        # Cleanup
        df.drop(['h-l', 'h-pc', 'l-pc', 'tr'], axis=1, inplace=True)
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['keltner_upper']) or pd.isna(curr['keltner_lower']):
            return False
        
        if direction == 'LONG':
            # Price breaks above upper band
            return (prev['close'] <= prev['keltner_upper'] and
                    curr['close'] > curr['keltner_upper'])
        
        elif direction == 'SHORT':
            # Price breaks below lower band
            return (prev['close'] >= prev['keltner_lower'] and
                    curr['close'] < curr['keltner_lower'])
        
        return False