# tests/test_api_modules.py
"""
Test API modules endpoint directly without full app import.
"""
import pytest
from core.strategy_modules.registry import get_registry


def test_registry_has_rsi():
    """Test that registry discovers RSI module"""
    registry = get_registry()
    
    # RSI should be discoverable
    rsi_class = registry.get_module('rsi')
    assert rsi_class is not None


def test_registry_get_all_modules():
    """Test get_all_modules returns proper structure"""
    registry = get_registry()
    all_modules = registry.get_all_modules()
    
    assert 'indicator' in all_modules
    assert 'ict' in all_modules
    assert 'mtf' in all_modules
    assert 'position_sizing' in all_modules
    
    # Should have at least RSI
    assert len(all_modules['indicator']) >= 1


def test_rsi_module_properties():
    """Test RSI module has required properties"""
    registry = get_registry()
    rsi_class = registry.get_module('rsi')
    rsi_instance = rsi_class()
    
    assert rsi_instance.name == "RSI (Relative Strength Index)"
    assert rsi_instance.category == "indicator"
    assert hasattr(rsi_instance, 'description')


def test_rsi_module_schema():
    """Test RSI module returns valid schema"""
    registry = get_registry()
    rsi_class = registry.get_module('rsi')
    rsi_instance = rsi_class()
    
    schema = rsi_instance.get_config_schema()
    
    assert 'fields' in schema
    assert len(schema['fields']) == 4  # period, overbought, oversold, direction
    
    # Check first field (period)
    period_field = schema['fields'][0]
    assert period_field['name'] == 'period'
    assert period_field['type'] == 'number'
    assert period_field['default'] == 14


def test_api_serialization_format():
    """Test that modules can be serialized to API format"""
    registry = get_registry()
    rsi_class = registry.get_module('rsi')
    rsi_instance = rsi_class()
    
    # Simulate what API does
    api_format = {
        'id': 'rsi',
        'name': rsi_instance.name,
        'description': rsi_instance.description,
        'category': rsi_instance.category,
        'schema': rsi_instance.get_config_schema()
    }
    
    # Verify structure
    assert api_format['id'] == 'rsi'
    assert api_format['name'] == "RSI (Relative Strength Index)"
    assert api_format['category'] == "indicator"
    assert 'fields' in api_format['schema']