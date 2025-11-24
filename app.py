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
- /run-backtest : Execute backtest
- /download/<filename> : Download PDF

Author: EdgeLab Development Team
Version: 2.0 (with Strategy Simulator)
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

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'edgelab-secret-key-change-in-production'
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
    """Run backtest on user-defined strategy"""
    
    try:
        # Parse form data
        symbol = request.form.get('symbol', 'XAUUSD')
        timeframe = request.form.get('timeframe', '15m')
        direction = request.form.get('direction', 'LONG')
        period = request.form.get('period', '6mo')
        
        # Entry condition
        indicator = request.form.get('indicator', 'rsi')
        operator = request.form.get('operator', '<')
        value = float(request.form.get('value', 30))
        
        # Exit rules
        tp_r = float(request.form.get('tp_r', 1.5))
        sl_r = float(request.form.get('sl_r', 1.0))
        
        # Session filter
        session = request.form.get('session', '') or None
        
        # Build strategy
        strategy = StrategyDefinition(
            name=f"{indicator} {operator} {value} Strategy",
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            entry_conditions=[
                EntryCondition(indicator, operator, value)
            ],
            tp_r=tp_r,
            sl_r=sl_r,
            session=session,
            period=period
        )
        
        # Run backtest
        engine = BacktestEngine()
        trades = engine.run(strategy)
        
        if len(trades) == 0:
            flash('No trades generated. Try adjusting your strategy parameters.', 'warning')
            return redirect(url_for('simulator'))
        
        # Analyze trades
        analyzer = BasicAnalyzer()
        results = analyzer.calculate(trades)
        
        # Generate PDF report
        generator = ModernReporter()
        pdf_bytes = generator.create_pdf(trades=trades, analysis=results, output_path=None)
        
        # Save PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_filename = f"backtest_report_{timestamp}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return render_template('results.html',
                             results=results,
                             pdf_filename=pdf_filename,
                             trades_count=len(trades),
                             source='backtest',
                             strategy=str(strategy))
    
    except Exception as e:
        flash(f'Backtest error: {str(e)}', 'error')
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