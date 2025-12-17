"""
cci.py
======

CCI (Commodity Channel Index) - Momentum oscillator
Measures deviation from statistical mean

Developed by Donald Lambert
Identifies cyclical trends and reversals

Signals:
- CCI > +100 = Overbought/Strong uptrend
- CCI < -100 = Oversold/Strong downtrend
- Zero line crosses = Trend changes

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class CCIModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "CCI (Commodity Channel Index)"
    
    @property
    def category(self) -> str:
        return "momentum"
    
    @property
    def description(self) -> str:
        return "Momentum oscillator. >+100 overbought, <-100 oversold."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "CCI Period",
                    "type": "number",
                    "default": 20,
                    "min": 5,
                    "max": 50,
                    "step": 5
                },
                {
                    "name": "overbought",
                    "label": "Overbought Level",
                    "type": "number",
                    "default": 100,
                    "min": 50,
                    "max": 200,
                    "step": 50
                },
                {
                    "name": "oversold",
                    "label": "Oversold Level",
                    "type": "number",
                    "default": -100,
                    "min": -200,
                    "max": -50,
                    "step": 50
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
        
        period = config.get('period', 20)
        
        # Typical Price
        df['tp'] = (df['high'] + df['low'] + df['close']) / 3
        
        # SMA of Typical Price
        df['tp_sma'] = df['tp'].rolling(window=period).mean()
        
        # Mean Absolute Deviation
        df['mad'] = df['tp'].rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean())), raw=True
        )
        
        # CCI formula
        df['cci'] = (df['tp'] - df['tp_sma']) / (0.015 * df['mad'])
        
        # Cleanup
        df.drop(['tp', 'tp_sma', 'mad'], axis=1, inplace=True)
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        oversold = config.get('oversold', -100)
        overbought = config.get('overbought', 100)
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['cci']):
            return False
        
        if direction == 'LONG':
            # Crosses above oversold
            return prev['cci'] < oversold and curr['cci'] >= oversold
        
        elif direction == 'SHORT':
            # Crosses below overbought
            return prev['cci'] > overbought and curr['cci'] <= overbought
        
        return False