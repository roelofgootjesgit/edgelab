"""
app.py
======

QuantMetrics Flask Web Application
Professional SaaS interface for trading analysis

Routes:
- / : Landing page
- /upload : Upload CSV
- /analyze : Process and generate report
- /simulator : Strategy simulator interface (classic)
- /simulator-v2 : Strategy simulator v2 (modular) - NEW
- /simulator-v3 : Strategy simulator v3 (structured flow) - NEW
- /run-backtest : Execute backtest (multi-condition support)
- /run-backtest-v2 : Execute backtest v2 (modular)
- /run-backtest-v3 : Execute backtest v3 (structured flow) - NEW
- /download/<filename> : Download PDF
- /api/modules : Get available strategy modules

Author: QuantMetrics Development Team
Version: 4.0 (Modular Strategy System)
"""

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from collections import defaultdict

from core.csv_parser import CSVParser
from core.analyzer import BasicAnalyzer
from core.playwright_reporter import PlaywrightReportGenerator
from core.strategy import StrategyDefinition, EntryCondition
from core.backtest_engine import BacktestEngine
from web.api_modules import modules_api
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'quantmetrics-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'csv'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Register API blueprints
app.register_blueprint(modules_api)

# Startup message to confirm correct version
print("=" * 60)
print("QuantMetrics v4.0 - Transform Trading Into Data Science")
print("=" * 60)


# ============================================================================
# RATE LIMITING (Guardrail G8 - Basic in-memory for beta)
# ============================================================================

# Simple in-memory rate limiter (for beta)
# In production, use Redis-based rate limiting
_rate_limit_store = defaultdict(list)  # IP -> list of timestamps


def check_rate_limit(ip_address, max_requests, window_minutes):
    """
    Check if IP has exceeded rate limit.
    
    Args:
        ip_address: Client IP address
        max_requests: Maximum requests allowed
        window_minutes: Time window in minutes
    
    Returns:
        (allowed, remaining, reset_time)
    """
    from config import Config
    now = datetime.now()
    cutoff = now - timedelta(minutes=window_minutes)
    
    # Clean old entries
    _rate_limit_store[ip_address] = [
        ts for ts in _rate_limit_store[ip_address] if ts > cutoff
    ]
    
    # Check limit BEFORE adding current request
    request_count = len(_rate_limit_store[ip_address])
    if request_count >= max_requests:
        # Find oldest request to calculate reset time
        if _rate_limit_store[ip_address]:
            oldest = min(_rate_limit_store[ip_address])
            reset_time = oldest + timedelta(minutes=window_minutes)
        else:
            reset_time = now + timedelta(minutes=window_minutes)
        
        return False, 0, reset_time
    
    # Add current request (only if within limit)
    _rate_limit_store[ip_address].append(now)
    remaining = max_requests - (request_count + 1)
    reset_time = now + timedelta(minutes=window_minutes)
    
    return True, remaining, reset_time


def get_client_ip():
    """Get client IP address from request."""
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    elif request.headers.getlist("X-Real-IP"):
        ip = request.headers.getlist("X-Real-IP")[0]
    else:
        ip = request.remote_addr
    return ip


# ============================================================================
# ERROR CONTRACT (Guardrail G7 - Eén error contract overal)
# ============================================================================

def error_response(code, message, details=None, status_code=400):
    """
    Standardized error response format (Guardrail G7).
    
    Args:
        code: Error code (e.g., 'NO_DECISION_BLOCKS', 'MAX_BLOCKS_EXCEEDED')
        message: Human-readable error message
        details: Optional dict with additional error details
        status_code: HTTP status code (400, 404, 500, etc.)
    
    Returns:
        Tuple (dict, int) for Flask response
    """
    response = {
        'success': False,
        'code': code,
        'error': message
    }
    if details:
        response['details'] = details
    
    return response, status_code


# Standard error codes
ERROR_CODES = {
    'NO_DECISION_BLOCKS': 'NO_DECISION_BLOCKS',
    'MAX_BLOCKS_EXCEEDED': 'MAX_BLOCKS_EXCEEDED',
    'NO_VALID_CONDITIONS': 'NO_VALID_CONDITIONS',
    'NO_TRADES_GENERATED': 'NO_TRADES_GENERATED',
    'INVALID_MODULE': 'INVALID_MODULE',
    'MODULE_ERROR': 'MODULE_ERROR',
    'INVALID_PARAMETERS': 'INVALID_PARAMETERS',
    'DATA_FETCH_ERROR': 'DATA_FETCH_ERROR',
    'BACKTEST_ERROR': 'BACKTEST_ERROR',
    'INTERNAL_ERROR': 'INTERNAL_ERROR',
    'RATE_LIMIT_EXCEEDED': 'RATE_LIMIT_EXCEEDED'
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload')
def upload_page():
    return render_template('upload.html')


@app.route('/simulator')
def simulator():
    """Classic strategy simulator (hardcoded modules)"""
    return render_template('simulator.html')


@app.route('/simulator-v2')
def simulator_v2():
    """NEW: Modular strategy builder with dynamic UI"""
    return render_template('simulator_v2.html')


@app.route('/simulator-v3')
def simulator_v3():
    """V3: Strategy Builder with mental promise and structured flow"""
    return render_template('simulator_v3.html')


@app.route('/simulator-v4')
def simulator_v4():
    """V4: Strategy Builder with Decision Block Model"""
    return render_template('simulator_v4.html')


@app.route('/simulator-v5')
def simulator_v5():
    """V5: Simple ICT Strategy Simulator - Direct testing"""
    return render_template('simulator_v5.html')


@app.route('/strategy-templates')
def strategy_templates():
    """NEW: Strategy template selector landing page"""
    return render_template('strategy_templates.html')


@app.route('/test-runner')
def test_runner():
    """Automated indicator test suite"""
    return render_template('test_runner.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('upload_page'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('upload_page'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload a CSV file.', 'error')
        return redirect(url_for('upload_page'))
    
    try:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)
        
        parser = CSVParser()
        trades = parser.parse(filepath)
        
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        generator = PlaywrightReportGenerator()
        pdf_bytes = generator.generate_report(results, trades)
        
        pdf_filename = f"quantmetrics_report_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return render_template('results.html', 
                             results=results,
                             pdf_filename=pdf_filename,
                             trades_count=len(trades),
                             trades=trades,  # Pass trades list for display
                             source='csv')
    
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('upload_page'))




@app.route('/run-backtest-v4', methods=['POST'])
def run_backtest_v4():
    """V4: Decision Block Model backtest - with Quick Test mode support"""
    try:
        import hashlib
        import json
        from core.strategy_modules.registry import get_registry
        
        data = request.get_json()
        
        # Check if Quick Test mode (fast preview)
        quick_test = data.get('quickTest', False)
        
        # Extract market context
        market_context = data.get('marketContext', {})
        symbol = market_context.get('market', 'XAUUSD')
        timeframe = market_context.get('timeframe', '15m')
        direction_raw = market_context.get('direction', 'Long')
        direction = 'LONG' if direction_raw.upper() in ['LONG', 'BOTH'] else 'SHORT'
        period = market_context.get('testPeriod', '2mo')
        session_raw = market_context.get('session', '').strip()
        session = session_raw if session_raw and session_raw != 'All' else None
        
        # Extract exit & risk
        exit_data = data.get('exit', {})
        tp_r = float(exit_data.get('takeProfit', 2.0))
        sl_r = float(exit_data.get('stopLoss', 1.0))
        
        # Extract Decision Blocks
        decision_blocks = data.get('decisionBlocks', [])
        
        if not decision_blocks:
            return error_response(
                ERROR_CODES['NO_DECISION_BLOCKS'],
                'No Decision Blocks specified. Please add at least one Decision Block with selected confirmations.',
                details={'decision_blocks_count': 0}
            )
        
        if len(decision_blocks) > 4:
            return error_response(
                ERROR_CODES['MAX_BLOCKS_EXCEEDED'],
                'Maximum 4 Decision Blocks allowed. Please remove excess blocks.',
                details={'provided': len(decision_blocks), 'max_allowed': 4}
            )
        
        # Quick Test mode: Limit to 30 days and max 4 modules
        if quick_test:
            # Override period to 30 days max
            period = '1mo'  # 30 days
            print(f"[BACKTEST-V4] Quick Test mode: Limited to 30 days")
        
        # Convert Decision Blocks to backtest conditions
        conditions = convert_decision_blocks_to_conditions(decision_blocks)
        
        if not conditions:
            return error_response(
                ERROR_CODES['NO_VALID_CONDITIONS'],
                'No valid conditions generated from Decision Blocks. Please ensure at least one sub-confirmation is selected per Decision Block.',
                details={
                    'decision_blocks_count': len(decision_blocks),
                    'suggestion': 'Check that each Decision Block has at least one sub-confirmation selected (checked/enabled).'
                }
            )
        
        # Quick Test mode: Limit to first 4 modules
        if quick_test and len(conditions) > 4:
            print(f"[BACKTEST-V4] Quick Test: Limiting to first 4 modules (was {len(conditions)})")
            conditions = conditions[:4]
        
        # Build strategy name
        strategy_name = f"{direction} {symbol} ({timeframe})"
        if len(decision_blocks) > 0:
            strategy_name = f"Decision Blocks - {strategy_name}"
        if quick_test:
            strategy_name = f"Quick Test - {strategy_name}"
        
        # Check cache (simple in-memory cache for MVP)
        # In production, use Redis
        cache_key = None
        if not quick_test:  # Only cache full tests
            cache_key = hashlib.md5(
                json.dumps({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'direction': direction,
                    'period': period,
                    'session': session,
                    'tp_r': tp_r,
                    'sl_r': sl_r,
                    'modules': [c.get('module_id') for c in conditions],
                    'configs': [c.get('config') for c in conditions]
                }, sort_keys=True).encode()
            ).hexdigest()
            
            # Simple in-memory cache (for MVP)
            # In production, use Redis with TTL
            if not hasattr(app, 'backtest_cache'):
                app.backtest_cache = {}
            
            if cache_key in app.backtest_cache:
                cached = app.backtest_cache[cache_key]
                print(f"[BACKTEST-V4] Cache HIT: Returning cached results")
                # Return cached results
                return render_template('results.html',
                                     results=cached['results'],
                                     pdf_filename=cached['pdf_filename'],
                                     trades_count=cached['trades_count'],
                                     trades=cached['trades'],
                                     source='backtest_v4',
                                     strategy=strategy_name)
        
        # Run backtest
        mode_str = "Quick Test" if quick_test else "Full Test"
        print(f"[BACKTEST-V4] Running {mode_str}: {strategy_name} with {len(conditions)} conditions from {len(decision_blocks)} Decision Blocks")
        engine = BacktestEngine()
        trades = engine.run_modular(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            period=period,
            session=session,
            tp_r=tp_r,
            sl_r=sl_r,
            modules=conditions
        )
        
        print(f"[BACKTEST-V4] Generated {len(trades)} trades")
        
        if not trades:
            # Render error page instead of JSON
            strategy_info = {
                'market': symbol,
                'timeframe': timeframe,
                'session': session,
                'direction': direction,
                'period': period,
                'blocks_count': len(decision_blocks),
                'quick_test': quick_test
            }
            
            # Try to get debug info from engine if available
            debug_info = None
            # Note: Debug info would need to be captured from engine logs
            # For now, we'll leave it as None - can be enhanced later
            
            return render_template('no_trades_error.html',
                                 strategy_info=strategy_info,
                                 debug_info=debug_info)
        
        # Analyze results
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        # Generate PDF report
        generator = PlaywrightReportGenerator()
        pdf_bytes = generator.generate_report(results, trades, strategy={'name': strategy_name})
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"backtest_v4_{symbol}_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"[BACKTEST-V4] PDF saved: {pdf_filename}")
        
        # Cache results (only for full tests, not quick tests)
        if cache_key:
            app.backtest_cache[cache_key] = {
                'results': results,
                'pdf_filename': pdf_filename,
                'trades_count': len(trades),
                'trades': trades,
                'timestamp': datetime.now()
            }
            # Limit cache size (keep last 100 entries)
            if len(app.backtest_cache) > 100:
                # Remove oldest entry
                oldest_key = min(app.backtest_cache.keys(), 
                               key=lambda k: app.backtest_cache[k].get('timestamp', datetime.min))
                del app.backtest_cache[oldest_key]
            print(f"[BACKTEST-V4] Results cached (key: {cache_key[:8]}...)")
        
        # Return results page
        return render_template('results.html',
                             results=results,
                             pdf_filename=pdf_filename,
                             trades_count=len(trades),
                             trades=trades,
                             source='backtest_v4',
                             strategy=strategy_name)
        
    except Exception as e:
        print(f"[ERROR] Backtest-v4 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(
            ERROR_CODES['BACKTEST_ERROR'],
            f'Backtest execution failed: {str(e)}',
            details={'exception_type': type(e).__name__},
            status_code=500
        )


@app.route('/run-backtest-v5', methods=['POST'])
def run_backtest_v5():
    """V5: Direct ICT backtest - no modules, just pure logic"""
    try:
        from core.backtest_engine_v5 import BacktestEngineV5
        from config import Config
        
        data = request.get_json()
        
        # Extract parameters
        symbol = data.get('symbol', 'XAUUSD')
        entry_timeframe = data.get('entryTimeframe', '5m')
        test_period = data.get('testPeriod', '1mo')
        
        htf_market_bias = data.get('htfMarketBias', {})
        liquidity_sweep = data.get('liquiditySweep', {})
        displacement_entry = data.get('displacementEntry', {})
        additional_blocks = data.get('additionalBlocks', [])  # New: extra ICT blocks
        risk = data.get('risk', {})
        
        # Hard Limits Enforcement (Guardrail G8)
        # 0. Rate limiting check (10 req/10min for beta)
        client_ip = get_client_ip()
        allowed, remaining, reset_time = check_rate_limit(
            client_ip,
            Config.RATE_LIMIT_REQUESTS,
            Config.RATE_LIMIT_WINDOW_MINUTES
        )
        if not allowed:
            return error_response(
                ERROR_CODES['RATE_LIMIT_EXCEEDED'],
                f'Rate limit exceeded. Maximum {Config.RATE_LIMIT_REQUESTS} requests per {Config.RATE_LIMIT_WINDOW_MINUTES} minutes.',
                details={
                    'max_requests': Config.RATE_LIMIT_REQUESTS,
                    'window_minutes': Config.RATE_LIMIT_WINDOW_MINUTES,
                    'reset_time': reset_time.isoformat(),
                    'suggestion': f'Please wait until {reset_time.strftime("%H:%M:%S")} before trying again.'
                },
                status_code=429
            )
        
        # 1. Max period check (6mo for beta)
        period_months_map = {'1mo': 1, '2mo': 2, '3mo': 3, '6mo': 6, '1y': 12, '2y': 24}
        requested_months = period_months_map.get(test_period, 1)
        if requested_months > Config.MAX_PERIOD_MONTHS:
            return error_response(
                ERROR_CODES['INVALID_PARAMETERS'],
                f'Test period exceeds maximum allowed ({Config.MAX_PERIOD_MONTHS} months).',
                details={
                    'requested_period': test_period,
                    'requested_months': requested_months,
                    'max_allowed_months': Config.MAX_PERIOD_MONTHS,
                    'suggestion': f'Use a period of {Config.MAX_PERIOD_MONTHS} months or less.'
                },
                status_code=400
            )
        
        # 2. Max modules check (10 for beta)
        if len(additional_blocks) > Config.MAX_MODULES_PER_STRATEGY:
            return error_response(
                ERROR_CODES['MAX_BLOCKS_EXCEEDED'],
                f'Too many additional blocks. Maximum allowed: {Config.MAX_MODULES_PER_STRATEGY}.',
                details={
                    'requested_count': len(additional_blocks),
                    'max_allowed': Config.MAX_MODULES_PER_STRATEGY,
                    'suggestion': f'Reduce to {Config.MAX_MODULES_PER_STRATEGY} blocks or fewer.'
                },
                status_code=400
            )
        
        # Build strategy name
        strategy_name = f"ICT V5 - {symbol} ({entry_timeframe})"
        
        print(f"[BACKTEST-V5] Running {strategy_name}")
        print(f"[BACKTEST-V5] HTF: {htf_market_bias.get('timeframe')}, Sweep: {liquidity_sweep.get('sweepType')}, Entry: {displacement_entry.get('entryMethod')}")
        print(f"[BACKTEST-V5] Additional blocks: {len(additional_blocks)}")
        if additional_blocks:
            for block in additional_blocks:
                print(f"[BACKTEST-V5]   - {block.get('moduleId') or block.get('module_id')}: {block.get('config', {})}")
        
        # Run backtest
        engine = BacktestEngineV5()
        trades = engine.run_ict_backtest(
            symbol=symbol,
            entry_timeframe=entry_timeframe,
            test_period=test_period,
            htf_market_bias=htf_market_bias,
            liquidity_sweep=liquidity_sweep,
            displacement_entry=displacement_entry,
            additional_blocks=additional_blocks,  # New: extra ICT blocks
            risk=risk
        )
        
        print(f"[BACKTEST-V5] Generated {len(trades)} trades")
        
        if not trades:
            return render_template('no_trades_error.html',
                                 strategy_info={
                                     'market': symbol,
                                     'timeframe': entry_timeframe,
                                     'period': test_period,
                                     'blocks_count': 3
                                 },
                                 debug_info=None)
        
        # Analyze results
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        # Generate PDF report
        generator = PlaywrightReportGenerator()
        pdf_bytes = generator.generate_report(results, trades, strategy={'name': strategy_name})
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"backtest_v5_{symbol}_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"[BACKTEST-V5] PDF saved: {pdf_filename}")
        
        # Generate CSV export
        csv_filename = f"backtest_v5_{symbol}_{timestamp}.csv"
        csv_path = os.path.join(app.config['OUTPUT_FOLDER'], csv_filename)
        
        # Convert trades to DataFrame and save as CSV
        import pandas as pd
        trades_data = []
        for trade in trades:
            trades_data.append({
                'Entry Time': trade.timestamp_open.strftime('%Y-%m-%d %H:%M:%S') if hasattr(trade.timestamp_open, 'strftime') else str(trade.timestamp_open),
                'Exit Time': trade.timestamp_close.strftime('%Y-%m-%d %H:%M:%S') if hasattr(trade.timestamp_close, 'strftime') else str(trade.timestamp_close),
                'Direction': trade.direction,
                'Entry Price': round(trade.entry_price, 4),
                'Exit Price': round(trade.exit_price, 4),
                'Stop Loss': round(trade.sl, 4) if hasattr(trade, 'sl') else '',
                'Take Profit': round(trade.tp, 4) if hasattr(trade, 'tp') else '',
                'Profit (USD)': round(trade.profit_usd, 2),
                'Profit (R)': round(trade.profit_r, 2),
                'Result': trade.result
            })
        
        df_trades = pd.DataFrame(trades_data)
        df_trades.to_csv(csv_path, index=False)
        print(f"[BACKTEST-V5] CSV saved: {csv_filename}")
        
        # Return results page
        return render_template('results.html',
                             results=results,
                             pdf_filename=pdf_filename,
                             csv_filename=csv_filename,
                             trades_count=len(trades),
                             trades=trades,
                             source='backtest_v5',
                             strategy=strategy_name)
        
    except Exception as e:
        print(f"[ERROR] Backtest-v5 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(
            ERROR_CODES['BACKTEST_ERROR'],
            f'ICT backtest execution failed: {str(e)}',
            details={'exception_type': type(e).__name__},
            status_code=500
        )


def convert_decision_blocks_to_conditions(decision_blocks):
    """
    Convert Decision Blocks to backtest-engine compatible conditions.
    Maps sub-confirmation labels to appropriate modules.
    """
    from core.strategy_modules.registry import get_registry
    
    registry = get_registry()
    conditions = []
    
    # Track which modules have already been added (prevent duplicates)
    # Only track by module_id - each module can only be used once regardless of config
    added_module_ids = set()
    
    print(f"[CONVERT] Starting conversion of {len(decision_blocks)} Decision Blocks")
    
    # Mapping from sub-confirmation labels/keywords to module IDs
    # Uses actual modules from strategy_modules directory
    LABEL_TO_MODULE_MAPPING = {
        # RSI
        'rsi': 'rsi',
        'oversold': 'rsi',
        'overbought': 'rsi',
        
        # Moving Averages
        'ma': 'sma',
        'moving average': 'sma',
        'sma': 'sma',
        'ema': 'sma',
        'golden cross': 'sma',
        'cross': 'sma',
        
        # MACD
        'macd': 'macd',
        
        # Bollinger Bands
        'bollinger': 'bollinger',
        'bb': 'bollinger',
        
        # Trend Indicators
        'supertrend': 'supertrend',
        'trend': 'supertrend',
        'adx': 'adx',
        'aroon': 'aroon',
        'ichimoku': 'ichimoku',
        'parabolic': 'parabolic_sar',
        'sar': 'parabolic_sar',
        
        # Momentum Indicators
        'stochastic': 'stochastic',
        'stoch': 'stochastic',
        'momentum': 'momentum_indicator',
        'divergence': 'momentum_indicator',
        'cci': 'cci',
        'mfi': 'mfi',
        'roc': 'roc',
        'williams': 'williams_r',
        'williams r': 'williams_r',
        'ultimate': 'ultimate_oscillator',
        'tsi': 'tsi',
        
        # Volatility
        'atr': 'atr',
        'volatility': 'atr',
        'keltner': 'keltner_channels',
        'donchian': 'donchian_channels',
        
        # Volume
        'vwap': 'vwap',
        'volume profile': 'volume_profile',
        'obv': 'obv',
        'cmf': 'cmf',
        'ad line': 'ad_line',
        'accumulation': 'ad_line',
        
        # ICT Modules
        'fair value gap': 'fair_value_gaps',
        'fvg': 'fair_value_gaps',
        'liquidity sweep': 'liquidity_sweep',
        'sweep': 'liquidity_sweep',
        'premium': 'premium_discount_zones',
        'discount': 'premium_discount_zones',
        'premium discount': 'premium_discount_zones',
        'market structure': 'market_structure_shift',
        'structure': 'market_structure_shift',
        'mss': 'market_structure_shift',
        'displacement': 'displacement',
        'order block': 'order_blocks',
        'orderblock': 'order_blocks',
        'killzone': 'kill_zones',
        'kill zone': 'kill_zones',
        'breaker': 'breaker_blocks',
        'mitigation': 'mitigation_blocks',
        'imbalance': 'imbalance_zones',
        'inducement': 'inducement',
        
        # Support/Resistance
        'pivot': 'pivot_points',
        'fibonacci': 'fibonacci',
        'fib': 'fibonacci',
        'camarilla': 'camarilla',
        'sr zone': 'sr_zones',
        'support resistance': 'sr_zones',
    }
    
    for block in decision_blocks:
        # Get all selected sub-confirmations
        selected_confirmations = [
            conf for conf in block.get('subConfirmations', [])
            if conf.get('selected', False) or (conf.get('type') == 'dropdown' and conf.get('selected'))
        ]
        
        if not selected_confirmations:
            continue  # Skip blocks with no selected confirmations
        
        # For each selected sub-confirmation, create a condition
        for conf in selected_confirmations:
            try:
                # Get config from sub-confirmation
                conf_config = conf.get('config', {})
                operator = conf_config.get('operator', '>')
                value = conf_config.get('value')
                period = conf_config.get('period', 14)
                
                # Determine module - FIRST check explicit moduleId, THEN fallback to label mapping
                module_id = conf.get('moduleId')  # Use explicit moduleId if provided
                label_lower = conf.get('label', '').lower()  # Always define for special handling
                
                if not module_id:
                    # Fallback to label-based mapping
                    module_id = 'rsi'  # Default fallback
                    
                    # Try to find matching module
                    for keyword, mod_id in LABEL_TO_MODULE_MAPPING.items():
                        if keyword in label_lower:
                            module_id = mod_id
                            break
                
                # Special handling for specific patterns with defaults (only if label available)
                if label_lower and ('rsi' in label_lower or 'oversold' in label_lower or 'overbought' in label_lower):
                    module_id = 'rsi'
                    if value is None:
                        if operator == '<' or 'oversold' in label_lower:
                            value = 30
                        elif operator == '>' or 'overbought' in label_lower:
                            value = 70
                    if not period:
                        period = 14
                elif 'ma' in label_lower or 'moving average' in label_lower or 'cross' in label_lower or 'golden' in label_lower:
                    module_id = 'sma'
                    if not period:
                        period = 20
                elif 'macd' in label_lower:
                    module_id = 'macd'
                    if not period:
                        period = 12  # MACD fast period
                elif 'momentum' in label_lower and 'divergence' in label_lower:
                    module_id = 'momentum_indicator'
                    if not period:
                        period = 14
                elif 'stochastic' in label_lower or 'stoch' in label_lower:
                    module_id = 'stochastic'
                    if not period:
                        period = 14
                elif 'supertrend' in label_lower:
                    module_id = 'supertrend'
                    if not period:
                        period = 10  # ATR period for supertrend
                elif 'vwap' in label_lower:
                    module_id = 'vwap'
                    if not period:
                        period = 20
                elif 'atr' in label_lower or ('volatility' in label_lower and 'sufficient' in label_lower):
                    module_id = 'atr'
                    if not period:
                        period = 14
                elif 'fair value gap' in label_lower or 'fvg' in label_lower:
                    module_id = 'fair_value_gaps'
                elif 'liquidity sweep' in label_lower or ('liquidity' in label_lower and 'sweep' in label_lower):
                    module_id = 'liquidity_sweep'
                elif 'premium' in label_lower or 'discount' in label_lower:
                    module_id = 'premium_discount_zones'
                elif 'market structure' in label_lower or 'structure' in label_lower and 'shift' not in label_lower:
                    module_id = 'market_structure_shift'
                elif 'displacement' in label_lower:
                    module_id = 'displacement'
                elif 'order block' in label_lower or 'orderblock' in label_lower:
                    module_id = 'order_blocks'
                elif 'killzone' in label_lower or 'kill zone' in label_lower:
                    module_id = 'kill_zones'
                elif 'bollinger' in label_lower or 'bb' in label_lower:
                    module_id = 'bollinger'
                    if not period:
                        period = 20
                elif 'rejection' in label_lower or 'candle' in label_lower:
                    # Price action patterns - use RSI as fallback
                    module_id = 'rsi'
                    if not period:
                        period = 14
                elif 'equal' in label_lower and ('high' in label_lower or 'low' in label_lower):
                    # Equal highs/lows - use liquidity_sweep
                    module_id = 'liquidity_sweep'
                elif 'stop hunt' in label_lower or 'inducement' in label_lower:
                    module_id = 'inducement'
                
                # Get module from registry
                try:
                    module_class = registry.get_module(module_id)
                    module_instance = module_class()
                except ValueError:
                    # Module not found, try RSI as fallback
                    print(f"Module '{module_id}' not found, using RSI as fallback for '{conf.get('label')}'")
                    module_class = registry.get_module('rsi')
                    module_instance = module_class()
                    module_id = 'rsi'
                
                # Build config - pass ALL config parameters from conf.config
                # This allows modules to receive their specific parameters (e.g., fast_period, slow_period, atr_period, multiplier, etc.)
                module_config = {}
                
                # Copy all config parameters from conf.config
                if conf_config:
                    for key, val in conf_config.items():
                        # Skip operator and value as they are handled separately
                        if key not in ['operator', 'value']:
                            if val is not None and val != '':
                                # Convert to appropriate type
                                if isinstance(val, (int, float)):
                                    module_config[key] = val
                                elif isinstance(val, str):
                                    # Try to convert string numbers
                                    try:
                                        if '.' in val:
                                            module_config[key] = float(val)
                                        else:
                                            module_config[key] = int(val)
                                    except ValueError:
                                        module_config[key] = val
                                else:
                                    module_config[key] = val
                
                # Legacy support: if period is set but not in config, add it
                if period and period > 0 and 'period' not in module_config:
                    module_config['period'] = int(period)
                
                # Check if this module_id already exists (each module can only be used once)
                if module_id in added_module_ids:
                    # Module already added - skip this duplicate
                    print(f"[CONVERT] ⚠️ Skipping duplicate module: {module_id} (from '{conf.get('label')}')")
                    print(f"[CONVERT]   Already added modules: {list(added_module_ids)}")
                    continue
                
                # Mark as added
                added_module_ids.add(module_id)
                print(f"[CONVERT] ✓ Added module: {module_id} (from '{conf.get('label')}')")
                
                # Only add operator/value if they are set
                condition = {
                    'module': module_instance,
                    'module_id': module_id,
                    'config': module_config
                }
                
                if operator:
                    condition['operator'] = operator
                if value is not None:
                    condition['value'] = float(value) if value != '' else None
                
                conditions.append(condition)
                
            except Exception as e:
                print(f"Error loading module for sub-confirmation '{conf.get('label')}': {e}")
                import traceback
                traceback.print_exc()
                continue
    
    print(f"[CONVERT] Conversion complete: {len(conditions)} conditions from {len(added_module_ids)} unique modules")
    print(f"[CONVERT] Module IDs used: {list(added_module_ids)}")
    
    return conditions


@app.route('/run-backtest-v3', methods=['POST'])
def run_backtest_v3():
    """V3: Strategy Builder with mental promise and structured flow"""
    try:
        from core.strategy_modules.registry import get_registry
        
        data = request.get_json()
        
        # Extract market context
        market_context = data.get('marketContext', {})
        symbol = market_context.get('market', 'XAUUSD')
        timeframe = market_context.get('timeframe', '15m')
        direction_raw = market_context.get('direction', 'Long')
        direction = 'LONG' if direction_raw.upper() in ['LONG', 'BOTH'] else 'SHORT'
        period = market_context.get('testPeriod', '2mo')
        session_raw = market_context.get('session', '').strip()
        session = session_raw if session_raw and session_raw != 'All' else None
        
        # Extract exit & risk
        exit_data = data.get('exit', {})
        tp_r = float(exit_data.get('takeProfit', 2.0))
        sl_r = float(exit_data.get('stopLoss', 1.0))
        
        # Extract flow-specific data
        flow = data.get('flow', 'A')
        conditions = []
        
        if flow == 'A':
            # Flow A: Clear Strategy - rules are text descriptions
            # For v3, we'll need to parse rules or use a simple approach
            # For now, we'll create a placeholder condition
            rules = data.get('rules', [])
            if not rules:
                return {'success': False, 'error': 'No rules specified'}, 400
            
            # Note: In a full implementation, rules would be parsed/structured
            # For now, we'll use a default RSI condition as placeholder
            # TODO: Implement rule parsing or structured rule builder
            registry = get_registry()
            try:
                rsi_module = registry.get_module('rsi')
                conditions.append({
                    'module': rsi_module(),
                    'module_id': 'rsi',
                    'config': {'period': 14},
                    'operator': '>',
                    'value': 30
                })
            except:
                pass
        
        elif flow == 'B':
            # Flow B: Explore Idea - logic conditions
            logic = data.get('logic', {})
            idea = data.get('idea', '')
            
            if not logic.get('primaryCondition'):
                return {'success': False, 'error': 'No primary condition defined'}, 400
            
            # For v3, logic conditions are placeholders
            # TODO: Implement full logic condition builder
            # For now, use default RSI condition
            registry = get_registry()
            try:
                rsi_module = registry.get_module('rsi')
                conditions.append({
                    'module': rsi_module(),
                    'module_id': 'rsi',
                    'config': {'period': 14},
                    'operator': '>',
                    'value': 30
                })
            except:
                pass
        
        if not conditions:
            return error_response(
                ERROR_CODES['NO_VALID_CONDITIONS'],
                'No entry conditions specified. Please add at least one condition.',
                details={'conditions_count': 0}
            )
        
        # Build strategy name
        strategy_name = f"{direction} {symbol} ({timeframe})"
        if flow == 'B':
            idea_names = {
                'trend-continuation': 'Trend Continuation',
                'mean-reversion': 'Mean Reversion',
                'breakout': 'Breakout',
                'liquidity-sweep': 'Liquidity Sweep',
                'momentum-push': 'Momentum Push'
            }
            idea_name = idea_names.get(idea, idea)
            strategy_name = f"{idea_name} - {strategy_name}"
        
        # Run backtest
        print(f"[BACKTEST-V3] Running {strategy_name} with {len(conditions)} conditions")
        engine = BacktestEngine()
        trades = engine.run_modular(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            period=period,
            session=session,
            tp_r=tp_r,
            sl_r=sl_r,
            modules=conditions
        )
        
        print(f"[BACKTEST-V3] Generated {len(trades)} trades")
        
        if not trades:
            return error_response(
                ERROR_CODES['NO_TRADES_GENERATED'],
                'No trades generated. Try different conditions or period.',
                details={
                    'suggestion': 'Consider: (1) Loosening entry conditions, (2) Increasing test period, (3) Trying different timeframes or sessions.'
                },
                status_code=200
            )
        
        # Analyze results
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        # Generate PDF report
        generator = PlaywrightReportGenerator()
        pdf_bytes = generator.generate_report(results, trades, strategy={'name': strategy_name})
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"backtest_v3_{symbol}_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"[BACKTEST-V3] PDF saved: {pdf_filename}")
        
        # Return results page
        return render_template('results.html',
                             results=results,
                             pdf_filename=pdf_filename,
                             trades_count=len(trades),
                             trades=trades,
                             source='backtest_v3',
                             strategy=strategy_name)
        
    except Exception as e:
        print(f"[ERROR] Backtest-v3 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(
            ERROR_CODES['BACKTEST_ERROR'],
            f'Backtest execution failed: {str(e)}',
            details={'exception_type': type(e).__name__},
            status_code=500
        )


@app.route('/run-backtest-v2', methods=['POST'])
def run_backtest_v2():
    """NEW: Modular strategy backtest with dynamic modules"""
    try:
        from core.strategy_modules.registry import get_registry
        
        data = request.get_json()
        
        # Extract basic strategy parameters
        symbol = data.get('symbol', 'XAUUSD')
        timeframe = data.get('timeframe', '15m')
        direction = data.get('direction', 'LONG')
        period = data.get('period', '2mo')
        session_raw = data.get('session', '').strip()
        session = session_raw if session_raw else None
        tp_r = float(data.get('tp_r', 2.0))
        sl_r = float(data.get('sl_r', 1.0))
        
        # Extract module-based conditions
        conditions = data.get('conditions', [])
        
        if not conditions:
            return error_response(
                ERROR_CODES['NO_VALID_CONDITIONS'],
                'No entry conditions specified. Please add at least one condition.',
                details={'conditions_count': 0}
            )
        
        # Load and instantiate modules
        registry = get_registry()
        strategy_modules = []
        
        for condition in conditions:
            category = condition.get('category')
            module_id = condition.get('module')
            config = condition.get('config', {})
            operator = condition.get('operator')
            value = condition.get('value')
            
            if not category or not module_id:
                return error_response(
                    ERROR_CODES['INVALID_PARAMETERS'],
                    'Invalid condition format. Both category and module are required.',
                    details={'category': category, 'module_id': module_id}
                )
            
            # Validate operator and value if provided
            if operator is not None and value is None:
                return error_response(
                    ERROR_CODES['INVALID_PARAMETERS'],
                    'Value required when operator is specified.',
                    details={'operator': operator, 'value': value}
                )
            
            # Get module from registry (registry stores by module_id only)
            try:
                module_class = registry.get_module(module_id)
            except ValueError as e:
                return error_response(
                    ERROR_CODES['INVALID_MODULE'],
                    f'Module not found: {module_id}',
                    details={
                        'module_id': module_id,
                        'available_modules': list(registry.list_available_modules().keys()) if hasattr(registry, 'list_available_modules') else []
                    },
                    status_code=404
                )
            
            # Instantiate module (no config in __init__)
            try:
                module_instance = module_class()
                # Store module with its config, operator, value, and module_id
                strategy_modules.append({
                    'module': module_instance,
                    'module_id': module_id,  # Store module_id for column name resolution
                    'config': config,
                    'operator': operator,
                    'value': value
                })
            except Exception as e:
                return error_response(
                    ERROR_CODES['MODULE_ERROR'],
                    f'Module error: {str(e)}',
                    details={'module_id': module_id, 'exception_type': type(e).__name__}
                )
        
        # Build strategy name
        strategy_name = f"{direction} {symbol} ({timeframe})"
        
        # Run backtest with modules
        print(f"[BACKTEST-V2] Running {strategy_name} with {len(strategy_modules)} modules")
        engine = BacktestEngine()
        trades = engine.run_modular(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            period=period,
            session=session,
            tp_r=tp_r,
            sl_r=sl_r,
            modules=strategy_modules
        )
        
        print(f"[BACKTEST-V2] Generated {len(trades)} trades")
        
        if not trades:
            return error_response(
                ERROR_CODES['NO_TRADES_GENERATED'],
                'No trades generated. Try different conditions or period.',
                details={
                    'suggestion': 'Consider: (1) Loosening entry conditions, (2) Increasing test period, (3) Trying different timeframes or sessions.'
                },
                status_code=200
            )
        
        # Analyze results
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        # Generate PDF report
        generator = PlaywrightReportGenerator()
        pdf_bytes = generator.generate_report(results, trades, strategy={'name': strategy_name})
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"backtest_v2_{symbol}_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"[BACKTEST-V2] PDF saved: {pdf_filename}")
        
        # Return results page directly (no redirect needed)
        return render_template('results.html',
                             results=results,
                             pdf_filename=pdf_filename,
                             trades_count=len(trades),
                             trades=trades,  # Pass trades list for display
                             source='backtest_v2',
                             strategy=strategy_name)
        
    except Exception as e:
        print(f"[ERROR] Backtest-v2 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(
            ERROR_CODES['BACKTEST_ERROR'],
            f'Backtest execution failed: {str(e)}',
            details={'exception_type': type(e).__name__},
            status_code=500
        )


@app.route('/run-backtest', methods=['POST'])
def run_backtest():
    try:
        symbol = request.form.get('symbol', 'XAUUSD')
        timeframe = request.form.get('timeframe', '15m')
        direction = request.form.get('direction', 'LONG')
        period = request.form.get('period', '2mo')
        
        # SESSION FIX: Properly handle empty strings
        session_raw = request.form.get('session', '').strip()
        session = session_raw if session_raw else None
        
        print(f"[BACKTEST] Session filter: {session} (raw: '{session_raw}')")
        
        tp_r = float(request.form.get('tp_r', 1.5))
        sl_r = float(request.form.get('sl_r', 1.0))
        
        condition_count = int(request.form.get('condition_count', 1))
        entry_conditions = []
        
        indicator_labels = {
            'rsi': 'RSI',
            'adx': 'ADX', 
            'macd': 'MACD',
            'sma_20': 'SMA(20)',
            'sma_50': 'SMA(50)',
            'ema_20': 'EMA(20)',
            'bb_upper': 'BB Upper',
            'bb_lower': 'BB Lower'
        }
        
        for i in range(condition_count):
            indicator = request.form.get(f'indicator_{i}')
            operator = request.form.get(f'operator_{i}')
            value = request.form.get(f'value_{i}')
            
            if indicator and operator and value:
                entry_conditions.append(EntryCondition(
                    indicator=indicator,
                    operator=operator,
                    value=float(value)
                ))
        
        if not entry_conditions:
            flash('At least one entry condition is required', 'error')
            return redirect(url_for('simulator'))
        
        # Debug: Print conditions
        print(f"[BACKTEST] Conditions: {[(c.indicator, c.operator, c.value) for c in entry_conditions]}")
        
        condition_parts = []
        for cond in entry_conditions:
            label = indicator_labels.get(cond.indicator, cond.indicator.upper())
            condition_parts.append(f"{label}{cond.operator}{cond.value}")
        
        strategy_name = f"{direction} {symbol} - {' AND '.join(condition_parts)}"
        
        strategy = StrategyDefinition(
            name=strategy_name,
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            entry_conditions=entry_conditions,
            tp_r=tp_r,
            sl_r=sl_r,
            session=session,
            period=period
        )
        
        print(f"[BACKTEST] Running strategy: {strategy_name}")
        engine = BacktestEngine()
        trades = engine.run(strategy)
        
        print(f"[BACKTEST] Generated {len(trades)} trades")
        
        if not trades:
            flash('No trades generated. Try adjusting your conditions or period.', 'warning')
            return redirect(url_for('simulator'))
        
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        print(f"[BACKTEST] Analysis complete - Win Rate: {results.get('win_rate', 0):.1f}%")
        
        generator = PlaywrightReportGenerator()
        pdf_bytes = generator.generate_report(results, trades, strategy=strategy)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"backtest_{symbol}_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"[BACKTEST] PDF saved: {pdf_filename}")
        
        strategy_display = f"{direction} {symbol} when "
        strategy_display += " AND ".join([
            f"{indicator_labels.get(c.indicator, c.indicator)} {c.operator} {c.value}" 
            for c in entry_conditions
        ])
        if session:
            strategy_display += f" [{session} session]"
        
        return render_template('results.html',
                             results=results,
                             pdf_filename=pdf_filename,
                             trades_count=len(trades),
                             trades=trades,  # Pass trades list for display
                             source='backtest',
                             strategy=strategy_display)
        
    except ValueError as e:
        print(f"[ERROR] ValueError in backtest: {str(e)}")
        flash(f'Backtest error: {str(e)}', 'error')
        return redirect(url_for('simulator'))
    except Exception as e:
        print(f"[ERROR] Unexpected error in backtest: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('simulator'))


@app.route('/download-test-data', methods=['POST'])
def download_test_data():
    """Pre-download test data for faster testing"""
    try:
        from core.data_manager import DataManager
        from datetime import datetime, timedelta
        
        data = request.get_json()
        symbol = data.get('symbol', 'XAUUSD')
        entry_timeframe = data.get('entryTimeframe', '5m')
        htf_timeframe = data.get('htfTimeframe', '1h')
        test_period = data.get('testPeriod', '1mo')
        
        # Convert period to dates
        period_days = {
            '1mo': 30,
            '2mo': 60,
            '3mo': 90
        }
        days = period_days.get(test_period, 30)
        end = datetime.now()
        start = end - timedelta(days=days)
        
        manager = DataManager()
        
        # Download entry timeframe data
        print(f"[TEST-DATA] Downloading {symbol} {entry_timeframe}...")
        entry_data = manager.get_data(
            symbol=symbol,
            timeframe=entry_timeframe,
            start=start,
            end=end,
            force_refresh=True  # Force download
        )
        
        # Download HTF data
        print(f"[TEST-DATA] Downloading {symbol} {htf_timeframe}...")
        htf_data = manager.get_data(
            symbol=symbol,
            timeframe=htf_timeframe,
            start=start,
            end=end,
            force_refresh=True  # Force download
        )
        
        return {
            'success': True,
            'message': f'Test data downloaded: {len(entry_data)} {entry_timeframe} rows, {len(htf_data)} {htf_timeframe} rows',
            'entry_rows': len(entry_data),
            'htf_rows': len(htf_data)
        }
    
    except Exception as e:
        print(f"[ERROR] Test data download failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(
            ERROR_CODES['BACKTEST_ERROR'],
            f'Backtest execution failed: {str(e)}',
            details={'exception_type': type(e).__name__},
            status_code=500
        )

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        flash('File not found', 'error')
        return redirect(url_for('upload_page'))
    
    # Determine mimetype and download name based on file extension
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext == '.csv':
        mimetype = 'text/csv'
        download_name = 'QuantMetrics_Trade_Log.csv'
    elif file_ext == '.pdf':
        mimetype = 'application/pdf'
        download_name = 'QuantMetrics_Analysis_Report.pdf'
    else:
        # Default to binary
        mimetype = 'application/octet-stream'
        download_name = filename
    
    return send_file(filepath, 
                    as_attachment=True,
                    download_name=download_name,
                    mimetype=mimetype)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)