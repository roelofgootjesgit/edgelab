"""
indicators.py
=============

Technical indicator calculations for EdgeLab.
Uses 'ta' library for reliable indicator implementations.

Author: QuantMetrics Development Team
Version: 1.0
"""

import pandas as pd
import ta


class IndicatorEngine:
    """
    Calculate technical indicators on OHLCV data.
    
    Supported indicators:
    - RSI (Relative Strength Index)
    - SMA (Simple Moving Average)
    - EMA (Exponential Moving Average)
    - MACD (Moving Average Convergence Divergence)
    - Bollinger Bands
    - ATR (Average True Range)
    - ADX (Average Directional Index)
    """
    
    def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all common indicators.
        
        Args:
            data: DataFrame with columns: open, high, low, close, volume
            
        Returns:
            DataFrame with added indicator columns
        """
        df = data.copy()
        
        # RSI
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        
        # Moving Averages
        df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['ema_20'] = ta.trend.ema_indicator(df['close'], window=20)
        
        # MACD
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_histogram'] = macd.macd_diff()
        
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['bb_upper'] = bollinger.bollinger_hband()
        df['bb_middle'] = bollinger.bollinger_mavg()
        df['bb_lower'] = bollinger.bollinger_lband()
        
        # ATR (Average True Range)
        df['atr'] = ta.volatility.average_true_range(
            df['high'], df['low'], df['close'], window=14
        )
        
        # ADX (Average Directional Index)
        df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
        
        return df
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        return ta.momentum.rsi(data['close'], window=period)
    
    def calculate_sma(self, data: pd.DataFrame, period: int = 50) -> pd.Series:
        """Calculate Simple Moving Average."""
        return ta.trend.sma_indicator(data['close'], window=period)
    
    def calculate_ema(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return ta.trend.ema_indicator(data['close'], window=period)
    
    def calculate_macd(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicator with signal and histogram."""
        macd = ta.trend.MACD(data['close'])
        return pd.DataFrame({
            'macd': macd.macd(),
            'signal': macd.macd_signal(),
            'histogram': macd.macd_diff()
        })
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        return ta.volatility.average_true_range(
            data['high'], data['low'], data['close'], window=period
        )
    
    def calculate_adx(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index."""
        return ta.trend.adx(data['high'], data['low'], data['close'], window=period)