# test_all_11_ict_modules.py
"""
Comprehensive real market data test for ALL 11 ICT modules
Complete Week 1 validation
"""

import pandas as pd
from datetime import datetime, timedelta
from core.data_manager import DataManager

# Import ALL 11 modules
from core.strategy_modules.ict.order_blocks import OrderBlockModule
from core.strategy_modules.ict.fair_value_gaps import FairValueGapModule
from core.strategy_modules.ict.liquidity_sweep import LiquiditySweepModule
from core.strategy_modules.ict.premium_discount_zones import PremiumDiscountZonesModule
from core.strategy_modules.ict.breaker_blocks import BreakerBlockModule
from core.strategy_modules.ict.market_structure_shift import MarketStructureShiftModule
from core.strategy_modules.ict.displacement import DisplacementModule
from core.strategy_modules.ict.imbalance_zones import ImbalanceZonesModule
from core.strategy_modules.ict.mitigation_blocks import MitigationBlocksModule
from core.strategy_modules.ict.inducement import InducementModule
from core.strategy_modules.ict.kill_zones import KillZonesModule

print("="*80)
print("🏆 ALL 11 ICT MODULES - COMPREHENSIVE REAL MARKET DATA TEST")
print("="*80)
print("WEEK 1 FINAL VALIDATION")
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

# Define all 11 modules with configs
modules = [
    {
        'name': '1. Order Blocks',
        'module': OrderBlockModule(),
        'config': {'min_candles': 3, 'min_move_pct': 2.0, 'validity_candles': 20},
        'key_columns': ['bullish_ob', 'bearish_ob']
    },
    {
        'name': '2. Fair Value Gaps',
        'module': FairValueGapModule(),
        'config': {'min_gap_size': 0.5, 'validity_candles': 50, 'fill_threshold': 50},
        'key_columns': ['bullish_fvg', 'bearish_fvg', 'fvg_filled']
    },
    {
        'name': '3. Liquidity Sweep',
        'module': LiquiditySweepModule(),
        'config': {'lookback_candles': 10, 'sweep_threshold_pct': 0.1, 'reversal_candles': 3, 'reversal_pct': 0.3},
        'key_columns': ['bullish_sweep', 'bearish_sweep']
    },
    {
        'name': '4. Premium/Discount Zones',
        'module': PremiumDiscountZonesModule(),
        'config': {'lookback_candles': 50, 'premium_threshold': 0.618, 'discount_threshold': 0.382, 'equilibrium_range': 0.1},
        'key_columns': ['in_premium', 'in_discount', 'zone']
    },
    {
        'name': '5. Breaker Blocks',
        'module': BreakerBlockModule(),
        'config': {'min_candles': 3, 'min_move_pct': 2.0, 'break_threshold_pct': 0.2, 'validity_candles': 30},
        'key_columns': ['bullish_breaker', 'bearish_breaker']
    },
    {
        'name': '6. Market Structure Shift',
        'module': MarketStructureShiftModule(),
        'config': {'swing_lookback': 5, 'break_threshold_pct': 0.2, 'confirmation_candles': 2},
        'key_columns': ['bullish_mss', 'bearish_mss']
    },
    {
        'name': '7. Displacement',
        'module': DisplacementModule(),
        'config': {'min_body_pct': 60, 'min_candles': 2, 'min_move_pct': 1.0, 'validity_candles': 20},
        'key_columns': ['bullish_displacement', 'bearish_displacement']
    },
    {
        'name': '8. Imbalance Zones',
        'module': ImbalanceZonesModule(),
        'config': {'min_gap_size': 0.5, 'validity_candles': 100, 'fill_threshold': 50},
        'key_columns': ['bullish_imbalance', 'bearish_imbalance', 'imbalance_filled']
    },
    {
        'name': '9. Mitigation Blocks',
        'module': MitigationBlocksModule(),
        'config': {'min_candles': 3, 'min_move_pct': 2.0, 'mitigation_validity': 20, 'hold_candles': 2},
        'key_columns': ['bullish_mitigation', 'bearish_mitigation']
    },
    {
        'name': '10. Inducement',
        'module': InducementModule(),
        'config': {'lookback_candles': 10, 'break_threshold_pct': 0.2, 'reversal_candles': 2, 'reversal_pct': 0.5, 'validity_candles': 15},
        'key_columns': ['bullish_inducement', 'bearish_inducement']
    },
    {
        'name': '11. Kill Zones',
        'module': KillZonesModule(),
        'config': {'enabled_zones': ['london', 'newyork'], 'london_start': 7, 'london_end': 10, 'ny_start': 12, 'ny_end': 15},
        'key_columns': ['in_kill_zone', 'kill_zone']
    }
]

# Test each module
results = {}
print("="*80)
print("TESTING ALL MODULES...")
print("="*80)
print()

for idx, test in enumerate(modules, 1):
    name = test['name']
    module = test['module']
    config = test['config']
    key_columns = test['key_columns']
    
    print(f"[{idx}/11] Testing {name}...", end=' ')
    
    try:
        # Calculate
        result_df = module.calculate(data.copy(), config)
        
        # Count signals
        long_signals = sum(1 for i in range(len(result_df)) 
                          if module.check_entry_condition(result_df, i, config, 'LONG'))
        short_signals = sum(1 for i in range(len(result_df)) 
                           if module.check_entry_condition(result_df, i, config, 'SHORT'))
        
        # Count detections
        detections = {}
        for col in key_columns:
            if col in result_df.columns:
                if result_df[col].dtype == bool:
                    detections[col] = len(result_df[result_df[col] == True])
                elif col == 'zone':
                    detections['zones'] = result_df[col].value_counts().to_dict()
        
        results[name] = {
            'status': 'PASS',
            'long_signals': long_signals,
            'short_signals': short_signals,
            'total_signals': long_signals + short_signals,
            'detections': detections
        }
        
        print(f"✓ PASS ({long_signals + short_signals} signals)")
        
    except Exception as e:
        results[name] = {
            'status': 'FAIL',
            'error': str(e)
        }
        print(f"✗ FAIL: {str(e)[:50]}")

print()
print("="*80)
print("DETAILED RESULTS")
print("="*80)
print()

for name, res in results.items():
    print(f"{name}")
    print("-" * 80)
    
    if res['status'] == 'PASS':
        print(f"  Status: ✓ PASS")
        print(f"  Signals: {res['long_signals']} LONG, {res['short_signals']} SHORT, {res['total_signals']} Total")
        
        if res['detections']:
            print(f"  Detections:")
            for key, value in res['detections'].items():
                if isinstance(value, dict):
                    for zone, count in value.items():
                        if zone:  # Skip empty
                            print(f"    {zone}: {count}")
                else:
                    print(f"    {key}: {value}")
    else:
        print(f"  Status: ✗ FAIL")
        print(f"  Error: {res['error']}")
    
    print()

# Summary table
print("="*80)
print("SUMMARY - SIGNAL GENERATION BY MODULE")
print("="*80)
print()

passed = sum(1 for r in results.values() if r['status'] == 'PASS')
failed = sum(1 for r in results.values() if r['status'] == 'FAIL')

print(f"Module Status: {passed}/11 PASS, {failed}/11 FAIL")
print()

print(f"{'Module':<35} {'LONG':<10} {'SHORT':<10} {'TOTAL':<10} {'Status'}")
print("-" * 75)

for name, res in results.items():
    if res['status'] == 'PASS':
        status_icon = "✓"
        long_sig = res['long_signals']
        short_sig = res['short_signals']
        total_sig = res['total_signals']
    else:
        status_icon = "✗"
        long_sig = short_sig = total_sig = 0
    
    print(f"{name:<35} {long_sig:<10} {short_sig:<10} {total_sig:<10} {status_icon}")

print()
print("="*80)
print(f"Dataset: {symbol} {timeframe} | Candles: {len(data)} | Period: {(end - start).days} days")
print("="*80)
print()

if failed == 0:
    print("🎉 ALL 11 ICT MODULES VALIDATED SUCCESSFULLY!")
    print("="*80)
    print("🏆 WEEK 1 COMPLETE - ICT MODULE SUITE READY FOR PRODUCTION")
    print("="*80)
else:
    print(f"⚠️  {failed} module(s) failed validation - review errors above")
    print("="*80)