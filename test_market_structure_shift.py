# test_market_structure_shift.py
"""Test Market Structure Shift module"""

import pandas as pd
from core.strategy_modules.ict.market_structure_shift import MarketStructureShiftModule

print("="*70)
print("MARKET STRUCTURE SHIFT MODULE TEST")
print("="*70)
print()

# Create test data with clear MSS pattern:
# Candles 0-10: Downtrend with swing high at candle 5
# Candle 12: Break above swing high (bullish MSS)
# Candles 15-25: Uptrend with swing low at candle 20
# Candle 27: Break below swing low (bearish MSS)

data = pd.DataFrame({
    'open':  [105, 104, 103, 102, 101, 103, 102, 101, 100,  99,  98,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 107, 106, 105, 104, 103, 102, 101, 100,  99],
    'high':  [106, 105, 104, 103, 102, 104, 103, 102, 101, 100,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100],
    'low':   [104, 103, 102, 101, 100, 102, 101, 100,  99,  98,  97,  98,  99, 100, 101, 102, 103, 104, 105, 106, 107, 106, 105, 104, 103, 102, 101, 100,  99,  98],
    'close': [104, 103, 102, 101, 100, 102, 101, 100,  99,  98,  97,  99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 107, 106, 105, 104, 103, 102, 101, 100,  99],
})

print("Test Data Pattern:")
print("  Candles 0-10: Downtrend (swing high expected around candle 5)")
print("  Candle 12: Break above swing high (bullish MSS)")
print("  Candles 15-25: Uptrend (swing low expected around candle 20)")
print("  Candle 27: Break below swing low (bearish MSS)")
print()
print("Key candles:")
print(data.iloc[[5, 12, 20, 27]][['open', 'high', 'low', 'close']])
print()

# Instantiate module
mss_module = MarketStructureShiftModule()

print("Module Configuration:")
config = {
    'swing_lookback': 3,          # 3 candles each side for swing detection
    'break_threshold_pct': 0.2,   # 0.2% break confirmation
    'mss_validity_candles': 10    # MSS active for 10 candles
}

for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Calculate
result = mss_module.calculate(data.copy(), config)

print("="*70)
print("RESULTS:")
print("="*70)
print()

# Show swing points
swing_highs = result[result['is_swing_high'] == True]
swing_lows = result[result['is_swing_low'] == True]

print("SWING POINTS DETECTED:")
if not swing_highs.empty:
    print("  Swing Highs:")
    for idx in swing_highs.index:
        print(f"    Candle {idx}: {swing_highs.loc[idx, 'swing_high']:.2f}")

if not swing_lows.empty:
    print("  Swing Lows:")
    for idx in swing_lows.index:
        print(f"    Candle {idx}: {swing_lows.loc[idx, 'swing_low']:.2f}")
print()

# Show MSS events
bullish_mss = result[result['bullish_mss'] == True]
bearish_mss = result[result['bearish_mss'] == True]

if not bullish_mss.empty:
    print("BULLISH MSS DETECTED (structure shift to uptrend):")
    for idx in bullish_mss.index:
        recent_high = result.iloc[idx-1]['recent_swing_high'] if idx > 0 else None
        actual_high = result.iloc[idx]['high']
        print(f"  Candle {idx}:")
        print(f"    Broke above swing high: {recent_high:.2f}")
        print(f"    Actual high: {actual_high:.2f}")
    print()
else:
    print("No bullish MSS detected")
    print()

if not bearish_mss.empty:
    print("BEARISH MSS DETECTED (structure shift to downtrend):")
    for idx in bearish_mss.index:
        recent_low = result.iloc[idx-1]['recent_swing_low'] if idx > 0 else None
        actual_low = result.iloc[idx]['low']
        print(f"  Candle {idx}:")
        print(f"    Broke below swing low: {recent_low:.2f}")
        print(f"    Actual low: {actual_low:.2f}")
    print()
else:
    print("No bearish MSS detected")
    print()

# Show MSS activity window
mss_active = result[result['mss_active'] == True]
if not mss_active.empty:
    print("MSS ACTIVE PERIODS:")
    print(f"  Total candles with active MSS: {len(mss_active)}")
    print(f"  Bullish MSS active: {len(mss_active[mss_active['mss_type'] == 'BULLISH'])}")
    print(f"  Bearish MSS active: {len(mss_active[mss_active['mss_type'] == 'BEARISH'])}")
    print()

# Test entry signals
print("="*70)
print("ENTRY SIGNAL TESTS:")
print("="*70)
print()

long_signals = []
short_signals = []

for i in range(len(result)):
    long_signal = mss_module.check_entry_condition(result, i, config, 'LONG')
    short_signal = mss_module.check_entry_condition(result, i, config, 'SHORT')
    
    if long_signal:
        long_signals.append(i)
    if short_signal:
        short_signals.append(i)

if long_signals:
    print(f"LONG signals detected at candles: {long_signals}")
else:
    print("No LONG signals detected")

if short_signals:
    print(f"SHORT signals detected at candles: {short_signals}")
else:
    print("No SHORT signals detected")

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)