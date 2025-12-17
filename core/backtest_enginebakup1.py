"""
backtest_engine.py
==================

Simulate strategy execution on historical price data.
Generates QuantMetricsTrade objects compatible with existing analyzer.

Author: QuantMetrics Development Team
Version: 1.1 (Added Bollinger Bands support)
"""

from typing import List, Optional
from datetime import datetime
import pandas as pd

from core.quantmetrics_schema import QuantMetricsTrade
from core.strategy import StrategyDefinition, EntryCondition
from core.data_downloader import DataDownloader
from core.indicators import IndicatorEngine


def detect_session(timestamp) -> str:
    """
    Detect trading session from timestamp hour (UTC).
    Handles pandas Timestamp, numpy datetime64, and Python datetime.
    """
    # Handle different timestamp types
    if hasattr(timestamp, 'hour'):
        hour = timestamp.hour
    else:
        # Convert to pandas Timestamp if needed
        try:
            ts = pd.Timestamp(timestamp)
            hour = ts.hour
        except Exception as e:
            print(f"[WARNING] Could not parse timestamp: {timestamp}, type: {type(timestamp)}")
            return 'NY'  # Default fallback
    
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
    6. Generate QuantMetricsTrade objects
    
    Output is compatible with existing EdgeLab analyzer.
    """
    
    def __init__(self, data_manager=None):
        """
        Initialize backtest engine.
        
        Args:
            data_manager: DataManager instance for cached data access.
                          If None, creates new DataManager (with caching).
        """
        if data_manager is None:
            from core.data_manager import DataManager
            data_manager = DataManager()
        
        self.data_manager = data_manager
        self.indicators = IndicatorEngine()
    
    def run(self, strategy: StrategyDefinition) -> List[QuantMetricsTrade]:
        """
        Run backtest for given strategy.
        
        Args:
            strategy: StrategyDefinition with entry/exit rules
            
        Returns:
            List of QuantMetricsTrade objects (same format as CSV parser)
        """
        # Validate strategy
        errors = strategy.validate()
        if errors:
            raise ValueError(f"Invalid strategy: {errors}")
        
        # Convert period to start/end dates
        from datetime import datetime, timedelta
        
        period_days = {
            '5d': 5, '7d': 7, '1mo': 30, '2mo': 60,
            '3mo': 90, '6mo': 180, '1y': 365, '2y': 730
        }
        days = period_days.get(strategy.period, 60)
        end = datetime.now()
        start = end - timedelta(days=days)
        
        # Get data via DataManager (with caching)
        data = self.data_manager.get_data(
            symbol=strategy.symbol,
            timeframe=strategy.timeframe,
            start=start,
            end=end
        )
        
        if data.empty:
            raise ValueError(f"No data available for {strategy.symbol}")
        
        # Calculate indicators
        data = self.indicators.calculate_all(data)
        
        # Drop rows with NaN (insufficient data for indicators)
        data = data.dropna()
        
        if len(data) < 100:
            raise ValueError(f"Insufficient data: only {len(data)} rows after indicator calculation")
        
        # Run simulation
        trades = self._simulate(data, strategy)
        
        return trades
    
    def run_modular(
        self,
        symbol: str,
        timeframe: str,
        direction: str,
        period: str,
        session: Optional[str],
        tp_r: float,
        sl_r: float,
        modules: list
    ) -> List[QuantMetricsTrade]:
        """
        Run backtest with modular strategy system.
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD')
            timeframe: Timeframe (e.g., '15m')
            direction: 'LONG' or 'SHORT'
            period: Backtest period (e.g., '2mo')
            session: Optional session filter ('Tokyo', 'London', 'NY', or None)
            tp_r: Take profit in R-multiples
            sl_r: Stop loss in R-multiples
            modules: List of instantiated module objects
            
        Returns:
            List of QuantMetricsTrade objects
        """
        # Convert period to start/end dates
        from datetime import datetime, timedelta
        
        period_days = {
            '5d': 5, '7d': 7, '1mo': 30, '2mo': 60,
            '3mo': 90, '6mo': 180, '1y': 365, '2y': 730
        }
        days = period_days.get(period, 60)
        end = datetime.now()
        start = end - timedelta(days=days)
        
        # Get data via DataManager (with caching)
        data = self.data_manager.get_data(
            symbol=symbol,
            timeframe=timeframe,
            start=start,
            end=end
        )
        
        if data.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Calculate indicators for all modules
        for module_item in modules:
            module = module_item['module']
            config = module_item['config']
            data = module.calculate(data, config)
        
        # Smart data cleanup - forward fill indicators instead of dropping rows
        indicator_cols = [col for col in data.columns 
                         if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        print(f"[BACKTEST] Raw data: {len(data)} rows")
        print(f"[BACKTEST] Indicators calculated: {len(indicator_cols)}")
        
        # Forward fill indicator NaN values (use last known value)
        # This is standard practice in backtesting - indicators need warmup period
        for col in indicator_cols:
            if col in data.columns:
                data[col] = data[col].ffill()  # New pandas syntax (replaces fillna(method='ffill'))
        
        # Drop rows where price data (OHLC) is NaN - these are unusable
        data = data.dropna(subset=['close'])
        
        # Drop remaining rows where ALL indicators are still NaN 
        # (typically first N rows where no indicator could calculate yet)
        if indicator_cols:
            data = data.dropna(subset=indicator_cols, how='all')
        
        print(f"[BACKTEST] Data after cleanup: {len(data)} rows")
        
        # Lower threshold - 30 rows minimum for statistical significance
        if len(data) < 30:
            raise ValueError(
                f"Insufficient data: only {len(data)} rows available after indicator calculation.\n"
                f"Solutions:\n"
                f"  1. Use longer backtest period (try 3mo or 6mo)\n"
                f"  2. Use shorter indicator periods (e.g., SMA 20 instead of SMA 200)\n"
                f"  3. Use higher timeframe (1h or 4h instead of 15m)"
            )
        
        # Save timestamp index as column before reset
        data['timestamp'] = pd.to_datetime(data.index)
        
        # Reset index to integer (0, 1, 2, ...) for module compatibility
        data = data.reset_index(drop=True)
        
        # Run simulation with modules
        trades = self._simulate_modular(data, direction, tp_r, sl_r, session, modules, symbol)
        
        return trades
    
    def _simulate_modular(
        self,
        data: pd.DataFrame,
        direction: str,
        tp_r: float,
        sl_r: float,
        session: Optional[str],
        modules: list,
        symbol: str
    ) -> List[QuantMetricsTrade]:
        """
        Core simulation loop for modular strategy.
        
        Args:
            data: DataFrame with OHLCV + module indicators
            direction: 'LONG' or 'SHORT'
            tp_r: Take profit R-multiple
            sl_r: Stop loss R-multiple
            session: Optional session filter
            modules: List of instantiated modules
            symbol: Trading symbol
            
        Returns:
            List of completed trades
        """
        trades = []
        position = None
        
        # Data now has integer index with timestamp column
        for i in range(len(data)):
            # Skip if not enough future data for exit
            if i >= len(data) - 1:
                break
            
            candle = data.iloc[i]
            timestamp = candle['timestamp']
            
            # Session filter
            current_session = detect_session(timestamp)
            if session and current_session != session:
                continue
            
            # If not in position, check for entry
            if position is None:
                # Check all modules - ALL must signal entry
                should_enter = True
                for module_item in modules:
                    module = module_item['module']
                    config = module_item['config']
                    # Pass strategy direction to module
                    if not module.check_entry_condition(data, i, config, direction):
                        should_enter = False
                        break
                
                if should_enter:
                    position = self._open_position_simple(timestamp, candle, direction, tp_r, sl_r, symbol)
            
            # If in position, check for exit
            else:
                exit_result = self._check_exit(candle, position)
                if exit_result:
                    trade = self._close_position(timestamp, candle, position, exit_result)
                    trades.append(trade)
                    position = None
        
        # Close any open position at end
        if position is not None:
            final_candle = data.iloc[-1]
            final_timestamp = final_candle['timestamp']
            trade = self._close_position(final_timestamp, final_candle, position, 'timeout')
            trades.append(trade)
        
        return trades
    
    def _open_position_simple(
        self,
        timestamp: datetime,
        candle: pd.Series,
        direction: str,
        tp_r: float,
        sl_r: float,
        symbol: str
    ) -> dict:
        """Open a new position (simplified for modular system)."""
        entry_price = candle['close']
        
        # Calculate SL/TP based on fixed risk percentage (1%)
        risk_distance = entry_price * 0.01
        
        if direction == 'LONG':
            sl = entry_price - risk_distance
            tp = entry_price + (risk_distance * tp_r)
        else:  # SHORT
            sl = entry_price + risk_distance
            tp = entry_price - (risk_distance * tp_r)
        
        # Add slippage
        slippage = entry_price * 0.0001
        if direction == 'LONG':
            entry_price += slippage
        else:
            entry_price -= slippage
        
        return {
            'timestamp_open': timestamp,
            'entry_price': entry_price,
            'sl': sl,
            'tp': tp,
            'direction': direction,
            'symbol': symbol,
            'risk_distance': risk_distance
        }
    
    def _simulate(
        self, 
        data: pd.DataFrame, 
        strategy: StrategyDefinition
    ) -> List[QuantMetricsTrade]:
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
    ) -> QuantMetricsTrade:
        """Close position and create QuantMetricsTrade."""
        
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
        
        return QuantMetricsTrade(
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