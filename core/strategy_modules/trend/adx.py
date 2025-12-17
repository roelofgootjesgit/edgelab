"""
adx.py
======

ADX (Average Directional Index) - Trend Strength Indicator

Developed by J. Welles Wilder Jr.
Measures trend strength regardless of direction (0-100 scale)

Components:
- ADX: Trend strength (0-100)
- +DI: Positive Directional Indicator
- -DI: Negative Directional Indicator

Signals:
- ADX > 25: Strong trend (good for trading)
- ADX < 20: Weak trend (avoid trading)
- +DI > -DI: Bullish direction
- -DI > +DI: Bearish direction

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class ADXModule(BaseModule):
    """
    Average Directional Index (ADX) module.
    
    Measures trend strength and direction.
    Essential for filtering choppy markets.
    
    Trading Logic:
    - LONG: ADX > threshold AND +DI > -DI
    - SHORT: ADX > threshold AND -DI > +DI
    - Optional: Require recent DI crossover
    
    Parameters:
    - period: Smoothing period (default 14)
    - adx_threshold: Strong trend threshold (default 25)
    - use_di_cross: Require DI crossover (default True)
    """
    
    @property
    def name(self) -> str:
        return "ADX (Average Directional Index)"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return "Measures trend strength. ADX > 25 = strong trend. +DI/-DI shows direction."
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "ADX Period",
                    "type": "number",
                    "default": 14,
                    "min": 5,
                    "max": 50,
                    "step": 1,
                    "help": "Smoothing period for ADX calculation"
                },
                {
                    "name": "adx_threshold",
                    "label": "Strong Trend Threshold",
                    "type": "number",
                    "default": 25,
                    "min": 10,
                    "max": 50,
                    "step": 5,
                    "help": "ADX value above which trend is considered strong"
                },
                {
                    "name": "use_di_cross",
                    "label": "Require DI Crossover",
                    "type": "boolean",
                    "default": True,
                    "help": "Require +DI/-DI crossover for entry signals"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate ADX, +DI, -DI indicators.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with ADX columns added
        """
        df = data.copy()
        
        # Reset index to integer (QuantMetrics pattern)
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        # Validate required columns
        required = ['high', 'low', 'close']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        period = config.get('period', 14)
        
        # Step 1: Calculate True Range (TR)
        df['h-l'] = df['high'] - df['low']
        df['h-pc'] = abs(df['high'] - df['close'].shift(1))
        df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        
        # Step 2: Calculate Directional Movements
        df['h_diff'] = df['high'] - df['high'].shift(1)
        df['l_diff'] = df['low'].shift(1) - df['low']
        
        # +DM and -DM
        df['plus_dm'] = np.where(
            (df['h_diff'] > df['l_diff']) & (df['h_diff'] > 0),
            df['h_diff'],
            0
        )
        df['minus_dm'] = np.where(
            (df['l_diff'] > df['h_diff']) & (df['l_diff'] > 0),
            df['l_diff'],
            0
        )
        
        # Step 3: Wilder's Smoothing (EMA with alpha = 1/period)
        alpha = 1.0 / period
        
        atr = df['tr'].ewm(alpha=alpha, adjust=False).mean()
        plus_dm_smooth = df['plus_dm'].ewm(alpha=alpha, adjust=False).mean()
        minus_dm_smooth = df['minus_dm'].ewm(alpha=alpha, adjust=False).mean()
        
        # Step 4: Calculate Directional Indicators
        df['plus_di'] = 100 * (plus_dm_smooth / atr)
        df['minus_di'] = 100 * (minus_dm_smooth / atr)
        
        # Step 5: Calculate DX
        di_sum = df['plus_di'] + df['minus_di']
        di_diff = abs(df['plus_di'] - df['minus_di'])
        dx = 100 * (di_diff / di_sum)
        
        # Step 6: Calculate ADX (smoothed DX)
        df['adx'] = dx.ewm(alpha=alpha, adjust=False).mean()
        
        # Cleanup temporary columns
        df.drop(['h-l', 'h-pc', 'l-pc', 'h_diff', 'l_diff', 
                 'plus_dm', 'minus_dm'], axis=1, inplace=True)
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int, 
                             config: Dict, direction: str) -> bool:
        """
        Check if ADX entry condition is met.
        
        LONG Entry:
        - ADX > threshold (strong trend)
        - +DI > -DI (bullish direction)
        - Optional: +DI crossed above -DI recently
        
        SHORT Entry:
        - ADX > threshold (strong trend)
        - -DI > +DI (bearish direction)
        - Optional: -DI crossed above +DI recently
        
        Args:
            data: DataFrame with ADX columns
            index: Current candle index
            config: Configuration dictionary
            direction: 'LONG' or 'SHORT'
            
        Returns:
            True if entry condition met
        """
        if index < 2:
            return False
        
        # Extract config
        threshold = config.get('adx_threshold', 25)
        use_di_cross = config.get('use_di_cross', True)
        
        row = data.iloc[index]
        
        # Check ADX strength
        if row['adx'] < threshold:
            return False
        
        if direction == 'LONG':
            # Require +DI > -DI
            if row['plus_di'] <= row['minus_di']:
                return False
            
            # Optional: Check for recent crossover
            if use_di_cross:
                crossed = False
                for i in range(max(0, index - 3), index + 1):
                    curr = data.iloc[i]
                    prev = data.iloc[i - 1] if i > 0 else None
                    
                    if prev is not None:
                        if (prev['plus_di'] <= prev['minus_di'] and
                            curr['plus_di'] > curr['minus_di']):
                            crossed = True
                            break
                
                return crossed
            
            return True
        
        elif direction == 'SHORT':
            # Require -DI > +DI
            if row['minus_di'] <= row['plus_di']:
                return False
            
            # Optional: Check for recent crossover
            if use_di_cross:
                crossed = False
                for i in range(max(0, index - 3), index + 1):
                    curr = data.iloc[i]
                    prev = data.iloc[i - 1] if i > 0 else None
                    
                    if prev is not None:
                        if (prev['minus_di'] <= prev['plus_di'] and
                            curr['minus_di'] > curr['plus_di']):
                            crossed = True
                            break
                
                return crossed
            
            return True
        
        return False