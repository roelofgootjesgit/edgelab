# test_mss_real_data.py
"""Test Market Structure Shift module with real Yahoo Finance data"""

import pandas as pd
from datetime import datetime, timedelta
from core.strategy_modules.ict.market_structure_shift import MarketStructureShiftModule
from core.data_manager import DataManager

print("="*70)
print("MARKET STRUCTURE SHIFT - REAL DATA TEST")
print("="*70)
print()

# Initialize data manager
data_manager = DataManager()

# Fetch real data
symbol = 'XAUUSD'
timeframe = '1h'
end = datetime.now()
start = end - timedelta(days=30)  # Last 30 days

print(f"Fetching real data:")
print(f"  Symbol: {symbol}")
print(f"  Timeframe: {timeframe}")
print(f"  Period: {start.date()} to {end.date()}")
print()

try:
    data = data_manager.get_data(
        symbol=symbol,
        timeframe=timeframe,
        start=start,
        end=end
    )
    
    if data.empty:
        print("ERROR: No data returned from Yahoo Finance")
        print("This may be due to:")
        print("  - Symbol format (try 'GC=F' for gold)")
        print("  - Network issues")
        print("  - Yahoo Finance API limitations")
        exit(1)
    
    print(f"Data loaded: {len(data)} candles")
    print()
    print("First 5 candles:")
    print(data.head()[['open', 'high', 'low', 'close', 'volume']])
    print()
    print("Last 5 candles:")
    print(data.tail()[['open', 'high', 'low', 'close', 'volume']])
    print()
    
    # Instantiate MSS module
    mss_module = MarketStructureShiftModule()
    
    print("Module Configuration:")
    config = {
        'swing_lookback': 5,          # 5 candles each side
        'break_threshold_pct': 0.3,   # 0.3% break confirmation
        'mss_validity_candles': 10    # MSS active for 10 candles
    }
    
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()
    
    # Calculate MSS
    print("Calculating Market Structure Shifts...")
    result = mss_module.calculate(data.copy(), config)
    print()
    
    # Analysis
    print("="*70)
    print("ANALYSIS RESULTS:")
    print("="*70)
    print()
    
    # Count swing points
    swing_highs = result[result['is_swing_high'] == True]
    swing_lows = result[result['is_swing_low'] == True]
    
    print(f"Swing Points Detected:")
    print(f"  Swing Highs: {len(swing_highs)}")
    print(f"  Swing Lows: {len(swing_lows)}")
    print()
    
    # Show recent swing points
    if not swing_highs.empty:
        print("Recent Swing Highs (last 5):")
        recent_highs = swing_highs.tail(5)
        for idx in recent_highs.index:
            print(f"  {idx}: {recent_highs.loc[idx, 'swing_high']:.2f}")
        print()
    
    if not swing_lows.empty:
        print("Recent Swing Lows (last 5):")
        recent_lows = swing_lows.tail(5)
        for idx in recent_lows.index:
            print(f"  {idx}: {recent_lows.loc[idx, 'swing_low']:.2f}")
        print()
    
    # Count MSS events
    bullish_mss = result[result['bullish_mss'] == True]
    bearish_mss = result[result['bearish_mss'] == True]
    
    print(f"Market Structure Shifts:")
    print(f"  Bullish MSS: {len(bullish_mss)}")
    print(f"  Bearish MSS: {len(bearish_mss)}")
    print()
    
    # Show recent MSS events
    if not bullish_mss.empty:
        print("Recent Bullish MSS Events (last 3):")
        recent_bull = bullish_mss.tail(3)
        for idx in recent_bull.index:
            swing_high = result.iloc[idx-1]['recent_swing_high'] if idx > 0 else None
            actual_high = result.iloc[idx]['high']
            print(f"  {idx}:")
            print(f"    Broke swing high: {swing_high:.2f}")
            print(f"    Actual high: {actual_high:.2f}")
            print(f"    Price: {result.iloc[idx]['close']:.2f}")
        print()
    
    if not bearish_mss.empty:
        print("Recent Bearish MSS Events (last 3):")
        recent_bear = bearish_mss.tail(3)
        for idx in recent_bear.index:
            swing_low = result.iloc[idx-1]['recent_swing_low'] if idx > 0 else None
            actual_low = result.iloc[idx]['low']
            print(f"  {idx}:")
            print(f"    Broke swing low: {swing_low:.2f}")
            print(f"    Actual low: {actual_low:.2f}")
            print(f"    Price: {result.iloc[idx]['close']:.2f}")
        print()
    
    # Current market state
    latest = result.iloc[-1]
    print("="*70)
    print("CURRENT MARKET STATE:")
    print("="*70)
    print()
    print(f"Current Price: {latest['close']:.2f}")
    print(f"Recent Swing High: {latest['recent_swing_high']:.2f}" if not pd.isna(latest['recent_swing_high']) else "Recent Swing High: None")
    print(f"Recent Swing Low: {latest['recent_swing_low']:.2f}" if not pd.isna(latest['recent_swing_low']) else "Recent Swing Low: None")
    print(f"MSS Active: {latest['mss_active']}")
    if latest['mss_active']:
        print(f"MSS Type: {latest['mss_type']}")
    print()
    
    # Trading signals
    print("="*70)
    print("TRADING SIGNALS:")
    print("="*70)
    print()
    
    long_signals = []
    short_signals = []
    
    for i in range(len(result)):
        long_signal = mss_module.check_entry_condition(result, i, config, 'LONG')
        short_signal = mss_module.check_entry_condition(result, i, config, 'SHORT')
        
        if long_signal:
            long_signals.append(i)
        if short_signal:
            short_signals.append(i)
    
    print(f"Total LONG signals: {len(long_signals)}")
    print(f"Total SHORT signals: {len(short_signals)}")
    print()
    
    if long_signals:
        print(f"Recent LONG signals (last 5): {long_signals[-5:]}")
    if short_signals:
        print(f"Recent SHORT signals (last 5): {short_signals[-5:]}")
    print()
    
    # Summary statistics
    print("="*70)
    print("SUMMARY:")
    print("="*70)
    print()
    print(f"Total Candles: {len(result)}")
    print(f"Swing Highs: {len(swing_highs)} ({len(swing_highs)/len(result)*100:.1f}%)")
    print(f"Swing Lows: {len(swing_lows)} ({len(swing_lows)/len(result)*100:.1f}%)")
    print(f"Bullish MSS: {len(bullish_mss)}")
    print(f"Bearish MSS: {len(bearish_mss)}")
    print(f"LONG Entry Signals: {len(long_signals)}")
    print(f"SHORT Entry Signals: {len(short_signals)}")
    
    print()
    print("="*70)
    print("TEST COMPLETE - MSS Working on Real Data")
    print("="*70)

except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()