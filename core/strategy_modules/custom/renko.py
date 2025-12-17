"""
Renko Bricks
============

Renko chart indicator - time-independent brick formation.

Formula:
Bricks form when price moves by brick_size amount:
- Up brick: Close >= Previous Brick High + brick_size
- Down brick: Close <= Previous Brick Low - brick_size

Features:
- Filters noise (ignores time and volume)
- Clear trend visualization
- Consecutive bricks = strong trend
- Brick reversal = potential trend change
- Works best in trending markets
- ATR-based brick size recommended

Entry Logic:
- LONG: 2+ consecutive up bricks
- SHORT: 2+ consecutive down bricks

Note: This is a simplified indicator version. True Renko requires 
special chart rendering. This tracks brick formations in OHLC data.

Author: QuantMetrics Development Team
Version: 2.0 - Complete Implementation
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class RenkoModule(BaseModule):
    """Renko Bricks indicator module"""
    
    @property
    def name(self) -> str:
        return "Renko Bricks"
    
    @property
    def category(self) -> str:
        return "custom"
    
    @property
    def description(self) -> str:
        return "Renko Bricks - time-independent trend indicator"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "brick_size": {
                    "type": "number",
                    "minimum": 0.0001,
                    "maximum": 1000,
                    "default": 0,
                    "description": "Fixed brick size (0 = auto ATR-based)"
                },
                "atr_period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 200,
                    "default": 14,
                    "description": "ATR period for auto brick size"
                },
                "atr_multiplier": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 10,
                    "default": 1.0,
                    "description": "ATR multiplier for brick size"
                },
                "consecutive_bricks": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 2,
                    "description": "Consecutive bricks for entry"
                }
            },
            "required": []
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Renko brick formations"""
        brick_size = config.get('brick_size', 0)
        atr_period = config.get('atr_period', 14)
        atr_mult = config.get('atr_multiplier', 1.0)
        
        # Calculate ATR if using auto brick size
        if brick_size == 0:
            high_low = data['high'] - data['low']
            high_close = np.abs(data['high'] - data['close'].shift(1))
            low_close = np.abs(data['low'] - data['close'].shift(1))
            
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(window=atr_period).mean()
            
            # Use ATR as brick size (dynamic)
            brick_sizes = atr * atr_mult
        else:
            # Fixed brick size
            brick_sizes = pd.Series([brick_size] * len(data), index=data.index)
        
        # Initialize Renko tracking
        data['renko_brick_size'] = brick_sizes
        data['renko_direction'] = 0  # 1=up, -1=down, 0=none
        data['renko_bricks_formed'] = 0
        data['renko_up_count'] = 0
        data['renko_down_count'] = 0
        
        # Track brick formation
        current_brick_high = data['close'].iloc[0]
        current_brick_low = data['close'].iloc[0]
        up_count = 0
        down_count = 0
        
        for i in range(1, len(data)):
            close = data['close'].iloc[i]
            brick_sz = brick_sizes.iloc[i]
            
            if pd.isna(brick_sz):
                continue
            
            bricks_formed = 0
            direction = 0
            
            # Check for up bricks
            while close >= current_brick_high + brick_sz:
                current_brick_high += brick_sz
                current_brick_low = current_brick_high - brick_sz
                bricks_formed += 1
                direction = 1
                up_count += 1
                down_count = 0
            
            # Check for down bricks
            while close <= current_brick_low - brick_sz:
                current_brick_low -= brick_sz
                current_brick_high = current_brick_low + brick_sz
                bricks_formed += 1
                direction = -1
                down_count += 1
                up_count = 0
            
            data.loc[data.index[i], 'renko_direction'] = direction
            data.loc[data.index[i], 'renko_bricks_formed'] = bricks_formed
            data.loc[data.index[i], 'renko_up_count'] = up_count
            data.loc[data.index[i], 'renko_down_count'] = down_count
        
        # Trend state
        data['renko_uptrend'] = data['renko_up_count'] >= 2
        data['renko_downtrend'] = data['renko_down_count'] >= 2
        
        # Reversal signals
        data['renko_reversal_up'] = (data['renko_direction'] == 1) & (data['renko_direction'].shift(1) == -1)
        data['renko_reversal_down'] = (data['renko_direction'] == -1) & (data['renko_direction'].shift(1) == 1)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if Renko entry condition is met"""
        if 'renko_direction' not in data.columns:
            return False
        
        if index < 1:
            return False
        
        consecutive = config.get('consecutive_bricks', 2)
        
        current = data.iloc[index]
        
        up_count = current['renko_up_count']
        down_count = current['renko_down_count']
        
        if direction == 'LONG':
            # Consecutive up bricks
            return up_count >= consecutive
        else:  # SHORT
            # Consecutive down bricks
            return down_count >= consecutive