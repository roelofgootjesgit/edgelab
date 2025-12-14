# tests/test_sma_module.py
"""
Test SMA module functionality
"""

import pandas as pd
import numpy as np
from core.strategy_modules.indicators.sma import SMAModule


def test_sma_calculation():
    """Test basic SMA calculation"""
    
    # Create sample data
    data = pd.DataFrame({
        'open': [100, 101, 102, 103, 104],
        'high': [101, 102, 103, 104, 105],
        'low': [99, 100, 101, 102, 103],
        'close': [100, 101, 102, 103, 104],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })
    
    # Initialize module
    sma = SMAModule()
    
    # Configure
    config = {
        'period': 3,
        'source': 'close',
        'condition_type': 'price_cross_above'
    }
    
    # Calculate
    data = sma.calculate(data, config)
    
    # Verify SMA column exists
    assert 'sma_3' in data.columns
    
    # Verify calculation (SMA of last 3: (102+103+104)/3 = 103)
    assert abs(data.loc[4, 'sma_3'] - 103.0) < 0.01
    
    print("✅ SMA calculation test passed")


def test_price_crossover():
    """Test price crossover detection"""
    
    # Create data with clear crossover
    data = pd.DataFrame({
        'close': [98, 99, 100, 102, 103],  # Crosses above 100
        'open': [97, 98, 99, 101, 102],
        'high': [99, 100, 101, 103, 104],
        'low': [97, 98, 99, 101, 102],
        'volume': [1000, 1000, 1000, 1000, 1000]
    })
    
    sma = SMAModule()
    config = {
        'period': 2,
        'source': 'close',
        'condition_type': 'price_cross_above'
    }
    
    # Calculate SMA
    data = sma.calculate(data, config)
    
    # Check crossover at index 3 (price 102 crosses above SMA ~101)
    is_signal = sma.check_entry_condition(data, 3, config, 'LONG')
    
    print(f"Price: {data.loc[3, 'close']}, SMA: {data.loc[3, 'sma_2']}")
    print(f"Crossover detected: {is_signal}")
    
    assert is_signal == True, "Should detect crossover"
    
    print("✅ Price crossover test passed")


def test_golden_cross():
    """Test Golden Cross detection (50 SMA crosses 200 SMA)"""
    
    # Create uptrending data
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(300) * 0.5 + 0.1)
    
    data = pd.DataFrame({
        'close': prices,
        'open': prices - 0.5,
        'high': prices + 1,
        'low': prices - 1,
        'volume': [1000] * 300
    })
    
    sma = SMAModule()
    config = {
        'period': 50,
        'cross_sma_period': 200,
        'source': 'close',
        'condition_type': 'sma_cross_above'
    }
    
    # Calculate
    data = sma.calculate(data, config)
    
    # Find if Golden Cross occurred
    golden_crosses = []
    for i in range(201, 300):
        if sma.check_entry_condition(data, i, config, 'LONG'):
            golden_crosses.append(i)
    
    print(f"✅ Golden Cross test complete - found {len(golden_crosses)} signals")
    
    if golden_crosses:
        print(f"First Golden Cross at index: {golden_crosses[0]}")
    

if __name__ == '__main__':
    test_sma_calculation()
    test_price_crossover()
    test_golden_cross()
    print("\n✅ ALL SMA TESTS PASSED!")