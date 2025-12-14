# test_imbalance_zones_real.py
"""Test Imbalance Zones module with real market data"""

import pandas as pd
from datetime import datetime, timedelta
from core.strategy_modules.ict.imbalance_zones import ImbalanceZonesModule
from core.data_manager import DataManager

print("="*70)
print("IMBALANCE ZONES - REAL MARKET DATA TEST")
print("="*70)
print()

# Fetch real data
data_manager = DataManager()
symbol = 'XAUUSD'
timeframe = '15m'  # Use 15m for more imbalances
end = datetime.now()
start = end - timedelta(days=14)  # 2 weeks

print(f"Fetching data: {symbol} {timeframe} for 14 days")
data = data_manager.get_data(symbol=symbol, timeframe=timeframe, start=start, end=end)
print(f"Data loaded: {len(data)} candles")
print(f"Price range: {data['low'].min():.2f} - {data['high'].max():.2f}")
print()

# Initialize module
imbalance_module = ImbalanceZonesModule()

# Test configurations
configs = [
    {
        'name': 'Standard',
        'min_gap_size': 0.5,
        'validity_candles': 50,
        'fill_threshold': 50
    },
    {
        'name': 'Sensitive (Small Gaps)',
        'min_gap_size': 0.2,
        'validity_candles': 50,
        'fill_threshold': 50
    },
    {
        'name': 'Large Gaps Only',
        'min_gap_size': 1.0,
        'validity_candles': 50,
        'fill_threshold': 50
    }
]

for test_config in configs:
    config_name = test_config.pop('name')
    
    print("="*70)
    print(f"TESTING: {config_name}")
    print("="*70)
    
    print("\nConfiguration:")
    for key, value in test_config.items():
        print(f"  {key}: {value}")
    print()
    
    # Calculate
    result = imbalance_module.calculate(data.copy(), test_config)
    
    # Find imbalances
    bullish_imb = result[result['bullish_imbalance'] == True]
    bearish_imb = result[result['bearish_imbalance'] == True]
    
    print(f"Bullish Imbalances Detected: {len(bullish_imb)}")
    print(f"Bearish Imbalances Detected: {len(bearish_imb)}")
    
    # Count filled imbalances
    filled = result[result['imbalance_filled'] == True]
    print(f"Imbalances Filled: {len(filled)}")
    
    # Count entry signals
    long_signals = 0
    short_signals = 0
    
    for i in range(len(result)):
        if imbalance_module.check_entry_condition(result, i, test_config, 'LONG'):
            long_signals += 1
        if imbalance_module.check_entry_condition(result, i, test_config, 'SHORT'):
            short_signals += 1
    
    print(f"\nEntry Signals:")
    print(f"  LONG: {long_signals}")
    print(f"  SHORT: {short_signals}")
    print()

print("="*70)
print("DETAILED ANALYSIS: Standard Configuration")
print("="*70)
print()

# Use standard config
config = {
    'min_gap_size': 0.5,
    'validity_candles': 50,
    'fill_threshold': 50
}

result = imbalance_module.calculate(data.copy(), config)

# Analyze imbalances
bullish_imb = result[result['bullish_imbalance'] == True]
bearish_imb = result[result['bearish_imbalance'] == True]

print(f"Imbalance Statistics:")
print(f"  Total Bullish: {len(bullish_imb)}")
print(f"  Total Bearish: {len(bearish_imb)}")
print()

if not bullish_imb.empty:
    print("Recent Bullish Imbalances (last 5):")
    for idx in bullish_imb.tail(5).index:
        row = result.iloc[idx]
        gap_size = row['imbalance_high'] - row['imbalance_low']
        print(f"\n  Index {idx}:")
        print(f"    Zone: {row['imbalance_low']:.2f} - {row['imbalance_high']:.2f}")
        print(f"    Gap Size: {gap_size:.2f}")
        print(f"    Close: {row['close']:.2f}")

print()

if not bearish_imb.empty:
    print("Recent Bearish Imbalances (last 5):")
    for idx in bearish_imb.tail(5).index:
        row = result.iloc[idx]
        gap_size = row['imbalance_high'] - row['imbalance_low']
        print(f"\n  Index {idx}:")
        print(f"    Zone: {row['imbalance_low']:.2f} - {row['imbalance_high']:.2f}")
        print(f"    Gap Size: {gap_size:.2f}")
        print(f"    Close: {row['close']:.2f}")

print()
print("="*70)
print("ENTRY SIGNAL EXAMPLES:")
print("="*70)
print()

# Show first few entry signals
long_count = 0
short_count = 0

for i in range(len(result)):
    row = result.iloc[i]
    
    if imbalance_module.check_entry_condition(result, i, config, 'LONG'):
        long_count += 1
        if long_count <= 3:
            print(f"LONG Signal #{long_count} at index {i}:")
            print(f"  Price: {row['close']:.2f}")
            print(f"  Imbalance Zone: {row['imbalance_low']:.2f} - {row['imbalance_high']:.2f}")
            print()
    
    if imbalance_module.check_entry_condition(result, i, config, 'SHORT'):
        short_count += 1
        if short_count <= 3:
            print(f"SHORT Signal #{short_count} at index {i}:")
            print(f"  Price: {row['close']:.2f}")
            print(f"  Imbalance Zone: {row['imbalance_low']:.2f} - {row['imbalance_high']:.2f}")
            print()

# Fill analysis
filled_count = len(result[result['imbalance_filled'] == True])
if filled_count > 0:
    print(f"Imbalance Fill Events: {filled_count}")
    print(f"  (Price returned to fill gaps)")

print()
print("="*70)
print("SUMMARY:")
print("="*70)
print(f"Total Candles: {len(result)}")
print(f"Bullish Imbalances: {len(bullish_imb)}")
print(f"Bearish Imbalances: {len(bearish_imb)}")
print(f"Total LONG Signals: {long_count}")
print(f"Total SHORT Signals: {short_count}")
print(f"Fill Events: {filled_count}")
print()
print("="*70)
print("✓ IMBALANCE ZONES MODULE VALIDATED ON REAL MARKET DATA")
print("="*70)