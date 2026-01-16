# ICT V5 Strategy - Instellingen Documentatie

## Strategy Overzicht

**Market Logic:** Trade in the direction of structure after liquidity is taken.

**Decision Blocks:** 3
1. HTF Market Bias
2. Liquidity Sweep
3. Displacement Entry

---

## 1. Market Context

### Symbol
- **Default:** XAUUSD (Gold)
- **Opties:** XAUUSD, EURUSD, GBPUSD, BTCUSD

### Entry Timeframe
- **Default:** 5m
- **Opties:** 5m, 15m, 30m

### Test Period
- **Default:** 1mo (30 dagen)
- **Opties:** 1mo, 2mo, 3mo

---

## 2. HTF Market Bias (Block 1)

**Doel:** Trade alleen in de richting van laatste Break of Structure (BOS) op hogere timeframe.

### HTF Timeframe
- **Default:** 1h
- **Opties:** 1h, 4h, 1d

### BOS Lookback Periods
- **Default:** 50 candles
- **Min:** 20
- **Max:** 200
- **Beschrijving:** Aantal candles om terug te kijken voor BOS detectie

### Logica:
- Detecteert swing highs/lows op HTF
- Vindt laatste BOS (bullish of bearish)
- Mapt HTF bias naar entry timeframe via forward fill
- Entry candles krijgen: `BULLISH`, `BEARISH`, of `NEUTRAL`

---

## 3. Liquidity Sweep (Block 2)

**Doel:** Detecteert wanneer price equal highs/lows of session highs/lows raakt.

### Sweep Type
- **Default:** Equal Highs
- **Opties:**
  - `equal_highs` - Equal Highs
  - `equal_lows` - Equal Lows
  - `session_high` - Previous Session High
  - `session_low` - Previous Session Low

### Equal Level Tolerance
- **Default:** 0.1%
- **Min:** 0.05%
- **Max:** 1.0%
- **Step:** 0.05%
- **Beschrijving:** Prijsverschil tolerantie voor equal levels

### Lookback Periods
- **Default:** 20 candles
- **Min:** 10
- **Max:** 100
- **Beschrijving:** Aantal candles om terug te kijken voor equal levels

### Logica:
- Voor `equal_highs`: Checkt of huidige high binnen tolerance is van vorige highs
- Voor `equal_lows`: Checkt of huidige low binnen tolerance is van vorige lows
- Voor `session_high/low`: Checkt vorige 24 candles (session)

---

## 4. Displacement Entry (Block 3)

**Doel:** Detecteert sterke impulsive candle weg van de sweep. Entry op 50% retrace of first imbalance.

### Min Body Size
- **Default:** 70%
- **Min:** 50%
- **Max:** 95%
- **Beschrijving:** Minimum candle body als % van totale range

### Min Move
- **Default:** 1.5%
- **Min:** 0.5%
- **Max:** 5.0%
- **Step:** 0.1%
- **Beschrijving:** Minimum prijsbeweging vanaf sweep

### Entry Method
- **Default:** 50% Retrace
- **Opties:**
  - `50_retrace` - 50% Retrace
  - `first_imbalance` - First Imbalance
  - `both` - Both (50% retrace OR first imbalance)

### Logica:
- Detecteert candles met grote body (min_body_pct)
- Checkt sterke move (min_move_pct * 0.5 voor 5m timeframe)
- Entry op displacement price (close van displacement candle)
- **Note:** In productie zou je entry kunnen doen op volgende candle open of 50% retrace

---

## 5. Risk Management

### Stop Loss
- **Default:** Beyond Liquidity Sweep
- **Opties:**
  - `beyond_sweep` - Beyond Liquidity Sweep (0.1% onder/boven sweep)
  - `structure` - Beyond Structure
  - `atr` - ATR-based

### Take Profit (R-multiples)
- **Default:** 2.0R
- **Min:** 1.0R
- **Max:** 5.0R
- **Step:** 0.5R
- **Beschrijving:** Target: 1R-2R of next structure

### Risk per Trade (R)
- **Default:** 1.0R
- **Min:** 0.5R
- **Max:** 3.0R
- **Step:** 0.1R

### Exit Logica:
- **TP Hit:** Exit op TP price (2.0R default)
- **SL Hit:** Exit op SL price (beyond sweep)
- **Risk Calculation:** `risk = abs(entry_price - sl_price)`
- **TP Calculation:** `tp_price = entry_price + (risk * tp_r)` voor LONG

---

## Entry Condities (Alle moeten TRUE zijn)

1. ✅ **HTF Bias:** Moet `BULLISH` of `BEARISH` zijn (niet `NEUTRAL`)
2. ✅ **Liquidity Sweep:** Moet gedetecteerd zijn (binnen laatste 20 candles)
3. ✅ **Displacement:** Moet gedetecteerd zijn na sweep
4. ✅ **Direction Match:** Displacement moet in richting van HTF bias zijn
   - `BULLISH` bias + bullish candle → LONG
   - `BEARISH` bias + bearish candle → SHORT

---

## Technische Details

### Data Fetching
- Entry timeframe data wordt opgehaald (5m, 15m, of 30m)
- HTF data wordt opgehaald (1h, 4h, of 1d)
- Beide worden gecached via DataManager

### Performance
- **Data cleaning:** Eén keer aan het begin
- **HTF Bias:** Rolling BOS detectie per HTF candle
- **Sweep Detection:** Per entry candle (lookback)
- **Displacement:** Per entry candle (relatief aan vorige candle)

### Multi-Timeframe Mapping
- HTF bias wordt gemapped naar entry timeframe via forward fill
- Elke entry candle krijgt meest recente HTF bias
- Bias kan veranderen tijdens backtest periode

---

## Default Configuratie (Huidige Instellingen)

```json
{
  "symbol": "XAUUSD",
  "entryTimeframe": "5m",
  "testPeriod": "1mo",
  "htfMarketBias": {
    "timeframe": "1h",
    "bosLookback": 50
  },
  "liquiditySweep": {
    "sweepType": "equal_highs",
    "tolerance": 0.1,
    "lookback": 20
  },
  "displacementEntry": {
    "minBodyPct": 70,
    "minMovePct": 1.5,
    "entryMethod": "50_retrace"
  },
  "risk": {
    "stopLoss": "beyond_sweep",
    "takeProfit": 2.0,
    "riskPerTrade": 1.0
  }
}
```

---

## Aanbevolen Aanpassingen

### Voor Meer Trades:
- Verlaag `minBodyPct` naar 60%
- Verlaag `minMovePct` naar 1.0%
- Verhoog `tolerance` naar 0.2%
- Verhoog `lookback` naar 30-50

### Voor Betere Kwaliteit:
- Verhoog `minBodyPct` naar 80%
- Verhoog `minMovePct` naar 2.0%
- Verlaag `tolerance` naar 0.05%
- Gebruik `4h` of `1d` voor HTF

### Voor Andere Markten:
- **Forex (EURUSD):** Verlaag `minMovePct` naar 0.5-1.0%
- **Crypto (BTCUSD):** Verhoog `minMovePct` naar 2.0-3.0%
- **Stocks:** Gebruik `session_high/low` voor sweeps

---

## Notes

- Entry gebeurt op `displacement_price` (close van displacement candle)
- In productie zou je kunnen wachten op 50% retrace of volgende candle open
- SL is 0.1% onder/boven sweep price
- TP is 2.0R default (aanpasbaar)
- Alle condities moeten TRUE zijn voor entry (AND logica)

