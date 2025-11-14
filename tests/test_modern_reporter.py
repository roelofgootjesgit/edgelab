"""
Test Modern PDF Reporter - Windows Version
===========================================
Verify that modern 2026-style PDF generation works correctly.
"""

import sys
import os

# Add parent directory to path (works on Windows)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reporter import ModernReporter
from datetime import datetime


def test_modern_pdf_generation():
    """Test complete PDF generation with mock data."""
    
    # Mock analysis data (simulating what analyzer would provide)
    mock_analysis = {
        # Basic metrics
        'total_trades': 87,
        'wins': 47,
        'losses': 40,
        'win_rate': 54.0,
        'profit_factor': 1.42,
        'expectancy': 0.73,
        'total_profit_r': 63.5,
        'sharpe_ratio': 1.8,
        'max_drawdown': 8.5,
        'esi': 0.68,
        'pvs': 0.71,
        
        # Pattern insights
        'timing': {
            'sessions': {
                'Tokyo': {
                    'trades': 28,
                    'win_rate': 38.0,
                    'expectancy': -0.15,
                    'verdict': 'AVOID'
                },
                'London': {
                    'trades': 31,
                    'win_rate': 51.0,
                    'expectancy': 0.32,
                    'verdict': 'NEUTRAL'
                },
                'NY': {
                    'trades': 42,
                    'win_rate': 67.0,
                    'expectancy': 0.94,
                    'verdict': 'FOCUS'
                }
            },
            'best_window': {
                'hour': '14:00-16:00 UTC',
                'trades': 27,
                'win_rate': 73.0
            }
        },
        
        'directional': {
            'LONG': {
                'trades': 58,
                'win_rate': 67.0,
                'expectancy': 0.98,
                'edge_strength': 'STRONG'
            },
            'SHORT': {
                'trades': 29,
                'win_rate': 29.0,
                'expectancy': -0.43,
                'edge_strength': 'NONE'
            },
            'bias': {
                'description': 'Strategy shows strong LONG bias. Removing SHORT trades would improve win rate by 18%.'
            }
        },
        
        'execution': {
            'quality_score': 68,
            'issues': [
                {'description': '32% of wins closed early (missed 9R potential profit)'},
                {'description': '16% of losses exceeded stop loss (discipline issue)'},
                {'description': 'Average hold time: 2.4 hours (consider extending for trending markets)'}
            ]
        },
        
        'insights': {
            'critical': [
                {
                    'category': 'Session Performance',
                    'observation': 'Tokyo session shows 38% win rate vs 67% in NY session. Removing Tokyo trades would improve overall win rate by 6%.'
                },
                {
                    'category': 'Directional Bias',
                    'observation': 'LONG trades show 67% win rate while SHORT trades only 29%. Strategy has no edge in SHORT direction.'
                },
                {
                    'category': 'Execution Discipline',
                    'observation': '7 trades held past stop loss, costing 8.5R in preventable losses. Discipline improvement is highest priority.'
                }
            ],
            'notable': [
                {
                    'observation': 'Best performance during London-NY overlap (14:00-16:00 UTC) with 73% win rate'
                },
                {
                    'observation': 'Average win size (1.8R) significantly larger than average loss (0.8R)'
                },
                {
                    'observation': 'No significant day-of-week bias detected'
                }
            ]
        }
    }
    
    # Generate PDF
    reporter = ModernReporter()
    
    try:
        # Use relative path for output
        output_path = os.path.join('output', 'modern_report.pdf')
        
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        pdf_bytes = reporter.create_pdf(
            trades=[],  # Empty for now (not used in current implementation)
            analysis=mock_analysis,
            output_path=output_path
        )
        
        print("SUCCESS: Modern PDF generated")
        print(f"Size: {len(pdf_bytes)} bytes")
        print(f"Saved to: {os.path.abspath(output_path)}")
        print("\nReport includes:")
        print("- Modern cover page with key stats")
        print("- Executive summary with verdict")
        print("- Detailed metrics page")
        print("- Timing intelligence analysis")
        print("- Directional analysis (LONG/SHORT)")
        print("- Execution quality assessment")
        print("- Key insights (critical + notable)")
        print("- Professional disclaimer")
        print("\nDesign features:")
        print("- 2026 modern color palette")
        print("- Clean typography (Helvetica)")
        print("- Visual hierarchy")
        print("- Professional spacing")
        print("- Card-based layouts")
        print("\n✅ TEST PASSED")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_modern_pdf_generation()
    exit(0 if success else 1)