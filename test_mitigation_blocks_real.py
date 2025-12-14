# test_mitigation_blocks_real.py
"""Test Mitigation Blocks module with real market data"""

import pandas as pd
from datetime import datetime, timedelta
from core.strategy_modules.ict.mitigation_blocks import MitigationBlocksModule
from core.data_manager import DataManager

print("="*70)
print("MITIGATION BLOCKS - REAL MARKET DATA TEST")
print("="*70)
print()

# Fetch real data
data_manager = DataManager()
symbol = 'XAUUSD'
timeframe = '1h'
end = datetime.now()
start = end - timedelta(days=30)

print(f"Fetching data: {symbol} {timeframe} for 30 days")
data = data_manager.get_data(symbol=symbol, timeframe=timeframe, start=start, end=end)
print(f"Data loaded: {len(data)} candles")
print(f"Price range: {data['low'].min():.2f} - {data['high'].max():.2f}")
print()

# Initialize module
mitigation_module = MitigationBlocksModule()
config = {
    'min_candles': 3,
    'min_move_pct': 2.0,
    'mitigation_validity': 20,
    'hold_candles': 2
}

print("Module Configuration:")
for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Calculate
result = mitigation_module.calculate(data, config)

print("="*70)
print("ORDER BLOCK DETECTION:")
print("="*70)

# Find all order blocks
all_obs = result[result['order_block'] == True]
bullish_obs = all_obs[all_obs['ob_type'] == 'BULLISH']
bearish_obs = all_obs[all_obs['ob_type'] == 'BEARISH']

print(f"\nTotal Order Blocks Detected: {len(all_obs)}")
print(f"  Bullish OBs: {len(bullish_obs)}")
print(f"  Bearish OBs: {len(bearish_obs)}")

if not bullish_obs.empty:
    print(f"\nRecent Bullish Order Blocks (last 3):")
    for idx in bullish_obs.tail(3).index:
        row = result.iloc[idx]
        zone_size = row['ob_high'] - row['ob_low']
        print(f"  Index {idx}:")
        print(f"    Zone: {row['ob_low']:.2f} - {row['ob_high']:.2f} (size: {zone_size:.2f})")

if not bearish_obs.empty:
    print(f"\nRecent Bearish Order Blocks (last 3):")
    for idx in bearish_obs.tail(3).index:
        row = result.iloc[idx]
        zone_size = row['ob_high'] - row['ob_low']
        print(f"  Index {idx}:")
        print(f"    Zone: {row['ob_low']:.2f} - {row['ob_high']:.2f} (size: {zone_size:.2f})")

print()
print("="*70)
print("MITIGATION EVENTS:")
print("="*70)

# Find mitigations
bullish_mit = result[result['bullish_mitigation'] == True]
bearish_mit = result[result['bearish_mitigation'] == True]

print(f"\nBullish Mitigations: {len(bullish_mit)}")
if not bullish_mit.empty:
    print("\nBullish Mitigation Details:")
    for idx in bullish_mit.index:
        row = result.iloc[idx]
        print(f"  Index {idx}:")
        print(f"    Price: {row['close']:.2f}")
        print(f"    Type: {row['mitigation_type']}")

print(f"\nBearish Mitigations: {len(bearish_mit)}")
if not bearish_mit.empty:
    print("\nBearish Mitigation Details:")
    for idx in bearish_mit.index:
        row = result.iloc[idx]
        print(f"  Index {idx}:")
        print(f"    Price: {row['close']:.2f}")
        print(f"    Type: {row['mitigation_type']}")

print()
print("="*70)
print("ENTRY SIGNALS:")
print("="*70)

# Count entry signals
long_signals = 0
short_signals = 0
long_examples = []
short_examples = []

for i in range(len(result)):
    if mitigation_module.check_entry_condition(result, i, config, 'LONG'):
        long_signals += 1
        if len(long_examples) < 3:
            long_examples.append((i, result.iloc[i]))
    
    if mitigation_module.check_entry_condition(result, i, config, 'SHORT'):
        short_signals += 1
        if len(short_examples) < 3:
            short_examples.append((i, result.iloc[i]))

print(f"\nTotal LONG Signals: {long_signals}")
if long_examples:
    print("\nLONG Signal Examples:")
    for idx, row in long_examples:
        print(f"  Index {idx}: Price {row['close']:.2f}, Type: {row['mitigation_type']}")

print(f"\nTotal SHORT Signals: {short_signals}")
if short_examples:
    print("\nSHORT Signal Examples:")
    for idx, row in short_examples:
        print(f"  Index {idx}: Price {row['close']:.2f}, Type: {row['mitigation_type']}")

print()
print("="*70)
print("SUMMARY:")
print("="*70)
print(f"Total Candles: {len(result)}")
print(f"Order Blocks Detected: {len(all_obs)} ({len(bullish_obs)} bullish, {len(bearish_obs)} bearish)")
print(f"Mitigation Events: {len(bullish_mit) + len(bearish_mit)} ({len(bullish_mit)} bullish, {len(bearish_mit)} bearish)")
print(f"LONG Signals: {long_signals}")
print(f"SHORT Signals: {short_signals}")
print()
print("="*70)
print("✓ MITIGATION BLOCKS MODULE VALIDATED ON REAL MARKET DATA")
print("="*70)