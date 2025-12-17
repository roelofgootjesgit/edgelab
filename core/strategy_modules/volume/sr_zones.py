"""
sr_zones.py - Support/Resistance Zones
Auto-detected S/R levels from price action
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class SRZonesModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "S/R Zones"
    
    @property
    def category(self) -> str:
        return "support_resistance"
    
    @property
    def description(self) -> str:
        return "Auto S/R detection. Price at zone = reaction expected."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "lookback", "label": "Lookback Period", "type": "number",
                 "default": 100, "min": 50, "max": 300},
                {"name": "zone_strength", "label": "Min Zone Touches", "type": "number",
                 "default": 3, "min": 2, "max": 5}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        lookback = config.get('lookback', 100)
        min_touches = config.get('zone_strength', 3)
        
        # Find local highs and lows (simple pivot detection)
        df['pivot_high'] = (
            (df['high'] > df['high'].shift(1)) & 
            (df['high'] > df['high'].shift(-1))
        )
        df['pivot_low'] = (
            (df['low'] < df['low'].shift(1)) & 
            (df['low'] < df['low'].shift(-1))
        )
        
        # Initialize SR zone columns
        df['resistance_zone'] = np.nan
        df['support_zone'] = np.nan
        df['at_resistance'] = False
        df['at_support'] = False
        
        # For each row, find nearest resistance/support
        for i in range(lookback, len(df)):
            window = df.iloc[i-lookback:i]
            current_price = df.iloc[i]['close']
            
            # Find resistance (pivot highs above current price)
            resistances = window[window['pivot_high']]['high']
            if len(resistances) >= min_touches:
                nearest_resistance = resistances[resistances > current_price].min()
                if not pd.isna(nearest_resistance):
                    df.at[df.index[i], 'resistance_zone'] = nearest_resistance
                    # Check if price is near resistance
                    if abs(current_price - nearest_resistance) < nearest_resistance * 0.003:
                        df.at[df.index[i], 'at_resistance'] = True
            
            # Find support (pivot lows below current price)
            supports = window[window['pivot_low']]['low']
            if len(supports) >= min_touches:
                nearest_support = supports[supports < current_price].max()
                if not pd.isna(nearest_support):
                    df.at[df.index[i], 'support_zone'] = nearest_support
                    # Check if price is near support
                    if abs(current_price - nearest_support) < nearest_support * 0.003:
                        df.at[df.index[i], 'at_support'] = True
        
        # Cleanup
        df = df.drop(columns=['pivot_high', 'pivot_low'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 2:
            return False
        
        curr = data.iloc[index]
        prev = data.iloc[index - 1]
        
        if direction == 'LONG':
            # Bounce from support zone
            return prev['at_support'] and curr['close'] > prev['close']
        
        else:
            # Rejection from resistance zone
            return prev['at_resistance'] and curr['close'] < prev['close']