"""
storage_interface.py
====================

Abstract base class for data storage backends.

This interface enables swapping storage implementations:
- LocalStorage: Parquet files on disk (MVP, 1-50 users)
- CloudStorage: S3 + PostgreSQL (Scale, 50-500 users)
- DistributedStorage: Multi-region (Enterprise, 500-1000+ users)

Application code uses this interface only.
Backend selection happens via configuration.

Usage:
    # Application code (never changes)
    storage: DataStorage = get_storage_backend()
    data = storage.get_data('XAUUSD', '15m', start, end)
    
    # Config determines which backend (changes per environment)
    # .env.local: STORAGE_TYPE=local
    # .env.cloud: STORAGE_TYPE=cloud

Author: EdgeLab Development
Version: 1.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime


class DataStorage(ABC):
    """
    Abstract storage interface for market data.
    
    All storage backends must implement these methods.
    This ensures consistent behavior regardless of backend.
    
    Design Principles:
    - Simple interface (5 core methods)
    - No backend-specific logic exposed
    - Metadata tracking built-in
    - Clear error handling contract
    """
    
    @abstractmethod
    def has_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start: datetime, 
        end: datetime
    ) -> bool:
        """
        Check if storage has complete data for requested range.
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD', 'EURUSD')
            timeframe: Candle interval (e.g., '15m', '1h', '1d')
            start: Start of requested date range
            end: End of requested date range
        
        Returns:
            True if storage has complete data for entire range
            False if data is missing or partial
        
        Note:
            This is a fast check - does not load data.
            Used by DataManager to decide if download needed.
        """
        pass
    
    @abstractmethod
    def get_data(
        self, 
        symbol: str, 
        timeframe: str,
        start: datetime, 
        end: datetime
    ) -> pd.DataFrame:
        """
        Retrieve market data from storage.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle interval
            start: Start of requested date range
            end: End of requested date range
        
        Returns:
            DataFrame with columns: open, high, low, close, volume
            Index: DatetimeIndex (UTC)
            Empty DataFrame if no data available
        
        Note:
            Returns only data within requested range.
            Caller should check has_data() first for efficiency.
        """
        pass
    
    @abstractmethod
    def save_data(
        self, 
        symbol: str, 
        timeframe: str, 
        data: pd.DataFrame
    ) -> None:
        """
        Store market data.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle interval
            data: DataFrame with OHLCV columns and DatetimeIndex
        
        Behavior:
            - Merges with existing data (no duplicates)
            - Updates metadata automatically
            - Handles concurrent writes safely (implementation-specific)
        
        Raises:
            ValueError: If data format invalid
            IOError: If storage write fails
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get storage statistics and dataset information.
        
        Returns:
            Dictionary with:
            - storage_type: str ('local', 'cloud', 'distributed')
            - total_size_mb: float (total storage used)
            - symbols: int (number of unique symbols)
            - datasets: int (number of symbol/timeframe combinations)
            - datasets_detail: dict (per-dataset metadata)
        
        Example:
            {
                'storage_type': 'local',
                'total_size_mb': 125.4,
                'symbols': 5,
                'datasets': 15,
                'datasets_detail': {
                    'XAUUSD_15m': {
                        'start': '2024-01-01T00:00:00',
                        'end': '2024-06-30T23:45:00',
                        'rows': 17280,
                        'last_updated': '2024-11-26T10:30:00',
                        'file_size_mb': 2.3
                    },
                    ...
                }
            }
        """
        pass
    
    @abstractmethod
    def clear_cache(self, older_than_days: int = 30) -> int:
        """
        Remove old cached data.
        
        Args:
            older_than_days: Delete data not accessed in this many days
        
        Returns:
            Number of datasets deleted
        
        Note:
            Implementation should be safe - never delete data
            that might still be needed. When in doubt, keep it.
        """
        pass
    
    # Optional methods with default implementations
    
    def get_available_symbols(self) -> list:
        """
        List all symbols with cached data.
        
        Returns:
            List of symbol strings (e.g., ['XAUUSD', 'EURUSD'])
        
        Default implementation extracts from metadata.
        Override for more efficient implementation.
        """
        metadata = self.get_metadata()
        symbols = set()
        for key in metadata.get('datasets_detail', {}).keys():
            symbol = key.split('_')[0]
            symbols.add(symbol)
        return sorted(list(symbols))
    
    def get_available_timeframes(self, symbol: str) -> list:
        """
        List all timeframes cached for a symbol.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            List of timeframe strings (e.g., ['15m', '1h', '1d'])
        
        Default implementation extracts from metadata.
        Override for more efficient implementation.
        """
        metadata = self.get_metadata()
        timeframes = []
        prefix = f"{symbol.upper()}_"
        for key in metadata.get('datasets_detail', {}).keys():
            if key.startswith(prefix):
                tf = key.replace(prefix, '')
                timeframes.append(tf)
        return sorted(timeframes)
    
    def get_date_range(
        self, 
        symbol: str, 
        timeframe: str
    ) -> Optional[tuple]:
        """
        Get cached date range for symbol/timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle interval
        
        Returns:
            Tuple of (start_datetime, end_datetime) or None if no data
        
        Default implementation extracts from metadata.
        Override for more efficient implementation.
        """
        metadata = self.get_metadata()
        key = f"{symbol.upper()}_{timeframe}"
        detail = metadata.get('datasets_detail', {}).get(key)
        
        if not detail:
            return None
        
        return (
            datetime.fromisoformat(detail['start']),
            datetime.fromisoformat(detail['end'])
        )