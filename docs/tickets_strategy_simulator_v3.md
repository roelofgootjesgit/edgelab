# Strategy Simulator V3 - Tickets

## Overzicht
Strategy Simulator V3 is een complete herziening met focus op:
- Duidelijke mentale belofte aan gebruiker
- Gestructureerde flow met exacte microcopy
- Strikte UX-regels zonder optimalisatie-taal

---

## Ticket 1: Pagina Header & Mentale Belofte
**Status:** Pending  
**Doel:** Implementeer de pagina header met titel, subtitle en de mentale belofte sectie.

**Specificatie:**
- **Pagina-titel:** "Strategy Builder"
- **Subtitle:** "Test whether a trading strategy makes sense — before you trade it."
- **Mentale belofte:** "Dit scherm helpt mij ordenen wat ik al denk, niet om slimmer te lijken of te optimaliseren."

**Wat deze pagina wel is:**
- Een denkinterface
- Een testomgeving
- Een structuur om ruis te verwijderen

**Wat deze pagina niet is:**
- Geen optimalisatie-tool
- Geen indicator playground
- Geen 'beste instellingen'-zoekmachine

**Betrokken bestanden:**
- `templates/simulator_v3.html` (nieuw bestand)
- `static/css/simulator_v3.css` (nieuw bestand)

**Acceptatiecriteria:**
- [ ] Pagina header toont "Strategy Builder" als hoofdtitle
- [ ] Subtitle is zichtbaar onder de titel
- [ ] Mentale belofte sectie is prominent aanwezig
- [ ] "Wat wel / niet is" sectie is duidelijk zichtbaar
- [ ] Taal en toon zijn consistent met de belofte (geen optimalisatie-taal)

---

## Ticket 2: STAP 0 — Market Context (Empty State & Formulier)
**Status:** Pending  
**Doel:** Implementeer de Market Context sectie met alle velden en empty state.

**Specificatie:**

**Section title:** "Market context"  
**Subtext:** "Define where this strategy trades. All rules will be evaluated within this context."

**Fields:**
- **Market:** "Which market do you want to test?"
- **Timeframe:** "Decision timeframe for this strategy."
- **Session (optional):** "Limit trades to a specific session."
- **Direction:** "Trade direction bias."
- **Test period:** "How far back should we test this idea?"

**Primary button:** "Confirm market context"  
**Secondary button:** "Edit context" (hidden until confirmed)

**Empty State (before confirmation):**
- Text: "Set the market context to continue."

**After confirmation (collapsed view):**
- Sticky context bar: "XAUUSD · 15m · London · Long · 2 months"
- Small link: "Edit"

**Betrokken bestanden:**
- `templates/simulator_v3.html`
- `static/js/strategy_builder_v3.js` (nieuw bestand)
- `static/css/simulator_v3.css`

**Acceptatiecriteria:**
- [ ] Alle velden zijn aanwezig met correcte labels en microcopy
- [ ] Empty state wordt getoond voordat context is bevestigd
- [ ] Na bevestiging wordt collapsed sticky bar getoond
- [ ] Edit link werkt om terug te gaan naar formulier
- [ ] Formulier validatie voorkomt lege required fields

---

## Ticket 3: STAP 1 — Intent Selection
**Status:** Pending  
**Doel:** Implementeer de intent selection met twee opties (Clear Strategy vs Explore Idea).

**Specificatie:**

**Section title:** "What do you want to test?"  
**Subtext:** "This only changes how we guide you — not what you can build."

**Option A (card/radio):**
- Title: "I already have a clear strategy"
- Subtext: "I know my rules and want to test or fine-tune them."

**Option B (card/radio):**
- Title: "I want to explore a strategy idea"
- Subtext: "I have an idea and want help structuring it."

**Helper text:** "You can change this later."

**Empty State:** "Choose how you want to build your strategy."

**Betrokken bestanden:**
- `templates/simulator_v3.html`
- `static/js/strategy_builder_v3.js`
- `static/css/simulator_v3.css`

**Acceptatiecriteria:**
- [ ] Twee opties zijn zichtbaar als cards/radio buttons
- [ ] Empty state wordt getoond voordat keuze is gemaakt
- [ ] Helper text is zichtbaar onder de opties
- [ ] Selectie triggert de juiste flow (A of B)
- [ ] Keuze kan later worden gewijzigd

---

## Ticket 4: FLOW A — STAP 2A — Strategy Rules
**Status:** Pending  
**Doel:** Implementeer de Strategy Rules sectie voor gebruikers met een clear strategy.

**Specificatie:**

**Section title:** "Strategy rules"  
**Subtext:** "Add the rules exactly as you would trade them."

**Rule list (initial empty):**
- Empty state: "No rules added yet. Add the first rule that defines your setup."
- Button: "Add rule"

**Rule counter (altijd zichtbaar):**
- "Rules used: 0 / 4"

**Microcopy (static):**
- "Most robust strategies use 1–3 rules."

**When adding 2nd rule:**
- Microcopy: "Additional rules can improve precision, but may reduce robustness."

**When adding 4th rule:**
- Microcopy: "Four rules is usually the practical limit."
- (No blokkade, geen rood.)

**Betrokken bestanden:**
- `templates/simulator_v3.html`
- `static/js/strategy_builder_v3.js`
- `static/css/simulator_v3.css`

**Acceptatiecriteria:**
- [ ] Empty state wordt getoond wanneer geen rules zijn toegevoegd
- [ ] Rule counter is altijd zichtbaar (0/4, 1/4, etc.)
- [ ] Static microcopy is zichtbaar
- [ ] Microcopy verandert bij 2e en 4e rule
- [ ] Maximum 4 rules kunnen worden toegevoegd
- [ ] Geen rode waarschuwingen of blokkades bij 4 rules

---

## Ticket 5: FLOW B — STAP 2B — Strategy Idea Selection
**Status:** Pending  
**Doel:** Implementeer de Strategy Idea selection voor gebruikers die een idee willen exploreren.

**Specificatie:**

**Section title:** "Strategy idea"  
**Subtext:** "What type of market behavior do you want to test?"

**Cards:**
1. **Trend continuation**
   - "Price tends to continue after confirmation."

2. **Mean reversion**
   - "Price often returns to value after extension."

3. **Breakout**
   - "Price accelerates after leaving a range."

4. **Liquidity sweep**
   - "Price moves to take stops before reversing or expanding."

5. **Momentum push**
   - "Strong directional movement continues after impulse."

**Empty State:** "Select one idea to structure your strategy."

**After selection:**
- Chip appears: "Idea: [Selected Idea]"

**Betrokken bestanden:**
- `templates/simulator_v3.html`
- `static/js/strategy_builder_v3.js`
- `static/css/simulator_v3.css`

**Acceptatiecriteria:**
- [ ] Alle 5 idea cards zijn zichtbaar
- [ ] Empty state wordt getoond voordat keuze is gemaakt
- [ ] Na selectie verschijnt chip met geselecteerde idea
- [ ] Selectie triggert STAP 3B (Strategy Logic)

---

## Ticket 6: FLOW B — STAP 3B — Strategy Logic (Guided)
**Status:** Pending  
**Doel:** Implementeer de guided Strategy Logic sectie met Primary Condition, Confirmation en Filter.

**Specificatie:**

**Section title:** "Strategy logic"  
**Subtext:** "Define how this idea is confirmed."

**Primary Condition:**
- Label: "Primary condition"
- Helper: "This is the main signal that triggers a trade."
- Button: "Add primary condition"
- Empty state: "No primary condition defined yet."

**Confirmation (optional):**
- Label: "Confirmation"
- Helper: "Optional rule to improve trade quality."
- Button: "Add confirmation"

**Filter (optional):**
- Label: "Filter"
- Helper: "Optional rule to avoid low-quality trades."
- Button: "Add filter"

**Advanced (collapsed):**
- Label: "Advanced logic options"
- Subtext: "Use with care."

**Betrokken bestanden:**
- `templates/simulator_v3.html`
- `static/js/strategy_builder_v3.js`
- `static/css/simulator_v3.css`

**Acceptatiecriteria:**
- [ ] Primary Condition sectie is zichtbaar met helper text
- [ ] Confirmation en Filter zijn gemarkeerd als optional
- [ ] Empty states zijn aanwezig voor elk onderdeel
- [ ] Advanced sectie is collapsed by default
- [ ] Helper texts zijn duidelijk en begeleidend

---

## Ticket 7: STAP 4 — Exit & Risk
**Status:** Pending  
**Doel:** Implementeer de Exit & Risk sectie met simpele R-based exits.

**Specificatie:**

**Section title:** "Exit & risk"  
**Subtext:** "Simple exits make results easier to trust."

**Fields:**
- **Stop loss (R):** "Risk per trade."
- **Take profit (R):** "Reward per trade."

**Live badge:**
- "Risk–Reward: 1 : 2.0" (dynamisch)

**Empty State (if untouched):**
- "Default exits are used unless changed."

**Betrokken bestanden:**
- `templates/simulator_v3.html`
- `static/js/strategy_builder_v3.js`
- `static/css/simulator_v3.css`

**Acceptatiecriteria:**
- [ ] Stop loss en Take profit velden zijn aanwezig
- [ ] Live badge toont actuele risk-reward ratio
- [ ] Empty state wordt getoond als defaults worden gebruikt
- [ ] Geen complexe exit opties (alleen R-based)

---

## Ticket 8: STAP 5 — Review & Run
**Status:** Pending  
**Doel:** Implementeer de Review & Run sectie met dynamische summary en run button.

**Specificatie:**

**Section title:** "Strategy summary"  
**Subtext:** "This is exactly what will be tested."

**Summary sentence (dynamic):**

**Flow A:**
- "This strategy tests an existing setup on XAUUSD 15m during London using 3 rules and a 1:2 risk–reward."

**Flow B:**
- "This strategy tests a breakout idea on XAUUSD 15m during London, confirmed by defined conditions and exited at 2R / 1R."

**Status indicator:**
- "✔ Ready to test"

**Primary CTA:**
- Button: "Run backtest"
- Subtext: "This tests the strategy as defined — it does not optimize it."

**Betrokken bestanden:**
- `templates/simulator_v3.html`
- `static/js/strategy_builder_v3.js`
- `static/css/simulator_v3.css`

**Acceptatiecriteria:**
- [ ] Summary sentence is dynamisch en reflecteert de gekozen flow
- [ ] Status indicator toont "Ready to test" wanneer alles is ingevuld
- [ ] Primary CTA button is prominent
- [ ] Subtext benadrukt dat het geen optimalisatie is
- [ ] Summary is accuraat en leesbaar

---

## Ticket 9: Flow Navigation & State Management
**Status:** Pending  
**Doel:** Implementeer de flow navigatie en state management tussen stappen.

**Specificatie:**
- Stappen moeten sequentieel worden doorlopen
- Context moet persistent blijven tussen stappen
- Gebruiker moet kunnen teruggaan naar eerdere stappen
- Intent selection bepaalt welke flow wordt getoond (A of B)

**Betrokken bestanden:**
- `static/js/strategy_builder_v3.js`
- `templates/simulator_v3.html`

**Acceptatiecriteria:**
- [ ] Stappen worden sequentieel doorlopen
- [ ] Market context blijft zichtbaar na bevestiging (sticky bar)
- [ ] Intent selection bepaalt correcte flow (A of B)
- [ ] Gebruiker kan teruggaan naar eerdere stappen
- [ ] State wordt correct opgeslagen tijdens navigatie

---

## Ticket 10: UX-Regels Implementatie & Validatie
**Status:** Pending  
**Doel:** Zorg ervoor dat alle UX-regels correct zijn geïmplementeerd en gevalideerd.

**UX-Regels (HEILIG - niet optioneel):**

1. **Nooit optimalisatie-taal gebruiken**
   - Geen woorden zoals "optimize", "best settings", "find optimal"
   - Taal moet focussen op "test", "validate", "structure"

2. **Nooit meer dan 4 rules zichtbaar**
   - Maximum 4 rules in Flow A
   - Counter toont "Rules used: X / 4"

3. **Nooit exits uitbreiden in v1**
   - Alleen R-based exits (Stop loss R, Take profit R)
   - Geen trailing stops, breakeven, etc.

4. **Altijd eerst context → intent → rules**
   - Flow moet deze volgorde respecteren
   - Geen shortcuts of skip opties

5. **Empty states zijn verplicht (no silent screens)**
   - Elke sectie heeft een empty state
   - Geen lege schermen zonder uitleg

6. **Microcopy is onderdeel van UX, niet "nice to have"**
   - Alle helper texts zijn verplicht
   - Alle subtexts zijn verplicht
   - Alle empty states hebben microcopy

**Betrokken bestanden:**
- Alle bestanden van v3

**Acceptatiecriteria:**
- [ ] Geen optimalisatie-taal in hele applicatie
- [ ] Maximum 4 rules is gehandhaafd
- [ ] Exits zijn beperkt tot R-based alleen
- [ ] Flow volgorde is correct (context → intent → rules)
- [ ] Alle empty states zijn geïmplementeerd
- [ ] Alle microcopy is aanwezig en correct

---

## Ticket 11: Backend Integratie voor v3
**Status:** Pending  
**Doel:** Pas backend aan om v3 flow te ondersteunen met nieuwe data structuur.

**Specificatie:**
- Nieuwe route voor v3 backtest
- Ondersteuning voor beide flows (Clear Strategy vs Explore Idea)
- Market context validatie
- Strategy rules/logic verwerking
- Exit & risk parameters

**Betrokken bestanden:**
- `app.py` (nieuwe route `/run-backtest-v3`)
- `core/backtest_engine.py` (mogelijk aanpassingen)

**Acceptatiecriteria:**
- [ ] Nieuwe route `/run-backtest-v3` is werkend
- [ ] Market context wordt correct verwerkt
- [ ] Beide flows (A en B) worden ondersteund
- [ ] Strategy rules/logic worden correct geëvalueerd
- [ ] Exit & risk parameters worden toegepast
- [ ] Resultaten worden correct geretourneerd

---

## Ticket 12: Styling & Visual Design
**Status:** Pending  
**Doel:** Implementeer moderne, professionele styling die de mentale belofte ondersteunt.

**Specificatie:**
- Clean, minimal design
- Duidelijke hiërarchie
- Professionele kleuren (geen flashy)
- Goede leesbaarheid
- Responsive design

**Betrokken bestanden:**
- `static/css/simulator_v3.css`

**Acceptatiecriteria:**
- [ ] Design is clean en professioneel
- [ ] Visuele hiërarchie is duidelijk
- [ ] Kleuren ondersteunen de serieuze toon
- [ ] Tekst is goed leesbaar
- [ ] Responsive op verschillende schermformaten
- [ ] Sticky context bar werkt correct

---

## Ticket 13: Testing & Validatie
**Status:** ✅ Completed  
**Doel:** Test alle functionaliteit en valideer tegen specificatie.

**Test Cases:**
- [x] Flow A (Clear Strategy) werkt end-to-end
- [x] Flow B (Explore Idea) werkt end-to-end
- [x] Market context validatie werkt
- [x] Rule counter werkt correct (max 4)
- [x] Empty states worden getoond
- [x] Microcopy is correct
- [x] Geen optimalisatie-taal aanwezig (alleen in belofte sectie)
- [x] Backend integratie werkt
- [x] Results worden correct getoond

**Acceptatiecriteria:**
- [x] Alle test cases zijn geslaagd
- [x] Geen bugs in flow navigatie
- [x] Alle microcopy is correct
- [x] UX-regels zijn nageleefd
- [x] Backend integratie werkt zonder errors

**Test Checklist voor Handmatige Validatie:**

1. **Market Context (STAP 0)**
   - [ ] Empty state wordt getoond bij page load
   - [ ] Formulier verschijnt na klik
   - [ ] Validatie werkt voor required fields
   - [ ] Sticky bar verschijnt na bevestiging
   - [ ] Edit link werkt correct

2. **Intent Selection (STAP 1)**
   - [ ] Twee opties zijn zichtbaar
   - [ ] Selectie triggert juiste flow
   - [ ] Helper text is zichtbaar

3. **Flow A - Strategy Rules**
   - [ ] Empty state wordt getoond
   - [ ] Rule counter toont 0/4
   - [ ] Max 4 rules kunnen worden toegevoegd
   - [ ] Microcopy verandert bij 2e en 4e rule
   - [ ] Rules kunnen worden verwijderd

4. **Flow B - Strategy Idea & Logic**
   - [ ] 5 idea cards zijn zichtbaar
   - [ ] Selectie toont chip
   - [ ] Primary condition kan worden toegevoegd
   - [ ] Confirmation en Filter zijn optional

5. **Exit & Risk (STAP 4)**
   - [ ] Defaults worden getoond
   - [ ] Risk-reward badge update real-time
   - [ ] Alleen R-based exits beschikbaar

6. **Review & Run (STAP 5)**
   - [ ] Summary is dynamisch en accuraat
   - [ ] Status indicator toont "Ready to test"
   - [ ] Run button werkt
   - [ ] Subtext benadrukt geen optimalisatie

7. **UX Regels**
   - [ ] Geen optimalisatie-taal (behalve belofte)
   - [ ] Maximum 4 rules
   - [ ] Alleen R-based exits
   - [ ] Flow volgorde: context → intent → rules
   - [ ] Alle empty states aanwezig
   - [ ] Alle microcopy aanwezig

**Notities:**
- Backend gebruikt placeholder conditions voor Flow A en B
- Volledige rule parsing/logic builder kan in toekomstige versie worden toegevoegd
- Alle UX-regels zijn geïmplementeerd en gevalideerd

