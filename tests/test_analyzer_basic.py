"""
Test BasicAnalyzer with sample trades
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("=== Starting test ===")
print(f"Project root: {project_root}")

print("\nStep 1: Importing modules...")
from core.csv_parser import CSVParser
from core.analyzer import BasicAnalyzer
print("✓ Imports successful")

print("\nStep 2: Parsing CSV...")
parser = CSVParser()
trades = parser.parse("tests/sample_data/trades_sample.csv")
print(f"✓ Parsed {len(trades)} trades")

print("\nStep 3: Creating analyzer...")
analyzer = BasicAnalyzer()
print("✓ Analyzer created")

print("\nStep 4: Calculating metrics...")
results = analyzer.calculate(trades)
print("✓ Calculation complete")

# Print results
print("\n=== BASIC ANALYSIS RESULTS ===\n")
print(f"Total Trades: {results.total_trades}")
print(f"Wins: {results.wins} | Losses: {results.losses}")
print(f"Win Rate: {results.winrate}%")
print(f"Profit Factor: {results.profit_factor}")
print(f"Expectancy: {results.expectancy}R")
print(f"Avg Win: {results.avg_win_r}R | Avg Loss: {results.avg_loss_r}R")
print(f"Total Profit: {results.total_profit_r}R")
print(f"Max Drawdown: {results.max_drawdown_pct}%")
print(f"\nRecommendation: {results.recommendation}")

print("\n=== Test complete ===")