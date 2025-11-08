"""Quick test script for CSV parser"""

from core.csv_parser import CSVParser

print("=" * 50)
print("EdgeLab CSV Parser Test")
print("=" * 50)

parser = CSVParser()
trades = parser.parse('tests/sample_data/trades_sample.csv')

print(f'\n✓ Successfully parsed {len(trades)} trades\n')

print("Trade Details:")
print("-" * 50)
for i, trade in enumerate(trades, 1):
    print(f'\nTrade {i}:')
    print(f'  Symbol:    {trade.symbol}')
    print(f'  Direction: {trade.direction}')
    print(f'  Entry:     ${trade.entry_price:.2f}')
    print(f'  Exit:      ${trade.exit_price:.2f}')
    print(f'  Result:    {trade.result}')
    print(f'  Profit:    ${trade.profit_usd:.2f} ({trade.profit_r:.2f}R)')
    print(f'  Session:   {trade.session}')
    print(f'  RR:        {trade.rr:.2f}')

print("\n" + "=" * 50)
print("✓ All tests passed!")
print("=" * 50)