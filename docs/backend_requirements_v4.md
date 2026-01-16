# Backend Requirements - Strategy Simulator V4 (Decision Block Model)

## Overzicht
Dit document beschrijft wat er backend-technisch nodig is om Strategy Simulator V4 volledig werkend te maken.

---

## 1. Decision Block Data Structure

### Frontend → Backend Data Format

```json
{
  "marketContext": {
    "market": "XAUUSD",
    "timeframe": "15m",
    "session": "London",
    "direction": "Long",
    "testPeriod": "2mo"
  },
  "decisionBlocks": [
    {
      "id": "block1",
      "title": "Market Bias",
      "explanation": "Defines higher-timeframe directional context.",
      "subConfirmations": [
        {
          "id": "conf1",
          "type": "checkbox",
          "label": "HTF market structure aligned",
          "selected": true,
          "config": {}
        },
        {
          "id": "conf2",
          "type": "checkbox",
          "label": "Premium / Discount zone respected",
          "selected": true,
          "config": {}
        },
        {
          "id": "conf3",
          "type": "dropdown",
          "label": "RSI Level",
          "selected": "Oversold",
          "config": {
            "options": ["Oversold", "Overbought", "Neutral"]
          }
        }
      ]
    }
  ],
  "exit": {
    "stopLoss": 1,
    "takeProfit": 2
  }
}
```

---

## 2. Backend Route: `/run-backtest-v4`

### Route Handler

```python
@app.route('/run-backtest-v4', methods=['POST'])
def run_backtest_v4():
    """V4: Decision Block Model backtest"""
    try:
        data = request.get_json()
        
        # Extract market context
        market_context = data.get('marketContext', {})
        symbol = market_context.get('market', 'XAUUSD')
        timeframe = market_context.get('timeframe', '15m')
        direction_raw = market_context.get('direction', 'Long')
        direction = 'LONG' if direction_raw.upper() in ['LONG', 'BOTH'] else 'SHORT'
        period = market_context.get('testPeriod', '2mo')
        session_raw = market_context.get('session', '').strip()
        session = session_raw if session_raw and session_raw != 'All' else None
        
        # Extract exit & risk
        exit_data = data.get('exit', {})
        tp_r = float(exit_data.get('takeProfit', 2.0))
        sl_r = float(exit_data.get('stopLoss', 1.0))
        
        # Extract Decision Blocks
        decision_blocks = data.get('decisionBlocks', [])
        
        if not decision_blocks:
            return {'success': False, 'error': 'No Decision Blocks specified'}, 400
        
        if len(decision_blocks) > 4:
            return {'success': False, 'error': 'Maximum 4 Decision Blocks allowed'}, 400
        
        # Convert Decision Blocks to backtest conditions
        conditions = convert_decision_blocks_to_conditions(decision_blocks)
        
        if not conditions:
            return {'success': False, 'error': 'No valid conditions generated from Decision Blocks'}, 400
        
        # Run backtest
        engine = BacktestEngine()
        trades = engine.run_modular(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            period=period,
            session=session,
            tp_r=tp_r,
            sl_r=sl_r,
            modules=conditions
        )
        
        # ... rest of backtest processing
        
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500
```

---

## 3. Decision Block → Condition Converter

### Functie: `convert_decision_blocks_to_conditions()`

**Doel:** Converteer Decision Blocks met sub-confirmaties naar backtest-engine compatible conditions.

**Logica:**

1. **Voor elke Decision Block:**
   - Alle sub-confirmaties moeten TRUE zijn (AND logica binnen block)
   - Als alle sub-confirmaties TRUE zijn → Decision Block = TRUE
   - Decision Blocks onderling: AND logica (alle blocks moeten TRUE zijn)

2. **Sub-confirmation Types:**

   **Checkbox:**
   - `selected: true` → condition is actief
   - `selected: false` → condition wordt genegeerd
   
   **Toggle:**
   - `selected: true` → condition is actief
   - `selected: false` → condition wordt genegeerd
   
   **Dropdown:**
   - `selected: "Oversold"` → specifieke waarde wordt gebruikt
   - Moet worden gemapped naar indicator configuratie

3. **Sub-confirmation Mapping:**

   Elke sub-confirmatie moet worden gemapped naar een indicator/module:
   
   ```python
   SUB_CONFIRMATION_MAPPING = {
       "HTF market structure aligned": {
           "module": "market_structure",
           "config": {"timeframe": "higher"},
           "operator": "==",
           "value": "aligned"
       },
       "RSI oversold": {
           "module": "rsi",
           "config": {"period": 14},
           "operator": "<",
           "value": 30
       },
       "Premium / Discount zone respected": {
           "module": "premium_discount",
           "config": {},
           "operator": "==",
           "value": "in_zone"
       },
       # ... meer mappings
   }
   ```

4. **Implementatie:**

   ```python
   def convert_decision_blocks_to_conditions(decision_blocks):
       """
       Convert Decision Blocks to backtest-engine compatible conditions.
       
       Returns list of module dictionaries for run_modular().
       """
       from core.strategy_modules.registry import get_registry
       registry = get_registry()
       conditions = []
       
       for block in decision_blocks:
           # Get all selected sub-confirmations
           selected_confirmations = [
               conf for conf in block.get('subConfirmations', [])
               if conf.get('selected', False)
           ]
           
           if not selected_confirmations:
               continue  # Skip blocks with no selected confirmations
           
           # Convert each sub-confirmation to a condition
           for conf in selected_confirmations:
               mapping = SUB_CONFIRMATION_MAPPING.get(conf['label'])
               if not mapping:
                   # Try to infer from label or use default
                   mapping = infer_mapping_from_label(conf)
               
               if mapping:
                   try:
                       module_class = registry.get_module(mapping['module'])
                       module_instance = module_class()
                       
                       conditions.append({
                           'module': module_instance,
                           'module_id': mapping['module'],
                           'config': mapping.get('config', {}),
                           'operator': mapping.get('operator'),
                           'value': mapping.get('value')
                       })
                   except Exception as e:
                       print(f"Error loading module {mapping['module']}: {e}")
                       continue
       
       return conditions
   ```

---

## 4. Sub-confirmation Mapping Database

### Vereiste Mappings

**Market Structure:**
- "HTF market structure aligned" → market_structure module
- "Lower-timeframe structure shift" → market_structure module (lower TF)
- "Structure break" → market_structure module

**Premium/Discount:**
- "Premium / Discount zone respected" → premium_discount module
- "Price extended from VWAP" → vwap module

**Liquidity:**
- "Liquidity sweep present" → liquidity_sweep module
- "Equal highs / lows taken" → equal_highs_lows module
- "Stop hunt or inducement" → stop_hunt module

**Momentum/RSI:**
- "RSI oversold / overbought" → rsi module
- "Momentum divergence" → momentum_divergence module
- "Momentum exhaustion" → momentum_exhaustion module

**Moving Averages:**
- "Fast MA crosses slow MA" → ma_crossover module
- "Moving average alignment" → ma_alignment module
- "Price above / below trend line" → supertrend module

**Volume/Volatility:**
- "Volume spike" → volume_spike module
- "Volatility expansion" → volatility_expansion module
- "ATR sufficient" → atr module

**Session/Timing:**
- "Session timing aligned" → session_filter module
- "Killzone / session" → killzone module
- "Active session" → session_filter module

**Price Action:**
- "Fair Value Gap entry" → fair_value_gap module
- "Displacement move" → displacement module
- "Rejection candle" → rejection_candle module
- "Wick rejection" → wick_rejection module

---

## 5. Nieuwe Modules die Mogelijk Nodig Zijn

### Modules die mogelijk moeten worden toegevoegd:

1. **market_structure** - HTF/LTF structure analysis
2. **premium_discount** - Premium/Discount zone detection
3. **liquidity_sweep** - Liquidity sweep detection
4. **equal_highs_lows** - Equal highs/lows detection
5. **stop_hunt** - Stop hunt pattern detection
6. **fair_value_gap** - Fair Value Gap detection
7. **displacement** - Displacement move detection
8. **momentum_divergence** - Momentum divergence detection
9. **momentum_exhaustion** - Momentum exhaustion detection
10. **ma_crossover** - Moving average crossover
11. **ma_alignment** - Moving average alignment
12. **supertrend** - Supertrend indicator
13. **volume_spike** - Volume spike detection
14. **volatility_expansion** - Volatility expansion detection
15. **session_filter** - Session-based filtering
16. **killzone** - Killzone timing
17. **rejection_candle** - Rejection candle pattern
18. **wick_rejection** - Wick rejection pattern
19. **vwap** - VWAP calculation and distance
20. **atr** - ATR calculation

---

## 6. Module Interface Requirements

### Elke Module Moet:

1. **check_entry_condition()** method hebben
2. **calculate()** method hebben voor indicator berekening
3. **Config parameters** accepteren
4. **Operator/value** ondersteuning hebben (indien van toepassing)

### Voorbeeld Module Structuur:

```python
class MarketStructureModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.name = "Market Structure"
        self.module_id = "market_structure"
    
    def calculate(self, data, config=None):
        """
        Calculate market structure.
        Config: {'timeframe': 'higher' | 'lower'}
        """
        # Implementation
        pass
    
    def check_entry_condition(self, data, index, config=None, operator=None, value=None):
        """
        Check if market structure is aligned.
        Operator: '==' | '!='
        Value: 'aligned' | 'not_aligned'
        """
        # Implementation
        pass
```

---

## 7. Backend Validatie

### Validatie Regels:

1. **Decision Blocks:**
   - Min 1 Decision Block
   - Max 4 Decision Blocks
   - Elke Decision Block moet min 1 sub-confirmatie hebben

2. **Sub-confirmaties:**
   - Min 1 geselecteerde sub-confirmatie per Decision Block
   - Alle sub-confirmaties moeten een mapping hebben

3. **Market Context:**
   - Alle required fields moeten aanwezig zijn
   - Timeframe moet geldig zijn
   - Period moet geldig zijn

4. **Exit:**
   - Stop loss en take profit moeten > 0 zijn
   - Take profit moet > stop loss zijn (logisch)

---

## 8. Error Handling

### Error Scenarios:

1. **Geen Decision Blocks:** Return 400 met duidelijke error
2. **Geen geselecteerde sub-confirmaties:** Return 400
3. **Onbekende sub-confirmatie:** Log warning, skip, of return error
4. **Module niet gevonden:** Return 404 met module naam
5. **Module error:** Return 400 met error details
6. **Geen trades gegenereerd:** Return 200 met message (niet error)

---

## 9. Testing Requirements

### Test Cases:

1. **Template Loading:**
   - Alle templates kunnen worden geladen
   - Decision Blocks worden correct geparsed
   - Sub-confirmaties worden correct geladen

2. **Decision Block Conversion:**
   - Single Decision Block → conditions
   - Multiple Decision Blocks → conditions (AND logica)
   - Sub-confirmaties → module configs

3. **Backtest Execution:**
   - Backtest werkt met Decision Blocks
   - Results zijn correct
   - Geen crashes bij invalid data

4. **Error Handling:**
   - Invalid Decision Blocks → error
   - Missing modules → error
   - Invalid market context → error

---

## 10. Performance Considerations

### Optimalisatie:

1. **Caching:**
   - Market data caching (al aanwezig)
   - Indicator calculations caching

2. **Batch Processing:**
   - Alle Decision Blocks in één backtest run
   - Geen meerdere runs nodig

3. **Module Loading:**
   - Lazy loading van modules
   - Module registry caching

---

## 11. Migration Path

### Van V3 naar V4:

1. **V3 Data Format:**
   - V3 gebruikt rules/logic
   - V4 gebruikt Decision Blocks
   - Migratie functie nodig (optioneel)

2. **Backward Compatibility:**
   - V3 route blijft werken
   - V4 route is nieuw
   - Geen breaking changes voor V3

---

## 12. Prioriteiten

### Phase 1 (MVP):
- Basis Decision Block converter
- Core mappings (RSI, MA, basic structure)
- Basis backtest functionaliteit

### Phase 2 (Full):
- Alle sub-confirmation mappings
- Alle nieuwe modules
- Volledige template support

### Phase 3 (Advanced):
- Performance optimalisatie
- Advanced error handling
- Analytics en logging

---

## 13. Documentatie Vereisten

### Te Documenteren:

1. **Sub-confirmation Mappings:**
   - Complete lijst van alle mappings
   - Config parameters per mapping
   - Operator/value options

2. **Module Development:**
   - Hoe nieuwe modules toe te voegen
   - Module interface requirements
   - Testing guidelines

3. **API Documentation:**
   - Request/response format
   - Error codes
   - Examples

---

## Conclusie

De backend moet:
1. Decision Blocks ontvangen en valideren
2. Decision Blocks converteren naar backtest conditions
3. Sub-confirmaties mappen naar modules/indicators
4. Backtest uitvoeren met gegenereerde conditions
5. Results retourneren

**Kritieke Dependencies:**
- Alle sub-confirmation mappings moeten worden gedefinieerd
- Nieuwe modules moeten worden geïmplementeerd (indien nodig)
- Module registry moet alle modules bevatten
- Backtest engine moet Decision Block format ondersteunen



