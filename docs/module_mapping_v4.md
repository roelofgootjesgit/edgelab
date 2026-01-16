# Module Mapping V4 - Sub-confirmation Labels → Modules

## Overzicht
Dit document toont hoe sub-confirmation labels worden gemapped naar daadwerkelijke modules in `core/strategy_modules/`.

---

## Indicator Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| RSI, oversold, overbought | `rsi` | RSIModule |
| MA, moving average, cross, golden | `sma` | SMAModule |
| MACD | `macd` | MACDModule |
| Bollinger, BB | `bollinger` | BollingerBandsModule |

---

## ICT Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| Fair Value Gap, FVG | `fair_value_gaps` | FairValueGapModule |
| Liquidity sweep, sweep | `liquidity_sweep` | LiquiditySweepModule |
| Premium, Discount, Premium Discount | `premium_discount_zones` | PremiumDiscountZonesModule |
| Market structure, structure, MSS | `market_structure_shift` | MarketStructureShiftModule |
| Displacement | `displacement` | DisplacementModule |
| Order block, Orderblock | `order_blocks` | OrderBlockModule |
| Killzone, Kill zone | `kill_zones` | KillZonesModule |
| Breaker | `breaker_blocks` | BreakerBlockModule |
| Mitigation | `mitigation_blocks` | MitigationBlocksModule |
| Imbalance | `imbalance_zones` | ImbalanceZonesModule |
| Inducement, Stop hunt | `inducement` | InducementModule |

---

## Trend Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| Supertrend, trend | `supertrend` | SuperTrendModule |
| ADX | `adx` | ADXModule |
| Aroon | `aroon` | AroonModule |
| Ichimoku | `ichimoku` | IchimokuModule |
| Parabolic, SAR | `parabolic_sar` | ParabolicSARModule |

---

## Momentum Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| Stochastic, Stoch | `stochastic` | StochasticModule |
| Momentum, Divergence | `momentum_indicator` | MomentumIndicatorModule |
| CCI | `cci` | CCIModule |
| MFI | `mfi` | MFIModule |
| ROC | `roc` | ROCModule |
| Williams, Williams R | `williams_r` | WilliamsRModule |
| Ultimate | `ultimate_oscillator` | UltimateOscillatorModule |
| TSI | `tsi` | TsiModule |

---

## Volatility Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| ATR, Volatility | `atr` | AtrModule |
| Keltner | `keltner_channels` | KeltnerChannelsModule |
| Donchian | `donchian_channels` | DonchianChannelsModule |

---

## Volume Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| VWAP | `vwap` | VWAPModule |
| Volume profile | `volume_profile` | VolumeProfileModule |
| OBV | `obv` | OBVModule |
| CMF | `cmf` | CMFModule |
| AD Line, Accumulation | `ad_line` | ADLineModule |

---

## Support/Resistance Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| Pivot | `pivot_points` | PivotPointsModule |
| Fibonacci, Fib | `fibonacci` | FibonacciModule |
| Camarilla | `camarilla` | CamarillaModule |
| SR Zone, Support Resistance | `sr_zones` | SRZonesModule |

---

## Moving Averages Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| DEMA | `dema` | DEMAModule |
| HMA | `hma` | HMAModule |
| KAMA | `kama` | KAMAModule |
| SMMA | `smma` | SMMAModule |
| TEMA | `tema` | TEMAModule |
| VWMA | `vwma` | VWMAModule |
| WMA | `wma` | WMAModule |
| ZLEMA | `zlema` | ZLEMAModule |

---

## Custom Modules

| Label Keywords | Module ID | Module Class |
|---------------|-----------|--------------|
| Accelerator | `accelerator_oscillator` | AcceleratorOscillatorModule |
| Awesome | `awesome_oscillator` | AwesomeOscillatorModule |
| Choppiness | `choppiness` | ChoppinessModule |
| Ease of Movement | `ease_of_movement` | EaseOfMovementModule |
| Elder Ray | `elder_ray` | ElderRayModule |
| Force Index | `force_index` | ForceIndexModule |
| Gator | `gator_oscillator` | GatorOscillatorModule |
| Heikin Ashi | `heikin_ashi` | HeikinAshiModule |
| Renko | `renko` | RenkoModule |
| Vortex | `vortex` | VortexModule |

---

## Default Fallbacks

Als geen match wordt gevonden:
- **Default**: `rsi` (RSIModule)
- **Price action patterns** (rejection, candle): `rsi`
- **Generic trend/structure**: `supertrend` of `market_structure_shift`

---

## Configuratie Defaults

### RSI
- Period: 14
- Value (oversold): 30
- Value (overbought): 70

### SMA
- Period: 20

### MACD
- Period: 12 (fast period)

### Supertrend
- Period: 10 (ATR period)

### VWAP
- Period: 20

### ATR
- Period: 14

### ICT Modules
- Period: 20-50 (afhankelijk van module)
- Value: 1 (boolean-like)

---

## Gebruik in Templates

Templates kunnen nu direct de juiste module IDs gebruiken via labels:

```javascript
{
    label: 'Liquidity sweep present',
    hasParams: true,
    config: {
        operator: '==',
        value: 1,
        period: 20
    }
}
```

Backend zal automatisch `liquidity_sweep` module gebruiken omdat "liquidity sweep" in het label staat.



