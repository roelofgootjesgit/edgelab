"""
Test ReportGenerator with sample analysis
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("=== Testing Report Generator ===\n")

from core.csv_parser import CSVParser
from core.analyzer import BasicAnalyzer
from core.reporter import ReportGenerator

# Step 1: Parse trades
print("Step 1: Parsing CSV...")
parser = CSVParser()
trades = parser.parse("tests/sample_data/trades_sample.csv")
print(f"✓ Parsed {len(trades)} trades\n")

# Step 2: Analyze
print("Step 2: Analyzing...")
analyzer = BasicAnalyzer()
results = analyzer.calculate(trades)
print(f"✓ Analysis complete\n")

# Step 3: Generate report
print("Step 3: Generating PDF report...")
generator = ReportGenerator()
pdf_bytes = generator.create_report(results, trades, "test_report.pdf")
print(f"✓ Report generated ({len(pdf_bytes)} bytes)\n")

# Step 4: Save PDF
print("Step 4: Saving to file...")
output_path = "output/test_report.pdf"

# Create output directory if needed
os.makedirs("output", exist_ok=True)

with open(output_path, "wb") as f:
    f.write(pdf_bytes)

print(f"✓ Saved to: {output_path}\n")
print("=== Test Complete ===")
print(f"\nOpen the PDF: {os.path.abspath(output_path)}")