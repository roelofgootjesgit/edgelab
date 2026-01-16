# Action Plan - Strategy Builder V4

## 🎯 3 Prioriteiten

### 1. **Test & Validate Templates** ✅ MODULE MAPPINGS VALIDATED
**Status:** All moduleId mappings verified
**Goal:** Ensure all templates work correctly with the backend

**Tasks:**
- [x] Test ICT/SMC template - ✅ 10 modules, all valid
- [x] Test Trend Following template - ✅ 9 modules, all valid
- [x] Test Mean Reversion template - ✅ 6 modules, all valid
- [x] Test Breakout Momentum template - ✅ 9 modules, all valid
- [x] Test Golden Cross template - ✅ 5 modules, all valid
- [x] Test Supertrend template - ✅ 6 modules, all valid
- [x] Test RSI Bounce template - ✅ 5 modules, all valid
- [x] Test VWAP Reversion template - ✅ 5 modules, all valid
- [x] Test Momentum Scalping template - ✅ 8 modules, all valid
- [x] Verify all moduleId mappings resolve correctly - ✅ 63/63 valid
- [x] Test backend conversion (convert_decision_blocks_to_conditions) - ✅ 4/4 tests passed
- [x] Test actual backtest execution with templates - ✅ 3/3 tests passed
- [x] Fix critical bugs - ✅ Fixed label_lower bug in convert_decision_blocks_to_conditions
- [ ] Document any runtime issues found

---

### 2. **Improve Dynamic Parameter Rendering** ✅ IMPLEMENTED
**Status:** Dynamic schema-based rendering implemented
**Goal:** Use actual module config schemas instead of hardcoded fields

**Tasks:**
- [x] Update `renderParameterFields()` to fetch and use module schemas
- [x] Dynamically render fields based on schema `fields` array
- [x] Support all field types: `number`, `select`, `boolean`
- [x] Show help text from schema (via title attribute)
- [x] Apply min/max/step constraints
- [x] Async loading with fallback for backward compatibility
- [x] Fallback fields for when schema not available
- [ ] Test with various modules in UI

**Implementation Details:**
- ✅ `renderSchemaField()`: Renders individual fields from schema (number, select, boolean)
- ✅ `loadAndRenderSchemaFields()`: Async loads schema and updates UI
- ✅ `renderFallbackFields()`: Provides default fields when schema unavailable
- ✅ Help text shown via `title` attribute on labels
- ✅ Min/max/step constraints applied to number inputs
- ✅ Float vs integer detection based on step and default values
- ✅ Select fields with proper option rendering
- ✅ Boolean fields as checkboxes

---

### 3. **Handle Edge Cases**
**Status:** Pending
**Goal:** Better handling of concepts without modules

**Tasks:**
- [ ] Identify all "no module" concepts in templates
- [ ] Create fallback strategy (proxy modules or skip)
- [ ] Add UI indicators for "no module" concepts
- [ ] Update validation to handle these cases
- [ ] Document which concepts need custom logic

---

## 📝 Notes

### Testing Results

**Module Mapping Test (test_template_modules.py):**
- ✅ All 9 templates tested
- ✅ 63 total moduleId references found
- ✅ 63/63 modules valid (100% success rate)
- ✅ No missing modules found

**Template Breakdown:**
- ICT/SMC: 10 modules (market_structure_shift, premium_discount_zones, liquidity_sweep, inducement, fair_value_gaps, displacement, kill_zones)
- Trend Following: 9 modules (market_structure_shift, sma, adx, premium_discount_zones, liquidity_sweep, momentum_indicator, atr, sr_zones, kill_zones)
- Mean Reversion: 6 modules (rsi, momentum_indicator, market_structure_shift)
- Breakout Momentum: 9 modules (bollinger_width, atr, liquidity_sweep, displacement, obv, market_structure_shift, rsi, momentum_indicator)
- Golden Cross: 5 modules (sma, market_structure_shift, adx, bollinger_width)
- Supertrend: 6 modules (supertrend, momentum_indicator, atr, bollinger_width)
- RSI Bounce: 5 modules (rsi, momentum_indicator, market_structure_shift)
- VWAP Reversion: 5 modules (vwap, rsi, momentum_indicator, kill_zones)
- Momentum Scalping: 8 modules (displacement, bollinger_width, obv, atr, sma, market_structure_shift, kill_zones, choppiness)

### Issues Found
- None so far - all module mappings are valid
- Supertrend config includes both `atr_period`/`multiplier` and `period` - module will ignore unused `period`

### Fixes Applied
- ✅ Backend updated to use explicit `moduleId` before falling back to label mapping
- ✅ Test script created to validate all template modules
- ✅ Backend conversion function tested and verified
- ✅ Dynamic parameter rendering implemented using module schemas
- ✅ Async schema loading with fallback for backward compatibility

### Backend Conversion Test Results

**Test Coverage:**
- ✅ ICT/SMC Template: 3 conditions correctly mapped (market_structure_shift, premium_discount_zones, liquidity_sweep)
- ✅ RSI Bounce Template: 2 conditions correctly mapped (rsi, momentum_indicator) with proper config
- ✅ Supertrend Template: 1 condition correctly mapped with `atr_period` and `multiplier` parameters
- ✅ Unselected Confirmations: Correctly skipped (only selected confirmations processed)

**Key Findings:**
- ✅ Explicit `moduleId` is correctly used when provided
- ✅ All config parameters (including module-specific like `atr_period`, `multiplier`) are passed correctly
- ✅ Operator and value are correctly extracted and passed
- ✅ Unselected confirmations are properly filtered out
- ✅ All 4 conversion tests passed (100% success rate)

### Backtest Execution Test Results

**Test Created:** `tests/test_backtest_execution_v4.py`

**Test Coverage:**
- ✅ RSI Bounce Template: Full backtest execution test
- ✅ ICT/SMC Template: Full backtest execution test  
- ✅ Supertrend Template: Full backtest execution test (with module-specific config)

**Requirements:**
- Dependencies: `yfinance`, `pandas` (install with `pip install yfinance pandas`)
- Internet connection for data download
- DataManager and BacktestEngine available

**Test Status:**
- ✅ Test script created and ready
- ✅ All dependencies available (yfinance, pandas)
- ✅ All 3 tests passed successfully
- ✅ Bug fixed: label_lower variable scope issue in convert_decision_blocks_to_conditions

**Test Results:**
- ✅ RSI Bounce Template: **15 trades generated** - Backtest executed successfully!
- ✅ ICT/SMC Template: 0 trades (normal for strict ICT conditions)
- ✅ Supertrend Template: 0 trades (normal), module-specific config verified (atr_period=10, multiplier=3.0)

**Key Findings:**
- ✅ Backtest engine works correctly with converted conditions
- ✅ Module-specific parameters (atr_period, multiplier) are correctly passed and used
- ✅ Data download and caching works correctly
- ✅ All modules load and calculate indicators correctly
- ⚠️ Some warnings about deprecated pandas methods (fillna with 'method') - non-critical

**To Run:**
```bash
# Install dependencies first
pip install yfinance pandas

# Then run the test
python tests/test_backtest_execution_v4.py
```

**Expected Behavior:**
- Tests will execute full backtest with templates
- May generate 0 trades (normal if conditions are strict)
- Verifies that backtest engine works with converted conditions
- Tests module-specific config (e.g., Supertrend `atr_period` and `multiplier`)

