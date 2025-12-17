"""
Donchian Channels
=================

Richard Donchian's price channel breakout indicator.

Formula:
Upper Band = Highest High over N periods
Lower Band = Lowest Low over N periods
Middle Band = (Upper + Lower) / 2

Features:
- Identifies breakouts (new highs/lows)
- Channel width shows volatility
- Narrow channels = consolidation (breakout coming)
- Wide channels = trending (ride the trend)
- Turtle Trading system uses this
- Original: 20-period

Entry Logic:
- LONG: Price breaks above upper band (new high)
- SHORT: Price breaks below lower band (new low)

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class DonchianChannelsModule(BaseModule):
    """Donchian Channels indicator module"""
    
    @property
    def name(self) -> str:
        return "Donchian Channels"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Donchian Channels - price breakout system"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 200,
                    "default": 20,
                    "description": "Lookback period (typical: 20)"
                },
                "use_close": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use close instead of high/low"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Donchian Channels"""
        period = config.get('period', 20)
        use_close = config.get('use_close', False)
        
        if use_close:
            # Use close price for both bands
            upper = data['close'].rolling(window=period).max()
            lower = data['close'].rolling(window=period).min()
        else:
            # Use high/low (traditional)
            upper = data['high'].rolling(window=period).max()
            lower = data['low'].rolling(window=period).min()
        
        # Middle band
        middle = (upper + lower) / 2
        
        # Add to dataframe
        data[f'donchian_upper_{period}'] = upper
        data[f'donchian_lower_{period}'] = lower
        data[f'donchian_middle_{period}'] = middle
        
        # Channel width (volatility)
        width = upper - lower
        data[f'donchian_width_{period}'] = width
        
        # Normalized width (% of middle)
        data[f'donchian_width_pct_{period}'] = (width / middle.replace(0, np.nan)) * 100
        
        # Price position in channel
        price_pos = (data['close'] - lower) / width.replace(0, np.nan)
        data[f'donchian_position_{period}'] = price_pos
        
        # Breakouts
        data[f'donchian_breakout_up_{period}'] = data['close'] > upper.shift(1)
        data[f'donchian_breakout_down_{period}'] = data['close'] < lower.shift(1)
        
        # Near bands
        tolerance = width * 0.02  # 2% of channel width
        data[f'donchian_near_upper_{period}'] = (upper - data['close']) < tolerance
        data[f'donchian_near_lower_{period}'] = (data['close'] - lower) < tolerance
        
        # Channel squeeze (narrow width = potential breakout)
        avg_width = width.rolling(window=period).mean()
        data[f'donchian_squeeze_{period}'] = width < (avg_width * 0.7)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Donchian breakout condition is met"""
        period = config.get('period', 20)
        
        breakout_up_col = f'donchian_breakout_up_{period}'
        breakout_down_col = f'donchian_breakout_down_{period}'
        
        if breakout_up_col not in data.columns:
            return False
        
        if index < 1:
            return False
        
        current = data.iloc[index]
        
        if direction == 'LONG':
            # Price breaks above upper band (new high)
            return current[breakout_up_col]
        else:  # SHORT
            # Price breaks below lower band (new low)
            return current[breakout_down_col]