# test_breaker_blocks.py
"""Test Breaker Blocks module"""

import pandas as pd
from core.strategy_modules.ict.breaker_blocks import BreakerBlockModule

print("="*70)
print("BREAKER BLOCKS MODULE TEST")
print("="*70)
print()

# Create test data with clear breaker pattern:
# Candles 0-3: Uptrend
# Candle 3: Bullish OB (last green before drop)
# Candles 4-7: Drop (creates bullish OB)
# Candle 10: Break below OB (converts to bearish breaker)
# Candle 15: Price returns to breaker zone

data = pd.DataFrame({
    'open':  [100, 101, 102, 103, 103, 100,  97,  95,  96,  98, 100, 102, 101, 100,  99,  98, 101, 100],
    'high':  [101, 102, 103, 104, 103, 101,  98,  96,  97,  99, 101, 103, 102, 101, 100,  99, 102, 101],
    'low':   [ 99, 100, 101, 102,  99,  97,  95,  93,  95,  97,  99, 101, 100,  99,  98,  97, 100,  99],
    'close': [101, 102, 103, 104, 100,  98,  96,  94,  96,  98, 100, 102, 101, 100,  99,  98, 101, 100],
})

print("Test Data Pattern:")
print("  Candles 0-3: Uptrend (bullish)")
print("  Candle 3: Last green candle (OB candidate)")
print("  Candles 4-7: Strong drop (creates bullish OB)")
print("  Candle 10: Price rallies, breaks above OB")
print("  Candle 15: Price returns to breaker zone")
print()
print(data[['open', 'high', 'low', 'close']])
print()

# Instantiate module
breaker_module = BreakerBlockModule()

print("Module Configuration:")
config = {
    'min_candles': 3,
    'min_move_pct': 3.0,
    'break_confirmation_pct': 1.0,
    'breaker_validity_candles': 50
}

for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Calculate
result = breaker_module.calculate(data.copy(), config)

print("="*70)
print("RESULTS:")
print("="*70)
print()

# Show relevant columns
display_cols = ['close', 'bullish_ob', 'bearish_ob', 'bullish_breaker', 'bearish_breaker', 
                'in_bullish_breaker', 'in_bearish_breaker']
print(result[display_cols])
print()

# Check for order blocks
bullish_obs = result[result['bullish_ob'] == True]
bearish_obs = result[result['bearish_ob'] == True]

if not bullish_obs.empty:
    print("BULLISH ORDER BLOCKS DETECTED:")
    for idx in bullish_obs.index:
        ob_low = bullish_obs.loc[idx, 'ob_low']
        ob_high = bullish_obs.loc[idx, 'ob_high']
        print(f"  Candle {idx}: Zone [{ob_low:.2f} - {ob_high:.2f}]")
    print()

if not bearish_obs.empty:
    print("BEARISH ORDER BLOCKS DETECTED:")
    for idx in bearish_obs.index:
        ob_low = bearish_obs.loc[idx, 'ob_low']
        ob_high = bearish_obs.loc[idx, 'ob_high']
        print(f"  Candle {idx}: Zone [{ob_low:.2f} - {ob_high:.2f}]")
    print()

# Check for breakers
bullish_breakers = result[result['bullish_breaker'] == True]
bearish_breakers = result[result['bearish_breaker'] == True]

if not bullish_breakers.empty:
    print("BULLISH BREAKERS DETECTED (failed bearish OB):")
    for idx in bullish_breakers.index:
        breaker_low = bullish_breakers.loc[idx, 'breaker_low']
        breaker_high = bullish_breakers.loc[idx, 'breaker_high']
        print(f"  Candle {idx}: Zone [{breaker_low:.2f} - {breaker_high:.2f}]")
        print(f"    (Former bearish OB converted to support)")
    print()
else:
    print("No bullish breakers detected")
    print()

if not bearish_breakers.empty:
    print("BEARISH BREAKERS DETECTED (failed bullish OB):")
    for idx in bearish_breakers.index:
        breaker_low = bearish_breakers.loc[idx, 'breaker_low']
        breaker_high = bearish_breakers.loc[idx, 'breaker_high']
        print(f"  Candle {idx}: Zone [{breaker_low:.2f} - {breaker_high:.2f}]")
        print(f"    (Former bullish OB converted to resistance)")
    print()
else:
    print("No bearish breakers detected")
    print()

# Check price in breaker zones
in_bullish_breaker = result[result['in_bullish_breaker'] == True]
in_bearish_breaker = result[result['in_bearish_breaker'] == True]

if not in_bullish_breaker.empty:
    print("PRICE IN BULLISH BREAKER ZONE:")
    for idx in in_bullish_breaker.index:
        price = result.iloc[idx]['close']
        low = result.iloc[idx]['breaker_low']
        high = result.iloc[idx]['breaker_high']
        print(f"  Candle {idx}: Price {price:.2f} in zone [{low:.2f} - {high:.2f}]")
    print()

if not in_bearish_breaker.empty:
    print("PRICE IN BEARISH BREAKER ZONE:")
    for idx in in_bearish_breaker.index:
        price = result.iloc[idx]['close']
        low = result.iloc[idx]['breaker_low']
        high = result.iloc[idx]['breaker_high']
        print(f"  Candle {idx}: Price {price:.2f} in zone [{low:.2f} - {high:.2f}]")
    print()

# Test entry signals
print("="*70)
print("ENTRY SIGNAL TESTS:")
print("="*70)
print()

for i in range(len(result)):
    long_signal = breaker_module.check_entry_condition(result, i, config, 'LONG')
    short_signal = breaker_module.check_entry_condition(result, i, config, 'SHORT')
    
    if long_signal:
        print(f"  Candle {i}: LONG signal (in bullish breaker)")
    if short_signal:
        print(f"  Candle {i}: SHORT signal (in bearish breaker)")

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)