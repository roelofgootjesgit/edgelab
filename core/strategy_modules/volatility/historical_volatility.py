"""
historical_volatility.py - Historical Volatility
Annualized price volatility percentage
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class HistoricalVolatilityModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Historical Volatility"
    
    @property
    def category(self) -> str:
        return "volatility"
    
    @property
    def description(self) -> str:
        return "Annualized volatility %. High HV = high risk/reward."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Period", "type": "number",
                 "default": 20, "min": 10, "max": 100},
                {"name": "threshold", "label": "High Vol %", "type": "number",
                 "default": 30, "min": 10, "max": 100}
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
        
        # Log returns
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        # Standard deviation of log returns
        df['hv_std'] = df['log_return'].rolling(window=period).std()
        
        # Annualized (assuming 252 trading days)
        df['hv'] = df['hv_std'] * np.sqrt(252) * 100
        
        # Percentile rank
        df['hv_percentile'] = df['hv'].rolling(window=100).apply(
            lambda x: (x.iloc[-1] <= x).sum() / len(x) * 100, raw=False
        )
        
        # Cleanup
        df = df.drop(columns=['log_return', 'hv_std'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if pd.isna(curr['hv']):
            return False
        
        threshold = config.get('threshold', 30)
        
        # High volatility breakout
        high_vol = curr['hv'] > threshold
        
        if not high_vol:
            return False
        
        if direction == 'LONG':
            return curr['close'] > prev['close']
        else:
            return curr['close'] < prev['close']