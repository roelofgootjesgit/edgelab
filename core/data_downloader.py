"""
data_downloader.py
==================

Download historical market data from Yahoo Finance.
Includes caching system for performance optimization.

Author: EdgeLab Development Team
Version: 1.0
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


# Symbol mapping: EdgeLab symbols to Yahoo Finance tickers
SYMBOL_MAP = {
    'XAUUSD': 'GC=F',      # Gold Futures
    'EURUSD': 'EURUSD=X',  # EUR/USD Forex
    'GBPUSD': 'GBPUSD=X',  # GBP/USD Forex
    'USDJPY': 'JPY=X',     # USD/JPY Forex
    'BTCUSD': 'BTC-USD',   # Bitcoin
    'SPX': '^GSPC',        # S&P 500
    'NQ': 'NQ=F',          # Nasdaq Futures
}


class DataDownloader:
    """
    Download and cache historical OHLCV data.
    
    Features:
    - Yahoo Finance integration
    - Parquet caching for fast reload
    - Data validation
    - Multiple symbol support
    """
    
    def __init__(self, cache_dir: str = "data/market_cache"):
        """
        Initialize downloader with cache directory.
        
        Args:
            cache_dir: Directory for cached data files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
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
            period: Data period ('1mo', '3mo', '6mo', '1y')
            interval: Candle interval ('1m', '5m', '15m', '1h', '1d')
            
        Returns:
            DataFrame with columns: open, high, low, close, volume
            
        Raises:
            ValueError: If symbol not supported or download fails
        """
        # Check cache first
        cached_data = self._load_from_cache(symbol, period, interval)
        if cached_data is not None:
            print(f"Loaded {symbol} from cache ({len(cached_data)} rows)")
            return cached_data
        
        # Get Yahoo Finance ticker
        ticker = SYMBOL_MAP.get(symbol.upper())
        if ticker is None:
            raise ValueError(f"Symbol not supported: {symbol}. Supported: {list(SYMBOL_MAP.keys())}")
        def download(
            self,
            symbol: str,
            period: str = "6mo",
            interval: str = "15m"
        ) -> pd.DataFrame:
            """
            Download historical data for symbol.
            """
            # Yahoo Finance limitation: intraday data only available for last 60 days
            if interval in ['1m', '5m', '15m', '30m', '1h']:
                if period in ['6mo', '1y', '2y']:
                    print(f"Note: {interval} data limited to 60 days. Adjusting period.")
                    period = "60d"
            
            # Check cache first
            cached_data = self._load_from_cache(symbol, period, interval)
            # ... rest of method    
        
        # Download from Yahoo Finance
        print(f"Downloading {symbol} ({ticker}) - {period} @ {interval}...")
        
        data = yf.download(
            tickers=ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True
        )
        
        if data.empty:
            raise ValueError(f"No data returned for {symbol}")
        
        # Flatten multi-level columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0].lower() for col in data.columns]
        else:
            data.columns = [col.lower() for col in data.columns]
        
        # Validate required columns
        required = ['open', 'high', 'low', 'close']
        missing = [col for col in required if col not in data.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        
        # Save to cache
        self._save_to_cache(data, symbol, period, interval)
        
        print(f"Downloaded {len(data)} rows for {symbol}")
        return data
    
    def _get_cache_path(self, symbol: str, period: str, interval: str) -> Path:
        """Generate cache file path."""
        filename = f"{symbol}_{interval}_{period}.parquet"
        return self.cache_dir / filename
    
    def _load_from_cache(
        self,
        symbol: str,
        period: str,
        interval: str
    ) -> Optional[pd.DataFrame]:
        """Load data from cache if exists and fresh."""
        cache_path = self._get_cache_path(symbol, period, interval)
        
        if not cache_path.exists():
            return None
        
        # Check if cache is fresh (less than 1 hour old)
        cache_age = datetime.now().timestamp() - cache_path.stat().st_mtime
        if cache_age > 3600:  # 1 hour
            return None
        
        try:
            data = pd.read_parquet(cache_path)
            return data
        except Exception:
            return None
    
    def _save_to_cache(
        self,
        data: pd.DataFrame,
        symbol: str,
        period: str,
        interval: str
    ) -> None:
        """Save data to cache."""
        cache_path = self._get_cache_path(symbol, period, interval)
        
        try:
            data.to_parquet(cache_path)
        except Exception as e:
            print(f"Warning: Could not cache data: {e}")
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        for file in self.cache_dir.glob("*.parquet"):
            file.unlink()
        print("Cache cleared")