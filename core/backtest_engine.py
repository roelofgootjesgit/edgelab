"""
backtest_engine.py
==================

Simulate strategy execution on historical price data.
Generates QuantMetricsTrade objects compatible with existing analyzer.

Author: QuantMetrics Development Team
Version: 2.0 (Simplified - Performance Optimized)
"""

from typing import List, Optional
from datetime import datetime
import pandas as pd
import numpy as np

from core.quantmetrics_schema import QuantMetricsTrade
from core.strategy import StrategyDefinition, EntryCondition
from core.data_downloader import DataDownloader
from core.indicators import IndicatorEngine


def clean_and_standardize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize DataFrame ONCE at the start.
    This ensures all modules receive clean, consistent data.
    
    Returns DataFrame with:
    - Clean DatetimeIndex (no duplicates)
    - Standard OHLCV columns
    - No duplicate rows
    """
    # Step 1: Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    if len(df) < before:
        print(f"[CLEAN] Removed {before - len(df)} duplicate rows")
    
    # Step 2: Ensure index is DatetimeIndex (clean, no duplicates)
    if not isinstance(df.index, pd.DatetimeIndex):
        # Convert index to datetime
        if df.index.duplicated().any():
            # Remove duplicates first
            df = df[~df.index.duplicated(keep='last')]
        try:
            df.index = pd.to_datetime(df.index, errors='coerce')
            df = df[df.index.notna()]
        except Exception as e:
            print(f"[CLEAN] Warning: Could not convert index to datetime: {e}")
            # Fallback: create sequential datetime index
            df.index = pd.date_range(start='2020-01-01', periods=len(df), freq='15min')
    
    # Step 3: Remove duplicate index values
    if df.index.duplicated().any():
        dup_count = df.index.duplicated().sum()
        print(f"[CLEAN] Removing {dup_count} duplicate index values")
        df = df[~df.index.duplicated(keep='last')]
    
    # Step 4: Sort by index
    df = df.sort_index()
    
    # Step 5: Ensure timestamp column exists and is clean
    if 'timestamp' not in df.columns:
        df['timestamp'] = df.index
    else:
        # Clean timestamp column
        if df['timestamp'].duplicated().any():
            dup_count = df['timestamp'].duplicated().sum()
            print(f"[CLEAN] Removing {dup_count} duplicate timestamps")
            df = df.drop_duplicates(subset=['timestamp'], keep='last')
        # Ensure it's datetime type
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df[df['timestamp'].notna()]
    
    return df


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
    
    def __init__(self):
        self.data_downloader = DataDownloader()
        self.indicator_engine = IndicatorEngine()
        # Use DataManager for caching (if available)
        try:
            from core.data_manager import DataManager
            self.data_manager = DataManager()
        except ImportError:
            self.data_manager = None
    
    def run(self, strategy: StrategyDefinition) -> List[QuantMetricsTrade]:
        """
        Run backtest with traditional strategy definition.
        
        Args:
            strategy: StrategyDefinition object
            
        Returns:
            List of QuantMetricsTrade objects
        """
        # Download data
        data = self.data_downloader.download(
            symbol=strategy.symbol,
            timeframe=strategy.timeframe,
            start=strategy.start_date,
            end=strategy.end_date
        )
        
        if data.empty:
            return []
        
        # Calculate indicators
        for indicator in strategy.indicators:
            data = self.indicator_engine.calculate(data, indicator)
        
        # Simulate trades
        trades = []
        in_trade = False
        entry_price = None
        entry_index = None
        direction = None
        
        for i in range(len(data)):
            row = data.iloc[i]
            
            # Check entry conditions
            if not in_trade:
                for condition in strategy.entry_conditions:
                    if self._check_condition(row, condition):
                        in_trade = True
                        entry_price = row['close']
                        entry_index = i
                        direction = condition.direction
                        break
            
            # Check exit conditions
            if in_trade:
                # Simple exit: TP or SL
                if direction == 'LONG':
                    if row['high'] >= entry_price * (1 + strategy.tp_r * strategy.sl_r):
                        # TP hit
                        exit_price = entry_price * (1 + strategy.tp_r * strategy.sl_r)
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'LONG', True,
                            data.index[entry_index], data.index[i]
                        ))
                        in_trade = False
                    elif row['low'] <= entry_price * (1 - strategy.sl_r):
                        # SL hit
                        exit_price = entry_price * (1 - strategy.sl_r)
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'LONG', False,
                            data.index[entry_index], data.index[i]
                        ))
                        in_trade = False
                else:  # SHORT
                    if row['low'] <= entry_price * (1 - strategy.tp_r * strategy.sl_r):
                        # TP hit
                        exit_price = entry_price * (1 - strategy.tp_r * strategy.sl_r)
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'SHORT', True,
                            data.index[entry_index], data.index[i]
                        ))
                        in_trade = False
                    elif row['high'] >= entry_price * (1 + strategy.sl_r):
                        # SL hit
                        exit_price = entry_price * (1 + strategy.sl_r)
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'SHORT', False,
                            data.index[entry_index], data.index[i]
                        ))
                        in_trade = False
        
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
        Run backtest with modular strategy system - SIMPLIFIED VERSION.
        
        Key improvements:
        - Clean data ONCE at the start
        - No monkey-patching
        - No complex safe_to_datetime
        - Simple error handling
        - Much faster execution
        
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
        import time
        total_start = time.time()
        
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
        if self.data_manager:
            data = self.data_manager.get_data(
                symbol=symbol,
                timeframe=timeframe,
                start=start,
                end=end
            )
        else:
            # Fallback to direct download
            data = self.data_downloader.download(
                symbol=symbol,
                timeframe=timeframe,
                start=start,
                end=end
            )
        
        if data.empty:
            raise ValueError(f"No data available for {symbol}")
        
        print(f"[BACKTEST] Initial data: {len(data)} rows, {len(data.columns)} columns")
        
        # CRITICAL: Clean and standardize data ONCE at the start
        data = clean_and_standardize_data(data)
        print(f"[BACKTEST] After cleanup: {len(data)} rows")
        
        # Calculate indicators for all modules
        existing_columns = set(data.columns)
        print(f"[BACKTEST] Processing {len(modules)} modules...")
        
        for idx, module_item in enumerate(modules):
            module = module_item['module']
            config = module_item['config']
            module_id = module_item.get('module_id', 'unknown')
            
            print(f"[BACKTEST] Processing module {idx+1}/{len(modules)}: {module_id}")
            
            # Store column count before
            cols_before = set(data.columns)
            
            # Calculate indicator
            try:
                module_start = time.time()
                data = module.calculate(data, config)
                module_elapsed = time.time() - module_start
                print(f"[BACKTEST] ✓ {module_id} completed in {module_elapsed:.2f}s")
            except Exception as e:
                error_msg = str(e)
                print(f"[BACKTEST] Error in module {module_id}: {error_msg}")
                # If it's a duplicate/assemble error, clean data and retry once
                if "cannot assemble" in error_msg or "duplicate" in error_msg.lower() or "Length of values" in error_msg:
                    print(f"[BACKTEST] Cleaning data and retrying {module_id}...")
                    data = clean_and_standardize_data(data)
                    data = module.calculate(data, config)
                else:
                    raise  # Re-raise if it's a different error
            
            # Check for duplicate columns and rename if needed
            cols_after = set(data.columns)
            new_cols = cols_after - cols_before
            
            for col in new_cols:
                if col in existing_columns:
                    # Column already exists - rename with module index
                    new_col_name = f"{col}_m{idx}"
                    if new_col_name in data.columns:
                        new_col_name = f"{col}_m{idx}_{module_id}"
                    data = data.rename(columns={col: new_col_name})
                    print(f"[BACKTEST] Renamed duplicate column '{col}' to '{new_col_name}'")
                else:
                    existing_columns.add(col)
            
            # Ensure data stays clean after each module
            # Quick check: if index has duplicates, clean it
            if data.index.duplicated().any():
                print(f"[BACKTEST] Module {module_id} created duplicate index, cleaning...")
                data = data[~data.index.duplicated(keep='last')]
                data = data.sort_index()
        
        # Smart data cleanup - forward fill indicators instead of dropping rows
        indicator_cols = [col for col in data.columns 
                         if col not in ['open', 'high', 'low', 'close', 'volume', 'timestamp']]
        
        print(f"[BACKTEST] Raw data: {len(data)} rows")
        print(f"[BACKTEST] Indicators calculated: {len(indicator_cols)}")
        
        # Forward fill indicator NaN values (use last known value)
        for col in indicator_cols:
            if col in data.columns:
                data[col] = data[col].ffill()
        
        # Drop rows where price data (OHLC) is NaN
        data = data.dropna(subset=['close'])
        
        # Drop remaining rows where ALL indicators are still NaN
        if indicator_cols:
            data = data.dropna(subset=indicator_cols, how='all')
        
        print(f"[BACKTEST] Data after cleanup: {len(data)} rows")
        
        # Lower threshold - 30 rows minimum
        if len(data) < 30:
            raise ValueError(
                f"Insufficient data: only {len(data)} rows available after indicator calculation.\n"
                f"Solutions:\n"
                f"  1. Use longer backtest period (try 3mo or 6mo)\n"
                f"  2. Use shorter indicator periods (e.g., SMA 20 instead of SMA 200)\n"
                f"  3. Use higher timeframe (1h or 4h instead of 15m)"
            )
        
        # Ensure timestamp column exists
        if 'timestamp' not in data.columns:
            data['timestamp'] = data.index
        
        # Apply session filter if specified
        if session:
            if session.lower() == 'tokyo':
                data = data[data['timestamp'].dt.hour.isin(range(0, 9))]
            elif session.lower() == 'london':
                data = data[data['timestamp'].dt.hour.isin(range(7, 16))]
            elif session.lower() == 'ny':
                data = data[data['timestamp'].dt.hour.isin(range(12, 21))]
            
            print(f"[BACKTEST] After session filter ({session}): {len(data)} rows")
        
        # OPTIMIZED APPROACH: Try vectorized first, fallback to row-by-row if needed
        # Many modules already have boolean columns we can use directly
        print(f"[BACKTEST] Computing entry conditions for {len(data)} rows...")
        
        condition_series = {}
        for module_item in modules:
            module = module_item['module']
            config = module_item['config']
            module_id = module_item.get('module_id', 'unknown')
            
            print(f"[BACKTEST] Computing conditions for {module_id}...")
            try:
                # Try to infer vectorized condition from module_id and data columns
                # This works for simple modules that set boolean flags
                vectorized = False
                
                # Simple boolean column checks (kill_zones, liquidity_sweep, etc.)
                if module_id == 'kill_zones' and 'in_kill_zone' in data.columns:
                    condition_series[module_id] = data['in_kill_zone'] == True
                    vectorized = True
                elif module_id == 'liquidity_sweep':
                    if direction == 'LONG' and 'bullish_sweep' in data.columns:
                        condition_series[module_id] = data['bullish_sweep'] == True
                        vectorized = True
                    elif direction == 'SHORT' and 'bearish_sweep' in data.columns:
                        condition_series[module_id] = data['bearish_sweep'] == True
                        vectorized = True
                elif module_id == 'mitigation_blocks':
                    if direction == 'LONG':
                        condition_series[module_id] = (data['mitigation_active'] == True) & (data['mitigation_type'] == 'BULLISH')
                        vectorized = True
                    elif direction == 'SHORT':
                        condition_series[module_id] = (data['mitigation_active'] == True) & (data['mitigation_type'] == 'BEARISH')
                        vectorized = True
                elif module_id == 'displacement':
                    if direction == 'LONG':
                        condition_series[module_id] = (data['displacement_active'] == True) & (data['displacement_type'] == 'BULLISH')
                        vectorized = True
                    elif direction == 'SHORT':
                        condition_series[module_id] = (data['displacement_active'] == True) & (data['displacement_type'] == 'BEARISH')
                        vectorized = True
                elif module_id == 'market_structure_shift':
                    if direction == 'LONG':
                        condition_series[module_id] = (data['bullish_mss'] == True) | ((data['mss_active'] == True) & (data['mss_type'] == 'BULLISH'))
                        vectorized = True
                    elif direction == 'SHORT':
                        condition_series[module_id] = (data['bearish_mss'] == True) | ((data['mss_active'] == True) & (data['mss_type'] == 'BEARISH'))
                        vectorized = True
                
                if not vectorized:
                    # Fallback: row-by-row check (for complex modules like RSI with cross logic)
                    print(f"[BACKTEST] Using row-by-row check for {module_id}...")
                    results = []
                    for i in range(len(data)):
                        try:
                            result = module.check_entry_condition(data, i, config, direction)
                            results.append(bool(result))
                        except Exception as e:
                            results.append(False)
                    condition_series[module_id] = pd.Series(results, index=data.index, dtype=bool)
                
                print(f"[BACKTEST] ✓ {module_id}: {condition_series[module_id].sum()} rows meet condition")
            except Exception as e:
                print(f"[BACKTEST] Error computing conditions for {module_id}: {e}")
                condition_series[module_id] = pd.Series(False, index=data.index)
        
        # Combine all conditions (AND logic - all must be True)
        print(f"[BACKTEST] Combining conditions...")
        entry_signal = pd.Series(True, index=data.index)
        for module_id, series in condition_series.items():
            entry_signal = entry_signal & series
        
        entry_count = entry_signal.sum()
        print(f"[BACKTEST] Entry signals: {entry_count} rows meet all conditions")
        
        # Simulate trades using vectorized entry signals
        trades = []
        in_trade = False
        entry_price = None
        entry_index = None
        trade_direction = None
        
        print(f"[BACKTEST] Simulating trades on {len(data)} rows...")
        
        for i in range(len(data)):
            # Check entry signal (pre-computed)
            if not in_trade:
                if entry_signal.iloc[i]:
                    in_trade = True
                    entry_price = data.iloc[i]['close']
                    entry_index = i
                    trade_direction = direction
            
            # Check exit conditions (TP/SL)
            if in_trade:
                row = data.iloc[i]
                if trade_direction == 'LONG':
                    tp_price = entry_price * (1 + tp_r * sl_r)
                    sl_price = entry_price * (1 - sl_r)
                    
                    if row['high'] >= tp_price:
                        # TP hit
                        exit_price = tp_price
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'LONG', True,
                            data.index[entry_index], data.index[i]
                        ))
                        in_trade = False
                    elif row['low'] <= sl_price:
                        # SL hit
                        exit_price = sl_price
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'LONG', False,
                            data.index[entry_index], data.index[i]
                        ))
                        in_trade = False
                else:  # SHORT
                    tp_price = entry_price * (1 - tp_r * sl_r)
                    sl_price = entry_price * (1 + sl_r)
                    
                    if row['low'] <= tp_price:
                        # TP hit
                        exit_price = tp_price
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'SHORT', True,
                            data.index[entry_index], data.index[i]
                        ))
                        in_trade = False
                    elif row['high'] >= sl_price:
                        # SL hit
                        exit_price = sl_price
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'SHORT', False,
                            data.index[entry_index], data.index[i]
                        ))
                        in_trade = False
        
        total_elapsed = time.time() - total_start
        print(f"[BACKTEST] Total time: {total_elapsed:.2f}s, Generated {len(trades)} trades")
        
        return trades
    
    def _check_condition(self, row: pd.Series, condition: EntryCondition) -> bool:
        """Check if a condition is met for a given row."""
        value = row.get(condition.indicator, None)
        if value is None or pd.isna(value):
            return False
        
        if condition.operator == '>':
            return value > condition.value
        elif condition.operator == '<':
            return value < condition.value
        elif condition.operator == '>=':
            return value >= condition.value
        elif condition.operator == '<=':
            return value <= condition.value
        elif condition.operator == '==':
            return value == condition.value
        else:
            return False
    
    def _create_trade(
        self,
        entry_price: float,
        exit_price: float,
        direction: str,
        is_winner: bool,
        entry_time: datetime,
        exit_time: datetime
    ) -> QuantMetricsTrade:
        """Create a QuantMetricsTrade object."""
        return QuantMetricsTrade(
            symbol="",  # Will be set by analyzer
            direction=direction,
            entry_price=entry_price,
            exit_price=exit_price,
            entry_time=entry_time,
            exit_time=exit_time,
            pnl=exit_price - entry_price if direction == 'LONG' else entry_price - exit_price,
            pnl_pct=(exit_price - entry_price) / entry_price * 100 if direction == 'LONG' else (entry_price - exit_price) / entry_price * 100,
            is_winner=is_winner,
            r_multiple=(exit_price - entry_price) / (entry_price * 0.01) if direction == 'LONG' else (entry_price - exit_price) / (entry_price * 0.01)
        )
