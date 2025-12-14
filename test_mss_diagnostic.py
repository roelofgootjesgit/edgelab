# test_mss_diagnostic.py
"""Diagnostic test to understand MSS detection on real data"""

import pandas as pd
from datetime import datetime, timedelta
from core.strategy_modules.ict.market_structure_shift import MarketStructureShiftModule
from core.data_manager import DataManager

print("="*70)
print("MSS DIAGNOSTIC TEST")
print("="*70)
print()

# Fetch data
data_manager = DataManager()
symbol = 'XAUUSD'
timeframe = '1h'
end = datetime.now()
start = end - timedelta(days=30)

data = data_manager.get_data(symbol=symbol, timeframe=timeframe, start=start, end=end)

print(f"Data loaded: {len(data)} candles")
print(f"Price range: {data['low'].min():.2f} - {data['high'].max():.2f}")
print()

# Test with different thresholds
thresholds = [0.1, 0.2, 0.3, 0.5]

for threshold in thresholds:
    print(f"Testing with break_threshold_pct = {threshold}%")
    
    mss_module = MarketStructureShiftModule()
    config = {
        'swing_lookback': 5,
        'break_threshold_pct': threshold,
        'mss_validity_candles': 10
    }
    
    result = mss_module.calculate(data.copy(), config)
    
    bullish_mss = result[result['bullish_mss'] == True]
    bearish_mss = result[result['bearish_mss'] == True]
    
    print(f"  Bullish MSS: {len(bullish_mss)}")
    print(f"  Bearish MSS: {len(bearish_mss)}")
    print()

# Detailed analysis with lowest threshold
print("="*70)
print("DETAILED ANALYSIS (0.1% threshold):")
print("="*70)
print()

config = {
    'swing_lookback': 5,
    'break_threshold_pct': 0.1,
    'mss_validity_candles': 10
}

result = mss_module.calculate(data.copy(), config)

# Check swing points and subsequent price action
swing_highs = result[result['is_swing_high'] == True]

if not swing_highs.empty:
    print("Analyzing swing high breaks:")
    print()
    
    for idx in swing_highs.tail(5).index:
        swing_high_value = result.loc[idx, 'swing_high']
        break_level = swing_high_value * (1 + 0.1/100)
        
        print(f"Swing High at index {idx}: {swing_high_value:.2f}")
        print(f"  Break level (0.1%): {break_level:.2f}")
        
        # Check if price broke this level
        future_data = result.loc[idx:]
        breaks = future_data[future_data['high'] >= break_level]
        
        if not breaks.empty:
            first_break = breaks.index[0]
            print(f"  BROKE at index {first_break}: high = {result.loc[first_break, 'high']:.2f}")
        else:
            print(f"  Never broke (max high after = {future_data['high'].max():.2f})")
        print()

print("="*70)
print("DIAGNOSTIC COMPLETE")
print("="*70)