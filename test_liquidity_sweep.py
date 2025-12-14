# test_liquidity_sweep.py
"""Test Liquidity Sweep module"""

import pandas as pd
import numpy as np
from core.strategy_modules.ict.liquidity_sweep import LiquiditySweepModule

print("="*70)
print("LIQUIDITY SWEEP MODULE TEST")
print("="*70)
print()

# Create test data with clear bullish sweep pattern:
# Candles 0-19: Establish range (swing low around 98)
# Candle 20: Break below swing low (sweep stops)
# Candle 21-22: Strong reversal up (confirms sweep)

data_list = []

# Initial range (candles 0-19)
for i in range(20):
    data_list.append({
        'open': 100 + np.random.uniform(-1, 1),
        'high': 101 + np.random.uniform(-1, 1),
        'low': 99 + np.random.uniform(-1, 1),
        'close': 100 + np.random.uniform(-1, 1)
    })

# Set specific swing low at candle 10
data_list[10] = {'open': 100, 'high': 101, 'low': 98, 'close': 99}

# Candle 20: Sweep below swing low
data_list.append({'open': 99, 'high': 100, 'low': 97.5, 'close': 98})

# Candle 21-22: Strong reversal up
data_list.append({'open': 98, 'high': 101, 'low': 98, 'close': 100.5})
data_list.append({'open': 100.5, 'high': 102, 'low': 100, 'close': 101.5})

data = pd.DataFrame(data_list)

print("Test Data Pattern:")
print("  Candles 0-19: Range with swing low at 98 (candle 10)")
print("  Candle 20: Sweep below 98 to 97.5")
print("  Candles 21-22: Reversal up to 101.5")
print()
print("Key candles:")
print(data.iloc[[10, 19, 20, 21, 22]][['open', 'high', 'low', 'close']])
print()

# Instantiate module
sweep_module = LiquiditySweepModule()

print("Module Configuration:")
config = {
    'lookback_candles': 15,         # Look back 15 candles for swing points
    'sweep_threshold_pct': 0.2,     # Must exceed by 0.2%
    'reversal_candles': 3,          # Allow 3 candles for reversal
    'reversal_strength_pct': 0.5    # Must reverse 0.5%
}

for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Calculate
result = sweep_module.calculate(data.copy(), config)

print("="*70)
print("RESULTS:")
print("="*70)
print()

# Show key columns for relevant candles
print("Swing levels and sweeps:")
display_cols = ['close', 'swing_high', 'swing_low', 'bullish_sweep', 'bearish_sweep', 'sweep_type']
print(result.iloc[15:][display_cols])
print()

# Check for sweeps
bullish_sweeps = result[result['bullish_sweep'] == True]
bearish_sweeps = result[result['bearish_sweep'] == True]

if not bullish_sweeps.empty:
    print("BULLISH SWEEP DETECTED:")
    for idx in bullish_sweeps.index:
        swing_low = result.iloc[idx-1]['swing_low']
        actual_low = result.iloc[idx]['low']
        print(f"  Candle {idx}:")
        print(f"    Swing Low: {swing_low:.2f}")
        print(f"    Actual Low: {actual_low:.2f}")
        print(f"    Sweep: {actual_low:.2f} < {swing_low:.2f}")
    print()
else:
    print("No bullish sweep detected")
    print()

if not bearish_sweeps.empty:
    print("BEARISH SWEEP DETECTED:")
    for idx in bearish_sweeps.index:
        swing_high = result.iloc[idx-1]['swing_high']
        actual_high = result.iloc[idx]['high']
        print(f"  Candle {idx}:")
        print(f"    Swing High: {swing_high:.2f}")
        print(f"    Actual High: {actual_high:.2f}")
        print(f"    Sweep: {actual_high:.2f} > {swing_high:.2f}")
    print()
else:
    print("No bearish sweep detected")
    print()

# Test entry signals
print("="*70)
print("ENTRY SIGNAL TESTS:")
print("="*70)
print()

long_signals = []
short_signals = []

for i in range(len(result)):
    long_signal = sweep_module.check_entry_condition(result, i, config, 'LONG')
    short_signal = sweep_module.check_entry_condition(result, i, config, 'SHORT')
    
    if long_signal:
        long_signals.append(i)
        print(f"  Candle {i}: LONG signal (bullish sweep detected)")
    if short_signal:
        short_signals.append(i)
        print(f"  Candle {i}: SHORT signal (bearish sweep detected)")

if not long_signals and not short_signals:
    print("  No entry signals detected")

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)

if bullish_sweeps.empty and bearish_sweeps.empty:
    print()
    print("DEBUGGING INFO:")
    print()
    print("Checking candle 20 (sweep candidate):")
    print(f"  Swing Low (from candle 19): {result.iloc[19]['swing_low']:.2f}")
    print(f"  Candle 20 Low: {result.iloc[20]['low']:.2f}")
    
    sweep_level = result.iloc[19]['swing_low'] * (1 - config['sweep_threshold_pct']/100)
    print(f"  Required sweep level: {sweep_level:.2f}")
    print(f"  Sweep condition met: {result.iloc[20]['low'] <= sweep_level}")
    
    print()
    print("Checking reversal (candles 21-22):")
    reversal_target = result.iloc[19]['swing_low'] * (1 + config['reversal_strength_pct']/100)
    print(f"  Required reversal target: {reversal_target:.2f}")
    print(f"  Candle 21 high: {result.iloc[21]['high']:.2f}")
    print(f"  Candle 22 high: {result.iloc[22]['high']:.2f}")
    print(f"  Reversal condition met: {result.iloc[21]['high'] >= reversal_target or result.iloc[22]['high'] >= reversal_target}")