# check_premium_discount_columns.py
"""Check what columns Premium/Discount module creates"""

import pandas as pd
from datetime import datetime, timedelta
from core.data_manager import DataManager
from core.strategy_modules.ict.premium_discount_zones import PremiumDiscountZonesModule

# Get small dataset
data_manager = DataManager()
data = data_manager.get_data(
    symbol='XAUUSD',
    timeframe='15m',
    start=datetime.now() - timedelta(days=3),
    end=datetime.now()
)

# Run module
module = PremiumDiscountZonesModule()
config = {
    'lookback_candles': 50,
    'premium_threshold': 0.618,
    'discount_threshold': 0.382,
    'equilibrium_range': 0.1
}

result = module.calculate(data, config)

print("Columns created by Premium/Discount module:")
print("=" * 60)
for col in result.columns:
    if col not in ['open', 'high', 'low', 'close', 'volume']:
        print(f"  {col}")
print("=" * 60)