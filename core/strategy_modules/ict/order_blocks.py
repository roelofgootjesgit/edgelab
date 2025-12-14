# core/strategy_modules/ict/order_blocks.py
"""
Order Blocks Module - ICT Concept

Institutional order blocks: Last bullish/bearish candle before significant reversal.
These zones often act as strong support/resistance where institutions placed large orders.

Author: QuantMetrics Development Team
Version: 1.0
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class OrderBlockModule(BaseModule):
    """
    Order Block Detection - Core ICT Concept.
    
    Identifies:
    - Bullish OB: Last green candle before strong drop (becomes support)
    - Bearish OB: Last red candle before strong rally (becomes resistance)
    
    Entry signals:
    - LONG: Price returns to bullish OB zone
    - SHORT: Price returns to bearish OB zone
    """
    
    @property
    def name(self) -> str:
        return "Order Blocks (OB)"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT institutional order zones - last candle before reversal"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "fields": [
                {
                    "name": "min_candles",
                    "label": "Minimum Reversal Candles",
                    "type": "number",
                    "default": 3,
                    "min": 2,
                    "max": 10,
                    "help": "How many consecutive candles define a 'strong move'"
                },
                {
                    "name": "min_move_pct",
                    "label": "Minimum Move %",
                    "type": "number",
                    "default": 3.0,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.5,
                    "help": "Minimum price move % to qualify as reversal"
                },
                {
                    "name": "validity_candles",
                    "label": "OB Validity Period",
                    "type": "number",
                    "default": 20,
                    "min": 10,
                    "max": 100,
                    "help": "How many candles an OB remains valid"
                },
                {
                    "name": "zone_type",
                    "label": "OB Zone Type",
                    "type": "select",
                    "options": ["full_candle", "body_only", "wick_only"],
                    "default": "full_candle",
                    "help": "Which part of candle defines the zone"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Detect order blocks and add indicators to dataframe.
        
        Adds columns:
        - bullish_ob: Boolean, True if bullish OB detected at this candle
        - bearish_ob: Boolean, True if bearish OB detected at this candle
        - ob_high: OB zone upper boundary (propagated for validity period)
        - ob_low: OB zone lower boundary (propagated for validity period)
        - in_bullish_ob: Boolean, True if price currently in bullish OB zone
        - in_bearish_ob: Boolean, True if price currently in bearish OB zone
        """
        # Extract config
        min_candles = config.get('min_candles', 3)
        min_move_pct = config.get('min_move_pct', 3.0)
        validity = config.get('validity_candles', 20)
        zone_type = config.get('zone_type', 'full_candle')
        
        # Initialize columns
        data['bullish_ob'] = False
        data['bearish_ob'] = False
        data['ob_high'] = np.nan
        data['ob_low'] = np.nan
        data['in_bullish_ob'] = False
        data['in_bearish_ob'] = False
        
        # Reset index to ensure integer-based indexing
        data = data.reset_index(drop=True)
        
        # Detect bullish order blocks
        data = self._find_bullish_obs(data, min_candles, min_move_pct, validity, zone_type)
        
        # Detect bearish order blocks
        data = self._find_bearish_obs(data, min_candles, min_move_pct, validity, zone_type)
        
        return data
    
    def _find_bullish_obs(
        self, 
        data: pd.DataFrame, 
        min_candles: int,
        min_move_pct: float,
        validity: int,
        zone_type: str
    ) -> pd.DataFrame:
        """Find bullish order blocks (last green candle before drop)."""
        
        for i in range(min_candles, len(data)):
            # Check if this is a green candle (bullish)
            if data.iloc[i]['close'] <= data.iloc[i]['open']:
                continue
            
            # Check if followed by strong down move
            future_lows = []
            consecutive_red = 0
            
            for j in range(i + 1, min(i + min_candles + 1, len(data))):
                future_lows.append(data.iloc[j]['low'])
                # Count consecutive red candles
                if data.iloc[j]['close'] < data.iloc[j]['open']:
                    consecutive_red += 1
            
            if not future_lows:
                continue
            
            # Get lowest point after this candle
            lowest_future = min(future_lows)
            current_high = data.iloc[i]['high']
            
            # Calculate move percentage
            move_pct = ((current_high - lowest_future) / current_high) * 100
            
            # Check if move is significant enough
            if move_pct >= min_move_pct and consecutive_red >= min_candles - 1:
                # This is a bullish OB! Define zone based on zone_type
                if zone_type == 'full_candle':
                    ob_low = data.iloc[i]['low']
                    ob_high = data.iloc[i]['high']
                elif zone_type == 'body_only':
                    ob_low = data.iloc[i]['open']
                    ob_high = data.iloc[i]['close']
                else:  # wick_only
                    ob_low = data.iloc[i]['low']
                    ob_high = data.iloc[i]['open']
                
                # Mark this candle as OB origin
                data.loc[i, 'bullish_ob'] = True
                
                # Propagate OB zone for validity period
                for k in range(i, min(i + validity + 1, len(data))):
                    # Don't overwrite existing zones
                    if pd.isna(data.loc[k, 'ob_low']):
                        data.loc[k, 'ob_low'] = ob_low
                        data.loc[k, 'ob_high'] = ob_high
        
        # Check if price is in bullish OB zone
        for i in range(len(data)):
            if not pd.isna(data.loc[i, 'ob_low']) and not pd.isna(data.loc[i, 'ob_high']):
                price = data.loc[i, 'close']
                in_zone = data.loc[i, 'ob_low'] <= price <= data.loc[i, 'ob_high']
                
                # Check if this is a bullish OB zone
                # Find the origin candle
                for j in range(max(0, i - validity), i + 1):
                    if data.loc[j, 'bullish_ob']:
                        data.loc[i, 'in_bullish_ob'] = in_zone
                        break
        
        return data
    
    def _find_bearish_obs(
        self,
        data: pd.DataFrame,
        min_candles: int,
        min_move_pct: float,
        validity: int,
        zone_type: str
    ) -> pd.DataFrame:
        """Find bearish order blocks (last red candle before rally)."""
        
        for i in range(min_candles, len(data)):
            # Check if this is a red candle (bearish)
            if data.iloc[i]['close'] >= data.iloc[i]['open']:
                continue
            
            # Check if followed by strong up move
            future_highs = []
            consecutive_green = 0
            
            for j in range(i + 1, min(i + min_candles + 1, len(data))):
                future_highs.append(data.iloc[j]['high'])
                # Count consecutive green candles
                if data.iloc[j]['close'] > data.iloc[j]['open']:
                    consecutive_green += 1
            
            if not future_highs:
                continue
            
            # Get highest point after this candle
            highest_future = max(future_highs)
            current_low = data.iloc[i]['low']
            
            # Calculate move percentage
            move_pct = ((highest_future - current_low) / current_low) * 100
            
            # Check if move is significant
            if move_pct >= min_move_pct and consecutive_green >= min_candles - 1:
                # This is a bearish OB!
                if zone_type == 'full_candle':
                    ob_low = data.iloc[i]['low']
                    ob_high = data.iloc[i]['high']
                elif zone_type == 'body_only':
                    ob_low = data.iloc[i]['close']
                    ob_high = data.iloc[i]['open']
                else:  # wick_only
                    ob_low = data.iloc[i]['close']
                    ob_high = data.iloc[i]['high']
                
                # Mark this candle as OB origin
                data.loc[i, 'bearish_ob'] = True
                
                # Propagate for validity period
                for k in range(i, min(i + validity + 1, len(data))):
                    # Don't overwrite bullish OB zones
                    if pd.isna(data.loc[k, 'ob_low']):
                        data.loc[k, 'ob_low'] = ob_low
                        data.loc[k, 'ob_high'] = ob_high
        
        # Check if price is in bearish OB zone
        for i in range(len(data)):
            if not pd.isna(data.loc[i, 'ob_low']) and not pd.isna(data.loc[i, 'ob_high']):
                price = data.loc[i, 'close']
                in_zone = data.loc[i, 'ob_low'] <= price <= data.loc[i, 'ob_high']
                
                # Check if this is a bearish OB zone
                for j in range(max(0, i - validity), i + 1):
                    if data.loc[j, 'bearish_ob']:
                        data.loc[i, 'in_bearish_ob'] = in_zone
                        break
        
        return data
    
    def check_entry_condition(
        self,
        data: pd.DataFrame,
        index: int,
        config: Dict[str, Any],
        strategy_direction: str
    ) -> bool:
        """
        Check if order block entry condition is met.
        
        LONG strategy: Price returns to bullish OB zone (support)
        SHORT strategy: Price returns to bearish OB zone (resistance)
        
        Args:
            data: DataFrame with OB indicators calculated
            index: Current candle index
            config: Module configuration
            strategy_direction: 'LONG' or 'SHORT'
        
        Returns:
            True if entry signal detected
        """
        if index < 1:
            return False
        
        current = data.iloc[index]
        
        if strategy_direction == 'LONG':
            # Entry on bullish OB touch
            return current.get('in_bullish_ob', False)
        
        elif strategy_direction == 'SHORT':
            # Entry on bearish OB touch
            return current.get('in_bearish_ob', False)
        
        return False