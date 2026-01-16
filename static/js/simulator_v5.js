// Strategy Simulator V5 - Simple ICT Template
// Direct testing without loading all modules

// Global state
let ictModules = [];
let additionalBlocks = []; // Array of {id, moduleId, config}

// Initialize test mode toggle
document.addEventListener('DOMContentLoaded', function() {
    // Test mode toggle handler
    const quickTestRadio = document.getElementById('quickTestMode');
    const fullTestRadio = document.getElementById('fullTestMode');
    const testPeriodSelect = document.getElementById('testPeriod');
    const testPeriodGroup = document.getElementById('testPeriodGroup');
    const periodHelp = document.getElementById('periodHelp');
    
    if (quickTestRadio && fullTestRadio && testPeriodSelect) {
        // Set initial state
        if (quickTestRadio.checked) {
            testPeriodSelect.value = '1mo';
            testPeriodGroup.style.opacity = '0.6';
            testPeriodGroup.style.pointerEvents = 'none';
            periodHelp.textContent = 'Quick Test: Fixed at 1 month for fast testing';
        }
        
        // Handle mode changes
        quickTestRadio.addEventListener('change', function() {
            if (this.checked) {
                testPeriodSelect.value = '1mo';
                testPeriodGroup.style.opacity = '0.6';
                testPeriodGroup.style.pointerEvents = 'none';
                periodHelp.textContent = 'Quick Test: Fixed at 1 month for fast testing';
            }
        });
        
        fullTestRadio.addEventListener('change', function() {
            if (this.checked) {
                testPeriodGroup.style.opacity = '1';
                testPeriodGroup.style.pointerEvents = 'auto';
                periodHelp.textContent = 'Full Test: Choose 1-6 months for comprehensive backtesting';
            }
        });
    }
});

/**
 * Display error message (Guardrail G7 - Error Contract)
 * Shows structured error with code, message, and details
 */
function displayError(errorData, containerId = 'simulator-v5-container') {
    // Remove any existing error messages
    const existingError = document.getElementById('backtestError');
    if (existingError) {
        existingError.remove();
    }
    
    const container = document.getElementById(containerId) || document.querySelector('.simulator-v5-container');
    if (!container) {
        console.error('Error container not found:', containerId);
        // Fallback to alert
        alert(errorData.error || errorData.message || 'An error occurred');
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

document.addEventListener('DOMContentLoaded', function() {
    const runBtn = document.getElementById('runBacktestBtn');
    const addBlockBtn = document.getElementById('addIctBlockBtn');
    const downloadTestDataBtn = document.getElementById('downloadTestDataBtn');
    
    if (runBtn) {
        runBtn.addEventListener('click', runBacktest);
    }
    
    if (addBlockBtn) {
        addBlockBtn.addEventListener('click', showAddBlockDialog);
    }
    
    if (downloadTestDataBtn) {
        downloadTestDataBtn.addEventListener('click', downloadTestData);
    }
    
    // Load ICT modules
    loadIctModules();
    
    // Update block status when fields change
    updateBlockStatuses();
    
    // Listen for changes
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('change', updateBlockStatuses);
    });
});

async function loadIctModules() {
    try {
        const response = await fetch('/api/modules/ict');
        const data = await response.json();
        if (data.success) {
            ictModules = data.modules;
            console.log('Loaded ICT modules:', ictModules.length);
        }
    } catch (error) {
        console.error('Error loading ICT modules:', error);
    }
}

function showAddBlockDialog() {
    if (ictModules.length === 0) {
        alert('Loading ICT modules... Please try again in a moment.');
        return;
    }
    
    // Create modal/dialog
    const dialog = document.createElement('div');
    dialog.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 2rem;
        border-radius: 8px;
        max-width: 500px;
        width: 90%;
        max-height: 80vh;
        overflow-y: auto;
    `;
    
    content.innerHTML = `
        <h3 style="margin-top: 0;">Add ICT Block</h3>
        <p>Select an ICT concept to add:</p>
        <select id="ictModuleSelect" class="form-control" style="margin-bottom: 1rem;">
            <option value="">-- Select ICT Module --</option>
            ${ictModules.map(m => `<option value="${m.id}">${m.name}</option>`).join('')}
        </select>
        <div style="display: flex; gap: 1rem; justify-content: flex-end;">
            <button class="btn-secondary" onclick="this.closest('div[style*=\"position: fixed\"]').remove()">Cancel</button>
            <button class="btn-primary" onclick="addSelectedBlock()">Add Block</button>
        </div>
    `;
    
    dialog.appendChild(content);
    document.body.appendChild(dialog);
    
    // Store dialog reference
    window.currentDialog = dialog;
    
    // Make addSelectedBlock available globally
    window.addSelectedBlock = function() {
    const select = document.getElementById('ictModuleSelect');
    const moduleId = select.value;
    
    if (!moduleId) {
        alert('Please select a module');
        return;
    }
    
    const module = ictModules.find(m => m.id === moduleId);
    if (!module) {
        alert('Module not found');
        return;
    }
    
    // Check if this module is already added (prevent duplicates)
    const alreadyAdded = additionalBlocks.some(b => b.moduleId === module.id);
    if (alreadyAdded) {
        alert(`"${module.name}" is already added. Each ICT concept can only be added once.`);
        return;
    }
    
    // Create block
    const blockId = `block_${Date.now()}`;
    additionalBlocks.push({
        id: blockId,
        moduleId: module.id,  // Use module.id from the module object
        config: {}
    });
    
    // Render block
    renderIctBlock(blockId, module);
    
    // Close dialog
    if (window.currentDialog) {
        window.currentDialog.remove();
        window.currentDialog = null;
    }
    };
}

function renderIctBlock(blockId, module) {
    const container = document.getElementById('additionalBlocksContainer');
    
    const blockDiv = document.createElement('div');
    blockDiv.className = 'decision-block';
    blockDiv.id = blockId;
    blockDiv.dataset.moduleId = module.id;
    
    // Build config fields from schema
    let configFields = '';
    if (module.config_schema && module.config_schema.fields) {
        configFields = module.config_schema.fields.map(field => {
            if (field.type === 'number') {
                return `
                    <div class="form-group">
                        <label>${field.label || field.name}</label>
                        <input type="number" 
                               class="form-control ict-config-field" 
                               data-field="${field.name}"
                               data-block="${blockId}"
                               value="${field.default || ''}"
                               ${field.min ? `min="${field.min}"` : ''}
                               ${field.max ? `max="${field.max}"` : ''}
                               ${field.step ? `step="${field.step}"` : ''}>
                        ${field.help ? `<small>${field.help}</small>` : ''}
                    </div>
                `;
            } else if (field.type === 'select') {
                const options = (field.options || []).map(opt => 
                    `<option value="${opt.value || opt}">${opt.label || opt}</option>`
                ).join('');
                return `
                    <div class="form-group">
                        <label>${field.label || field.name}</label>
                        <select class="form-control ict-config-field" 
                                data-field="${field.name}"
                                data-block="${blockId}">
                            ${options}
                        </select>
                        ${field.help ? `<small>${field.help}</small>` : ''}
                    </div>
                `;
            } else if (field.type === 'boolean') {
                return `
                    <div class="form-group">
                        <label>
                            <input type="checkbox" 
                                   class="ict-config-field" 
                                   data-field="${field.name}"
                                   data-block="${blockId}"
                                   ${field.default ? 'checked' : ''}>
                            ${field.label || field.name}
                        </label>
                        ${field.help ? `<small>${field.help}</small>` : ''}
                    </div>
                `;
            }
            return '';
        }).join('');
    }
    
    blockDiv.innerHTML = `
        <div class="block-header">
            <h4>${module.name}</h4>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <span class="block-status" id="${blockId}Status">Not configured</span>
                <button class="block-remove-btn" onclick="removeBlock('${blockId}')">Remove</button>
            </div>
        </div>
        <div class="block-content">
            <p class="block-description">${module.description || ''}</p>
            ${configFields}
        </div>
    `;
    
    container.appendChild(blockDiv);
    
    // Add change listeners
    blockDiv.querySelectorAll('.ict-config-field').forEach(field => {
        field.addEventListener('change', () => updateBlockStatus(blockId));
    });
    
    updateBlockStatus(blockId);
}

window.removeBlock = function(blockId) {
    if (confirm('Remove this block?')) {
        additionalBlocks = additionalBlocks.filter(b => b.id !== blockId);
        const blockEl = document.getElementById(blockId);
        if (blockEl) {
            blockEl.remove();
        }
    }
};

function updateBlockStatus(blockId) {
    const block = additionalBlocks.find(b => b.id === blockId);
    if (!block) return;
    
    const blockEl = document.getElementById(blockId);
    if (!blockEl) return;
    
    const statusEl = document.getElementById(`${blockId}Status`);
    if (!statusEl) return;
    
    // Check if all required fields are filled
    const fields = blockEl.querySelectorAll('.ict-config-field');
    let allFilled = true;
    
    fields.forEach(field => {
        if (field.type === 'checkbox') {
            // Checkboxes are always "filled"
        } else if (field.value === '' || field.value === null) {
            allFilled = false;
        }
    });
    
    if (allFilled && fields.length > 0) {
        statusEl.textContent = 'Configured';
        statusEl.classList.add('configured');
    } else {
        statusEl.textContent = 'Not configured';
        statusEl.classList.remove('configured');
    }
}

function updateBlockStatuses() {
    // Block 1: HTF Market Bias
    const htfTimeframe = document.getElementById('htfTimeframe').value;
    const bosLookback = document.getElementById('bosLookback').value;
    const block1Status = document.getElementById('block1Status');
    if (htfTimeframe && bosLookback) {
        block1Status.textContent = 'Configured';
        block1Status.classList.add('configured');
    } else {
        block1Status.textContent = 'Not configured';
        block1Status.classList.remove('configured');
    }
    
    // Block 2: Liquidity Sweep
    const sweepType = document.getElementById('sweepType').value;
    const sweepTolerance = document.getElementById('sweepTolerance').value;
    const sweepLookback = document.getElementById('sweepLookback').value;
    const block2Status = document.getElementById('block2Status');
    if (sweepType && sweepTolerance && sweepLookback) {
        block2Status.textContent = 'Configured';
        block2Status.classList.add('configured');
    } else {
        block2Status.textContent = 'Not configured';
        block2Status.classList.remove('configured');
    }
    
    // Block 3: Displacement Entry
    const displacementBodyPct = document.getElementById('displacementBodyPct').value;
    const displacementMovePct = document.getElementById('displacementMovePct').value;
    const entryMethod = document.getElementById('entryMethod').value;
    const block3Status = document.getElementById('block3Status');
    if (displacementBodyPct && displacementMovePct && entryMethod) {
        block3Status.textContent = 'Configured';
        block3Status.classList.add('configured');
    } else {
        block3Status.textContent = 'Not configured';
        block3Status.classList.remove('configured');
    }
}

function runBacktest() {
    // Get test mode and adjust period accordingly
    const testMode = document.querySelector('input[name="testMode"]:checked')?.value || 'quick';
    let testPeriod = document.getElementById('testPeriod').value;
    
    // Quick Test mode: force 1mo
    if (testMode === 'quick') {
        testPeriod = '1mo';
    }
    
    // Collect all data
    const backtestData = {
        symbol: document.getElementById('symbol').value,
        entryTimeframe: document.getElementById('entryTimeframe').value,
        testPeriod: testPeriod,
        testMode: testMode, // Include mode for potential backend use
        
        // Block 1: HTF Market Bias
        htfMarketBias: {
            timeframe: document.getElementById('htfTimeframe').value,
            bosLookback: parseInt(document.getElementById('bosLookback').value)
        },
        
        // Block 2: Liquidity Sweep
        liquiditySweep: {
            sweepType: document.getElementById('sweepType').value,
            tolerance: parseFloat(document.getElementById('sweepTolerance').value),
            lookback: parseInt(document.getElementById('sweepLookback').value)
        },
        
        // Block 3: Displacement Entry
        displacementEntry: {
            minBodyPct: parseFloat(document.getElementById('displacementBodyPct').value),
            minMovePct: parseFloat(document.getElementById('displacementMovePct').value),
            entryMethod: document.getElementById('entryMethod').value
        },
        
        // Additional ICT Blocks
        additionalBlocks: collectAdditionalBlocks(),
        
        // Risk Management
        risk: {
            stopLoss: document.getElementById('stopLoss').value,
            takeProfit: parseFloat(document.getElementById('takeProfit').value),
            riskPerTrade: parseFloat(document.getElementById('riskPerTrade').value)
        }
    };
    
    console.log('Running backtest with data:', backtestData);
    console.log('Additional blocks:', backtestData.additionalBlocks.length);
    
    // Disable button
    const runBtn = document.getElementById('runBacktestBtn');
    const originalText = runBtn.textContent;
    runBtn.disabled = true;
    runBtn.textContent = 'Running backtest...';
    
    // Show loading
    showLoading();
    
    // Send to backend
    fetch('/run-backtest-v5', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestData)
    })
    .then(response => {
        if (response.ok) {
            return response.text().then(html => {
                hideLoading();
                document.open();
                document.write(html);
                document.close();
            });
        } else {
            // Handle error response (Guardrail G7 - Error Contract)
            return handleErrorResponse(response, 'Backtest failed')
                .then(result => {
                    if (result && result.isHtml) {
                        hideLoading();
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
        hideLoading();
        
        // Check if it's an HTML error page
        if (error && error.error && error.error.includes('<!DOCTYPE')) {
            // Already handled as HTML
            return;
        }
        
        // Display structured error (Beta-1: Error Contract)
        displayError(error);
        runBtn.disabled = false;
        runBtn.textContent = originalText;
    });
}

function showLoading() {
    // Beta-2: Improved loading indicator
    let overlay = document.getElementById('loadingOverlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            color: white;
            flex-direction: column;
            gap: 1.5rem;
        `;
        
        // Create spinner
        const spinner = document.createElement('div');
        spinner.style.cssText = `
            width: 60px;
            height: 60px;
            border: 4px solid rgba(255, 255, 255, 0.2);
            border-top-color: #2196F3;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        `;
        
        // Add spinner animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
        
        overlay.innerHTML = `
            ${spinner.outerHTML}
            <div style="font-size: 1.25rem; font-weight: 600;">Running ICT Backtest</div>
            <div style="font-size: 0.95rem; opacity: 0.8;">Analyzing structure, liquidity, and displacement...</div>
        `;
        
        document.body.appendChild(overlay);
    } else {
        overlay.style.display = 'flex';
    }
    
    console.log('[Loading] Overlay shown for V5');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
        // Don't remove - keep it for next use (faster)
        // overlay.remove();
    }
    console.log('[Loading] Overlay hidden for V5');
}

function collectAdditionalBlocks() {
    const blocks = [];
    
    additionalBlocks.forEach(block => {
        const blockEl = document.getElementById(block.id);
        if (!blockEl) return;
        
        const config = {};
        const fields = blockEl.querySelectorAll('.ict-config-field');
        
        fields.forEach(field => {
            const fieldName = field.dataset.field;
            if (field.type === 'checkbox') {
                config[fieldName] = field.checked;
            } else if (field.type === 'number') {
                // Parse as integer if no decimal, otherwise float
                const value = field.value;
                if (value === '' || value === null) {
                    // Skip empty values (use module default)
                    return;
                }
                // Check if it's an integer (no decimal point)
                if (value.includes('.')) {
                    config[fieldName] = parseFloat(value);
                } else {
                    config[fieldName] = parseInt(value, 10);
                }
            } else {
                const value = field.value;
                if (value === '' || value === null) {
                    // Skip empty values
                    return;
                }
                config[fieldName] = value;
            }
        });
        
        blocks.push({
            moduleId: block.moduleId,
            config: config
        });
    });
    
    return blocks;
}

async function downloadTestData() {
    const btn = document.getElementById('downloadTestDataBtn');
    if (!btn) return;
    
    const originalText = btn.textContent;
    
    btn.disabled = true;
    btn.textContent = 'Downloading...';
    
    try {
        const testData = {
            symbol: document.getElementById('symbol').value,
            entryTimeframe: document.getElementById('entryTimeframe').value,
            htfTimeframe: document.getElementById('htfTimeframe').value,
            testPeriod: document.getElementById('testPeriod').value
        };
        
        const response = await fetch('/download-test-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`✓ Test data downloaded!\n${result.message}\n\nYou can now run backtests faster using cached data.`);
        } else {
            alert(`Error: ${result.error || 'Failed to download test data'}`);
        }
    } catch (error) {
        console.error('Error downloading test data:', error);
        alert('Error downloading test data. Please check console for details.');
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

