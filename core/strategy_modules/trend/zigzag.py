"""
zigzag.py - ZigZag
Swing high/low detection, filters noise
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class ZigzagModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "ZigZag"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return "Swing points. Filters out moves smaller than threshold."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "deviation", "label": "Min % Deviation", "type": "number",
                 "default": 5.0, "min": 1.0, "max": 10.0, "step": 0.5}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        deviation = config.get('deviation', 5.0) / 100
        
        # Initialize
        df['zigzag'] = np.nan
        df['zigzag_direction'] = 0  # 1=up, -1=down
        
        if len(df) < 3:
            return df
        
        # Find pivots
        last_pivot_price = df['close'].iloc[0]
        last_pivot_idx = 0
        direction = 0  # 0=unknown, 1=looking for high, -1=looking for low
        
        for i in range(1, len(df)):
            high = df['high'].iloc[i]
            low = df['low'].iloc[i]
            
            if direction == 0:
                # Determine initial direction
                if high > last_pivot_price * (1 + deviation):
                    direction = 1  # Now looking for highs
                    df.loc[df.index[i], 'zigzag'] = high
                    df.loc[df.index[i], 'zigzag_direction'] = 1
                    last_pivot_price = high
                    last_pivot_idx = i
                elif low < last_pivot_price * (1 - deviation):
                    direction = -1  # Now looking for lows
                    df.loc[df.index[i], 'zigzag'] = low
                    df.loc[df.index[i], 'zigzag_direction'] = -1
                    last_pivot_price = low
                    last_pivot_idx = i
            
            elif direction == 1:
                # Looking for higher highs
                if high > last_pivot_price:
                    # Update high
                    df.loc[df.index[last_pivot_idx], 'zigzag'] = np.nan
                    df.loc[df.index[i], 'zigzag'] = high
                    df.loc[df.index[i], 'zigzag_direction'] = 1
                    last_pivot_price = high
                    last_pivot_idx = i
                elif low < last_pivot_price * (1 - deviation):
                    # Reversal to downtrend
                    direction = -1
                    df.loc[df.index[i], 'zigzag'] = low
                    df.loc[df.index[i], 'zigzag_direction'] = -1
                    last_pivot_price = low
                    last_pivot_idx = i
            
            else:  # direction == -1
                # Looking for lower lows
                if low < last_pivot_price:
                    # Update low
                    df.loc[df.index[last_pivot_idx], 'zigzag'] = np.nan
                    df.loc[df.index[i], 'zigzag'] = low
                    df.loc[df.index[i], 'zigzag_direction'] = -1
                    last_pivot_price = low
                    last_pivot_idx = i
                elif high > last_pivot_price * (1 + deviation):
                    # Reversal to uptrend
                    direction = 1
                    df.loc[df.index[i], 'zigzag'] = high
                    df.loc[df.index[i], 'zigzag_direction'] = 1
                    last_pivot_price = high
                    last_pivot_idx = i
        
        # Forward fill direction
        df['zigzag_direction'] = df['zigzag_direction'].replace(0, np.nan).fillna(method='ffill').fillna(0)
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 2:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        # Entry on ZigZag reversal
        if direction == 'LONG':
            # ZigZag switched to uptrend
            return (not pd.isna(curr['zigzag']) and 
                    curr['zigzag_direction'] == 1 and
                    prev['zigzag_direction'] != 1)
        
        else:  # SHORT
            # ZigZag switched to downtrend
            return (not pd.isna(curr['zigzag']) and 
                    curr['zigzag_direction'] == -1 and
                    prev['zigzag_direction'] != -1)