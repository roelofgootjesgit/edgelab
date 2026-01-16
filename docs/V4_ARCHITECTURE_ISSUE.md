# V4 Architecture Probleem

## Het Probleem

**Huidige aanpak:**
1. 7 modules laden en indicators berekenen (OK, ~30 seconden)
2. Voor elke row (3600 rows) → check ALLE 7 modules
3. **25,200 function calls** (`check_entry_condition()`)
4. Elke call doet `data.iloc[index]` of `data.loc[index]`
5. Sommige modules doen ook lookback (`data.loc[index - 1]`)

**Resultaat:** 12+ minuten per backtest

## Waarom dit niet werkt

1. **Inefficiënt**: We checken per row, terwijl we al alle data hebben
2. **Herhaald werk**: Elke module wordt 3600x gecheckt
3. **Geen vectorization**: Pandas is gemaakt voor vectorized operations, niet row-by-row

## Betere Aanpak - Opties

### Optie 1: Vectorized Conditions (Aanbevolen)
**Pre-compute alle conditions als boolean columns:**

```python
# In plaats van per row checken:
for i in range(len(data)):
    if module.check_entry_condition(data, i, config, direction):
        ...

# Doen we:
data['rsi_condition'] = (data['rsi'] < 30) & (data['rsi'].shift(1) >= 30)
data['kill_zone_condition'] = data['in_kill_zone'] == True
# etc.

# Dan checken we:
entry_signal = data['rsi_condition'] & data['kill_zone_condition'] & ...
```

**Voordelen:**
- Pandas vectorized operations (100x sneller)
- Eén keer berekenen, niet 3600x
- Duidelijke boolean logic

**Nadelen:**
- Modules moeten aangepast worden om vectorized checks te ondersteunen
- Of: wrapper functie die `check_entry_condition` vectorized maakt

### Optie 2: Condition Caching
**Cache results per module:**

```python
# Pre-compute alle conditions voor alle modules
module_results = {}
for module_item in modules:
    module_id = module_item['module_id']
    results = []
    for i in range(len(data)):
        results.append(module.check_entry_condition(data, i, config, direction))
    module_results[module_id] = pd.Series(results, index=data.index)
```

**Voordelen:**
- Geen code changes in modules nodig
- Eén keer berekenen, daarna alleen boolean AND

**Nadelen:**
- Nog steeds 25,200 calls, maar dan upfront
- Memory overhead

### Optie 3: Lazy Evaluation
**Check alleen wanneer nodig:**

```python
# Check modules in volgorde van "lightweight" naar "heavyweight"
# Als eerste module False is, skip de rest
for i in range(len(data)):
    entry_signal = True
    for module_item in sorted_modules:  # Sorted by complexity
        if not module.check_entry_condition(data, i, config, direction):
            entry_signal = False
            break  # Early exit
```

**Voordelen:**
- Eenvoudig te implementeren
- Soms sneller (early exit)

**Nadelen:**
- Nog steeds row-by-row
- Niet fundamenteel sneller

### Optie 4: Fundamentaal Andere Architectuur
**Decision Blocks → Pre-computed Signals**

In plaats van modules per row te checken:
1. Bereken alle indicators (zoals nu)
2. Converteer Decision Blocks naar **boolean expressions**
3. Evalueer expressions vectorized op hele dataframe
4. Trades = waar alle conditions True zijn

**Voorbeeld:**
```
Decision Block 1: RSI < 30 AND Kill Zone active
Decision Block 2: Market Structure == Bullish

→ 
signal = (data['rsi'] < 30) & (data['in_kill_zone']) & (data['mss_direction'] == 'bullish')
trades = data[signal]
```

**Voordelen:**
- Volledig vectorized
- Zeer snel
- Duidelijke logica

**Nadelen:**
- Grote refactor nodig
- Decision Blocks moeten naar boolean expressions

## Aanbeveling

**Korte termijn:** Optie 1 (Vectorized Conditions)
- Wrapper functie die `check_entry_condition` vectorized maakt
- Pre-compute alle conditions
- Boolean AND op hele dataframe

**Lange termijn:** Optie 4 (Nieuwe Architectuur)
- Decision Blocks → Boolean Expressions
- Volledig vectorized backtesting
- 100x sneller

## Implementatie Plan

1. **Vectorized wrapper voor `check_entry_condition`:**
   ```python
   def vectorized_check(module, data, config, direction):
       # Voor simpele checks (kill_zones, etc.)
       if hasattr(module, 'get_condition_column'):
           return data[module.get_condition_column()]
       
       # Voor complexe checks (RSI cross, etc.)
       # Pre-compute voor alle rows
       results = []
       for i in range(len(data)):
           results.append(module.check_entry_condition(data, i, config, direction))
       return pd.Series(results, index=data.index)
   ```

2. **Pre-compute alle conditions:**
   ```python
   condition_series = {}
   for module_item in modules:
       module_id = module_item['module_id']
       condition_series[module_id] = vectorized_check(
           module_item['module'], 
           data, 
           module_item['config'], 
           direction
       )
   ```

3. **Combine conditions:**
   ```python
   # All conditions must be True (AND logic)
   entry_signal = pd.Series(True, index=data.index)
   for module_id, series in condition_series.items():
       entry_signal = entry_signal & series
   ```

4. **Find entry points:**
   ```python
   entry_indices = entry_signal[entry_signal].index
   ```

Dit zou de backtest tijd moeten reduceren van 12+ minuten naar **30-60 seconden**.

