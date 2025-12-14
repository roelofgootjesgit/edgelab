"""
kill_zones.py
=============

Kill Zones - ICT time-based institutional activity windows
Identifies optimal trading times based on institutional activity

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class KillZonesModule(BaseModule):
    """
    Kill Zones detection module.
    
    Concept:
    - Specific time windows when institutions are most active
    - Based on ICT methodology (Michael Huddleston)
    - Higher volatility and directional moves during kill zones
    - Best times to enter trades
    
    Time Windows (UTC):
    - London Kill Zone: 07:00-10:00 UTC (most active)
    - New York Kill Zone: 12:00-15:00 UTC (second most active)
    - Asian Kill Zone: 00:00-03:00 UTC (ranging behavior)
    
    Characteristics:
    - London: Strong directional moves, trend continuation
    - New York: High volume, reversals common
    - Asian: Range-bound, accumulation/distribution
    
    Trading Logic:
    - Enter trades during active kill zones
    - Combine with other ICT concepts (FVG, OB, etc.)
    - Avoid trading outside kill zones (lower probability)
    
    Parameters:
    - london_start: London kill zone start hour (default 7)
    - london_end: London kill zone end hour (default 10)
    - ny_start: New York kill zone start hour (default 12)
    - ny_end: New York kill zone end hour (default 15)
    - asian_start: Asian kill zone start hour (default 0)
    - asian_end: Asian kill zone end hour (default 3)
    - enabled_zones: Which zones to use (default all)
    """
    
    @property
    def name(self) -> str:
        return "Kill Zones"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT time windows - institutional activity periods"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "enabled_zones",
                    "label": "Enabled Kill Zones",
                    "type": "multiselect",
                    "options": [
                        {"value": "london", "label": "London (07:00-10:00 UTC)"},
                        {"value": "newyork", "label": "New York (12:00-15:00 UTC)"},
                        {"value": "asian", "label": "Asian (00:00-03:00 UTC)"}
                    ],
                    "default": ["london", "newyork"],
                    "help": "Select which kill zones to use"
                },
                {
                    "name": "london_start",
                    "label": "London Start Hour (UTC)",
                    "type": "number",
                    "default": 7,
                    "min": 0,
                    "max": 23,
                    "step": 1,
                    "help": "London kill zone start time"
                },
                {
                    "name": "london_end",
                    "label": "London End Hour (UTC)",
                    "type": "number",
                    "default": 10,
                    "min": 0,
                    "max": 23,
                    "step": 1,
                    "help": "London kill zone end time"
                },
                {
                    "name": "ny_start",
                    "label": "New York Start Hour (UTC)",
                    "type": "number",
                    "default": 12,
                    "min": 0,
                    "max": 23,
                    "step": 1,
                    "help": "New York kill zone start time"
                },
                {
                    "name": "ny_end",
                    "label": "New York End Hour (UTC)",
                    "type": "number",
                    "default": 15,
                    "min": 0,
                    "max": 23,
                    "step": 1,
                    "help": "New York kill zone end time"
                },
                {
                    "name": "asian_start",
                    "label": "Asian Start Hour (UTC)",
                    "type": "number",
                    "default": 0,
                    "min": 0,
                    "max": 23,
                    "step": 1,
                    "help": "Asian kill zone start time"
                },
                {
                    "name": "asian_end",
                    "label": "Asian End Hour (UTC)",
                    "type": "number",
                    "default": 3,
                    "min": 0,
                    "max": 23,
                    "step": 1,
                    "help": "Asian kill zone end time"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Kill Zone periods.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with kill zone columns added
        """
        df = data.copy()
        
        # Preserve timestamp index/column
        has_datetime_index = isinstance(df.index, pd.DatetimeIndex)
        if has_datetime_index:
            df['timestamp'] = df.index
        elif 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        elif 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        else:
            # Reset index to get timestamp
            df = df.reset_index(drop=False)
            if 'index' in df.columns:
                df = df.rename(columns={'index': 'timestamp'})
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract config
        enabled_zones = config.get('enabled_zones', ['london', 'newyork'])
        if isinstance(enabled_zones, str):
            enabled_zones = [enabled_zones]
        
        london_start = config.get('london_start', 7)
        london_end = config.get('london_end', 10)
        ny_start = config.get('ny_start', 12)
        ny_end = config.get('ny_end', 15)
        asian_start = config.get('asian_start', 0)
        asian_end = config.get('asian_end', 3)
        
        # Initialize columns
        df['in_kill_zone'] = False
        df['kill_zone'] = ''
        df['in_london_kz'] = False
        df['in_newyork_kz'] = False
        df['in_asian_kz'] = False
        
        # Reset index to integer for reliable iteration
        df = df.reset_index(drop=True)
        
        # Identify kill zones based on hour
        for i in range(len(df)):
            hour = df.iloc[i]['timestamp'].hour
            
            # London Kill Zone
            if 'london' in enabled_zones:
                if london_start <= hour < london_end:
                    df.loc[i, 'in_london_kz'] = True
                    df.loc[i, 'in_kill_zone'] = True
                    df.loc[i, 'kill_zone'] = 'LONDON'
            
            # New York Kill Zone
            if 'newyork' in enabled_zones:
                if ny_start <= hour < ny_end:
                    df.loc[i, 'in_newyork_kz'] = True
                    df.loc[i, 'in_kill_zone'] = True
                    # Overlap priority: NY > London
                    df.loc[i, 'kill_zone'] = 'NEW_YORK'
            
            # Asian Kill Zone
            if 'asian' in enabled_zones:
                if asian_start <= hour < asian_end:
                    df.loc[i, 'in_asian_kz'] = True
                    df.loc[i, 'in_kill_zone'] = True
                    # Only set if no other zone active
                    if df.loc[i, 'kill_zone'] == '':
                        df.loc[i, 'kill_zone'] = 'ASIAN'
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int, config: Dict, direction: str) -> bool:
        """
        Check if entry condition is met at given candle.
        
        Args:
            data: DataFrame with kill zone columns
            index: Current candle index
            config: Configuration dictionary
            direction: 'LONG' or 'SHORT'
            
        Returns:
            True if entry condition met (in active kill zone)
        """
        row = data.iloc[index]
        
        # Enter trades during kill zones (regardless of direction)
        # This module acts as a TIME FILTER, not a directional signal
        return row['in_kill_zone'] == True