"""
Test BacktestEngine - Complete simulation test
"""
from core.strategy import StrategyDefinition, EntryCondition
from core.backtest_engine import BacktestEngine

print("=" * 60)
print("BACKTEST ENGINE TEST")
print("=" * 60)

# Define strategy: LONG when RSI < 35
strategy = StrategyDefinition(
    name="RSI Oversold Long",
    symbol="XAUUSD",
    timeframe="15m",
    direction="LONG",
    entry_conditions=[
        EntryCondition("rsi", "<", 35)
    ],
    tp_r=1.5,
    sl_r=1.0,
    period="1mo"
)

print(f"\nStrategy: {strategy}")
print(f"Valid: {strategy.is_valid()}")

# Run backtest
print("\nRunning backtest...")
engine = BacktestEngine()
trades = engine.run(strategy)

print(f"\nTrades generated: {len(trades)}")

# Show trade statistics
if trades:
    wins = [t for t in trades if t.result == 'WIN']
    losses = [t for t in trades if t.result == 'LOSS']
    timeouts = [t for t in trades if t.result == 'TIMEOUT']
    
    print(f"  Wins: {len(wins)}")
    print(f"  Losses: {len(losses)}")
    print(f"  Timeouts: {len(timeouts)}")
    
    if len(trades) > 0:
        winrate = len(wins) / len(trades) * 100
        print(f"  Win Rate: {winrate:.1f}%")
    
    # Show first 3 trades
    print("\nFirst 3 trades:")
    for i, trade in enumerate(trades[:3]):
        print(f"\n  Trade {i+1}:")
        print(f"    Direction: {trade.direction}")
        print(f"    Entry: {trade.entry_price:.2f}")
        print(f"    Exit: {trade.exit_price:.2f}")
        print(f"    Result: {trade.result}")
        print(f"    Profit: {trade.profit_r:.2f}R")

# Verify EdgeLabTrade compatibility
print("\n" + "-" * 60)
print("COMPATIBILITY CHECK")
print("-" * 60)

if trades:
    trade = trades[0]
    required_attrs = [
        'timestamp_open', 'timestamp_close', 'symbol', 'direction',
        'entry_price', 'exit_price', 'sl', 'tp',
        'profit_usd', 'profit_r', 'result'
    ]
    
    missing = [attr for attr in required_attrs if not hasattr(trade, attr)]
    
    if missing:
        print(f"FAIL: Missing attributes: {missing}")
    else:
        print("PASS: All EdgeLabTrade attributes present")
        print("      Compatible with existing analyzer!")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)