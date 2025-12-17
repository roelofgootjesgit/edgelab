"""
VWMA - Volume Weighted Moving Average
======================================

Moving average weighted by volume, giving more importance to high-volume periods.

Formula:
VWMA = Sum(Price × Volume) / Sum(Volume)

Features:
- Volume-weighted prices
- Institutional activity emphasis
- Confirms price moves with volume
- More reliable in high-volume areas
- Popular for identifying value zones

Entry Logic:
- LONG: price > VWMA AND volume increasing
- SHORT: price < VWMA AND volume increasing
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from core.strategy_modules.base import BaseModule


class VWMAModule(BaseModule):
    """Volume Weighted Moving Average indicator module"""
    
    @property
    def name(self) -> str:
        return "VWMA"
    
    @property
    def category(self) -> str:
        return "moving_averages"
    
    @property
    def description(self) -> str:
        return "Volume Weighted MA - emphasizes high-volume periods"
    
    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "period": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 500,
                    "default": 20,
                    "description": "VWMA period (typical: 20, 50)"
                },
                "source": {
                    "type": "string",
                    "enum": ["close", "hlc3", "ohlc4"],
                    "default": "close",
                    "description": "Price source for calculation"
                }
            },
            "required": ["period"]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate VWMA indicator"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        # Get source price
        if source == 'hlc3':
            prices = (data['high'] + data['low'] + data['close']) / 3
        elif source == 'ohlc4':
            prices = (data['open'] + data['high'] + data['low'] + data['close']) / 4
        else:
            prices = data[source]
        
        volume = data['volume']
        
        # Calculate VWMA
        pv = prices * volume
        vwma = pv.rolling(window=period).sum() / volume.rolling(window=period).sum()
        
        # Add to dataframe
        data[f'vwma_{period}'] = vwma
        
        # Calculate trend
        data[f'vwma_{period}_rising'] = vwma > vwma.shift(1)
        
        # Volume trend (for entry confirmation)
        avg_volume = volume.rolling(window=period).mean()
        data[f'vwma_{period}_volume_increasing'] = volume > avg_volume
        
        # Distance from price (%)
        data[f'vwma_{period}_dist_pct'] = ((prices - vwma) / vwma * 100)
        
        return data
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict[str, Any],
        direction: str
    ) -> bool:
        """Check if VWMA entry condition is met"""
        period = config.get('period', 20)
        source = config.get('source', 'close')
        
        vwma_col = f'vwma_{period}'
        vol_col = f'vwma_{period}_volume_increasing'
        
        if vwma_col not in data.columns or vol_col not in data.columns:
            return False
        
        if index < 1:
            return False
        
        current = data.iloc[index]
        
        # Get price
        if source == 'hlc3':
            price = (current['high'] + current['low'] + current['close']) / 3
        elif source == 'ohlc4':
            price = (current['open'] + current['high'] + current['low'] + current['close']) / 4
        else:
            price = current[source]
        
        vwma = current[vwma_col]
        volume_increasing = current[vol_col]
        
        if pd.isna(vwma) or pd.isna(volume_increasing):
            return False
        
        # Require volume confirmation
        if not volume_increasing:
            return False
        
        if direction == 'LONG':
            # Price above VWMA with increasing volume
            return price > vwma
        else:  # SHORT
            # Price below VWMA with increasing volume
            return price < vwma

