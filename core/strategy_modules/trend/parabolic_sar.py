"""
parabolic_sar.py
================

Parabolic SAR (Stop and Reverse) - Trend Following System

Developed by J. Welles Wilder Jr.
Provides trailing stop levels that accelerate with trend

Signals:
- SAR below price = Uptrend (LONG)
- SAR above price = Downtrend (SHORT)
- SAR flip = Trend reversal

Parameters:
- acceleration: AF increment (default 0.02)
- maximum: Max AF value (default 0.20)

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class ParabolicSARModule(BaseModule):
    """
    Parabolic SAR (Stop and Reverse) module.
    
    Provides dynamic trailing stops that accelerate with trend.
    SAR flips indicate trend reversals.
    
    Trading Logic:
    - LONG: SAR below price (uptrend)
    - SHORT: SAR above price (downtrend)
    - Exit when SAR flips
    
    Parameters:
    - acceleration: AF step (default 0.02)
    - maximum: Max AF (default 0.20)
    """
    
    @property
    def name(self) -> str:
        return "Parabolic SAR"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return "Stop and Reverse system. SAR below = bullish, SAR above = bearish."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {
                    "name": "acceleration",
                    "label": "Acceleration Factor (AF)",
                    "type": "number",
                    "default": 0.02,
                    "min": 0.01,
                    "max": 0.10,
                    "step": 0.01,
                    "help": "AF increment per period"
                },
                {
                    "name": "maximum",
                    "label": "Maximum AF",
                    "type": "number",
                    "default": 0.20,
                    "min": 0.10,
                    "max": 0.50,
                    "step": 0.05,
                    "help": "Maximum AF value"
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
        
        af_step = config.get('acceleration', 0.02)
        af_max = config.get('maximum', 0.20)
        
        # Initialize
        df['sar'] = np.nan
        df['sar_trend'] = 0  # 1 = uptrend, -1 = downtrend
        
        if len(df) < 2:
            return df
        
        # Start with first trend
        is_uptrend = df.loc[1, 'close'] > df.loc[0, 'close']
        
        if is_uptrend:
            sar = df.loc[0, 'low']
            ep = df.loc[1, 'high']
            trend = 1
        else:
            sar = df.loc[0, 'high']
            ep = df.loc[1, 'low']
            trend = -1
        
        af = af_step
        
        for i in range(1, len(df)):
            df.loc[i, 'sar'] = sar
            df.loc[i, 'sar_trend'] = trend
            
            # Check for reversal
            if trend == 1:  # Uptrend
                if df.loc[i, 'low'] < sar:
                    # Reversal to downtrend
                    trend = -1
                    sar = ep
                    ep = df.loc[i, 'low']
                    af = af_step
                else:
                    # Continue uptrend
                    sar = sar + af * (ep - sar)
                    
                    # Update EP and AF
                    if df.loc[i, 'high'] > ep:
                        ep = df.loc[i, 'high']
                        af = min(af + af_step, af_max)
                    
                    # SAR cannot be above prior lows
                    sar = min(sar, df.loc[i-1, 'low'])
                    if i > 1:
                        sar = min(sar, df.loc[i-2, 'low'])
            
            else:  # Downtrend (trend == -1)
                if df.loc[i, 'high'] > sar:
                    # Reversal to uptrend
                    trend = 1
                    sar = ep
                    ep = df.loc[i, 'high']
                    af = af_step
                else:
                    # Continue downtrend
                    sar = sar + af * (ep - sar)
                    
                    # Update EP and AF
                    if df.loc[i, 'low'] < ep:
                        ep = df.loc[i, 'low']
                        af = min(af + af_step, af_max)
                    
                    # SAR cannot be below prior highs
                    sar = max(sar, df.loc[i-1, 'high'])
                    if i > 1:
                        sar = max(sar, df.loc[i-2, 'high'])
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        row = data.iloc[index]
        prev_row = data.iloc[index - 1]
        
        if direction == 'LONG':
            # SAR below price (uptrend)
            return row['sar_trend'] == 1
        
        elif direction == 'SHORT':
            # SAR above price (downtrend)
            return row['sar_trend'] == -1
        
        return False