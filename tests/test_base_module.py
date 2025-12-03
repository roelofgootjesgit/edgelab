# tests/test_base_module.py
import pytest
from core.strategy_modules.base import BaseModule

def test_base_module_is_abstract():
    """Cannot instantiate BaseModule directly"""
    with pytest.raises(TypeError):
        BaseModule()

def test_base_module_enforces_methods():
    """Subclass must implement all abstract methods"""
    
    class IncompleteModule(BaseModule):
        @property
        def name(self):
            return "Test"
    
    with pytest.raises(TypeError):
        IncompleteModule()