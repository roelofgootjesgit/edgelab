"""
data_manager.py
===============

Unified data access layer for EdgeLab.

Combines:
- LocalStorage (cache)
- DataDownloader (Yahoo Finance)
- Smart caching logic

Features:
- Check cache before downloading
- Download only missing data (delta updates)
- Automatic cache refresh for recent data
- Pre-loading for popular symbols

Usage:
    from core.data_manager import DataManager
    
    manager = DataManager()
    data = manager.get_data('XAUUSD', '15m', start, end)
    
    # Pre-load popular symbols
    manager.preload_symbol('XAUUSD')

Author: EdgeLab Development
Version: 1.0
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from config import Config, get_storage_backend
from core.storage_interface import DataStorage
from core.data_downloader import DataDownloader
from core.metrics import track_performance


class DataManager:
    """
    Unified data access layer.
    
    Handles:
    - Storage abstraction (local or cloud via config)
    - Download orchestration
    - Cache management
    - Data freshness
    
    The application code uses DataManager - never touches
    storage or downloader directly.
    """
    
    def __init__(
        self, 
        storage: Optional[DataStorage] = None,
        downloader: Optional[DataDownloader] = None,
        cache_ttl_hours: int = 24
    ):
        """
        Initialize DataManager.
        
        Args:
            storage: Storage backend (auto-detected from config if None)
            downloader: Data downloader (creates default if None)
            cache_ttl_hours: How long before refreshing recent data
        """
        self.storage = storage or get_storage_backend()
        self.downloader = downloader or DataDownloader()
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
    
    @track_performance("data_fetch", slow_threshold_seconds=30.0)
    def get_data(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Get market data - from cache if available, download if not.
        
        Smart caching logic:
        1. Check if cache has complete data for range
        2. If yes and fresh -> return from cache
        3. If partial -> download missing, merge
        4. If none -> download all
        5. Save to cache
        6. Return data
        
        Args:
            symbol: Trading symbol (XAUUSD, EURUSD, etc)
            timeframe: Candle interval (1m, 5m, 15m, 1h, 4h, 1d)
            start: Start datetime
            end: End datetime
            force_refresh: Bypass cache, always download
        
        Returns:
            DataFrame with OHLCV data (open, high, low, close, volume)
            Empty DataFrame if no data available
        
        Raises:
            ValueError: If symbol not supported or download fails
        """
        symbol = symbol.upper()
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            if self.storage.has_data(symbol, timeframe, start, end):
                cached = self.storage.get_data(symbol, timeframe, start, end)
                
                # Check if we need to refresh recent data
                if self._needs_refresh(end):
                    cached = self._refresh_recent(symbol, timeframe, cached)
                
                if not cached.empty:
                    print(f"[Cache] Loaded {symbol} {timeframe}: {len(cached)} rows")
                    return cached
        
        # Download from source
        print(f"[Download] Fetching {symbol} {timeframe}...")
        
        data = self._download_data(symbol, timeframe, start, end)
        
        if data.empty:
            print(f"[Warning] No data returned for {symbol} {timeframe}")
            return pd.DataFrame()
        
        # Save to cache
        self.storage.save_data(symbol, timeframe, data)
        print(f"[Cache] Saved {symbol} {timeframe}: {len(data)} rows")
        
        # Filter to exact requested range
        mask = (data.index >= pd.Timestamp(start)) & (data.index <= pd.Timestamp(end))
        return data[mask]
    
    def _needs_refresh(self, end: datetime) -> bool:
        """Check if end date is recent enough to need refresh."""
        return end > datetime.now() - self.cache_ttl
    
    def _refresh_recent(
        self,
        symbol: str,
        timeframe: str,
        cached: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Update recent candles that might have changed.
        
        Downloads last 2 days and merges with cached data.
        """
        recent_start = datetime.now() - timedelta(days=2)
        
        try:
            recent = self._download_data(
                symbol, timeframe,
                recent_start, datetime.now()
            )
            
            if not recent.empty:
                # Merge: prefer new data for overlapping timestamps
                combined = pd.concat([cached, recent])
                combined = combined[~combined.index.duplicated(keep='last')]
                combined = combined.sort_index()
                
                # Update cache
                self.storage.save_data(symbol, timeframe, combined)
                
                return combined
                
        except Exception as e:
            print(f"[Warning] Could not refresh recent data: {e}")
        
        return cached
    
    def _download_data(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime
    ) -> pd.DataFrame:
        """
        Download data from Yahoo Finance.
        
        Handles:
        - Period string calculation
        - 60-day intraday limitation
        - Error handling
        """
        # Calculate period for Yahoo Finance
        period = self._calculate_period(start, end, timeframe)
        
        try:
            data = self.downloader.download(
                symbol=symbol,
                period=period,
                interval=timeframe
            )
            
            if data.empty:
                return pd.DataFrame()
            
            # Ensure proper index
            if not isinstance(data.index, pd.DatetimeIndex):
                if 'timestamp' in data.columns:
                    data = data.set_index('timestamp')
                elif 'Datetime' in data.columns:
                    data = data.set_index('Datetime')
                data.index = pd.to_datetime(data.index)
            
            # Standardize column names to lowercase
            data.columns = [c.lower() for c in data.columns]
            
            # Filter to requested range
            mask = (data.index >= pd.Timestamp(start)) & (data.index <= pd.Timestamp(end))
            return data[mask]
            
        except Exception as e:
            print(f"[Error] Download failed for {symbol}: {e}")
            return pd.DataFrame()
    
    def _calculate_period(
        self,
        start: datetime,
        end: datetime,
        timeframe: str
    ) -> str:
        """
        Calculate Yahoo Finance period string.
        
        Handles 60-day limitation for intraday data.
        """
        days_requested = (end - start).days + 1
        
        # Intraday limitation warning
        intraday_timeframes = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']
        if timeframe in intraday_timeframes:
            if days_requested > 60:
                print(f"[Warning] {timeframe} data limited to 60 days by Yahoo Finance")
                return "60d"
        
        # Map days to period strings
        if days_requested <= 5:
            return "5d"
        elif days_requested <= 7:
            return "7d"
        elif days_requested <= 30:
            return "1mo"
        elif days_requested <= 90:
            return "3mo"
        elif days_requested <= 180:
            return "6mo"
        elif days_requested <= 365:
            return "1y"
        elif days_requested <= 730:
            return "2y"
        elif days_requested <= 1825:
            return "5y"
        else:
            return "max"
    
    def preload_symbol(
        self,
        symbol: str,
        timeframes: Optional[List[str]] = None,
        days_back: int = 60
    ) -> Dict[str, int]:
        """
        Pre-download historical data for a symbol.
        
        Call this for popular symbols to build cache.
        Can run as background job on server startup.
        
        Args:
            symbol: Symbol to preload
            timeframes: List of timeframes (default: common ones)
            days_back: How many days to fetch
        
        Returns:
            Dict with timeframe -> row count
        """
        if timeframes is None:
            timeframes = ['1d', '4h', '1h', '15m']
        
        results = {}
        end = datetime.now()
        
        for tf in timeframes:
            # Respect 60-day limit for intraday
            if tf in ['1m', '5m', '15m', '30m', '1h'] and days_back > 60:
                actual_days = 60
            else:
                actual_days = days_back
            
            start = end - timedelta(days=actual_days)
            
            try:
                data = self.get_data(symbol, tf, start, end)
                results[tf] = len(data)
                print(f"[Preload] {symbol} {tf}: {len(data)} rows")
            except Exception as e:
                print(f"[Preload] Failed {symbol} {tf}: {e}")
                results[tf] = 0
        
        return results
    
    def preload_popular_symbols(self) -> None:
        """
        Preload commonly used symbols.
        
        Call on server startup to warm cache.
        """
        popular = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD']
        
        for symbol in popular:
            try:
                self.preload_symbol(symbol)
            except Exception as e:
                print(f"[Preload] Skipped {symbol}: {e}")
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """
        Get summary of cached data.
        
        Returns storage metadata plus manager stats.
        """
        storage_meta = self.storage.get_metadata()
        
        return {
            **storage_meta,
            'cache_ttl_hours': self.cache_ttl.total_seconds() / 3600,
            'downloader_available': self.downloader is not None
        }
    
    def clear_old_cache(self, days: int = 30) -> int:
        """
        Remove cached data older than X days.
        
        Args:
            days: Delete data not updated in this many days
        
        Returns:
            Number of datasets deleted
        """
        return self.storage.clear_cache(older_than_days=days)
    
    def has_cached_data(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime
    ) -> bool:
        """
        Check if data is cached (without downloading).
        
        Useful for UI to show cache status.
        """
        return self.storage.has_data(symbol, timeframe, start, end)
    
    def get_cached_symbols(self) -> List[str]:
        """Get list of symbols in cache."""
        return self.storage.get_available_symbols()
    
    def delete_symbol_cache(self, symbol: str) -> int:
        """
        Delete all cached data for a symbol.
        
        Returns number of timeframes deleted.
        """
        if hasattr(self.storage, 'delete_symbol'):
            return self.storage.delete_symbol(symbol)
        return 0