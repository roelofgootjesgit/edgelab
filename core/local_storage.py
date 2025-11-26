"""
local_storage.py
================

Local filesystem storage using Parquet files.

Implements DataStorage interface for MVP deployment.
Scales to ~50 concurrent users on single VPS.

Directory Structure:
    data/
    └── market_cache/
        ├── XAUUSD/
        │   ├── 15m.parquet
        │   ├── 1h.parquet
        │   └── 1d.parquet
        ├── EURUSD/
        │   └── ...
        └── metadata.json

Features:
- Parquet compression (snappy) - 5-10x smaller than CSV
- Automatic merge with existing data
- Metadata tracking for fast has_data() checks
- Thread-safe file operations

Usage:
    from core.local_storage import LocalStorage
    
    storage = LocalStorage('data/market_cache')
    storage.save_data('XAUUSD', '15m', dataframe)
    data = storage.get_data('XAUUSD', '15m', start, end)

Author: EdgeLab Development
Version: 1.0
"""

from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, Optional
import threading

from core.storage_interface import DataStorage
from core.metrics import track_performance


class LocalStorage(DataStorage):
    """
    Local filesystem storage using Parquet format.
    
    Designed for:
    - MVP deployment (1-50 users)
    - Single VPS with SSD storage
    - Development and testing
    
    When to migrate to CloudStorage:
    - Storage exceeds 80GB
    - Concurrent users exceed 50
    - Need multi-server deployment
    """
    
    def __init__(self, base_path: str = "data/market_cache"):
        """
        Initialize local storage.
        
        Args:
            base_path: Root directory for market data cache
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.base_path / "metadata.json"
        self._lock = threading.Lock()
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load metadata: {e}")
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self) -> None:
        """Persist metadata to JSON file."""
        with self._lock:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
    
    def _get_file_path(self, symbol: str, timeframe: str) -> Path:
        """
        Get path for symbol/timeframe Parquet file.
        
        Creates symbol directory if it doesn't exist.
        """
        symbol_dir = self.base_path / symbol.upper()
        symbol_dir.mkdir(exist_ok=True)
        return symbol_dir / f"{timeframe}.parquet"
    
    def _get_metadata_key(self, symbol: str, timeframe: str) -> str:
        """Generate metadata key for symbol/timeframe."""
        return f"{symbol.upper()}_{timeframe}"
    
    def has_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start: datetime, 
        end: datetime
    ) -> bool:
        """
        Check if storage has complete data for requested range.
        
        Uses metadata for fast check - does not load file.
        """
        key = self._get_metadata_key(symbol, timeframe)
        
        if key not in self.metadata:
            return False
        
        meta = self.metadata[key]
        
        try:
            cached_start = datetime.fromisoformat(meta['start'])
            cached_end = datetime.fromisoformat(meta['end'])
        except (KeyError, ValueError):
            return False
        
        # Check if cached range covers requested range
        return cached_start <= start and cached_end >= end
    
    @track_performance("storage_read", slow_threshold_seconds=5.0)
    def get_data(
        self, 
        symbol: str, 
        timeframe: str,
        start: datetime, 
        end: datetime
    ) -> pd.DataFrame:
        """
        Retrieve market data from local Parquet file.
        
        Returns empty DataFrame if no data available.
        """
        file_path = self._get_file_path(symbol, timeframe)
        
        if not file_path.exists():
            return pd.DataFrame()
        
        try:
            df = pd.read_parquet(file_path)
            
            # Ensure index is datetime
            if not isinstance(df.index, pd.DatetimeIndex):
                if 'timestamp' in df.columns:
                    df = df.set_index('timestamp')
                df.index = pd.to_datetime(df.index)
            
            # Filter to requested range
            mask = (df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end))
            return df[mask]
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return pd.DataFrame()
    
    @track_performance("storage_write", slow_threshold_seconds=5.0)
    def save_data(
        self, 
        symbol: str, 
        timeframe: str, 
        data: pd.DataFrame
    ) -> None:
        """
        Store market data to local Parquet file.
        
        Merges with existing data - no duplicates.
        """
        if data.empty:
            return
        
        file_path = self._get_file_path(symbol, timeframe)
        
        # Ensure data has proper index
        if not isinstance(data.index, pd.DatetimeIndex):
            if 'timestamp' in data.columns:
                data = data.set_index('timestamp')
            data.index = pd.to_datetime(data.index)
        
        with self._lock:
            # Merge with existing data if present
            if file_path.exists():
                try:
                    existing = pd.read_parquet(file_path)
                    
                    # Ensure existing has proper index
                    if not isinstance(existing.index, pd.DatetimeIndex):
                        if 'timestamp' in existing.columns:
                            existing = existing.set_index('timestamp')
                        existing.index = pd.to_datetime(existing.index)
                    
                    # Combine and remove duplicates
                    data = pd.concat([existing, data])
                    data = data[~data.index.duplicated(keep='last')]
                    data = data.sort_index()
                    
                except Exception as e:
                    print(f"Warning: Could not merge with existing data: {e}")
            
            # Save with compression
            data.to_parquet(file_path, compression='snappy')
            
            # Update metadata
            key = self._get_metadata_key(symbol, timeframe)
            self.metadata[key] = {
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'start': data.index.min().isoformat(),
                'end': data.index.max().isoformat(),
                'rows': len(data),
                'last_updated': datetime.now().isoformat(),
                'file_size_mb': round(file_path.stat().st_size / (1024 * 1024), 3)
            }
            self._save_metadata()
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get storage statistics and dataset information.
        """
        # Calculate total size
        total_size = 0
        for file in self.base_path.rglob("*.parquet"):
            total_size += file.stat().st_size
        
        # Count unique symbols
        symbols = set()
        for key in self.metadata.keys():
            symbol = key.split('_')[0]
            symbols.add(symbol)
        
        return {
            'storage_type': 'local',
            'base_path': str(self.base_path),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'symbols': len(symbols),
            'datasets': len(self.metadata),
            'datasets_detail': self.metadata
        }
    
    def clear_cache(self, older_than_days: int = 30) -> int:
        """
        Remove data not updated in X days.
        
        Returns number of datasets deleted.
        """
        cutoff = datetime.now().timestamp() - (older_than_days * 86400)
        deleted = 0
        
        with self._lock:
            keys_to_delete = []
            
            for key, meta in self.metadata.items():
                try:
                    last_updated = datetime.fromisoformat(meta['last_updated'])
                    if last_updated.timestamp() < cutoff:
                        # Delete file
                        symbol, timeframe = key.split('_', 1)
                        file_path = self._get_file_path(symbol, timeframe)
                        if file_path.exists():
                            file_path.unlink()
                            print(f"Deleted old cache: {key}")
                            deleted += 1
                        keys_to_delete.append(key)
                except Exception as e:
                    print(f"Error processing {key}: {e}")
            
            # Remove from metadata
            for key in keys_to_delete:
                del self.metadata[key]
            
            if keys_to_delete:
                self._save_metadata()
        
        return deleted
    
    def delete_symbol(self, symbol: str) -> int:
        """
        Delete all data for a symbol.
        
        Returns number of timeframes deleted.
        """
        symbol = symbol.upper()
        deleted = 0
        
        with self._lock:
            keys_to_delete = []
            
            for key in list(self.metadata.keys()):
                if key.startswith(f"{symbol}_"):
                    # Delete file
                    _, timeframe = key.split('_', 1)
                    file_path = self._get_file_path(symbol, timeframe)
                    if file_path.exists():
                        file_path.unlink()
                        deleted += 1
                    keys_to_delete.append(key)
            
            # Remove from metadata
            for key in keys_to_delete:
                del self.metadata[key]
            
            # Remove symbol directory if empty
            symbol_dir = self.base_path / symbol
            if symbol_dir.exists() and not any(symbol_dir.iterdir()):
                symbol_dir.rmdir()
            
            if keys_to_delete:
                self._save_metadata()
        
        return deleted
    
    def get_storage_health(self) -> Dict[str, Any]:
        """
        Check storage health and return diagnostics.
        
        Useful for monitoring and troubleshooting.
        """
        health = {
            'status': 'healthy',
            'issues': [],
            'stats': {}
        }
        
        # Check base path exists and is writable
        if not self.base_path.exists():
            health['status'] = 'error'
            health['issues'].append('Base path does not exist')
        else:
            # Try to write test file
            test_file = self.base_path / '.health_check'
            try:
                test_file.write_text('ok')
                test_file.unlink()
            except Exception as e:
                health['status'] = 'error'
                health['issues'].append(f'Cannot write to storage: {e}')
        
        # Check metadata consistency
        metadata_count = len(self.metadata)
        file_count = len(list(self.base_path.rglob("*.parquet")))
        
        if metadata_count != file_count:
            health['status'] = 'warning'
            health['issues'].append(
                f'Metadata mismatch: {metadata_count} entries, {file_count} files'
            )
        
        # Get stats
        meta = self.get_metadata()
        health['stats'] = {
            'total_size_mb': meta['total_size_mb'],
            'symbols': meta['symbols'],
            'datasets': meta['datasets']
        }
        
        return health