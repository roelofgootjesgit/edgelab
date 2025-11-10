"""
Test InsightGenerator
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.pattern_analyzer import (
    TimingAnalyzer, DirectionalAnalyzer, 
    ExecutionAnalyzer, LossForensics, InsightGenerator
)
from core.edgelab_schema import EdgeLabTrade
from datetime import datetime

def test_insight_generation():
    """Test insight synthesis from all analyzers"""
    
    # Create test trades with clear patterns
    trades = [
        # Tokyo losses
        EdgeLabTrade(
            timestamp_open=datetime(2024, 1, 15, 2, 30),
            timestamp_close=datetime(2024, 1, 15, 3, 0),
            symbol="XAUUSD", direction="SHORT",
            entry_price=2050.0, exit_price=2055.0,
            sl=2053.0, tp=2040.0,
            profit_usd=-50.0, profit_r=-1.0, result="LOSS",
            rr=-1.0, session="Tokyo", source="test", confidence=100
        ),
        # NY LONG wins
        EdgeLabTrade(
            timestamp_open=datetime(2024, 1, 15, 15, 0),
            timestamp_close=datetime(2024, 1, 15, 16, 30),
            symbol="XAUUSD", direction="LONG",
            entry_price=2055.0, exit_price=2070.0,
            sl=2050.0, tp=2070.0,
            profit_usd=150.0, profit_r=3.0, result="WIN",
            rr=3.0, session="NY", source="test", confidence=100
        ),
        EdgeLabTrade(
            timestamp_open=datetime(2024, 1, 16, 14, 30),
            timestamp_close=datetime(2024, 1, 16, 15, 45),
            symbol="XAUUSD", direction="LONG",
            entry_price=2050.0, exit_price=2065.0,
            sl=2045.0, tp=2065.0,
            profit_usd=150.0, profit_r=3.0, result="WIN",
            rr=3.0, session="NY", source="test", confidence=100
        ),
        # SHORT loss (directional pattern)
        EdgeLabTrade(
            timestamp_open=datetime(2024, 1, 17, 16, 0),
            timestamp_close=datetime(2024, 1, 17, 16, 45),
            symbol="XAUUSD", direction="SHORT",
            entry_price=2058.0, exit_price=2062.0,
            sl=2062.0, tp=2050.0,
            profit_usd=-40.0, profit_r=-1.0, result="LOSS",
            rr=-1.0, session="NY", source="test", confidence=100
        ),
    ]
    
    # Run all analyzers
    timing_analyzer = TimingAnalyzer()
    directional_analyzer = DirectionalAnalyzer()
    execution_analyzer = ExecutionAnalyzer()
    loss_analyzer = LossForensics()
    
    timing_results = timing_analyzer.analyze(trades)
    directional_results = directional_analyzer.analyze(trades)
    execution_results = execution_analyzer.analyze(trades)
    loss_results = loss_analyzer.analyze(trades)
    
    # Basic metrics
    wins = len([t for t in trades if t.result == 'WIN'])
    basic_metrics = {
        'total_trades': len(trades),
        'wins': wins,
        'winrate': (wins / len(trades)) * 100
    }
    
    # Generate insights
    insight_gen = InsightGenerator()
    insights = insight_gen.generate(
        timing_results,
        directional_results,
        execution_results,
        loss_results,
        basic_metrics,
        trades
    )
    
    # Verify structure
    assert 'critical_findings' in insights
    assert 'notable_patterns' in insights
    assert 'performance_correlations' in insights
    assert 'statistical_summary' in insights
    
    # Verify findings detected
    assert len(insights['critical_findings']) > 0 or len(insights['notable_patterns']) > 0
    
    # Verify statistical summary
    assert 'total_findings' in insights['statistical_summary']
    assert 'overall_assessment' in insights['statistical_summary']
    
    print("✅ InsightGenerator test passed!")
    print(f"\nStatistical Summary:")
    print(f"  Total Findings: {insights['statistical_summary']['total_findings']}")
    print(f"  Critical: {insights['statistical_summary']['critical_findings']}")
    print(f"  Notable: {insights['statistical_summary']['notable_patterns']}")
    
    print(f"\nCritical Findings:")
    for finding in insights['critical_findings']:
        print(f"  • {finding['title']}")
        print(f"    {finding['observation']}")
    
    print(f"\nNotable Patterns:")
    for pattern in insights['notable_patterns']:
        print(f"  • {pattern['title']}")
        print(f"    {pattern['observation']}")
    
    print(f"\nOverall Assessment:")
    print(f"  {insights['statistical_summary']['overall_assessment']}")

if __name__ == '__main__':
    test_insight_generation()