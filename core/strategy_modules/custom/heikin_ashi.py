"""
Heikin Ashi
===========

Heikin Ashi candlesticks - smoothed price action.

Formula:
HA Close = (Open + High + Low + Close) / 4
HA Open = (HA Open[1] + HA Close[1]) / 2
HA High = MAX(High, HA Open, HA Close)
HA Low = MIN(Low, HA Open, HA Close)

Features:
- Filters market noise
- Smoother trend identification
- No wicks = strong trend
- Small bodies = consolidation
- Color change = potential reversal
- Better for trend following

Entry Logic:
- LONG: Green HA candle with no lower wick (strong uptrend)
- SHORT: Red HA candle with no upper wick (strong downtrend)

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class HeikinAshiModule(BaseModule):
    """Heikin Ashi candlestick module"""
    
    @property
    def name(self) -> str:
        return "Heikin Ashi"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Heikin Ashi - smoothed candlestick technique"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "consecutive_candles": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 2,
                    "description": "Consecutive candles required for entry"
                },
                "require_no_wick": {
                    "type": "boolean",
                    "default": True,
                    "description": "Require no opposing wick for entry"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Heikin Ashi candles"""
        df = data.copy()
        
        # Initialize HA values
        ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        ha_open = pd.Series(index=df.index, dtype=float)
        
        # First HA open is average of first regular open and close
        ha_open.iloc[0] = (df['open'].iloc[0] + df['close'].iloc[0]) / 2
        
        # Calculate HA open for each bar
        for i in range(1, len(df)):
            ha_open.iloc[i] = (ha_open.iloc[i-1] + ha_close.iloc[i-1]) / 2
        
        # Calculate HA high and low
        ha_high = pd.concat([df['high'], ha_open, ha_close], axis=1).max(axis=1)
        ha_low = pd.concat([df['low'], ha_open, ha_close], axis=1).min(axis=1)
        
        # Add to dataframe
        data['ha_open'] = ha_open
        data['ha_high'] = ha_high
        data['ha_low'] = ha_low
        data['ha_close'] = ha_close
        
        # HA candle properties
        data['ha_green'] = ha_close > ha_open
        data['ha_red'] = ha_close < ha_open
        
        # Body size
        data['ha_body'] = np.abs(ha_close - ha_open)
        
        # Wick analysis
        data['ha_upper_wick'] = ha_high - pd.concat([ha_open, ha_close], axis=1).max(axis=1)
        data['ha_lower_wick'] = pd.concat([ha_open, ha_close], axis=1).min(axis=1) - ha_low
        
        # No wick conditions (strong trend)
        wick_threshold = data['ha_body'] * 0.1  # 10% of body
        data['ha_no_upper_wick'] = data['ha_upper_wick'] < wick_threshold
        data['ha_no_lower_wick'] = data['ha_lower_wick'] < wick_threshold
        
        # Consecutive candle counting
        data['ha_green_count'] = 0
        data['ha_red_count'] = 0
        
        green_count = 0
        red_count = 0
        
        for i in range(len(data)):
            if data['ha_green'].iloc[i]:
                green_count += 1
                red_count = 0
            elif data['ha_red'].iloc[i]:
                red_count += 1
                green_count = 0
            
            data.loc[data.index[i], 'ha_green_count'] = green_count
            data.loc[data.index[i], 'ha_red_count'] = red_count
        
        # Trend strength
        data['ha_strong_uptrend'] = data['ha_green'] & data['ha_no_lower_wick']
        data['ha_strong_downtrend'] = data['ha_red'] & data['ha_no_upper_wick']
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Heikin Ashi entry condition is met"""
        if 'ha_close' not in data.columns:
            return False
        
        if index < 1:
            return False
        
        consecutive = config.get('consecutive_candles', 2)
        require_no_wick = config.get('require_no_wick', True)
        
        current = data.iloc[index]
        
        green_count = current['ha_green_count']
        red_count = current['ha_red_count']
        
        if direction == 'LONG':
            # Green HA candles
            if green_count < consecutive:
                return False
            
            # Optionally require no lower wick (strong uptrend)
            if require_no_wick:
                return current['ha_no_lower_wick']
            
            return True
            
        else:  # SHORT
            # Red HA candles
            if red_count < consecutive:
                return False
            
            # Optionally require no upper wick (strong downtrend)
            if require_no_wick:
                return current['ha_no_upper_wick']
            
            return True