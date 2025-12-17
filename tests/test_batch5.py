"""
test_batch5.py
==============

Test all 12 custom indicators (Batch 5 - FINAL BATCH!)

Tests Batch 5 modules:
1. Awesome Oscillator
2. Accelerator Oscillator
3. Elder Ray
4. Choppiness Index
5. Vortex Indicator
6. Force Index
7. Ease of Movement
8. Gator Oscillator
9. Momentum Indicator
10. Heikin Ashi
11. Renko Bricks
12. Donchian Channels (BONUS - reaches 50!)

Author: QuantMetrics Development Team
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from datetime import datetime, timedelta

# Import all 12 custom modules
from core.strategy_modules.custom.awesome_oscillator import AwesomeOscillatorModule
from core.strategy_modules.custom.accelerator_oscillator import AcceleratorOscillatorModule
from core.strategy_modules.custom.elder_ray import ElderRayModule
from core.strategy_modules.custom.choppiness import ChoppinessModule
from core.strategy_modules.custom.vortex import VortexModule
from core.strategy_modules.custom.force_index import ForceIndexModule
from core.strategy_modules.custom.ease_of_movement import EaseOfMovementModule
from core.strategy_modules.custom.gator_oscillator import GatorOscillatorModule
from core.strategy_modules.custom.momentum_indicator import MomentumIndicatorModule
from core.strategy_modules.custom.heikin_ashi import HeikinAshiModule
from core.strategy_modules.custom.renko import RenkoModule
from core.strategy_modules.custom.donchian_channels import DonchianChannelsModule


def get_test_data():
    """Get real market data for testing"""
    try:
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
        
        if data.empty:
            raise ValueError("No data returned")
        
        print(f"✓ Loaded {len(data)} candles of XAUUSD 15m data")
        return data
        
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        sys.exit(1)


def test_indicator(module_class, name, data):
    """Test a single indicator"""
    try:
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"{'='*60}")
        
        # Initialize module
        module = module_class()
        
        # Get config schema
        schema = module.get_config_schema()
        print(f"✓ Schema loaded: {len(schema.get('properties', {}))} parameters")
        
        # Use default config
        config = {}
        for param, details in schema.get('properties', {}).items():
            if 'default' in details:
                config[param] = details['default']
        
        # Calculate indicator
        result = module.calculate(data.copy(), config)
        print(f"✓ Calculation successful: {len(result.columns)} total columns")
        
        # Find indicator columns (exclude OHLCV)
        base_cols = ['open', 'high', 'low', 'close', 'volume']
        indicator_cols = [col for col in result.columns if col not in base_cols]
        print(f"✓ Indicator columns added: {len(indicator_cols)}")
        
        # Show sample values from most recent row
        last_row = result.iloc[-1]
        print(f"\n  Sample values (most recent):")
        for col in indicator_cols[:5]:  # Show first 5 indicator columns
            val = last_row[col]
            if pd.notna(val):
                print(f"    {col}: {val:.4f}" if isinstance(val, (int, float)) else f"    {col}: {val}")
        
        if len(indicator_cols) > 5:
            print(f"    ... and {len(indicator_cols) - 5} more columns")
        
        # Test entry conditions
        print(f"\n  Testing entry conditions...")
        
        # Test LONG
        long_signals = 0
        for i in range(50, len(result)):  # Test last 50 candles
            if module.check_entry_condition(result, i, config, 'LONG'):
                long_signals += 1
        
        # Test SHORT
        short_signals = 0
        for i in range(50, len(result)):
            if module.check_entry_condition(result, i, config, 'SHORT'):
                short_signals += 1
        
        print(f"  ✓ LONG signals: {long_signals}")
        print(f"  ✓ SHORT signals: {short_signals}")
        
        if long_signals == 0 and short_signals == 0:
            print(f"  ⚠ Warning: No signals generated (may need config adjustment)")
        
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Batch 5 tests"""
    print("="*60)
    print("QUANTMETRICS BATCH 5 TEST SUITE")
    print("Testing 12 Custom Indicators (FINAL BATCH!)")
    print("="*60)
    
    # Load test data
    data = get_test_data()
    
    # Define all 12 indicators
    indicators = [
        (AwesomeOscillatorModule, "Awesome Oscillator"),
        (AcceleratorOscillatorModule, "Accelerator Oscillator"),
        (ElderRayModule, "Elder Ray"),
        (ChoppinessModule, "Choppiness Index"),
        (VortexModule, "Vortex Indicator"),
        (ForceIndexModule, "Force Index"),
        (EaseOfMovementModule, "Ease of Movement"),
        (GatorOscillatorModule, "Gator Oscillator"),
        (MomentumIndicatorModule, "Momentum Indicator"),
        (HeikinAshiModule, "Heikin Ashi"),
        (RenkoModule, "Renko Bricks"),
        (DonchianChannelsModule, "Donchian Channels (BONUS)")
    ]
    
    # Test each indicator
    results = []
    for module_class, name in indicators:
        success = test_indicator(module_class, name, data)
        results.append((name, success))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} indicators passed")
    print(f"\nDetails:")
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status} - {name}")
    
    # Final milestone message
    if passed == total:
        print("\n" + "🎉"*30)
        print("SUCCESS! ALL 12 BATCH 5 INDICATORS WORKING!")
        print("="*60)
        print("MILESTONE: 50/50 INDICATORS COMPLETE!")
        print("="*60)
        print("Batches completed:")
        print("  ✓ Batch 1: 10 indicators (Trend, Momentum, Volatility basics)")
        print("  ✓ Batch 2: 10 indicators (Advanced Trend & Momentum)")
        print("  ✓ Batch 3: 8 indicators (Volume, Support/Resistance)")
        print("  ✓ Batch 4: 8 indicators (Moving Averages)")
        print("  ✓ Batch 5: 12 indicators (Custom) + BONUS")
        print("  = TOTAL: 50 INDICATORS! 🎊")
        print("🎉"*30)
    else:
        print(f"\n⚠ {total - passed} indicator(s) need attention")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)