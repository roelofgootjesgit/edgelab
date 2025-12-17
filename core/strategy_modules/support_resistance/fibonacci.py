"""
fibonacci.py - Fibonacci Retracement
Auto-calculated fib levels from swing high/low
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class FibonacciModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Fibonacci"
    
    @property
    def category(self) -> str:
        return "support_resistance"
    
    @property
    def description(self) -> str:
        return "Auto Fibonacci levels. Price at 61.8% = key level."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "lookback", "label": "Swing Lookback", "type": "number",
                 "default": 50, "min": 20, "max": 200,
                 "help": "Period to find swing high/low"}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        lookback = config.get('lookback', 50)
        
        # Find swing high/low
        df['swing_high'] = df['high'].rolling(window=lookback).max()
        df['swing_low'] = df['low'].rolling(window=lookback).min()
        
        # Calculate range
        df['fib_range'] = df['swing_high'] - df['swing_low']
        
        # Fibonacci retracement levels (from high to low)
        df['fib_0'] = df['swing_high']
        df['fib_236'] = df['swing_high'] - (df['fib_range'] * 0.236)
        df['fib_382'] = df['swing_high'] - (df['fib_range'] * 0.382)
        df['fib_50'] = df['swing_high'] - (df['fib_range'] * 0.50)
        df['fib_618'] = df['swing_high'] - (df['fib_range'] * 0.618)
        df['fib_786'] = df['swing_high'] - (df['fib_range'] * 0.786)
        df['fib_100'] = df['swing_low']
        
        # Cleanup
        df = df.drop(columns=['swing_high', 'swing_low', 'fib_range'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 2:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['fib_618']):
            return False
        
        price = curr['close']
        prev_price = prev['close']
        
        # Key fib levels
        key_levels = [curr['fib_382'], curr['fib_50'], curr['fib_618']]
        
        if direction == 'LONG':
            # Bounce from key fib level
            for level in key_levels:
                if abs(prev_price - level) < level * 0.005:  # Within 0.5%
                    if price > prev_price:
                        return True
            return False
        
        else:
            # Rejection from key fib level
            for level in key_levels:
                if abs(prev_price - level) < level * 0.005:
                    if price < prev_price:
                        return True
            return False