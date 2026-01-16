# web/api_modules.py
from flask import Blueprint, jsonify
from core.strategy_modules.registry import get_registry

modules_api = Blueprint('modules_api', __name__)

# Category Metadata - Icons and labels for frontend dropdown
CATEGORY_METADATA = {
    'indicator': {
        'icon': '📊',
        'label': 'Indicators',
        'description': 'Core technical indicators (RSI, MACD, SMA, etc.)'
    },
    'momentum': {
        'icon': '📈',
        'label': 'Momentum',
        'description': 'Indicators measuring rate of price change'
    },
    'trend': {
        'icon': '📊',
        'label': 'Trend',
        'description': 'Indicators identifying market direction'
    },
    'volume': {
        'icon': '📉',
        'label': 'Volume',
        'description': 'Indicators analyzing trading volume'
    },
    'volatility': {
        'icon': '⚡',
        'label': 'Volatility',
        'description': 'Indicators measuring price fluctuation'
    },
    'moving_averages': {
        'icon': '〰️',
        'label': 'Moving Averages',
        'description': 'Smoothed price trend indicators'
    },
    'support_resistance': {
        'icon': '🎯',
        'label': 'Support/Resistance',
        'description': 'Key price levels and zones'
    },
    'ict': {
        'icon': '🎯',
        'label': 'ICT/SMC',
        'description': 'Inner Circle Trader and Smart Money Concepts'
    },
    'custom': {
        'icon': '🔧',
        'label': 'Custom',
        'description': 'Advanced and specialized indicators'
    }
}

@modules_api.route('/api/modules', methods=['GET'])
def get_available_modules():
    try:
        registry = get_registry()
        available = registry.list_available_modules()
        
        result = {}
        for category, module_ids in available.items():
            result[category] = []
            
            for module_id in module_ids:
                module_class = registry.get_module(module_id)
                module = module_class()
                
                result[category].append({
                    'id': module_id,
                    'name': module.name,
                    'description': module.description,
                    'category': module.category,
                    'config_schema': module.get_config_schema()
                })
        
        return jsonify({
            'success': True,
            'modules': result,
            'categories': CATEGORY_METADATA  # NEW: Include category metadata
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@modules_api.route('/api/modules/<module_id>', methods=['GET'])
def get_module_details(module_id):
    try:
        registry = get_registry()
        module_class = registry.get_module(module_id)
        module = module_class()
        
        return jsonify({
            'success': True,
            'module': {
                'id': module_id,
                'name': module.name,
                'description': module.description,
                'category': module.category,
                'config_schema': module.get_config_schema()
            }
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@modules_api.route('/api/modules/ict', methods=['GET'])
def get_ict_modules():
    """Get only ICT modules for V5 simulator"""
    try:
        registry = get_registry()
        available = registry.list_available_modules()
        
        ict_modules = []
        for module_id in available.get('ict', []):
            module_class = registry.get_module(module_id)
            module = module_class()
            
            ict_modules.append({
                'id': module_id,
                'name': module.name,
                'description': module.description,
                'config_schema': module.get_config_schema()
            })
        
        return jsonify({
            'success': True,
            'modules': ict_modules
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500