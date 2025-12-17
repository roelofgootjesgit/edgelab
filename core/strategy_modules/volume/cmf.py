"""
cmf.py - CMF (Chaikin Money Flow)
Volume-weighted buying/selling pressure
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class CMFModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "CMF"
    
    @property
    def category(self) -> str:
        return "volume"
    
    @property
    def description(self) -> str:
        return "Chaikin Money Flow. CMF > 0 = buying pressure."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Period", "type": "number",
                 "default": 20, "min": 10, "max": 50},
                {"name": "threshold", "label": "Signal Threshold", "type": "number",
                 "default": 0.05, "min": 0.0, "max": 0.2, "step": 0.05}
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
        
        # Money Flow Multiplier
        clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
        clv = clv.fillna(0)
        
        # Money Flow Volume
        df['mfv'] = clv * df['volume']
        
        # CMF = sum(MFV) / sum(Volume)
        df['cmf'] = (
            df['mfv'].rolling(window=period).sum() / 
            df['volume'].rolling(window=period).sum()
        )
        
        # Cleanup
        df = df.drop(columns=['mfv'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['cmf']):
            return False
        
        threshold = config.get('threshold', 0.05)
        
        if direction == 'LONG':
            # CMF crosses above threshold (buying pressure)
            return curr['cmf'] > threshold and prev['cmf'] <= threshold
        
        else:
            # CMF crosses below -threshold (selling pressure)
            return curr['cmf'] < -threshold and prev['cmf'] >= -threshold