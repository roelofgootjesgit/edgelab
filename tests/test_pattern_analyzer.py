"""
Test TimingAnalyzer with sample data
Validates session breakdown and timing intelligence
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pattern_analyzer import TimingAnalyzer, SessionPerformance, TimingIntelligence
from core.quantmetrics_schema import QuantMetricsTrade
from datetime import datetime

# Create test trades with known session distribution
test_trades = [
    # Tokyo trades (low performance)
    QuantMetricsTrade(
        timestamp_open=datetime(2024, 1, 15, 2, 30),  # Tokyo hour
        timestamp_close=datetime(2024, 1, 15, 3, 45),
        symbol='XAUUSD',
        direction='LONG',
        entry_price=2050.0,
        exit_price=2045.0,  # Loss
        sl=2045.0,
        tp=2060.0,
        profit_usd=-50.0,
        profit_r=-1.0,
        result='LOSS',
        rr=1.0,
        session='Tokyo',
        source='test',
        confidence=100
    ),
    # London trades (neutral)
    QuantMetricsTrade(
        timestamp_open=datetime(2024, 1, 15, 10, 30),  # London hour
        timestamp_close=datetime(2024, 1, 15, 11, 45),
        symbol='XAUUSD',
        direction='LONG',
        entry_price=2050.0,
        exit_price=2065.0,  # Win
        sl=2045.0,
        tp=2065.0,
        profit_usd=150.0,
        profit_r=3.0,
        result='WIN',
        rr=3.0,
        session='London',
        source='test',
        confidence=100
    ),
    # NY trades (high performance)
    QuantMetricsTrade(
        timestamp_open=datetime(2024, 1, 15, 14, 30),  # NY hour
        timestamp_close=datetime(2024, 1, 15, 15, 45),
        symbol='XAUUSD',
        direction='LONG',
        entry_price=2050.0,
        exit_price=2065.0,  # Win
        sl=2045.0,
        tp=2060.0,
        profit_usd=150.0,
        profit_r=3.0,
        result='WIN',
        rr=3.0,
        session='NY',
        source='test',
        confidence=100
    ),
    QuantMetricsTrade(
        timestamp_open=datetime(2024, 1, 16, 15, 0),  # NY hour (overlap)
        timestamp_close=datetime(2024, 1, 16, 16, 30),
        symbol='XAUUSD',
        direction='LONG',
        entry_price=2048.0,
        exit_price=2063.0,  # Win
        sl=2045.0,
        tp=2060.0,
        profit_usd=150.0,
        profit_r=3.0,
        result='WIN',
        rr=3.0,
        session='NY',
        source='test',
        confidence=100
    ),
]

print("\n" + "="*50)
print("TIMING ANALYZER TEST")
print("="*50 + "\n")

# Initialize analyzer
analyzer = TimingAnalyzer(test_trades)

# Run analysis
results = analyzer.analyze()

print("SESSION BREAKDOWN")
print("-"*50)

for session_name, perf in results.sessions.items():
    print(f"\n{session_name} Session:")
    print(f"  Trades: {perf.total_trades}")
    print(f"  Wins: {perf.wins} | Losses: {perf.losses}")
    print(f"  Win Rate: {perf.winrate:.1%}")
    print(f"  Avg Win: {perf.avg_win_r:.2f}R | Avg Loss: {perf.avg_loss_r:.2f}R")
    print(f"  Expectancy: {perf.expectancy:.2f}R")
    print(f"  Total Profit: {perf.total_profit_r:.2f}R")
    print(f"  Verdict: {perf.verdict}")

print("\n" + "-"*50)
print("KEY FINDINGS")
print("-"*50)

print(f"\nBest Session: {results.best_session}")
print(f"Worst Session: {results.worst_session}")
print(f"Best Hour: {results.best_hour}:00 UTC")

if results.overlap_performance.get('London-NY', 0) > 0:
    overlap_wr = results.overlap_performance['London-NY']
    print(f"London-NY Overlap (14:00-16:00 UTC): {overlap_wr:.1%} WR")

print("\n" + "="*50)
print("TEST COMPLETE")
print("="*50 + "\n")

# Validation checks
print("VALIDATION:")
assert 'Tokyo' in results.sessions, "Tokyo session should be present"
assert 'London' in results.sessions, "London session should be present"
assert 'NY' in results.sessions, "NY session should be present"
assert results.best_session in ['NY', 'London'], "NY or London should be best session (both 100% WR)"
assert results.worst_session == 'Tokyo', "Tokyo should be worst session (0/1 wins)"
print("All validations passed!")
print(f"\nNote: {results.best_session} selected as best (tied with other profitable sessions)")