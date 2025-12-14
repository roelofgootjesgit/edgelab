"""
liquidity_sweep.py
==================

Liquidity Sweep - ICT stop hunt detection
Identifies when price spikes through key levels to trigger stops, then reverses

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class LiquiditySweepModule(BaseModule):
    """
    Liquidity Sweep detection module.
    
    Concept:
    - Bullish Sweep: Price breaks below recent low, then reverses up
      Indicates stop hunt below support before institutional buying
    
    - Bearish Sweep: Price breaks above recent high, then reverses down
      Indicates stop hunt above resistance before institutional selling
    
    Trading Logic:
    - LONG after bullish sweep (fake breakdown, real reversal up)
    - SHORT after bearish sweep (fake breakout, real reversal down)
    
    Parameters:
    - lookback_candles: Period to find swing highs/lows (default 20)
    - sweep_threshold_pct: How far price must exceed level (default 0.2%)
    - reversal_candles: How quickly must reverse (default 3)
    - reversal_strength_pct: Minimum reversal size (default 0.5%)
    """
    
    @property
    def name(self) -> str:
        return "Liquidity Sweep"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT stop hunts - fake breakouts before reversal"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "lookback_candles",
                    "label": "Lookback Period (candles)",
                    "type": "number",
                    "default": 20,
                    "min": 10,
                    "max": 50,
                    "step": 5,
                    "help": "Period to identify swing highs/lows"
                },
                {
                    "name": "sweep_threshold_pct",
                    "label": "Sweep Threshold (%)",
                    "type": "number",
                    "default": 0.2,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1,
                    "help": "How far price must exceed level"
                },
                {
                    "name": "reversal_candles",
                    "label": "Reversal Window (candles)",
                    "type": "number",
                    "default": 3,
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "help": "Candles allowed for reversal"
                },
                {
                    "name": "reversal_strength_pct",
                    "label": "Reversal Strength (%)",
                    "type": "number",
                    "default": 0.5,
                    "min": 0.3,
                    "max": 2.0,
                    "step": 0.1,
                    "help": "Minimum reversal size to confirm"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Liquidity Sweeps.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with sweep columns added
        """
        df = data.copy()
        
        # Extract config
        lookback = config.get('lookback_candles', 20)
        sweep_threshold_pct = config.get('sweep_threshold_pct', 0.2) / 100.0
        reversal_candles = config.get('reversal_candles', 3)
        reversal_strength_pct = config.get('reversal_strength_pct', 0.5) / 100.0
        
        # Initialize columns
        df['swing_high'] = np.nan
        df['swing_low'] = np.nan
        df['bullish_sweep'] = False
        df['bearish_sweep'] = False
        df['sweep_active'] = False
        df['sweep_type'] = ''
        
        # Calculate swing highs and lows
        for i in range(lookback, len(df)):
            # Swing high: highest high in lookback period
            lookback_highs = df.iloc[i-lookback:i]['high']
            swing_high = lookback_highs.max()
            df.at[i, 'swing_high'] = swing_high
            
            # Swing low: lowest low in lookback period
            lookback_lows = df.iloc[i-lookback:i]['low']
            swing_low = lookback_lows.min()
            df.at[i, 'swing_low'] = swing_low
        
        # Detect sweeps
        for i in range(lookback + reversal_candles, len(df)):
            current_high = df.iloc[i]['high']
            current_low = df.iloc[i]['low']
            current_close = df.iloc[i]['close']
            
            # Get swing levels from previous candles
            prev_swing_high = df.iloc[i-1]['swing_high']
            prev_swing_low = df.iloc[i-1]['swing_low']
            
            if pd.isna(prev_swing_high) or pd.isna(prev_swing_low):
                continue
            
            # Check for Bearish Sweep (break above high, then reverse down)
            # 1. Price must exceed swing high by threshold
            sweep_high_level = prev_swing_high * (1 + sweep_threshold_pct)
            if current_high >= sweep_high_level:
                # 2. Check for reversal within next N candles
                reversal_detected = False
                
                for j in range(i, min(i + reversal_candles + 1, len(df))):
                    future_close = df.iloc[j]['close']
                    future_low = df.iloc[j]['low']
                    
                    # Reversal: price moves back below swing high significantly
                    reversal_target = prev_swing_high * (1 - reversal_strength_pct)
                    if future_low <= reversal_target:
                        reversal_detected = True
                        df.at[i, 'bearish_sweep'] = True
                        df.at[i, 'sweep_type'] = 'BEARISH'
                        
                        # Mark next candles as sweep active
                        for k in range(i, min(j + 1, len(df))):
                            df.at[k, 'sweep_active'] = True
                        break
            
            # Check for Bullish Sweep (break below low, then reverse up)
            # 1. Price must go below swing low by threshold
            sweep_low_level = prev_swing_low * (1 - sweep_threshold_pct)
            if current_low <= sweep_low_level:
                # 2. Check for reversal within next N candles
                reversal_detected = False
                
                for j in range(i, min(i + reversal_candles + 1, len(df))):
                    future_close = df.iloc[j]['close']
                    future_high = df.iloc[j]['high']
                    
                    # Reversal: price moves back above swing low significantly
                    reversal_target = prev_swing_low * (1 + reversal_strength_pct)
                    if future_high >= reversal_target:
                        reversal_detected = True
                        df.at[i, 'bullish_sweep'] = True
                        df.at[i, 'sweep_type'] = 'BULLISH'
                        
                        # Mark next candles as sweep active
                        for k in range(i, min(j + 1, len(df))):
                            df.at[k, 'sweep_active'] = True
                        break
        
        return df
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict,
        direction: str
    ) -> bool:
        """
        Check if entry condition is met at given index.
        
        Args:
            data: DataFrame with sweep calculations
            index: Current candle index
            config: Configuration dictionary
            direction: 'LONG' or 'SHORT'
            
        Returns:
            True if entry condition met
        """
        if index >= len(data):
            return False
        
        candle = data.iloc[index]
        
        if direction == 'LONG':
            # Enter LONG after bullish sweep detected
            return candle['bullish_sweep'] == True
        
        elif direction == 'SHORT':
            # Enter SHORT after bearish sweep detected
            return candle['bearish_sweep'] == True
        
        return False