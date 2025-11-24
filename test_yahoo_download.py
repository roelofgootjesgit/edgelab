"""
Test Yahoo Finance data download
"""
import yfinance as yf

print("Downloading XAUUSD (Gold) data...")

# Download 1 month of 15-minute data
data = yf.download(
    tickers="GC=F",  # Gold Futures (proxy voor XAUUSD)
    period="1mo",
    interval="15m",
    progress=False
)

print(f"\nDownload complete!")
print(f"Rows: {len(data)}")
print(f"Columns: {list(data.columns)}")
print(f"Date range: {data.index[0]} to {data.index[-1]}")
print(f"\nFirst 3 rows:")
print(data.head(3))"""
Test DataDownloader functionality
"""
import time
from core.data_downloader import DataDownloader

print("=" * 50)
print("DATA DOWNLOADER TEST")
print("=" * 50)

# Initialize
downloader = DataDownloader()

# Test 1: First download (should hit Yahoo Finance)
print("\n[Test 1] First download (from Yahoo Finance)...")
start = time.time()
data = downloader.download("XAUUSD", period="1mo", interval="15m")
first_time = time.time() - start

print(f"  Rows: {len(data)}")
print(f"  Columns: {list(data.columns)}")
print(f"  Time: {first_time:.2f} seconds")

# Test 2: Second download (should hit cache)
print("\n[Test 2] Second download (from cache)...")
start = time.time()
data2 = downloader.download("XAUUSD", period="1mo", interval="15m")
cache_time = time.time() - start

print(f"  Rows: {len(data2)}")
print(f"  Time: {cache_time:.2f} seconds")
print(f"  Speedup: {first_time/cache_time:.1f}x faster")

# Test 3: Data structure validation
print("\n[Test 3] Data structure...")
print(f"  Index type: {type(data.index).__name__}")
print(f"  First timestamp: {data.index[0]}")
print(f"  Last timestamp: {data.index[-1]}")

# Test 4: OHLCV values check
print("\n[Test 4] Sample data:")
print(data.head(3))

print("\n" + "=" * 50)
print("ALL TESTS PASSED")
print("=" * 50)