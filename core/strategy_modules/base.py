# core/strategy_modules/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any
import pandas as pd

class BaseModule(ABC):
    """
    Abstract base class for all strategy modules.
    
    Each module represents a tradable concept:
    - Indicators (RSI, MACD, Bollinger)
    - ICT concepts (FVG, Order Block, Liquidity)
    - Multi-timeframe (HTF trend, LTF entry)
    - Position sizing (Fixed, Kelly, Risk Ladder)
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Display name shown in UI"""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """
        Module category for UI organization:
        - 'indicator': Technical indicators
        - 'ict': Inner Circle Trader concepts
        - 'mtf': Multi-timeframe analysis
        - 'position_sizing': Risk management
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Short description for tooltips"""
        pass
    
    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for configuration UI.
        
        Format:
        {
            "fields": [
                {
                    "name": "period",
                    "label": "Period",
                    "type": "number",
                    "default": 14,
                    "min": 1,
                    "max": 200
                },
                {
                    "name": "direction",
                    "label": "Direction",
                    "type": "select",
                    "options": ["bullish", "bearish", "both"],
                    "default": "both"
                }
            ]
        }
        """
        pass
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Calculate indicator/signal and add to dataframe.
        
        Args:
            data: OHLCV dataframe
            config: User configuration from get_config_schema()
        
        Returns:
            data with new column(s) added
        """
        pass
    
    @abstractmethod
    def check_entry_condition(self, data: pd.DataFrame, index: int, config: Dict[str, Any], strategy_direction: str) -> bool:
        """
        Check if entry condition met at specific candle.
        
        Args:
            data: OHLCV dataframe with calculated indicators
            index: Current candle index to check
            config: User configuration
            strategy_direction: 'LONG' or 'SHORT' from overall strategy
        
        Returns:
            True if condition met, False otherwise
        """
        pass