"""Test the complete web flow"""
from core.strategy import StrategyDefinition, EntryCondition
from core.backtest_engine import BacktestEngine
from core.analyzer import BasicAnalyzer
from core.reporter import ModernReporter

print('1. Creating strategy...')
s = StrategyDefinition(
    name='Test', 
    symbol='XAUUSD', 
    entry_conditions=[EntryCondition('rsi', '<', 35)], 
    period='1mo'
)

print('2. Running backtest...')
e = BacktestEngine()
trades = e.run(s)
print(f'   Trades: {len(trades)}')

print('3. Analyzing...')
a = BasicAnalyzer()
r = a.calculate(trades)
print(f'   WR: {r["winrate"]}%')

print('4. Generating report...')
gen = ModernReporter()
pdf = gen.create_pdf(trades=trades, analysis=r, output_path='output/test.pdf')
print(f'   PDF: {len(pdf)} bytes')

print('SUCCESS')