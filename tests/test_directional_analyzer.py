"""
Test DirectionalAnalyzer
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.pattern_analyzer import DirectionalAnalyzer
from core.quantmetrics_schema import QuantMetricsTrade
from datetime import datetime

def test_directional_bias_long_edge():
    """Test detection of LONG bias"""
    
    trades = [
        # 2 LONG wins
        QuantMetricsTrade(
            timestamp_open=datetime(2024, 1, 15, 14, 30),
            timestamp_close=datetime(2024, 1, 15, 15, 45),
            symbol="XAUUSD", 
            direction="LONG",
            entry_price=2050.0, 
            exit_price=2065.0,
            sl=2045.0, 
            tp=2065.0,
            profit_usd=150.0, 
            profit_r=3.0, 
            result="WIN",
            rr=3.0,  # NEW
            session="NY",  # NEW
            source="test",  # NEW
            confidence=100  # NEW
        ),
        QuantMetricsTrade(
            timestamp_open=datetime(2024, 1, 16, 15, 0),
            timestamp_close=datetime(2024, 1, 16, 16, 30),
            symbol="XAUUSD", 
            direction="LONG",
            entry_price=2055.0, 
            exit_price=2070.0,
            sl=2050.0, 
            tp=2070.0,
            profit_usd=150.0, 
            profit_r=3.0, 
            result="WIN",
            rr=3.0,  # NEW
            session="NY",  # NEW
            source="test",  # NEW
            confidence=100  # NEW
        ),
        # 2 SHORT losses
        QuantMetricsTrade(
            timestamp_open=datetime(2024, 1, 17, 16, 0),
            timestamp_close=datetime(2024, 1, 17, 16, 45),
            symbol="XAUUSD", 
            direction="SHORT",
            entry_price=2058.0, 
            exit_price=2062.0,
            sl=2062.0, 
            tp=2050.0,
            profit_usd=-40.0, 
            profit_r=-1.0, 
            result="LOSS",
            rr=-1.0,  # NEW
            session="NY",  # NEW
            source="test",  # NEW
            confidence=100  # NEW
        ),
        QuantMetricsTrade(
            timestamp_open=datetime(2024, 1, 18, 8, 15),
            timestamp_close=datetime(2024, 1, 18, 8, 30),
            symbol="XAUUSD", 
            direction="SHORT",
            entry_price=2045.0, 
            exit_price=2048.0,
            sl=2048.0, 
            tp=2035.0,
            profit_usd=-30.0, 
            profit_r=-1.0, 
            result="LOSS",
            rr=-1.0,  # NEW
            session="London",  # NEW
            source="test",  # NEW
            confidence=100  # NEW
        ),
    ]
    
    analyzer = DirectionalAnalyzer()
    results = analyzer.analyze(trades)
    
    # Verify structure
    assert 'long_stats' in results
    assert 'short_stats' in results
    assert 'bias' in results
    assert 'recommendation' in results
    
    # Verify LONG bias detected
    assert results['bias'] == 'LONG'
    assert results['long_stats']['winrate'] == 100.0
    assert results['short_stats']['winrate'] == 0.0
    assert results['long_stats']['edge'] == 'STRONG'
    assert results['short_stats']['edge'] == 'NONE'
    
    # Verify improvement calculation
    assert results['expected_improvement'] > 0
    
    print("✅ DirectionalAnalyzer test passed!")
    print(f"Bias: {results['bias']}")
    print(f"LONG WR: {results['long_stats']['winrate']}%")
    print(f"SHORT WR: {results['short_stats']['winrate']}%")
    print(f"Expected improvement: +{results['expected_improvement']}%")

if __name__ == '__main__':
    test_directional_bias_long_edge()