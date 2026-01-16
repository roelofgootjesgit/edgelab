# Strategy Modules Inventory - V4 Templates

## Overview
**Total Modules Available: 66**

This document inventories all available strategy modules and verifies that templates use them correctly.

---

## Available Modules by Category

### 1. Indicator (5 modules)
- `bollinger` - Bollinger Bands
- `macd` - MACD
- `moving_average` - Moving Average
- `rsi` - RSI
- `sma` - Simple Moving Average

### 2. ICT (11 modules)
- `breaker_blocks` - Breaker Blocks
- `displacement` - Displacement
- `fair_value_gaps` - Fair Value Gaps
- `imbalance_zones` - Imbalance Zones
- `inducement` - Inducement
- `kill_zones` - Kill Zones
- `liquidity_sweep` - Liquidity Sweep
- `market_structure_shift` - Market Structure Shift
- `mitigation_blocks` - Mitigation Blocks
- `order_blocks` - Order Blocks
- `premium_discount_zones` - Premium/Discount Zones

### 3. Trend (8 modules)
- `adx` - ADX (Average Directional Index)
- `aroon` - Aroon
- `chande_kroll` - Chande Kroll Stop
- `ichimoku` - Ichimoku Cloud
- `linear_regression` - Linear Regression
- `parabolic_sar` - Parabolic SAR
- `supertrend` - Supertrend
- `zigzag` - Zigzag

### 4. Momentum (8 modules)
- `cci` - Commodity Channel Index
- `kst` - Know Sure Thing
- `mfi` - Money Flow Index
- `roc` - Rate of Change
- `stochastic` - Stochastic Oscillator
- `tsi` - True Strength Index
- `ultimate_oscillator` - Ultimate Oscillator
- `williams_r` - Williams %R

### 5. Moving Averages (8 modules)
- `dema` - Double Exponential Moving Average
- `hma` - Hull Moving Average
- `kama` - Kaufman Adaptive Moving Average
- `smma` - Smoothed Moving Average
- `tema` - Triple Exponential Moving Average
- `vwma` - Volume Weighted Moving Average
- `wma` - Weighted Moving Average
- `zlema` - Zero Lag Exponential Moving Average

### 6. Volatility (6 modules)
- `atr` - Average True Range
- `bollinger_width` - Bollinger Band Width
- `donchian_channels` - Donchian Channels
- `historical_volatility` - Historical Volatility
- `keltner_channels` - Keltner Channels
- `standard_deviation` - Standard Deviation

### 7. Volume (6 modules)
- `ad_line` - Accumulation/Distribution Line
- `cmf` - Chaikin Money Flow
- `obv` - On Balance Volume
- `sr_zones` - Support/Resistance Zones
- `volume_profile` - Volume Profile
- `vwap` - Volume Weighted Average Price

### 8. Support/Resistance (4 modules)
- `camarilla` - Camarilla Pivots
- `fibonacci` - Fibonacci Retracements
- `pivot_points` - Pivot Points
- `sr_zones` - Support/Resistance Zones

### 9. Custom (12 modules)
- `accelerator_oscillator` - Accelerator Oscillator
- `awesome_oscillator` - Awesome Oscillator
- `choppiness` - Choppiness Index
- `donchian_channels` - Donchian Channels (custom version)
- `ease_of_movement` - Ease of Movement
- `elder_ray` - Elder Ray
- `force_index` - Force Index
- `gator_oscillator` - Gator Oscillator
- `heikin_ashi` - Heikin Ashi
- `momentum_indicator` - Momentum Indicator
- `renko` - Renko
- `vortex` - Vortex Indicator

---

## Template Usage Analysis

### Template 1: ICT / SMC Base Setup
**Decision Blocks: 3**

**Block 1 - Market Bias:**
- ✅ `premium_discount_zones` - "Premium / Discount zone respected"
- ✅ `market_structure_shift` - "Higher-timeframe bias confirmed"
- ⚠️ "HTF market structure aligned" - Should use `market_structure_shift` or custom logic

**Block 2 - Liquidity Event:**
- ✅ `liquidity_sweep` - "Liquidity sweep present"
- ✅ `liquidity_sweep` - "Equal highs / lows taken"
- ✅ `inducement` - "Stop hunt or inducement"

**Block 3 - Entry Model:**
- ✅ `fair_value_gaps` - "Fair Value Gap entry"
- ✅ `displacement` - "Displacement move"
- ⚠️ "Lower-timeframe structure shift" - Should use `market_structure_shift`
- ⚠️ "Session timing aligned" - Should use `kill_zones`

**Status:** ✅ Mostly correct, minor improvements needed

---

### Template 2: Trend Following
**Decision Blocks: 3**

**Block 1 - Trend Direction:**
- ⚠️ "Higher-high / higher-low structure" - Should use `market_structure_shift` or custom logic
- ✅ `sma` - "Moving average alignment"
- ⚠️ "Market regime trending" - Should use `adx` or `supertrend`

**Block 2 - Continuation Trigger:**
- ⚠️ "Pullback into value" - Should use `premium_discount_zones` or `vwap`
- ⚠️ "Break & retest" - Should use `liquidity_sweep` or custom logic
- ⚠️ "Momentum continuation signal" - Should use `momentum_indicator` or `roc`

**Block 3 - Strength Filter:**
- ✅ `atr` - "Volatility sufficient"
- ⚠️ "No nearby structure resistance" - Should use `sr_zones`
- ⚠️ "Session alignment" - Should use `kill_zones`

**Status:** ⚠️ Needs improvement - many sub-confirmations not mapped to modules

---

### Template 3: Mean Reversion
**Decision Blocks: 2**

**Block 1 - Extension From Value:**
- ⚠️ "Distance from mean" - Should use `bollinger` or `sma`
- ⚠️ "Momentum exhaustion" - Should use `momentum_indicator` or `rsi`
- ⚠️ "Overextension signal" - Should use `bollinger` or `rsi`

**Block 2 - Reversion Confirmation:**
- ⚠️ "Price rejection" - Price action, could use `rsi` or `stochastic`
- ⚠️ "Momentum shift" - Should use `momentum_indicator` or `rsi`
- ⚠️ "Structure holding" - Should use `market_structure_shift` or `sr_zones`

**Status:** ⚠️ Needs improvement - sub-confirmations not mapped to modules

---

### Template 4: Breakout Momentum
**Decision Blocks: 3**

**Block 1 - Compression:**
- ⚠️ "Range present" - Should use `bollinger_width` or `atr`
- ✅ `bollinger_width` or `atr` - "Volatility contraction"
- ✅ `liquidity_sweep` - "Equal highs / lows"

**Block 2 - Break With Intent:**
- ⚠️ "Strong impulse break" - Should use `displacement` or `momentum_indicator`
- ⚠️ "Volume expansion" - Should use `obv` or `cmf`
- ⚠️ "Structure break" - Should use `market_structure_shift`

**Block 3 - Failure Filter:**
- ⚠️ "No immediate rejection" - Price action
- ⚠️ "Retest holds" - Should use `liquidity_sweep` or `sr_zones`
- ⚠️ "Momentum sustained" - Should use `momentum_indicator` or `roc`

**Status:** ⚠️ Needs improvement

---

### Template 5: Golden Cross
**Decision Blocks: 2**

**Block 1 - Trend Shift:**
- ✅ `sma` - "Fast MA crosses slow MA"
- ⚠️ "Slope confirmation" - Should use `sma` with slope calculation
- ⚠️ "HTF alignment" - Should use `market_structure_shift` or multi-timeframe

**Block 2 - Environment Filter:**
- ⚠️ "Trending regime" - Should use `adx` or `supertrend`
- ⚠️ "No range compression" - Should use `bollinger_width` or `atr`

**Status:** ⚠️ Needs improvement

---

### Template 6: Supertrend Trend
**Decision Blocks: 3**

**Block 1 - Trend State:**
- ✅ `supertrend` - "Supertrend direction"
- ⚠️ "Price above / below trend line" - Should use `supertrend`

**Block 2 - Entry Alignment:**
- ⚠️ "Pullback into trend" - Should use `supertrend` with price action
- ⚠️ "Continuation signal" - Should use `momentum_indicator` or `roc`

**Block 3 - Volatility Filter:**
- ✅ `atr` - "ATR sufficient"
- ⚠️ "No compression" - Should use `bollinger_width` or `atr`

**Status:** ✅ Mostly correct

---

### Template 7: RSI Oversold Bounce
**Decision Blocks: 3**

**Block 1 - Momentum Extreme:**
- ✅ `rsi` - "RSI oversold / overbought"
- ✅ `momentum_indicator` - "Momentum divergence"

**Block 2 - Price Reaction:**
- ⚠️ "Rejection candle" - Price action
- ⚠️ "Structure hold" - Should use `market_structure_shift` or `sr_zones`

**Block 3 - Trend Filter:**
- ⚠️ "Trade with higher-timeframe bias" - Should use `market_structure_shift` or multi-timeframe

**Status:** ✅ Mostly correct

---

### Template 8: VWAP Reversion
**Decision Blocks: 3**

**Block 1 - Distance From VWAP:**
- ✅ `vwap` - "Price extended from VWAP"
- ⚠️ "Deviation threshold met" - Should use `vwap` with deviation calculation

**Block 2 - Rejection Signal:**
- ⚠️ "Wick rejection" - Price action
- ⚠️ "Momentum slowdown" - Should use `momentum_indicator` or `rsi`

**Block 3 - Session Filter:**
- ⚠️ "Active session" - Should use `kill_zones`
- ⚠️ "No major news" - Not a module (external data needed)

**Status:** ⚠️ Needs improvement

---

### Template 9: Momentum Scalping
**Decision Blocks: 4**

**Block 1 - Momentum Ignition:**
- ⚠️ "Sudden impulse" - Should use `displacement` or `momentum_indicator`
- ⚠️ "Break from micro-range" - Should use `bollinger_width` or `atr`

**Block 2 - Volume / Volatility:**
- ⚠️ "Volume spike" - Should use `obv` or `cmf`
- ✅ `atr` - "ATR volatility expansion"

**Block 3 - Directional Bias:**
- ⚠️ "Micro-trend aligned" - Should use `sma` or `supertrend`
- ⚠️ "HTF not opposing" - Should use `market_structure_shift` or multi-timeframe

**Block 4 - Time Filter:**
- ✅ `kill_zones` - "Killzone / session"
- ⚠️ "No chop conditions" - Should use `choppiness` or `adx`

**Status:** ⚠️ Needs improvement

---

## Summary

### ✅ Correctly Mapped Modules
- RSI (`rsi`)
- Moving Averages (`sma`)
- Supertrend (`supertrend`)
- ATR (`atr`)
- VWAP (`vwap`)
- Momentum Indicator (`momentum_indicator`)
- ICT modules (FVG, Liquidity Sweep, Premium/Discount, etc.)
- Kill Zones (`kill_zones`)

### ⚠️ Needs Mapping
Many sub-confirmations in templates are:
1. **Price action patterns** (rejection candles, structure breaks) - Need custom logic or module
2. **Multi-timeframe concepts** (HTF alignment, LTF structure) - Need MTF module support
3. **Generic concepts** (trending regime, range compression) - Need specific module mapping
4. **Volume concepts** (volume spike, volume expansion) - Should use `obv`, `cmf`, or `volume_profile`
5. **Structure concepts** (higher-highs, breakouts) - Should use `market_structure_shift` or custom logic

### 🔧 Recommendations

1. **Create mapping document** for common trading concepts → modules
2. **Add custom logic modules** for price action patterns
3. **Enhance templates** to use actual module IDs instead of generic labels
4. **Add module_id field** to all template sub-confirmations
5. **Create validation** to ensure all sub-confirmations map to available modules

---

## Next Steps

1. ✅ **DONE:** Inventory all 66 available modules
2. ⚠️ **TODO:** Update templates to explicitly use module IDs
3. ⚠️ **TODO:** Create concept-to-module mapping guide
4. ⚠️ **TODO:** Add validation to ensure templates only use available modules
5. ⚠️ **TODO:** Document which concepts need custom logic vs. modules



