# Concept-to-Module Mapping Guide

## Overview
This guide maps common trading concepts to their corresponding strategy modules. Use this when creating templates or adding sub-confirmations.

---

## Momentum & Oscillators

| Concept | Module ID | Notes |
|---------|-----------|-------|
| RSI oversold/overbought | `rsi` | Use `operator` and `value` (30/70) |
| RSI level | `rsi` | Use `operator` and `value` |
| Momentum divergence | `momentum_indicator` | Use `period` (typically 14) |
| Momentum exhaustion | `momentum_indicator` | Use `period` and `value` |
| Stochastic oversold/overbought | `stochastic` | Use `k_period`, `d_period`, `oversold`, `overbought` |
| CCI extreme | `cci` | Use `period` and `value` |
| Williams %R | `williams_r` | Use `period` and `value` |
| MFI divergence | `mfi` | Use `period` and `value` |
| Ultimate Oscillator | `ultimate_oscillator` | Use `period` and `value` |
| TSI signal | `tsi` | Use `period` and `value` |
| KST signal | `kst` | Use `period` and `value` |
| ROC (Rate of Change) | `roc` | Use `period` and `value` |

---

## Moving Averages & Crossovers

| Concept | Module ID | Notes |
|---------|-----------|-------|
| Moving average alignment | `sma` | Use `period` (20, 50, 200) |
| Fast MA crosses slow MA | `sma` | Requires two SMA conditions |
| Golden Cross | `sma` | Fast MA (20) crosses above slow MA (50) |
| Death Cross | `sma` | Fast MA crosses below slow MA |
| EMA alignment | `sma` | Use `sma` module (same as SMA) |
| DEMA | `dema` | Double Exponential MA |
| TEMA | `tema` | Triple Exponential MA |
| HMA | `hma` | Hull Moving Average |
| KAMA | `kama` | Kaufman Adaptive MA |
| WMA | `wma` | Weighted Moving Average |
| VWMA | `vwma` | Volume Weighted MA |
| ZLEMA | `zlema` | Zero Lag EMA |

---

## Trend Indicators

| Concept | Module ID | Notes |
|---------|-----------|-------|
| Supertrend direction | `supertrend` | Use `atr_period` (10) and `multiplier` (3.0) |
| ADX trending | `adx` | Use `period` and `value` (typically >25) |
| Aroon trend | `aroon` | Use `period` and `value` |
| Parabolic SAR | `parabolic_sar` | Use `period` and `acceleration` |
| Ichimoku Cloud | `ichimoku` | Use `tenkan`, `kijun`, `senkou` periods |
| Linear Regression | `linear_regression` | Use `period` and `value` |
| Chande Kroll Stop | `chande_kroll` | Use `period` and `value` |
| Zigzag pattern | `zigzag` | Use `period` and `value` |

---

## Volatility

| Concept | Module ID | Notes |
|---------|-----------|-------|
| ATR volatility | `atr` | Use `period` (typically 14) |
| ATR sufficient | `atr` | Use `period` and `value` threshold |
| Volatility expansion | `atr` | Compare current vs. historical ATR |
| Bollinger Bands | `bollinger` | Use `period` (20) and `std_dev` (2.0) |
| Bollinger squeeze | `bollinger` | Use `bollinger_width` module |
| Bollinger width | `bollinger_width` | Use `period` and `value` |
| Keltner Channels | `keltner_channels` | Use `period` and `multiplier` |
| Donchian Channels | `donchian_channels` | Use `period` and `value` |
| Historical Volatility | `historical_volatility` | Use `period` and `value` |
| Standard Deviation | `standard_deviation` | Use `period` and `value` |

---

## Volume

| Concept | Module ID | Notes |
|---------|-----------|-------|
| VWAP | `vwap` | Use `period` (typically 20) |
| Price extended from VWAP | `vwap` | Use `operator` and `value` (deviation %) |
| Volume spike | `obv` or `cmf` | Use `obv` for volume trend, `cmf` for money flow |
| Volume expansion | `obv` or `cmf` | Compare current vs. historical |
| OBV trend | `obv` | Use `period` and `value` |
| Chaikin Money Flow | `cmf` | Use `period` and `value` |
| Accumulation/Distribution | `ad_line` | Use `period` and `value` |
| Volume Profile | `volume_profile` | Use `period` and `value` |

---

## ICT / SMC Concepts

| Concept | Module ID | Notes |
|---------|-----------|-------|
| Fair Value Gap | `fair_value_gaps` | Use `min_gap_pct`, `validity_candles`, `fill_threshold` |
| FVG entry | `fair_value_gaps` | Price enters FVG zone |
| Liquidity Sweep | `liquidity_sweep` | Use `lookback_candles`, `threshold_pct` |
| Equal highs/lows taken | `liquidity_sweep` | Same as liquidity sweep |
| Premium/Discount zone | `premium_discount_zones` | Use `period` and `value` |
| Order Block | `order_blocks` | Use `lookback_candles`, `strength_threshold` |
| Breaker Block | `breaker_blocks` | Use `lookback_candles`, `strength_threshold` |
| Mitigation Block | `mitigation_blocks` | Use `lookback_candles`, `strength_threshold` |
| Market Structure Shift | `market_structure_shift` | Use `lookback_candles`, `strength_threshold` |
| MSS | `market_structure_shift` | Abbreviation for Market Structure Shift |
| Displacement | `displacement` | Use `lookback_candles`, `threshold_pct` |
| Imbalance Zone | `imbalance_zones` | Use `min_gap_pct`, `validity_candles` |
| Inducement | `inducement` | Use `lookback_candles`, `threshold_pct` |
| Kill Zone | `kill_zones` | Use `session` and `time_range` |
| Session timing | `kill_zones` | Use `session` parameter |

---

## Support & Resistance

| Concept | Module ID | Notes |
|---------|-----------|-------|
| Support/Resistance zone | `sr_zones` | Use `lookback_candles`, `strength_threshold` |
| Pivot Points | `pivot_points` | Use `period` and `value` |
| Fibonacci Retracement | `fibonacci` | Use `period` and `value` |
| Camarilla Pivots | `camarilla` | Use `period` and `value` |

---

## Price Action Patterns

| Concept | Module ID | Notes |
|---------|-----------|-------|
| Rejection candle | ⚠️ **No module** | Price action pattern - needs custom logic |
| Wick rejection | ⚠️ **No module** | Price action pattern - needs custom logic |
| Structure break | `market_structure_shift` | Use MSS module |
| Higher-high / higher-low | `market_structure_shift` | Use MSS module |
| Lower-high / lower-low | `market_structure_shift` | Use MSS module |
| Breakout | `market_structure_shift` + `bollinger` | Combination of MSS and volatility |
| Break and retest | `liquidity_sweep` | Use liquidity sweep module |
| Pullback into value | `premium_discount_zones` or `vwap` | Use PDZ or VWAP |
| Price rejection | ⚠️ **No module** | Price action - use RSI or Stochastic as proxy |

---

## Multi-Timeframe Concepts

| Concept | Module ID | Notes |
|---------|-----------|-------|
| HTF alignment | ⚠️ **No MTF module** | Requires multi-timeframe support (future) |
| HTF bias | ⚠️ **No MTF module** | Requires multi-timeframe support (future) |
| LTF structure | ⚠️ **No MTF module** | Requires multi-timeframe support (future) |
| Higher-timeframe trend | ⚠️ **No MTF module** | Requires multi-timeframe support (future) |

---

## Market Regime

| Concept | Module ID | Notes |
|---------|-----------|-------|
| Trending regime | `adx` | Use ADX > 25 |
| Range-bound | `bollinger_width` | Use narrow Bollinger width |
| Volatility contraction | `bollinger_width` or `atr` | Use BB width or ATR |
| Choppiness | `choppiness` | Use `choppiness` module |
| Market structure | `market_structure_shift` | Use MSS module |

---

## Custom Indicators

| Concept | Module ID | Notes |
|---------|-----------|-------|
| Awesome Oscillator | `awesome_oscillator` | Use `period` and `value` |
| Accelerator Oscillator | `accelerator_oscillator` | Use `period` and `value` |
| Gator Oscillator | `gator_oscillator` | Use `period` and `value` |
| Elder Ray | `elder_ray` | Use `period` and `value` |
| Force Index | `force_index` | Use `period` and `value` |
| Ease of Movement | `ease_of_movement` | Use `period` and `value` |
| Vortex Indicator | `vortex` | Use `period` and `value` |
| Heikin Ashi | `heikin_ashi` | Use `period` and `value` |
| Renko | `renko` | Use `period` and `value` |

---

## Common Patterns & Combinations

### Trend Following
- **Trend Direction**: `supertrend` or `adx` + `sma`
- **Continuation**: `momentum_indicator` + `sma` pullback
- **Strength Filter**: `atr` + `adx`

### Mean Reversion
- **Extension**: `bollinger` or `rsi` extreme
- **Reversion Signal**: `rsi` or `stochastic` reversal
- **Confirmation**: `momentum_indicator` shift

### Breakout
- **Compression**: `bollinger_width` or `atr` contraction
- **Break**: `market_structure_shift` + `displacement`
- **Volume**: `obv` or `cmf` expansion

### ICT/SMC
- **Market Bias**: `premium_discount_zones` + `market_structure_shift`
- **Liquidity**: `liquidity_sweep` + `inducement`
- **Entry**: `fair_value_gaps` + `displacement` + `kill_zones`

---

## ⚠️ Concepts Without Modules

These concepts need custom logic or are not yet supported:

1. **Price Action Patterns**
   - Rejection candles
   - Wick rejection
   - Pin bars
   - Engulfing patterns

2. **Multi-Timeframe**
   - HTF alignment
   - LTF structure
   - Timeframe confluence

3. **External Data**
   - News events
   - Economic calendar
   - Market hours

4. **Complex Patterns**
   - Chart patterns (head & shoulders, triangles)
   - Harmonic patterns
   - Elliott Wave

---

## Usage Guidelines

1. **Always specify `moduleId`** in templates when possible
2. **Use the most specific module** available (e.g., `supertrend` instead of generic "trend")
3. **Combine modules** for complex concepts (e.g., breakout = MSS + displacement)
4. **Document custom logic** needed for price action patterns
5. **Validate mappings** before adding to templates

---

## Quick Reference

```javascript
// Example: RSI Oversold
{
    label: 'RSI oversold',
    moduleId: 'rsi',
    hasParams: true,
    config: {
        operator: '<',
        value: 30,
        period: 14
    }
}

// Example: Supertrend
{
    label: 'Supertrend bullish',
    moduleId: 'supertrend',
    hasParams: true,
    config: {
        atr_period: 10,
        multiplier: 3.0
    }
}

// Example: Fair Value Gap
{
    label: 'Fair Value Gap entry',
    moduleId: 'fair_value_gaps',
    hasParams: true,
    config: {
        min_gap_pct: 0.5,
        validity_candles: 50,
        fill_threshold: 0.5
    }
}
```



