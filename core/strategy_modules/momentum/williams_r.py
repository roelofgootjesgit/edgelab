"""
williams_r.py
=============

Williams %R - Momentum oscillator
Inverted Stochastic (scale -100 to 0)

Developed by Larry Williams
Identifies overbought/oversold conditions

Signals:
- Above -20 = Overbought
- Below -80 = Oversold

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class WilliamsRModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Williams %R"
    
    @property
    def category(self) -> str:
        return "momentum"
    
    @property
    def description(self) -> str:
        return "Momentum oscillator. >-20 overbought, <-80 oversold."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "Lookback Period",
                    "type": "number",
                    "default": 14,
                    "min": 5,
                    "max": 50,
                    "step": 1
                },
                {
                    "name": "oversold",
                    "label": "Oversold Level",
                    "type": "number",
                    "default": -80,
                    "min": -90,
                    "max": -70,
                    "step": 5
                },
                {
                    "name": "overbought",
                    "label": "Overbought Level",
                    "type": "number",
                    "default": -20,
                    "min": -30,
                    "max": -10,
                    "step": 5
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
        
        period = config.get('period', 14)
        
        # Calculate Williams %R
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        df['williams_r'] = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        oversold = config.get('oversold', -80)
        overbought = config.get('overbought', -20)
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['williams_r']):
            return False
        
        if direction == 'LONG':
            # Crosses above oversold
            return prev['williams_r'] < oversold and curr['williams_r'] >= oversold
        
        elif direction == 'SHORT':
            # Crosses below overbought
            return prev['williams_r'] > overbought and curr['williams_r'] <= overbought
        
        return False