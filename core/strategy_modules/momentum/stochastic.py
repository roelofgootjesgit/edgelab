"""
stochastic.py
=============

Stochastic Oscillator - Momentum indicator
Compares close price to high-low range

Developed by George Lane
Shows momentum and potential reversals

Signals:
- %K > 80 = Overbought
- %K < 20 = Oversold
- %K crosses %D = Entry signal

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class StochasticModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Stochastic Oscillator"
    
    @property
    def category(self) -> str:
        return "momentum"
    
    @property
    def description(self) -> str:
        return "Momentum oscillator. <20 oversold, >80 overbought. %K/%D crossovers."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "k_period",
                    "label": "%K Period",
                    "type": "number",
                    "default": 14,
                    "min": 5,
                    "max": 50,
                    "step": 1
                },
                {
                    "name": "d_period",
                    "label": "%D Period (Smoothing)",
                    "type": "number",
                    "default": 3,
                    "min": 1,
                    "max": 10,
                    "step": 1
                },
                {
                    "name": "oversold",
                    "label": "Oversold Level",
                    "type": "number",
                    "default": 20,
                    "min": 10,
                    "max": 30,
                    "step": 5
                },
                {
                    "name": "overbought",
                    "label": "Overbought Level",
                    "type": "number",
                    "default": 80,
                    "min": 70,
                    "max": 90,
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
        
        k_period = config.get('k_period', 14)
        d_period = config.get('d_period', 3)
        
        # Calculate %K
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        
        df['stoch_k'] = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        
        # Calculate %D (SMA of %K)
        df['stoch_d'] = df['stoch_k'].rolling(window=d_period).mean()
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 2:
            return False
        
        oversold = config.get('oversold', 20)
        overbought = config.get('overbought', 80)
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['stoch_k']) or pd.isna(curr['stoch_d']):
            return False
        
        if direction == 'LONG':
            # %K crosses above %D in oversold zone
            return (curr['stoch_k'] < oversold and
                    prev['stoch_k'] <= prev['stoch_d'] and
                    curr['stoch_k'] > curr['stoch_d'])
        
        elif direction == 'SHORT':
            # %K crosses below %D in overbought zone
            return (curr['stoch_k'] > overbought and
                    prev['stoch_k'] >= prev['stoch_d'] and
                    curr['stoch_k'] < curr['stoch_d'])
        
        return False