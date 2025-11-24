"""
backtest_engine.py
==================

Simulate strategy execution on historical price data.
Generates EdgeLabTrade objects compatible with existing analyzer.

Author: EdgeLab Development Team
Version: 1.1 (Added Bollinger Bands support)
"""

from typing import List, Optional
from datetime import datetime
import pandas as pd

from core.edgelab_schema import EdgeLabTrade
from core.strategy import StrategyDefinition, EntryCondition
from core.data_downloader import DataDownloader
from core.indicators import IndicatorEngine


def detect_session(timestamp: datetime) -> str:
    """Detect trading session from timestamp hour (UTC)."""
    hour = timestamp.hour
    if 0 <= hour < 8:
        return 'Tokyo'
    elif 8 <= hour < 14:
        return 'London'
    else:
        return 'NY'


class BacktestEngine:
    """
    Simulate trading strategy on historical data.
    
    Process:
    1. Download historical data
    2. Calculate indicators
    3. Loop through candles
    4. Check entry conditions
    5. Simulate trade execution
    6. Generate EdgeLabTrade objects
    
    Output is compatible with existing EdgeLab analyzer.
    """
    
    def __init__(self):
        self.downloader = DataDownloader()
        self.indicators = IndicatorEngine()
    
    def run(self, strategy: StrategyDefinition) -> List[EdgeLabTrade]:
        """
        Run backtest for given strategy.
        
        Args:
            strategy: StrategyDefinition with entry/exit rules
            
        Returns:
            List of EdgeLabTrade objects (same format as CSV parser)
        """
        # Validate strategy
        errors = strategy.validate()
        if errors:
            raise ValueError(f"Invalid strategy: {errors}")
        
        # Download data
        data = self.downloader.download(
            symbol=strategy.symbol,
            period=strategy.period,
            interval=strategy.timeframe
        )
        
        # Calculate indicators
        data = self.indicators.calculate_all(data)
        
        # Drop rows with NaN (insufficient data for indicators)
        data = data.dropna()
        
        if len(data) < 100:
            raise ValueError(f"Insufficient data: only {len(data)} rows after indicator calculation")
        
        # Run simulation
        trades = self._simulate(data, strategy)
        
        return trades
    
    def _simulate(
        self, 
        data: pd.DataFrame, 
        strategy: StrategyDefinition
    ) -> List[EdgeLabTrade]:
        """
        Core simulation loop.
        
        Args:
            data: DataFrame with OHLCV + indicators
            strategy: Strategy definition
            
        Returns:
            List of completed trades
        """
        trades = []
        position = None  # Current open position
        
        # Convert to list for iteration
        rows = list(data.iterrows())
        
        for i, (timestamp, candle) in enumerate(rows):
            # Skip if not enough future data for exit
            if i >= len(rows) - 1:
                break
            
            # Session filter
            current_session = detect_session(timestamp)
            if strategy.session and current_session != strategy.session:
                continue
            
            # If not in position, check for entry
            if position is None:
                if self._check_entry(candle, strategy):
                    position = self._open_position(timestamp, candle, strategy)
            
            # If in position, check for exit
            else:
                exit_result = self._check_exit(candle, position)
                if exit_result:
                    trade = self._close_position(timestamp, candle, position, exit_result)
                    trades.append(trade)
                    position = None
        
        # Close any open position at end
        if position is not None:
            final_timestamp, final_candle = rows[-1]
            trade = self._close_position(final_timestamp, final_candle, position, 'timeout')
            trades.append(trade)
        
        return trades
    
    def _check_entry(self, candle: pd.Series, strategy: StrategyDefinition) -> bool:
        """Check if all entry conditions are met."""
        for condition in strategy.entry_conditions:
            if not self._evaluate_condition(candle, condition):
                return False
        return True
    
    def _evaluate_condition(self, candle: pd.Series, condition: EntryCondition) -> bool:
        """
        Evaluate a single entry condition.
        
        Supported indicators:
        - rsi: RSI(14)
        - adx: ADX(14)
        - macd: MACD line
        - sma_20: Simple Moving Average (20)
        - sma_50: Simple Moving Average (50)
        - ema_20: Exponential Moving Average (20)
        - atr: Average True Range
        - bb_upper: Bollinger Band Upper
        - bb_lower: Bollinger Band Lower
        - bb_middle: Bollinger Band Middle
        - price: Current close price
        """
        # Map indicator name to DataFrame column
        indicator_map = {
            'rsi': 'rsi',
            'adx': 'adx',
            'macd': 'macd',
            'sma_20': 'sma_20',
            'sma_50': 'sma_50',
            'ema_20': 'ema_20',
            'atr': 'atr',
            'bb_upper': 'bb_upper',
            'bb_lower': 'bb_lower',
            'bb_middle': 'bb_middle',
            'price': 'close'
        }
        
        # Get column name
        column = indicator_map.get(condition.indicator)
        if column is None:
            return False
        
        # Get value from candle
        value = candle.get(column)
        
        if value is None or pd.isna(value):
            return False
        
        # Evaluate operator
        threshold = condition.value
        
        if condition.operator == '<':
            return value < threshold
        elif condition.operator == '>':
            return value > threshold
        elif condition.operator == '<=':
            return value <= threshold
        elif condition.operator == '>=':
            return value >= threshold
        elif condition.operator == '==':
            return abs(value - threshold) < 0.0001
        
        return False
    
    def _open_position(
        self, 
        timestamp: datetime, 
        candle: pd.Series, 
        strategy: StrategyDefinition
    ) -> dict:
        """Open a new position."""
        entry_price = candle['close']
        
        # Calculate SL/TP based on risk percentage
        risk_distance = entry_price * (strategy.risk_pct / 100)
        
        if strategy.direction == 'LONG':
            sl = entry_price - risk_distance
            tp = entry_price + (risk_distance * strategy.tp_r)
        else:  # SHORT
            sl = entry_price + risk_distance
            tp = entry_price - (risk_distance * strategy.tp_r)
        
        # Add slippage (2 pips for realism)
        slippage = entry_price * 0.0001  # ~1 pip
        if strategy.direction == 'LONG':
            entry_price += slippage
        else:
            entry_price -= slippage
        
        return {
            'timestamp_open': timestamp,
            'entry_price': entry_price,
            'sl': sl,
            'tp': tp,
            'direction': strategy.direction,
            'symbol': strategy.symbol,
            'risk_distance': risk_distance
        }
    
    def _check_exit(self, candle: pd.Series, position: dict) -> Optional[str]:
        """
        Check if TP or SL hit.
        
        Returns:
            'tp', 'sl', or None
        """
        if position['direction'] == 'LONG':
            # Check TP first (optimistic for testing)
            if candle['high'] >= position['tp']:
                return 'tp'
            # Check SL
            if candle['low'] <= position['sl']:
                return 'sl'
        else:  # SHORT
            if candle['low'] <= position['tp']:
                return 'tp'
            if candle['high'] >= position['sl']:
                return 'sl'
        
        return None
    
    def _close_position(
        self, 
        timestamp: datetime, 
        candle: pd.Series,
        position: dict, 
        exit_reason: str
    ) -> EdgeLabTrade:
        """Close position and create EdgeLabTrade."""
        
        # Determine exit price
        if exit_reason == 'tp':
            exit_price = position['tp']
            result = 'WIN'
        elif exit_reason == 'sl':
            exit_price = position['sl']
            result = 'LOSS'
        else:  # timeout
            exit_price = candle['close']
            result = 'TIMEOUT'
        
        # Calculate profit
        if position['direction'] == 'LONG':
            profit_raw = exit_price - position['entry_price']
        else:
            profit_raw = position['entry_price'] - exit_price
        
        # Calculate R-multiple
        profit_r = profit_raw / position['risk_distance']
        
        # Estimate USD profit (assume $10 per pip for XAUUSD)
        profit_usd = profit_raw * 10
        
        return EdgeLabTrade(
            timestamp_open=position['timestamp_open'],
            timestamp_close=timestamp,
            symbol=position['symbol'],
            direction=position['direction'],
            entry_price=position['entry_price'],
            exit_price=exit_price,
            sl=position['sl'],
            tp=position['tp'],
            profit_usd=round(profit_usd, 2),
            profit_r=round(profit_r, 2),
            result=result
        )