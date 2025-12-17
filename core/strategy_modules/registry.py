# core/strategy_modules/registry.py
"""
Module Registry - Auto-discovery system for strategy modules.
Updated to scan ALL indicator categories (50+ indicators)
"""

from typing import Dict, List, Type
import importlib
import inspect
from pathlib import Path
from core.strategy_modules.base import BaseModule


class ModuleRegistry:
    """Registry for auto-discovering and managing strategy modules."""
    
    def __init__(self):
        self._modules: Dict[str, Type[BaseModule]] = {}
        
        # ALL CATEGORIES (not just 4!)
        self._categories: Dict[str, List[str]] = {
            'indicator': [],           # Original 5 indicators
            'ict': [],                 # 11 ICT modules
            'trend': [],               # 8 trend indicators
            'momentum': [],            # 8 momentum indicators
            'moving_averages': [],     # 8 moving average indicators
            'volatility': [],          # 6 volatility indicators
            'volume': [],              # 6 volume indicators
            'support_resistance': [],  # 4 S/R indicators
            'custom': [],              # 12 custom indicators
            'mtf': [],                 # Future: multi-timeframe
            'position_sizing': []      # Future: position sizing
        }
    
    def discover_modules(self) -> None:
        """Scan strategy_modules/ directory and load all modules."""
        base_path = Path(__file__).parent
        
        print(f"[Registry] Scanning for modules in: {base_path}")
        
        # Scan each category directory
        for category in self._categories.keys():
            category_path = base_path / category
            
            if not category_path.exists():
                print(f"[Registry] Category '{category}' directory not found, skipping")
                continue
            
            # Find all .py files (except __init__.py)
            module_count = 0
            for module_file in category_path.glob('*.py'):
                if module_file.name.startswith('__'):
                    continue
                
                # Import module
                module_name = f"core.strategy_modules.{category}.{module_file.stem}"
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find BaseModule subclasses
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BaseModule) and 
                            obj is not BaseModule and
                            not inspect.isabstract(obj)):
                            
                            # Register module
                            module_id = module_file.stem
                            self._modules[module_id] = obj
                            self._categories[category].append(module_id)
                            module_count += 1
                            
                except Exception as e:
                    print(f"[Registry] WARNING: Could not load {module_name}: {e}")
            
            if module_count > 0:
                print(f"[Registry] Loaded {module_count} modules from '{category}'")
    
    def get_module(self, module_id: str) -> Type[BaseModule]:
        """Get module class by ID"""
        if module_id not in self._modules:
            raise ValueError(f"Module '{module_id}' not found")
        return self._modules[module_id]
    
    def get_modules_by_category(self, category: str) -> List[Type[BaseModule]]:
        """Get all modules in a category"""
        if category not in self._categories:
            raise ValueError(f"Category '{category}' not found")
        
        return [self._modules[mod_id] for mod_id in self._categories[category]]
    
    def get_all_modules(self) -> Dict[str, List[Type[BaseModule]]]:
        """Get all modules organized by category"""
        return {
            category: self.get_modules_by_category(category)
            for category in self._categories.keys()
            if len(self._categories[category]) > 0  # Only return non-empty categories
        }
    
    def list_available_modules(self) -> Dict[str, List[str]]:
        """Get list of module IDs organized by category"""
        return {
            category: list(module_ids)
            for category, module_ids in self._categories.items()
            if len(module_ids) > 0  # Only return non-empty categories
        }
    
    def get_total_count(self) -> int:
        """Get total number of registered modules"""
        return len(self._modules)


# Global registry instance
_registry = None

def get_registry() -> ModuleRegistry:
    """Get or create global registry instance"""
    global _registry
    if _registry is None:
        _registry = ModuleRegistry()
        _registry.discover_modules()
        
        # Print summary
        total = _registry.get_total_count()
        print(f"[Registry] Total modules registered: {total}")
    
    return _registry