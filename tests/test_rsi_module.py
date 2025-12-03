# tests/test_rsi_module.py
import pytest
import pandas as pd
import numpy as np
from core.strategy_modules.indicator.rsi import RSIModule


@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing"""
    dates = pd.date_range('2024-01-01', periods=100, freq='1H')
    
    # Create trending data for predictable RSI
    close = np.linspace(100, 120, 100)  # Uptrend
    
    data = pd.DataFrame({
        'timestamp': dates,
        'open': close - 0.5,
        'high': close + 1,
        'low': close - 1,
        'close': close,
        'volume': 1000
    })
    
    return data


def test_rsi_module_properties():
    """Test module metadata"""
    module = RSIModule()
    
    assert module.name == "RSI (Relative Strength Index)"
    assert module.category == "indicator"
    assert "momentum" in module.description.lower()


def test_rsi_config_schema():
    """Test configuration schema structure"""
    module = RSIModule()
    schema = module.get_config_schema()
    
    assert "fields" in schema
    assert len(schema["fields"]) == 4
    
    # Check period field
    period_field = next(f for f in schema["fields"] if f["name"] == "period")
    assert period_field["type"] == "number"
    assert period_field["default"] == 14


def test_rsi_calculation(sample_data):
    """Test RSI calculation adds column"""
    module = RSIModule()
    config = {"period": 14, "overbought": 70, "oversold": 30}
    
    result = module.calculate(sample_data, config)
    
    assert 'rsi' in result.columns
    assert 'rsi_overbought' in result.columns
    assert 'rsi_oversold' in result.columns
    
    # RSI should be between 0 and 100
    valid_rsi = result['rsi'].dropna()
    assert (valid_rsi >= 0).all()
    assert (valid_rsi <= 100).all()


def test_rsi_entry_condition_long(sample_data):
    """Test long entry signal detection"""
    module = RSIModule()
    
    # Create oversold condition followed by bounce
    sample_data.loc[20:25, 'close'] = 90  # Drop price
    sample_data.loc[26:30, 'close'] = 95  # Small recovery
    
    config = {"period": 14, "oversold": 30, "direction": "long"}
    data = module.calculate(sample_data, config)
    
    # Check some index where RSI might cross oversold
    # (exact index depends on calculation, so we check if ANY signal exists)
    signals = [module.check_entry_condition(data, i, config) for i in range(20, 35)]
    
    # Should have at least one signal in oversold recovery zone
    assert any(signals), "Expected at least one long signal in test data"


def test_rsi_entry_no_signal_insufficient_data():
    """Test no signal when insufficient data"""
    module = RSIModule()
    
    # Only 5 candles (need 14 for RSI)
    data = pd.DataFrame({
        'close': [100, 101, 102, 103, 104],
        'rsi': [np.nan] * 5
    })
    
    config = {"period": 14, "oversold": 30, "direction": "both"}
    
    signal = module.check_entry_condition(data, 4, config)
    assert signal == False


def test_rsi_module_registry_integration():
    """Test module can be discovered by registry"""
    from core.strategy_modules.registry import ModuleRegistry
    
    registry = ModuleRegistry()
    registry.discover_modules()
    
    # RSI should be discoverable
    rsi_class = registry.get_module('rsi')
    assert rsi_class == RSIModule
    
    # Should be in indicators category
    indicators = registry.get_modules_by_category('indicator')
    assert RSIModule in indicators