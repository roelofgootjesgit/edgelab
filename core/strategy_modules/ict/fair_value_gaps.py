"""
fair_value_gaps.py
==================

Fair Value Gaps (FVG) - ICT price imbalance detection
Identifies gaps where price moved too fast, creating zones that tend to fill

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class FairValueGapModule(BaseModule):
    """
    Fair Value Gaps (FVG) detection module.
    
    Concept:
    - Bullish FVG: Low of candle (i+1) > High of candle (i-1)
      Creates gap between high[i-1] and low[i+1]
    
    - Bearish FVG: High of candle (i+1) < Low of candle (i-1)
      Creates gap between low[i-1] and high[i+1]
    
    Trading Logic:
    - LONG when price returns to bullish FVG zone
    - SHORT when price returns to bearish FVG zone
    
    Parameters:
    - min_gap_pct: Minimum gap size (default 0.5%)
    - validity_candles: How long FVG stays active (default 50)
    - fill_threshold: % of gap that must fill to invalidate (default 0.5 = 50%)
    """
    
    @property
    def name(self) -> str:
        return "Fair Value Gaps (FVG)"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT price imbalances - gaps that tend to fill"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "min_gap_pct",
                    "label": "Minimum Gap Size (%)",
                    "type": "number",
                    "default": 0.5,
                    "min": 0.1,
                    "max": 2.0,
                    "step": 0.1,
                    "help": "Minimum gap size to qualify as FVG"
                },
                {
                    "name": "validity_candles",
                    "label": "Validity Period (candles)",
                    "type": "number",
                    "default": 50,
                    "min": 10,
                    "max": 100,
                    "step": 5,
                    "help": "How many candles FVG remains valid"
                },
                {
                    "name": "fill_threshold",
                    "label": "Fill Threshold",
                    "type": "number",
                    "default": 0.5,
                    "min": 0.25,
                    "max": 1.0,
                    "step": 0.05,
                    "help": "Fraction of gap that must fill (0.5 = 50%)"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Fair Value Gaps.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with FVG columns added
        """
        df = data.copy()
        
        # Extract config
        min_gap_pct = config.get('min_gap_pct', 0.5) / 100.0
        validity_candles = config.get('validity_candles', 50)
        fill_threshold = config.get('fill_threshold', 0.5)
        
        # Initialize columns
        df['bullish_fvg'] = False
        df['bearish_fvg'] = False
        df['fvg_high'] = np.nan
        df['fvg_low'] = np.nan
        df['in_bullish_fvg'] = False
        df['in_bearish_fvg'] = False
        df['fvg_filled'] = False
        
        # Store active FVGs
        active_bullish_fvgs = []
        active_bearish_fvgs = []
        
        for i in range(2, len(df)):
            current_price = df.iloc[i]['close']
            
            # Detect Bullish FVG at candle (i-1)
            # Requires: low[i] > high[i-2]
            if i >= 2:
                prev_prev_high = df.iloc[i-2]['high']
                current_low = df.iloc[i]['low']
                
                if current_low > prev_prev_high:
                    gap_size = current_low - prev_prev_high
                    gap_pct = gap_size / prev_prev_high
                    
                    if gap_pct >= min_gap_pct:
                        df.at[i-1, 'bullish_fvg'] = True
                        df.at[i-1, 'fvg_low'] = prev_prev_high
                        df.at[i-1, 'fvg_high'] = current_low
                        
                        # Add to active FVGs
                        active_bullish_fvgs.append({
                            'origin': i-1,
                            'low': prev_prev_high,
                            'high': current_low,
                            'filled': False
                        })
            
            # Detect Bearish FVG at candle (i-1)
            # Requires: high[i] < low[i-2]
            if i >= 2:
                prev_prev_low = df.iloc[i-2]['low']
                current_high = df.iloc[i]['high']
                
                if current_high < prev_prev_low:
                    gap_size = prev_prev_low - current_high
                    gap_pct = gap_size / prev_prev_low
                    
                    if gap_pct >= min_gap_pct:
                        df.at[i-1, 'bearish_fvg'] = True
                        df.at[i-1, 'fvg_low'] = current_high
                        df.at[i-1, 'fvg_high'] = prev_prev_low
                        
                        # Add to active FVGs
                        active_bearish_fvgs.append({
                            'origin': i-1,
                            'low': current_high,
                            'high': prev_prev_low,
                            'filled': False
                        })
            
            # Check if current price is in any active bullish FVG
            for fvg in active_bullish_fvgs:
                if fvg['filled']:
                    continue
                
                # Check validity period
                if i - fvg['origin'] > validity_candles:
                    fvg['filled'] = True
                    continue
                
                # Check if price is in FVG zone
                if fvg['low'] <= current_price <= fvg['high']:
                    df.at[i, 'in_bullish_fvg'] = True
                    df.at[i, 'fvg_low'] = fvg['low']
                    df.at[i, 'fvg_high'] = fvg['high']
                
                # Check if FVG is filled
                fill_level = fvg['low'] + (fvg['high'] - fvg['low']) * fill_threshold
                if current_price <= fill_level:
                    fvg['filled'] = True
                    df.at[i, 'fvg_filled'] = True
            
            # Check if current price is in any active bearish FVG
            for fvg in active_bearish_fvgs:
                if fvg['filled']:
                    continue
                
                # Check validity period
                if i - fvg['origin'] > validity_candles:
                    fvg['filled'] = True
                    continue
                
                # Check if price is in FVG zone
                if fvg['low'] <= current_price <= fvg['high']:
                    df.at[i, 'in_bearish_fvg'] = True
                    df.at[i, 'fvg_low'] = fvg['low']
                    df.at[i, 'fvg_high'] = fvg['high']
                
                # Check if FVG is filled
                fill_level = fvg['high'] - (fvg['high'] - fvg['low']) * fill_threshold
                if current_price >= fill_level:
                    fvg['filled'] = True
                    df.at[i, 'fvg_filled'] = True
        
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
            data: DataFrame with FVG calculations
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
            # Enter LONG when price is in bullish FVG zone
            return candle['in_bullish_fvg'] == True
        
        elif direction == 'SHORT':
            # Enter SHORT when price is in bearish FVG zone
            return candle['in_bearish_fvg'] == True
        
        return False