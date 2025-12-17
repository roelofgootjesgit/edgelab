"""
test_batch3.py
==============

Test all 10 indicators from Batch 3

Indicators tested:
1. Standard Deviation (volatility)
2. Historical Volatility (volatility)
3. OBV (volume)
4. VWAP (volume)
5. A/D Line (volume)
6. CMF (volume)
7. Pivot Points (support_resistance)
8. Fibonacci (support_resistance)
9. S/R Zones (support_resistance)
10. Camarilla Pivots (support_resistance)

Usage:
    python test_batch3.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core.data_manager import DataManager
from datetime import datetime, timedelta
import pandas as pd


def load_data():
    """Load real XAUUSD data once for all tests"""
    print("\n" + "="*70)
    print("  LOADING MARKET DATA")
    print("="*70)
    
    dm = DataManager()
    end = datetime.now()
    start = end - timedelta(days=60)
    
    data = dm.get_data(
        symbol='XAUUSD',
        timeframe='15m',
        start=start,
        end=end
    )
    
    print(f"Loaded {len(data)} candles from {start.date()} to {end.date()}")
    return data


def test_indicator(module_class, name, category, config=None):
    """Test a single indicator"""
    print(f"\n[{name}]")
    print(f"  Category: {category}")
    
    try:
        data = load_data()
        module = module_class()
        
        if config is None:
            schema = module.get_config_schema()
            config = {}
            for field in schema.get('fields', []):
                config[field['name']] = field['default']
        
        print(f"  Config: {config}")
        
        result = module.calculate(data.copy(), config)
        print(f"  Result shape: {result.shape}")
        
        original_cols = set(data.columns)
        new_cols = [col for col in result.columns if col not in original_cols and col != 'timestamp']
        print(f"  Columns added: {new_cols}")
        
        for col in new_cols:
            non_nan = result[col].notna().sum()
            print(f"    {col}: {non_nan}/{len(result)} valid values")
        
        long_signals = 0
        short_signals = 0
        
        for i in range(len(result)):
            if module.check_entry_condition(result, i, config, 'LONG'):
                long_signals += 1
            if module.check_entry_condition(result, i, config, 'SHORT'):
                short_signals += 1
        
        print(f"  Entry signals: {long_signals} LONG, {short_signals} SHORT")
        
        assert len(result) == len(data), "Row count mismatch"
        assert all(col in result.columns for col in new_cols), "Missing indicator columns"
        
        print(f"  ✓ PASS")
        return True
        
    except Exception as e:
        print(f"  ✗ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Batch 3 tests"""
    
    print("\n" + "="*70)
    print("  QUANTMETRICS BATCH 3 TEST SUITE")
    print("  Testing 10 indicators (21-30)")
    print("="*70)
    
    results = {}
    
    # Volatility (2)
    from core.strategy_modules.volatility.standard_deviation import StandardDeviationModule
    results['Standard Deviation'] = test_indicator(
        StandardDeviationModule, 'Standard Deviation', 'volatility'
    )
    
    from core.strategy_modules.volatility.historical_volatility import HistoricalVolatilityModule
    results['Historical Volatility'] = test_indicator(
        HistoricalVolatilityModule, 'Historical Volatility', 'volatility'
    )
    
    # Volume (4)
    from core.strategy_modules.volume.obv import OBVModule
    results['OBV'] = test_indicator(OBVModule, 'OBV', 'volume')
    
    from core.strategy_modules.volume.vwap import VWAPModule
    results['VWAP'] = test_indicator(VWAPModule, 'VWAP', 'volume')
    
    from core.strategy_modules.volume.ad_line import ADLineModule
    results['A/D Line'] = test_indicator(ADLineModule, 'A/D Line', 'volume')
    
    from core.strategy_modules.volume.cmf import CMFModule
    results['CMF'] = test_indicator(CMFModule, 'CMF', 'volume')
    
    # Support/Resistance (4)
    from core.strategy_modules.support_resistance.pivot_points import PivotPointsModule
    results['Pivot Points'] = test_indicator(
        PivotPointsModule, 'Pivot Points', 'support_resistance'
    )
    
    from core.strategy_modules.support_resistance.fibonacci import FibonacciModule
    results['Fibonacci'] = test_indicator(
        FibonacciModule, 'Fibonacci', 'support_resistance'
    )
    
    from core.strategy_modules.support_resistance.sr_zones import SRZonesModule
    results['S/R Zones'] = test_indicator(
        SRZonesModule, 'S/R Zones', 'support_resistance'
    )
    
    from core.strategy_modules.support_resistance.camarilla import CamarillaModule
    results['Camarilla'] = test_indicator(
        CamarillaModule, 'Camarilla Pivots', 'support_resistance'
    )
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name:25s} {status}")
    
    print(f"\n  Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n  🎉 ALL TESTS PASSED!")
    else:
        print(f"\n  ⚠️  {failed} TEST(S) FAILED")
    
    print("="*70)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)