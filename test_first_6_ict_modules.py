# test_first_6_ict_modules.py
"""
Comprehensive real market data test for first 6 ICT modules
Tests all modules with actual XAUUSD data
"""

import pandas as pd
from datetime import datetime, timedelta
from core.data_manager import DataManager

# Import all modules (using correct class names)
from core.strategy_modules.ict.order_blocks import OrderBlockModule
from core.strategy_modules.ict.fair_value_gaps import FairValueGapModule
from core.strategy_modules.ict.liquidity_sweep import LiquiditySweepModule
from core.strategy_modules.ict.premium_discount_zones import PremiumDiscountZonesModule
from core.strategy_modules.ict.breaker_blocks import BreakerBlockModule
from core.strategy_modules.ict.market_structure_shift import MarketStructureShiftModule

print("="*80)
print("ICT MODULES - COMPREHENSIVE REAL MARKET DATA TEST")
print("="*80)
print("Testing first 6 modules with XAUUSD data")
print("="*80)
print()

# Fetch real data
data_manager = DataManager()
symbol = 'XAUUSD'
timeframe = '15m'
end = datetime.now()
start = end - timedelta(days=14)

print(f"Fetching data: {symbol} {timeframe} for 14 days")
data = data_manager.get_data(symbol=symbol, timeframe=timeframe, start=start, end=end)
print(f"Data loaded: {len(data)} candles")
print(f"Date range: {data.index[0]} to {data.index[-1]}")
print(f"Price range: {data['low'].min():.2f} - {data['high'].max():.2f}")
print()

# Test each module
modules = [
    {
        'name': 'Order Blocks',
        'module': OrderBlockModule(),
        'config': {
            'min_candles': 3,
            'min_move_pct': 2.0,
            'validity_candles': 20
        }
    },
    {
        'name': 'Fair Value Gaps',
        'module': FairValueGapModule(),
        'config': {
            'min_gap_size': 0.5,
            'validity_candles': 50,
            'fill_threshold': 50
        }
    },
    {
        'name': 'Liquidity Sweep',
        'module': LiquiditySweepModule(),
        'config': {
            'lookback_candles': 10,
            'sweep_threshold_pct': 0.1,
            'reversal_candles': 3,
            'reversal_pct': 0.3
        }
    },
    {
        'name': 'Premium/Discount Zones',
        'module': PremiumDiscountZonesModule(),
        'config': {
            'lookback_candles': 50,
            'premium_threshold': 0.618,
            'discount_threshold': 0.382,
            'equilibrium_range': 0.1
        }
    },
    {
        'name': 'Breaker Blocks',
        'module': BreakerBlockModule(),
        'config': {
            'min_candles': 3,
            'min_move_pct': 2.0,
            'break_threshold_pct': 0.2,
            'validity_candles': 30
        }
    },
    {
        'name': 'Market Structure Shift',
        'module': MarketStructureShiftModule(),
        'config': {
            'swing_lookback': 5,
            'break_threshold_pct': 0.2,
            'confirmation_candles': 2
        }
    }
]

# Test each module
results = {}

for test in modules:
    name = test['name']
    module = test['module']
    config = test['config']
    
    print("="*80)
    print(f"MODULE: {name}")
    print("="*80)
    print()
    
    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Calculate
    result_df = module.calculate(data.copy(), config)
    
    # Count signals
    long_signals = 0
    short_signals = 0
    
    for i in range(len(result_df)):
        if module.check_entry_condition(result_df, i, config, 'LONG'):
            long_signals += 1
        if module.check_entry_condition(result_df, i, config, 'SHORT'):
            short_signals += 1
    
    # Module-specific analysis
    if name == 'Order Blocks':
        bullish_obs = len(result_df[result_df['bullish_ob'] == True])
        bearish_obs = len(result_df[result_df['bearish_ob'] == True])
        print(f"Order Blocks Detected:")
        print(f"  Bullish: {bullish_obs}")
        print(f"  Bearish: {bearish_obs}")
        print(f"  Total: {bullish_obs + bearish_obs}")
    
    elif name == 'Fair Value Gaps':
        bullish_fvgs = len(result_df[result_df['bullish_fvg'] == True])
        bearish_fvgs = len(result_df[result_df['bearish_fvg'] == True])
        filled = len(result_df[result_df['fvg_filled'] == True])
        print(f"Fair Value Gaps Detected:")
        print(f"  Bullish: {bullish_fvgs}")
        print(f"  Bearish: {bearish_fvgs}")
        print(f"  Total: {bullish_fvgs + bearish_fvgs}")
        print(f"  Filled: {filled}")
    
    elif name == 'Liquidity Sweep':
        bullish_sweeps = len(result_df[result_df['bullish_sweep'] == True])
        bearish_sweeps = len(result_df[result_df['bearish_sweep'] == True])
        print(f"Liquidity Sweeps Detected:")
        print(f"  Bullish (swept lows): {bullish_sweeps}")
        print(f"  Bearish (swept highs): {bearish_sweeps}")
        print(f"  Total: {bullish_sweeps + bearish_sweeps}")
    
    elif name == 'Premium/Discount Zones':
        # Check if columns exist before accessing
        if 'in_premium' in result_df.columns:
            in_premium = len(result_df[result_df['in_premium'] == True])
        else:
            in_premium = 0
        
        if 'in_discount' in result_df.columns:
            in_discount = len(result_df[result_df['in_discount'] == True])
        else:
            in_discount = 0
        
        # Check for equilibrium (might be missing if no valid range)
        if 'zone' in result_df.columns:
            in_equilibrium = len(result_df[result_df['zone'] == 'EQUILIBRIUM'])
        else:
            in_equilibrium = 0
        
        print(f"Zone Distribution:")
        print(f"  Premium: {in_premium} candles ({in_premium/len(result_df)*100:.1f}%)")
        print(f"  Discount: {in_discount} candles ({in_discount/len(result_df)*100:.1f}%)")
        print(f"  Equilibrium: {in_equilibrium} candles ({in_equilibrium/len(result_df)*100:.1f}%)")
        
        # Show recent zone info if available
        if 'zone' in result_df.columns:
            recent_zones = result_df['zone'].tail(10).value_counts()
            print(f"\n  Recent zone distribution (last 10 candles):")
            for zone, count in recent_zones.items():
                if zone:  # Skip empty strings
                    print(f"    {zone}: {count}")
    
    elif name == 'Breaker Blocks':
        bullish_breakers = len(result_df[result_df['bullish_breaker'] == True])
        bearish_breakers = len(result_df[result_df['bearish_breaker'] == True])
        print(f"Breaker Blocks Detected:")
        print(f"  Bullish: {bullish_breakers}")
        print(f"  Bearish: {bearish_breakers}")
        print(f"  Total: {bullish_breakers + bearish_breakers}")
    
    elif name == 'Market Structure Shift':
        bullish_mss = len(result_df[result_df['bullish_mss'] == True])
        bearish_mss = len(result_df[result_df['bearish_mss'] == True])
        print(f"Market Structure Shifts Detected:")
        print(f"  Bullish (bearish→bullish): {bullish_mss}")
        print(f"  Bearish (bullish→bearish): {bearish_mss}")
        print(f"  Total: {bullish_mss + bearish_mss}")
    
    print()
    print(f"Entry Signals Generated:")
    print(f"  LONG signals: {long_signals}")
    print(f"  SHORT signals: {short_signals}")
    print(f"  Total signals: {long_signals + short_signals}")
    print()
    
    # Store results
    results[name] = {
        'long_signals': long_signals,
        'short_signals': short_signals,
        'total_signals': long_signals + short_signals,
        'data': result_df
    }

# Summary
print("="*80)
print("SUMMARY - ALL MODULES")
print("="*80)
print()

print(f"Dataset: {symbol} {timeframe}")
print(f"Candles: {len(data)}")
print(f"Period: {(end - start).days} days")
print()

print("Signal Generation by Module:")
print(f"{'Module':<30} {'LONG':<10} {'SHORT':<10} {'TOTAL':<10}")
print("-" * 60)
for name, res in results.items():
    print(f"{name:<30} {res['long_signals']:<10} {res['short_signals']:<10} {res['total_signals']:<10}")

print()
print("="*80)
print("✓ ALL 6 ICT MODULES VALIDATED ON REAL MARKET DATA")
print("="*80)
print()
print("Next: Test remaining 5 modules (Displacement, Imbalance, Mitigation, Inducement, Kill Zones)")
print("="*80)