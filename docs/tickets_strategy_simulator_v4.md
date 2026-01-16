# Strategy Simulator V4 - Decision Block Model - Tickets

## Overzicht
Strategy Simulator V4 introduceert een fundamentele herdefinitie:
- **Oude denkwijze**: 1 condition = 1 indicator / regel
- **Nieuwe denkwijze**: 1 condition = 1 Decision Block

Een Decision Block:
- Vertegenwoordigt één beslismoment
- Kan intern bestaan uit meerdere sub-confirmaties
- Voelt voor de trader als "ja/nee: dit klopt"

---

## Ticket 1: Fundamentele Herdefinitie - Decision Block Model
**Status:** Pending  
**Doel:** Implementeer de fundamentele herdefinitie van conditions naar Decision Blocks.

**Specificatie:**
- 1 condition = 1 Decision Block (niet 1 indicator)
- Decision Blocks bevatten meerdere sub-confirmaties
- Max 4 Decision Blocks per strategie (hard limit)
- Elke Decision Block heeft:
  - Een titel
  - Een uitlegzin
  - Meerdere selecteerbare sub-confirmaties

**Sub-confirmaties zijn:**
- Checkboxes
- Toggles
- Dropdowns
- ❌ NOOIT vrije tekst

**Betrokken bestanden:**
- `templates/simulator_v4.html` (nieuw)
- `static/js/strategy_builder_v4.js` (nieuw)
- `static/css/simulator_v4.css` (nieuw)

**Acceptatiecriteria:**
- [ ] Decision Block model is geïmplementeerd
- [ ] Max 4 Decision Blocks enforced
- [ ] Sub-confirmaties zijn checkboxes/toggles/dropdowns
- [ ] Geen vrije tekst input voor sub-confirmaties
- [ ] Elke Decision Block heeft titel en uitlegzin

---

## Ticket 2: Decision Block UI Component
**Status:** Pending  
**Doel:** Bouw de Decision Block UI component met titel, uitlegzin en sub-confirmaties.

**Specificatie:**

**Decision Block Structuur:**
```
Decision Block Card:
├── Title (editable)
├── Explanation (editable)
├── Sub-confirmations:
│   ├── Checkbox/Toggle/Dropdown items
│   └── "Add sub-confirmation" button
└── Remove button
```

**UX Copy:**
- Decision Block label: "Groups multiple confirmations into one decision."
- Sub-confirmations label: "Select all that apply."
- Tooltip bij veel confirmaties: "Multiple confirmations increase confidence, but may reduce flexibility."

**Betrokken bestanden:**
- `templates/simulator_v4.html`
- `static/js/strategy_builder_v4.js`
- `static/css/simulator_v4.css`

**Acceptatiecriteria:**
- [ ] Decision Block card component is werkend
- [ ] Titel en uitlegzin zijn editable
- [ ] Sub-confirmaties kunnen worden toegevoegd
- [ ] Sub-confirmaties zijn checkboxes/toggles/dropdowns
- [ ] Tooltip is aanwezig bij veel confirmaties
- [ ] Remove functionaliteit werkt

---

## Ticket 3: Template Selector - Base Structure
**Status:** Pending  
**Doel:** Implementeer template selector met alle beschikbare templates.

**Templates:**
1. 🧠 ICT / SMC Base Setup (3 Decision Blocks)
2. 📈 Trend Following (3 Decision Blocks)
3. 🔄 Mean Reversion (2 Decision Blocks)
4. 🚀 Breakout Momentum (3 Decision Blocks)
5. ✨ Golden Cross (2 Decision Blocks)
6. 🌊 Supertrend Trend (3 Decision Blocks)
7. 📉 RSI Oversold Bounce (3 Decision Blocks)
8. ⚖️ VWAP Reversion (3 Decision Blocks)
9. ⚡ Momentum Scalping (4 Decision Blocks)
10. 🧩 My Templates (Soon)

**Template Structuur:**
- Intent: "Explore strategy idea" (vooraf ingevuld)
- Market context: suggesties (niet locked)
- Decision Blocks: vooraf aangemaakt
- Sub-confirmaties: voorgeselecteerd (aanpasbaar)
- Exit: simpele R-defaults

**Betrokken bestanden:**
- `templates/simulator_v4.html`
- `static/js/strategy_builder_v4.js`
- `templates/template_selector_v4.html` (mogelijk)

**Acceptatiecriteria:**
- [ ] Template selector toont alle templates
- [ ] Template selectie vult vooraf in:
  - Intent
  - Market context suggesties
  - Decision Blocks
  - Sub-confirmaties
  - Exit defaults
- [ ] Gebruiker kan alles aanpassen na selectie
- [ ] "My Templates" toont "Soon" message

---

## Ticket 4: Template 1 - ICT / SMC Base Setup
**Status:** Pending  
**Doel:** Implementeer ICT / SMC Base Setup template met 3 Decision Blocks.

**Decision Block 1 — Market Bias:**
- Titel: "Market Bias"
- Uitleg: "Defines higher-timeframe directional context."
- Sub-confirmaties:
  - ☐ HTF market structure aligned
  - ☐ Premium / Discount zone respected
  - ☐ Higher-timeframe bias confirmed

**Decision Block 2 — Liquidity Event:**
- Titel: "Liquidity Event"
- Uitleg: "Identifies where smart money is active."
- Sub-confirmaties:
  - ☐ Liquidity sweep present
  - ☐ Equal highs / lows taken
  - ☐ Stop hunt or inducement

**Decision Block 3 — Entry Model:**
- Titel: "Entry Model"
- Uitleg: "Defines precise trade entry timing."
- Sub-confirmaties:
  - ☐ Fair Value Gap entry
  - ☐ Displacement move
  - ☐ Lower-timeframe structure shift
  - ☐ Session timing aligned

**Betrokken bestanden:**
- `static/js/templates/ict_smc_template.js` (nieuw)
- `static/js/strategy_builder_v4.js`

**Acceptatiecriteria:**
- [ ] Template bevat 3 Decision Blocks
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] Sub-confirmaties zijn voorgeselecteerd (aanpasbaar)
- [ ] Template kan worden geladen en aangepast

---

## Ticket 5: Template 2 - Trend Following
**Status:** Pending  
**Doel:** Implementeer Trend Following template met 3 Decision Blocks.

**Decision Block 1 — Trend Direction:**
- Sub-confirmaties:
  - ☐ Higher-high / higher-low structure
  - ☐ Moving average alignment
  - ☐ Market regime trending

**Decision Block 2 — Continuation Trigger:**
- Sub-confirmaties:
  - ☐ Pullback into value
  - ☐ Break & retest
  - ☐ Momentum continuation signal

**Decision Block 3 — Strength Filter:**
- Sub-confirmaties:
  - ☐ Volatility sufficient
  - ☐ No nearby structure resistance
  - ☐ Session alignment

**Acceptatiecriteria:**
- [ ] Template bevat 3 Decision Blocks
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] Template kan worden geladen

---

## Ticket 6: Template 3 - Mean Reversion
**Status:** Pending  
**Doel:** Implementeer Mean Reversion template met 2 Decision Blocks.

**Decision Block 1 — Extension From Value:**
- Sub-confirmaties:
  - ☐ Distance from mean
  - ☐ Momentum exhaustion
  - ☐ Overextension signal

**Decision Block 2 — Reversion Confirmation:**
- Sub-confirmaties:
  - ☐ Price rejection
  - ☐ Momentum shift
  - ☐ Structure holding

**Acceptatiecriteria:**
- [ ] Template bevat 2 Decision Blocks
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] Template kan worden geladen

---

## Ticket 7: Template 4 - Breakout Momentum
**Status:** Pending  
**Doel:** Implementeer Breakout Momentum template met 3 Decision Blocks.

**Decision Block 1 — Compression:**
- Sub-confirmaties:
  - ☐ Range present
  - ☐ Volatility contraction
  - ☐ Equal highs / lows

**Decision Block 2 — Break With Intent:**
- Sub-confirmaties:
  - ☐ Strong impulse break
  - ☐ Volume expansion
  - ☐ Structure break

**Decision Block 3 — Failure Filter:**
- Sub-confirmaties:
  - ☐ No immediate rejection
  - ☐ Retest holds
  - ☐ Momentum sustained

**Acceptatiecriteria:**
- [ ] Template bevat 3 Decision Blocks
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] Template kan worden geladen

---

## Ticket 8: Template 5 - Golden Cross
**Status:** Pending  
**Doel:** Implementeer Golden Cross template met 2 Decision Blocks.

**Decision Block 1 — Trend Shift:**
- Sub-confirmaties:
  - ☐ Fast MA crosses slow MA
  - ☐ Slope confirmation
  - ☐ HTF alignment

**Decision Block 2 — Environment Filter:**
- Sub-confirmaties:
  - ☐ Trending regime
  - ☐ No range compression

**Acceptatiecriteria:**
- [ ] Template bevat 2 Decision Blocks
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] Template kan worden geladen

---

## Ticket 9: Template 6 - Supertrend Trend
**Status:** Pending  
**Doel:** Implementeer Supertrend Trend template met 3 Decision Blocks.

**Decision Block 1 — Trend State:**
- Sub-confirmaties:
  - ☐ Supertrend direction
  - ☐ Price above / below trend line

**Decision Block 2 — Entry Alignment:**
- Sub-confirmaties:
  - ☐ Pullback into trend
  - ☐ Continuation signal

**Decision Block 3 — Volatility Filter:**
- Sub-confirmaties:
  - ☐ ATR sufficient
  - ☐ No compression

**Acceptatiecriteria:**
- [ ] Template bevat 3 Decision Blocks
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] Template kan worden geladen

---

## Ticket 10: Template 7 - RSI Oversold Bounce
**Status:** Pending  
**Doel:** Implementeer RSI Oversold Bounce template met 3 Decision Blocks.

**Decision Block 1 — Momentum Extreme:**
- Sub-confirmaties:
  - ☐ RSI oversold / overbought
  - ☐ Momentum divergence

**Decision Block 2 — Price Reaction:**
- Sub-confirmaties:
  - ☐ Rejection candle
  - ☐ Structure hold

**Decision Block 3 — Trend Filter:**
- Sub-confirmaties:
  - ☐ Trade with higher-timeframe bias

**Acceptatiecriteria:**
- [ ] Template bevat 3 Decision Blocks
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] RSI is selecteerbaar, niet tekstueel
- [ ] Template kan worden geladen

---

## Ticket 11: Template 8 - VWAP Reversion
**Status:** Pending  
**Doel:** Implementeer VWAP Reversion template met 3 Decision Blocks.

**Decision Block 1 — Distance From VWAP:**
- Sub-confirmaties:
  - ☐ Price extended from VWAP
  - ☐ Deviation threshold met

**Decision Block 2 — Rejection Signal:**
- Sub-confirmaties:
  - ☐ Wick rejection
  - ☐ Momentum slowdown

**Decision Block 3 — Session Filter:**
- Sub-confirmaties:
  - ☐ Active session
  - ☐ No major news

**Acceptatiecriteria:**
- [ ] Template bevat 3 Decision Blocks
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] Template kan worden geladen

---

## Ticket 12: Template 9 - Momentum Scalping
**Status:** Pending  
**Doel:** Implementeer Momentum Scalping template met 4 Decision Blocks.

**Decision Block 1 — Momentum Ignition:**
- Sub-confirmaties:
  - ☐ Sudden impulse
  - ☐ Break from micro-range

**Decision Block 2 — Volume / Volatility:**
- Sub-confirmaties:
  - ☐ Volume spike
  - ☐ Volatility expansion

**Decision Block 3 — Directional Bias:**
- Sub-confirmaties:
  - ☐ Micro-trend aligned
  - ☐ HTF not opposing

**Decision Block 4 — Time Filter:**
- Sub-confirmaties:
  - ☐ Killzone / session
  - ☐ No chop conditions

**Notitie:** Higher complexity, higher execution sensitivity.

**Acceptatiecriteria:**
- [ ] Template bevat 4 Decision Blocks (max)
- [ ] Alle sub-confirmaties zijn aanwezig
- [ ] Template kan worden geladen

---

## Ticket 13: Template 10 - My Templates (Placeholder)
**Status:** Pending  
**Doel:** Implementeer "My Templates" placeholder.

**UX Copy:**
"Save your own strategies once you understand why they work."

**Notitie:** Opslaan = expliciete intent tot begrip.

**Acceptatiecriteria:**
- [ ] "My Templates" sectie is zichtbaar
- [ ] "Soon" message wordt getoond
- [ ] UX copy is aanwezig

---

## Ticket 14: Decision Block Counter & Validation
**Status:** Pending  
**Doel:** Implementeer counter en validatie voor Decision Blocks.

**Specificatie:**
- Counter: "Decision Blocks: X / 4"
- Hard limit: maximum 4 Decision Blocks
- Validatie: min 1 Decision Block vereist
- Elke Decision Block moet min 1 sub-confirmatie hebben

**Acceptatiecriteria:**
- [ ] Counter is altijd zichtbaar
- [ ] Max 4 Decision Blocks enforced
- [ ] Validatie voorkomt 0 Decision Blocks
- [ ] Validatie voorkomt Decision Blocks zonder sub-confirmaties

---

## Ticket 15: Sub-confirmation Types - Checkbox Implementation
**Status:** Pending  
**Doel:** Implementeer checkbox sub-confirmaties.

**Specificatie:**
- Checkbox voor boolean confirmaties
- Label is duidelijk en beschrijvend
- Kan worden aangevinkt/uitgevinkt
- State wordt opgeslagen in appState

**Acceptatiecriteria:**
- [ ] Checkboxes werken correct
- [ ] State wordt opgeslagen
- [ ] Labels zijn duidelijk

---

## Ticket 16: Sub-confirmation Types - Toggle Implementation
**Status:** Pending  
**Doel:** Implementeer toggle sub-confirmaties.

**Specificatie:**
- Toggle voor on/off confirmaties
- Visueel duidelijk (aan/uit)
- State wordt opgeslagen

**Acceptatiecriteria:**
- [ ] Toggles werken correct
- [ ] Visueel duidelijk
- [ ] State wordt opgeslagen

---

## Ticket 17: Sub-confirmation Types - Dropdown Implementation
**Status:** Pending  
**Doel:** Implementeer dropdown sub-confirmaties.

**Specificatie:**
- Dropdown voor selectie uit opties
- Bijvoorbeeld: "RSI level" → dropdown met "Oversold", "Overbought", "Neutral"
- State wordt opgeslagen

**Acceptatiecriteria:**
- [ ] Dropdowns werken correct
- [ ] Opties zijn duidelijk
- [ ] State wordt opgeslagen

---

## Ticket 18: Template Data Structure & Storage
**Status:** Pending  
**Doel:** Definieer en implementeer template data structuur.

**Data Structuur:**
```javascript
{
  id: 'ict_smc',
  name: 'ICT / SMC Base Setup',
  intent: 'explore',
  marketContext: {
    suggestions: { market: 'XAUUSD', timeframe: '15m', ... }
  },
  decisionBlocks: [
    {
      id: 'block1',
      title: 'Market Bias',
      explanation: 'Defines higher-timeframe directional context.',
      subConfirmations: [
        { type: 'checkbox', label: 'HTF market structure aligned', selected: true },
        ...
      ]
    },
    ...
  ],
  exit: { stopLoss: 1, takeProfit: 2 }
}
```

**Acceptatiecriteria:**
- [ ] Data structuur is gedefinieerd
- [ ] Templates worden opgeslagen in JSON
- [ ] Templates kunnen worden geladen
- [ ] Templates kunnen worden aangepast

---

## Ticket 19: Backend Integration - Decision Block Processing
**Status:** Pending  
**Doel:** Pas backend aan om Decision Blocks te verwerken.

**Specificatie:**
- Backend moet Decision Blocks ontvangen
- Decision Blocks moeten worden omgezet naar backtest conditions
- Sub-confirmaties moeten worden geëvalueerd
- Zie backend document voor details

**Betrokken bestanden:**
- `app.py` (nieuwe route `/run-backtest-v4`)
- `core/backtest_engine.py` (mogelijk aanpassingen)

**Acceptatiecriteria:**
- [ ] Backend route ontvangt Decision Blocks
- [ ] Decision Blocks worden verwerkt
- [ ] Backtest wordt uitgevoerd
- [ ] Results worden geretourneerd

---

## Ticket 20: UX Copy & Tooltips
**Status:** Pending  
**Doel:** Implementeer alle UX copy en tooltips.

**UX Copy:**
- Decision Block: "Groups multiple confirmations into one decision."
- Sub-confirmations: "Select all that apply."
- Tooltip bij veel confirmaties: "Multiple confirmations increase confidence, but may reduce flexibility."

**Acceptatiecriteria:**
- [ ] Alle UX copy is aanwezig
- [ ] Tooltips zijn geïmplementeerd
- [ ] Copy is consistent door hele applicatie

---

## Ticket 21: Empty States & Onboarding
**Status:** Pending  
**Doel:** Implementeer empty states en onboarding flow.

**Empty States:**
- Geen Decision Blocks: "Add your first Decision Block to define a strategy decision point."
- Geen sub-confirmaties: "Add sub-confirmations to this Decision Block."

**Acceptatiecriteria:**
- [ ] Empty states zijn aanwezig
- [ ] Empty states zijn helpend
- [ ] Onboarding flow is duidelijk

---

## Ticket 22: Styling & Visual Design
**Status:** Pending  
**Doel:** Implementeer professionele styling voor v4.

**Specificatie:**
- Clean, modern design
- Decision Blocks zijn visueel duidelijk
- Sub-confirmaties zijn goed georganiseerd
- Responsive design

**Acceptatiecriteria:**
- [ ] Design is professioneel
- [ ] Decision Blocks zijn visueel duidelijk
- [ ] Responsive op alle schermen
- [ ] Consistent met QuantMetrics design system

---

## Ticket 23: Testing & Validatie
**Status:** Pending  
**Doel:** Test alle functionaliteit en valideer tegen specificatie.

**Test Cases:**
- [ ] Alle templates kunnen worden geladen
- [ ] Decision Blocks kunnen worden toegevoegd/verwijderd
- [ ] Max 4 Decision Blocks enforced
- [ ] Sub-confirmaties werken (checkbox/toggle/dropdown)
- [ ] Templates kunnen worden aangepast
- [ ] Backend integratie werkt
- [ ] UX copy is correct
- [ ] Empty states werken

**Acceptatiecriteria:**
- [ ] Alle test cases zijn geslaagd
- [ ] Geen bugs
- [ ] Alle UX-regels zijn nageleefd
- [ ] Backend integratie werkt zonder errors



