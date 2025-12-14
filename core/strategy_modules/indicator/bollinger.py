# core/strategy_modules/indicators/bollinger.py
"""
Bollinger Bands Module

Volatility indicator using standard deviations.
Mean reversion signals from band touches/crosses.
"""

from typing import Dict, Any
import pandas as pd
from core.strategy_modules.base import BaseModule


class BollingerBandsModule(BaseModule):
    """
    Bollinger Bands - Volatility and mean reversion indicator.
    
    Components:
    - Middle Band = SMA(20)
    - Upper Band = Middle + (2 * StdDev)
    - Lower Band = Middle - (2 * StdDev)
    
    Entry signals:
    - Bullish: Price touches/crosses below lower band (oversold bounce)
    - Bearish: Price touches/crosses above upper band (overbought drop)
    """
    
    @property
    def name(self) -> str:
        return "Bollinger Bands"
    
    @property
    def category(self) -> str:
        return "indicator"
    
    @property
    def description(self) -> str:
        return "Volatility bands for mean reversion strategies"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "Period",
                    "type": "number",
                    "default": 20,
                    "min": 2,
                    "max": 200,
                    "help": "SMA period for middle band"
                },
                {
                    "name": "std_dev",
                    "label": "Standard Deviations",
                    "type": "number",
                    "default": 2.0,
                    "min": 0.5,
                    "max": 5.0,
                    "step": 0.1,
                    "help": "Number of standard deviations for bands"
                },
                {
                    "name": "signal_type",
                    "label": "Signal Type",
                    "type": "select",
                    "options": ["touch", "cross", "squeeze"],
                    "default": "cross",
                    "help": "Touch band, cross band, or squeeze breakout"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        period = config.get('period', 20)
        std_dev = config.get('std_dev', 2.0)
        
        # Calculate middle band (SMA)
        data['bb_middle'] = data['close'].rolling(window=period).mean()
        
        # Calculate standard deviation
        std = data['close'].rolling(window=period).std()
        
        # Calculate upper and lower bands
        data['bb_upper'] = data['bb_middle'] + (std * std_dev)
        data['bb_lower'] = data['bb_middle'] - (std * std_dev)
        
        # Calculate band width (for squeeze detection)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any], 
        strategy_direction: str
    ) -> bool:
        """
        Check Bollinger Bands entry conditions.
        
        LONG: Price bounces from lower band (mean reversion up)
        SHORT: Price bounces from upper band (mean reversion down)
        """
        if index < 1:
            return False
        
        if 'bb_upper' not in data.columns or 'bb_lower' not in data.columns:
            return False
        
        current_close = data.loc[index, 'close']
        prev_close = data.loc[index - 1, 'close']
        current_upper = data.loc[index, 'bb_upper']
        current_lower = data.loc[index, 'bb_lower']
        prev_upper = data.loc[index - 1, 'bb_upper']
        prev_lower = data.loc[index - 1, 'bb_lower']
        
        if pd.isna(current_upper) or pd.isna(current_lower):
            return False
        
        signal_type = config.get('signal_type', 'cross')
        
        if signal_type == 'touch':
            if strategy_direction == 'LONG':
                # Price touches lower band
                return current_close <= current_lower
            else:
                # Price touches upper band
                return current_close >= current_upper
        
        elif signal_type == 'cross':
            if strategy_direction == 'LONG':
                # Price crosses back above lower band
                return prev_close < prev_lower and current_close > current_lower
            else:
                # Price crosses back below upper band
                return prev_close > prev_upper and current_close < current_upper
        
        elif signal_type == 'squeeze':
            # Bollinger Squeeze breakout
            if index < 20:
                return False
            
            # Check if band width is contracting (squeeze)
            current_width = data.loc[index, 'bb_width']
            avg_width = data.loc[index-19:index, 'bb_width'].mean()
            
            is_squeeze = current_width < avg_width * 0.8
            
            if not is_squeeze:
                return False
            
            # Check for breakout
            if strategy_direction == 'LONG':
                return current_close > data.loc[index, 'bb_middle']
            else:
                return current_close < data.loc[index, 'bb_middle']
        
        return False