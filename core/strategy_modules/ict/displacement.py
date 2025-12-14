"""
displacement.py
===============

Displacement - ICT institutional momentum detection
Identifies strong, decisive moves indicating institutional conviction

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class DisplacementModule(BaseModule):
    """
    Displacement detection module.
    
    Concept:
    - Strong institutional moves with conviction
    - Large candle bodies (minimal wicks)
    - Rapid directional movement
    - Often leaves Fair Value Gaps
    
    Bullish Displacement:
    - Multiple consecutive bullish candles
    - Large bodies (70%+ of candle range)
    - Significant upward price movement
    
    Bearish Displacement:
    - Multiple consecutive bearish candles
    - Large bodies (70%+ of candle range)
    - Significant downward price movement
    
    Trading Logic:
    - LONG after bullish displacement (institutional buying)
    - SHORT after bearish displacement (institutional selling)
    
    Parameters:
    - min_body_pct: Minimum body size vs range (default 70%)
    - min_candles: Consecutive strong candles (default 3)
    - min_move_pct: Minimum total price move (default 1.5%)
    - validity_candles: Signal validity period (default 10)
    """
    
    @property
    def name(self) -> str:
        return "Displacement"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT institutional momentum - strong directional moves"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "min_body_pct",
                    "label": "Min Body Size (%)",
                    "type": "number",
                    "default": 70,
                    "min": 50,
                    "max": 90,
                    "step": 5,
                    "help": "Minimum candle body vs total range"
                },
                {
                    "name": "min_candles",
                    "label": "Min Consecutive Candles",
                    "type": "number",
                    "default": 3,
                    "min": 2,
                    "max": 10,
                    "step": 1,
                    "help": "Required consecutive strong candles"
                },
                {
                    "name": "min_move_pct",
                    "label": "Min Price Move (%)",
                    "type": "number",
                    "default": 1.5,
                    "min": 0.5,
                    "max": 5.0,
                    "step": 0.5,
                    "help": "Minimum total price movement required"
                },
                {
                    "name": "validity_candles",
                    "label": "Signal Validity (candles)",
                    "type": "number",
                    "default": 10,
                    "min": 5,
                    "max": 30,
                    "step": 5,
                    "help": "How long displacement signal stays active"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Displacement events.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with displacement columns added
        """
        df = data.copy()
        
        # Reset index to integer for easier iteration
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        # Extract config
        min_body_pct = config.get('min_body_pct', 70) / 100.0
        min_candles = config.get('min_candles', 3)
        min_move_pct = config.get('min_move_pct', 1.5) / 100.0
        validity = config.get('validity_candles', 10)
        
        # Initialize columns
        df['candle_body_pct'] = 0.0
        df['is_strong_bull'] = False
        df['is_strong_bear'] = False
        df['bullish_displacement'] = False
        df['bearish_displacement'] = False
        df['displacement_active'] = False
        df['displacement_type'] = ''
        df['displacement_start'] = np.nan
        df['displacement_move_pct'] = 0.0
        
        # Calculate candle body percentage
        for i in range(len(df)):
            candle_range = df.loc[i, 'high'] - df.loc[i, 'low']
            if candle_range > 0:
                body_size = abs(df.loc[i, 'close'] - df.loc[i, 'open'])
                df.loc[i, 'candle_body_pct'] = body_size / candle_range
                
                # Strong bullish candle
                if df.loc[i, 'close'] > df.loc[i, 'open']:
                    if df.loc[i, 'candle_body_pct'] >= min_body_pct:
                        df.loc[i, 'is_strong_bull'] = True
                
                # Strong bearish candle
                elif df.loc[i, 'close'] < df.loc[i, 'open']:
                    if df.loc[i, 'candle_body_pct'] >= min_body_pct:
                        df.loc[i, 'is_strong_bear'] = True
        
        # Detect displacement sequences
        for i in range(min_candles, len(df)):
            
            # Check for bullish displacement
            lookback_range = range(i - min_candles + 1, i + 1)
            
            # All recent candles are strong bullish?
            if all(df.loc[j, 'is_strong_bull'] for j in lookback_range):
                # Calculate total move
                start_price = df.loc[i - min_candles + 1, 'open']
                end_price = df.loc[i, 'close']
                move_pct = (end_price - start_price) / start_price
                
                if move_pct >= min_move_pct:
                    df.loc[i, 'bullish_displacement'] = True
                    df.loc[i, 'displacement_start'] = start_price
                    df.loc[i, 'displacement_move_pct'] = move_pct * 100
            
            # Check for bearish displacement
            if all(df.loc[j, 'is_strong_bear'] for j in lookback_range):
                # Calculate total move
                start_price = df.loc[i - min_candles + 1, 'open']
                end_price = df.loc[i, 'close']
                move_pct = (start_price - end_price) / start_price
                
                if move_pct >= min_move_pct:
                    df.loc[i, 'bearish_displacement'] = True
                    df.loc[i, 'displacement_start'] = start_price
                    df.loc[i, 'displacement_move_pct'] = move_pct * 100
        
        # Propagate displacement signals for validity period
        active_displacement = None
        active_displacement_type = None
        candles_since_displacement = 0
        
        for i in range(len(df)):
            # New displacement detected
            if df.loc[i, 'bullish_displacement']:
                active_displacement = i
                active_displacement_type = 'BULLISH'
                candles_since_displacement = 0
            elif df.loc[i, 'bearish_displacement']:
                active_displacement = i
                active_displacement_type = 'BEARISH'
                candles_since_displacement = 0
            
            # Mark displacement as active
            if active_displacement is not None:
                if candles_since_displacement < validity:
                    df.loc[i, 'displacement_active'] = True
                    df.loc[i, 'displacement_type'] = active_displacement_type
                else:
                    # Validity expired
                    active_displacement = None
                    active_displacement_type = None
                
                candles_since_displacement += 1
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int, config: Dict, direction: str) -> bool:
        """
        Check if entry condition is met at given candle.
        
        Args:
            data: DataFrame with displacement columns
            index: Current candle index
            config: Configuration dictionary
            direction: 'LONG' or 'SHORT'
            
        Returns:
            True if entry condition met
        """
        row = data.iloc[index]
        
        if direction == 'LONG':
            # Enter LONG after bullish displacement
            return row['displacement_active'] and row['displacement_type'] == 'BULLISH'
        
        elif direction == 'SHORT':
            # Enter SHORT after bearish displacement
            return row['displacement_active'] and row['displacement_type'] == 'BEARISH'
        
        return False