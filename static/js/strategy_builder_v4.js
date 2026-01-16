/* =============================================
   STRATEGY BUILDER V4 - Decision Block Model
   ============================================= */

// Application State
const appState = {
    template: null,
    marketContext: null,
    decisionBlocks: [],
    exit: {
        stopLoss: 1,
        takeProfit: 2
    }
};

// Cache for module config schemas
const moduleSchemaCache = {};

// Available modules list (loaded from API)
let availableModules = null;

/**
 * Load available modules from API
 */
async function loadAvailableModules() {
    if (availableModules) return availableModules;
    
    try {
        const response = await fetch('/api/modules');
        const data = await response.json();
        
        if (data.success && data.modules) {
            // Flatten all modules into a single list with their IDs
            availableModules = [];
            for (const category in data.modules) {
                data.modules[category].forEach(module => {
                    availableModules.push(module.id);
                });
            }
            console.log(`[Validation] Loaded ${availableModules.length} available modules`);
            return availableModules;
        }
    } catch (error) {
        console.warn('[Validation] Could not load available modules:', error);
    }
    
    return [];
}

/**
 * Validate that all sub-confirmations have valid module mappings
 */
async function validateModuleMappings() {
    const warnings = [];
    const errors = [];
    
    // Load available modules
    const modules = await loadAvailableModules();
    
    // Check each decision block
    for (const block of appState.decisionBlocks) {
        if (!block.subConfirmations) continue;
        
        for (const conf of block.subConfirmations) {
            // Skip if not selected (not used in backtest)
            if (!conf.selected && conf.type !== 'dropdown') continue;
            
            // Determine moduleId
            let moduleId = conf.moduleId;
            if (!moduleId) {
                moduleId = getModuleIdFromLabel(conf.label || '');
            }
            
            // Check if module exists
            if (modules.length > 0 && !modules.includes(moduleId)) {
                const error = {
                    block: block.title || `Block ${block.id}`,
                    confirmation: conf.label || 'Unknown',
                    moduleId: moduleId,
                    message: `Module '${moduleId}' not found in registry`
                };
                
                // Check if it's a known "no module" case
                const noModuleConcepts = [
                    'rejection candle', 'wick rejection', 'price rejection',
                    'no major news', 'active session' // Some have modules, some don't
                ];
                
                const isKnownNoModule = noModuleConcepts.some(concept => 
                    conf.label.toLowerCase().includes(concept)
                );
                
                if (isKnownNoModule) {
                    warnings.push({
                        ...error,
                        message: `'${conf.label}' has no module mapping (price action or external data)`
                    });
                } else {
                    errors.push(error);
                }
            }
        }
    }
    
    return { warnings, errors };
}

/**
 * Display error message (Guardrail G7 - Error Contract)
 * Shows structured error with code, message, and details
 */
function displayError(errorData, containerId = 'builderContainer') {
    // Remove any existing error messages
    const existingError = document.getElementById('backtestError');
    if (existingError) {
        existingError.remove();
    }
    
    const container = document.getElementById(containerId);
    if (!container) {
        console.error('Error container not found:', containerId);
        // Fallback to alert
        alert(errorData.error || 'An error occurred');
        return;
    }
    
    // Parse error data (could be Error object or response data)
    let error = {
        code: 'UNKNOWN_ERROR',
        error: 'An unexpected error occurred',
        details: null
    };
    
    if (errorData.code) {
        // Already in error response format
        error = errorData;
    } else if (errorData.message) {
        // Error object
        error.error = errorData.message;
    } else if (typeof errorData === 'string') {
        // String message
        error.error = errorData;
    }
    
    // Create error display element
    const errorDiv = document.createElement('div');
    errorDiv.id = 'backtestError';
    errorDiv.style.cssText = `
        margin: 1rem 0;
        padding: 1.5rem;
        border-radius: 8px;
        background: #fee;
        border: 2px solid #fcc;
        color: #c00;
    `;
    
    let html = `
        <div style="display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.5em;">⚠️</span>
            <div style="flex: 1;">
                <strong style="font-size: 1.1rem; display: block; margin-bottom: 0.5rem;">${escapeHtml(error.error)}</strong>
                ${error.code ? `<div style="font-size: 0.85rem; color: #666; margin-bottom: 0.5rem;">Error Code: <code>${escapeHtml(error.code)}</code></div>` : ''}
            </div>
        </div>
    `;
    
    // Add details if available
    if (error.details) {
        if (error.details.suggestion) {
            html += `
                <div style="margin-top: 1rem; padding: 0.75rem; background: #fff9e6; border-left: 3px solid #ff9800; border-radius: 4px;">
                    <strong>💡 Suggestion:</strong>
                    <div style="margin-top: 0.25rem;">${escapeHtml(error.details.suggestion)}</div>
                </div>
            `;
        }
        
        // Show other details
        const otherDetails = Object.entries(error.details)
            .filter(([key]) => key !== 'suggestion')
            .map(([key, value]) => {
                const formattedValue = typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value);
                return `<div style="margin-top: 0.5rem;"><strong>${escapeHtml(key)}:</strong> ${escapeHtml(formattedValue)}</div>`;
            });
        
        if (otherDetails.length > 0) {
            html += `
                <details style="margin-top: 1rem; cursor: pointer;">
                    <summary style="font-weight: bold; cursor: pointer;">Technical Details</summary>
                    <div style="margin-top: 0.5rem; padding: 0.75rem; background: #f5f5f5; border-radius: 4px; font-size: 0.9rem;">
                        ${otherDetails.join('')}
                    </div>
                </details>
            `;
        }
    }
    
    errorDiv.innerHTML = html;
    
    // Insert at the top of container
    container.insertBefore(errorDiv, container.firstChild);
    
    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Handle error response from backend (Guardrail G7 - Error Contract)
 */
function handleErrorResponse(response, defaultMessage = 'An error occurred') {
    return response.text().then(text => {
        try {
            // Try to parse as JSON (new error format)
            const data = JSON.parse(text);
            if (data.success === false) {
                // Structured error response
                return Promise.reject({
                    code: data.code || 'UNKNOWN_ERROR',
                    error: data.error || defaultMessage,
                    details: data.details || null
                });
            }
            // Not an error response, might be HTML
            throw new Error('Not an error response');
        } catch (e) {
            // Not JSON, might be HTML error page
            if (text.includes('<!DOCTYPE') || text.includes('<html')) {
                // Return HTML string so caller can render it
                return Promise.resolve({ isHtml: true, content: text });
            }
            // Plain text error
            return Promise.reject({
                code: 'PARSE_ERROR',
                error: text || defaultMessage,
                details: null
            });
        }
    });
}

/**
 * Display validation warnings/errors
 */
async function displayValidationResults() {
    const { warnings, errors } = await validateModuleMappings();
    
    // Clear previous validation messages
    const existingValidation = document.getElementById('moduleValidationMessage');
    if (existingValidation) {
        existingValidation.remove();
    }
    
    if (warnings.length === 0 && errors.length === 0) {
        return; // All good
    }
    
    // Create validation message container
    const container = document.getElementById('builderContainer');
    if (!container) return;
    
    const validationDiv = document.createElement('div');
    validationDiv.id = 'moduleValidationMessage';
    validationDiv.style.cssText = `
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 8px;
        background: ${errors.length > 0 ? '#fee' : '#fff9e6'};
        border: 1px solid ${errors.length > 0 ? '#fcc' : '#ffd700'};
    `;
    
    let html = `<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
        <span style="font-size: 1.2em;">${errors.length > 0 ? '⚠️' : 'ℹ️'}</span>
        <strong>Module Mapping ${errors.length > 0 ? 'Errors' : 'Warnings'}</strong>
    </div>`;
    
    if (errors.length > 0) {
        html += `<div style="margin-top: 0.5rem;">
            <strong style="color: #c00;">Errors (${errors.length}):</strong>
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                ${errors.map(e => `<li><strong>${e.block}</strong>: "${e.confirmation}" → Module '${e.moduleId}' not found</li>`).join('')}
            </ul>
        </div>`;
    }
    
    if (warnings.length > 0) {
        html += `<div style="margin-top: 0.5rem;">
            <strong style="color: #d4a017;">Warnings (${warnings.length}):</strong>
            <ul style="margin: 0.5rem 0; padding-left: 1.5rem;">
                ${warnings.map(w => `<li><strong>${w.block}</strong>: "${w.confirmation}" → ${w.message}</li>`).join('')}
            </ul>
        </div>`;
    }
    
    html += `<div style="margin-top: 0.5rem; font-size: 0.875rem; color: #666;">
        These may not work correctly in backtests. Check <a href="/docs/concept_to_module_mapping.md" target="_blank">module mapping guide</a> for details.
    </div>`;
    
    validationDiv.innerHTML = html;
    
    // Insert at the top of builder container
    const firstChild = container.firstElementChild;
    if (firstChild) {
        container.insertBefore(validationDiv, firstChild);
    } else {
        container.appendChild(validationDiv);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Strategy Builder V4 initialized');
    initializeApp();
});

function initializeApp() {
    // Load templates
    loadTemplates();
    
    // Initialize exit & risk
    initializeExitRisk();
    
    // Setup event listeners
    setupEventListeners();
}

// ===== TEMPLATE SELECTOR =====
function loadTemplates() {
    const templatesGrid = document.getElementById('templatesGrid');
    if (!templatesGrid) return;
    
    const templates = [
        {
            id: 'ict_smc',
            icon: '🧠',
            name: 'ICT / SMC Base Setup',
            description: 'Smart Money Concepts framework with 3 Decision Blocks.',
            blocksCount: 3
        },
        {
            id: 'trend_following',
            icon: '📈',
            name: 'Trend Following',
            description: 'Ride momentum with 3 Decision Blocks.',
            blocksCount: 3
        },
        {
            id: 'mean_reversion',
            icon: '🔄',
            name: 'Mean Reversion',
            description: 'Return to value with 2 Decision Blocks.',
            blocksCount: 2
        },
        {
            id: 'breakout_momentum',
            icon: '🚀',
            name: 'Breakout Momentum',
            description: 'Expansion plays with 3 Decision Blocks.',
            blocksCount: 3
        },
        {
            id: 'golden_cross',
            icon: '✨',
            name: 'Golden Cross',
            description: 'Classic crossover with 2 Decision Blocks.',
            blocksCount: 2
        },
        {
            id: 'supertrend',
            icon: '🌊',
            name: 'Supertrend Trend',
            description: 'Volatility-based trend with 3 Decision Blocks.',
            blocksCount: 3
        },
        {
            id: 'rsi_bounce',
            icon: '📉',
            name: 'RSI Oversold Bounce',
            description: 'Momentum pullback with 3 Decision Blocks.',
            blocksCount: 3
        },
        {
            id: 'vwap_reversion',
            icon: '⚖️',
            name: 'VWAP Reversion',
            description: 'Intraday mean with 3 Decision Blocks.',
            blocksCount: 3
        },
        {
            id: 'momentum_scalping',
            icon: '⚡',
            name: 'Momentum Scalping',
            description: 'High-speed setups with 4 Decision Blocks.',
            blocksCount: 4
        },
        {
            id: 'my_templates',
            icon: '🧩',
            name: 'My Templates',
            description: 'Save your own strategies once you understand why they work.',
            blocksCount: 'Soon',
            disabled: true
        }
    ];
    
    templatesGrid.innerHTML = templates.map(template => `
        <div class="template-card" 
             data-template-id="${template.id}"
             ${template.disabled ? 'style="opacity: 0.5; cursor: not-allowed;"' : ''}
             onclick="${template.disabled ? '' : `selectTemplate('${template.id}')`}">
            <div class="template-icon">${template.icon}</div>
            <h3 class="template-name">${template.name}</h3>
            <p class="template-description">${template.description}</p>
            <p class="template-blocks-count">
                ${template.blocksCount === 'Soon' ? 'Coming soon' : `${template.blocksCount} Decision Blocks`}
            </p>
        </div>
    `).join('');
}

function selectTemplate(templateId) {
    appState.template = templateId;
    
    // Hide template selector
    document.getElementById('templateSelector').style.display = 'none';
    
    // Show builder
    document.getElementById('builderContainer').style.display = 'block';
    
    // Load template data
    loadTemplateData(templateId);
    
    // Show market context bar
    showMarketContextBar();
}

function loadTemplateData(templateId) {
    console.log('Loading template:', templateId);
    
    // Load template data
    let templateData = null;
    
    switch(templateId) {
        case 'ict_smc':
            templateData = ictSMCTemplate;
            break;
        case 'trend_following':
            templateData = trendFollowingTemplate;
            break;
        case 'mean_reversion':
            templateData = meanReversionTemplate;
            break;
        case 'breakout_momentum':
            templateData = breakoutMomentumTemplate;
            break;
        case 'golden_cross':
            templateData = goldenCrossTemplate;
            break;
        case 'supertrend':
            templateData = supertrendTemplate;
            break;
        case 'rsi_bounce':
            templateData = rsiBounceTemplate;
            break;
        case 'vwap_reversion':
            templateData = vwapReversionTemplate;
            break;
        case 'momentum_scalping':
            templateData = momentumScalpingTemplate;
            break;
        case 'my_templates':
            alert('My Templates feature coming soon. Save your own strategies once you understand why they work.');
            return;
        default:
            console.warn('Template not found:', templateId);
            return;
    }
    
    if (!templateData) return;
    
    // Apply market context suggestions
    if (templateData.marketContext && templateData.marketContext.suggestions) {
        appState.marketContext = { ...templateData.marketContext.suggestions };
        showMarketContextBar();
    }
    
    // Load Decision Blocks
    if (templateData.decisionBlocks) {
        const usedModuleIds = new Set();
        const duplicateWarnings = [];
        
        appState.decisionBlocks = templateData.decisionBlocks.map((block, blockIndex) => ({
            ...block,
            id: Date.now() + blockIndex, // Ensure unique IDs
            subConfirmations: block.subConfirmations?.map((conf, confIndex) => {
                const newConf = {
                    ...conf,
                    id: Date.now() + blockIndex * 1000 + confIndex // Ensure unique IDs
                };
                // Auto-determine moduleId if not set
                if (!newConf.moduleId) {
                    newConf.moduleId = getModuleIdFromLabel(conf.label || '');
                }
                
                // Check for duplicate modules
                if (newConf.moduleId && usedModuleIds.has(newConf.moduleId)) {
                    duplicateWarnings.push({
                        label: conf.label || 'Unknown',
                        moduleId: newConf.moduleId,
                        blockTitle: block.title || `Block ${blockIndex + 1}`
                    });
                    // Mark as duplicate (will be filtered out)
                    newConf._isDuplicate = true;
                } else if (newConf.moduleId) {
                    usedModuleIds.add(newConf.moduleId);
                }
                
                // Initialize config if hasParams is true but config is missing
                if (newConf.hasParams && !newConf.config) {
                    newConf.config = {};
                }
                return newConf;
            }).filter(conf => !conf._isDuplicate) || [] // Remove duplicates
        }));
        
        // Show warning if duplicates were found and removed
        if (duplicateWarnings.length > 0) {
            const warningMsg = `Template contains duplicate modules. The following were removed:\n\n` +
                duplicateWarnings.map(w => `- "${w.label}" (${w.moduleId}) in ${w.blockTitle}`).join('\n') +
                `\n\nEach module can only be used once across all Decision Blocks.`;
            alert(warningMsg);
        }
        
        renderDecisionBlocks();
        updateBlockCounter();
        
        // Hide empty state, show container
        document.getElementById('blocksEmptyState').style.display = 'none';
        document.getElementById('decisionBlocksContainer').style.display = 'block';
        document.getElementById('addBlockBtn').style.display = 'inline-flex';
    }
    
    // Apply exit defaults
    if (templateData.exit) {
        appState.exit = { ...templateData.exit };
        document.getElementById('stopLossInput').value = appState.exit.stopLoss;
        document.getElementById('takeProfitInput').value = appState.exit.takeProfit;
        updateRiskRewardBadge();
    }
    
    // Generate summary
    generateSummary();
    
    // Validate module mappings
    displayValidationResults();
    
    // Scroll to top of builder
    document.getElementById('builderContainer').scrollIntoView({ behavior: 'smooth' });
}

// ===== MARKET CONTEXT =====
function showMarketContextBar() {
    // For now, use defaults
    appState.marketContext = {
        market: 'XAUUSD',
        timeframe: '15m',
        session: 'London',
        direction: 'Long',
        testPeriod: '2mo'
    };
    
    const bar = document.getElementById('marketContextBar');
    const text = document.getElementById('contextText');
    
    if (bar && text) {
        const ctx = appState.marketContext;
        text.textContent = `${ctx.market} · ${ctx.timeframe} · ${ctx.session} · ${ctx.direction} · ${ctx.testPeriod}`;
        bar.style.display = 'block';
    }
    
    // Setup edit button
    const editBtn = document.getElementById('contextEditBtn');
    if (editBtn) {
        editBtn.addEventListener('click', function() {
            showMarketContextEditor();
        });
    }
}

function showMarketContextEditor() {
    const ctx = appState.marketContext;
    const editor = document.getElementById('marketContextEditor');
    const bar = document.getElementById('marketContextBar');
    
    if (!editor) return;
    
    // Hide bar, show editor
    if (bar) bar.style.display = 'none';
    editor.style.display = 'block';
    
    // Populate form
    document.getElementById('editMarket').value = ctx.market || 'XAUUSD';
    document.getElementById('editTimeframe').value = ctx.timeframe || '15m';
    document.getElementById('editSession').value = ctx.session || 'London';
    document.getElementById('editDirection').value = ctx.direction || 'Long';
    document.getElementById('editTestPeriod').value = ctx.testPeriod || '2mo';
    
    // Scroll to editor
    editor.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function saveMarketContext() {
    appState.marketContext = {
        market: document.getElementById('editMarket').value,
        timeframe: document.getElementById('editTimeframe').value,
        session: document.getElementById('editSession').value,
        direction: document.getElementById('editDirection').value,
        testPeriod: document.getElementById('editTestPeriod').value
    };
    
    const editor = document.getElementById('marketContextEditor');
    if (editor) editor.style.display = 'none';
    
    showMarketContextBar();
    generateSummary();
}

function cancelMarketContextEdit() {
    const editor = document.getElementById('marketContextEditor');
    const bar = document.getElementById('marketContextBar');
    
    if (editor) editor.style.display = 'none';
    if (bar) bar.style.display = 'block';
}

// ===== DECISION BLOCKS =====
function addDecisionBlock() {
    // Check max blocks
    if (appState.decisionBlocks.length >= 4) {
        alert('Maximum 4 Decision Blocks allowed.');
        return;
    }
    
    const newBlock = {
        id: Date.now(),
        title: 'New Decision Block',
        explanation: 'Groups multiple confirmations into one decision.',
        subConfirmations: []
    };
    
    appState.decisionBlocks.push(newBlock);
    
    renderDecisionBlocks();
    updateBlockCounter();
    
    // Hide empty state, show container
    document.getElementById('blocksEmptyState').style.display = 'none';
    document.getElementById('decisionBlocksContainer').style.display = 'block';
    document.getElementById('addBlockBtn').style.display = 'inline-flex';
}

function removeDecisionBlock(blockId) {
    appState.decisionBlocks = appState.decisionBlocks.filter(b => b.id !== blockId);
    
    renderDecisionBlocks();
    updateBlockCounter();
    
    // Show empty state if no blocks
    if (appState.decisionBlocks.length === 0) {
        document.getElementById('blocksEmptyState').style.display = 'block';
        document.getElementById('decisionBlocksContainer').style.display = 'none';
        document.getElementById('addBlockBtn').style.display = 'none';
    }
}

function renderDecisionBlocks() {
    const container = document.getElementById('decisionBlocksContainer');
    if (!container) return;
    
    container.innerHTML = appState.decisionBlocks.map(block => `
        <div class="decision-block-card" data-block-id="${block.id}">
            <div class="decision-block-header">
                <div class="decision-block-title-section">
                    <input type="text" 
                           class="decision-block-title-input" 
                           value="${block.title}"
                           placeholder="Decision Block Title"
                           onchange="updateBlockTitle(${block.id}, this.value)">
                    <input type="text" 
                           class="decision-block-explanation-input" 
                           value="${block.explanation}"
                           placeholder="Explanation: Groups multiple confirmations into one decision."
                           onchange="updateBlockExplanation(${block.id}, this.value)">
                </div>
                <button class="decision-block-remove" onclick="removeDecisionBlock(${block.id})">×</button>
            </div>
            
            <div class="sub-confirmations-section">
                <div class="sub-confirmations-header">
                    <div>
                        <span class="sub-confirmations-label">Sub-confirmations</span>
                        <p class="sub-confirmations-helper">Select all that apply.</p>
                    </div>
                </div>
                
                <div class="sub-confirmations-list" id="subConfirmations_${block.id}">
                    ${renderSubConfirmations(block)}
                </div>
                
                <button class="add-sub-confirmation-btn" onclick="addSubConfirmation(${block.id})">
                    + Add sub-confirmation
                </button>
            </div>
        </div>
    `).join('');
}

function renderSubConfirmations(block) {
    if (!block.subConfirmations || block.subConfirmations.length === 0) {
        return '<p class="empty-state-text" style="text-align: left; padding: 1rem;">Add sub-confirmations to this Decision Block.</p>';
    }
    
    return block.subConfirmations.map(conf => {
        // Generate unique ID for this confirmation
        const confId = conf.id || Date.now() + Math.random();
        if (!conf.id) conf.id = confId;
        
        // Initialize config if not present
        if (!conf.config) conf.config = {};
        
        // Render based on type
        if (conf.type === 'checkbox') {
            // Check if this checkbox has parameters enabled
            const hasParams = conf.hasParams === true;
            
            let paramsHtml = '';
            if (hasParams) {
                // Use fallback fields first (synchronous)
                const fieldsHtml = renderFallbackFields(conf, block.id, confId, conf.config || {});
                paramsHtml = `
                    <div class="sub-confirmation-params" id="params_${block.id}_${confId}" style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border-color); display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center;">
                        ${fieldsHtml}
                    </div>
                `;
                
                // Then async load and update with schema fields
                loadAndRenderSchemaFields(conf, block.id, confId);
            }
            
            return `
                <div class="sub-confirmation-item" style="flex-direction: column; align-items: stretch;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <input type="checkbox" 
                               class="sub-confirmation-checkbox" 
                               id="conf_${block.id}_${confId}"
                               ${conf.selected ? 'checked' : ''}
                               onchange="toggleSubConfirmation(${block.id}, ${confId}, this.checked)">
                        <label class="sub-confirmation-label" for="conf_${block.id}_${confId}" style="flex: 1;">
                            ${conf.label}
                        </label>
                        <button class="sub-confirmation-edit" 
                                onclick="toggleSubConfirmationParams(${block.id}, ${confId})" 
                                title="${hasParams ? 'Hide parameters' : 'Show parameters'}"
                                style="color: ${hasParams ? 'var(--accent-blue)' : 'var(--text-muted)'};">
                            ⚙️
                        </button>
                        <button class="sub-confirmation-remove" onclick="removeSubConfirmation(${block.id}, ${confId})">×</button>
                    </div>
                    ${paramsHtml}
                </div>
            `;
        } else if (conf.type === 'dropdown') {
            return `
                <div class="sub-confirmation-item" style="flex-direction: column; align-items: stretch;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <label class="sub-confirmation-label" style="flex: 0 0 auto; min-width: 150px;">
                            ${conf.label}:
                        </label>
                        <select class="form-input" style="flex: 1;"
                                onchange="updateSubConfirmationValue(${block.id}, ${confId}, this.value)">
                            ${conf.options.map(opt => `
                                <option value="${opt}" ${conf.selected === opt ? 'selected' : ''}>${opt}</option>
                            `).join('')}
                        </select>
                        <button class="sub-confirmation-remove" onclick="removeSubConfirmation(${block.id}, ${confId})">×</button>
                    </div>
                </div>
            `;
        } else {
            // Default to checkbox
            return `
                <div class="sub-confirmation-item">
                    <input type="checkbox" 
                           class="sub-confirmation-checkbox" 
                           id="conf_${block.id}_${confId}"
                           ${conf.selected ? 'checked' : ''}
                           onchange="toggleSubConfirmation(${block.id}, ${confId}, this.checked)">
                    <label class="sub-confirmation-label" for="conf_${block.id}_${confId}">
                        ${conf.label}
                    </label>
                    <button class="sub-confirmation-remove" onclick="removeSubConfirmation(${block.id}, ${confId})">×</button>
                </div>
            `;
        }
    }).join('');
}

function updateBlockTitle(blockId, title) {
    const block = appState.decisionBlocks.find(b => b.id === blockId);
    if (block) {
        block.title = title;
        generateSummary(); // Update summary
    }
}

function updateBlockExplanation(blockId, explanation) {
    const block = appState.decisionBlocks.find(b => b.id === blockId);
    if (block) block.explanation = explanation;
}

/**
 * Get all currently used module IDs across all Decision Blocks
 */
function getUsedModuleIds() {
    const usedModules = new Set();
    
    for (const block of appState.decisionBlocks) {
        if (block.subConfirmations) {
            for (const conf of block.subConfirmations) {
                if (conf.moduleId) {
                    usedModules.add(conf.moduleId);
                }
            }
        }
    }
    
    return usedModules;
}

function addSubConfirmation(blockId) {
    const block = appState.decisionBlocks.find(b => b.id === blockId);
    if (!block) return;
    
    const label = prompt('Enter sub-confirmation label:');
    if (!label || label.trim() === '') return;
    
    const needsParams = confirm('Does this sub-confirmation need parameters (operator, value, period)?');
    
    // Auto-determine moduleId from label
    const moduleId = getModuleIdFromLabel(label.trim());
    
    // Check if this module is already used in any Decision Block
    const usedModules = getUsedModuleIds();
    if (usedModules.has(moduleId)) {
        alert(`Module "${moduleId}" is already used in another Decision Block.\n\nEach module can only be used once across all Decision Blocks.`);
        return;
    }
    
    const newConf = {
        id: Date.now() + Math.random(),
        type: 'checkbox',
        label: label.trim(),
        selected: false,
        hasParams: needsParams,
        moduleId: moduleId,
        config: needsParams ? {
            operator: '>',
            value: 0,
            period: undefined
        } : {}
    };
    
    if (!block.subConfirmations) block.subConfirmations = [];
    block.subConfirmations.push(newConf);
    
    renderDecisionBlocks();
    generateSummary(); // Update summary
    displayValidationResults(); // Re-validate after changes
}

function removeSubConfirmation(blockId, confId) {
    const block = appState.decisionBlocks.find(b => b.id === blockId);
    if (block && block.subConfirmations) {
        block.subConfirmations = block.subConfirmations.filter(c => c.id !== confId);
        renderDecisionBlocks();
    }
}

function toggleSubConfirmation(blockId, confId, selected) {
    const block = appState.decisionBlocks.find(b => b.id === blockId);
    if (block && block.subConfirmations) {
        const conf = block.subConfirmations.find(c => c.id === confId);
        if (conf) {
            conf.selected = selected;
            generateSummary(); // Update summary (includes validation)
        }
    }
}

function updateBlockCounter() {
    const counter = document.getElementById('blockCount');
    if (counter) {
        counter.textContent = appState.decisionBlocks.length;
    }
}

// ===== EXIT & RISK =====
function initializeExitRisk() {
    const stopLossInput = document.getElementById('stopLossInput');
    const takeProfitInput = document.getElementById('takeProfitInput');
    
    if (stopLossInput) {
        stopLossInput.addEventListener('input', function() {
            appState.exit.stopLoss = parseFloat(this.value) || 1;
            updateRiskRewardBadge();
        });
    }
    
    if (takeProfitInput) {
        takeProfitInput.addEventListener('input', function() {
            appState.exit.takeProfit = parseFloat(this.value) || 2;
            updateRiskRewardBadge();
        });
    }
    
    updateRiskRewardBadge();
}

function updateRiskRewardBadge() {
    const badge = document.getElementById('riskRewardRatio');
    if (badge) {
        const ratio = (appState.exit.takeProfit / appState.exit.stopLoss).toFixed(1);
        badge.textContent = ratio;
    }
}

// ===== EVENT LISTENERS =====
function setupEventListeners() {
    const addFirstBlockBtn = document.getElementById('addFirstBlockBtn');
    const addBlockBtn = document.getElementById('addBlockBtn');
    const runBacktestBtn = document.getElementById('runBacktestBtn');
    const quickTestBtn = document.getElementById('quickTestBtn');
    
    if (addFirstBlockBtn) {
        addFirstBlockBtn.addEventListener('click', addDecisionBlock);
    }
    
    if (addBlockBtn) {
        addBlockBtn.addEventListener('click', addDecisionBlock);
    }
    
    if (runBacktestBtn) {
        runBacktestBtn.addEventListener('click', runBacktest);
    }
    
    if (quickTestBtn) {
        quickTestBtn.addEventListener('click', runQuickTest);
    }
}

// ===== REVIEW & RUN =====
function generateSummary() {
    const summaryContent = document.getElementById('summaryContent');
    if (!summaryContent) return;
    
    // Validate module mappings after summary update
    displayValidationResults();
    
    const ctx = appState.marketContext;
    const blocksCount = appState.decisionBlocks.length;
    const rrRatio = (appState.exit.takeProfit / appState.exit.stopLoss).toFixed(1);
    
    // Count total selected sub-confirmations
    let totalConfirmations = 0;
    appState.decisionBlocks.forEach(block => {
        const selected = block.subConfirmations?.filter(c => 
            c.selected || (c.type === 'dropdown' && c.selected)
        ) || [];
        totalConfirmations += selected.length;
    });
    
    let summary = `This strategy tests ${blocksCount} Decision Block${blocksCount !== 1 ? 's' : ''} `;
    summary += `with ${totalConfirmations} selected sub-confirmation${totalConfirmations !== 1 ? 's' : ''} `;
    summary += `on ${ctx.market} ${ctx.timeframe} during ${ctx.session} `;
    summary += `using a 1:${rrRatio} risk–reward.`;
    
    summaryContent.textContent = summary;
    
    // Update summary when blocks change
    setTimeout(() => {
        generateSummary();
    }, 100);
}

function runQuickTest() {
    // Same validation as full test
    if (!appState.marketContext) {
        alert('Please set market context first.');
        return;
    }
    
    if (appState.decisionBlocks.length === 0) {
        alert('Please add at least one Decision Block.');
        return;
    }
    
    // Check each block has at least one selected sub-confirmation
    for (const block of appState.decisionBlocks) {
        const selected = block.subConfirmations?.filter(c => c.selected) || [];
        if (selected.length === 0) {
            alert(`Decision Block "${block.title}" has no selected sub-confirmations.`);
            return;
        }
    }
    
    // Prepare data with quickTest flag
    const backtestData = {
        marketContext: appState.marketContext,
        decisionBlocks: appState.decisionBlocks,
        exit: appState.exit,
        quickTest: true  // Quick test mode
    };
    
    console.log('Running QUICK TEST with data:', backtestData);
    
    // Show loading overlay
    showLoadingOverlay();
    
    // Show loading on button
    const quickBtn = document.getElementById('quickTestBtn');
    const originalText = quickBtn.textContent;
    quickBtn.disabled = true;
    quickBtn.textContent = 'Running quick test...';
    
    // Send to backend
    fetch('/run-backtest-v4', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestData)
    })
    .then(response => {
        const contentType = response.headers.get('content-type');
        
        if (response.ok) {
            return response.text().then(html => {
                hideLoadingOverlay();
                document.open();
                document.write(html);
                document.close();
            });
        } else {
            // Handle error response (Guardrail G7 - Error Contract)
            return handleErrorResponse(response, 'Quick test failed')
                .then(result => {
                    if (result && result.isHtml) {
                        hideLoadingOverlay();
                        document.open();
                        document.write(result.content);
                        document.close();
                    }
                })
                .catch(error => {
                    throw error;
                });
        }
    })
    .catch(error => {
        console.error('Quick test error:', error);
        hideLoadingOverlay();
        
        // Check if it's an HTML error page
        if (error && error.error && error.error.includes('<!DOCTYPE')) {
            // Already handled as HTML
            return;
        }
        
        // Display structured error
        displayError(error);
        quickBtn.disabled = false;
        quickBtn.textContent = originalText;
    });
}

function runBacktest() {
    // Validate
    if (!appState.marketContext) {
        alert('Please set market context first.');
        return;
    }
    
    if (appState.decisionBlocks.length === 0) {
        alert('Please add at least one Decision Block.');
        return;
    }
    
    // Check each block has at least one selected sub-confirmation
    for (const block of appState.decisionBlocks) {
        const selected = block.subConfirmations?.filter(c => c.selected) || [];
        if (selected.length === 0) {
            alert(`Decision Block "${block.title}" has no selected sub-confirmations.`);
            return;
        }
    }
    
    // Prepare data
    const backtestData = {
        marketContext: appState.marketContext,
        decisionBlocks: appState.decisionBlocks,
        exit: appState.exit,
        quickTest: false  // Full test by default
    };
    
    console.log('Running backtest with data:', backtestData);
    
    // Show loading overlay
    showLoadingOverlay();
    
    // Show loading on button
    const runBtn = document.getElementById('runBacktestBtn');
    const originalText = runBtn.textContent;
    runBtn.disabled = true;
    runBtn.textContent = 'Running backtest...';
    
    // Send to backend
    fetch('/run-backtest-v4', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestData)
    })
    .then(response => {
        // Check content type to determine if it's HTML (error page) or JSON
        const contentType = response.headers.get('content-type');
        
        if (response.ok) {
            return response.text().then(html => {
                // Hide loading overlay before navigating
                hideLoadingOverlay();
                // If it's HTML, it's either the results page or error page
                document.open();
                document.write(html);
                document.close();
            });
        } else {
            // Handle error response (Guardrail G7 - Error Contract)
            return handleErrorResponse(response, 'Backtest failed')
                .then(result => {
                    if (result && result.isHtml) {
                        hideLoadingOverlay();
                        document.open();
                        document.write(result.content);
                        document.close();
                    }
                })
                .catch(error => {
                    throw error;
                });
        }
    })
    .catch(error => {
        console.error('Backtest error:', error);
        // Hide loading overlay
        hideLoadingOverlay();
        
        // Check if it's an HTML error page
        if (error && error.error && error.error.includes('<!DOCTYPE')) {
            // Already handled as HTML
            return;
        }
        
        // Display structured error
        displayError(error);
        runBtn.disabled = false;
        runBtn.textContent = originalText;
    });
}

/**
 * Show loading overlay with animated steps (Beta-2: Loading Indicator)
 * Shows immediately for user feedback, especially important for backtests >3s
 */
function showLoadingOverlay() {
    const overlay = document.getElementById('backtestLoadingOverlay');
    if (!overlay) {
        console.warn('[Loading] Overlay element not found');
        return;
    }
    
    // Show overlay immediately
    overlay.classList.add('show');
    
    // Update title based on context (Quick Test vs Full Test)
    const loadingTitle = overlay.querySelector('.loading-title');
    const isQuickTest = document.getElementById('quickTestBtn')?.disabled === true;
    if (loadingTitle) {
        loadingTitle.textContent = isQuickTest ? 'Running Quick Test' : 'Running Backtest';
    }
    
    // Animate steps sequentially
    const steps = ['step1', 'step2', 'step3', 'step4'];
    let currentStep = 0;
    
    // Reset all steps
    steps.forEach(stepId => {
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.remove('active');
            step.classList.remove('completed');
        }
    });
    
    // Activate first step
    const firstStep = document.getElementById(steps[0]);
    if (firstStep) firstStep.classList.add('active');
    
    // Animate through steps (Beta requirement: show progress for >3s operations)
    const stepInterval = setInterval(() => {
        if (currentStep < steps.length - 1) {
            const current = document.getElementById(steps[currentStep]);
            const next = document.getElementById(steps[currentStep + 1]);
            
            if (current) {
                current.classList.remove('active');
                current.classList.add('completed');
            }
            if (next) {
                next.classList.add('active');
            }
            
            currentStep++;
        } else {
            // Loop back to first step (for long-running backtests)
            const last = document.getElementById(steps[steps.length - 1]);
            const first = document.getElementById(steps[0]);
            
            if (last) {
                last.classList.remove('active');
                last.classList.add('completed');
            }
            if (first) {
                first.classList.remove('completed');
                first.classList.add('active');
            }
            
            currentStep = 0;
        }
    }, 2000); // Change step every 2 seconds
    
    // Store interval ID for cleanup
    overlay.dataset.intervalId = stepInterval;
    
    // Also update progress bar (if exists) - Beta-2: Better progress feedback
    const progressBar = overlay.querySelector('.loading-progress-bar');
    if (progressBar) {
        // Reset progress
        progressBar.style.width = '0%';
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + 2, 90); // Cap at 90% until complete
            progressBar.style.width = progress + '%';
        }, 500);
        overlay.dataset.progressIntervalId = progressInterval;
    }
    
    console.log('[Loading] Overlay shown');
    
    // Also update progress bar (if exists)
    const progressBar = overlay.querySelector('.loading-progress-bar');
    if (progressBar) {
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress = Math.min(progress + 5, 90); // Cap at 90% until complete
            progressBar.style.width = progress + '%';
        }, 500);
        overlay.dataset.progressIntervalId = progressInterval;
    }
    
    console.log('[Loading] Overlay shown');
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('backtestLoadingOverlay');
    if (!overlay) return;
    
    // Clear step animation interval
    if (overlay.dataset.intervalId) {
        clearInterval(parseInt(overlay.dataset.intervalId));
    }
    
    // Clear progress bar interval
    if (overlay.dataset.progressIntervalId) {
        clearInterval(parseInt(overlay.dataset.progressIntervalId));
        delete overlay.dataset.progressIntervalId;
    }
    
    // Complete progress bar
    const progressBar = overlay.querySelector('.loading-progress-bar');
    if (progressBar) {
        progressBar.style.width = '100%';
        // Small delay before hiding to show completion
        setTimeout(() => {
            overlay.classList.remove('show');
            // Reset progress for next time
            if (progressBar) progressBar.style.width = '0%';
        }, 300);
    } else {
        overlay.classList.remove('show');
    }
    
    // Reset steps
    const steps = ['step1', 'step2', 'step3', 'step4'];
    steps.forEach(stepId => {
        const step = document.getElementById(stepId);
        if (step) {
            step.classList.remove('active');
            step.classList.remove('completed');
        }
    });
    
    console.log('[Loading] Overlay hidden');
}

function updateSubConfirmationValue(blockId, confId, value) {
    const block = appState.decisionBlocks.find(b => b.id === blockId);
    if (block && block.subConfirmations) {
        const conf = block.subConfirmations.find(c => c.id === confId);
        if (conf) {
            conf.selected = value;
            generateSummary(); // Update summary
        }
    }
}

/**
 * Determine module_id from sub-confirmation label
 * Uses the same mapping as backend
 */
function getModuleIdFromLabel(label) {
    const labelLower = label.toLowerCase();
    
    // Same mapping as backend LABEL_TO_MODULE_MAPPING
    const mappings = {
        'rsi': 'rsi', 'oversold': 'rsi', 'overbought': 'rsi',
        'ma': 'sma', 'moving average': 'sma', 'sma': 'sma', 'ema': 'sma', 'golden cross': 'sma', 'cross': 'sma',
        'macd': 'macd',
        'bollinger': 'bollinger', 'bb': 'bollinger',
        'supertrend': 'supertrend', 'trend': 'supertrend',
        'adx': 'adx', 'aroon': 'aroon', 'ichimoku': 'ichimoku',
        'parabolic': 'parabolic_sar', 'sar': 'parabolic_sar',
        'stochastic': 'stochastic', 'stoch': 'stochastic',
        'momentum': 'momentum_indicator', 'divergence': 'momentum_indicator',
        'cci': 'cci', 'mfi': 'mfi', 'roc': 'roc',
        'williams': 'williams_r', 'williams r': 'williams_r',
        'ultimate': 'ultimate_oscillator', 'tsi': 'tsi',
        'atr': 'atr', 'volatility': 'atr',
        'keltner': 'keltner_channels', 'donchian': 'donchian_channels',
        'vwap': 'vwap', 'volume profile': 'volume_profile',
        'obv': 'obv', 'cmf': 'cmf', 'ad line': 'ad_line', 'accumulation': 'ad_line',
        'fair value gap': 'fair_value_gaps', 'fvg': 'fair_value_gaps',
        'liquidity sweep': 'liquidity_sweep', 'sweep': 'liquidity_sweep',
        'premium': 'premium_discount_zones', 'discount': 'premium_discount_zones',
        'premium discount': 'premium_discount_zones',
        'market structure': 'market_structure_shift', 'structure': 'market_structure_shift',
        'mss': 'market_structure_shift', 'displacement': 'displacement',
        'order block': 'order_blocks', 'orderblock': 'order_blocks',
        'killzone': 'kill_zones', 'kill zone': 'kill_zones',
        'breaker': 'breaker_blocks', 'mitigation': 'mitigation_blocks',
        'imbalance': 'imbalance_zones', 'inducement': 'inducement',
        'pivot': 'pivot_points', 'fibonacci': 'fibonacci', 'fib': 'fibonacci',
        'camarilla': 'camarilla', 'sr zone': 'sr_zones', 'support resistance': 'sr_zones'
    };
    
    // Try to find matching module
    for (const [keyword, modId] of Object.entries(mappings)) {
        if (labelLower.includes(keyword)) {
            return modId;
        }
    }
    
    // Default fallback
    return 'rsi';
}

/**
 * Fetch module config schema from API
 */
async function getModuleConfigSchema(moduleId) {
    // Check cache first
    if (moduleSchemaCache[moduleId]) {
        return moduleSchemaCache[moduleId];
    }
    
    try {
        const response = await fetch(`/api/modules/${moduleId}`);
        const data = await response.json();
        
        if (data.success && data.module && data.module.config_schema) {
            const schema = data.module.config_schema;
            moduleSchemaCache[moduleId] = schema;
            return schema;
        }
    } catch (error) {
        console.warn(`Could not fetch schema for ${moduleId}:`, error);
    }
    
    // Return null if not found
    return null;
}

/**
 * Render a single field from schema
 */
function renderSchemaField(field, blockId, confId, currentValue) {
    const fieldName = field.name;
    const fieldLabel = field.label || fieldName;
    const fieldType = field.type || 'number';
    const defaultValue = field.default;
    const helpText = field.help || '';
    
    // Get current value or default
    const value = currentValue !== undefined && currentValue !== null ? currentValue : (defaultValue !== undefined ? defaultValue : '');
    
    let fieldHtml = '';
    
    if (fieldType === 'select' && field.options) {
        // Select dropdown
        const selectedValue = value || defaultValue || field.options[0];
        fieldHtml = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <label style="font-size: 0.875rem; color: var(--text-secondary); white-space: nowrap;" title="${helpText}">
                    ${fieldLabel}:
                </label>
                <select class="form-input" style="min-width: 140px;"
                        onchange="updateSubConfirmationConfig(${blockId}, ${confId}, '${fieldName}', this.value)">
                    ${field.options.map(opt => {
                        const optValue = typeof opt === 'string' ? opt : String(opt);
                        const optLabel = optValue.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        return `<option value="${optValue}" ${selectedValue === optValue || selectedValue === opt ? 'selected' : ''}>${optLabel}</option>`;
                    }).join('')}
                </select>
            </div>
        `;
    } else if (fieldType === 'boolean') {
        // Checkbox for boolean
        const isChecked = value === true || value === 'true' || (defaultValue === true && value === '');
        fieldHtml = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <input type="checkbox" 
                       id="field_${blockId}_${confId}_${fieldName}"
                       ${isChecked ? 'checked' : ''}
                       onchange="updateSubConfirmationConfig(${blockId}, ${confId}, '${fieldName}', this.checked)">
                <label for="field_${blockId}_${confId}_${fieldName}" 
                       style="font-size: 0.875rem; color: var(--text-secondary);" 
                       title="${helpText}">
                    ${fieldLabel}
                </label>
            </div>
        `;
    } else {
        // Number input (default)
        const min = field.min !== undefined ? `min="${field.min}"` : '';
        const max = field.max !== undefined ? `max="${field.max}"` : '';
        const step = field.step !== undefined ? `step="${field.step}"` : '';
        const placeholder = defaultValue !== undefined ? String(defaultValue) : '';
        
        // Determine if we need float parsing (has step with decimals or default is float)
        const needsFloat = field.step !== undefined && field.step < 1 || 
                         (defaultValue !== undefined && !Number.isInteger(defaultValue));
        const parseFunc = needsFloat ? 'parseFloat' : 'parseInt';
        
        fieldHtml = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <label style="font-size: 0.875rem; color: var(--text-secondary); white-space: nowrap;" title="${helpText}">
                    ${fieldLabel}:
                </label>
                <input type="number" 
                       class="form-input" 
                       style="min-width: 80px;"
                       ${min} ${max} ${step}
                       placeholder="${placeholder}"
                       value="${value}"
                       onchange="updateSubConfirmationConfig(${blockId}, ${confId}, '${fieldName}', this.value !== '' ? ${parseFunc}(this.value) : null)">
            </div>
        `;
    }
    
    return fieldHtml;
}

/**
 * Render parameter fields based on module config schema
 * DEPRECATED: Now using loadAndRenderSchemaFields for async loading
 * Kept for backward compatibility
 */
async function renderParameterFields(conf, blockId, confId) {
    // Use fallback fields synchronously, then update async
    const fallbackHtml = renderFallbackFields(conf, blockId, confId, conf.config || {});
    
    // Trigger async schema loading
    loadAndRenderSchemaFields(conf, blockId, confId);
    
    return fallbackHtml;
}

/**
 * Fallback fields when schema is not available
 */
function renderFallbackFields(conf, blockId, confId, config) {
    // If no module_id stored, determine it from label
    if (!conf.moduleId) {
        conf.moduleId = getModuleIdFromLabel(conf.label);
    }
    
    // Always include operator field
    let fieldsHtml = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <label style="font-size: 0.875rem; color: var(--text-secondary); white-space: nowrap;">Operator:</label>
            <select class="form-input" style="min-width: 140px;"
                    onchange="updateSubConfirmationConfig(${blockId}, ${confId}, 'operator', this.value)">
                <option value=">" ${(config.operator || '>') === '>' ? 'selected' : ''}>> Greater than</option>
                <option value="<" ${config.operator === '<' ? 'selected' : ''}>< Less than</option>
                <option value=">=" ${config.operator === '>=' ? 'selected' : ''}>>= Greater or equal</option>
                <option value="<=" ${config.operator === '<=' ? 'selected' : ''}><= Less or equal</option>
                <option value="==" ${config.operator === '==' ? 'selected' : ''}>= Equal to</option>
                <option value="crosses_above" ${config.operator === 'crosses_above' ? 'selected' : ''}>Crosses Above</option>
                <option value="crosses_below" ${config.operator === 'crosses_below' ? 'selected' : ''}>Crosses Below</option>
            </select>
        </div>
    `;
    
    // Default: period and value for most indicators
    fieldsHtml += `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <label style="font-size: 0.875rem; color: var(--text-secondary); white-space: nowrap;">Period:</label>
            <input type="number" class="form-input" style="min-width: 80px;" placeholder="14"
                   value="${config.period || ''}"
                   onchange="updateSubConfirmationConfig(${blockId}, ${confId}, 'period', this.value ? parseInt(this.value) : null)">
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <label style="font-size: 0.875rem; color: var(--text-secondary); white-space: nowrap;">Value:</label>
            <input type="number" class="form-input" style="min-width: 100px;" step="any" placeholder="0"
                   value="${config.value !== undefined && config.value !== null ? config.value : ''}"
                   onchange="updateSubConfirmationConfig(${blockId}, ${confId}, 'value', this.value ? parseFloat(this.value) : null)">
        </div>
    `;
    
    return fieldsHtml;
}

/**
 * Load schema and update parameter fields asynchronously
 */
async function loadAndRenderSchemaFields(conf, blockId, confId) {
    // If no module_id stored, determine it from label
    if (!conf.moduleId) {
        conf.moduleId = getModuleIdFromLabel(conf.label);
    }
    
    const config = conf.config || {};
    const paramsContainer = document.getElementById(`params_${blockId}_${confId}`);
    
    if (!paramsContainer) return; // Container not found, skip
    
    // Try to fetch schema
    const schema = await getModuleConfigSchema(conf.moduleId);
    
    if (schema && schema.fields && Array.isArray(schema.fields)) {
        // Build fields HTML from schema
        let fieldsHtml = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <label style="font-size: 0.875rem; color: var(--text-secondary); white-space: nowrap;">Operator:</label>
                <select class="form-input" style="min-width: 140px;"
                        onchange="updateSubConfirmationConfig(${blockId}, ${confId}, 'operator', this.value)">
                    <option value=">" ${(config.operator || '>') === '>' ? 'selected' : ''}>> Greater than</option>
                    <option value="<" ${config.operator === '<' ? 'selected' : ''}>< Less than</option>
                    <option value=">=" ${config.operator === '>=' ? 'selected' : ''}>>= Greater or equal</option>
                    <option value="<=" ${config.operator === '<=' ? 'selected' : ''}><= Less or equal</option>
                    <option value="==" ${config.operator === '==' ? 'selected' : ''}>= Equal to</option>
                    <option value="crosses_above" ${config.operator === 'crosses_above' ? 'selected' : ''}>Crosses Above</option>
                    <option value="crosses_below" ${config.operator === 'crosses_below' ? 'selected' : ''}>Crosses Below</option>
                </select>
            </div>
        `;
        
        // Add schema fields
        for (const field of schema.fields) {
            // Skip operator and value as they're handled separately
            if (field.name === 'operator' || field.name === 'value') {
                continue;
            }
            
            const currentValue = config[field.name];
            fieldsHtml += renderSchemaField(field, blockId, confId, currentValue);
        }
        
        // Update container with schema-based fields
        paramsContainer.innerHTML = fieldsHtml;
    }
    // If schema not found, keep fallback fields (already rendered)
}

function toggleSubConfirmationParams(blockId, confId) {
    const block = appState.decisionBlocks.find(b => b.id === blockId);
    if (!block || !block.subConfirmations) return;
    
    const conf = block.subConfirmations.find(c => c.id === confId);
    if (!conf) return;
    
    // Toggle hasParams
    conf.hasParams = !conf.hasParams;
    
    // Initialize config if needed
    if (!conf.config) conf.config = {};
    
    // Determine module_id if not set
    if (!conf.moduleId) {
        conf.moduleId = getModuleIdFromLabel(conf.label);
    }
    
    // Re-render to show/hide params
    renderDecisionBlocks();
    generateSummary();
    
    // If enabling params, trigger async schema loading
    if (conf.hasParams) {
        setTimeout(() => {
            loadAndRenderSchemaFields(conf, blockId, confId);
        }, 100);
    }
}

function updateSubConfirmationConfig(blockId, confId, key, value) {
    const block = appState.decisionBlocks.find(b => b.id === blockId);
    if (block && block.subConfirmations) {
        const conf = block.subConfirmations.find(c => c.id === confId);
        if (conf) {
            if (!conf.config) conf.config = {};
            if (value === null || value === undefined || value === '') {
                delete conf.config[key];
            } else {
                conf.config[key] = value;
            }
            generateSummary(); // Update summary
        }
    }
}

// Make functions globally available
window.addDecisionBlock = addDecisionBlock;
window.removeDecisionBlock = removeDecisionBlock;
window.updateBlockTitle = updateBlockTitle;
window.updateBlockExplanation = updateBlockExplanation;
window.addSubConfirmation = addSubConfirmation;
window.removeSubConfirmation = removeSubConfirmation;
window.toggleSubConfirmation = toggleSubConfirmation;
window.toggleSubConfirmationParams = toggleSubConfirmationParams;
window.updateSubConfirmationValue = updateSubConfirmationValue;
window.updateSubConfirmationConfig = updateSubConfirmationConfig;
window.saveMarketContext = saveMarketContext;
window.cancelMarketContextEdit = cancelMarketContextEdit;
window.selectTemplate = selectTemplate;

