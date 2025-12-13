"""
Test ExecutionAnalyzer
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.pattern_analyzer import ExecutionAnalyzer
from core.quantmetrics_schema import QuantMetricsTrade
from datetime import datetime, timedelta

def test_execution_quality():
    """Test execution quality analysis"""
    
    trades = [
        # Full TP win (good execution)
        QuantMetricsTrade(
            timestamp_open=datetime(2024, 1, 15, 14, 30),
            timestamp_close=datetime(2024, 1, 15, 16, 0),  # 1.5h duration
            symbol="XAUUSD", direction="LONG",
            entry_price=2050.0, exit_price=2065.0,
            sl=2045.0, tp=2065.0,
            profit_usd=150.0, profit_r=3.0, result="WIN",
            rr=3.0, session="NY", source="test", confidence=100
        ),
        # Early exit (bad execution)
        QuantMetricsTrade(
            timestamp_open=datetime(2024, 1, 16, 15, 0),
            timestamp_close=datetime(2024, 1, 16, 15, 30),  # 0.5h duration
            symbol="XAUUSD", direction="LONG",
            entry_price=2055.0, exit_price=2062.0,
            sl=2050.0, tp=2070.0,
            profit_usd=70.0, profit_r=1.4, result="WIN",  # Could have been 3R
            rr=1.4, session="NY", source="test", confidence=100
        ),
        # Proper SL hit (good execution)
        QuantMetricsTrade(
            timestamp_open=datetime(2024, 1, 17, 16, 0),
            timestamp_close=datetime(2024, 1, 17, 17, 0),  # 1h duration
            symbol="XAUUSD", direction="SHORT",
            entry_price=2058.0, exit_price=2062.0,
            sl=2062.0, tp=2050.0,
            profit_usd=-40.0, profit_r=-1.0, result="LOSS",
            rr=-1.0, session="NY", source="test", confidence=100
        ),
        # Held past SL (bad execution)
        QuantMetricsTrade(
            timestamp_open=datetime(2024, 1, 18, 8, 15),
            timestamp_close=datetime(2024, 1, 18, 10, 0),  # 1.75h duration
            symbol="XAUUSD", direction="SHORT",
            entry_price=2045.0, exit_price=2052.0,
            sl=2048.0, tp=2035.0,
            profit_usd=-70.0, profit_r=-2.3, result="LOSS",  # Should be -1R
            rr=-2.3, session="London", source="test", confidence=100
        ),
    ]
    
    analyzer = ExecutionAnalyzer()
    results = analyzer.analyze(trades)
    
    # Verify structure
    assert 'tp_behavior' in results
    assert 'sl_behavior' in results
    assert 'duration_analysis' in results
    assert 'execution_score' in results
    assert 'issues' in results
    assert 'recommendations' in results
    
    # Verify TP analysis
    assert results['tp_behavior']['total_wins'] == 2
    assert results['tp_behavior']['early_exits'] > 0
    
    # Verify SL analysis
    assert results['sl_behavior']['total_losses'] == 2
    assert results['sl_behavior']['held_past_sl'] > 0
    
    # Verify execution score
    assert 0 <= results['execution_score'] <= 100
    
    # Verify issues detected
    assert len(results['issues']) > 0
    
    # Verify recommendations generated
    assert len(results['recommendations']) > 0
    
    print("✅ ExecutionAnalyzer test passed!")
    print(f"Execution Score: {results['execution_score']}/100")
    print(f"Issues Found: {len(results['issues'])}")
    print(f"Recommendations: {len(results['recommendations'])}")
    
    # Print details
    print("\nTP Behavior:")
    print(f"  Full TP: {results['tp_behavior']['full_tp_hits']}/{results['tp_behavior']['total_wins']}")
    print(f"  Early Exits: {results['tp_behavior']['early_exits']}")
    
    print("\nSL Behavior:")
    print(f"  Proper SL: {results['sl_behavior']['proper_sl_hits']}/{results['sl_behavior']['total_losses']}")
    print(f"  Held Past SL: {results['sl_behavior']['held_past_sl']}")
    
    print("\nIssues:")
    for issue in results['issues']:
        print(f"  - {issue}")

if __name__ == '__main__':
    test_execution_quality()
