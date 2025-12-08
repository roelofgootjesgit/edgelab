# tests/test_module_registry.py
import pytest
from core.strategy_modules.registry import ModuleRegistry, get_registry
from core.strategy_modules.base import BaseModule


def test_registry_initialization():
    """Registry initializes with empty state"""
    registry = ModuleRegistry()
    assert registry._modules == {}
    assert 'indicator' in registry._categories
    assert 'ict' in registry._categories


def test_registry_singleton():
    """get_registry() returns same instance"""
    reg1 = get_registry()
    reg2 = get_registry()
    assert reg1 is reg2


def test_get_module_not_found():
    """get_module() raises error for unknown module"""
    registry = ModuleRegistry()
    
    with pytest.raises(ValueError, match="Module 'nonexistent' not found"):
        registry.get_module('nonexistent')


def test_get_modules_by_category_invalid():
    """get_modules_by_category() raises error for invalid category"""
    registry = ModuleRegistry()
    
    with pytest.raises(ValueError, match="Category 'invalid' not found"):
        registry.get_modules_by_category('invalid')


def test_list_available_modules():
    """list_available_modules() returns dict of categories"""
    registry = ModuleRegistry()
    registry.discover_modules()
    
    modules = registry.list_available_modules()
    assert isinstance(modules, dict)
    assert 'indicator' in modules
    assert 'ict' in modules