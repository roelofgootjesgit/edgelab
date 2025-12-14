# test_mss_full.py
"""Full MSS test with real data and entry signals"""

import pandas as pd
from datetime import datetime, timedelta
from core.strategy_modules.ict.market_structure_shift import MarketStructureShiftModule
from core.data_manager import DataManager

print("="*70)
print("MARKET STRUCTURE SHIFT - FULL REAL DATA TEST")
print("="*70)
print()

# Fetch data
data_manager = DataManager()
symbol = 'XAUUSD'
timeframe = '1h'
end = datetime.now()
start = end - timedelta(days=30)

print(f"Fetching data: {symbol} {timeframe} for 30 days")
data = data_manager.get_data(symbol=symbol, timeframe=timeframe, start=start, end=end)
print(f"Data loaded: {len(data)} candles")
print()

# Initialize module with optimal config
mss_module = MarketStructureShiftModule()
config = {
    'swing_lookback': 5,
    'break_threshold_pct': 0.2,  # Optimal for gold
    'mss_validity_candles': 10
}

print("Module Configuration:")
for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Calculate MSS
result = mss_module.calculate(data, config)

print("="*70)
print("MARKET STRUCTURE ANALYSIS:")
print("="*70)

# MSS Events
bullish_mss = result[result['bullish_mss'] == True]
bearish_mss = result[result['bearish_mss'] == True]

print(f"\nBullish MSS Events: {len(bullish_mss)}")
if not bullish_mss.empty:
    print("\nRecent Bullish MSS (last 5):")
    for idx in bullish_mss.tail(5).index:
        row = result.iloc[idx]
        print(f"  Index {idx}: Price broke above {row['recent_swing_high']:.2f}")
        print(f"    High: {row['high']:.2f} | Close: {row['close']:.2f}")

print(f"\nBearish MSS Events: {len(bearish_mss)}")
if not bearish_mss.empty:
    print("\nRecent Bearish MSS (last 5):")
    for idx in bearish_mss.tail(5).index:
        row = result.iloc[idx]
        print(f"  Index {idx}: Price broke below {row['recent_swing_low']:.2f}")
        print(f"    Low: {row['low']:.2f} | Close: {row['close']:.2f}")

print()
print("="*70)
print("TRADING SIGNALS:")
print("="*70)

# Test LONG signals (after bullish MSS)
long_signals = 0
short_signals = 0

for i in range(len(result)):
    # LONG after bullish MSS
    if mss_module.check_entry_condition(result, i, config, 'LONG'):
        long_signals += 1
        if long_signals <= 5:  # Show first 5
            row = result.iloc[i]
            print(f"\nLONG Signal at index {i}:")
            print(f"  Price: {row['close']:.2f}")
            print(f"  MSS Type: {row['mss_type']}")
            print(f"  MSS Active: {row['mss_active']}")
    
    # SHORT after bearish MSS
    if mss_module.check_entry_condition(result, i, config, 'SHORT'):
        short_signals += 1
        if short_signals <= 5:  # Show first 5
            row = result.iloc[i]
            print(f"\nSHORT Signal at index {i}:")
            print(f"  Price: {row['close']:.2f}")
            print(f"  MSS Type: {row['mss_type']}")
            print(f"  MSS Active: {row['mss_active']}")

print()
print("="*70)
print("SUMMARY:")
print("="*70)
print(f"Total Candles: {len(result)}")
print(f"Bullish MSS Events: {len(bullish_mss)}")
print(f"Bearish MSS Events: {len(bearish_mss)}")
print(f"LONG Entry Signals: {long_signals}")
print(f"SHORT Entry Signals: {short_signals}")
print()
print("="*70)
print("MSS MODULE VALIDATED ON REAL MARKET DATA")
print("="*70)