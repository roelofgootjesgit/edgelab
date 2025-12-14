"""
premium_discount_zones.py
=========================

Premium/Discount Zones - ICT price positioning analysis
Identifies whether price is in premium (expensive) or discount (cheap) zones

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class PremiumDiscountZonesModule(BaseModule):
    """
    Premium/Discount Zones detection module.
    
    Concept:
    - Calculate range high/low over lookback period
    - Equilibrium = 50% level = (high + low) / 2
    - Premium Zone = Above equilibrium (top 50% of range)
    - Discount Zone = Below equilibrium (bottom 50% of range)
    
    ICT Logic:
    - Buy in discount (price cheap relative to range)
    - Sell in premium (price expensive relative to range)
    
    Trading Logic:
    - LONG when price enters discount zone
    - SHORT when price enters premium zone
    
    Parameters:
    - lookback_candles: Period for range calculation (default 50)
    - extreme_threshold_pct: Deep discount/premium threshold (default 25%)
      25% = bottom/top quarter of range
    """
    
    @property
    def name(self) -> str:
        return "Premium/Discount Zones"
    
    @property
    def category(self) -> str:
        return "ict"
    
    @property
    def description(self) -> str:
        return "ICT price positioning - buy discount, sell premium"
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema for UI generation."""
        return {
            "fields": [
                {
                    "name": "lookback_candles",
                    "label": "Lookback Period (candles)",
                    "type": "number",
                    "default": 50,
                    "min": 20,
                    "max": 100,
                    "step": 10,
                    "help": "Period to calculate price range"
                },
                {
                    "name": "extreme_threshold_pct",
                    "label": "Extreme Zone Threshold (%)",
                    "type": "number",
                    "default": 25,
                    "min": 20,
                    "max": 40,
                    "step": 5,
                    "help": "Deep discount/premium percentage (25% = bottom/top quarter)"
                }
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """
        Calculate Premium/Discount zones.
        
        Args:
            data: OHLCV DataFrame
            config: Configuration dictionary
            
        Returns:
            DataFrame with zone columns added
        """
        df = data.copy()
        
        # Extract config
        lookback = config.get('lookback_candles', 50)
        extreme_threshold = config.get('extreme_threshold_pct', 25) / 100.0
        
        # Initialize columns
        df['range_high'] = np.nan
        df['range_low'] = np.nan
        df['equilibrium'] = np.nan
        df['premium_threshold'] = np.nan
        df['discount_threshold'] = np.nan
        df['price_position_pct'] = np.nan
        df['in_premium'] = False
        df['in_discount'] = False
        df['in_extreme_premium'] = False
        df['in_extreme_discount'] = False
        df['zone'] = ''
        
        # Calculate zones for each candle
        for i in range(lookback, len(df)):
            # Get range over lookback period
            lookback_data = df.iloc[i-lookback:i]
            range_high = lookback_data['high'].max()
            range_low = lookback_data['low'].min()
            
            # Calculate levels
            equilibrium = (range_high + range_low) / 2
            range_size = range_high - range_low
            
            # Premium/Discount thresholds (50% level)
            premium_threshold = equilibrium
            discount_threshold = equilibrium
            
            # Extreme zone thresholds
            extreme_premium_level = range_high - (range_size * extreme_threshold)
            extreme_discount_level = range_low + (range_size * extreme_threshold)
            
            # Current price position
            current_price = df.iloc[i]['close']
            
            # Calculate price position as percentage of range
            if range_size > 0:
                price_position_pct = ((current_price - range_low) / range_size) * 100
            else:
                price_position_pct = 50.0
            
            # Store values
            df.at[i, 'range_high'] = range_high
            df.at[i, 'range_low'] = range_low
            df.at[i, 'equilibrium'] = equilibrium
            df.at[i, 'premium_threshold'] = premium_threshold
            df.at[i, 'discount_threshold'] = discount_threshold
            df.at[i, 'price_position_pct'] = price_position_pct
            
            # Determine zone
            if current_price >= extreme_premium_level:
                df.at[i, 'in_extreme_premium'] = True
                df.at[i, 'in_premium'] = True
                df.at[i, 'zone'] = 'EXTREME_PREMIUM'
            elif current_price > equilibrium:
                df.at[i, 'in_premium'] = True
                df.at[i, 'zone'] = 'PREMIUM'
            elif current_price <= extreme_discount_level:
                df.at[i, 'in_extreme_discount'] = True
                df.at[i, 'in_discount'] = True
                df.at[i, 'zone'] = 'EXTREME_DISCOUNT'
            elif current_price < equilibrium:
                df.at[i, 'in_discount'] = True
                df.at[i, 'zone'] = 'DISCOUNT'
            else:
                df.at[i, 'zone'] = 'EQUILIBRIUM'
        
        return df
    
    def check_entry_condition(
        self, 
        data: pd.DataFrame, 
        index: int, 
        config: Dict,
        direction: str
    ) -> bool:
        """
        Check if entry condition is met at given index.
        
        Args:
            data: DataFrame with zone calculations
            index: Current candle index
            config: Configuration dictionary
            direction: 'LONG' or 'SHORT'
            
        Returns:
            True if entry condition met
        """
        if index >= len(data):
            return False
        
        candle = data.iloc[index]
        
        if direction == 'LONG':
            # Enter LONG when price is in discount zone
            # Prefer extreme discount for stronger signal
            return candle['in_discount'] == True
        
        elif direction == 'SHORT':
            # Enter SHORT when price is in premium zone
            # Prefer extreme premium for stronger signal
            return candle['in_premium'] == True
        
        return False