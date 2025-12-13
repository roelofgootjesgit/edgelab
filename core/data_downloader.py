"""
data_downloader.py
==================

Download historical market data from Yahoo Finance.

Note: Caching is handled by DataManager + LocalStorage.
This module only downloads fresh data from Yahoo Finance.

Author: QuantMetrics Development Team
Version: 2.0
"""

import yfinance as yf
import pandas as pd
from typing import Optional


# Symbol mapping: EdgeLab symbols to Yahoo Finance tickers
SYMBOL_MAP = {
    'XAUUSD': 'GC=F',      # Gold Futures
    'EURUSD': 'EURUSD=X',  # EUR/USD Forex
    'GBPUSD': 'GBPUSD=X',  # GBP/USD Forex
    'USDJPY': 'JPY=X',     # USD/JPY Forex
    'BTCUSD': 'BTC-USD',   # Bitcoin
    'ETHUSD': 'ETH-USD',   # Ethereum
    'SPX': '^GSPC',        # S&P 500
    'NQ': 'NQ=F',          # Nasdaq Futures
    'US30': 'YM=F',        # Dow Jones Futures
}


class DataDownloader:
    """
    Download historical OHLCV data from Yahoo Finance.
    
    Features:
    - Yahoo Finance integration
    - Symbol mapping (EdgeLab -> Yahoo tickers)
    - Data validation
    - Column standardization
    
    Note: Caching is handled by DataManager.
    """
    
    def __init__(self):
        """Initialize downloader."""
        pass
    
    def download(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "15m"
    ) -> pd.DataFrame:
        """
        Download historical data for symbol.
        
        Args:
            symbol: EdgeLab symbol (e.g., 'XAUUSD')
            period: Data period ('5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            interval: Candle interval ('1m', '5m', '15m', '30m', '1h', '1d', '1wk')
            
        Returns:
            DataFrame with columns: open, high, low, close, volume
            Index is DatetimeIndex
            
        Raises:
            ValueError: If symbol not supported or download fails
        """
        symbol = symbol.upper()
        
        # Yahoo Finance limitation: intraday data only available for last 60 days
        intraday_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']
        if interval in intraday_intervals:
            long_periods = ['6mo', '1y', '2y', '5y', 'max']
            if period in long_periods:
                print(f"[Warning] {interval} data limited to 60 days by Yahoo Finance")
                period = "60d"
        
        # Get Yahoo Finance ticker
        ticker = SYMBOL_MAP.get(symbol)
        if ticker is None:
            # Try using symbol directly (might be valid Yahoo ticker)
            ticker = symbol
            print(f"[Note] Symbol {symbol} not in map, trying as Yahoo ticker")
        
        # Download from Yahoo Finance
        print(f"[Download] {symbol} ({ticker}) - {period} @ {interval}...")
        
        try:
            data = yf.download(
                tickers=ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True
            )
        except Exception as e:
            raise ValueError(f"Download failed for {symbol}: {e}")
        
        if data.empty:
            raise ValueError(f"No data returned for {symbol}")
        
        # Flatten multi-level columns if present (yfinance quirk)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0].lower() for col in data.columns]
        else:
            data.columns = [col.lower() for col in data.columns]
        
        # Validate required columns
        required = ['open', 'high', 'low', 'close']
        missing = [col for col in required if col not in data.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        # Ensure volume exists (some instruments don't have it)
        if 'volume' not in data.columns:
            data['volume'] = 0
        
        print(f"[Download] Got {len(data)} rows for {symbol}")
        return data
    
    def get_supported_symbols(self) -> list:
        """Return list of supported symbols."""
        return list(SYMBOL_MAP.keys())
    
    def is_symbol_supported(self, symbol: str) -> bool:
        """Check if symbol is in the supported list."""
        return symbol.upper() in SYMBOL_MAP