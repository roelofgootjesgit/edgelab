from core.html_reporter import HTMLReportGenerator

# Mock data with insights
results = {
    'win_rate': 65.5,
    'esi': 1.42,
    'pvs': 0.85,
    'profit_factor': 2.3,
    'avg_win': 150.50,
    'avg_loss': -85.30,
    'winning_trades': 13,
    'losing_trades': 7,
    
    # Add timing and insights for testing
    'timing_analysis': {
        'best_session': 'NY Session'
    },
    'insights': {
        'critical_findings': [
            'Average loss size exceeds optimal risk parameters by 15%',
            'Win rate drops below 50% during London session'
        ],
        'notable_patterns': [
            'Best performance occurs between 14:00-18:00 UTC',
            'Long positions outperform short positions by 2:1 ratio',
            'Trade execution quality improves significantly on Tuesdays'
        ]
    }
}

# Mock trades (just need length)
class MockTrades:
    def __len__(self):
        return 20

trades = MockTrades()

# Generate report
print("Generating EdgeLab branded PDF report...")
generator = HTMLReportGenerator()
pdf_bytes = generator.generate_report(results, trades)

# Save test PDF
with open('test_report_edgelab.pdf', 'wb') as f:
    f.write(pdf_bytes)

print(f"✓ EdgeLab branded PDF generated: {len(pdf_bytes):,} bytes")
print("✓ Open test_report_edgelab.pdf to check:")
print("  - EdgeLab logo with 3-color icon")
print("  - Blue gradient cover matching your brand")
print("  - Professional tables with ratings")
print("  - Insight cards with icons")
print("\nFile saved: test_report_edgelab.pdf")
