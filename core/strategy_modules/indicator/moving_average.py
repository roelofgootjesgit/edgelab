# core/strategy_modules/indicators/moving_average.py
"""
Moving Average Module - SMA and EMA support

Supports both:
- Trend following (price crosses MA)
- Crossover strategies (fast MA crosses slow MA)
"""

from typing import Dict, Any
import pandas as pd
from core.strategy_modules.base import BaseModule


class MovingAverageModule(BaseModule):
    """
    Moving Average - Trend identification and crossover signals.
    
    Supports:
    - SMA (Simple Moving Average)
    - EMA (Exponential Moving Average)
    - Price crosses MA
    - MA crosses MA (fast/slow crossover)
    """
    
    @property
    def name(self) -> str:
        return "Moving Average"
    
    @property
    def category(self) -> str:
        return "indicator"
    
    @property
    def description(self) -> str:
        return "Trend indicator - SMA/EMA with crossover detection"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "fields": [
                {
                    "name": "ma_type",
                    "label": "MA Type",
                    "type": "select",
                    "options": ["SMA", "EMA"],
                    "default": "EMA",
                    "help": "Simple or Exponential Moving Average"
                },
                {
                    "name": "period",
                    "label": "Period",
                    "type": "number",
                    "default": 50,
                    "min": 1,
                    "max": 500,
                    "help": "Number of periods for MA calculation"
                },
                {
                    "name": "signal_type",
                    "label": "Signal Type",
                    "type": "select",
                    "options": ["price_cross", "ma_cross"],
                    "default": "price_cross",
                    "help": "Price crosses MA or MA crosses another MA"
                },
                {
                    "name": "fast_period",
                    "label": "Fast MA Period (for crossover)",
                    "type": "number",
                    "default": 20,
                    "min": 1,
                    "max": 200,
                    "help": "Fast MA period (only used for MA crossover)"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate moving averages"""
        ma_type = config.get('ma_type', 'EMA')
        period = config.get('period', 50)
        signal_type = config.get('signal_type', 'price_cross')
        
        # Calculate main MA
        if ma_type == 'SMA':
            data['ma'] = data['close'].rolling(window=period).mean()
        else:  # EMA
            data['ma'] = data['close'].ewm(span=period, adjust=False).mean()
        
        # If MA crossover, calculate fast MA too
        if signal_type == 'ma_cross':
            fast_period = config.get('fast_period', 20)
            if ma_type == 'SMA':
                data['ma_fast'] = data['close'].rolling(window=fast_period).mean()
            else:
                data['ma_fast'] = data['close'].ewm(span=fast_period, adjust=False).mean()
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any], 
        strategy_direction: str
    ) -> bool:
        """
        Check MA entry conditions.
        
        LONG: Price crosses above MA OR fast MA crosses above slow MA
        SHORT: Price crosses below MA OR fast MA crosses below slow MA
        """
        if index < 1:
            return False
        
        signal_type = config.get('signal_type', 'price_cross')
        
        # Price crossover signal
        if signal_type == 'price_cross':
            if 'ma' not in data.columns:
                return False
            
            current_price = data.loc[index, 'close']
            prev_price = data.loc[index - 1, 'close']
            current_ma = data.loc[index, 'ma']
            prev_ma = data.loc[index - 1, 'ma']
            
            if pd.isna(current_ma) or pd.isna(prev_ma):
                return False
            
            if strategy_direction == 'LONG':
                # Price crosses above MA
                return prev_price <= prev_ma and current_price > current_ma
            else:  # SHORT
                # Price crosses below MA
                return prev_price >= prev_ma and current_price < current_ma
        
        # MA crossover signal
        elif signal_type == 'ma_cross':
            if 'ma_fast' not in data.columns or 'ma' not in data.columns:
                return False
            
            current_fast = data.loc[index, 'ma_fast']
            prev_fast = data.loc[index - 1, 'ma_fast']
            current_slow = data.loc[index, 'ma']
            prev_slow = data.loc[index - 1, 'ma']
            
            if pd.isna(current_fast) or pd.isna(prev_fast) or pd.isna(current_slow) or pd.isna(prev_slow):
                return False
            
            if strategy_direction == 'LONG':
                # Fast MA crosses above slow MA
                return prev_fast <= prev_slow and current_fast > current_slow
            else:  # SHORT
                # Fast MA crosses below slow MA
                return prev_fast >= prev_slow and current_fast < current_slow
        
        return False