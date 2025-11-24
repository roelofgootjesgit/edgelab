"""
Test Complete Pipeline: Strategy -> Backtest -> Analyzer
Proves backtest integrates with existing EdgeLab system
"""
from core.strategy import StrategyDefinition, EntryCondition
from core.backtest_engine import BacktestEngine
from core.analyzer import BasicAnalyzer

print("=" * 60)
print("FULL PIPELINE TEST")
print("Strategy -> Backtest -> Analyzer")
print("=" * 60)

# Step 1: Define strategy
print("\n[1] Defining strategy...")
strategy = StrategyDefinition(
    name="RSI Oversold NY Session",
    symbol="XAUUSD",
    timeframe="15m",
    direction="LONG",
    entry_conditions=[
        EntryCondition("rsi", "<", 30)
    ],
    tp_r=1.5,
    sl_r=1.0,
    session="NY",
    period="1mo"
)
print(f"    {strategy}")

# Step 2: Run backtest
print("\n[2] Running backtest...")
engine = BacktestEngine()
trades = engine.run(strategy)
print(f"    Generated {len(trades)} trades")

# Step 3: Run through existing analyzer
print("\n[3] Running analyzer (existing code)...")
analyzer = BasicAnalyzer()
results = analyzer.calculate(trades)

# Step 4: Display results
print("\n[4] ANALYSIS RESULTS")
print("-" * 60)
print(f"    Total Trades:   {results['total_trades']}")
print(f"    Win Rate:       {results['winrate']}%")
print(f"    Profit Factor:  {results['profit_factor']}")
print(f"    Expectancy:     {results['expectancy']}R")
print(f"    Total Profit:   {results['total_profit_r']}R")
print(f"    Max Drawdown:   {results['max_drawdown_pct']}%")
print(f"    ESI:            {results['esi']}")
print(f"    PVS:            {results['pvs']}")

# Step 5: Show insights
print("\n[5] PATTERN INSIGHTS")
print("-" * 60)
if 'timing_analysis' in results:
    timing = results['timing_analysis']
    if 'session_breakdown' in timing:
        print("    Session Performance:")
        for session, data in timing['session_breakdown'].items():
            print(f"      {session}: {data['winrate']:.1f}% WR ({data['total_trades']} trades)")

print("\n" + "=" * 60)
print("PIPELINE TEST COMPLETE")
print("Backtest output works with existing analyzer!")
print("=" * 60)