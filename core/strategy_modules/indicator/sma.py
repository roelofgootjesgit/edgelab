# core/strategy_modules/indicators/sma.py
"""
SMA (Simple Moving Average) Module

The classic trend indicator - arithmetic average of price over N periods.
Foundation for Golden Cross (50/200 SMA) and trend following strategies.
"""

from typing import Dict, Any
import pandas as pd
from core.strategy_modules.base import BaseModule


class SMAModule(BaseModule):
    """
    Simple Moving Average - Trend identification and support/resistance.
    
    Popular configurations:
    - SMA(20): Short-term trend
    - SMA(50): Medium-term trend  
    - SMA(200): Long-term trend (major S/R)
    
    Entry signals:
    - Price crosses SMA (trend change)
    - Fast SMA crosses slow SMA (Golden Cross / Death Cross)
    """
    
    @property
    def name(self) -> str:
        return "SMA (Simple Moving Average)"
    
    @property
    def category(self) -> str:
        return "indicator"
    
    @property
    def description(self) -> str:
        return "Classic trend indicator - arithmetic average of price"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "fields": [
                {
                    "name": "period",
                    "label": "Period",
                    "type": "number",
                    "default": 50,
                    "min": 1,
                    "max": 500,
                    "help": "Number of periods (20=short, 50=medium, 200=long)"
                },
                {
                    "name": "source",
                    "label": "Price Source",
                    "type": "select",
                    "options": ["close", "open", "high", "low", "hl2", "hlc3", "ohlc4"],
                    "default": "close",
                    "help": "Which price to use for calculation"
                },
                {
                    "name": "condition_type",
                    "label": "Condition Type",
                    "type": "select",
                    "options": [
                        "price_cross_above",
                        "price_cross_below", 
                        "price_above",
                        "price_below",
                        "sma_cross_above",
                        "sma_cross_below"
                    ],
                    "default": "price_cross_above",
                    "help": "What triggers entry signal"
                },
                {
                    "name": "cross_sma_period",
                    "label": "Cross SMA Period (for SMA crossover)",
                    "type": "number",
                    "default": 200,
                    "min": 1,
                    "max": 500,
                    "help": "Slow SMA period for crossover strategies (e.g., 50/200 Golden Cross)"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Calculate SMA indicator.
        
        Formula: SMA = Sum(Price[i...i+n]) / n
        """
        period = config.get('period', 50)
        source = config.get('source', 'close')
        condition_type = config.get('condition_type', 'price_cross_above')
        
        # Get price source
        if source == 'hl2':
            price = (data['high'] + data['low']) / 2
        elif source == 'hlc3':
            price = (data['high'] + data['low'] + data['close']) / 3
        elif source == 'ohlc4':
            price = (data['open'] + data['high'] + data['low'] + data['close']) / 4
        else:
            price = data[source]
        
        # Calculate main SMA
        column_name = f'sma_{period}'
        data[column_name] = price.rolling(window=period, min_periods=period).mean()
        
        # If crossover condition, calculate second SMA
        if 'sma_cross' in condition_type:
            cross_period = config.get('cross_sma_period', 200)
            cross_column = f'sma_{cross_period}'
            data[cross_column] = price.rolling(window=cross_period, min_periods=cross_period).mean()
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any], 
        strategy_direction: str
    ) -> bool:
        """
        Check SMA entry conditions.
        
        Supports:
        - Price crosses above/below SMA
        - Price is above/below SMA (trend filter)
        - Fast SMA crosses above/below slow SMA (Golden/Death Cross)
        """
        if index < 1:
            return False
        
        period = config.get('period', 50)
        source = config.get('source', 'close')
        condition_type = config.get('condition_type', 'price_cross_above')
        
        # Get price
        if source in data.columns:
            current_price = data.loc[index, source]
            prev_price = data.loc[index - 1, source]
        else:
            current_price = data.loc[index, 'close']
            prev_price = data.loc[index - 1, 'close']
        
        # Get SMA
        sma_column = f'sma_{period}'
        if sma_column not in data.columns:
            return False
        
        current_sma = data.loc[index, sma_column]
        prev_sma = data.loc[index - 1, sma_column]
        
        # Check for NaN
        if pd.isna(current_sma) or pd.isna(prev_sma):
            return False
        
        # --- PRICE CROSSOVER CONDITIONS ---
        
        if condition_type == 'price_cross_above':
            # Price crosses from below to above SMA
            return prev_price <= prev_sma and current_price > current_sma
        
        elif condition_type == 'price_cross_below':
            # Price crosses from above to below SMA
            return prev_price >= prev_sma and current_price < current_sma
        
        # --- PRICE POSITION CONDITIONS (Trend Filter) ---
        
        elif condition_type == 'price_above':
            # Price is above SMA (bullish trend filter)
            return current_price > current_sma
        
        elif condition_type == 'price_below':
            # Price is below SMA (bearish trend filter)
            return current_price < current_sma
        
        # --- SMA CROSSOVER CONDITIONS (Golden Cross / Death Cross) ---
        
        elif condition_type == 'sma_cross_above':
            # Fast SMA crosses above slow SMA (Golden Cross)
            cross_period = config.get('cross_sma_period', 200)
            cross_column = f'sma_{cross_period}'
            
            if cross_column not in data.columns:
                return False
            
            current_slow = data.loc[index, cross_column]
            prev_slow = data.loc[index - 1, cross_column]
            
            if pd.isna(current_slow) or pd.isna(prev_slow):
                return False
            
            # Fast (shorter period) crosses above slow (longer period)
            return prev_sma <= prev_slow and current_sma > current_slow
        
        elif condition_type == 'sma_cross_below':
            # Fast SMA crosses below slow SMA (Death Cross)
            cross_period = config.get('cross_sma_period', 200)
            cross_column = f'sma_{cross_period}'
            
            if cross_column not in data.columns:
                return False
            
            current_slow = data.loc[index, cross_column]
            prev_slow = data.loc[index - 1, cross_column]
            
            if pd.isna(current_slow) or pd.isna(prev_slow):
                return False
            
            # Fast crosses below slow
            return prev_sma >= prev_slow and current_sma < current_slow
        
        return False