"""
Integration Test - Flexible Version
====================================
Works with any analyzer structure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("FLEXIBLE INTEGRATION TEST")
print("=" * 60)
print()

# Step 1: Check what we have
print("Step 1: Checking available modules...")
print()

try:
    from core.csv_parser import CSVParser
    print("✅ CSVParser found")
except ImportError as e:
    print(f"❌ CSVParser not found: {e}")
    exit(1)

try:
    from core.reporter import ModernReporter
    print("✅ ModernReporter found")
except ImportError as e:
    print(f"❌ ModernReporter not found: {e}")
    exit(1)

# Try to find analyzer
analyzer_found = False
analyzer_class = None

try:
    from core.analyzer import Analyzer
    analyzer_class = Analyzer
    analyzer_found = True
    print("✅ Analyzer found")
except ImportError:
    try:
        from core.analyzer import BasicAnalyzer
        analyzer_class = BasicAnalyzer
        analyzer_found = True
        print("✅ BasicAnalyzer found")
    except ImportError:
        print("❌ No analyzer found")
        print()
        print("Available in core.analyzer:")
        import core.analyzer as analyzer_module
        print([x for x in dir(analyzer_module) if not x.startswith('_')])
        print()
        print("Please use one of these classes.")
        exit(1)

print()

# Step 2: Parse sample data
print("Step 2: Parsing sample CSV...")
try:
    parser = CSVParser()
    
    # Try to find sample data
    sample_paths = [
        'tests/sample_data/trades_sample.csv',
        'sample_data/trades_sample.csv',
        'tests/trades_sample.csv'
    ]
    
    trades = None
    for path in sample_paths:
        if os.path.exists(path):
            trades = parser.parse(path)
            print(f"✅ Parsed {len(trades)} trades from {path}")
            break
    
    if trades is None:
        print("❌ No sample data found. Tried:")
        for path in sample_paths:
            print(f"   - {path}")
        print()
        print("Creating mock data instead...")
        
        # Create mock trades for testing
        from datetime import datetime
        from core.edgelab_schema import EdgeLabTrade
        
        trades = [
            EdgeLabTrade(
                timestamp_open=datetime(2024, 1, 15, 14, 30),
                timestamp_close=datetime(2024, 1, 15, 15, 45),
                symbol='XAUUSD',
                direction='LONG',
                entry_price=2050.0,
                exit_price=2065.0,
                sl=2045.0,
                tp=2060.0,
                profit_usd=150.0,
                profit_r=3.0,
                result='WIN'
            ),
            EdgeLabTrade(
                timestamp_open=datetime(2024, 1, 15, 16, 0),
                timestamp_close=datetime(2024, 1, 15, 16, 45),
                symbol='XAUUSD',
                direction='SHORT',
                entry_price=2058.0,
                exit_price=2053.5,
                sl=2062.0,
                tp=2050.0,
                profit_usd=45.0,
                profit_r=1.13,
                result='WIN'
            ),
        ]
        print(f"✅ Created {len(trades)} mock trades")
        
except Exception as e:
    print(f"❌ Parse failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# Step 3: Analyze
print("Step 3: Analyzing trades...")
try:
    analyzer = analyzer_class()
    
    # Try calculate method
    if hasattr(analyzer, 'calculate'):
        analysis = analyzer.calculate(trades)
    elif hasattr(analyzer, 'analyze'):
        analysis = analyzer.analyze(trades)
    else:
        print("❌ Analyzer has no calculate() or analyze() method")
        print(f"   Available methods: {[x for x in dir(analyzer) if not x.startswith('_')]}")
        exit(1)
    
    print("✅ Analysis complete")
    
    # Show what we got
    if isinstance(analysis, dict):
        print(f"   Type: dict with {len(analysis)} keys")
        print(f"   Keys: {list(analysis.keys())[:5]}...")
        
        # Show some metrics
        if 'win_rate' in analysis:
            print(f"   Win Rate: {analysis['win_rate']:.1f}%")
        if 'esi' in analysis:
            print(f"   ESI: {analysis['esi']:.2f}")
        if 'pvs' in analysis:
            print(f"   PVS: {analysis['pvs']:.2f}")
    else:
        print(f"   Type: {type(analysis)}")
        print(f"   Content: {str(analysis)[:100]}...")
    
except Exception as e:
    print(f"❌ Analysis failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# Step 4: Generate PDF
print("Step 4: Generating PDF...")
try:
    os.makedirs('output/reports', exist_ok=True)
    
    reporter = ModernReporter()
    output_path = 'output/reports/flexible_test_report.pdf'
    
    # Reporter needs dict format
    if not isinstance(analysis, dict):
        print("⚠️  Converting analysis to dict format...")
        # Try to convert dataclass or object to dict
        if hasattr(analysis, '__dict__'):
            analysis = analysis.__dict__
        else:
            print("❌ Cannot convert analysis to dict")
            exit(1)
    
    pdf_bytes = reporter.create_pdf(
        trades=trades,
        analysis=analysis,
        output_path=output_path
    )
    
    print(f"✅ PDF generated: {len(pdf_bytes)} bytes")
    print(f"   Location: {os.path.abspath(output_path)}")
    
except Exception as e:
    print(f"❌ PDF generation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()
print("=" * 60)
print("✅ FLEXIBLE INTEGRATION TEST PASSED")
print("=" * 60)
print()
print("Next: Open the PDF to verify")
print(f"Command: start {output_path}")
print()
