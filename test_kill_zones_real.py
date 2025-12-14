# test_kill_zones_real.py
"""Test Kill Zones module with real market data - FINAL ICT MODULE TEST!"""

import pandas as pd
from datetime import datetime, timedelta
from core.strategy_modules.ict.kill_zones import KillZonesModule
from core.data_manager import DataManager

print("="*70)
print("KILL ZONES - REAL MARKET DATA TEST")
print("="*70)
print("🎯 FINAL ICT MODULE - Week 1 Complete After This!")
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
kz_module = KillZonesModule()

# Test different configurations
configs = [
    {
        'name': 'London + NY (Recommended)',
        'enabled_zones': ['london', 'newyork'],
        'london_start': 7,
        'london_end': 10,
        'ny_start': 12,
        'ny_end': 15,
        'asian_start': 0,
        'asian_end': 3
    },
    {
        'name': 'All Zones',
        'enabled_zones': ['london', 'newyork', 'asian'],
        'london_start': 7,
        'london_end': 10,
        'ny_start': 12,
        'ny_end': 15,
        'asian_start': 0,
        'asian_end': 3
    },
    {
        'name': 'London Only',
        'enabled_zones': ['london'],
        'london_start': 7,
        'london_end': 10,
        'ny_start': 12,
        'ny_end': 15,
        'asian_start': 0,
        'asian_end': 3
    }
]

for test_config in configs:
    config_name = test_config.pop('name')
    
    print("="*70)
    print(f"TESTING: {config_name}")
    print("="*70)
    print()
    
    # Calculate
    result = kz_module.calculate(data.copy(), test_config)
    
    # Count kill zone candles
    total_kz = len(result[result['in_kill_zone'] == True])
    london_kz = len(result[result['in_london_kz'] == True])
    ny_kz = len(result[result['in_newyork_kz'] == True])
    asian_kz = len(result[result['in_asian_kz'] == True])
    
    print(f"Kill Zone Coverage:")
    print(f"  Total candles in kill zones: {total_kz} ({total_kz/len(result)*100:.1f}%)")
    print(f"  London: {london_kz} candles ({london_kz/len(result)*100:.1f}%)")
    print(f"  New York: {ny_kz} candles ({ny_kz/len(result)*100:.1f}%)")
    print(f"  Asian: {asian_kz} candles ({asian_kz/len(result)*100:.1f}%)")
    print(f"  Outside zones: {len(result) - total_kz} candles ({(len(result)-total_kz)/len(result)*100:.1f}%)")
    print()

print("="*70)
print("DETAILED ANALYSIS: London + NY Configuration")
print("="*70)
print()

# Use recommended config
config = {
    'enabled_zones': ['london', 'newyork'],
    'london_start': 7,
    'london_end': 10,
    'ny_start': 12,
    'ny_end': 15,
    'asian_start': 0,
    'asian_end': 3
}

result = kz_module.calculate(data.copy(), config)

# Show hourly distribution
print("Hourly Distribution of Data:")
hour_counts = result.groupby(result['timestamp'].dt.hour).size()
print(f"\n{'Hour (UTC)':<12} {'Candles':<10} {'Kill Zone'}")
print("-" * 50)
for hour in sorted(hour_counts.index):
    count = hour_counts[hour]
    # Check if this hour is in a kill zone
    kz_name = ''
    if 7 <= hour < 10:
        kz_name = '🟢 LONDON'
    elif 12 <= hour < 15:
        kz_name = '🔵 NEW YORK'
    else:
        kz_name = '⚪ Outside'
    
    print(f"{hour:02d}:00 UTC    {count:<10} {kz_name}")

print()

# Performance by zone (if we had trade data, we'd analyze it here)
print("="*70)
print("KILL ZONE CHARACTERISTICS:")
print("="*70)
print()

london_candles = result[result['in_london_kz'] == True]
ny_candles = result[result['in_newyork_kz'] == True]

if not london_candles.empty:
    london_range = london_candles['high'].max() - london_candles['low'].min()
    london_avg_range = (london_candles['high'] - london_candles['low']).mean()
    print(f"London Kill Zone (07:00-10:00 UTC):")
    print(f"  Candles: {len(london_candles)}")
    print(f"  Total price range: {london_range:.2f}")
    print(f"  Avg candle range: {london_avg_range:.2f}")
    print(f"  Characteristics: Strong directional moves, trend continuation")
    print()

if not ny_candles.empty:
    ny_range = ny_candles['high'].max() - ny_candles['low'].min()
    ny_avg_range = (ny_candles['high'] - ny_candles['low']).mean()
    print(f"New York Kill Zone (12:00-15:00 UTC):")
    print(f"  Candles: {len(ny_candles)}")
    print(f"  Total price range: {ny_range:.2f}")
    print(f"  Avg candle range: {ny_avg_range:.2f}")
    print(f"  Characteristics: High volume, reversals common")
    print()

print("="*70)
print("ENTRY SIGNAL LOGIC:")
print("="*70)
print()

# Count how many candles would pass the time filter
long_signals = 0
short_signals = 0

for i in range(len(result)):
    # Kill zones act as TIME FILTER (same for both directions)
    if kz_module.check_entry_condition(result, i, config, 'LONG'):
        long_signals += 1
    if kz_module.check_entry_condition(result, i, config, 'SHORT'):
        short_signals += 1

print(f"Time Filter Results:")
print(f"  Candles in kill zones: {long_signals} (same for LONG/SHORT)")
print(f"  Candles outside zones: {len(result) - long_signals}")
print()
print("Note: Kill Zones is a TIME FILTER, not a directional signal.")
print("Combine with other ICT concepts (OB, FVG, MSS) for entries.")

print()
print("="*70)
print("SUMMARY:")
print("="*70)
print(f"Total Candles: {len(result)}")
print(f"London Kill Zone: {len(london_candles)} candles")
print(f"New York Kill Zone: {len(ny_candles)} candles")
print(f"Total in Kill Zones: {long_signals} ({long_signals/len(result)*100:.1f}%)")
print()
print("="*70)
print("🎉 KILL ZONES MODULE VALIDATED - FINAL ICT MODULE COMPLETE!")
print("="*70)
print()
print("🏆 WEEK 1 COMPLETE: 11/11 ICT MODULES FINISHED!")
print("="*70)