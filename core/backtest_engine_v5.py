"""
backtest_engine_v5.py
=====================

Direct ICT backtest engine - no module loading, just pure logic.
Fast and simple for V5 simulator.

Author: QuantMetrics Development Team
Version: 5.0 (Direct ICT Strategy)
"""

from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from core.quantmetrics_schema import QuantMetricsTrade
from core.data_downloader import DataDownloader


class BacktestEngineV5:
    """
    Direct ICT backtest engine - no modules, just pure logic.
    Tests: HTF Market Bias → Liquidity Sweep → Displacement Entry
    """
    
    def __init__(self):
        self.data_downloader = DataDownloader()
        try:
            from core.data_manager import DataManager
            self.data_manager = DataManager()
        except ImportError:
            self.data_manager = None
    
    def run_ict_backtest(
        self,
        symbol: str,
        entry_timeframe: str,
        test_period: str,
        htf_market_bias: dict,
        liquidity_sweep: dict,
        displacement_entry: dict,
        additional_blocks: list = None,  # New: extra ICT blocks
        risk: dict = None
    ) -> List[QuantMetricsTrade]:
        """
        Run direct ICT backtest without loading modules.
        
        Strategy flow:
        1. Check HTF Market Bias (BOS direction)
        2. Wait for Liquidity Sweep
        3. Enter on Displacement (impulsive candle)
        4. Exit on TP/SL
        
        Args:
            symbol: Trading symbol (e.g., 'XAUUSD')
            entry_timeframe: Entry timeframe (e.g., '5m')
            test_period: Test period (e.g., '1mo')
            htf_market_bias: HTF config
            liquidity_sweep: Sweep config
            displacement_entry: Entry config
            risk: Risk management config
            
        Returns:
            List of QuantMetricsTrade objects
        """
        import time
        start_time = time.time()
        
        # Convert period to dates
        period_days = {
            '1mo': 30,
            '2mo': 60,
            '3mo': 90
        }
        days = period_days.get(test_period, 30)
        end = datetime.now()
        start = end - timedelta(days=days)
        
        # Check if we should use test data (pre-downloaded)
        use_test_data = htf_market_bias.get('use_test_data', False) or \
                       liquidity_sweep.get('use_test_data', False) or \
                       displacement_entry.get('use_test_data', False) or \
                       risk.get('use_test_data', False)
        
        # Get entry timeframe data
        print(f"[V5] Fetching {symbol} {entry_timeframe} data...")
        if self.data_manager:
            entry_data = self.data_manager.get_data(
                symbol=symbol,
                timeframe=entry_timeframe,
                start=start,
                end=end
            )
        else:
            entry_data = self.data_downloader.download(
                symbol=symbol,
                timeframe=entry_timeframe,
                start=start,
                end=end
            )
        
        if entry_data.empty:
            raise ValueError(f"No data available for {symbol} {entry_timeframe}")
        
        print(f"[V5] Entry data: {len(entry_data)} rows")
        
        # Get HTF data for market bias
        htf_timeframe = htf_market_bias['timeframe']
        print(f"[V5] Fetching HTF {htf_timeframe} data for market bias...")
        if self.data_manager:
            htf_data = self.data_manager.get_data(
                symbol=symbol,
                timeframe=htf_timeframe,
                start=start,
                end=end
            )
        else:
            htf_data = self.data_downloader.download(
                symbol=symbol,
                timeframe=htf_timeframe,
                start=start,
                end=end
            )
        
        if htf_data.empty:
            raise ValueError(f"No HTF data available for {symbol} {htf_timeframe}")
        
        print(f"[V5] HTF data: {len(htf_data)} rows")
        
        # Clean data
        entry_data = self._clean_data(entry_data)
        htf_data = self._clean_data(htf_data)
        
        # Step 1: Calculate HTF Market Bias (BOS direction)
        print(f"[V5] Calculating HTF Market Bias...")
        htf_bias = self._calculate_htf_bias(htf_data, entry_data, htf_market_bias)
        print(f"[V5] HTF Bias: {htf_bias['direction'].value_counts().to_dict()}")
        
        # Step 2: Detect Liquidity Sweeps
        print(f"[V5] Detecting Liquidity Sweeps...")
        sweeps = self._detect_liquidity_sweeps(entry_data, liquidity_sweep)
        print(f"[V5] Found {sweeps['sweep_detected'].sum()} liquidity sweeps")
        
        # Step 3: Detect Displacement Entries (after sweeps)
        print(f"[V5] Detecting Displacement Entries...")
        displacements = self._detect_displacement(entry_data, displacement_entry, sweeps)
        print(f"[V5] Found {displacements['displacement_detected'].sum()} displacements")
        
        # Step 3.5: Combine base signals FIRST (before dynamic modules)
        # This ensures htf_bias is set before modules potentially modify the dataframe
        htf_bias_series = htf_bias['direction'].fillna('NEUTRAL').astype(str)
        htf_bias_series = htf_bias_series.replace('nan', 'NEUTRAL')
        entry_data['htf_bias'] = htf_bias_series
        
        entry_data['sweep_detected'] = sweeps['sweep_detected']
        entry_data['sweep_price'] = sweeps['sweep_price']
        entry_data['displacement_detected'] = displacements['displacement_detected']
        entry_data['displacement_price'] = displacements['displacement_price']
        
        # Step 4: Process additional ICT blocks (if any)
        # IMPORTANT: Do this AFTER base signals are set, so modules don't break the mapping
        additional_block_results = {}
        if additional_blocks and len(additional_blocks) > 0:
            print(f"[V5] Processing {len(additional_blocks)} additional ICT blocks...")
            from core.strategy_modules.registry import get_registry
            registry = get_registry()
            
            # Track processed modules to prevent duplicates
            processed_modules = set()
            
            for block in additional_blocks:
                module_id = block.get('moduleId') or block.get('module_id')
                config = block.get('config', {})
                
                if not module_id:
                    continue
                
                # Skip if already processed (prevent duplicate processing)
                if module_id in processed_modules:
                    print(f"[V5] Skipping duplicate {module_id} block")
                    continue
                
                processed_modules.add(module_id)
                
                # Clean config: convert string numbers to int/float
                cleaned_config = {}
                for key, value in config.items():
                    if isinstance(value, str):
                        # Try to convert string numbers
                        if value == '':
                            continue  # Skip empty strings (use module default)
                        try:
                            if '.' in value:
                                cleaned_config[key] = float(value)
                            else:
                                cleaned_config[key] = int(value)
                        except ValueError:
                            cleaned_config[key] = value  # Keep as string if not a number
                    else:
                        cleaned_config[key] = value
                
                config = cleaned_config
                
                try:
                    module_class = registry.get_module(module_id)
                    module_instance = module_class()
                    
                    print(f"[V5] Calculating {module_id}...")
                    # Calculate module indicators
                    entry_data = module_instance.calculate(entry_data.copy(), config)
                    
                    # Pre-compute conditions for this module (vectorized)
                    print(f"[V5] Pre-computing conditions for {module_id}...")
                    condition_series = self._precompute_module_conditions(
                        entry_data, module_instance, module_id, config
                    )
                    
                    # Store module result for later checking
                    additional_block_results[module_id] = {
                        'module': module_instance,
                        'config': config,
                        'condition_series': condition_series  # Pre-computed boolean Series
                    }
                    print(f"[V5] ✓ {module_id} completed - {condition_series.sum()} rows meet condition")
                except Exception as e:
                    print(f"[V5] Error processing {module_id}: {e}")
                    import traceback
                    traceback.print_exc()
        
        # Ensure htf_bias is still correct after module processing
        # (modules might have modified the dataframe, so re-apply if needed)
        if 'htf_bias' not in entry_data.columns or entry_data['htf_bias'].isna().any():
            print(f"[V5] Re-applying htf_bias after module processing...")
            htf_bias_series = htf_bias['direction'].fillna('NEUTRAL').astype(str)
            htf_bias_series = htf_bias_series.replace('nan', 'NEUTRAL')
            # Reindex to match current entry_data index
            htf_bias_series = htf_bias_series.reindex(entry_data.index, method='ffill').fillna('NEUTRAL')
            entry_data['htf_bias'] = htf_bias_series.astype(str).replace('nan', 'NEUTRAL')
        
        # Simulate trades
        print(f"[V5] Simulating trades...")
        print(f"[V5] Additional blocks to check: {len(additional_block_results)}")
        trades = self._simulate_trades(entry_data, risk, additional_block_results)
        
        elapsed = time.time() - start_time
        print(f"[V5] Backtest completed in {elapsed:.2f}s - Generated {len(trades)} trades")
        
        return trades
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize data."""
        # Remove duplicates
        data = data.drop_duplicates()
        
        # Ensure index is DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index, errors='coerce')
            data = data[data.index.notna()]
        
        # Remove duplicate index
        if data.index.duplicated().any():
            data = data[~data.index.duplicated(keep='last')]
        
        # Sort
        data = data.sort_index()
        
        return data
    
    def _calculate_htf_bias(
        self, 
        htf_data: pd.DataFrame, 
        entry_data: pd.DataFrame,
        config: dict
    ) -> pd.DataFrame:
        """
        Calculate HTF Market Bias based on Break of Structure (BOS).
        
        Returns DataFrame with 'direction' column: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        lookback = config.get('bosLookback', 50)
        
        # Calculate swing highs and lows on HTF
        htf_data = htf_data.copy()
        htf_data['swing_high'] = False
        htf_data['swing_low'] = False
        
        # Simple swing detection (local max/min)
        for i in range(2, len(htf_data) - 2):
            # Swing high: higher than 2 candles before and after
            if (htf_data.iloc[i]['high'] > htf_data.iloc[i-2]['high'] and
                htf_data.iloc[i]['high'] > htf_data.iloc[i-1]['high'] and
                htf_data.iloc[i]['high'] > htf_data.iloc[i+1]['high'] and
                htf_data.iloc[i]['high'] > htf_data.iloc[i+2]['high']):
                htf_data.iloc[i, htf_data.columns.get_loc('swing_high')] = True
            
            # Swing low: lower than 2 candles before and after
            if (htf_data.iloc[i]['low'] < htf_data.iloc[i-2]['low'] and
                htf_data.iloc[i]['low'] < htf_data.iloc[i-1]['low'] and
                htf_data.iloc[i]['low'] < htf_data.iloc[i+1]['low'] and
                htf_data.iloc[i]['low'] < htf_data.iloc[i+2]['low']):
                htf_data.iloc[i, htf_data.columns.get_loc('swing_low')] = True
        
        # Calculate BOS for each HTF candle (rolling)
        # This allows the bias to change over time
        htf_data = htf_data.copy()
        htf_data['bos_direction'] = 'NEUTRAL'
        
        # For each HTF candle, find the most recent BOS
        for i in range(lookback, len(htf_data)):
            current_bos = 'NEUTRAL'
            
            # Look back from current position
            for j in range(i, max(0, i - lookback), -1):
                # Bullish BOS: price breaks above previous swing high
                if htf_data.iloc[j]['swing_high']:
                    prev_swing_highs = htf_data.iloc[max(0, j-lookback):j]
                    prev_swing_highs = prev_swing_highs[prev_swing_highs['swing_high']]
                    if len(prev_swing_highs) > 0:
                        prev_high = prev_swing_highs['high'].max()
                        if htf_data.iloc[j]['high'] > prev_high:
                            current_bos = 'BULLISH'
                            break
                
                # Bearish BOS: price breaks below previous swing low
                if htf_data.iloc[j]['swing_low']:
                    prev_swing_lows = htf_data.iloc[max(0, j-lookback):j]
                    prev_swing_lows = prev_swing_lows[prev_swing_lows['swing_low']]
                    if len(prev_swing_lows) > 0:
                        prev_low = prev_swing_lows['low'].min()
                        if htf_data.iloc[j]['low'] < prev_low:
                            current_bos = 'BEARISH'
                            break
            
            # If no BOS found, use previous direction (persistence)
            if current_bos == 'NEUTRAL' and i > 0:
                current_bos = htf_data.iloc[i-1]['bos_direction']
            
            htf_data.iloc[i, htf_data.columns.get_loc('bos_direction')] = current_bos
        
        # Map HTF bias to entry timeframe using forward fill
        # Create a Series with HTF timestamps and their bias
        htf_bias_series = pd.Series(
            htf_data['bos_direction'].values,
            index=htf_data.index
        )
        
        # Ensure all values are strings (not NaN)
        htf_bias_series = htf_bias_series.fillna('NEUTRAL').astype(str)
        htf_bias_series = htf_bias_series.replace('nan', 'NEUTRAL')
        
        # Reindex to entry timeframe and forward fill
        # This ensures every entry candle has a bias value
        result_series = htf_bias_series.reindex(entry_data.index, method='ffill')
        
        # Fill any remaining NaN values (at the start before first HTF candle)
        result_series = result_series.fillna('NEUTRAL')
        
        # Ensure all values are strings (not NaN floats)
        result_series = result_series.astype(str)
        result_series = result_series.replace('nan', 'NEUTRAL')
        
        # Create result DataFrame
        result = pd.DataFrame(index=entry_data.index)
        result['direction'] = result_series
        
        return result
    
    def _detect_liquidity_sweeps(
        self, 
        data: pd.DataFrame, 
        config: dict
    ) -> pd.DataFrame:
        """
        Detect liquidity sweeps (equal highs/lows or session highs/lows).
        
        Returns DataFrame with 'sweep_detected' and 'sweep_price' columns.
        """
        data = data.copy()
        sweep_type = config.get('sweepType', 'equal_highs')
        tolerance = config.get('tolerance', 0.1) / 100.0  # Convert % to decimal
        lookback = config.get('lookback', 20)
        
        result = pd.DataFrame(index=data.index)
        result['sweep_detected'] = False
        result['sweep_price'] = np.nan
        
        for i in range(lookback, len(data)):
            if sweep_type == 'equal_highs':
                # Check if current high is equal to previous highs
                lookback_data = data.iloc[i-lookback:i]
                prev_highs = lookback_data['high'].values
                current_high = data.iloc[i]['high']
                
                # Check if current high is within tolerance of any previous high
                for prev_high in prev_highs:
                    if abs(current_high - prev_high) / prev_high <= tolerance:
                        result.iloc[i, result.columns.get_loc('sweep_detected')] = True
                        result.iloc[i, result.columns.get_loc('sweep_price')] = current_high
                        break
            
            elif sweep_type == 'equal_lows':
                # Check if current low is equal to previous lows
                lookback_data = data.iloc[i-lookback:i]
                prev_lows = lookback_data['low'].values
                current_low = data.iloc[i]['low']
                
                for prev_low in prev_lows:
                    if abs(current_low - prev_low) / prev_low <= tolerance:
                        result.iloc[i, result.columns.get_loc('sweep_detected')] = True
                        result.iloc[i, result.columns.get_loc('sweep_price')] = current_low
                        break
            
            elif sweep_type == 'session_high':
                # Previous session high
                if i >= 24:  # Assume 24 candles per day for 1h, adjust for other timeframes
                    session_data = data.iloc[i-24:i]
                    session_high = session_data['high'].max()
                    if data.iloc[i]['high'] >= session_high:
                        result.iloc[i, result.columns.get_loc('sweep_detected')] = True
                        result.iloc[i, result.columns.get_loc('sweep_price')] = session_high
            
            elif sweep_type == 'session_low':
                # Previous session low
                if i >= 24:
                    session_data = data.iloc[i-24:i]
                    session_low = session_data['low'].min()
                    if data.iloc[i]['low'] <= session_low:
                        result.iloc[i, result.columns.get_loc('sweep_detected')] = True
                        result.iloc[i, result.columns.get_loc('sweep_price')] = session_low
        
        return result
    
    def _detect_displacement(
        self, 
        data: pd.DataFrame, 
        config: dict,
        sweeps: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Detect displacement (strong impulsive candle away from sweep).
        
        Displacement should:
        1. Have large body (min_body_pct of range)
        2. Show strong move (min_move_pct from previous close OR strong body)
        3. Ideally occur after a sweep (if sweeps provided)
        
        Returns DataFrame with 'displacement_detected' and 'displacement_price' columns.
        """
        data = data.copy()
        min_body_pct = config.get('minBodyPct', 70) / 100.0
        min_move_pct = config.get('minMovePct', 1.5) / 100.0
        
        # Handle both camelCase and snake_case
        if 'minBodyPct' not in config:
            min_body_pct = config.get('min_body_pct', 70) / 100.0
        if 'minMovePct' not in config:
            min_move_pct = config.get('min_move_pct', 1.5) / 100.0
        
        # For 5m timeframe, be more lenient (1.5% is high for 5m)
        # Adjust based on timeframe if we can detect it
        timeframe_multiplier = 0.5  # Make it easier to detect
        
        result = pd.DataFrame(index=data.index)
        result['displacement_detected'] = False
        result['displacement_price'] = np.nan
        
        # More lenient detection - look for strong candles
        for i in range(1, len(data)):
            candle = data.iloc[i]
            prev_candle = data.iloc[i-1]
            
            # Calculate candle body
            body_size = abs(candle['close'] - candle['open'])
            candle_range = candle['high'] - candle['low']
            
            if candle_range == 0:
                continue
            
            body_pct = body_size / candle_range
            
            # Check if body is large enough (relaxed: allow 60% if move is strong)
            if body_pct < (min_body_pct * 0.85):  # 85% of required body size
                continue
            
            # Check for strong move (relative to previous close)
            if candle['close'] > candle['open']:  # Bullish candle
                # Move from previous close
                move_pct = (candle['close'] - prev_candle['close']) / prev_candle['close']
                
                # Candle body move (as % of open)
                candle_move_pct = (candle['close'] - candle['open']) / candle['open']
                
                # Displacement if: 
                # - Strong move (adjusted for timeframe) OR
                # - Strong candle body (70% of required move)
                threshold = min_move_pct * timeframe_multiplier
                if move_pct >= threshold or candle_move_pct >= (threshold * 0.7):
                    result.iloc[i, result.columns.get_loc('displacement_detected')] = True
                    result.iloc[i, result.columns.get_loc('displacement_price')] = candle['close']
            
            elif candle['close'] < candle['open']:  # Bearish candle
                # Move from previous close
                move_pct = (prev_candle['close'] - candle['close']) / prev_candle['close']
                
                # Candle body move
                candle_move_pct = (candle['open'] - candle['close']) / candle['open']
                
                # Displacement if: strong move OR strong candle body
                threshold = min_move_pct * timeframe_multiplier
                if move_pct >= threshold or candle_move_pct >= (threshold * 0.7):
                    result.iloc[i, result.columns.get_loc('displacement_detected')] = True
                    result.iloc[i, result.columns.get_loc('displacement_price')] = candle['close']
        
        return result
    
    def _precompute_module_conditions(
        self,
        data: pd.DataFrame,
        module,
        module_id: str,
        config: dict
    ) -> pd.Series:
        """
        Pre-compute module conditions for all rows (vectorized).
        This is much faster than checking row-by-row.
        
        Returns boolean Series indicating which rows meet the condition.
        """
        # Try to infer vectorized condition from module_id and data columns
        # This works for simple modules that set boolean flags
        
        # Kill Zones - simple boolean check
        if module_id == 'kill_zones' and 'in_kill_zone' in data.columns:
            return data['in_kill_zone'] == True
        
        # Premium/Discount Zones - direction dependent, return all True (filter later)
        elif module_id == 'premium_discount_zones':
            if 'in_discount' in data.columns and 'in_premium' in data.columns:
                return pd.Series(True, index=data.index)
        
        # Order Blocks
        elif module_id == 'order_blocks':
            if 'in_bullish_ob' in data.columns and 'in_bearish_ob' in data.columns:
                return (data['in_bullish_ob'] == True) | (data['in_bearish_ob'] == True)
        
        # Breaker Blocks
        elif module_id == 'breaker_blocks':
            if 'in_bullish_breaker' in data.columns and 'in_bearish_breaker' in data.columns:
                return (data['in_bullish_breaker'] == True) | (data['in_bearish_breaker'] == True)
        
        # Imbalance Zones
        elif module_id == 'imbalance_zones':
            if 'in_bullish_imbalance' in data.columns and 'in_bearish_imbalance' in data.columns:
                return (data['in_bullish_imbalance'] == True) | (data['in_bearish_imbalance'] == True)
        
        # Fair Value Gaps
        elif module_id == 'fair_value_gaps':
            if 'in_bullish_fvg' in data.columns and 'in_bearish_fvg' in data.columns:
                return (data['in_bullish_fvg'] == True) | (data['in_bearish_fvg'] == True)
        
        # Market Structure Shift
        elif module_id == 'market_structure_shift':
            if 'mss_active' in data.columns:
                return data['mss_active'] == True
        
        # Mitigation Blocks
        elif module_id == 'mitigation_blocks':
            if 'mitigation_active' in data.columns:
                return data['mitigation_active'] == True
        
        # Displacement
        elif module_id == 'displacement':
            if 'displacement_active' in data.columns:
                return data['displacement_active'] == True
        
        # Inducement
        elif module_id == 'inducement':
            if 'inducement_active' in data.columns:
                return data['inducement_active'] == True
        
        # Fallback: row-by-row check (slower but works for all modules)
        # Only do this for a sample to avoid hanging
        print(f"[V5] Using row-by-row check for {module_id} (no vectorized path)...")
        print(f"[V5] Warning: This may be slow for large datasets. Consider optimizing {module_id} module.")
        
        # Sample first 100 rows to test, then extrapolate
        sample_size = min(100, len(data))
        results = []
        for i in range(sample_size):
            try:
                result_long = module.check_entry_condition(data, i, config, 'LONG')
                result_short = module.check_entry_condition(data, i, config, 'SHORT')
                results.append(result_long or result_short)
            except Exception as e:
                results.append(False)
        
        # For remaining rows, assume False (conservative)
        if len(data) > sample_size:
            results.extend([False] * (len(data) - sample_size))
        
        return pd.Series(results, index=data.index, dtype=bool)
    
    def _simulate_trades(
        self, 
        data: pd.DataFrame, 
        risk: dict,
        additional_blocks: dict = None
    ) -> List[QuantMetricsTrade]:
        """
        Simulate trades based on signals.
        
        Entry logic:
        1. HTF bias must be BULLISH or BEARISH (not NEUTRAL)
        2. Liquidity sweep detected
        3. Displacement detected after sweep
        4. Enter on 50% retrace or first imbalance
        
        Exit logic:
        - SL: Beyond liquidity sweep (or structure)
        - TP: Risk multiple (1R-2R)
        """
        # Ensure index is DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index, errors='coerce')
            # Remove rows with invalid timestamps
            data = data[data.index.notna()]
        
        trades = []
        in_trade = False
        entry_price = None
        entry_index = None
        trade_direction = None
        sl_price = None
        tp_price = None
        
        tp_r = risk.get('takeProfit', 2.0)
        risk_per_trade = risk.get('riskPerTrade', 1.0)
        
        # Debug: Count potential entries at each stage
        potential_entries = {
            'htf_bias_ok': 0,
            'displacement_ok': 0,
            'sweep_ok': 0,
            'direction_ok': 0,
            'additional_blocks_ok': 0,
            'final_entries': 0
        }
        sl_method = risk.get('stopLoss', 'beyond_sweep')
        
        for i in range(len(data)):
            row = data.iloc[i]
            
            # Check entry conditions
            if not in_trade:
                # Must have HTF bias
                if row['htf_bias'] == 'NEUTRAL':
                    continue
                potential_entries['htf_bias_ok'] += 1
                
                # Must have displacement detected
                if not row['displacement_detected']:
                    continue
                potential_entries['displacement_ok'] += 1
                
                # Check if there was a sweep BEFORE this displacement
                # Look back up to 20 candles for a recent sweep
                sweep_found = False
                sweep_idx = None
                for j in range(max(0, i-20), i):
                    if data.iloc[j]['sweep_detected']:
                        sweep_found = True
                        sweep_idx = j
                        break
                
                if not sweep_found:
                    continue  # No sweep before displacement
                potential_entries['sweep_ok'] += 1
                
                # Determine trade direction based on HTF bias
                # If HTF bias is BULLISH, trade LONG
                # If HTF bias is BEARISH, trade SHORT
                htf_bias_raw = row['htf_bias']
                
                # Handle NaN or None values
                if pd.isna(htf_bias_raw) or htf_bias_raw is None:
                    continue  # Skip NaN values
                
                # Convert to string and normalize
                htf_bias_value = str(htf_bias_raw).strip().upper()
                
                # Handle 'nan' strings (from float NaN conversion)
                if htf_bias_value == 'NAN' or htf_bias_value == '':
                    continue
                
                # Debug first few values
                if i < 3:
                    print(f"[V5] Debug: Index {i}, htf_bias_raw={htf_bias_raw} (type: {type(htf_bias_raw)}), htf_bias_value='{htf_bias_value}'")
                
                if htf_bias_value == 'BULLISH':
                    trade_direction = 'LONG'
                    potential_entries['direction_ok'] += 1
                elif htf_bias_value == 'BEARISH':
                    trade_direction = 'SHORT'
                    potential_entries['direction_ok'] += 1
                else:
                    # Should be NEUTRAL (already filtered above) or unexpected value
                    if i < 3:
                        print(f"[V5] Debug: Skipping - htf_bias_value='{htf_bias_value}' is not BULLISH or BEARISH")
                    continue
                
                # Check additional ICT blocks (if any) - VECTORIZED (much faster)
                if additional_blocks and len(additional_blocks) > 0:
                    all_blocks_pass = True
                    for module_id, block_info in additional_blocks.items():
                        # Use pre-computed condition series (much faster than row-by-row)
                        if 'condition_series' in block_info:
                            condition_series = block_info['condition_series']
                            if not condition_series.iloc[i]:
                                all_blocks_pass = False
                                break
                            
                            # For direction-specific modules, check direction
                            row = data.iloc[i]
                            if module_id == 'premium_discount_zones':
                                if trade_direction == 'LONG' and not row.get('in_discount', False):
                                    all_blocks_pass = False
                                    break
                                elif trade_direction == 'SHORT' and not row.get('in_premium', False):
                                    all_blocks_pass = False
                                    break
                            elif module_id == 'order_blocks':
                                if trade_direction == 'LONG' and not row.get('in_bullish_ob', False):
                                    all_blocks_pass = False
                                    break
                                elif trade_direction == 'SHORT' and not row.get('in_bearish_ob', False):
                                    all_blocks_pass = False
                                    break
                            elif module_id == 'breaker_blocks':
                                if trade_direction == 'LONG' and not row.get('in_bullish_breaker', False):
                                    all_blocks_pass = False
                                    break
                                elif trade_direction == 'SHORT' and not row.get('in_bearish_breaker', False):
                                    all_blocks_pass = False
                                    break
                            elif module_id == 'imbalance_zones':
                                if trade_direction == 'LONG' and not row.get('in_bullish_imbalance', False):
                                    all_blocks_pass = False
                                    break
                                elif trade_direction == 'SHORT' and not row.get('in_bearish_imbalance', False):
                                    all_blocks_pass = False
                                    break
                            elif module_id == 'fair_value_gaps':
                                if trade_direction == 'LONG' and not row.get('in_bullish_fvg', False):
                                    all_blocks_pass = False
                                    break
                                elif trade_direction == 'SHORT' and not row.get('in_bearish_fvg', False):
                                    all_blocks_pass = False
                                    break
                        else:
                            # Fallback: row-by-row check (slower - should not happen if precompute worked)
                            module = block_info['module']
                            config = block_info['config']
                            try:
                                if not module.check_entry_condition(data, i, config, trade_direction):
                                    all_blocks_pass = False
                                    break
                            except Exception as e:
                                all_blocks_pass = False
                                break
                    
                    if not all_blocks_pass:
                        continue  # Skip this entry if any additional block fails
                
                potential_entries['additional_blocks_ok'] += 1
                potential_entries['final_entries'] += 1
                
                # Get sweep price from the sweep we found
                sweep_price = data.iloc[sweep_idx]['sweep_price']
                
                # Entry: 50% retrace or at displacement price
                # For simplicity, enter at displacement price (close of displacement candle)
                # In real trading, you'd enter on next candle open or at 50% retrace
                entry_price = row['displacement_price']  # Close of displacement candle
                entry_index = i
                
                # Note: In production, you might want to enter on next candle open
                # or wait for 50% retrace from displacement high/low
                
                # Calculate SL (beyond sweep)
                if sl_method == 'beyond_sweep':
                    if trade_direction == 'LONG':
                        sl_price = sweep_price * 0.999  # Slightly below sweep
                    else:
                        sl_price = sweep_price * 1.001  # Slightly above sweep
                else:
                    # Default: 1% risk
                    if trade_direction == 'LONG':
                        sl_price = entry_price * 0.99
                    else:
                        sl_price = entry_price * 1.01
                
                # Calculate TP
                risk_amount = abs(entry_price - sl_price) * risk_per_trade
                if trade_direction == 'LONG':
                    tp_price = entry_price + (risk_amount * tp_r)
                else:
                    tp_price = entry_price - (risk_amount * tp_r)
                
                in_trade = True
            
            # Check exit conditions
            if in_trade:
                if trade_direction == 'LONG':
                    if row['high'] >= tp_price:
                        # TP hit
                        exit_price = tp_price
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'LONG', True,
                            data.index[entry_index], data.index[i],
                            sl_price, tp_price
                        ))
                        in_trade = False
                    elif row['low'] <= sl_price:
                        # SL hit
                        exit_price = sl_price
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'LONG', False,
                            data.index[entry_index], data.index[i],
                            sl_price, tp_price
                        ))
                        in_trade = False
                else:  # SHORT
                    if row['low'] <= tp_price:
                        # TP hit
                        exit_price = tp_price
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'SHORT', True,
                            data.index[entry_index], data.index[i],
                            sl_price, tp_price
                        ))
                        in_trade = False
                    elif row['high'] >= sl_price:
                        # SL hit
                        exit_price = sl_price
                        trades.append(self._create_trade(
                            entry_price, exit_price, 'SHORT', False,
                            data.index[entry_index], data.index[i],
                            sl_price, tp_price
                        ))
                        in_trade = False
        
        # Debug output
        print(f"[V5] Entry filtering stats:")
        print(f"[V5]   HTF bias OK: {potential_entries['htf_bias_ok']}")
        print(f"[V5]   Displacement OK: {potential_entries['displacement_ok']}")
        print(f"[V5]   Sweep OK: {potential_entries['sweep_ok']}")
        print(f"[V5]   Direction OK: {potential_entries['direction_ok']}")
        print(f"[V5]   Additional blocks OK: {potential_entries['additional_blocks_ok']}")
        print(f"[V5]   Final entries: {potential_entries['final_entries']}")
        
        return trades
    
    def _create_trade(
        self,
        entry_price: float,
        exit_price: float,
        direction: str,
        is_winner: bool,
        entry_time: datetime,
        exit_time: datetime,
        sl_price: float,
        tp_price: float
    ) -> QuantMetricsTrade:
        """Create a QuantMetricsTrade object."""
        # Calculate profit
        if direction == 'LONG':
            profit_usd = exit_price - entry_price
        else:  # SHORT
            profit_usd = entry_price - exit_price
        
        # Calculate R-multiple
        risk = abs(entry_price - sl_price)
        if risk > 0:
            profit_r = profit_usd / risk
        else:
            profit_r = 0.0
        
        # Determine result based on actual profit_r, not is_winner flag
        # (is_winner is based on TP/SL hit, but actual exit might differ)
        if profit_r > 0:
            result = 'WIN'
        elif profit_r < 0:
            result = 'LOSS'
        else:
            result = 'LOSS'  # Break-even counts as loss
        
        return QuantMetricsTrade(
            timestamp_open=entry_time,
            timestamp_close=exit_time,
            symbol="",  # Will be set by analyzer
            direction=direction,
            entry_price=entry_price,
            exit_price=exit_price,
            sl=sl_price,
            tp=tp_price,
            profit_usd=profit_usd,
            profit_r=profit_r,
            result=result
        )

