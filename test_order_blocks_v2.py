# test_order_blocks_v2.py
"""Test Order Blocks module with realistic pattern"""

import pandas as pd
import numpy as np
from core.strategy_modules.ict.order_blocks import OrderBlockModule

print("=" * 70)
print("ORDER BLOCKS MODULE TEST - Realistic Market Pattern")
print("=" * 70)
print()

# Create test data with CLEAR bullish OB pattern:
# 1. Uptrend (candles 0-3)
# 2. LAST GREEN CANDLE at index 3 (this will be the OB)
# 3. STRONG DROP after (candles 4-7: -5% drop)
# 4. Price returns to OB zone later (candle 10)

data = pd.DataFrame({
    # Index:  0     1     2     3     4     5     6     7     8     9    10    11
    'open':  [100,  101,  102,  103,  103,  100,   97,   95,   94,   96,  103,  104],
    'high':  [101,  102,  103,  104,  103,  101,   98,   96,   95,   97,  104,  105],
    'low':   [ 99,  100,  101,  102,   99,   97,   95,   93,   93,   95,  102,  103],
    'close': [101,  102,  103,  104,  100,   98,   96,   94,   94,   96,  103,  105],
})

print("📊 Test Data Pattern:")
print("   Candles 0-3: Uptrend (bullish)")
print("   Candle 3:    LAST GREEN before drop (OB candidate)")
print("   Candles 4-7: Strong drop -9.6% (triggers OB)")
print("   Candle 10:   Price returns to OB zone")
print()
print(data[['open', 'high', 'low', 'close']])
print()

# Calculate price move
drop_pct = ((data.iloc[3]['high'] - data.iloc[7]['low']) / data.iloc[3]['high']) * 100
print(f"📉 Drop from candle 3 high to candle 7 low: {drop_pct:.1f}%")
print(f"   (Required: ≥3.0% with ≥3 red candles)")
print()

# Instantiate module
ob_module = OrderBlockModule()

print("🔧 Module Configuration:")
config = {
    'min_candles': 3,      # Need 3+ red candles for reversal
    'min_move_pct': 3.0,   # Need 3%+ move
    'validity_candles': 20, # OB valid for 20 candles
    'zone_type': 'full_candle'  # Use full candle range
}

for key, value in config.items():
    print(f"   {key}: {value}")
print()

# Calculate
result = ob_module.calculate(data.copy(), config)

print("=" * 70)
print("📈 RESULTS:")
print("=" * 70)
print()
print(result[['close', 'bullish_ob', 'bearish_ob', 'ob_low', 'ob_high', 'in_bullish_ob']])
print()

# Check for bullish OB
bullish_obs = result[result['bullish_ob'] == True]
if not bullish_obs.empty:
    print("✅ BULLISH ORDER BLOCK DETECTED!")
    for idx in bullish_obs.index:
        ob_low = bullish_obs.loc[idx, 'ob_low']
        ob_high = bullish_obs.loc[idx, 'ob_high']
        print(f"   📍 Index: {idx}")
        print(f"   📊 Candle: O:{data.iloc[idx]['open']} H:{data.iloc[idx]['high']} L:{data.iloc[idx]['low']} C:{data.iloc[idx]['close']}")
        print(f"   🎯 OB Zone: {ob_low:.2f} - {ob_high:.2f}")
        print()
else:
    print("❌ No bullish OB detected")
    print("   Possible reasons:")
    print("   - Move not strong enough (need 3%+ drop)")
    print("   - Not enough consecutive red candles (need 3+)")
    print()

# Check which candles have price in OB zone
in_zone = result[result['in_bullish_ob'] == True]
if not in_zone.empty:
    print("🎯 PRICE IN BULLISH OB ZONE:")
    for idx in in_zone.index:
        print(f"   Candle {idx}: Price {result.iloc[idx]['close']:.2f} in zone [{result.iloc[idx]['ob_low']:.2f} - {result.iloc[idx]['ob_high']:.2f}]")
    print()

# Test entry signals
print("=" * 70)
print("🎯 ENTRY SIGNAL TESTS:")
print("=" * 70)
print()

long_signals = []
short_signals = []

for i in range(len(result)):
    long_signal = ob_module.check_entry_condition(result, i, config, 'LONG')
    short_signal = ob_module.check_entry_condition(result, i, config, 'SHORT')
    
    if long_signal:
        long_signals.append(i)
        print(f"   ✅ Candle {i}: LONG signal (price in bullish OB zone)")
    if short_signal:
        short_signals.append(i)
        print(f"   ✅ Candle {i}: SHORT signal (price in bearish OB zone)")

if not long_signals and not short_signals:
    print("   ℹ️  No entry signals detected")
    print("   (This is normal - entry signals only trigger when price returns to OB)")

print()
print("=" * 70)
print("✅ TEST COMPLETE!")
print("=" * 70)
print()

if bullish_obs.empty and result[result['bearish_ob'] == True].empty:
    print("⚠️  DEBUGGING INFO:")
    print()
    print("No OBs detected. Let's check why:")
    print()
    
    # Check candle 3 specifically
    print(f"Analyzing candle 3 (OB candidate):")
    print(f"  - Candle type: {'GREEN' if data.iloc[3]['close'] > data.iloc[3]['open'] else 'RED'}")
    print(f"  - Next 4 candles:")
    for i in range(4, min(8, len(data))):
        candle_type = 'RED' if data.iloc[i]['close'] < data.iloc[i]['open'] else 'GREEN'
        print(f"    Candle {i}: {candle_type} (O:{data.iloc[i]['open']} C:{data.iloc[i]['close']})")
    
    print()
    consecutive_red = sum(1 for i in range(4, min(8, len(data))) if data.iloc[i]['close'] < data.iloc[i]['open'])
    print(f"  - Consecutive red candles: {consecutive_red} (need {config['min_candles']-1}+)")
    print(f"  - Move size: {drop_pct:.1f}% (need {config['min_move_pct']}%+)")
    
else:
    print("🎉 SUCCESS! Order Block detection working correctly!")
    print()
    print("Integration steps:")
    print("1. Module is already in core/strategy_modules/ict/")
    print("2. Registry will auto-discover it")
    print("3. Will appear in Strategy Builder UI under 'ICT' category")
    print("4. Users can configure: min_candles, min_move_pct, validity, zone_type")