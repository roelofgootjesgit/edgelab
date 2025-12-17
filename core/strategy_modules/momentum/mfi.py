"""
mfi.py
======

MFI (Money Flow Index) - Volume-weighted RSI
Combines price and volume for momentum

Measures buying/selling pressure
Volume confirmation of price moves

Signals:
- MFI > 80 = Overbought
- MFI < 20 = Oversold
- Divergences = Reversals

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class MFIModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "MFI (Money Flow Index)"
    
    @property
    def category(self) -> str:
        return "momentum"
    
    @property
    def description(self) -> str:
        return "Volume-weighted RSI. >80 overbought, <20 oversold."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "MFI Period",
                    "type": "number",
                    "default": 14,
                    "min": 5,
                    "max": 50,
                    "step": 1
                },
                {
                    "name": "overbought",
                    "label": "Overbought Level",
                    "type": "number",
                    "default": 80,
                    "min": 70,
                    "max": 90,
                    "step": 5
                },
                {
                    "name": "oversold",
                    "label": "Oversold Level",
                    "type": "number",
                    "default": 20,
                    "min": 10,
                    "max": 30,
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
        
        required = ['high', 'low', 'close', 'volume']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        
        period = config.get('period', 14)
        
        # Typical Price
        df['tp'] = (df['high'] + df['low'] + df['close']) / 3
        
        # Raw Money Flow
        df['raw_mf'] = df['tp'] * df['volume']
        
        # Positive/Negative Money Flow
        df['mf_sign'] = np.where(df['tp'] > df['tp'].shift(1), 1, -1)
        df['positive_mf'] = np.where(df['mf_sign'] == 1, df['raw_mf'], 0)
        df['negative_mf'] = np.where(df['mf_sign'] == -1, df['raw_mf'], 0)
        
        # Sum over period
        positive_mf_sum = df['positive_mf'].rolling(window=period).sum()
        negative_mf_sum = df['negative_mf'].rolling(window=period).sum()
        
        # Money Flow Ratio
        mf_ratio = positive_mf_sum / negative_mf_sum
        
        # MFI
        df['mfi'] = 100 - (100 / (1 + mf_ratio))
        
        # Cleanup
        df.drop(['tp', 'raw_mf', 'mf_sign', 'positive_mf', 'negative_mf'], 
                axis=1, inplace=True)
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        oversold = config.get('oversold', 20)
        overbought = config.get('overbought', 80)
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['mfi']):
            return False
        
        if direction == 'LONG':
            # Crosses above oversold
            return prev['mfi'] < oversold and curr['mfi'] >= oversold
        
        elif direction == 'SHORT':
            # Crosses below overbought
            return prev['mfi'] > overbought and curr['mfi'] <= overbought
        
        return False