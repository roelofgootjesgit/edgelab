"""
Test IndicatorEngine functionality
"""
from core.data_downloader import DataDownloader
from core.indicators import IndicatorEngine

print("=" * 50)
print("INDICATOR ENGINE TEST")
print("=" * 50)

# Download data
downloader = DataDownloader()
data = downloader.download("XAUUSD", period="1mo", interval="15m")
print(f"\nLoaded {len(data)} candles")

# Calculate indicators
engine = IndicatorEngine()
data_with_indicators = engine.calculate_all(data)

# Show new columns
original_cols = ['open', 'high', 'low', 'close', 'volume']
indicator_cols = [c for c in data_with_indicators.columns if c not in original_cols]

print(f"\nIndicators calculated: {len(indicator_cols)}")
for col in indicator_cols:
    print(f"  - {col}")

# Show sample values (skip NaN rows at start)
print("\nSample values (row 50):")
row = data_with_indicators.iloc[50]
print(f"  Close:  {row['close']:.2f}")
print(f"  RSI:    {row['rsi']:.2f}")
print(f"  SMA_20: {row['sma_20']:.2f}")
print(f"  SMA_50: {row['sma_50']:.2f}")
print(f"  MACD:   {row['macd']:.4f}")
print(f"  ATR:    {row['atr']:.2f}")
print(f"  ADX:    {row['adx']:.2f}")

# Validate RSI range (should be 0-100)
rsi_min = data_with_indicators['rsi'].min()
rsi_max = data_with_indicators['rsi'].max()
print(f"\nRSI range validation:")
print(f"  Min: {rsi_min:.2f} (should be >= 0)")
print(f"  Max: {rsi_max:.2f} (should be <= 100)")

assert rsi_min >= 0, "RSI below 0"
assert rsi_max <= 100, "RSI above 100"

print("\n" + "=" * 50)
print("ALL TESTS PASSED")
print("=" * 50)