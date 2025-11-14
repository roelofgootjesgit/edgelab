"""
Integration Test - Analyzer → Reporter
=======================================
Test complete pipeline: Parse → Analyze → Generate PDF
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.csv_parser import CSVParser
from core.analyzer import Analyzer
from core.reporter import ModernReporter


def test_integration():
    """Test complete analysis pipeline."""
    
    print("=" * 60)
    print("INTEGRATION TEST: Parser → Analyzer → Reporter")
    print("=" * 60)
    print()
    
    # Step 1: Parse CSV
    print("Step 1: Parsing CSV...")
    try:
        parser = CSVParser()
        trades = parser.parse('tests/sample_data/trades_sample.csv')
        print(f" Parsed {len(trades)} trades")
    except Exception as e:
        print(f" Parse failed: {e}")
        return False
    
    print()
    
    # Step 2: Analyze
    print("Step 2: Analyzing trades...")
    try:
        analyzer = Analyzer()
        analysis = analyzer.calculate(trades)
        print(f" Analysis complete")
        print(f"   Win Rate: {analysis.get('win_rate', 0):.1f}%")
        print(f"   ESI: {analysis.get('esi', 0):.2f}")
        print(f"   PVS: {analysis.get('pvs', 0):.2f}")
        
        # Check what keys we have
        print(f"\n   Available keys: {list(analysis.keys())}")
        
    except Exception as e:
        print(f" Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    
    # Step 3: Generate PDF
    print("Step 3: Generating modern PDF...")
    try:
        # Create output directory
        os.makedirs('output/reports', exist_ok=True)
        
        reporter = ModernReporter()
        output_path = 'output/reports/integrated_test_report.pdf'
        
        pdf_bytes = reporter.create_pdf(
            trades=trades,
            analysis=analysis,
            output_path=output_path
        )
        
        print(f"✅ PDF generated: {len(pdf_bytes)} bytes")
        print(f"   Saved to: {os.path.abspath(output_path)}")
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 60)
    print("✅ INTEGRATION TEST PASSED")
    print("=" * 60)
    print()
    print("Next step: Open the PDF to verify content")
    print(f"Command: start {output_path}")
    print()
    
    return True


if __name__ == '__main__':
    success = test_integration()
    exit(0 if success else 1)