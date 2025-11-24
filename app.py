"""
app.py
======

EdgeLab Flask Web Application
Professional SaaS interface for trading analysis

Routes:
- / : Landing page
- /upload : Upload CSV
- /analyze : Process and generate report
- /simulator : Strategy simulator interface
- /run-backtest : Execute backtest (multi-condition support)
- /download/<filename> : Download PDF

Author: EdgeLab Development Team
Version: 2.1 (Multi-condition support)
"""

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from core.csv_parser import CSVParser
from core.analyzer import BasicAnalyzer
from core.reporter import ModernReporter
from core.strategy import StrategyDefinition, EntryCondition
from core.backtest_engine import BacktestEngine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'edgelab-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/upload')
def upload_page():
    """Upload interface"""
    return render_template('upload.html')


@app.route('/simulator')
def simulator():
    """Strategy simulator interface"""
    return render_template('simulator.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Process uploaded CSV and generate report"""
    
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
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        file.save(filepath)
        
        # Parse CSV
        parser = CSVParser()
        trades = parser.parse(filepath)
        
        # Analyze trades
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        # Generate PDF report
        generator = ModernReporter()
        pdf_bytes = generator.create_pdf(trades=trades, analysis=results, output_path=None)
        
        # Save PDF
        pdf_filename = f"edgelab_report_{timestamp}.pdf"
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


@app.route('/run-backtest', methods=['POST'])
def run_backtest():
    """
    Run backtest with multiple entry conditions.
    
    Form fields:
    - symbol, timeframe, direction, period, session
    - tp_r, sl_r
    - condition_count (number of conditions)
    - indicator_0, operator_0, value_0 (first condition)
    - indicator_1, operator_1, value_1 (second condition, if exists)
    - ... up to indicator_4, operator_4, value_4
    """
    
    try:
        # Basic settings
        symbol = request.form.get('symbol', 'XAUUSD')
        timeframe = request.form.get('timeframe', '15m')
        direction = request.form.get('direction', 'LONG')
        period = request.form.get('period', '2mo')
        session = request.form.get('session', '') or None
        
        # Exit rules
        tp_r = float(request.form.get('tp_r', 1.5))
        sl_r = float(request.form.get('sl_r', 1.0))
        
        # Parse multiple conditions
        condition_count = int(request.form.get('condition_count', 1))
        entry_conditions = []
        
        # Indicator display names for strategy description
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
        
        # Validate at least one condition
        if not entry_conditions:
            flash('At least one entry condition is required', 'error')
            return redirect(url_for('simulator'))
        
        # Build strategy name from conditions
        condition_parts = []
        for cond in entry_conditions:
            label = indicator_labels.get(cond.indicator, cond.indicator.upper())
            condition_parts.append(f"{label}{cond.operator}{cond.value}")
        
        strategy_name = f"{direction} {symbol} - {' AND '.join(condition_parts)}"
        
        # Create strategy definition
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
        
        # Run backtest
        engine = BacktestEngine()
        trades = engine.run(strategy)
        
        if not trades:
            flash('No trades generated. Try adjusting your conditions or period.', 'warning')
            return redirect(url_for('simulator'))
        
        # Analyze results
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        # Generate PDF report
        generator = ModernReporter()
        pdf_bytes = generator.create_pdf(
            trades=trades,
            analysis=results,
            output_path=None,
            strategy_definition=strategy
        )
        
        # Save PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"backtest_{symbol}_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Build strategy description for display
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
        flash(f'Backtest error: {str(e)}', 'error')
        return redirect(url_for('simulator'))
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(url_for('simulator'))


@app.route('/download/<filename>')
def download(filename):
    """Download generated PDF report"""
    
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        flash('File not found', 'error')
        return redirect(url_for('upload_page'))
    
    return send_file(filepath, 
                    as_attachment=True,
                    download_name='EdgeLab_Analysis_Report.pdf',
                    mimetype='application/pdf')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)