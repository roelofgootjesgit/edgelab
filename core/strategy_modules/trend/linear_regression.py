"""
linear_regression.py - Linear Regression
Statistical trend line with channel
"""

import pandas as pd
import numpy as np
from typing import Dict
from core.strategy_modules.base import BaseModule


class LinearRegressionModule(BaseModule):
    
    @property
    def name(self) -> str:
        return "Linear Regression"
    
    @property
    def category(self) -> str:
        return "trend"
    
    @property
    def description(self) -> str:
        return "Statistical trend line. Price above = bullish."
    
    def get_config_schema(self) -> Dict:
        return {
            "fields": [
                {"name": "period", "label": "Period", "type": "number",
                 "default": 50, "min": 20, "max": 200},
                {"name": "std_dev", "label": "Std Dev Multiplier", "type": "number",
                 "default": 2.0, "min": 1.0, "max": 3.0, "step": 0.5}
            ]
        }
    
    def calculate(self, data: pd.DataFrame, config: Dict) -> pd.DataFrame:
        df = data.copy()
        df = df.reset_index(drop=False)
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp'})
        elif 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        period = config.get('period', 50)
        std_multiplier = config.get('std_dev', 2.0)
        
        def linreg(series):
            """Calculate linear regression"""
            if len(series) < 2:
                return np.nan
            x = np.arange(len(series))
            y = series.values
            slope, intercept = np.polyfit(x, y, 1)
            return slope * (len(series) - 1) + intercept
        
        # Linear regression line
        df['linreg'] = df['close'].rolling(window=period).apply(linreg, raw=False)
        
        # Standard deviation for channel
        df['linreg_std'] = df['close'].rolling(window=period).std()
        
        # Upper and lower bands
        df['linreg_upper'] = df['linreg'] + (df['linreg_std'] * std_multiplier)
        df['linreg_lower'] = df['linreg'] - (df['linreg_std'] * std_multiplier)
        
        # Slope (trend direction)
        df['linreg_slope'] = df['linreg'].diff()
        
        return df
    
    def check_entry_condition(self, data: pd.DataFrame, index: int,
                             config: Dict, direction: str) -> bool:
        if index < 1:
            return False
        
        curr = data.iloc[index]
        
        if pd.isna(curr['linreg']) or pd.isna(curr['linreg_slope']):
            return False
        
        price = curr['close']
        
        if direction == 'LONG':
            # Price above regression line, positive slope
            return price > curr['linreg'] and curr['linreg_slope'] > 0
        
        else:  # SHORT
            # Price below regression line, negative slope
            return price < curr['linreg'] and curr['linreg_slope'] < 0