# V4 Simplified Approach - Performance Fix

## Probleem
De originele V4 implementatie had:
- **Complexe `safe_to_datetime` functie** (200+ regels) die bij elke aanroep veel werk deed
- **Monkey-patching** van `pd.to_datetime` - error-prone en moeilijk te debuggen
- **Herhaalde duplicate checks** voor elke module
- **12+ minuten** backtest tijd - veel te lang

## Nieuwe Aanpak

### 1. Data Cleaning - EEN KEER aan het begin
```python
def clean_and_standardize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize DataFrame ONCE at the start.
    - Remove duplicate rows
    - Ensure clean DatetimeIndex (no duplicates)
    - Standardize timestamp column
    - Sort by index
    """
```

**Voordelen:**
- Data wordt EEN KEER schoongemaakt, niet herhaaldelijk
- Alle modules krijgen schone, consistente data
- Geen complexe duplicate handling tijdens module execution

### 2. Geen Monkey-Patching
- **Verwijderd:** Complexe `safe_to_datetime` wrapper
- **Verwijderd:** Monkey-patching van `pd.to_datetime`
- **Gebruikt:** Normale `pd.to_datetime` - sneller en betrouwbaarder

### 3. Eenvoudige Error Handling
- Als een module een duplicate error geeft → clean data en retry EEN KEER
- Geen complexe retry logica
- Duidelijke error messages

### 4. Module Interface Standaardisatie
- Alle modules krijgen **schone data** met:
  - Clean DatetimeIndex
  - Geen duplicate rows
  - Gestandaardiseerde timestamp column
- Modules hoeven zelf geen duplicate handling te doen

### 5. Trade Simulation
- Gebruikt `module.check_entry_condition()` method
- Eenvoudige TP/SL logica
- Geen complexe condition parsing

## Performance Verbeteringen

**Voor:**
- 12+ minuten per backtest
- Complexe duplicate handling bij elke module
- Herhaalde data cleaning

**Na:**
- Data cleaning: EEN KEER aan het begin (~1-2 seconden)
- Module execution: Direct, zonder extra checks
- Verwacht: **2-5 minuten** per backtest (afhankelijk van aantal modules)

## Code Structuur

```
run_modular():
  1. Download data (met caching)
  2. clean_and_standardize_data() - EEN KEER
  3. Voor elke module:
     - Calculate indicator
     - Check voor duplicate columns (rename indien nodig)
     - Quick check: als index duplicates heeft → clean
  4. Forward fill indicators
  5. Drop NaN rows
  6. Simulate trades met module.check_entry_condition()
```

## Belangrijke Wijzigingen

1. **Verwijderd:**
   - `safe_to_datetime()` functie (200+ regels)
   - Monkey-patching logica
   - Herhaalde duplicate removal in loops
   - Complexe error handling

2. **Toegevoegd:**
   - `clean_and_standardize_data()` - eenvoudige, snelle data cleaning
   - Performance timing logs
   - Eenvoudige retry logica (1x)

3. **Behouden:**
   - Module caching via DataManager
   - Column renaming voor duplicates
   - Forward fill voor indicators
   - TP/SL trade simulation

## Testen

Test de nieuwe aanpak met:
1. Eenvoudige strategie (1-2 modules)
2. Complexe strategie (5-7 modules)
3. ICT strategie (veel modules)

**Verwachte resultaten:**
- Backtest tijd: 2-5 minuten (was 12+ minuten)
- Geen "duplicate keys" errors
- Geen "length mismatch" errors
- Correcte trade generatie

## Volgende Stappen

1. ✅ Data cleaning functie geïmplementeerd
2. ✅ Monkey-patching verwijderd
3. ✅ Eenvoudige error handling
4. ⏳ Testen met verschillende strategieën
5. ⏳ Performance metingen
6. ⏳ Module caching optimalisatie (optioneel)

