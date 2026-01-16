# Strategy Simulator V2 - Verbetering Tickets

## Ticket 1: Frontend-backend integratie operator/value
**Status:** ✅ Completed  
**Doel:** Operator en value die in de frontend worden ingevoerd correct doorgeven naar de backend en verwerken in de backtest-engine.

**Betrokken bestanden:**
- `static/js/strategy_builder.js` (regel 821-826: formData conditions)
- `app.py` (regel 174-200: run-backtest-v2 route)
- `core/backtest_engine.py` (regel 278-295: _simulate_modular methode, regel 513-613: _evaluate_module_condition)

**Uitgevoerd:**
- ✅ Frontend stuurt operator en value mee per condition in formData (regel 821-826)
- ✅ Backend ontvangt en valideert operator/value (regel 178-186)
- ✅ Backend slaat module_id op voor kolom detectie (regel 198)
- ✅ Backtest-engine verwerkt operator/value bij het evalueren van entry conditions (regel 281-295)
- ✅ Generic evaluatie functie `_evaluate_module_condition` toegevoegd (regel 513-613)
- ✅ Ondersteunt operators: `>`, `<`, `>=`, `<=`, `==`, `crosses_above`, `crosses_below`
- ✅ Debug logging toegevoegd voor troubleshooting

**Acceptatiecriteria:**
- [x] Frontend stuurt operator en value mee per condition in formData
- [x] Backend ontvangt en valideert operator/value
- [x] Backtest-engine verwerkt operator/value bij het evalueren van entry conditions
- [x] Generic evaluatie logica geïmplementeerd met kolom detectie

**Notities:**
- Implementatie gebruikt module_id voor kolom naam detectie (bijv. 'rsi' module → 'rsi' kolom)
- Fallback mechanisme: als kolom niet gevonden wordt, wordt module's eigen check_entry_condition gebruikt
- Debug logging aanwezig voor troubleshooting (regel 255-264, 565-580)

---

## Ticket 2: Generic indicator evaluatie in backtest-engine
**Status:** ✅ Completed  
**Doel:** Generic evaluatie logica toevoegen aan backtest-engine voor modules die een simpele operator/value check nodig hebben (zoals RSI > 30, MACD > 0).

**Betrokken bestanden:**
- `core/backtest_engine.py` (_simulate_modular methode, regel 278-295)
- `core/backtest_engine.py` (_evaluate_module_condition methode, regel 513-621)

**Uitgevoerd:**
- ✅ Generic evaluatie functie `_evaluate_module_condition` geïmplementeerd (regel 513-621)
- ✅ Ondersteunt alle operators: `>`, `<`, `>=`, `<=`, `==`, `crosses_above`, `crosses_below`
- ✅ Slimme kolom detectie:
  - Directe match: module_id → kolom (bijv. 'rsi' → 'rsi', 'macd' → 'macd')
  - Period-based: module_id + period → kolom (bijv. 'sma' + period 50 → 'sma_50')
  - Pattern matching: zoekt kolommen die beginnen met module_id (voor variaties)
- ✅ Modules kunnen optioneel operator/value gebruiken: als operator/value aanwezig is, wordt generic evaluatie gebruikt; anders fallback naar module's eigen check_entry_condition
- ✅ Bestaande module-specifieke logica blijft werken via fallback mechanisme (regel 285-289)
- ✅ Debug logging toegevoegd voor troubleshooting

**Acceptatiecriteria:**
- [x] Backtest-engine heeft generic evaluatie voor operator/value checks
- [x] Modules kunnen optioneel operator/value gebruiken via config (als operator/value aanwezig is, wordt generic evaluatie gebruikt)
- [x] Bestaande module-specifieke logica blijft werken (fallback mechanisme)
- [x] Generic evaluatie werkt met verschillende module types (RSI, MACD, SMA, etc.)

**Notities:**
- Implementatie gebruikt intelligente kolom detectie die werkt met verschillende naming patterns
- Voor modules zonder operator/value wordt automatisch de module's eigen check_entry_condition() gebruikt
- Generic evaluatie ondersteunt alle basis operators plus cross operators
- Kolom detectie werkt voor: RSI ('rsi'), MACD ('macd'), SMA ('sma_{period}'), en andere patterns

---

## Ticket 3: Template selector verwijderen of aanpassen
**Status:** ✅ Completed  
**Doel:** Template selector logica in strategy_builder.js aanpassen zodat deze niet interfereert met de normale flow, of verwijderen als niet nodig.

**Betrokken bestanden:**
- `static/js/strategy_builder.js` (regel 210-223: initializeBuilder functie)

**Uitgevoerd:**
- ✅ Automatische aanroep van `showTemplateSelector()` verwijderd uit `initializeBuilder()`
- ✅ Template selector functies behouden voor eventueel toekomstig gebruik (niet verwijderd, maar niet actief)
- ✅ Normale "Add Condition" flow werkt nu zonder interferentie
- ✅ Page load is schoon: toont direct de empty state met "Click Add Condition" message
- ✅ Gebruiker kan direct conditions toevoegen zonder extra stappen

**Acceptatiecriteria:**
- [x] Template selector wordt niet automatisch getoond bij page load
- [x] Normale "Add Condition" flow werkt zonder interferentie
- [x] Page load is schoon en direct bruikbaar

**Notities:**
- Template selector functies (`showTemplateSelector`, `selectTemplate`, `loadTemplateConditions`, etc.) blijven in de code voor eventueel toekomstig gebruik
- De automatische aanroep is verwijderd, waardoor de gebruiker direct kan beginnen met conditions toevoegen
- Empty state wordt nu correct getoond bij page load
- Template functionaliteit kan in de toekomst worden geactiveerd via URL parameter of button als gewenst

---

## Ticket 4: Foutafhandeling en validatie verbeteren
**Status:** Pending  
**Doel:** Betere error handling en input validatie toevoegen aan de Strategy Simulator V2 flow.

**Betrokken bestanden:**
- `static/js/strategy_builder.js` (handleFormSubmit, addCondition)
- `app.py` (run_backtest_v2 route)
- `templates/simulator_v2.html` (mogelijk error display toevoegen)

**Acceptatiecriteria:**
- [ ] Frontend valideert dat alle required fields ingevuld zijn
- [ ] Backend retourneert duidelijke error messages in JSON format
- [ ] Frontend toont errors gebruiksvriendelijk (niet alleen alert)
- [ ] Bij module errors wordt specifieke foutmelding getoond
- [ ] Geen crashes bij invalid input

---

## Ticket 5: Strategy preview real-time updaten
**Status:** Pending  
**Doel:** Strategy preview box real-time updaten wanneer gebruiker conditions toevoegt/verwijdert of settings wijzigt.

**Betrokken bestanden:**
- `static/js/strategy_builder.js` (updateStrategyPreview functie toevoegen)
- `templates/simulator_v2.html` (strategyPreview element)

**Acceptatiecriteria:**
- [ ] Preview toont duidelijk welke conditions zijn toegevoegd
- [ ] Preview toont symbol, timeframe, direction, period
- [ ] Preview toont TP/SL settings
- [ ] Preview update automatisch bij wijzigingen
- [ ] Preview is leesbaar en professioneel geformatteerd

