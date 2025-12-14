"""
mitigation_blocks.py
====================

Mitigation Blocks - ICT Order Block confirmation via return
Identifies OBs that price returns to and validates

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class MitigationBlocksModule(BaseModule):
    """
    Mitigation Blocks detection module.
    
    Concept:
    - Order Block that price RETURNS to and VALIDATES
    - Not just detection, requires confirmation
    - Price must return to OB zone (mitigation)
    - Must hold as support/resistance (validation)
    
    Process:
    1. Detect Order Block (last bull/bear before reversal)
    2. Wait for price to LEAVE the OB zone
    3. Wait for price to RETURN to OB zone (mitigation)
    4. Confirm OB holds (price respects zone)
    
    Bullish Mitigation:
    - Bullish OB detected (last green before drop)
    - Price leaves zone, then returns
    - Zone acts as support (holds)
    
    Bearish Mitigation:
    - Bearish OB detected (last red before rally)
    - Price leaves zone, then returns
    - Zone acts as resistance (holds)
    
    Trading Logic:
    - LONG after bullish mitigation (confirmed support)
    - SHORT after bearish mitigation (confirmed resistance)
    
    Parameters:
    - min_candles: Reversal candles for OB (default 3)
    - min_move_pct: Reversal move size (default 2%)
    - mitigation_validity: How long mitigation stays active (default 20)
    - hold_candles: Candles zone must hold (default 2)
    """
    
    @property
    def name(self) -> str:
        return "Mitigation Blocks"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT Order Block confirmation - validated support/resistance"
    
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
                    "help": "Candles needed for OB reversal"
                },
                {
                    "name": "min_move_pct",
                    "label": "Min Reversal Move (%)",
                    "type": "number",
                    "default": 2.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.5,
                    "help": "Reversal move size required"
                },
                {
                    "name": "mitigation_validity",
                    "label": "Mitigation Validity (candles)",
                    "type": "number",
                    "default": 20,
                    "min": 10,
                    "max": 50,
                    "step": 5,
                    "help": "How long mitigation signal active"
                },
                {
                    "name": "hold_candles",
                    "label": "Hold Confirmation (candles)",
                    "type": "number",
                    "default": 2,
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "help": "Candles zone must hold"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Mitigation Blocks.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with mitigation block columns added
        """
        df = data.copy()
        
        # Reset index to integer
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        # Extract config
        min_candles = config.get('min_candles', 3)
        min_move_pct = config.get('min_move_pct', 2.0) / 100.0
        mitigation_validity = config.get('mitigation_validity', 20)
        hold_candles = config.get('hold_candles', 2)
        
        # Initialize columns
        df['order_block'] = False
        df['ob_type'] = ''
        df['ob_high'] = np.nan
        df['ob_low'] = np.nan
        df['bullish_mitigation'] = False
        df['bearish_mitigation'] = False
        df['mitigation_active'] = False
        df['mitigation_type'] = ''
        df['in_mitigation_zone'] = False
        
        # Phase 1: Detect Order Blocks
        for i in range(1, len(df) - min_candles):
            current = df.iloc[i]
            
            # Check for bullish OB (last green before drop)
            if current['close'] > current['open']:
                # Check next candles for drop
                drop_count = 0
                drop_amount = 0
                
                for j in range(i + 1, min(i + 1 + min_candles, len(df))):
                    next_candle = df.iloc[j]
                    if next_candle['close'] < next_candle['open']:
                        drop_count += 1
                    drop_amount = current['high'] - df.iloc[i + 1:min(i + 1 + min_candles, len(df))]['low'].min()
                
                drop_pct = drop_amount / current['high'] if current['high'] > 0 else 0
                
                if drop_count >= min_candles and drop_pct >= min_move_pct:
                    df.loc[i, 'order_block'] = True
                    df.loc[i, 'ob_type'] = 'BULLISH'
                    df.loc[i, 'ob_low'] = current['low']
                    df.loc[i, 'ob_high'] = current['high']
            
            # Check for bearish OB (last red before rally)
            elif current['close'] < current['open']:
                # Check next candles for rally
                rally_count = 0
                rally_amount = 0
                
                for j in range(i + 1, min(i + 1 + min_candles, len(df))):
                    next_candle = df.iloc[j]
                    if next_candle['close'] > next_candle['open']:
                        rally_count += 1
                    rally_amount = df.iloc[i + 1:min(i + 1 + min_candles, len(df))]['high'].max() - current['low']
                
                rally_pct = rally_amount / current['low'] if current['low'] > 0 else 0
                
                if rally_count >= min_candles and rally_pct >= min_move_pct:
                    df.loc[i, 'order_block'] = True
                    df.loc[i, 'ob_type'] = 'BEARISH'
                    df.loc[i, 'ob_low'] = current['low']
                    df.loc[i, 'ob_high'] = current['high']
        
        # Phase 2: Track OBs and detect mitigation
        active_obs = []  # List of {'index': i, 'type': 'BULLISH/BEARISH', 'high': X, 'low': Y, 'left': False, 'mitigation_index': None}
        
        for i in range(len(df)):
            # Add new OBs to tracking
            if df.loc[i, 'order_block']:
                active_obs.append({
                    'index': i,
                    'type': df.loc[i, 'ob_type'],
                    'high': df.loc[i, 'ob_high'],
                    'low': df.loc[i, 'ob_low'],
                    'left': False,
                    'mitigation_index': None,
                    'hold_count': 0
                })
            
            current_high = df.loc[i, 'high']
            current_low = df.loc[i, 'low']
            current_close = df.loc[i, 'close']
            
            # Check existing OBs
            remaining_obs = []
            for ob in active_obs:
                # Check if price left the zone
                if not ob['left']:
                    if ob['type'] == 'BULLISH':
                        if current_low < ob['low']:
                            ob['left'] = True
                    else:  # BEARISH
                        if current_high > ob['high']:
                            ob['left'] = True
                
                # Check if price returned (mitigation)
                if ob['left'] and ob['mitigation_index'] is None:
                    # Price must return to zone
                    in_zone = current_low <= ob['high'] and current_high >= ob['low']
                    
                    if in_zone:
                        if ob['type'] == 'BULLISH':
                            # Check if holding as support
                            if current_close >= ob['low']:
                                ob['hold_count'] += 1
                                if ob['hold_count'] >= hold_candles:
                                    ob['mitigation_index'] = i
                                    df.loc[i, 'bullish_mitigation'] = True
                        else:  # BEARISH
                            # Check if holding as resistance
                            if current_close <= ob['high']:
                                ob['hold_count'] += 1
                                if ob['hold_count'] >= hold_candles:
                                    ob['mitigation_index'] = i
                                    df.loc[i, 'bearish_mitigation'] = True
                    else:
                        ob['hold_count'] = 0  # Reset if left zone again
                
                # Keep tracking if not too old
                age = i - ob['index']
                if age < 100:  # Keep OBs for max 100 candles
                    remaining_obs.append(ob)
            
            active_obs = remaining_obs
        
        # Phase 3: Propagate mitigation signals
        active_mitigation = None
        active_mitigation_type = None
        candles_since_mitigation = 0
        
        for i in range(len(df)):
            # New mitigation detected
            if df.loc[i, 'bullish_mitigation']:
                active_mitigation = i
                active_mitigation_type = 'BULLISH'
                candles_since_mitigation = 0
            elif df.loc[i, 'bearish_mitigation']:
                active_mitigation = i
                active_mitigation_type = 'BEARISH'
                candles_since_mitigation = 0
            
            # Mark mitigation as active
            if active_mitigation is not None:
                if candles_since_mitigation < mitigation_validity:
                    df.loc[i, 'mitigation_active'] = True
                    df.loc[i, 'mitigation_type'] = active_mitigation_type
                    df.loc[i, 'in_mitigation_zone'] = True
                else:
                    active_mitigation = None
                    active_mitigation_type = None
                
                candles_since_mitigation += 1
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int, config: Dict, direction: str) -> bool:
        """
        Check if entry condition is met at given candle.
        
        Args:
            data: DataFrame with mitigation columns
            index: Current candle index
            config: Configuration dictionary
            direction: 'LONG' or 'SHORT'
            
        Returns:
            True if entry condition met
        """
        row = data.iloc[index]
        
        if direction == 'LONG':
            # Enter LONG after bullish mitigation (confirmed support)
            return row['mitigation_active'] and row['mitigation_type'] == 'BULLISH'
        
        elif direction == 'SHORT':
            # Enter SHORT after bearish mitigation (confirmed resistance)
            return row['mitigation_active'] and row['mitigation_type'] == 'BEARISH'
        
        return False