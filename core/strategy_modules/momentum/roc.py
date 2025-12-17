"""
roc.py
======

ROC (Rate of Change) - Pure momentum indicator
Measures percent change over period

Shows momentum strength and direction
Leading indicator for trend changes

Signals:
- ROC > 0 = Bullish momentum
- ROC < 0 = Bearish momentum
- Zero crosses = Trend changes

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class ROCModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "ROC (Rate of Change)"
    
    @property
    def category(self) -> str:
        return "momentum"
    
    @property
    def description(self) -> str:
        return "Momentum indicator. >0 bullish, <0 bearish. Zero crosses = trend changes."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "ROC Period",
                    "type": "number",
                    "default": 12,
                    "min": 5,
                    "max": 50,
                    "step": 1
                },
                {
                    "name": "threshold",
                    "label": "Signal Threshold (%)",
                    "type": "number",
                    "default": 0,
                    "min": -5,
                    "max": 5,
                    "step": 1,
                    "help": "Minimum ROC value for signal"
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
        
        required = ['close']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        
        period = config.get('period', 12)
        
        # Calculate ROC
        df['roc'] = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        threshold = config.get('threshold', 0)
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['roc']) or pd.isna(prev['roc']):
            return False
        
        if direction == 'LONG':
            # Crosses above threshold
            return prev['roc'] <= threshold and curr['roc'] > threshold
        
        elif direction == 'SHORT':
            # Crosses below threshold
            return prev['roc'] >= threshold and curr['roc'] < threshold
        
        return False