from core.html_reporter import HTMLReportGenerator

# Mock data
results = {
    'win_rate': 65.5,
    'esi': 1.42,
    'pvs': 0.85,
    'profit_factor': 2.3,
    'avg_win': 150.50,
    'avg_loss': -85.30,
    'winning_trades': 13,
    'losing_trades': 7,
}

# Mock trades (just need length)
class MockTrades:
    def __len__(self):
        return 20

trades = MockTrades()

# Generate report
generator = HTMLReportGenerator()
pdf_bytes = generator.generate_report(results, trades)

# Save test PDF
with open('test_report_prem.pdf', 'wb') as f:
    f.write(pdf_bytes)

print(f"✓ Test PDF generated: {len(pdf_bytes)} bytes")
print("✓ Open test_report.pdf to check styling")