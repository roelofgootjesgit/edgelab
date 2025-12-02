"""
Test script for Playwright PDF generation
Generates a sample report using mock trading data
"""

from core.playwright_reporter import PlaywrightReportGenerator
from datetime import datetime


def create_mock_results():
    """Create mock analysis results for testing."""
    class Results:
        def __init__(self):
            self.win_rate = 65.5
            self.esi = 1.42
            self.pvs = 0.85
            self.profit_factor = 2.30
            self.avg_win = 150.50
            self.avg_loss = 85.30
            self.rr_ratio = 1.76
            self.winning_trades = 13
            self.losing_trades = 7
            self.best_session = 'NY Session'
            self.worst_session = 'London'
    
    return Results()


def create_mock_trades():
    """Create mock trade list for testing."""
    # Simple list of 20 trades
    return list(range(20))


def create_mock_insights():
    """Create mock pattern analysis insights."""
    return {
        'critical_findings': [
            'Average loss size exceeds optimal risk parameters by 15%',
            'Win rate drops below 50% during London session'
        ],
        'notable_patterns': [
            'Best performance occurs between 14:00-18:00 UTC',
            'Long positions outperform short positions by 2:1 ratio',
            'Trade execution quality improves significantly on Tuesdays'
        ]
    }


if __name__ == '__main__':
    print("EdgeLab Playwright PDF Generator Test")
    print("=" * 50)
    
    # Create mock data
    results = create_mock_results()
    trades = create_mock_trades()
    insights = create_mock_insights()
    
    print(f"\n✓ Mock data created:")
    print(f"  - {len(trades)} trades")
    print(f"  - Win rate: {results.win_rate}%")
    print(f"  - ESI: {results.esi}")
    print(f"  - PVS: {results.pvs}")
    
    # Generate PDF
    print("\nGenerating PDF with Playwright...")
    
    try:
        generator = PlaywrightReportGenerator()
        pdf_bytes = generator.generate_report(
            results=results,
            trades=trades,
            insights=insights
        )
        
        # Save to file
        output_file = 'test_report_playwright.pdf'
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"\n✓ PDF generated successfully!")
        print(f"  - File: {output_file}")
        print(f"  - Size: {len(pdf_bytes):,} bytes")
        print(f"\nOpen the PDF to verify:")
        print(f"  - Cover page with building background")
        print(f"  - Logo icons on all pages")
        print(f"  - Professional styling throughout")
        
    except Exception as e:
        print(f"\n✗ Error generating PDF:")
        print(f"  {type(e).__name__}: {e}")
        print(f"\nMake sure Playwright is installed:")
        print(f"  pip install playwright")
        print(f"  playwright install chromium")
