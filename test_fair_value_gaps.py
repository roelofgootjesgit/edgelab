# test_fair_value_gaps.py
"""Test Fair Value Gaps module"""

import pandas as pd
from core.strategy_modules.ict.fair_value_gaps import FairValueGapModule

print("="*70)
print("FAIR VALUE GAPS MODULE TEST")
print("="*70)
print()

# Create test data with clear FVG pattern:
# Candles 0-2: Setup
# Candle 3: Gap up (creates bullish FVG between candle 1 high and candle 3 low)
# Candle 7: Price returns to FVG

data = pd.DataFrame({
    'open':  [100, 101, 102, 102, 104, 105, 106, 104, 103, 102],
    'high':  [101, 102, 103, 103, 105, 106, 107, 105, 104, 103],
    'low':   [ 99, 100, 101, 102, 103, 104, 105, 103, 102, 101],
    'close': [101, 102, 103, 102, 104, 105, 106, 104, 103, 102],
})

print("Test Data Pattern:")
print("  Candles 0-2: Normal movement")
print("  Candle 3: Gap up - low[3]=102 > high[1]=102 creates FVG")
print("  Candle 7: Price returns to FVG zone")
print()
print(data[['open', 'high', 'low', 'close']])
print()

# Calculate gap
gap_low = data.iloc[1]['high']
gap_high = data.iloc[3]['low']
gap_size = gap_high - gap_low
gap_pct = (gap_size / gap_low) * 100

print(f"FVG Analysis:")
print(f"  Gap between candle 1 high ({gap_low}) and candle 3 low ({gap_high})")
print(f"  Gap size: {gap_size:.2f} ({gap_pct:.2f}%)")
print()

# Instantiate module
fvg_module = FairValueGapModule()

print("Module Configuration:")
config = {
    'min_gap_pct': 0.1,      # Very low threshold for test
    'validity_candles': 50,
    'fill_threshold': 0.5
}

for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Calculate
result = fvg_module.calculate(data.copy(), config)

print("="*70)
print("RESULTS:")
print("="*70)
print()
print(result[['close', 'bullish_fvg', 'bearish_fvg', 'fvg_low', 'fvg_high', 'in_bullish_fvg']])
print()

# Check for FVGs
bullish_fvgs = result[result['bullish_fvg'] == True]
bearish_fvgs = result[result['bearish_fvg'] == True]

if not bullish_fvgs.empty:
    print("BULLISH FVG DETECTED:")
    for idx in bullish_fvgs.index:
        low = bullish_fvgs.loc[idx, 'fvg_low']
        high = bullish_fvgs.loc[idx, 'fvg_high']
        print(f"  Index {idx}: Zone [{low:.2f} - {high:.2f}]")
    print()
else:
    print("No bullish FVG detected")
    print()

if not bearish_fvgs.empty:
    print("BEARISH FVG DETECTED:")
    for idx in bearish_fvgs.index:
        low = bearish_fvgs.loc[idx, 'fvg_low']
        high = bearish_fvgs.loc[idx, 'fvg_high']
        print(f"  Index {idx}: Zone [{low:.2f} - {high:.2f}]")
    print()
else:
    print("No bearish FVG detected")
    print()

# Check price in FVG
in_fvg = result[result['in_bullish_fvg'] == True]
if not in_fvg.empty:
    print("PRICE IN BULLISH FVG:")
    for idx in in_fvg.index:
        price = result.iloc[idx]['close']
        low = result.iloc[idx]['fvg_low']
        high = result.iloc[idx]['fvg_high']
        print(f"  Candle {idx}: Price {price:.2f} in zone [{low:.2f} - {high:.2f}]")
    print()

# Test entry signals
print("="*70)
print("ENTRY SIGNAL TESTS:")
print("="*70)
print()

for i in range(len(result)):
    long_signal = fvg_module.check_entry_condition(result, i, config, 'LONG')
    short_signal = fvg_module.check_entry_condition(result, i, config, 'SHORT')
    
    if long_signal:
        print(f"  Candle {i}: LONG signal (price in bullish FVG)")
    if short_signal:
        print(f"  Candle {i}: SHORT signal (price in bearish FVG)")

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)