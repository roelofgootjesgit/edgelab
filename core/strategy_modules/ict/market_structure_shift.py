"""
market_structure_shift.py
=========================

Market Structure Shift (MSS) - ICT trend reversal detection
Identifies when market structure changes from bullish to bearish or vice versa

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class MarketStructureShiftModule(BaseModule):
    """
    Market Structure Shift (MSS) detection module.
    
    Concept:
    - Track swing highs and swing lows
    - Bullish MSS: Price breaks above recent swing high (trend shift to bullish)
    - Bearish MSS: Price breaks below recent swing low (trend shift to bearish)
    
    Swing Point Definition:
    - Swing High: Highest high with lower highs on both sides
    - Swing Low: Lowest low with higher lows on both sides
    
    Trading Logic:
    - LONG after bullish MSS (downtrend ending, uptrend beginning)
    - SHORT after bearish MSS (uptrend ending, downtrend beginning)
    
    Parameters:
    - swing_lookback: Candles each side for swing detection (default 5)
    - break_threshold_pct: Distance to confirm break (default 0.2%)
    - mss_validity_candles: How long MSS signal stays active (default 10)
    """
    
    @property
    def name(self) -> str:
        return "Market Structure Shift (MSS)"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT trend reversals - structure break detection"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "swing_lookback",
                    "label": "Swing Lookback (candles)",
                    "type": "number",
                    "default": 5,
                    "min": 3,
                    "max": 20,
                    "step": 1,
                    "help": "Candles each side for swing detection"
                },
                {
                    "name": "break_threshold_pct",
                    "label": "Break Threshold (%)",
                    "type": "number",
                    "default": 0.2,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1,
                    "help": "Distance to confirm structure break"
                },
                {
                    "name": "mss_validity_candles",
                    "label": "MSS Validity (candles)",
                    "type": "number",
                    "default": 10,
                    "min": 5,
                    "max": 20,
                    "step": 5,
                    "help": "How long MSS signal stays active"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Market Structure Shifts.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with MSS columns added
        """
        df = data.copy()
        
        # Reset index to integer for easier iteration
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        # Extract config
        swing_lookback = config.get('swing_lookback', 5)
        break_threshold_pct = config.get('break_threshold_pct', 0.2) / 100.0
        mss_validity = config.get('mss_validity_candles', 10)
        
        # Initialize columns
        df['swing_high'] = np.nan
        df['swing_low'] = np.nan
        df['is_swing_high'] = False
        df['is_swing_low'] = False
        df['bullish_mss'] = False
        df['bearish_mss'] = False
        df['mss_active'] = False
        df['mss_type'] = ''
        df['recent_swing_high'] = np.nan
        df['recent_swing_low'] = np.nan
        
        # Phase 1: Identify swing highs and lows
        for i in range(swing_lookback, len(df) - swing_lookback):
            current_high = df.iloc[i]['high']
            current_low = df.iloc[i]['low']
            
            # Check if current candle is swing high
            # (highest high with lower highs on both sides)
            left_highs = [df.iloc[j]['high'] for j in range(i - swing_lookback, i)]
            right_highs = [df.iloc[j]['high'] for j in range(i + 1, i + swing_lookback + 1)]
            
            if all(current_high > h for h in left_highs) and all(current_high > h for h in right_highs):
                df.at[i, 'is_swing_high'] = True
                df.at[i, 'swing_high'] = current_high
            
            # Check if current candle is swing low
            # (lowest low with higher lows on both sides)
            left_lows = [df.iloc[j]['low'] for j in range(i - swing_lookback, i)]
            right_lows = [df.iloc[j]['low'] for j in range(i + 1, i + swing_lookback + 1)]
            
            if all(current_low < l for l in left_lows) and all(current_low < l for l in right_lows):
                df.at[i, 'is_swing_low'] = True
                df.at[i, 'swing_low'] = current_low
        
        # Phase 2: Track recent swing points and detect MSS
        recent_swing_high = None
        recent_swing_low = None
        active_mss = []
        
        for i in range(len(df)):
            # Update recent swing points
            if df.iloc[i]['is_swing_high']:
                recent_swing_high = df.iloc[i]['swing_high']
            
            if df.iloc[i]['is_swing_low']:
                recent_swing_low = df.iloc[i]['swing_low']
            
            # Store recent swing levels
            df.at[i, 'recent_swing_high'] = recent_swing_high
            df.at[i, 'recent_swing_low'] = recent_swing_low
            
            current_high = df.iloc[i]['high']
            current_low = df.iloc[i]['low']
            
            # Detect Bullish MSS (break above recent swing high)
            if recent_swing_high is not None:
                break_level = recent_swing_high * (1 + break_threshold_pct)
                
                if current_high >= break_level:
                    df.at[i, 'bullish_mss'] = True
                    df.at[i, 'mss_type'] = 'BULLISH'
                    
                    active_mss.append({
                        'origin': i,
                        'type': 'BULLISH',
                        'expired': False
                    })
                    
                    # Reset recent swing high after break
                    recent_swing_high = None
            
            # Detect Bearish MSS (break below recent swing low)
            if recent_swing_low is not None:
                break_level = recent_swing_low * (1 - break_threshold_pct)
                
                if current_low <= break_level:
                    df.at[i, 'bearish_mss'] = True
                    df.at[i, 'mss_type'] = 'BEARISH'
                    
                    active_mss.append({
                        'origin': i,
                        'type': 'BEARISH',
                        'expired': False
                    })
                    
                    # Reset recent swing low after break
                    recent_swing_low = None
            
            # Check if any MSS is still active
            for mss in active_mss:
                if mss['expired']:
                    continue
                
                # Check validity period
                if i - mss['origin'] > mss_validity:
                    mss['expired'] = True
                    continue
                
                # Mark as active
                df.at[i, 'mss_active'] = True
                if not df.at[i, 'mss_type']:  # Don't overwrite new MSS
                    df.at[i, 'mss_type'] = mss['type']
        
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
            data: DataFrame with MSS calculations
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
            # Enter LONG after bullish MSS (structure shift to bullish)
            return candle['bullish_mss'] == True or (candle['mss_active'] and candle['mss_type'] == 'BULLISH')
        
        elif direction == 'SHORT':
            # Enter SHORT after bearish MSS (structure shift to bearish)
            return candle['bearish_mss'] == True or (candle['mss_active'] and candle['mss_type'] == 'BEARISH')
        
        return False