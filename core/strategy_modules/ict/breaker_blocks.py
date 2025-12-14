"""
breaker_blocks.py
=================

Breaker Blocks - ICT failed order block conversion
When order blocks fail, they become breaker blocks with reversed polarity

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class BreakerBlockModule(BaseModule):
    """
    Breaker Blocks detection module.
    
    Concept:
    - Order blocks can fail when price breaks through them
    - Failed bullish OB becomes bearish breaker (resistance)
    - Failed bearish OB becomes bullish breaker (support)
    
    Detection:
    1. Identify order blocks (last candle before reversal)
    2. Track when price breaks through OB zone
    3. Convert to breaker block with opposite polarity
    
    Trading Logic:
    - LONG when price returns to bullish breaker
    - SHORT when price returns to bearish breaker
    
    Parameters:
    - min_candles: Minimum reversal candles for OB (default 3)
    - min_move_pct: Minimum move to confirm reversal (default 3%)
    - break_confirmation_pct: Break distance to confirm (default 1%)
    - breaker_validity_candles: How long breaker active (default 50)
    """
    
    @property
    def name(self) -> str:
        return "Breaker Blocks"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT failed order blocks - support becomes resistance"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "min_candles",
                    "label": "Min Reversal Candles",
                    "type": "number",
                    "default": 3,
                    "min": 2,
                    "max": 10,
                    "step": 1,
                    "help": "Minimum candles for OB detection"
                },
                {
                    "name": "min_move_pct",
                    "label": "Min Move (%)",
                    "type": "number",
                    "default": 3.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.5,
                    "help": "Minimum move to confirm OB"
                },
                {
                    "name": "break_confirmation_pct",
                    "label": "Break Confirmation (%)",
                    "type": "number",
                    "default": 1.0,
                    "min": 0.5,
                    "max": 2.0,
                    "step": 0.1,
                    "help": "Distance past OB to confirm break"
                },
                {
                    "name": "breaker_validity_candles",
                    "label": "Breaker Validity (candles)",
                    "type": "number",
                    "default": 50,
                    "min": 20,
                    "max": 100,
                    "step": 10,
                    "help": "How long breaker remains active"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Breaker Blocks.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with breaker columns added
        """
        df = data.copy()
        
        # Extract config
        min_candles = config.get('min_candles', 3)
        min_move_pct = config.get('min_move_pct', 3.0) / 100.0
        break_confirmation_pct = config.get('break_confirmation_pct', 1.0) / 100.0
        breaker_validity = config.get('breaker_validity_candles', 50)
        
        # Initialize columns
        df['bullish_ob'] = False
        df['bearish_ob'] = False
        df['ob_high'] = np.nan
        df['ob_low'] = np.nan
        df['bullish_breaker'] = False
        df['bearish_breaker'] = False
        df['breaker_high'] = np.nan
        df['breaker_low'] = np.nan
        df['in_bullish_breaker'] = False
        df['in_bearish_breaker'] = False
        
        # Track active order blocks and breakers
        active_bullish_obs = []
        active_bearish_obs = []
        active_bullish_breakers = []
        active_bearish_breakers = []
        
        # Phase 1: Detect Order Blocks
        for i in range(min_candles + 1, len(df)):
            # Detect Bullish OB (last green candle before drop)
            current_candle = df.iloc[i-1]
            if current_candle['close'] > current_candle['open']:
                # Check for strong drop after
                consecutive_red = 0
                move_start = df.iloc[i-1]['high']
                move_end = move_start
                
                for j in range(i, min(i + min_candles + 5, len(df))):
                    future_candle = df.iloc[j]
                    if future_candle['close'] < future_candle['open']:
                        consecutive_red += 1
                        move_end = min(move_end, future_candle['low'])
                    else:
                        break
                
                move_pct = abs((move_end - move_start) / move_start)
                
                if consecutive_red >= min_candles or move_pct >= min_move_pct:
                    df.at[i-1, 'bullish_ob'] = True
                    df.at[i-1, 'ob_low'] = current_candle['low']
                    df.at[i-1, 'ob_high'] = current_candle['high']
                    
                    active_bullish_obs.append({
                        'origin': i-1,
                        'low': current_candle['low'],
                        'high': current_candle['high'],
                        'broken': False
                    })
            
            # Detect Bearish OB (last red candle before rally)
            if current_candle['close'] < current_candle['open']:
                # Check for strong rally after
                consecutive_green = 0
                move_start = df.iloc[i-1]['low']
                move_end = move_start
                
                for j in range(i, min(i + min_candles + 5, len(df))):
                    future_candle = df.iloc[j]
                    if future_candle['close'] > future_candle['open']:
                        consecutive_green += 1
                        move_end = max(move_end, future_candle['high'])
                    else:
                        break
                
                move_pct = abs((move_end - move_start) / move_start)
                
                if consecutive_green >= min_candles or move_pct >= min_move_pct:
                    df.at[i-1, 'bearish_ob'] = True
                    df.at[i-1, 'ob_low'] = current_candle['low']
                    df.at[i-1, 'ob_high'] = current_candle['high']
                    
                    active_bearish_obs.append({
                        'origin': i-1,
                        'low': current_candle['low'],
                        'high': current_candle['high'],
                        'broken': False
                    })
        
        # Phase 2: Detect Breaker Blocks (OB breaks)
        for i in range(len(df)):
            current_price = df.iloc[i]['close']
            current_low = df.iloc[i]['low']
            current_high = df.iloc[i]['high']
            
            # Check if bullish OBs are broken (price drops below)
            for ob in active_bullish_obs:
                if ob['broken']:
                    continue
                
                # Break confirmation: close below OB low by threshold
                break_level = ob['low'] * (1 - break_confirmation_pct)
                
                if current_low <= break_level:
                    ob['broken'] = True
                    
                    # Convert to bearish breaker
                    df.at[i, 'bearish_breaker'] = True
                    df.at[i, 'breaker_low'] = ob['low']
                    df.at[i, 'breaker_high'] = ob['high']
                    
                    active_bearish_breakers.append({
                        'origin': i,
                        'low': ob['low'],
                        'high': ob['high'],
                        'expired': False
                    })
            
            # Check if bearish OBs are broken (price rallies above)
            for ob in active_bearish_obs:
                if ob['broken']:
                    continue
                
                # Break confirmation: close above OB high by threshold
                break_level = ob['high'] * (1 + break_confirmation_pct)
                
                if current_high >= break_level:
                    ob['broken'] = True
                    
                    # Convert to bullish breaker
                    df.at[i, 'bullish_breaker'] = True
                    df.at[i, 'breaker_low'] = ob['low']
                    df.at[i, 'breaker_high'] = ob['high']
                    
                    active_bullish_breakers.append({
                        'origin': i,
                        'low': ob['low'],
                        'high': ob['high'],
                        'expired': False
                    })
            
            # Check if current price is in any active breaker zone
            for breaker in active_bullish_breakers:
                if breaker['expired']:
                    continue
                
                # Check validity period
                if i - breaker['origin'] > breaker_validity:
                    breaker['expired'] = True
                    continue
                
                # Check if price in breaker zone
                if breaker['low'] <= current_price <= breaker['high']:
                    df.at[i, 'in_bullish_breaker'] = True
                    df.at[i, 'breaker_low'] = breaker['low']
                    df.at[i, 'breaker_high'] = breaker['high']
            
            for breaker in active_bearish_breakers:
                if breaker['expired']:
                    continue
                
                # Check validity period
                if i - breaker['origin'] > breaker_validity:
                    breaker['expired'] = True
                    continue
                
                # Check if price in breaker zone
                if breaker['low'] <= current_price <= breaker['high']:
                    df.at[i, 'in_bearish_breaker'] = True
                    df.at[i, 'breaker_low'] = breaker['low']
                    df.at[i, 'breaker_high'] = breaker['high']
        
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
            data: DataFrame with breaker calculations
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
            # Enter LONG when price returns to bullish breaker
            return candle['in_bullish_breaker'] == True
        
        elif direction == 'SHORT':
            # Enter SHORT when price returns to bearish breaker
            return candle['in_bearish_breaker'] == True
        
        return False