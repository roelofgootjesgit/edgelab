"""
inducement.py
=============

Inducement - ICT fake breakout detection
Identifies liquidity grabs that trap retail traders

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class InducementModule(BaseModule):
    """
    Inducement detection module.
    
    Concept:
    - Fake breakout designed to trap retail traders
    - Price breaks obvious level (swing high/low)
    - Retail enters expecting breakout continuation
    - Smart money reverses, trapping retail
    - Classic stop hunt + reversal pattern
    
    Bullish Inducement:
    - Price breaks above swing high (fake bullish breakout)
    - Retail goes LONG
    - Price reverses DOWN (trap)
    - Enter SHORT after fake breakout fails
    
    Bearish Inducement:
    - Price breaks below swing low (fake bearish breakdown)
    - Retail goes SHORT
    - Price reverses UP (trap)
    - Enter LONG after fake breakdown fails
    
    Trading Logic:
    - LONG after bearish inducement (fake breakdown reverses)
    - SHORT after bullish inducement (fake breakout reverses)
    - Trade OPPOSITE of the fake move
    
    Parameters:
    - lookback_candles: Swing high/low detection period (default 10)
    - break_threshold_pct: Distance beyond level (default 0.2%)
    - reversal_candles: Candles to confirm reversal (default 2)
    - reversal_pct: Reversal size required (default 0.5%)
    - validity_candles: Signal validity period (default 15)
    """
    
    @property
    def name(self) -> str:
        return "Inducement"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT fake breakouts - retail trader traps"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "lookback_candles",
                    "label": "Lookback Period (candles)",
                    "type": "number",
                    "default": 10,
                    "min": 5,
                    "max": 30,
                    "step": 5,
                    "help": "Period for swing high/low detection"
                },
                {
                    "name": "break_threshold_pct",
                    "label": "Break Threshold (%)",
                    "type": "number",
                    "default": 0.2,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1,
                    "help": "Distance beyond level for fake breakout"
                },
                {
                    "name": "reversal_candles",
                    "label": "Reversal Confirmation (candles)",
                    "type": "number",
                    "default": 2,
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "help": "Candles needed to confirm reversal"
                },
                {
                    "name": "reversal_pct",
                    "label": "Reversal Size (%)",
                    "type": "number",
                    "default": 0.5,
                    "min": 0.2,
                    "max": 2.0,
                    "step": 0.1,
                    "help": "Reversal move size required"
                },
                {
                    "name": "validity_candles",
                    "label": "Signal Validity (candles)",
                    "type": "number",
                    "default": 15,
                    "min": 5,
                    "max": 30,
                    "step": 5,
                    "help": "How long inducement signal active"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Inducement events.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with inducement columns added
        """
        df = data.copy()
        
        # Reset index to integer
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        # Extract config
        lookback = config.get('lookback_candles', 10)
        break_threshold = config.get('break_threshold_pct', 0.2) / 100.0
        reversal_candles = config.get('reversal_candles', 2)
        reversal_pct = config.get('reversal_pct', 0.5) / 100.0
        validity = config.get('validity_candles', 15)
        
        # Initialize columns
        df['swing_high'] = np.nan
        df['swing_low'] = np.nan
        df['bullish_inducement'] = False  # Fake breakout up
        df['bearish_inducement'] = False  # Fake breakdown down
        df['inducement_active'] = False
        df['inducement_type'] = ''
        df['inducement_level'] = np.nan
        
        # Phase 1: Identify swing highs and lows
        for i in range(lookback, len(df) - lookback):
            # Swing high: highest in window
            window_highs = df.iloc[i - lookback:i + lookback + 1]['high']
            if df.loc[i, 'high'] == window_highs.max():
                df.loc[i, 'swing_high'] = df.loc[i, 'high']
            
            # Swing low: lowest in window
            window_lows = df.iloc[i - lookback:i + lookback + 1]['low']
            if df.loc[i, 'low'] == window_lows.min():
                df.loc[i, 'swing_low'] = df.loc[i, 'low']
        
        # Phase 2: Detect inducements (fake breakouts with reversals)
        recent_swing_high = None
        recent_swing_low = None
        
        for i in range(len(df)):
            # Update recent swings
            if not pd.isna(df.loc[i, 'swing_high']):
                recent_swing_high = df.loc[i, 'swing_high']
            if not pd.isna(df.loc[i, 'swing_low']):
                recent_swing_low = df.loc[i, 'swing_low']
            
            # Check for bullish inducement (fake breakout up that reverses down)
            if recent_swing_high is not None:
                break_level = recent_swing_high * (1 + break_threshold)
                
                # Check if we broke above
                if df.loc[i, 'high'] >= break_level:
                    # Check for reversal in next candles
                    reversal_start_idx = i + 1
                    reversal_end_idx = min(i + 1 + reversal_candles, len(df))
                    
                    if reversal_end_idx <= len(df):
                        # Check if reversed back down
                        peak_price = df.loc[i, 'high']
                        future_lows = df.iloc[reversal_start_idx:reversal_end_idx]['low']
                        
                        if not future_lows.empty:
                            lowest_after = future_lows.min()
                            reversal_amount = peak_price - lowest_after
                            reversal_pct_actual = reversal_amount / peak_price
                            
                            if reversal_pct_actual >= reversal_pct:
                                # Bullish inducement confirmed (trap for longs)
                                df.loc[reversal_end_idx - 1, 'bullish_inducement'] = True
                                df.loc[reversal_end_idx - 1, 'inducement_level'] = recent_swing_high
            
            # Check for bearish inducement (fake breakdown down that reverses up)
            if recent_swing_low is not None:
                break_level = recent_swing_low * (1 - break_threshold)
                
                # Check if we broke below
                if df.loc[i, 'low'] <= break_level:
                    # Check for reversal in next candles
                    reversal_start_idx = i + 1
                    reversal_end_idx = min(i + 1 + reversal_candles, len(df))
                    
                    if reversal_end_idx <= len(df):
                        # Check if reversed back up
                        trough_price = df.loc[i, 'low']
                        future_highs = df.iloc[reversal_start_idx:reversal_end_idx]['high']
                        
                        if not future_highs.empty:
                            highest_after = future_highs.max()
                            reversal_amount = highest_after - trough_price
                            reversal_pct_actual = reversal_amount / trough_price
                            
                            if reversal_pct_actual >= reversal_pct:
                                # Bearish inducement confirmed (trap for shorts)
                                df.loc[reversal_end_idx - 1, 'bearish_inducement'] = True
                                df.loc[reversal_end_idx - 1, 'inducement_level'] = recent_swing_low
        
        # Phase 3: Propagate inducement signals
        active_inducement = None
        active_inducement_type = None
        candles_since_inducement = 0
        
        for i in range(len(df)):
            # New inducement detected
            if df.loc[i, 'bullish_inducement']:
                active_inducement = i
                active_inducement_type = 'BULLISH'
                candles_since_inducement = 0
            elif df.loc[i, 'bearish_inducement']:
                active_inducement = i
                active_inducement_type = 'BEARISH'
                candles_since_inducement = 0
            
            # Mark inducement as active
            if active_inducement is not None:
                if candles_since_inducement < validity:
                    df.loc[i, 'inducement_active'] = True
                    df.loc[i, 'inducement_type'] = active_inducement_type
                else:
                    active_inducement = None
                    active_inducement_type = None
                
                candles_since_inducement += 1
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int, config: Dict, direction: str) -> bool:
        """
        Check if entry condition is met at given candle.
        
        Args:
            data: DataFrame with inducement columns
            index: Current candle index
            config: Configuration dictionary
            direction: 'LONG' or 'SHORT'
            
        Returns:
            True if entry condition met
        """
        row = data.iloc[index]
        
        if direction == 'LONG':
            # Enter LONG after bearish inducement (fake breakdown trapped shorts)
            return row['inducement_active'] and row['inducement_type'] == 'BEARISH'
        
        elif direction == 'SHORT':
            # Enter SHORT after bullish inducement (fake breakout trapped longs)
            return row['inducement_active'] and row['inducement_type'] == 'BULLISH'
        
        return False