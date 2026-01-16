# Next Steps - Strategy Builder V4

## ✅ Completed
1. ✅ Module inventory (66 modules documented)
2. ✅ Concept-to-module mapping guide
3. ✅ All templates updated with explicit `moduleId` fields
4. ✅ Validation system for missing module mappings
5. ✅ Dynamic parameter fields per module type

---

## 🎯 Recommended Next Steps

### 1. **Test & Validate Templates** (Priority: HIGH)
**Goal:** Ensure all templates work correctly with the backend

**Tasks:**
- [ ] Test each template with a simple backtest
- [ ] Verify all `moduleId` mappings resolve correctly
- [ ] Check that parameter values are passed correctly to modules
- [ ] Validate that backtests generate trades (or fail gracefully)

**How to test:**
1. Load each template in the UI
2. Run a backtest with default settings
3. Check console for errors
4. Verify trades are generated (or appropriate error messages)

**Expected issues:**
- Some modules might need different parameter names
- Some concepts might not work as expected (e.g., "HTF alignment" without MTF support)
- Price action patterns might need fallback logic

---

### 2. **Improve Dynamic Parameter Rendering** (Priority: MEDIUM)
**Goal:** Use actual module config schemas instead of hardcoded fields

**Current state:**
- We have hardcoded parameter fields per module type
- We fetch schemas but don't use them yet

**Tasks:**
- [ ] Update `renderParameterFields()` to use `getModuleConfigSchema()`
- [ ] Dynamically render fields based on schema `fields` array
- [ ] Support all field types: `number`, `select`, `boolean`
- [ ] Show help text from schema
- [ ] Apply min/max/step constraints

**Benefits:**
- Automatically supports new modules without code changes
- Shows correct field names and defaults
- Better UX with help text

---

### 3. **Handle Edge Cases** (Priority: MEDIUM)
**Goal:** Better handling of concepts without modules

**Current issues:**
- Price action patterns (rejection candles, wick rejection) have no modules
- Multi-timeframe concepts (HTF alignment) have no MTF module
- External data (news events) not available

**Tasks:**
- [ ] Create "Price Action" proxy module that uses RSI/Stochastic as fallback
- [ ] Document which concepts need custom logic vs. modules
- [ ] Add UI indicators for "no module" concepts (gray out, show tooltip)
- [ ] Consider creating placeholder modules for common patterns

**Alternative:**
- Mark these as "informational only" in templates
- Don't include them in backtest conditions
- Show warning in UI

---

### 4. **Enhance Validation** (Priority: LOW)
**Goal:** More comprehensive validation and user feedback

**Tasks:**
- [ ] Validate parameter values (min/max ranges)
- [ ] Check for required parameters
- [ ] Warn about incompatible module combinations
- [ ] Suggest alternatives for missing modules
- [ ] Show validation status per Decision Block

**Example validations:**
- RSI period must be between 2-200
- Supertrend multiplier must be between 1.0-10.0
- MACD requires fast_period < slow_period

---

### 5. **Documentation & Examples** (Priority: LOW)
**Goal:** Help users understand how to use the system

**Tasks:**
- [ ] Create "Quick Start" guide
- [ ] Add examples for each template
- [ ] Document common patterns and best practices
- [ ] Create troubleshooting guide

---

## 🔧 Technical Improvements

### A. Backend Configuration Handling
**Current:** Backend passes all config parameters to modules
**Potential issue:** Some modules might not handle all parameters correctly

**Tasks:**
- [ ] Test each module with various parameter combinations
- [ ] Ensure default values are applied correctly
- [ ] Handle missing parameters gracefully

### B. Module Schema Consistency
**Current:** Some modules use `fields` array, some use `properties` object
**Issue:** `momentum_indicator` uses different schema format

**Tasks:**
- [ ] Standardize all modules to use `fields` array format
- [ ] Update `momentum_indicator` and any others
- [ ] Ensure schema validation works for all formats

### C. Error Handling
**Current:** Basic error handling in place
**Improvements:**
- [ ] Better error messages for module loading failures
- [ ] Graceful degradation when modules fail
- [ ] User-friendly error messages in UI

---

## 🚀 Future Enhancements

### 1. Multi-Timeframe Support
- Create MTF module category
- Support HTF/LTF analysis
- Allow HTF bias + LTF entry combinations

### 2. Price Action Module
- Create dedicated price action pattern detector
- Support rejection candles, pin bars, engulfing patterns
- Integrate with existing modules

### 3. Template Builder
- Allow users to create custom templates
- Save templates to database
- Share templates with community

### 4. Advanced Validation
- Real-time parameter validation
- Strategy complexity scoring
- Performance prediction

---

## 📋 Immediate Action Items

**This Week:**
1. ✅ Test all 9 templates with simple backtests
2. ✅ Fix any module mapping issues found
3. ✅ Verify parameter passing works correctly

**Next Week:**
1. Improve dynamic parameter rendering
2. Handle edge cases better
3. Add more validation

**This Month:**
1. Complete documentation
2. Create examples
3. Consider price action module

---

## 🐛 Known Issues

1. **"No major news"** - No module available, marked as informational
2. **HTF/LTF concepts** - No MTF module yet, using MSS as proxy
3. **Price action patterns** - Using RSI/Stochastic as fallback
4. **Some parameter names** - May need adjustment based on actual module schemas

---

## 💡 Recommendations

**Priority Order:**
1. **Test everything first** - Find issues before improving
2. **Fix critical bugs** - Ensure basic functionality works
3. **Improve UX** - Better parameter rendering, validation
4. **Add features** - Price action, MTF support

**Quick Wins:**
- Test templates (30 min)
- Fix obvious mapping issues (1 hour)
- Improve validation messages (1 hour)

**Bigger Projects:**
- Dynamic parameter rendering (4-6 hours)
- Price action module (1-2 days)
- MTF support (2-3 days)



