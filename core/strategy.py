"""
strategy.py
===========

Strategy definition models for EdgeLab backtesting.

Author: QuantMetrics Development Team
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import List, Literal, Optional
from datetime import datetime


@dataclass
class EntryCondition:
    """Single entry condition for a strategy."""
    
    indicator: str  # 'rsi', 'sma', 'macd', 'price'
    operator: Literal['<', '>', '<=', '>=', '==', 'crosses_above', 'crosses_below']
    value: float  # Threshold value or indicator period
    
    def __str__(self):
        return f"{self.indicator} {self.operator} {self.value}"


@dataclass
class StrategyDefinition:
    """
    Complete strategy definition for backtesting.
    
    Example:
        strategy = StrategyDefinition(
            name="RSI Oversold Long",
            symbol="XAUUSD",
            direction="LONG",
            entry_conditions=[
                EntryCondition("rsi", "<", 30)
            ],
            tp_r=1.5,
            sl_r=1.0,
            session="NY"
        )
    """
    
    # Basic settings
    name: str
    symbol: str
    timeframe: str = "15m"
    direction: Literal['LONG', 'SHORT'] = "LONG"
    
    # Entry conditions (all must be true)
    entry_conditions: List[EntryCondition] = field(default_factory=list)
    
    # Exit rules (R-multiples)
    tp_r: float = 1.5  # Take profit in R
    sl_r: float = 1.0  # Stop loss in R (risk)
    
    # Optional filters
    session: Optional[Literal['Tokyo', 'London', 'NY']] = None
    
    # Test period
    period: str = "6mo"  # Data period to test
    
    # Risk settings
    risk_pct: float = 0.5  # Risk per trade as % of price (for SL calculation)
    
    def validate(self) -> List[str]:
        """
        Validate strategy definition.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not self.name:
            errors.append("Strategy name is required")
        
        if not self.symbol:
            errors.append("Symbol is required")
        
        if self.tp_r <= 0:
            errors.append("Take profit must be positive")
        
        if self.sl_r <= 0:
            errors.append("Stop loss must be positive")
        
        if not self.entry_conditions:
            errors.append("At least one entry condition is required")
        
        if self.risk_pct <= 0 or self.risk_pct > 5:
            errors.append("Risk percentage must be between 0 and 5")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if strategy is valid."""
        return len(self.validate()) == 0
    
    def __str__(self):
        conditions = ", ".join(str(c) for c in self.entry_conditions)
        return f"{self.name}: {self.direction} {self.symbol} when {conditions}"