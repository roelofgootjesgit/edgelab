# example_ict_strategy_backtest_fixed.py
"""
Example: ICT Strategy Backtest (FIXED for realistic Gold targets)
Template: "MSS + Value + Time" (Conservative)

Fixed: Adjusted TP/SL for Gold 15m timeframe
"""

import pandas as pd
from datetime import datetime, timedelta
from core.data_manager import DataManager
from core.strategy_modules.ict.market_structure_shift import MarketStructureShiftModule
from core.strategy_modules.ict.premium_discount_zones import PremiumDiscountZonesModule
from core.strategy_modules.ict.kill_zones import KillZonesModule
from core.quantmetrics_schema import QuantMetricsTrade

print("="*80)
print("ICT STRATEGY BACKTEST - FIXED FOR GOLD 15M")
print("="*80)
print()
print("Strategy: 'MSS + Value + Time' (Conservative Template)")
print()
print("Rules:")
print("  LONG Entry:")
print("    ✓ In Kill Zone (London OR New York)")
print("    ✓ Bullish MSS detected")
print("    ✓ Price in Discount zone")
print()
print("  SHORT Entry:")
print("    ✓ In Kill Zone (London OR New York)")
print("    ✓ Bearish MSS detected")
print("    ✓ Price in Premium zone")
print()
print("  Exit (FIXED FOR GOLD):")
print("    TP: 15 points (~0.35% gain)")
print("    SL: 10 points (~0.23% loss)")
print("    R:R = 1:1.5")
print("="*80)
print()

# Fetch data
data_manager = DataManager()
symbol = 'XAUUSD'
timeframe = '15m'
end = datetime.now()
start = end - timedelta(days=14)

print(f"Fetching {symbol} {timeframe} data...")
data = data_manager.get_data(symbol=symbol, timeframe=timeframe, start=start, end=end)
print(f"✓ Data loaded: {len(data)} candles")
print(f"  Period: {start.date()} to {end.date()}")
print(f"  Price range: {data['low'].min():.2f} - {data['high'].max():.2f}")
print()

# Calculate average candle range for reference
avg_range = (data['high'] - data['low']).mean()
print(f"Average candle range: {avg_range:.2f} points")
print(f"  → TP target (15 points) = {15/avg_range:.1f}x avg range")
print(f"  → SL target (10 points) = {10/avg_range:.1f}x avg range")
print()

# Initialize modules
print("Initializing ICT modules...")

mss_module = MarketStructureShiftModule()
mss_config = {
    'swing_lookback': 5,
    'break_threshold_pct': 0.2,
    'confirmation_candles': 2
}

pdz_module = PremiumDiscountZonesModule()
pdz_config = {
    'lookback_candles': 50,
    'premium_threshold': 0.618,
    'discount_threshold': 0.382,
    'equilibrium_range': 0.1
}

kz_module = KillZonesModule()
kz_config = {
    'enabled_zones': ['london', 'newyork'],
    'london_start': 7,
    'london_end': 10,
    'ny_start': 12,
    'ny_end': 15
}

print("✓ Modules initialized")
print()

# Calculate all modules
print("Calculating indicators...")
data_with_mss = mss_module.calculate(data.copy(), mss_config)
data_with_pdz = pdz_module.calculate(data_with_mss, pdz_config)
data_with_all = kz_module.calculate(data_with_pdz, kz_config)
print("✓ All indicators calculated")
print()

# Backtest simulation with FIXED targets
print("="*80)
print("RUNNING BACKTEST SIMULATION (REALISTIC TARGETS)")
print("="*80)
print()

trades = []
tp_points = 15.0  # Fixed point target
sl_points = 10.0  # Fixed point stop

for i in range(len(data_with_all)):
    row = data_with_all.iloc[i]
    
    # Check LONG conditions
    if (row.get('in_kill_zone') and 
        row.get('mss_active') and 
        row.get('mss_type') == 'BULLISH' and
        row.get('in_discount')):
        
        # Simulate LONG trade
        entry_price = row['close']
        sl = entry_price - sl_points
        tp = entry_price + tp_points
        
        # Find exit (check next 30 candles = ~7.5 hours)
        exit_idx = None
        exit_price = None
        result = 'TIMEOUT'
        
        for j in range(i + 1, min(i + 31, len(data_with_all))):
            future_row = data_with_all.iloc[j]
            
            # Check TP
            if future_row['high'] >= tp:
                exit_idx = j
                exit_price = tp
                result = 'WIN'
                break
            
            # Check SL
            if future_row['low'] <= sl:
                exit_idx = j
                exit_price = sl
                result = 'LOSS'
                break
        
        if exit_idx is None:
            exit_idx = min(i + 30, len(data_with_all) - 1)
            exit_price = data_with_all.iloc[exit_idx]['close']
            result = 'TIMEOUT'
        
        # Calculate profit in R-multiples
        profit_points = exit_price - entry_price
        profit_r = profit_points / sl_points
        profit_usd = profit_points * 100  # $100 per point (simplified)
        
        trade = QuantMetricsTrade(
            timestamp_open=row['timestamp'] if 'timestamp' in row else data_with_all.index[i],
            timestamp_close=data_with_all.iloc[exit_idx]['timestamp'] if 'timestamp' in data_with_all.iloc[exit_idx] else data_with_all.index[exit_idx],
            symbol=symbol,
            direction='LONG',
            entry_price=entry_price,
            exit_price=exit_price,
            sl=sl,
            tp=tp,
            profit_usd=profit_usd,
            profit_r=profit_r,
            result=result
        )
        trades.append(trade)
    
    # Check SHORT conditions
    elif (row.get('in_kill_zone') and 
          row.get('mss_active') and 
          row.get('mss_type') == 'BEARISH' and
          row.get('in_premium')):
        
        # Simulate SHORT trade
        entry_price = row['close']
        sl = entry_price + sl_points
        tp = entry_price - tp_points
        
        # Find exit
        exit_idx = None
        exit_price = None
        result = 'TIMEOUT'
        
        for j in range(i + 1, min(i + 31, len(data_with_all))):
            future_row = data_with_all.iloc[j]
            
            # Check TP
            if future_row['low'] <= tp:
                exit_idx = j
                exit_price = tp
                result = 'WIN'
                break
            
            # Check SL
            if future_row['high'] >= sl:
                exit_idx = j
                exit_price = sl
                result = 'LOSS'
                break
        
        if exit_idx is None:
            exit_idx = min(i + 30, len(data_with_all) - 1)
            exit_price = data_with_all.iloc[exit_idx]['close']
            result = 'TIMEOUT'
        
        # Calculate profit
        profit_points = entry_price - exit_price
        profit_r = profit_points / sl_points
        profit_usd = profit_points * 100
        
        trade = QuantMetricsTrade(
            timestamp_open=row['timestamp'] if 'timestamp' in row else data_with_all.index[i],
            timestamp_close=data_with_all.iloc[exit_idx]['timestamp'] if 'timestamp' in data_with_all.iloc[exit_idx] else data_with_all.index[exit_idx],
            symbol=symbol,
            direction='SHORT',
            entry_price=entry_price,
            exit_price=exit_price,
            sl=sl,
            tp=tp,
            profit_usd=profit_usd,
            profit_r=profit_r,
            result=result
        )
        trades.append(trade)

print(f"Backtest complete: {len(trades)} trades generated")
print()

# Analyze results
if trades:
    wins = [t for t in trades if t.result == 'WIN']
    losses = [t for t in trades if t.result == 'LOSS']
    timeouts = [t for t in trades if t.result == 'TIMEOUT']
    
    longs = [t for t in trades if t.direction == 'LONG']
    shorts = [t for t in trades if t.direction == 'SHORT']
    
    win_rate = (len(wins) / len(trades)) * 100
    total_profit_r = sum(t.profit_r for t in trades)
    total_profit_usd = sum(t.profit_usd for t in trades)
    avg_win = sum(t.profit_r for t in wins) / len(wins) if wins else 0
    avg_loss = sum(t.profit_r for t in losses) / len(losses) if losses else 0
    avg_timeout = sum(t.profit_r for t in timeouts) / len(timeouts) if timeouts else 0
    
    print("="*80)
    print("BACKTEST RESULTS")
    print("="*80)
    print()
    print(f"Total Trades: {len(trades)}")
    print(f"  Wins: {len(wins)} ({len(wins)/len(trades)*100:.1f}%)")
    print(f"  Losses: {len(losses)} ({len(losses)/len(trades)*100:.1f}%)")
    print(f"  Timeouts: {len(timeouts)} ({len(timeouts)/len(trades)*100:.1f}%)")
    print()
    print(f"Direction:")
    print(f"  LONG: {len(longs)} trades")
    print(f"  SHORT: {len(shorts)} trades")
    print()
    print(f"Performance:")
    print(f"  Win Rate: {win_rate:.1f}%")
    print(f"  Total Profit: {total_profit_r:+.2f}R (${total_profit_usd:+.2f})")
    print(f"  Average Win: {avg_win:+.2f}R")
    print(f"  Average Loss: {avg_loss:+.2f}R")
    print(f"  Average Timeout: {avg_timeout:+.2f}R")
    print()
    
    # Show example trades
    print("="*80)
    print("EXAMPLE TRADES (First 5)")
    print("="*80)
    print()
    
    for idx, trade in enumerate(trades[:5], 1):
        duration = (trade.timestamp_close - trade.timestamp_open).total_seconds() / 3600
        print(f"Trade {idx}:")
        print(f"  Direction: {trade.direction}")
        print(f"  Entry: {trade.entry_price:.2f} at {trade.timestamp_open}")
        print(f"  Exit: {trade.exit_price:.2f} at {trade.timestamp_close}")
        print(f"  Duration: {duration:.1f} hours")
        print(f"  Result: {trade.result} ({trade.profit_r:+.2f}R = ${trade.profit_usd:+.2f})")
        print()
    
    # Strategy assessment
    print("="*80)
    print("STRATEGY ASSESSMENT")
    print("="*80)
    print()
    
    if win_rate >= 50 and total_profit_r > 5.0:
        print("✓ STRATEGY VALIDATED")
        print()
        print("This strategy shows:")
        print(f"  ✓ Win rate: {win_rate:.1f}% (target: 50%+)")
        print(f"  ✓ Positive expectancy: {total_profit_r:+.2f}R")
        print(f"  ✓ Total profit: ${total_profit_usd:+.2f}")
        print()
        print("Key Metrics:")
        print(f"  - Avg Win: {avg_win:.2f}R vs Avg Loss: {avg_loss:.2f}R")
        print(f"  - Profit Factor: {(sum(t.profit_r for t in wins) / abs(sum(t.profit_r for t in losses))):.2f}" if losses else "N/A")
        print(f"  - Win/Loss/Timeout: {len(wins)}/{len(losses)}/{len(timeouts)}")
        print()
        print("Recommendation: READY FOR PAPER TRADING")
        print("  → Test with $10,000 virtual account")
        print("  → Risk $100 per trade (1%)")
        print("  → 20-30 trades to confirm")
    elif win_rate >= 40 and total_profit_r > 0:
        print("⚠ STRATEGY NEEDS REFINEMENT")
        print()
        print("This strategy shows:")
        print(f"  ~ Win rate: {win_rate:.1f}% (target: 50%+)")
        print(f"  ✓ Positive expectancy: {total_profit_r:+.2f}R")
        print(f"  ~ Many timeouts: {len(timeouts)} ({len(timeouts)/len(trades)*100:.0f}%)")
        print()
        print("Suggestions:")
        print("  1. Tighten entry filters (reduce timeouts)")
        print("  2. Add confirmation module (Breaker, Imbalance)")
        print("  3. Try different exit strategy (trailing stop?)")
        print("  4. Test longer timeframe (1h instead of 15m)")
    else:
        print("✗ STRATEGY NOT VALIDATED")
        print()
        print("This strategy shows:")
        print(f"  ✗ Win rate: {win_rate:.1f}% (below 40%)")
        print(f"  ✗ Total profit: {total_profit_r:+.2f}R")
        print()
        print("Recommendation: TRY DIFFERENT ICT COMBINATION")
    
    print()
    print("="*80)
    print("Next Steps:")
    print()
    print("  ✓ This example now uses REALISTIC targets for Gold 15m")
    print("  ✓ TP: 15 points (~0.35%) | SL: 10 points (~0.23%)")
    print("  ✓ Should see mix of WINS, LOSSES, and some TIMEOUTS")
    print()
    print("Want better results? Try in QuantMetrics Strategy Builder:")
    print("  1. Add Breaker Blocks (confluence)")
    print("  2. Add Imbalance Zones (better entries)")
    print("  3. Try Inducement module (reversals)")
    print("  4. Test 1h timeframe (bigger moves)")
    print("  5. Adjust Premium/Discount thresholds")
    print("="*80)

else:
    print("⚠ No trades generated")
    print()
    print("Possible reasons:")
    print("  - Filters too strict (try loosening one)")
    print("  - Market didn't align with conditions")
    print("  - Try longer backtest period")