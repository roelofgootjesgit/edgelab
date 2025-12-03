# web/api_modules.py
"""
API endpoints for strategy modules.
Serves module metadata and schemas to frontend.
"""

from flask import Blueprint, jsonify
from core.strategy_modules.registry import get_registry

# Create blueprint for module API
modules_api = Blueprint('modules_api', __name__)


@modules_api.route('/api/modules', methods=['GET'])
def get_available_modules():
    """
    Get all available strategy modules organized by category.
    
    Returns:
        JSON with structure:
        {
            "indicator": [
                {
                    "id": "rsi",
                    "name": "RSI (Relative Strength Index)",
                    "description": "Momentum oscillator...",
                    "schema": {"fields": [...]}
                }
            ],
            "ict": [...],
            "mtf": [...],
            "position_sizing": [...]
        }
    """
    registry = get_registry()
    all_modules = registry.get_all_modules()
    
    # Convert module classes to JSON-serializable format
    result = {}
    
    for category, module_classes in all_modules.items():
        result[category] = []
        
        for module_class in module_classes:
            # Instantiate to get properties
            module_instance = module_class()
            
            result[category].append({
                'id': module_class.__name__.lower().replace('module', ''),
                'name': module_instance.name,
                'description': module_instance.description,
                'category': module_instance.category,
                'schema': module_instance.get_config_schema()
            })
    
    return jsonify(result)


@modules_api.route('/api/modules/<category>', methods=['GET'])
def get_modules_by_category(category):
    """
    Get modules for a specific category.
    
    Args:
        category: 'indicator', 'ict', 'mtf', or 'position_sizing'
    
    Returns:
        JSON array of modules in that category
    """
    registry = get_registry()
    
    try:
        module_classes = registry.get_modules_by_category(category)
        
        result = []
        for module_class in module_classes:
            module_instance = module_class()
            
            result.append({
                'id': module_class.__name__.lower().replace('module', ''),
                'name': module_instance.name,
                'description': module_instance.description,
                'schema': module_instance.get_config_schema()
            })
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404


@modules_api.route('/api/modules/<category>/<module_id>', methods=['GET'])
def get_module_schema(category, module_id):
    """
    Get schema for a specific module.
    
    Args:
        category: Module category
        module_id: Module identifier (e.g., 'rsi')
    
    Returns:
        JSON schema for the module
    """
    registry = get_registry()
    
    try:
        module_class = registry.get_module(module_id)
        module_instance = module_class()
        
        return jsonify({
            'id': module_id,
            'name': module_instance.name,
            'description': module_instance.description,
            'category': module_instance.category,
            'schema': module_instance.get_config_schema()
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404