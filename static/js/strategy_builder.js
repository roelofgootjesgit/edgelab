/**
 * EdgeLab Strategy Builder - Dynamic Module UI
 * 
 * Fetches modules from API and builds UI dynamically
 * No hardcoded modules - everything driven by backend
 */

class StrategyBuilder {
    constructor() {
        this.modules = null;
        this.conditions = [];
        this.conditionCounter = 0;
        
        this.init();
    }
    
    async init() {
        console.log('[StrategyBuilder] Initializing...');
        
        // Fetch available modules from API
        await this.loadModules();
        
        // Setup event listeners
        this.setupEventListeners();
        
        console.log('[StrategyBuilder] Ready');
    }
    
    async loadModules() {
        try {
            console.log('[StrategyBuilder] Fetching modules from API...');
            const response = await fetch('/api/modules');
            
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            
            this.modules = await response.json();
            console.log('[StrategyBuilder] Modules loaded:', this.modules);
            
        } catch (error) {
            console.error('[StrategyBuilder] Failed to load modules:', error);
            alert('Failed to load strategy modules. Please refresh the page.');
        }
    }
    
    setupEventListeners() {
        // Add condition button
        const addBtn = document.getElementById('add-condition');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.addCondition());
        }
        
        // Form submit
        const form = document.getElementById('strategyForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }
    
    addCondition() {
        const conditionId = this.conditionCounter++;
        console.log(`[StrategyBuilder] Adding condition #${conditionId}`);
        
        const container = document.getElementById('conditionsContainer');
        const emptyState = document.getElementById('empty-state');
        
        // Hide empty state
        if (emptyState) {
            emptyState.style.display = 'none';
        }
        
        const isFirst = this.conditions.length === 0;
        
        // Create condition card
        const conditionCard = document.createElement('div');
        conditionCard.className = isFirst 
            ? 'condition-row flex flex-wrap items-center gap-3 p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200'
            : 'condition-row flex flex-wrap items-center gap-3 p-5 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border-2 border-purple-200';
        conditionCard.id = `condition-${conditionId}`;
        conditionCard.innerHTML = `
            <span class="font-bold w-8 ${isFirst ? 'text-edgelab-blue' : 'text-edgelab-purple'}">
                ${isFirst ? 'IF' : 'AND'}
            </span>
            
            <select id="module-select-${conditionId}" class="module-select flex-1 min-w-32 bg-white border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-edgelab-purple transition">
                <option value="">Select indicator...</option>
                ${this.buildModuleOptions()}
            </select>
            
            <div id="config-fields-${conditionId}" class="flex-1 min-w-64"></div>
            
            <button type="button" onclick="strategyBuilder.removeCondition(${conditionId})" class="text-red-500 hover:text-red-700 p-2 transition">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
            </button>
        `;
        
        container.appendChild(conditionCard);
        
        // Add event listener for module selection
        const select = document.getElementById(`module-select-${conditionId}`);
        select.addEventListener('change', (e) => {
            this.onModuleSelected(conditionId, e.target.value);
        });
        
        this.conditions.push({
            id: conditionId,
            module: null,
            config: {}
        });
        
        this.updateRemoveButtons();
    }
    
    buildModuleOptions() {
        if (!this.modules) return '';
        
        const categoryLabels = {
            'indicator': '📊 Indicators',
            'ict': '🎯 ICT Concepts',
            'mtf': '📈 Multi-Timeframe',
            'position_sizing': '💰 Position Sizing'
        };
        
        let html = '';
        
        for (const [category, moduleList] of Object.entries(this.modules)) {
            if (moduleList.length === 0) continue;
            
            html += `<optgroup label="${categoryLabels[category] || category}">`;
            
            for (const module of moduleList) {
                html += `<option value="${category}/${module.id}">${module.name}</option>`;
            }
            
            html += '</optgroup>';
        }
        
        return html;
    }
    
    async onModuleSelected(conditionId, moduleKey) {
        if (!moduleKey) {
            // Clear config fields
            document.getElementById(`config-fields-${conditionId}`).innerHTML = '';
            return;
        }
        
        console.log(`[StrategyBuilder] Module selected: ${moduleKey}`);
        
        // Parse module key (e.g., "indicator/rsi")
        const [category, moduleId] = moduleKey.split('/');
        
        // Find module in loaded data
        const module = this.modules[category].find(m => m.id === moduleId);
        
        if (!module) {
            console.error(`[StrategyBuilder] Module not found: ${moduleKey}`);
            return;
        }
        
        // Update condition
        const condition = this.conditions.find(c => c.id === conditionId);
        condition.module = moduleKey;
        condition.schema = module.schema;
        
        // Build config fields
        this.buildConfigFields(conditionId, module);
    }
    
    buildConfigFields(conditionId, module) {
        const container = document.getElementById(`config-fields-${conditionId}`);
        
        if (!module.schema || !module.schema.fields) {
            container.innerHTML = '<span class="text-gray-500 text-sm">No configuration needed</span>';
            return;
        }
        
        let html = '<div class="flex flex-wrap gap-3">';
        
        for (const field of module.schema.fields) {
            html += this.buildField(conditionId, field);
        }
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    buildField(conditionId, field) {
        const fieldId = `field-${conditionId}-${field.name}`;
        
        let inputHtml = '';
        
        switch (field.type) {
            case 'number':
                inputHtml = `
                    <input 
                        type="number" 
                        id="${fieldId}"
                        name="${field.name}"
                        value="${field.default || 0}"
                        min="${field.min || ''}"
                        max="${field.max || ''}"
                        step="${field.step || 'any'}"
                        class="w-full bg-white border border-gray-300 rounded px-2 py-1 text-sm"
                    >
                `;
                break;
                
            case 'select':
                inputHtml = `
                    <select id="${fieldId}" name="${field.name}" class="w-full bg-white border border-gray-300 rounded px-2 py-1 text-sm">
                        ${field.options.map(opt => 
                            `<option value="${opt}" ${opt === field.default ? 'selected' : ''}>${opt}</option>`
                        ).join('')}
                    </select>
                `;
                break;
                
            case 'text':
                inputHtml = `
                    <input 
                        type="text" 
                        id="${fieldId}"
                        name="${field.name}"
                        value="${field.default || ''}"
                        class="w-full bg-white border border-gray-300 rounded px-2 py-1 text-sm"
                    >
                `;
                break;
                
            default:
                inputHtml = `<p>Unsupported field type: ${field.type}</p>`;
        }
        
        return `
            <div class="flex-1 min-w-24">
                <label class="block text-xs font-semibold text-gray-600 mb-1">${field.label || field.name}</label>
                ${inputHtml}
                ${field.help ? `<small class="block text-xs text-gray-500 mt-1">${field.help}</small>` : ''}
            </div>
        `;
    }
    
    removeCondition(conditionId) {
        console.log(`[StrategyBuilder] Removing condition #${conditionId}`);
        
        // Remove from DOM
        const element = document.getElementById(`condition-${conditionId}`);
        if (element) {
            element.remove();
        }
        
        // Remove from conditions array
        this.conditions = this.conditions.filter(c => c.id !== conditionId);
        
        // Show empty state if no conditions
        if (this.conditions.length === 0) {
            const emptyState = document.getElementById('empty-state');
            if (emptyState) {
                emptyState.style.display = 'block';
            }
        }
        
        this.updateLabels();
        this.updateRemoveButtons();
    }
    
    updateLabels() {
        const rows = document.querySelectorAll('.condition-row');
        rows.forEach((row, index) => {
            const label = row.querySelector('span');
            if (index === 0) {
                label.textContent = 'IF';
                label.className = 'font-bold w-8 text-edgelab-blue';
                row.className = 'condition-row flex flex-wrap items-center gap-3 p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200';
            } else {
                label.textContent = 'AND';
                label.className = 'font-bold w-8 text-edgelab-purple';
                row.className = 'condition-row flex flex-wrap items-center gap-3 p-5 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border-2 border-purple-200';
            }
        });
    }
    
    updateRemoveButtons() {
        const rows = document.querySelectorAll('.condition-row');
        rows.forEach(row => {
            const btn = row.querySelector('button[onclick*="removeCondition"]');
            if (rows.length === 1) {
                btn.disabled = true;
                btn.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                btn.disabled = false;
                btn.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        });
    }
    
    collectStrategyData() {
        const strategy = {
            symbol: document.getElementById('symbol').value,
            direction: document.querySelector('input[name="direction"]:checked').value,
            timeframe: document.getElementById('timeframe').value,
            period: document.getElementById('period').value,
            session: document.getElementById('session').value || '',
            tp_r: parseFloat(document.getElementById('tp_r').value),
            sl_r: parseFloat(document.getElementById('sl_r').value),
            conditions: []
        };
        
        // Collect each condition's config
        for (const condition of this.conditions) {
            if (!condition.module) continue;
            
            const [category, moduleId] = condition.module.split('/');
            const config = {};
            const fields = condition.schema?.fields || [];
            
            for (const field of fields) {
                const fieldId = `field-${condition.id}-${field.name}`;
                const element = document.getElementById(fieldId);
                
                if (element) {
                    config[field.name] = element.type === 'number' 
                        ? parseFloat(element.value) 
                        : element.value;
                }
            }
            
            strategy.conditions.push({
                category: category,
                module: moduleId,
                config: config
            });
        }
        
        return strategy;
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        console.log('[StrategyBuilder] Submitting strategy...');
        
        if (this.conditions.length === 0) {
            alert('Please add at least one condition');
            return;
        }
        
        const strategy = this.collectStrategyData();
        console.log('[StrategyBuilder] Strategy data:', strategy);
        
        const submitBtn = document.getElementById('submitBtn');
        const originalText = submitBtn.innerHTML;
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-6 w-6 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Running Backtest...';
        
        try {
            const response = await fetch('/run-backtest-v2', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(strategy)
            });
            
            if (response.ok) {
                // Response is HTML results page, replace entire document
                const html = await response.text();
                document.open();
                document.write(html);
                document.close();
            } else {
                // Error response - parse JSON
                const result = await response.json();
                console.error('[StrategyBuilder] Backtest failed:', result.error);
                alert('Backtest failed: ' + result.error);
            }
        } catch (error) {
            console.error('[StrategyBuilder] Request failed:', error);
            alert('Failed to run backtest. Please try again.');
        } finally {
            // Restore button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }
}

// Initialize when DOM ready
let strategyBuilder;

document.addEventListener('DOMContentLoaded', () => {
    console.log('[EdgeLab] Initializing Strategy Builder...');
    strategyBuilder = new StrategyBuilder();
});