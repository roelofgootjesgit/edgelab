"""
ichimoku.py - Ichimoku Cloud
Comprehensive trend system with multiple components
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class IchimokuModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Ichimoku Cloud"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return "Comprehensive trend. Price above cloud = bullish."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "tenkan_period", "label": "Tenkan (Conversion)", "type": "number",
                 "default": 9, "min": 5, "max": 20},
                {"name": "kijun_period", "label": "Kijun (Base)", "type": "number",
                 "default": 26, "min": 10, "max": 50},
                {"name": "senkou_b_period", "label": "Senkou B (Leading)", "type": "number",
                 "default": 52, "min": 30, "max": 100}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        tenkan = config.get('tenkan_period', 9)
        kijun = config.get('kijun_period', 26)
        senkou_b = config.get('senkou_b_period', 52)
        
        # Tenkan-sen (Conversion Line)
        high_tenkan = df['high'].rolling(window=tenkan).max()
        low_tenkan = df['low'].rolling(window=tenkan).min()
        df['tenkan_sen'] = (high_tenkan + low_tenkan) / 2
        
        # Kijun-sen (Base Line)
        high_kijun = df['high'].rolling(window=kijun).max()
        low_kijun = df['low'].rolling(window=kijun).min()
        df['kijun_sen'] = (high_kijun + low_kijun) / 2
        
        # Senkou Span A (Leading Span A) - shifted forward
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(kijun)
        
        # Senkou Span B (Leading Span B) - shifted forward
        high_senkou = df['high'].rolling(window=senkou_b).max()
        low_senkou = df['low'].rolling(window=senkou_b).min()
        df['senkou_span_b'] = ((high_senkou + low_senkou) / 2).shift(kijun)
        
        # Chikou Span (Lagging Span) - price shifted back
        df['chikou_span'] = df['close'].shift(-kijun)
        
        # Cloud color
        df['cloud_color'] = np.where(df['senkou_span_a'] > df['senkou_span_b'], 'green', 'red')
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 2:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        # Check all components exist
        cols = ['tenkan_sen', 'kijun_sen', 'senkou_span_a', 'senkou_span_b']
        if any(pd.isna(curr[col]) for col in cols):
            return False
        
        price = curr['close']
        cloud_top = max(curr['senkou_span_a'], curr['senkou_span_b'])
        cloud_bottom = min(curr['senkou_span_a'], curr['senkou_span_b'])
        
        if direction == 'LONG':
            # Price above cloud, Tenkan > Kijun, green cloud
            return (price > cloud_top and 
                    curr['tenkan_sen'] > curr['kijun_sen'] and
                    curr['cloud_color'] == 'green')
        
        else:  # SHORT
            # Price below cloud, Tenkan < Kijun, red cloud
            return (price < cloud_bottom and 
                    curr['tenkan_sen'] < curr['kijun_sen'] and
                    curr['cloud_color'] == 'red')