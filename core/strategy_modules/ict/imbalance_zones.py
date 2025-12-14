"""
imbalance_zones.py
==================

Imbalance Zones - ICT wick-based gap detection
Identifies price imbalances that tend to get filled

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class ImbalanceZonesModule(BaseModule):
    """
    Imbalance Zones detection module.
    
    Concept:
    - Similar to Fair Value Gaps but focuses on wick imbalances
    - Occurs when entire candle range doesn't overlap with previous
    - Price tends to return to fill these gaps
    - Often smaller than FVG but still significant
    
    Bullish Imbalance:
    - Candle i+1's low > Candle i-1's high
    - Creates gap in price action
    - Buyers dominated, leaving unfilled area below
    
    Bearish Imbalance:
    - Candle i+1's high < Candle i-1's low
    - Creates gap in price action
    - Sellers dominated, leaving unfilled area above
    
    Trading Logic:
    - LONG when price returns to bullish imbalance
    - SHORT when price returns to bearish imbalance
    
    Parameters:
    - min_gap_size: Minimum gap size in price units (default 0.5)
    - validity_candles: How long to track imbalance (default 50)
    - fill_threshold: What % of gap must fill (default 50%)
    """
    
    @property
    def name(self) -> str:
        return "Imbalance Zones"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT wick-based gaps - price imbalances to fill"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "min_gap_size",
                    "label": "Min Gap Size (price units)",
                    "type": "number",
                    "default": 0.5,
                    "min": 0.1,
                    "max": 10.0,
                    "step": 0.1,
                    "help": "Minimum gap size to consider"
                },
                {
                    "name": "validity_candles",
                    "label": "Validity Period (candles)",
                    "type": "number",
                    "default": 50,
                    "min": 20,
                    "max": 200,
                    "step": 10,
                    "help": "How long to track imbalance"
                },
                {
                    "name": "fill_threshold",
                    "label": "Fill Threshold (%)",
                    "type": "number",
                    "default": 50,
                    "min": 25,
                    "max": 100,
                    "step": 25,
                    "help": "What % of gap must fill to consider filled"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Imbalance Zones.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with imbalance zone columns added
        """
        df = data.copy()
        
        # Reset index to integer for easier iteration
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        # Extract config
        min_gap_size = config.get('min_gap_size', 0.5)
        validity = config.get('validity_candles', 50)
        fill_threshold = config.get('fill_threshold', 50) / 100.0
        
        # Initialize columns
        df['bullish_imbalance'] = False
        df['bearish_imbalance'] = False
        df['imbalance_high'] = np.nan
        df['imbalance_low'] = np.nan
        df['in_bullish_imbalance'] = False
        df['in_bearish_imbalance'] = False
        df['imbalance_filled'] = False
        
        # Track active imbalances
        active_bullish_imbalances = []  # List of (index, high, low, candles_old)
        active_bearish_imbalances = []  # List of (index, high, low, candles_old)
        
        # Detect imbalances (need 3 candles: i-1, i, i+1)
        for i in range(1, len(df) - 1):
            prev_candle = df.iloc[i - 1]
            curr_candle = df.iloc[i]
            next_candle = df.iloc[i + 1]
            
            # Bullish Imbalance: next candle's low > prev candle's high
            if next_candle['low'] > prev_candle['high']:
                gap_size = next_candle['low'] - prev_candle['high']
                
                if gap_size >= min_gap_size:
                    df.loc[i + 1, 'bullish_imbalance'] = True
                    df.loc[i + 1, 'imbalance_low'] = prev_candle['high']
                    df.loc[i + 1, 'imbalance_high'] = next_candle['low']
                    
                    # Add to active tracking
                    active_bullish_imbalances.append({
                        'index': i + 1,
                        'high': next_candle['low'],
                        'low': prev_candle['high'],
                        'age': 0
                    })
            
            # Bearish Imbalance: next candle's high < prev candle's low
            if next_candle['high'] < prev_candle['low']:
                gap_size = prev_candle['low'] - next_candle['high']
                
                if gap_size >= min_gap_size:
                    df.loc[i + 1, 'bearish_imbalance'] = True
                    df.loc[i + 1, 'imbalance_low'] = next_candle['high']
                    df.loc[i + 1, 'imbalance_high'] = prev_candle['low']
                    
                    # Add to active tracking
                    active_bearish_imbalances.append({
                        'index': i + 1,
                        'high': prev_candle['low'],
                        'low': next_candle['high'],
                        'age': 0
                    })
        
        # Propagate imbalance zones and check for fills
        for i in range(len(df)):
            current_price = df.loc[i, 'close']
            current_high = df.loc[i, 'high']
            current_low = df.loc[i, 'low']
            
            # Check bullish imbalances
            remaining_bullish = []
            for imb in active_bullish_imbalances:
                imb['age'] += 1
                
                # Check if filled
                gap_size = imb['high'] - imb['low']
                penetration = min(current_low, imb['high']) - imb['low']
                fill_pct = penetration / gap_size if gap_size > 0 else 0
                
                if fill_pct >= fill_threshold:
                    # Imbalance filled
                    df.loc[i, 'imbalance_filled'] = True
                elif imb['age'] < validity:
                    # Still active, check if price in zone
                    if current_low <= imb['high'] and current_high >= imb['low']:
                        df.loc[i, 'in_bullish_imbalance'] = True
                        df.loc[i, 'imbalance_low'] = imb['low']
                        df.loc[i, 'imbalance_high'] = imb['high']
                    
                    remaining_bullish.append(imb)
            
            active_bullish_imbalances = remaining_bullish
            
            # Check bearish imbalances
            remaining_bearish = []
            for imb in active_bearish_imbalances:
                imb['age'] += 1
                
                # Check if filled
                gap_size = imb['high'] - imb['low']
                penetration = imb['high'] - max(current_high, imb['low'])
                fill_pct = penetration / gap_size if gap_size > 0 else 0
                
                if fill_pct >= fill_threshold:
                    # Imbalance filled
                    df.loc[i, 'imbalance_filled'] = True
                elif imb['age'] < validity:
                    # Still active, check if price in zone
                    if current_high >= imb['low'] and current_low <= imb['high']:
                        df.loc[i, 'in_bearish_imbalance'] = True
                        df.loc[i, 'imbalance_low'] = imb['low']
                        df.loc[i, 'imbalance_high'] = imb['high']
                    
                    remaining_bearish.append(imb)
            
            active_bearish_imbalances = remaining_bearish
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int, config: Dict, direction: str) -> bool:
        """
        Check if entry condition is met at given candle.
        
        Args:
            data: DataFrame with imbalance zone columns
            index: Current candle index
            config: Configuration dictionary
            direction: 'LONG' or 'SHORT'
            
        Returns:
            True if entry condition met
        """
        row = data.iloc[index]
        
        if direction == 'LONG':
            # Enter LONG when price is in bullish imbalance zone
            return row['in_bullish_imbalance'] == True
        
        elif direction == 'SHORT':
            # Enter SHORT when price is in bearish imbalance zone
            return row['in_bearish_imbalance'] == True
        
        return False