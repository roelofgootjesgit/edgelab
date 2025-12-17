"""
supertrend.py
=============

SuperTrend - ATR-based Trend Indicator

Popular retail indicator combining ATR and price action
Visual trend filter with clear buy/sell signals

Signals:
- Green line below price = Uptrend (LONG)
- Red line above price = Downtrend (SHORT)
- Line flip = Trend change

Parameters:
- atr_period: ATR calculation period (default 10)
- multiplier: ATR multiplier (default 3.0)

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class SuperTrendModule(BaseModule):
    """
    SuperTrend indicator module.
    
    Combines ATR volatility with price action for trend identification.
    Very popular with retail traders for its simplicity.
    
    Trading Logic:
    - LONG: SuperTrend below price (green line)
    - SHORT: SuperTrend above price (red line)
    
    Parameters:
    - atr_period: ATR smoothing (default 10)
    - multiplier: ATR distance multiplier (default 3.0)
    """
    
    @property
    def name(self) -> str:
        return "SuperTrend"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return "ATR-based trend filter. Green = bullish, Red = bearish."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "atr_period",
                    "label": "ATR Period",
                    "type": "number",
                    "default": 10,
                    "min": 5,
                    "max": 50,
                    "step": 5,
                    "help": "Period for ATR calculation"
                },
                {
                    "name": "multiplier",
                    "label": "ATR Multiplier",
                    "type": "number",
                    "default": 3.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.5,
                    "help": "Distance from price (higher = less sensitive)"
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
                raise ValueError(f"Missing required column: {col}")
        
        period = config.get('atr_period', 10)
        multiplier = config.get('multiplier', 3.0)
        
        # Calculate ATR
        df['h-l'] = df['high'] - df['low']
        df['h-pc'] = abs(df['high'] - df['close'].shift(1))
        df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=period).mean()
        
        # Calculate basic bands
        df['hl_avg'] = (df['high'] + df['low']) / 2
        df['upper_band'] = df['hl_avg'] + (multiplier * df['atr'])
        df['lower_band'] = df['hl_avg'] - (multiplier * df['atr'])
        
        # Initialize SuperTrend
        df['supertrend'] = np.nan
        df['supertrend_direction'] = 0  # 1 = uptrend, -1 = downtrend
        
        # Calculate SuperTrend
        for i in range(1, len(df)):
            # Skip if no ATR yet
            if pd.isna(df.loc[i, 'atr']):
                continue
            
            curr_close = df.loc[i, 'close']
            prev_close = df.loc[i-1, 'close']
            
            # Final bands (adjusted)
            if i == 1 or pd.isna(df.loc[i-1, 'supertrend']):
                # First valid value
                if curr_close <= df.loc[i, 'upper_band']:
                    df.loc[i, 'supertrend'] = df.loc[i, 'upper_band']
                    df.loc[i, 'supertrend_direction'] = -1
                else:
                    df.loc[i, 'supertrend'] = df.loc[i, 'lower_band']
                    df.loc[i, 'supertrend_direction'] = 1
            else:
                prev_st = df.loc[i-1, 'supertrend']
                prev_dir = df.loc[i-1, 'supertrend_direction']
                
                # Uptrend logic
                if prev_dir == 1:
                    if curr_close <= df.loc[i, 'lower_band']:
                        # Flip to downtrend
                        df.loc[i, 'supertrend'] = df.loc[i, 'upper_band']
                        df.loc[i, 'supertrend_direction'] = -1
                    else:
                        # Continue uptrend
                        df.loc[i, 'supertrend'] = max(df.loc[i, 'lower_band'], prev_st)
                        df.loc[i, 'supertrend_direction'] = 1
                
                # Downtrend logic
                else:  # prev_dir == -1
                    if curr_close >= df.loc[i, 'upper_band']:
                        # Flip to uptrend
                        df.loc[i, 'supertrend'] = df.loc[i, 'lower_band']
                        df.loc[i, 'supertrend_direction'] = 1
                    else:
                        # Continue downtrend
                        df.loc[i, 'supertrend'] = min(df.loc[i, 'upper_band'], prev_st)
                        df.loc[i, 'supertrend_direction'] = -1
        
        # Cleanup
        df.drop(['h-l', 'h-pc', 'l-pc', 'tr', 'hl_avg', 
                 'upper_band', 'lower_band'], axis=1, inplace=True)
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        row = data.iloc[index]
        
        if pd.isna(row['supertrend']):
            return False
        
        if direction == 'LONG':
            # SuperTrend below price (uptrend)
            return row['supertrend_direction'] == 1
        
        elif direction == 'SHORT':
            # SuperTrend above price (downtrend)
            return row['supertrend_direction'] == -1
        
        return False