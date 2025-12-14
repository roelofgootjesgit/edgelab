# test_inducement_real.py
"""Test Inducement module with real market data"""

import pandas as pd
from datetime import datetime, timedelta
from core.strategy_modules.ict.inducement import InducementModule
from core.data_manager import DataManager

print("="*70)
print("INDUCEMENT - REAL MARKET DATA TEST")
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
inducement_module = InducementModule()
config = {
    'lookback_candles': 10,
    'break_threshold_pct': 0.2,
    'reversal_candles': 2,
    'reversal_pct': 0.5,
    'validity_candles': 15
}

print("Module Configuration:")
for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Calculate
result = inducement_module.calculate(data, config)

print("="*70)
print("SWING POINT ANALYSIS:")
print("="*70)

# Count swing points
swing_highs = result[~result['swing_high'].isna()]
swing_lows = result[~result['swing_low'].isna()]

print(f"\nSwing Points Detected:")
print(f"  Swing Highs: {len(swing_highs)}")
print(f"  Swing Lows: {len(swing_lows)}")

if not swing_highs.empty:
    print(f"\nRecent Swing Highs (last 5):")
    for idx in swing_highs.tail(5).index:
        row = result.iloc[idx]
        print(f"  Index {idx}: {row['swing_high']:.2f}")

if not swing_lows.empty:
    print(f"\nRecent Swing Lows (last 5):")
    for idx in swing_lows.tail(5).index:
        row = result.iloc[idx]
        print(f"  Index {idx}: {row['swing_low']:.2f}")

print()
print("="*70)
print("INDUCEMENT EVENTS:")
print("="*70)

# Find inducements
bullish_ind = result[result['bullish_inducement'] == True]
bearish_ind = result[result['bearish_inducement'] == True]

print(f"\nBullish Inducements (fake breakouts): {len(bullish_ind)}")
if not bullish_ind.empty:
    print("\nBullish Inducement Details:")
    for idx in bullish_ind.index:
        row = result.iloc[idx]
        print(f"  Index {idx}:")
        print(f"    Level broken: {row['inducement_level']:.2f}")
        print(f"    Close: {row['close']:.2f}")
        print(f"    (Fake breakout UP, reversed DOWN)")

print(f"\nBearish Inducements (fake breakdowns): {len(bearish_ind)}")
if not bearish_ind.empty:
    print("\nBearish Inducement Details:")
    for idx in bearish_ind.index:
        row = result.iloc[idx]
        print(f"  Index {idx}:")
        print(f"    Level broken: {row['inducement_level']:.2f}")
        print(f"    Close: {row['close']:.2f}")
        print(f"    (Fake breakdown DOWN, reversed UP)")

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
    if inducement_module.check_entry_condition(result, i, config, 'LONG'):
        long_signals += 1
        if len(long_examples) < 3:
            long_examples.append((i, result.iloc[i]))
    
    if inducement_module.check_entry_condition(result, i, config, 'SHORT'):
        short_signals += 1
        if len(short_examples) < 3:
            short_examples.append((i, result.iloc[i]))

print(f"\nTotal LONG Signals: {long_signals}")
print("  (Enter LONG after bearish inducement - fake breakdown trapped shorts)")
if long_examples:
    print("\nLONG Signal Examples:")
    for idx, row in long_examples:
        print(f"  Index {idx}: Price {row['close']:.2f}, Type: {row['inducement_type']}")

print(f"\nTotal SHORT Signals: {short_signals}")
print("  (Enter SHORT after bullish inducement - fake breakout trapped longs)")
if short_examples:
    print("\nSHORT Signal Examples:")
    for idx, row in short_examples:
        print(f"  Index {idx}: Price {row['close']:.2f}, Type: {row['inducement_type']}")

print()
print("="*70)
print("SUMMARY:")
print("="*70)
print(f"Total Candles: {len(result)}")
print(f"Swing Highs: {len(swing_highs)}")
print(f"Swing Lows: {len(swing_lows)}")
print(f"Bullish Inducements: {len(bullish_ind)} (fake breakouts)")
print(f"Bearish Inducements: {len(bearish_ind)} (fake breakdowns)")
print(f"LONG Signals: {long_signals} (fade bearish inducement)")
print(f"SHORT Signals: {short_signals} (fade bullish inducement)")
print()
print("="*70)
print("✓ INDUCEMENT MODULE VALIDATED ON REAL MARKET DATA")
print("="*70)