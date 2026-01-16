"""
EdgeLab Data Models
===================
Modern data structures for trading analysis platform.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


@dataclass
class QuantMetricsTrade:
    """Single trade record - universal format."""
    
    timestamp_open: datetime
    timestamp_close: datetime
    symbol: str
    direction: Literal['LONG', 'SHORT']
    entry_price: float
    exit_price: float
    sl: float
    tp: float
    profit_usd: float
    profit_r: float
    result: Literal['WIN', 'LOSS', 'TIMEOUT']


@dataclass
class AnalysisResult:
    """Complete analysis output with all insights."""
    
    # Basic metrics (REQUIRED - no defaults)
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    profit_factor: float
    expectancy: float
    total_profit_r: float
    esi: float
    pvs: float
    sharpe_ratio: float
    max_drawdown: float
    
    # Pattern insights (OPTIONAL - with defaults)
    timing: Optional[dict] = None
    directional: Optional[dict] = None
    execution: Optional[dict] = None
    losses_analysis: Optional[dict] = None
    insights: Optional[dict] = None


# Helper functions

def detect_session(timestamp) -> str:
    """
    Detect trading session based on UTC hour.
    
    Sessions:
    - Tokyo: 00:00-08:00 UTC
    - London: 08:00-16:00 UTC
    - NY: 14:00-22:00 UTC (overlaps with London)
    
    Args:
        timestamp: Trade timestamp (must be UTC). Can be datetime, pandas Timestamp, or integer (Unix timestamp)
        
    Returns:
        Session name: 'Tokyo', 'London', or 'NY'
    """
    import pandas as pd
    
    # Handle different timestamp types
    if hasattr(timestamp, 'hour'):
        # datetime or pandas Timestamp
        hour = timestamp.hour
    elif isinstance(timestamp, (int, float)):
        # Unix timestamp - convert to datetime
        try:
            ts = pd.Timestamp(timestamp, unit='s')
            hour = ts.hour
        except (ValueError, TypeError):
            # Try as nanoseconds (pandas default)
            try:
                ts = pd.Timestamp(timestamp)
                hour = ts.hour
            except Exception:
                print(f"[WARNING] Could not parse timestamp: {timestamp}, type: {type(timestamp)}")
                return 'NY'  # Default fallback
    else:
        # Try to convert to pandas Timestamp
        try:
            ts = pd.Timestamp(timestamp)
            hour = ts.hour
        except Exception as e:
            print(f"[WARNING] Could not parse timestamp: {timestamp}, type: {type(timestamp)}, error: {e}")
            return 'NY'  # Default fallback
    
    if 0 <= hour < 8:
        return 'Tokyo'
    elif 8 <= hour < 14:
        return 'London'
    else:  # 14-23
        return 'NY'


def calculate_rr(
    entry: float,
    exit: float,
    sl: float,
    direction: str
) -> float:
    """
    Calculate R-multiple (profit in terms of risk).
    
    R = 1 means profit equals initial risk
    R = 2 means profit is 2x initial risk
    R = -1 means loss equals initial risk
    
    Args:
        entry: Entry price
        exit: Exit price
        sl: Stop loss price
        direction: 'LONG' or 'SHORT'
        
    Returns:
        R-multiple (can be negative)
    """
    if direction == 'LONG':
        risk = abs(entry - sl)
        profit = exit - entry
    else:  # SHORT
        risk = abs(sl - entry)
        profit = entry - exit
    
    if risk == 0:
        return 0.0
    
    return profit / risk