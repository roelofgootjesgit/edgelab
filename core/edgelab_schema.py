"""
edgelab_schema.py
=================

Core data structures for EdgeLab platform.

Defines the universal trade format and analysis result structure.
All modules use these schemas for consistency.

Author: EdgeLab Development Team
Version: 1.0
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class EdgeLabTrade:
    """
    Universal trade format for EdgeLab.
    
    All input formats (MT4, TradingView, CSV) convert to this structure.
    """
    timestamp_open: datetime
    timestamp_close: datetime
    symbol: str
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    exit_price: float
    sl: float
    tp: float
    profit_usd: float
    profit_r: float
    result: str  # 'WIN', 'LOSS', 'TIMEOUT'
    rr: float  # Risk:Reward ratio
    session: str  # 'Tokyo', 'London', 'NY'
    source: str  # 'csv_upload', 'mt4', 'tradingview'
    confidence: int  # 0-100 data quality score


@dataclass
class AnalysisResult:
    """
    Complete analysis output
    Contains all metrics calculated by analyzer
    """
    
    # Basic Statistics
    total_trades: int
    wins: int
    losses: int
    winrate: float  # Percentage
    profit_factor: float
    expectancy: float  # R-multiple per trade
    
    # Profit Metrics
    total_profit_r: float  # Total profit in R-multiples
    avg_win_r: float
    avg_loss_r: float
    
    # Risk Metrics
    max_drawdown_pct: float
    
    # Advanced Metrics (Pro/Elite tier)
    esi: float  # Edge Stability Index
    pvs: float  # Prop Verification Score
    sharpe_ratio: float
    
    # Pattern Analysis (Pro/Elite tier)
    best_session: str  # Tokyo/London/NY
    best_hour: str  # "14:00 UTC"
    long_winrate: float
    short_winrate: float
    
    # Insights
    recommendation: str  # Natural language recommendation


def detect_session(timestamp: datetime) -> str:
    """
    Detect trading session based on UTC time.
    
    Sessions:
    - Tokyo: 00:00-09:00 UTC
    - London: 08:00-17:00 UTC  
    - NY: 13:00-22:00 UTC
    
    Args:
        timestamp: Trade timestamp (UTC)
        
    Returns:
        Session name: 'Tokyo' | 'London' | 'NY'
    """
    hour = timestamp.hour
    
    if 0 <= hour < 8:
        return 'Tokyo'
    elif 8 <= hour < 13:
        return 'London'
    else:
        return 'NY'


def calculate_rr(entry: float, exit: float, sl: float) -> float:
    """
    Calculate Risk:Reward ratio.
    
    Formula: (Profit in pips) / (Risk in pips)
    
    Args:
        entry: Entry price
        exit: Exit price
        sl: Stop loss price
        
    Returns:
        R:R ratio (e.g., 2.5 = 2.5R)
    """
    risk = abs(entry - sl)
    reward = abs(exit - entry)
    
    if risk == 0:
        return 0.0
    
    return reward / risk