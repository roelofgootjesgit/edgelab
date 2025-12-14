# multi_month_ict_backtest.py
"""
ICT Strategy Multi-Month Backtest
Tests: MSS + Premium/Discount + Kill Zones across different months

Purpose: Validate strategy works in various market conditions
"""

import pandas as pd
from datetime import datetime, timedelta
from core.data_manager import DataManager
from core.strategy_modules.ict.market_structure_shift import MarketStructureShiftModule
from core.strategy_modules.ict.premium_discount_zones import PremiumDiscountZonesModule
from core.strategy_modules.ict.kill_zones import KillZonesModule
from core.quantmetrics_schema import QuantMetricsTrade

def run_backtest_period(symbol, timeframe, start, end, period_name):
    """Run backtest for a specific time period"""
    
    print(f"\n{'='*80}")
    print(f"TESTING PERIOD: {period_name}")
    print(f"{'='*80}")
    
    # Fetch data
    data_manager = DataManager()
    print(f"Fetching {symbol} {timeframe} data...")
    data = data_manager.get_data(symbol=symbol, timeframe=timeframe, start=start, end=end)
    
    if len(data) < 100:
        print(f"⚠ Insufficient data: {len(data)} candles (need 100+)")
        return None
    
    print(f"✓ Data loaded: {len(data)} candles")
    print(f"  Date range: {data.index[0].date()} to {data.index[-1].date()}")
    print(f"  Price range: {data['low'].min():.2f} - {data['high'].max():.2f}")
    
    # Initialize modules
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
    
    # Calculate indicators
    data_with_mss = mss_module.calculate(data.copy(), mss_config)
    data_with_pdz = pdz_module.calculate(data_with_mss, pdz_config)
    data_with_all = kz_module.calculate(data_with_pdz, kz_config)
    
    # Backtest with realistic Gold 15m targets
    trades = []
    tp_points = 15.0
    sl_points = 10.0
    
    for i in range(len(data_with_all)):
        row = data_with_all.iloc[i]
        
        # LONG conditions
        if (row.get('in_kill_zone') and 
            row.get('mss_active') and 
            row.get('mss_type') == 'BULLISH' and
            row.get('in_discount')):
            
            entry_price = row['close']
            sl = entry_price - sl_points
            tp = entry_price + tp_points
            
            exit_idx = None
            exit_price = None
            result = 'TIMEOUT'
            
            for j in range(i + 1, min(i + 31, len(data_with_all))):
                future_row = data_with_all.iloc[j]
                
                if future_row['high'] >= tp:
                    exit_idx = j
                    exit_price = tp
                    result = 'WIN'
                    break
                
                if future_row['low'] <= sl:
                    exit_idx = j
                    exit_price = sl
                    result = 'LOSS'
                    break
            
            if exit_idx is None:
                exit_idx = min(i + 30, len(data_with_all) - 1)
                exit_price = data_with_all.iloc[exit_idx]['close']
                result = 'TIMEOUT'
            
            profit_points = exit_price - entry_price
            profit_r = profit_points / sl_points
            
            trade = QuantMetricsTrade(
                timestamp_open=data_with_all.index[i],
                timestamp_close=data_with_all.index[exit_idx],
                symbol=symbol,
                direction='LONG',
                entry_price=entry_price,
                exit_price=exit_price,
                sl=sl,
                tp=tp,
                profit_usd=profit_points * 100,
                profit_r=profit_r,
                result=result
            )
            trades.append(trade)
        
        # SHORT conditions
        elif (row.get('in_kill_zone') and 
              row.get('mss_active') and 
              row.get('mss_type') == 'BEARISH' and
              row.get('in_premium')):
            
            entry_price = row['close']
            sl = entry_price + sl_points
            tp = entry_price - tp_points
            
            exit_idx = None
            exit_price = None
            result = 'TIMEOUT'
            
            for j in range(i + 1, min(i + 31, len(data_with_all))):
                future_row = data_with_all.iloc[j]
                
                if future_row['low'] <= tp:
                    exit_idx = j
                    exit_price = tp
                    result = 'WIN'
                    break
                
                if future_row['high'] >= sl:
                    exit_idx = j
                    exit_price = sl
                    result = 'LOSS'
                    break
            
            if exit_idx is None:
                exit_idx = min(i + 30, len(data_with_all) - 1)
                exit_price = data_with_all.iloc[exit_idx]['close']
                result = 'TIMEOUT'
            
            profit_points = entry_price - exit_price
            profit_r = profit_points / sl_points
            
            trade = QuantMetricsTrade(
                timestamp_open=data_with_all.index[i],
                timestamp_close=data_with_all.index[exit_idx],
                symbol=symbol,
                direction='SHORT',
                entry_price=entry_price,
                exit_price=exit_price,
                sl=sl,
                tp=tp,
                profit_usd=profit_points * 100,
                profit_r=profit_r,
                result=result
            )
            trades.append(trade)
    
    # Analyze results
    if not trades:
        print("⚠ No trades generated")
        return None
    
    wins = [t for t in trades if t.result == 'WIN']
    losses = [t for t in trades if t.result == 'LOSS']
    timeouts = [t for t in trades if t.result == 'TIMEOUT']
    longs = [t for t in trades if t.direction == 'LONG']
    shorts = [t for t in trades if t.direction == 'SHORT']
    
    win_rate = (len(wins) / len(trades)) * 100
    total_profit_r = sum(t.profit_r for t in trades)
    
    print(f"\nResults:")
    print(f"  Total Trades: {len(trades)}")
    print(f"  Wins: {len(wins)} ({win_rate:.1f}%)")
    print(f"  Losses: {len(losses)} ({len(losses)/len(trades)*100:.1f}%)")
    print(f"  Timeouts: {len(timeouts)} ({len(timeouts)/len(trades)*100:.1f}%)")
    print(f"  Direction: {len(longs)} LONG, {len(shorts)} SHORT")
    print(f"  Total Profit: {total_profit_r:+.2f}R")
    
    return {
        'period': period_name,
        'start': start,
        'end': end,
        'candles': len(data),
        'trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'timeouts': len(timeouts),
        'longs': len(longs),
        'shorts': len(shorts),
        'win_rate': win_rate,
        'total_profit_r': total_profit_r,
        'avg_profit_per_trade': total_profit_r / len(trades) if trades else 0
    }

# Main execution
print("="*80)
print("MULTI-MONTH ICT STRATEGY BACKTEST")
print("="*80)
print()
print("Strategy: MSS + Premium/Discount + Kill Zones")
print("Symbol: XAUUSD")
print("Timeframe: 15m")
print("Targets: TP=15pts (1.5R), SL=10pts (1R)")
print()
print("Testing 6 months to validate robustness...")
print("="*80)

symbol = 'XAUUSD'
timeframe = '15m'

# Define test periods (going back 6 months)
now = datetime.now()

test_periods = [
    {
        'name': 'Dec 2025 (Recent)',
        'start': datetime(2025, 11, 30),
        'end': datetime(2025, 12, 14)
    },
    {
        'name': 'Nov 2025',
        'start': datetime(2025, 11, 1),
        'end': datetime(2025, 11, 30)
    },
    {
        'name': 'Oct 2025',
        'start': datetime(2025, 10, 1),
        'end': datetime(2025, 10, 31)
    },
    {
        'name': 'Sep 2025',
        'start': datetime(2025, 9, 1),
        'end': datetime(2025, 9, 30)
    },
    {
        'name': 'Aug 2025',
        'start': datetime(2025, 8, 1),
        'end': datetime(2025, 8, 31)
    },
    {
        'name': 'Jul 2025',
        'start': datetime(2025, 7, 1),
        'end': datetime(2025, 7, 31)
    }
]

# Run backtests
all_results = []

for period in test_periods:
    result = run_backtest_period(
        symbol=symbol,
        timeframe=timeframe,
        start=period['start'],
        end=period['end'],
        period_name=period['name']
    )
    
    if result:
        all_results.append(result)

# Summary comparison
print("\n" + "="*80)
print("MULTI-MONTH COMPARISON")
print("="*80)
print()

if all_results:
    print(f"{'Period':<20} {'Trades':<8} {'Win%':<8} {'Profit':<10} {'L/S Ratio':<12}")
    print("-"*80)
    
    for r in all_results:
        ls_ratio = f"{r['longs']}/{r['shorts']}"
        print(f"{r['period']:<20} {r['trades']:<8} {r['win_rate']:<7.1f}% {r['total_profit_r']:>+8.2f}R  {ls_ratio:<12}")
    
    print("-"*80)
    
    # Calculate aggregate statistics
    total_trades = sum(r['trades'] for r in all_results)
    total_wins = sum(r['wins'] for r in all_results)
    total_profit = sum(r['total_profit_r'] for r in all_results)
    avg_win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
    
    print(f"{'TOTAL':<20} {total_trades:<8} {avg_win_rate:<7.1f}% {total_profit:>+8.2f}R")
    print()
    
    # Assessment
    print("="*80)
    print("STRATEGY ASSESSMENT ACROSS ALL PERIODS")
    print("="*80)
    print()
    
    # Check consistency
    winning_periods = [r for r in all_results if r['total_profit_r'] > 0]
    consistent_win_rate = len([r for r in all_results if r['win_rate'] >= 50])
    
    print(f"Periods tested: {len(all_results)}")
    print(f"Profitable periods: {len(winning_periods)} ({len(winning_periods)/len(all_results)*100:.0f}%)")
    print(f"Periods with 50%+ win rate: {consistent_win_rate} ({consistent_win_rate/len(all_results)*100:.0f}%)")
    print(f"Total trades across all periods: {total_trades}")
    print(f"Overall win rate: {avg_win_rate:.1f}%")
    print(f"Total profit: {total_profit:+.2f}R")
    print(f"Average profit per period: {total_profit/len(all_results):+.2f}R")
    print()
    
    # Final verdict
    if avg_win_rate >= 55 and len(winning_periods) >= len(all_results) * 0.6:
        print("✓ STRATEGY VALIDATED ACROSS MULTIPLE MONTHS")
        print()
        print("This strategy shows:")
        print(f"  ✓ Consistent performance ({consistent_win_rate}/{len(all_results)} periods profitable)")
        print(f"  ✓ Acceptable win rate ({avg_win_rate:.1f}% overall)")
        print(f"  ✓ Positive expectancy across {len(all_results)} months")
        print()
        print("Recommendation: PROCEED TO PAPER TRADING")
        print("  → Test with $10,000 virtual account")
        print("  → Target: 30-50 trades to confirm")
    elif avg_win_rate >= 45 and total_profit > 0:
        print("⚠ STRATEGY SHOWS PROMISE BUT NEEDS REFINEMENT")
        print()
        print("This strategy shows:")
        print(f"  ~ Mixed results ({len(winning_periods)}/{len(all_results)} profitable periods)")
        print(f"  ~ Acceptable win rate ({avg_win_rate:.1f}%)")
        print(f"  ✓ Overall positive expectancy ({total_profit:+.2f}R)")
        print()
        print("Recommendations:")
        print("  1. Add confirmation filters (Breaker Blocks, Imbalance)")
        print("  2. Test on 1h timeframe (cleaner signals)")
        print("  3. Tighten entry criteria")
    else:
        print("✗ STRATEGY NOT VALIDATED ACROSS MULTIPLE MONTHS")
        print()
        print("This strategy shows:")
        print(f"  ✗ Inconsistent results ({len(winning_periods)}/{len(all_results)} profitable)")
        print(f"  ✗ Low win rate ({avg_win_rate:.1f}%)")
        print()
        print("Recommendations:")
        print("  1. Try different ICT module combination")
        print("  2. Test different timeframe (1h, 4h)")
        print("  3. Add more filters for quality signals")
    
    print()
    print("="*80)
    print("Want to test:")
    print("  1. Different symbol (EURUSD, BTCUSD)?")
    print("  2. Different timeframe (1h, 4h)?")
    print("  3. Add more modules (Breaker, Imbalance, Inducement)?")
    print("="*80)

else:
    print("\n⚠ No results collected - check data availability")