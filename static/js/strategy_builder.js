/**
 * strategy_builder.js
 * QuantMetrics Strategy Builder v2 - Modular System
 * 
 * Features:
 * - Double dropdown (Category → Indicator)
 * - Dynamic module loading from backend
 * - Multi-condition support
 * - Real-time validation
 * 
 * Version: 2.0 - UX Improvements
 */

// ============================================================================
// GLOBAL STATE
// ============================================================================

let availableModules = {};      // All modules grouped by category
let categoryMetadata = {};      // Category icons, labels, descriptions
let conditionCount = 0;         // Counter for unique condition IDs
let conditions = [];            // Array of all conditions

// ============================================================================
// STRATEGY TEMPLATES
// ============================================================================

const STRATEGY_TEMPLATES = {
  scratch: {
    id: 'scratch',
    name: 'Start from Scratch',
    icon: '✨',
    description: 'Build your own custom strategy',
    color: '#3b82f6',  // Blue
    conditions: []
  },
  
  ict_smc: {
    id: 'ict_smc',
    name: 'ICT/SMC Setup',
    icon: '🎯',
    description: 'Smart Money Concepts trading',
    color: '#2563eb',  // Darker blue
    conditions: [
      {
        category: 'custom',
        module: 'fair_value_gap',
        operator: '==',
        value: '1',
        logic: 'AND'
      },
      {
        category: 'custom',
        module: 'order_block',
        operator: '==',
        value: '1',
        logic: 'AND'
      },
      {
        category: 'custom',
        module: 'liquidity_sweep',
        operator: '==',
        value: '1',
        logic: 'AND'
      }
    ],
    settings: {
      session: 'London'
    }
  },
  
  trend_following: {
    id: 'trend_following',
    name: 'Trend Following',
    icon: '📊',
    description: 'Ride market momentum',
    color: '#1d4ed8',  // Medium blue
    conditions: [
      {
        category: 'trend',
        module: 'adx',
        operator: '>',
        value: '25',
        logic: 'AND'
      },
      {
        category: 'moving_averages',
        module: 'ema',
        operator: 'crosses_above',
        value: '0',
        logic: 'AND',
        note: 'EMA(20) crosses above EMA(50)'
      },
      {
        category: 'volume',
        module: 'volume_sma',
        operator: '>',
        value: '1',
        logic: 'AND'
      }
    ]
  },
  
  mean_reversion: {
    id: 'mean_reversion',
    name: 'Mean Reversion',
    icon: '↔️',
    description: 'Buy oversold, sell overbought',
    color: '#60a5fa',  // Light blue
    conditions: [
      {
        category: 'momentum',
        module: 'rsi',
        operator: '<',
        value: '30',
        logic: 'OR'
      },
      {
        category: 'volatility',
        module: 'bollinger_bands',
        operator: '<',
        value: '0',
        logic: 'AND',
        note: 'Price touches lower band'
      }
    ]
  },
  
  breakout_momentum: {
    id: 'breakout_momentum',
    name: 'Breakout Momentum',
    icon: '⚡',
    description: 'Catch strong moves early',
    color: '#1e40af',  // Deep blue
    conditions: [
      {
        category: 'momentum',
        module: 'macd',
        operator: 'crosses_above',
        value: '0',
        logic: 'AND'
      },
      {
        category: 'volume',
        module: 'volume_sma',
        operator: '>',
        value: '1.5',
        logic: 'AND',
        note: 'Volume 50% above average'
      },
      {
        category: 'volatility',
        module: 'atr',
        operator: '>',
        value: '0',
        logic: 'AND',
        note: 'Volatility expansion'
      }
    ]
  },
  
  custom_templates: {
    id: 'custom_templates',
    name: 'My Templates',
    icon: '💾',
    description: 'Your saved strategies',
    color: '#93c5fd',  // Very light blue
    conditions: [],
    isCustom: true,
    comingSoon: true
  }
};

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Load available modules from backend API
 * Called on page load
 */
async function loadAvailableModules() {
  try {
    console.log('[INIT] Loading modules from API...');
    
    const response = await fetch('/api/modules');
    const data = await response.json();
    
    if (data.success) {
      availableModules = data.modules;
      categoryMetadata = data.categories || {};
      
      console.log('[INIT] ✓ Loaded modules:', Object.keys(availableModules));
      console.log('[INIT] ✓ Categories:', Object.keys(categoryMetadata));
      
      return true;
    } else {
      console.error('[INIT] ✗ API returned error:', data.error);
      return false;
    }
  } catch (error) {
    console.error('[INIT] ✗ Failed to fetch modules:', error);
    return false;
  }
}

/**
 * Initialize the strategy builder
 * Called after modules are loaded
 */
function initializeBuilder() {
  console.log('[INIT] Initializing strategy builder...');
  
  // Show template selector first
  showTemplateSelector();
  
  // Set up event listeners
  setupEventListeners();
  
  // Initial state
  updateAddConditionButton();
  
  console.log('[INIT] ✓ Strategy builder ready');
}

/**
 * Show strategy template selector
 */
function showTemplateSelector() {
  const container = document.getElementById('conditionsContainer');
  if (!container) return;
  
  const templates = Object.values(STRATEGY_TEMPLATES);
  
  const selectorHTML = `
    <div class="template-selector">
      <div style="text-align: center; margin-bottom: 3rem;">
        <h2 style="font-size: 2rem; color: var(--text-primary); margin-bottom: 1rem;">
          🎯 Build Your Trading Strategy
        </h2>
        <p style="color: var(--text-muted); font-size: 1.1rem;">
          Choose a starting point or build from scratch
        </p>
      </div>
      
      <div class="template-grid">
        ${templates.map(template => `
          <div class="template-card" 
               data-template-id="${template.id}"
               onclick="selectTemplate('${template.id}')"
               style="border-top: 4px solid ${template.color}; cursor: pointer;">
            <div class="template-icon" style="font-size: 3rem; margin-bottom: 1rem;">
              ${template.icon}
            </div>
            <h3 class="template-name" style="font-size: 1.25rem; color: var(--text-primary); margin-bottom: 0.5rem;">
              ${template.name}
            </h3>
            <p class="template-description" style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1rem;">
              ${template.description}
            </p>
            ${template.conditions.length > 0 ? `
              <div class="template-conditions" style="font-size: 0.75rem; color: ${template.color}; font-weight: 600;">
                ${template.conditions.length} conditions included
              </div>
            ` : ''}
            ${template.comingSoon ? `
              <div style="background: rgba(59, 130, 246, 0.1); color: var(--accent-blue); padding: 0.5rem; border-radius: 8px; font-size: 0.75rem; font-weight: 600;">
                Coming Soon
              </div>
            ` : ''}
          </div>
        `).join('')}
      </div>
    </div>
  `;
  
  container.innerHTML = selectorHTML;
  
  // Hide empty state
  const emptyState = document.getElementById('empty-state');
  if (emptyState) {
    emptyState.style.display = 'none';
  }
  
  console.log('[UI] ✓ Template selector displayed');
}

/**
 * Select a strategy template
 */
function selectTemplate(templateId) {
  console.log('[TEMPLATE] Selected:', templateId);
  
  const template = STRATEGY_TEMPLATES[templateId];
  
  if (!template) {
    console.error('[TEMPLATE] Template not found:', templateId);
    return;
  }
  
  // Coming soon templates
  if (template.comingSoon) {
    alert('This feature is coming soon! For now, you can start from scratch or use another template.');
    return;
  }
  
  // Clear template selector
  const container = document.getElementById('conditionsContainer');
  if (container) {
    container.innerHTML = '';
  }
  
  // Start from scratch - show empty form
  if (template.id === 'scratch') {
    // Just clear and user can add conditions manually
    updateAddConditionButton();
    return;
  }
  
  // Load template conditions
  loadTemplateConditions(template);
}

/**
 * Load template conditions into strategy
 */
function loadTemplateConditions(template) {
  console.log('[TEMPLATE] Loading conditions for:', template.name);
  
  // Apply template settings
  if (template.settings) {
    if (template.settings.session) {
      const sessionSelect = document.getElementById('session');
      if (sessionSelect) {
        sessionSelect.value = template.settings.session;
      }
    }
  }
  
  // Load each condition with delay for visual effect
  template.conditions.forEach((conditionConfig, index) => {
    setTimeout(() => {
      addTemplateCondition(conditionConfig);
    }, index * 300); // 300ms delay between each
  });
  
  // Update UI
  updateAddConditionButton();
  
  console.log('[TEMPLATE] ✓ Loaded', template.conditions.length, 'conditions');
}

/**
 * Add a condition from template
 */
function addTemplateCondition(conditionConfig) {
  // Find module by ID
  const category = conditionConfig.category;
  const moduleId = conditionConfig.module;
  
  if (!availableModules[category]) {
    console.warn('[TEMPLATE] Category not found:', category);
    return;
  }
  
  const moduleData = availableModules[category].find(m => m.id === moduleId);
  
  if (!moduleData) {
    console.warn('[TEMPLATE] Module not found:', moduleId);
    return;
  }
  
  // Create condition
  const condition = {
    id: conditionCount++,
    category: category,
    module: moduleId,
    moduleName: moduleData.name,
    operator: conditionConfig.operator,
    value: conditionConfig.value,
    logic: conditionConfig.logic || 'AND',
    config: {},
    note: conditionConfig.note
  };
  
  // Add to conditions array
  conditions.push(condition);
  
  // Render condition card
  renderConditionCard(condition);
  
  // Update UI
  updateSubmitButton();
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
  // Add condition button
  const addBtn = document.getElementById('add-condition');
  if (addBtn) {
    addBtn.addEventListener('click', showAddConditionForm);
    console.log('[INIT] ✓ Add condition button listener attached');
  } else {
    console.error('[INIT] ✗ Could not find add-condition button');
  }
  
  // Form submission
  const form = document.getElementById('strategyForm');
  if (form) {
    form.addEventListener('submit', handleFormSubmit);
  }
}

// ============================================================================
// DOUBLE DROPDOWN LOGIC
// ============================================================================

/**
 * Populate category dropdown with icons and labels
 */
function populateCategoryDropdown(selectElement) {
  // Clear existing options
  selectElement.innerHTML = '<option value="">Select Category...</option>';
  
  // Add category options
  for (const [categoryId, metadata] of Object.entries(categoryMetadata)) {
    if (availableModules[categoryId] && availableModules[categoryId].length > 0) {
      const option = document.createElement('option');
      option.value = categoryId;
      option.textContent = `${metadata.icon} ${metadata.label}`;
      selectElement.appendChild(option);
    }
  }
}

/**
 * Populate indicator dropdown based on selected category
 */
function populateIndicatorDropdown(selectElement, category) {
  // Clear existing options
  selectElement.innerHTML = '<option value="">Select Indicator...</option>';
  
  if (!category || !availableModules[category]) {
    selectElement.disabled = true;
    return;
  }
  
  // Enable and populate
  selectElement.disabled = false;
  
  const modules = availableModules[category];
  modules.forEach(module => {
    const option = document.createElement('option');
    option.value = module.id;
    option.textContent = module.name;
    option.dataset.moduleData = JSON.stringify(module);
    selectElement.appendChild(option);
  });
}

/**
 * Handle category selection change
 */
function handleCategoryChange(categorySelect, indicatorSelect) {
  const category = categorySelect.value;
  populateIndicatorDropdown(indicatorSelect, category);
  
  // Reset indicator selection
  indicatorSelect.value = '';
  
  // Hide configuration panel until indicator selected
  const configPanel = document.getElementById('moduleConfigPanel');
  if (configPanel) {
    configPanel.style.display = 'none';
  }
}

// ============================================================================
// CONDITION MANAGEMENT
// ============================================================================

/**
 * Show the add condition form
 */
function showAddConditionForm() {
  console.log('[UI] Opening add condition form...');
  
  const container = document.getElementById('conditionsContainer');
  if (!container) {
    console.error('[UI] Could not find conditionsContainer');
    return;
  }
  
  // Hide empty state
  const emptyState = document.getElementById('empty-state');
  if (emptyState) {
    emptyState.style.display = 'none';
  }
  
  // Create form HTML
  const formHTML = `
    <div id="addConditionFormCard" class="strategy-card" style="border: 2px solid var(--accent-blue); background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);">
      <div class="card-header">
        <h3 style="color: var(--accent-blue); margin: 0; font-size: 1.1rem;">➕ Add Entry Condition</h3>
      </div>
      
      <div style="padding: 1.5rem;">
        <div class="form-grid" style="grid-template-columns: 1fr 1fr;">
          <div class="form-group">
            <label class="form-label">Category</label>
            <select id="conditionCategory" class="form-select">
              <option value="">Select Category...</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Indicator</label>
            <select id="conditionIndicator" class="form-select" disabled>
              <option value="">First select a category...</option>
            </select>
          </div>
        </div>
        
        <div class="form-grid" style="grid-template-columns: 2fr 1fr 1fr; margin-top: 1rem;">
          <div class="form-group">
            <label class="form-label">Operator</label>
            <select id="conditionOperator" class="form-select">
              <option value=">">Greater than (>)</option>
              <option value="<">Less than (<)</option>
              <option value=">=">Greater or equal (≥)</option>
              <option value="<=">Less or equal (≤)</option>
              <option value="==">Equal to (=)</option>
              <option value="crosses_above">Crosses above (↗)</option>
              <option value="crosses_below">Crosses below (↘)</option>
            </select>
          </div>
          
          <div class="form-group">
            <label class="form-label">Value</label>
            <input type="number" id="conditionValue" class="form-input" step="any" placeholder="e.g. 30" required>
          </div>
          
          <div class="form-group">
            <label class="form-label">Logic</label>
            <select id="conditionLogic" class="form-select">
              <option value="AND">AND</option>
              <option value="OR">OR</option>
            </select>
            <p class="form-hint" style="font-size: 0.75rem; margin-top: 0.25rem;">How to combine with next condition</p>
          </div>
        </div>
        
        <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
          <button type="button" class="btn-submit" onclick="addCondition()" style="flex: 1;">
            ✓ Add Condition
          </button>
          <button type="button" class="btn-add-condition" onclick="cancelAddCondition()" style="flex: 1; background: var(--bg-secondary);">
            ✕ Cancel
          </button>
        </div>
      </div>
    </div>
  `;
  
  // Insert form at the top of container
  container.insertAdjacentHTML('afterbegin', formHTML);
  
  // Populate category dropdown
  const categorySelect = document.getElementById('conditionCategory');
  const indicatorSelect = document.getElementById('conditionIndicator');
  
  populateCategoryDropdown(categorySelect);
  
  // Set up event listeners
  categorySelect.addEventListener('change', () => {
    handleCategoryChange(categorySelect, indicatorSelect);
  });
  
  console.log('[UI] ✓ Add condition form displayed');
}

/**
 * Cancel add condition form
 */
function cancelAddCondition() {
  const formCard = document.getElementById('addConditionFormCard');
  if (formCard) {
    formCard.remove();
  }
  
  // Show empty state if no conditions
  if (conditions.length === 0) {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
      emptyState.style.display = 'block';
    }
  }
  
  console.log('[UI] Add condition form cancelled');
}

/**
 * Add a condition to the strategy
 */
function addCondition() {
  // Get form values
  const category = document.getElementById('conditionCategory').value;
  const indicatorId = document.getElementById('conditionIndicator').value;
  const operator = document.getElementById('conditionOperator').value;
  const value = document.getElementById('conditionValue').value;
  const logic = document.getElementById('conditionLogic').value;
  
  // Validate
  if (!category || !indicatorId || !value) {
    alert('Please fill in all required fields');
    return;
  }
  
  // Get module data
  const indicatorSelect = document.getElementById('conditionIndicator');
  const selectedOption = indicatorSelect.options[indicatorSelect.selectedIndex];
  const moduleData = JSON.parse(selectedOption.dataset.moduleData);
  
  // Create condition object
  const condition = {
    id: conditionCount++,
    category: category,
    module: indicatorId,
    moduleName: moduleData.name,
    operator: operator,
    value: value,
    logic: logic,
    config: {}  // Empty config for now
  };
  
  // Add to conditions array
  conditions.push(condition);
  
  // Render condition card
  renderConditionCard(condition);
  
  // Hide form
  cancelAddCondition();
  
  // Update UI
  updateAddConditionButton();
  updateSubmitButton();
  
  console.log('[CONDITION] Added:', condition);
}

/**
 * Render a condition card
 */
function renderConditionCard(condition) {
  const container = document.getElementById('conditionsContainer');
  if (!container) return;
  
  // Get category metadata
  const categoryMeta = categoryMetadata[condition.category] || {};
  
  // Create card HTML - STANDALONE CARD
  const cardHTML = `
    <div class="strategy-card" data-condition-id="${condition.id}" style="border-left: 4px solid #3b82f6; margin-bottom: 1.5rem; animation: slideIn 0.3s ease;">
      <div style="padding: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
          <div>
            <span style="background: rgba(59, 130, 246, 0.1); padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.875rem; color: var(--accent-blue); font-weight: 600;">
              ${categoryMeta.icon || '📊'} ${categoryMeta.label || condition.category}
            </span>
          </div>
          <button type="button" onclick="removeCondition(${condition.id})" style="background: rgba(239, 68, 68, 0.1); color: #dc2626; padding: 0.5rem 1rem; border: none; border-radius: 8px; font-size: 0.875rem; font-weight: 600; cursor: pointer; transition: all 0.2s;">
            🗑️ Remove
          </button>
        </div>
        
        <div style="margin-bottom: 1rem;">
          <div style="font-size: 1.1rem; color: var(--text-primary); font-weight: 700; margin-bottom: 0.5rem;">
            ${condition.moduleName}
          </div>
          ${condition.note ? `
            <div style="font-size: 0.875rem; color: var(--text-muted); font-style: italic;">
              ${condition.note}
            </div>
          ` : ''}
        </div>
        
        <div style="display: flex; align-items: center; gap: 0.75rem; background: var(--bg-secondary); padding: 1rem; border-radius: 12px;">
          <span style="color: var(--text-muted); font-weight: 500;">When</span>
          <span style="color: var(--text-primary); font-weight: 600;">Value</span>
          <span style="font-size: 1.5rem; color: #3b82f6; font-weight: 700;">${condition.operator}</span>
          <span style="color: #3b82f6; font-weight: 700; font-size: 1.25rem;">${condition.value}</span>
        </div>
      </div>
    </div>
    
    ${conditions.indexOf(condition) < conditions.length - 1 ? `
      <div style="text-align: center; margin: 1.5rem 0;">
        <div style="display: inline-flex; align-items: center; gap: 1rem;">
          <div style="width: 60px; height: 2px; background: linear-gradient(90deg, transparent, #cbd5e1);"></div>
          <span style="display: inline-block; padding: 0.5rem 1.5rem; background: ${condition.logic === 'AND' ? '#3b82f6' : '#8b5cf6'}; color: white; border-radius: 20px; font-weight: 700; font-size: 0.875rem; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);">
            ${condition.logic}
          </span>
          <div style="width: 60px; height: 2px; background: linear-gradient(90deg, #cbd5e1, transparent);"></div>
        </div>
      </div>
    ` : ''}
  `;
  
  // Hide empty state
  const emptyState = document.getElementById('empty-state');
  if (emptyState) {
    emptyState.style.display = 'none';
  }
  
  // Insert card
  container.insertAdjacentHTML('beforeend', cardHTML);
  
  console.log('[UI] ✓ Condition card rendered:', condition.id);
}

// Add animation CSS
if (!document.getElementById('conditionAnimations')) {
  const style = document.createElement('style');
  style.id = 'conditionAnimations';
  style.textContent = `
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(-20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  `;
  document.head.appendChild(style);
}

/**
 * Remove a condition
 */
function removeCondition(conditionId) {
  // Remove from array
  conditions = conditions.filter(c => c.id !== conditionId);
  
  // Remove from DOM
  const card = document.querySelector(`[data-condition-id="${conditionId}"]`);
  if (card) {
    card.remove();
  }
  
  // Update UI
  updateAddConditionButton();
  updateSubmitButton();
  
  console.log('[CONDITION] Removed:', conditionId);
}

/**
 * Update add condition button state
 */
function updateAddConditionButton() {
  const btn = document.getElementById('add-condition');
  if (!btn) return;
  
  if (conditions.length === 0) {
    btn.innerHTML = `
      <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
      </svg>
      Add First Condition
    `;
  } else {
    btn.innerHTML = `
      <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
      </svg>
      Add Another (${conditions.length})
    `;
  }
}

/**
 * Update submit button state
 */
function updateSubmitButton() {
  const btn = document.getElementById('submitBtn');
  if (!btn) return;
  
  // Enable only if at least one condition exists
  btn.disabled = conditions.length === 0;
}

// ============================================================================
// FORM SUBMISSION
// ============================================================================

/**
 * Handle form submission
 */
async function handleFormSubmit(event) {
  event.preventDefault();
  
  if (conditions.length === 0) {
    alert('Please add at least one entry condition');
    return;
  }
  
  // Collect form data
  const formData = {
    symbol: document.getElementById('symbol').value,
    timeframe: document.getElementById('timeframe').value,
    direction: document.querySelector('input[name="direction"]:checked').value,
    period: document.getElementById('period').value,
    session: document.getElementById('session')?.value || '',
    tp_r: parseFloat(document.getElementById('tp_r').value),
    sl_r: parseFloat(document.getElementById('sl_r').value),
    conditions: conditions.map(c => ({
      category: c.category,
      module: c.module,
      config: c.config
    }))
  };
  
  console.log('[SUBMIT] Running backtest with:', formData);
  
  // Show loading state
  const submitBtn = document.getElementById('submitBtn');
  const originalText = submitBtn.textContent;
  submitBtn.disabled = true;
  submitBtn.textContent = 'Running backtest...';
  
  try {
    const response = await fetch('/run-backtest-v2', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Backtest failed');
    }
    
    // Get HTML response
    const html = await response.text();
    
    // Replace page with results
    document.open();
    document.write(html);
    document.close();
    
  } catch (error) {
    console.error('[SUBMIT] Error:', error);
    alert(`Backtest failed: ${error.message}`);
    
    // Restore button
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
  }
}

// ============================================================================
// PAGE LOAD
// ============================================================================

document.addEventListener('DOMContentLoaded', async function() {
  console.log('='.repeat(60));
  console.log('QuantMetrics Strategy Builder v2.0 - Initializing...');
  console.log('='.repeat(60));
  
  // Load modules from API
  const loaded = await loadAvailableModules();
  
  if (loaded) {
    console.log('[SUCCESS] Modules loaded, initializing builder...');
    initializeBuilder();
  } else {
    console.error('[FAILED] Could not load modules');
    alert('Failed to load indicator library. Please refresh the page.');
  }
});