#!/usr/bin/env python3
"""Test Suite for Strategy Modules"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core.strategy_modules.registry import get_registry

def create_sample_data(periods=100):
    np.random.seed(42)
    base_price = 100.0
    returns = np.random.randn(periods) * 2 + 0.1
    prices = base_price + np.cumsum(returns)
    
    data = pd.DataFrame({
        'open': prices + np.random.randn(periods) * 0.5,
        'high': prices + abs(np.random.randn(periods)) * 1.5,
        'low': prices - abs(np.random.randn(periods)) * 1.5,
        'close': prices,
        'volume': np.random.randint(1000, 10000, periods)
    })
    data = data.reset_index(drop=True)
    return data

def test_module_discovery():
    print("\n" + "="*60)
    print("TEST 1: Module Discovery")
    print("="*60)
    
    registry = get_registry()
    available = registry.list_available_modules()
    
    print(f"\n📦 Discovered modules by category:")
    for category, modules in available.items():
        print(f"\n  {category.upper()}:")
        for module_id in modules:
            module_class = registry.get_module(module_id)
            module = module_class()
            print(f"    ✓ {module_id}: {module.name}")
    
    total_modules = sum(len(mods) for mods in available.values())
    print(f"\n✅ Total modules discovered: {total_modules}")
    assert total_modules > 0, "No modules discovered!"
    return True

def test_rsi_module():
    print("\n" + "="*60)
    print("TEST 2: RSI Module")
    print("="*60)
    
    from core.strategy_modules.indicator.rsi import RSIModule
    rsi = RSIModule()
    print(f"\n📊 Module: {rsi.name}")
    
    data = create_sample_data(50)
    config = {'period': 14, 'overbought': 70, 'oversold': 30}
    data = rsi.calculate(data, config)
    
    assert 'rsi' in data.columns, "RSI column not added"
    valid_rsi = data['rsi'].dropna()
    assert len(valid_rsi) > 0, "No RSI values"
    assert valid_rsi.min() >= 0 and valid_rsi.max() <= 100, "RSI range invalid"
    
    print(f"\n📈 RSI Range: {valid_rsi.min():.2f} - {valid_rsi.max():.2f}")
    print("\n✅ RSI Module: PASSED")
    return True

def test_sma_module():
    print("\n" + "="*60)
    print("TEST 3: SMA Module")
    print("="*60)
    
    from core.strategy_modules.indicator.sma import SMAModule
    sma = SMAModule()
    print(f"\n📊 Module: {sma.name}")
    
    data = create_sample_data(100)
    config = {'period': 20}
    data = sma.calculate(data, config)
    
    # FIX: Check for sma_20 instead of just 'sma'
    sma_col = 'sma_20'
    assert sma_col in data.columns, f"SMA column '{sma_col}' not added. Available: {list(data.columns)}"
    valid_sma = data[sma_col].dropna()
    assert len(valid_sma) > 0, "No SMA values"
    
    print(f"\n📈 Valid SMA values: {len(valid_sma)}/{len(data)}")
    print(f"   Column name: {sma_col}")
    print("\n✅ SMA Module: PASSED")
    return True

def test_all_indicators():
    print("\n" + "="*60)
    print("TEST 4: All Indicators")
    print("="*60)
    
    registry = get_registry()
    available = registry.list_available_modules()
    
    data = create_sample_data(100)
    
    print(f"\n🧪 Testing all {len(available['indicator'])} indicators...")
    
    for module_id in available['indicator']:
        try:
            module_class = registry.get_module(module_id)
            module = module_class()
            
            # Get default config
            schema = module.get_config_schema()
            config = {field['name']: field['default'] for field in schema['fields']}
            
            # Calculate
            result = module.calculate(data.copy(), config)
            
            print(f"  ✓ {module_id}: Added {len(result.columns) - len(data.columns)} columns")
            
        except Exception as e:
            print(f"  ✗ {module_id}: {e}")
            raise
    
    print("\n✅ All Indicators: PASSED")
    return True

def run_all_tests():
    print("\n🧪 " + "="*56)
    print("  QuantMetrics Strategy Modules - Test Suite")
    print("="*60 + "\n")
    
    tests = [
        ("Module Discovery", test_module_discovery),
        ("RSI Module", test_rsi_module),
        ("SMA Module", test_sma_module),
        ("All Indicators", test_all_indicators),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test_name}: FAILED - {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Failed: {failed}/{len(tests)}")
    print("\n" + "="*60 + "\n")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
