"""
Test LossForensics
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.pattern_analyzer import LossForensics
from core.edgelab_schema import EdgeLabTrade
from datetime import datetime, timedelta

def test_loss_forensics():
    """Test loss categorization and analysis"""
    
    trades = [
        # Proper loss (good execution)
        EdgeLabTrade(
            timestamp_open=datetime(2024, 1, 15, 14, 30),
            timestamp_close=datetime(2024, 1, 15, 15, 0),
            symbol="XAUUSD", direction="LONG",
            entry_price=2050.0, exit_price=2045.0,
            sl=2045.0, tp=2065.0,
            profit_usd=-50.0, profit_r=-1.0, result="LOSS",
            rr=-1.0, session="NY", source="test", confidence=100
        ),
        # Held past SL (bad execution)
        EdgeLabTrade(
            timestamp_open=datetime(2024, 1, 16, 8, 0),
            timestamp_close=datetime(2024, 1, 16, 9, 0),
            symbol="XAUUSD", direction="SHORT",
            entry_price=2055.0, exit_price=2062.0,
            sl=2058.0, tp=2045.0,
            profit_usd=-70.0, profit_r=-2.3, result="LOSS",  # Should be -1R
            rr=-2.3, session="London", source="test", confidence=100
        ),
        # Win (for context)
        EdgeLabTrade(
            timestamp_open=datetime(2024, 1, 16, 15, 0),
            timestamp_close=datetime(2024, 1, 16, 16, 30),
            symbol="XAUUSD", direction="LONG",
            entry_price=2055.0, exit_price=2070.0,
            sl=2050.0, tp=2070.0,
            profit_usd=150.0, profit_r=3.0, result="WIN",
            rr=3.0, session="NY", source="test", confidence=100
        ),
        # Revenge trade (loss immediately after loss)
        EdgeLabTrade(
            timestamp_open=datetime(2024, 1, 16, 9, 15),  # 15min after loss
            timestamp_close=datetime(2024, 1, 16, 9, 45),
            symbol="XAUUSD", direction="SHORT",
            entry_price=2060.0, exit_price=2065.0,
            sl=2063.0, tp=2050.0,
            profit_usd=-50.0, profit_r=-1.7, result="LOSS",
            rr=-1.7, session="London", source="test", confidence=100
        ),
    ]
    
    analyzer = LossForensics()
    results = analyzer.analyze(trades)
    
    # Verify structure
    assert 'loss_breakdown' in results
    assert 'loss_causes' in results
    assert 'emotional_trades' in results
    assert 'preventable_cost' in results
    assert 'critical_finding' in results
    
    # Verify loss categorization
    assert 'proper' in results['loss_breakdown']
    assert 'held_past_sl' in results['loss_breakdown']
    
    # Verify emotional trading detection
    assert results['emotional_trades']['count'] > 0
    
    # Verify preventable cost calculation
    assert results['preventable_cost'] > 0
    
    print("✅ LossForensics test passed!")
    print(f"Total Losses: 3")
    print(f"Preventable Cost: {results['preventable_cost']:.2f}R")
    
    # Print loss breakdown
    print("\nLoss Breakdown:")
    for loss_type, stats in results['loss_breakdown'].items():
        print(f"  {loss_type}: {stats['count']} trades, {stats.get('total_cost', 0):.2f}R cost")
    
    # Print causes
    print("\nLoss Causes:")
    for cause, stats in results['loss_causes'].items():
        print(f"  {cause}: {stats['count']} ({stats['percentage']:.1f}%)")
    
    # Print emotional trading
    print(f"\nEmotional Trades: {results['emotional_trades']['count']}")
    print(f"  Cost: {results['emotional_trades']['cost']:.2f}R")
    
    # Print critical finding
    print(f"\nCritical Finding:")
    print(f"  {results['critical_finding']}")

if __name__ == '__main__':
    test_loss_forensics()
