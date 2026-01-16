# Beta Test Checklist - 5 Personen
**Datum:** 2026-01-16  
**Doel:** Werkende beta voor 5 personen binnen 1-2 weken  
**Focus:** End-to-end flow werkt, heldere errors, geen crashes

> **Build Contract Alignment:** Beta moet "Time-to-value (<10 min)" en "Reliability (heldere errors)" demonstreren. Focus op "Heilig Pad": Template → Run → Analyse → PDF.

---

## ✅ Wat Al Werkt (85%)

- ✅ Templates getest en gevalideerd (9 templates, 63/63 modules)
- ✅ Backend conversion werkend
- ✅ Backtest execution werkend
- ✅ PDF generatie werkend
- ✅ Module registry systeem
- ✅ Caching mechanisme (in-memory)

---

## 🎯 Beta Vereisten (P0 - Must Have)

### 1. End-to-End Flow Testen
- [ ] **Template selector → Simulator v4** flow werkt
- [ ] **Template laden** werkt (alle 9 templates)
- [ ] **Parameters aanpassen** werkt (minimaal 2-3 templates testen)
- [ ] **Backtest runnen** werkt (geen crashes)
- [ ] **Resultaten bekijken** werkt (metrics + trades lijst)
- [ ] **PDF downloaden** werkt

**Acceptatie:** Gebruiker kan in <10 minuten van template selectie naar PDF zonder crashes.

---

### 2. Error Handling & Feedback
- [ ] **Geen "mysterieuze" 500 errors** - alle errors hebben code + message
- [ ] **Heldere foutmeldingen** bij:
  - Geen Decision Blocks geselecteerd
  - Geen sub-confirmations geselecteerd
  - Invalid parameters (out of range)
  - Geen trades gegenereerd (al aanwezig: `no_trades_error.html`)
- [ ] **Loading indicator** bij backtest (>3 seconden)
- [ ] **Progress feedback** tijdens lange operaties

**Acceptatie:** Gebruiker snapt altijd wat er mis ging en wat hij moet doen.

---

### 3. Basis Validatie & Limits
- [ ] **Hard limits enforced**:
  - Max 4 Decision Blocks (al geïmplementeerd ✅)
  - Max period (suggestie: 6mo voor beta)
  - Max modules per strategy (suggestie: 10)
- [ ] **Parameter validation**:
  - Min/max ranges (via schema - al geïmplementeerd ✅)
  - Required fields check
- [ ] **Rate limiting basics** (suggestie: 10 backtests per 10 minuten per IP)

**Acceptatie:** Systeem crasht niet bij edge cases en misbruik.

---

### 4. UX Basics
- [ ] **Template flow duidelijk** - gebruiker weet wat te doen
- [ ] **Parameters begrijpelijk** - labels en help text (al aanwezig via schema ✅)
- [ ] **Resultaten overzichtelijk** - metrics + trades + PDF
- [ ] **Mobile responsive** - basis bruikbaarheid op mobile (niet perfect)

**Acceptatie:** Gebruiker kan zonder instructies door flow navigeren.

---

### 5. Stability & Reliability
- [ ] **Geen crashes bij normale use** - 10+ backtests zonder crash
- [ ] **Cache werkt** - tweede run vanzelfde strategie is sneller
- [ ] **PDF altijd te genereren** - geen crashes tijdens PDF generation
- [ ] **Data download robuust** - Yahoo Finance failures worden afgehandeld

**Acceptatie:** Systeem is stabiel voor normale gebruik.

---

## 🔧 Technische Implementatie Items

### Prioriteit 1 (Deze Week - Beta Blocker)
1. **Error Contract Standardisatie**
   - Alle errors returnen: `{success: false, code: "...", error: "...", details: {...}}`
   - Frontend toont altijd code + message

2. **Loading Indicator**
   - Toon "Running backtest..." tijdens execution
   - Spinner/progress voor >3 seconden

3. **Hard Limits Enforcement**
   - Max period: 6mo (config)
   - Max modules: 10 (config)
   - Rate limiting: 10 req/10min (basic Flask-Limiter)

4. **End-to-End Test**
   - Test alle 9 templates in UI
   - Document issues gevonden
   - Fix critical blockers

---

### Prioriteit 2 (Nice to Have - Beta Polishing)
1. **Better Error Messages**
   - "No trades found" → suggesties voor oplossing
   - Parameter validation errors → duidelijk wat fout is

2. **Quick Test Mode UI**
   - Button: "Quick Test (30 days)" vs "Full Test (2 months)"
   - Duidelijk wat het verschil is

3. **Result Caching Feedback**
   - Toon "Using cached result" als applicable
   - Cache hit indicator

4. **Data Freshness UI**
   - "Data cached as of: [timestamp]"
   - Option to refresh

---

## 📋 Testing Checklist voor Beta

### Pre-Beta Testing (Interne Test)
- [ ] Test alle 9 templates end-to-end
- [ ] Test edge cases (geen blocks, geen confirmations, invalid params)
- [ ] Test rate limiting (10 req/10min)
- [ ] Test error handling (geen trades, Yahoo Finance failure)
- [ ] Test PDF generation (alle templates)
- [ ] Test op verschillende browsers (Chrome, Firefox, Safari)
- [ ] Test op mobile (basis bruikbaarheid)

### Beta User Scenarios (5 personen)
1. **Scenario 1: ICT Trader**
   - Template: ICT/SMC
   - Configuratie: Default + 1 parameter aangepast
   - Verwacht: PDF met results

2. **Scenario 2: Trend Trader**
   - Template: Trend Following
   - Configuratie: Default
   - Verwacht: PDF met results

3. **Scenario 3: Experimenter**
   - Template: RSI Bounce
   - Configuratie: Meerdere parameters aangepast
   - Verwacht: PDF met results

4. **Scenario 4: Edge Case Explorer**
   - Test: Geen Decision Blocks → verwacht heldere error
   - Test: Geen sub-confirmations → verwacht heldere error
   - Test: Invalid period → verwacht heldere error

5. **Scenario 5: Power User**
   - Test: Meerdere backtests achter elkaar
   - Test: Rate limiting (10 req/10min)
   - Test: PDF generation multiple times

---

## 🚨 Known Issues (Acceptable voor Beta)

### Minor Issues (OK voor Beta)
- ⚠️ Mobile responsive niet perfect (OK als basis bruikbaar)
- ⚠️ PDF generation 5-7 seconden (acceptabel met loading indicator)
- ⚠️ Geen regime labels (31-60 dagen feature)
- ⚠️ Geen saved strategies (31-60 dagen feature)
- ⚠️ Edge cases met "no module" concepts (werkaround OK)

### Blocker Issues (Moet gefixed zijn)
- ❌ Crashes bij normale use → **MOET FIXED**
- ❌ Mysterieuze 500 errors → **MOET FIXED**
- ❌ Geen loading indicator → **MOET FIXED** (of minstens "Please wait")
- ❌ Templates laden niet → **MOET FIXED**
- ❌ PDF generation crasht → **MOET FIXED**

---

## 📊 Beta Success Criteria

### Must Have (Beta gaat door)
- ✅ Alle 9 templates kunnen worden geladen
- ✅ Minimaal 3 templates kunnen worden gerund zonder crashes
- ✅ PDF kan worden gegenereerd voor alle templates
- ✅ Errors zijn helder en begrijpelijk
- ✅ Loading feedback tijdens backtest

### Nice to Have (Beta is beter)
- ✅ Quick Test mode beschikbaar
- ✅ Result caching zichtbaar
- ✅ Data freshness indicator
- ✅ Mobile responsive (basis)

---

## 🎯 Beta Launch Plan

### Week 1: Beta Blocker Fixes
**Maandag-Dinsdag:**
- Error contract standardisatie
- Loading indicator
- Hard limits enforcement

**Woensdag-Donderdag:**
- End-to-end testing alle templates
- Fix critical bugs gevonden
- Rate limiting implementatie

**Vrijdag:**
- Final testing
- Beta deployment prep

### Week 2: Beta Testing
**Maandag:**
- Beta launch voor 5 personen
- Collect feedback

**Rest van Week:**
- Fix critical bugs (als gevonden)
- Iterate op feedback
- Plan voor productie

---

## 🔍 Focus Gebieden (Volgens 30/60/90 Roadmap)

### 0-30 dagen items die relevant zijn voor Beta:
- ✅ Template flow: "Kies → Configureer → Run → Result" → **Testen in beta**
- ⚠️ Strategy fingerprint → **Nice to have**
- ✅ "Generate PDF" knop → **Al werkend**
- ✅ Eén error contract → **Implementeren**
- ✅ Hard limits → **Implementeren**
- ⚠️ Structured logging → **Nice to have**

### Items die NIET nodig zijn voor Beta:
- ❌ API versioning (kunnen later doen)
- ❌ Yahoo throttling advanced (basic OK)
- ❌ Data freshness UI (nice to have)
- ❌ Regime labels (31-60 dagen)
- ❌ Saved strategies (31-60 dagen)

---

## ✅ Definition of Done - Beta Ready

**Beta is ready wanneer:**
1. [ ] Alle P0 items zijn geïmplementeerd en getest
2. [ ] Geen blocker issues meer open
3. [ ] Minimaal 3 templates end-to-end getest
4. [ ] Error handling is consistent en helder
5. [ ] Loading indicators aanwezig
6. [ ] Hard limits geïmplementeerd
7. [ ] PDF generation werkt voor alle templates
8. [ ] Interne test door 1-2 personen succesvol

---

**Volgende Stappen:**
1. Prioriteit 1 items implementeren (deze week)
2. End-to-end testing (deze week)
3. Beta launch (volgende week)

**Gerelateerde documenten:**
- [30/60/90 Roadmap](30_60_90_ROADMAP.md) - Volledige roadmap
- [Build Contract](BUILD_CONTRACT.md) - Product focus
- [Architecture Guardrails](ARCHITECTURE_GUARDRAILS.md) - Technische guardrails
