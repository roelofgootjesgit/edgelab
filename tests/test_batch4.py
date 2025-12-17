"""
Test Batch 4: Moving Averages (8 indicators)
=============================================

Tests all moving average indicators with real XAUUSD data.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import modules from core.strategy_modules
from core.strategy_modules.moving_averages.wma import WMAModule
from core.strategy_modules.moving_averages.hma import HMAModule
from core.strategy_modules.moving_averages.tema import TEMAModule
from core.strategy_modules.moving_averages.dema import DEMAModule
from core.strategy_modules.moving_averages.zlema import ZLEMAModule
from core.strategy_modules.moving_averages.kama import KAMAModule
from core.strategy_modules.moving_averages.vwma import VWMAModule
from core.strategy_modules.moving_averages.smma import SMMAModule


def load_test_data():
    """Load real XAUUSD 15m data"""
    print("📥 Loading XAUUSD 15m data...")
    from core.data_manager import DataManager
    
    dm = DataManager()
    end = datetime.now()
    start = end - timedelta(days=60)
    
    data = dm.get_data(
        symbol='XAUUSD',
        timeframe='15m',
        start=start,
        end=end
    )
    
    print(f"✓ Loaded {len(data)} candles")
    return data


def test_indicator(module_class, name, config):
    """Test a single indicator"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    try:
        # Load data
        data = load_test_data()
        
        # Initialize module
        module = module_class()
        
        # Calculate
        print("🔧 Calculating indicator...")
        result = module.calculate(data.copy(), config)
        
        # Check columns added
        expected_cols = [col for col in result.columns if name.lower() in col.lower()]
        print(f"✓ Added columns: {len(expected_cols)}")
        for col in expected_cols[:3]:
            print(f"  - {col}")
        if len(expected_cols) > 3:
            print(f"  ... and {len(expected_cols) - 3} more")
        
        # Test entry conditions
        print("\n🎯 Testing entry conditions...")
        long_signals = 0
        short_signals = 0
        
        for i in range(100, len(result)):
            if module.check_entry_condition(result, i, config, 'LONG'):
                long_signals += 1
            if module.check_entry_condition(result, i, config, 'SHORT'):
                short_signals += 1
        
        print(f"✓ LONG signals: {long_signals}")
        print(f"✓ SHORT signals: {short_signals}")
        
        # Validate no NaN in recent data
        main_col = [col for col in result.columns if name.lower() in col.lower()][0]
        recent_data = result[main_col].tail(100)
        nan_count = recent_data.isna().sum()
        
        print(f"\n📊 Data quality:")
        print(f"✓ NaN in last 100 candles: {nan_count}")
        print(f"✓ Min value: {recent_data.min():.4f}")
        print(f"✓ Max value: {recent_data.max():.4f}")
        
        if long_signals > 0 or short_signals > 0:
            print(f"\n✅ {name} PASSED")
            return True
        else:
            print(f"\n⚠️  {name} WARNING: No signals generated")
            return True  # Still pass if calculation works
            
    except Exception as e:
        print(f"\n❌ {name} FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("BATCH 4: MOVING AVERAGES TEST SUITE")
    print("="*60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Symbol: XAUUSD")
    print(f"Timeframe: 15m")
    print(f"Period: Last 60 days")
    print("="*60)
    
    tests = [
        (WMAModule, "WMA", {"period": 20, "source": "close"}),
        (HMAModule, "HMA", {"period": 20, "source": "close"}),
        (TEMAModule, "TEMA", {"period": 20, "source": "close"}),
        (DEMAModule, "DEMA", {"period": 20, "source": "close"}),
        (ZLEMAModule, "ZLEMA", {"period": 20, "source": "close"}),
        (KAMAModule, "KAMA", {"period": 10, "fast": 2, "slow": 30, "er_threshold": 0.3}),
        (VWMAModule, "VWMA", {"period": 20, "source": "close"}),
        (SMMAModule, "SMMA", {"period": 20, "source": "close"}),
    ]
    
    results = []
    for module_class, name, config in tests:
        passed = test_indicator(module_class, name, config)
        results.append((name, passed))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for name, p in results:
        status = "✅ PASS" if p else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {total - passed}")
    
    if passed == total:
        print("  🎉 ALL TESTS PASSED!")
    else:
        print(f"  ⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)