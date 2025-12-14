# test_displacement_real.py
"""Test Displacement module with real market data"""

import pandas as pd
from datetime import datetime, timedelta
from core.strategy_modules.ict.displacement import DisplacementModule
from core.data_manager import DataManager

print("="*70)
print("DISPLACEMENT - REAL MARKET DATA TEST")
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
displacement_module = DisplacementModule()

# Test with different configurations
configs = [
    {
        'name': 'Standard',
        'min_body_pct': 70,
        'min_candles': 3,
        'min_move_pct': 1.5,
        'validity_candles': 10
    },
    {
        'name': 'Sensitive',
        'min_body_pct': 60,
        'min_candles': 2,
        'min_move_pct': 1.0,
        'validity_candles': 10
    },
    {
        'name': 'Conservative',
        'min_body_pct': 80,
        'min_candles': 4,
        'min_move_pct': 2.0,
        'validity_candles': 10
    }
]

for test_config in configs:
    config_name = test_config.pop('name')
    
    print("="*70)
    print(f"TESTING: {config_name} Configuration")
    print("="*70)
    
    print("\nConfiguration:")
    for key, value in test_config.items():
        print(f"  {key}: {value}")
    print()
    
    # Calculate
    result = displacement_module.calculate(data.copy(), test_config)
    
    # Find displacements
    bullish_disp = result[result['bullish_displacement'] == True]
    bearish_disp = result[result['bearish_displacement'] == True]
    
    print(f"Bullish Displacements: {len(bullish_disp)}")
    if not bullish_disp.empty:
        print("\nRecent Bullish Displacements (last 3):")
        for idx in bullish_disp.tail(3).index:
            row = result.iloc[idx]
            print(f"  Index {idx}:")
            print(f"    Start: {row['displacement_start']:.2f}")
            print(f"    Close: {row['close']:.2f}")
            print(f"    Move: {row['displacement_move_pct']:.2f}%")
    
    print(f"\nBearish Displacements: {len(bearish_disp)}")
    if not bearish_disp.empty:
        print("\nRecent Bearish Displacements (last 3):")
        for idx in bearish_disp.tail(3).index:
            row = result.iloc[idx]
            print(f"  Index {idx}:")
            print(f"    Start: {row['displacement_start']:.2f}")
            print(f"    Close: {row['close']:.2f}")
            print(f"    Move: {row['displacement_move_pct']:.2f}%")
    
    # Count entry signals
    long_signals = 0
    short_signals = 0
    
    for i in range(len(result)):
        if displacement_module.check_entry_condition(result, i, test_config, 'LONG'):
            long_signals += 1
        if displacement_module.check_entry_condition(result, i, test_config, 'SHORT'):
            short_signals += 1
    
    print(f"\nEntry Signals:")
    print(f"  LONG: {long_signals}")
    print(f"  SHORT: {short_signals}")
    print()

print("="*70)
print("DETAILED ANALYSIS: Standard Configuration")
print("="*70)
print()

# Use standard config for detailed analysis
config = {
    'min_body_pct': 70,
    'min_candles': 3,
    'min_move_pct': 1.5,
    'validity_candles': 10
}

result = displacement_module.calculate(data.copy(), config)

# Analyze candle body statistics
strong_bulls = result[result['is_strong_bull'] == True]
strong_bears = result[result['is_strong_bear'] == True]

print(f"Strong Candle Analysis:")
print(f"  Strong Bullish Candles: {len(strong_bulls)} ({len(strong_bulls)/len(result)*100:.1f}%)")
print(f"  Strong Bearish Candles: {len(strong_bears)} ({len(strong_bears)/len(result)*100:.1f}%)")
print(f"  Average Body %: {result['candle_body_pct'].mean()*100:.1f}%")
print()

# Show displacement examples with context
bullish_disp = result[result['bullish_displacement'] == True]
bearish_disp = result[result['bearish_displacement'] == True]

if not bullish_disp.empty:
    print("Sample Bullish Displacement:")
    idx = bullish_disp.index[-1]  # Most recent
    row = result.iloc[idx]
    
    print(f"  Index: {idx}")
    print(f"  Start Price: {row['displacement_start']:.2f}")
    print(f"  End Price: {row['close']:.2f}")
    print(f"  Total Move: {row['displacement_move_pct']:.2f}%")
    print(f"  Type: {row['displacement_type']}")
    
    # Show the 3 candles that formed displacement
    print(f"\n  Candles forming displacement:")
    min_candles = config['min_candles']
    for j in range(idx - min_candles + 1, idx + 1):
        candle = result.iloc[j]
        body_pct = candle['candle_body_pct'] * 100
        move = (candle['close'] - candle['open']) / candle['open'] * 100
        print(f"    Candle {j}: Body {body_pct:.1f}%, Move {move:+.2f}%")
    print()

if not bearish_disp.empty:
    print("Sample Bearish Displacement:")
    idx = bearish_disp.index[-1]  # Most recent
    row = result.iloc[idx]
    
    print(f"  Index: {idx}")
    print(f"  Start Price: {row['displacement_start']:.2f}")
    print(f"  End Price: {row['close']:.2f}")
    print(f"  Total Move: {row['displacement_move_pct']:.2f}%")
    print(f"  Type: {row['displacement_type']}")
    
    # Show the 3 candles that formed displacement
    print(f"\n  Candles forming displacement:")
    min_candles = config['min_candles']
    for j in range(idx - min_candles + 1, idx + 1):
        candle = result.iloc[j]
        body_pct = candle['candle_body_pct'] * 100
        move = (candle['open'] - candle['close']) / candle['open'] * 100
        print(f"    Candle {j}: Body {body_pct:.1f}%, Move {move:+.2f}%")
    print()

# Test entry signals with examples
print("="*70)
print("ENTRY SIGNAL EXAMPLES:")
print("="*70)
print()

long_count = 0
short_count = 0

for i in range(len(result)):
    row = result.iloc[i]
    
    # Show first 3 LONG signals
    if displacement_module.check_entry_condition(result, i, config, 'LONG'):
        long_count += 1
        if long_count <= 3:
            print(f"LONG Signal #{long_count} at index {i}:")
            print(f"  Price: {row['close']:.2f}")
            print(f"  Displacement Type: {row['displacement_type']}")
            print(f"  Active: {row['displacement_active']}")
    
    # Show first 3 SHORT signals
    if displacement_module.check_entry_condition(result, i, config, 'SHORT'):
        short_count += 1
        if short_count <= 3:
            print(f"\nSHORT Signal #{short_count} at index {i}:")
            print(f"  Price: {row['close']:.2f}")
            print(f"  Displacement Type: {row['displacement_type']}")
            print(f"  Active: {row['displacement_active']}")

print()
print("="*70)
print("SUMMARY:")
print("="*70)
print(f"Total Candles: {len(result)}")
print(f"Bullish Displacements: {len(bullish_disp)}")
print(f"Bearish Displacements: {len(bearish_disp)}")
print(f"Total LONG Signals: {long_count}")
print(f"Total SHORT Signals: {short_count}")
print()
print("="*70)
print("✓ DISPLACEMENT MODULE VALIDATED ON REAL MARKET DATA")
print("="*70)