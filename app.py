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
- /run-backtest : Execute backtest (multi-condition support)
- /download/<filename> : Download PDF
- /api/modules : Get available strategy modules

Author: QuantMetrics Development Team
Version: 4.0 (Modular Strategy System)
"""

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

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
                             source='csv')
    
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return redirect(url_for('upload_page'))




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
            return {'success': False, 'error': 'No entry conditions specified'}, 400
        
        # Load and instantiate modules
        registry = get_registry()
        strategy_modules = []
        
        for condition in conditions:
            category = condition.get('category')
            module_id = condition.get('module')
            config = condition.get('config', {})
            
            if not category or not module_id:
                return {'success': False, 'error': 'Invalid condition format'}, 400
            
            # Get module from registry (registry stores by module_id only)
            try:
                module_class = registry.get_module(module_id)
            except ValueError as e:
                return {'success': False, 'error': f'Module not found: {module_id}'}, 404
            
            # Instantiate module (no config in __init__)
            try:
                module_instance = module_class()
                # Store module with its config
                strategy_modules.append({
                    'module': module_instance,
                    'config': config
                })
            except Exception as e:
                return {'success': False, 'error': f'Module error: {str(e)}'}, 400
        
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
            return {'success': False, 'error': 'No trades generated. Try different conditions or period.'}, 200
        
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
                             source='backtest_v2',
                             strategy=strategy_name)
        
    except Exception as e:
        print(f"[ERROR] Backtest-v2 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}, 500


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


@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        flash('File not found', 'error')
        return redirect(url_for('upload_page'))
    
    return send_file(filepath, 
                    as_attachment=True,
                    download_name='QuantMetrics_Analysis_Report.pdf',
                    mimetype='application/pdf')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)