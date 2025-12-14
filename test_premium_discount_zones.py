# test_premium_discount_zones.py
"""Test Premium/Discount Zones module"""

import pandas as pd
import numpy as np
from core.strategy_modules.ict.premium_discount_zones import PremiumDiscountZonesModule

print("="*70)
print("PREMIUM/DISCOUNT ZONES MODULE TEST")
print("="*70)
print()

# Create test data with clear range pattern:
# Candles 0-29: Establish range (low 95, high 105)
# Candle 30: Price in discount zone (97)
# Candle 35: Price in premium zone (103)
# Candle 40: Price in extreme discount (96)

data_list = []

# Establish range (95-105)
np.random.seed(42)
for i in range(30):
    base = 100
    data_list.append({
        'open': base + np.random.uniform(-4, 4),
        'high': base + np.random.uniform(-3, 5),
        'low': base + np.random.uniform(-5, 3),
        'close': base + np.random.uniform(-4, 4)
    })

# Set clear range boundaries
data_list[5] = {'open': 100, 'high': 105, 'low': 100, 'close': 102}  # High
data_list[15] = {'open': 97, 'high': 98, 'low': 95, 'close': 96}    # Low

# Candle 30: Discount zone (97)
data_list.append({'open': 98, 'high': 99, 'low': 96.5, 'close': 97})

# Candles 31-34: Mid-range
for i in range(4):
    data_list.append({'open': 100, 'high': 101, 'low': 99, 'close': 100})

# Candle 35: Premium zone (103)
data_list.append({'open': 102, 'high': 104, 'low': 102, 'close': 103})

# Candles 36-39: Mid-range
for i in range(4):
    data_list.append({'open': 100, 'high': 101, 'low': 99, 'close': 100})

# Candle 40: Extreme discount (96)
data_list.append({'open': 97, 'high': 98, 'low': 95.5, 'close': 96})

data = pd.DataFrame(data_list)

print("Test Data Pattern:")
print("  Candles 0-29: Range established (95-105)")
print("  Candle 30: Discount zone (97)")
print("  Candle 35: Premium zone (103)")
print("  Candle 40: Extreme discount (96)")
print()

# Instantiate module
pd_module = PremiumDiscountZonesModule()

print("Module Configuration:")
config = {
    'lookback_candles': 25,        # Look back 25 candles for range
    'extreme_threshold_pct': 25    # Top/bottom 25% = extreme zones
}

for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Calculate
result = pd_module.calculate(data.copy(), config)

print("="*70)
print("RESULTS:")
print("="*70)
print()

# Show key candles
key_candles = [29, 30, 35, 40]
display_cols = ['close', 'range_high', 'range_low', 'equilibrium', 'price_position_pct', 'zone']

print("Key candles analysis:")
print(result.iloc[key_candles][display_cols])
print()

# Analyze zones
print("Zone Distribution:")
zone_counts = result['zone'].value_counts()
for zone, count in zone_counts.items():
    if zone:
        print(f"  {zone}: {count} candles")
print()

# Check specific conditions
discount_candles = result[result['in_discount'] == True]
premium_candles = result[result['in_premium'] == True]
extreme_discount = result[result['in_extreme_discount'] == True]
extreme_premium = result[result['in_extreme_premium'] == True]

print(f"Discount zone candles: {len(discount_candles)}")
print(f"Premium zone candles: {len(premium_candles)}")
print(f"Extreme discount candles: {len(extreme_discount)}")
print(f"Extreme premium candles: {len(extreme_premium)}")
print()

# Show candle 30 details (should be in discount)
if 30 < len(result):
    print("Candle 30 Analysis (Expected: Discount):")
    c30 = result.iloc[30]
    print(f"  Close: {c30['close']:.2f}")
    print(f"  Range: {c30['range_low']:.2f} - {c30['range_high']:.2f}")
    print(f"  Equilibrium: {c30['equilibrium']:.2f}")
    print(f"  Price Position: {c30['price_position_pct']:.1f}%")
    print(f"  Zone: {c30['zone']}")
    print(f"  In Discount: {c30['in_discount']}")
    print()

# Show candle 35 details (should be in premium)
if 35 < len(result):
    print("Candle 35 Analysis (Expected: Premium):")
    c35 = result.iloc[35]
    print(f"  Close: {c35['close']:.2f}")
    print(f"  Range: {c35['range_low']:.2f} - {c35['range_high']:.2f}")
    print(f"  Equilibrium: {c35['equilibrium']:.2f}")
    print(f"  Price Position: {c35['price_position_pct']:.1f}%")
    print(f"  Zone: {c35['zone']}")
    print(f"  In Premium: {c35['in_premium']}")
    print()

# Test entry signals
print("="*70)
print("ENTRY SIGNAL TESTS:")
print("="*70)
print()

long_signals = []
short_signals = []

for i in range(len(result)):
    long_signal = pd_module.check_entry_condition(result, i, config, 'LONG')
    short_signal = pd_module.check_entry_condition(result, i, config, 'SHORT')
    
    if long_signal and i in key_candles:
        long_signals.append(i)
        print(f"  Candle {i}: LONG signal (in discount zone)")
    if short_signal and i in key_candles:
        short_signals.append(i)
        print(f"  Candle {i}: SHORT signal (in premium zone)")

print()
print(f"Total LONG signals (discount zone): {len([i for i in range(len(result)) if pd_module.check_entry_condition(result, i, config, 'LONG')])}")
print(f"Total SHORT signals (premium zone): {len([i for i in range(len(result)) if pd_module.check_entry_condition(result, i, config, 'SHORT')])}")

print()
print("="*70)
print("TEST COMPLETE")
print("="*70)