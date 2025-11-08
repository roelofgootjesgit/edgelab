"""
csv_parser.py
=============

CSV parsing module for EdgeLab.

Handles multiple input formats and converts to universal EdgeLab schema.
Validates data quality and generates confidence scores.

Usage:
    parser = CSVParser()
    trades = parser.parse("trades.csv")
    
Author: EdgeLab Development Team
Version: 1.0
"""

import pandas as pd
from typing import List
from pathlib import Path
from core.edgelab_schema import EdgeLabTrade, detect_session, calculate_rr


class CSVParser:
    """
    Intelligent CSV parser for trading data.
    
    Supports multiple formats:
    - EdgeLab native (11 columns)
    - MT4/MT5 exports
    - TradingView exports
    - Generic trading journals
    
    Converts all formats to EdgeLab standard (EdgeLabTrade objects).
    """
    
    def __init__(self):
        """Initialize CSV parser."""
        self.supported_formats = ['edgelab', 'mt4', 'tradingview', 'generic']
    
    def detect_format(self, file_path: str) -> str:
        """
        Detect CSV format by analyzing column headers.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Format type: 'edgelab' | 'mt4' | 'tradingview' | 'generic'
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If CSV is empty or unreadable
        """
        # Check file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        # Read header row
        try:
            df = pd.read_csv(file_path, nrows=0)
            columns = [col.lower().strip() for col in df.columns]
        except Exception as e:
            raise ValueError(f"Cannot read CSV file: {e}")
        
        # Check for EdgeLab native format (11 exact columns)
        edgelab_columns = [
            'timestamp_open', 'timestamp_close', 'symbol', 'direction',
            'entry_price', 'exit_price', 'sl', 'tp',
            'profit_usd', 'profit_r', 'result'
        ]
        
        if all(col in columns for col in edgelab_columns):
            return 'edgelab'
        
        # Check for MT4 format (will implement later)
        # Check for TradingView format (will implement later)
        
        # Default to generic
        return 'generic'
    
    def parse(self, file_path: str) -> List[EdgeLabTrade]:
        """
        Main parsing function - detects format and converts to EdgeLab standard.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of EdgeLabTrade objects
            
        Raises:
            ValueError: If format not supported or data invalid
            FileNotFoundError: If file doesn't exist
        """
        # Detect format
        format_type = self.detect_format(file_path)
        
        # Route to appropriate parser
        if format_type == 'edgelab':
            return self._parse_edgelab(file_path)
        elif format_type == 'mt4':
            return self._parse_mt4(file_path)
        elif format_type == 'tradingview':
            return self._parse_tradingview(file_path)
        else:
            return self._parse_generic(file_path)
    
    def _parse_edgelab(self, file_path: str) -> List[EdgeLabTrade]:
        """
        Parse EdgeLab native format (11 columns).
        
        Expected columns:
        - timestamp_open, timestamp_close, symbol, direction
        - entry_price, exit_price, sl, tp
        - profit_usd, profit_r, result
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of EdgeLabTrade objects
        """
        # Read CSV
        df = pd.read_csv(file_path)
        
        # Convert to EdgeLabTrade objects
        trades = []
        for _, row in df.iterrows():
            # Parse timestamps
            timestamp_open = pd.to_datetime(row['timestamp_open'])
            timestamp_close = pd.to_datetime(row['timestamp_close'])
            
            # Calculate RR
            rr = calculate_rr(
                entry=float(row['entry_price']),
                exit=float(row['exit_price']),
                sl=float(row['sl'])
            )
            
            # Detect session
            session = detect_session(timestamp_open)
            
            trade = EdgeLabTrade(
                timestamp_open=timestamp_open,
                timestamp_close=timestamp_close,
                symbol=row['symbol'],
                direction=row['direction'],
                entry_price=float(row['entry_price']),
                exit_price=float(row['exit_price']),
                sl=float(row['sl']),
                tp=float(row['tp']),
                profit_usd=float(row['profit_usd']),
                profit_r=float(row['profit_r']),
                result=row['result'],
                rr=rr,
                session=session,
                source='csv_upload',
                confidence=100  # Native format = full confidence
            )
            trades.append(trade)
        
        return trades
    
    def _parse_mt4(self, file_path: str) -> List[EdgeLabTrade]:
        """Parse MT4 export format (to be implemented)."""
        raise NotImplementedError("MT4 format parser coming in next step")
    
    def _parse_tradingview(self, file_path: str) -> List[EdgeLabTrade]:
        """Parse TradingView format (to be implemented)."""
        raise NotImplementedError("TradingView format parser coming in next step")
    
    def _parse_generic(self, file_path: str) -> List[EdgeLabTrade]:
        """Parse generic format with flexible column mapping (to be implemented)."""
        raise NotImplementedError("Generic format parser coming in next step")