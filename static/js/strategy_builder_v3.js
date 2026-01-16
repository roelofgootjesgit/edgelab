/* =============================================
   STRATEGY BUILDER V3 - JavaScript
   ============================================= */

// Application State
const appState = {
    marketContext: null,
    intent: null, // 'clear' or 'explore'
    flow: null, // 'A' or 'B'
    rules: [],
    idea: null,
    logic: {
        primaryCondition: null,
        confirmation: null,
        filter: null
    },
    exit: {
        stopLoss: 1,
        takeProfit: 2
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Strategy Builder V3 initialized');
    initializeMarketContext();
});

// ===== STAP 0: MARKET CONTEXT =====
function initializeMarketContext() {
    const form = document.getElementById('marketContextForm');
    const emptyState = document.getElementById('step0EmptyState');
    const stickyBar = document.getElementById('stickyContextBar');
    
    // Check if context already exists
    if (appState.marketContext) {
        showMarketContextConfirmed();
    } else {
        // Show form
        emptyState.style.display = 'none';
        form.style.display = 'block';
    }
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        handleMarketContextSubmit();
    });
    
    // Handle edit link
    const editLink = document.getElementById('contextBarEdit');
    if (editLink) {
        editLink.addEventListener('click', function(e) {
            e.preventDefault();
            showMarketContextForm();
        });
    }
}

function handleMarketContextSubmit() {
    const market = document.getElementById('marketSelect').value;
    const timeframe = document.getElementById('timeframeSelect').value;
    const session = document.getElementById('sessionSelect').value;
    const direction = document.getElementById('directionSelect').value;
    const testPeriod = document.getElementById('testPeriodSelect').value;
    
    // Validate required fields
    if (!market || !timeframe || !direction || !testPeriod) {
        alert('Please fill in all required fields.');
        return;
    }
    
    // Save to state
    appState.marketContext = {
        market,
        timeframe,
        session: session || 'All',
        direction,
        testPeriod
    };
    
    showMarketContextConfirmed();
    // Move to next step
    setTimeout(() => {
        showIntentSelection();
    }, 300);
}

function showMarketContextConfirmed() {
    const form = document.getElementById('marketContextForm');
    const emptyState = document.getElementById('step0EmptyState');
    const stickyBar = document.getElementById('stickyContextBar');
    const contextText = document.getElementById('contextBarText');
    
    // Hide form
    form.style.display = 'none';
    emptyState.style.display = 'none';
    
    // Show sticky bar
    const ctx = appState.marketContext;
    const sessionText = ctx.session && ctx.session !== 'All' ? ctx.session : '';
    contextText.textContent = `${ctx.market} · ${ctx.timeframe}${sessionText ? ' · ' + sessionText : ''} · ${ctx.direction} · ${ctx.testPeriod}`;
    stickyBar.style.display = 'block';
}

function showMarketContextForm() {
    const form = document.getElementById('marketContextForm');
    const stickyBar = document.getElementById('stickyContextBar');
    
    stickyBar.style.display = 'none';
    form.style.display = 'block';
    
    // Populate form with existing values
    if (appState.marketContext) {
        document.getElementById('marketSelect').value = appState.marketContext.market;
        document.getElementById('timeframeSelect').value = appState.marketContext.timeframe;
        document.getElementById('sessionSelect').value = appState.marketContext.session;
        document.getElementById('directionSelect').value = appState.marketContext.direction;
        document.getElementById('testPeriodSelect').value = appState.marketContext.testPeriod;
    }
}

// ===== STAP 1: INTENT SELECTION =====
function showIntentSelection() {
    const step1 = document.getElementById('step1');
    const emptyState = document.getElementById('step1EmptyState');
    const intentOptions = document.getElementById('intentOptions');
    
    // Show step 1
    step1.style.display = 'block';
    
    // Hide empty state, show options
    emptyState.style.display = 'none';
    intentOptions.style.display = 'block';
    
    // Handle intent selection
    const intentRadios = document.querySelectorAll('input[name="intent"]');
    intentRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                handleIntentSelection(this.value);
            }
        });
    });
}

function handleIntentSelection(intent) {
    appState.intent = intent;
    appState.flow = intent === 'clear' ? 'A' : 'B';
    
    // Move to appropriate flow
    setTimeout(() => {
        if (intent === 'clear') {
            showFlowA();
        } else {
            showFlowB();
        }
    }, 300);
}

// ===== FLOW A: CLEAR STRATEGY =====
function showFlowA() {
    const step2A = document.getElementById('step2A');
    step2A.style.display = 'block';
    
    // Scroll to step
    step2A.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Initialize rules UI
    initializeRulesUI();
    
    // Show exit & risk after rules are added (or allow manual progression)
    // For now, we'll show it after at least one rule is added
    const checkAndShowExit = () => {
        if (appState.rules.length > 0) {
            setTimeout(() => {
                showExitRisk();
            }, 500);
        }
    };
    
    // Monitor rules changes
    const originalAddRule = addRule;
    addRule = function() {
        originalAddRule();
        checkAndShowExit();
    };
}

function initializeRulesUI() {
    const emptyState = document.getElementById('step2AEmptyState');
    const rulesContainer = document.getElementById('rulesContainer');
    const addFirstRuleBtn = document.getElementById('addFirstRuleBtn');
    const addRuleBtn = document.getElementById('addRuleBtn');
    
    // Show empty state initially
    emptyState.style.display = 'block';
    rulesContainer.style.display = 'none';
    
    // Handle add first rule
    addFirstRuleBtn.addEventListener('click', function() {
        addRule();
    });
    
    // Handle add rule button
    if (addRuleBtn) {
        addRuleBtn.addEventListener('click', function() {
            addRule();
        });
    }
    
    updateRuleCounter();
}

function addRule() {
    const ruleNumber = appState.rules.length + 1;
    
    // UX Rule: Never more than 4 rules visible
    if (appState.rules.length >= 4) {
        return;
    }
    
    // Create new rule object
    const newRule = {
        id: Date.now(),
        number: ruleNumber,
        description: ''
    };
    
    appState.rules.push(newRule);
    
    // Update UI
    renderRules();
    updateRuleCounter();
    updateRuleMicrocopy();
    
    // Hide empty state, show rules container
    const emptyState = document.getElementById('step2AEmptyState');
    const rulesContainer = document.getElementById('rulesContainer');
    const addRuleBtn = document.getElementById('addRuleBtn');
    
    emptyState.style.display = 'none';
    rulesContainer.style.display = 'block';
    
    if (appState.rules.length < 4) {
        addRuleBtn.style.display = 'inline-flex';
    }
}

function removeRule(ruleId) {
    appState.rules = appState.rules.filter(r => r.id !== ruleId);
    
    // Renumber rules
    appState.rules.forEach((rule, index) => {
        rule.number = index + 1;
    });
    
    renderRules();
    updateRuleCounter();
    updateRuleMicrocopy();
    
    // Show empty state if no rules
    if (appState.rules.length === 0) {
        const emptyState = document.getElementById('step2AEmptyState');
        const rulesContainer = document.getElementById('rulesContainer');
        emptyState.style.display = 'block';
        rulesContainer.style.display = 'none';
    }
}

function renderRules() {
    const rulesList = document.getElementById('rulesList');
    const addRuleBtn = document.getElementById('addRuleBtn');
    
    rulesList.innerHTML = '';
    
    appState.rules.forEach(rule => {
        const ruleElement = document.createElement('div');
        ruleElement.className = 'rule-item';
        ruleElement.innerHTML = `
            <div class="rule-item-header">
                <span class="rule-item-number">Rule ${rule.number}</span>
                <button class="rule-item-remove" onclick="removeRule(${rule.id})">×</button>
            </div>
            <input type="text" 
                   class="form-input" 
                   placeholder="Describe this rule exactly as you would trade it..."
                   value="${rule.description}"
                   onchange="updateRuleDescription(${rule.id}, this.value)">
        `;
        rulesList.appendChild(ruleElement);
    });
    
    // Show/hide add button
    if (appState.rules.length < 4) {
        addRuleBtn.style.display = 'inline-flex';
    } else {
        addRuleBtn.style.display = 'none';
    }
}

function updateRuleDescription(ruleId, description) {
    const rule = appState.rules.find(r => r.id === ruleId);
    if (rule) {
        rule.description = description;
    }
}

function updateRuleCounter() {
    const counter = document.getElementById('ruleCount');
    if (counter) {
        counter.textContent = appState.rules.length;
    }
}

function updateRuleMicrocopy() {
    const microcopy = document.getElementById('ruleMicrocopy');
    if (!microcopy) return;
    
    const count = appState.rules.length;
    
    if (count === 0) {
        microcopy.textContent = 'Most robust strategies use 1–3 rules.';
    } else if (count === 1) {
        microcopy.textContent = 'Most robust strategies use 1–3 rules.';
    } else if (count === 2) {
        microcopy.textContent = 'Additional rules can improve precision, but may reduce robustness.';
    } else if (count === 3) {
        microcopy.textContent = 'Additional rules can improve precision, but may reduce robustness.';
    } else if (count === 4) {
        microcopy.textContent = 'Four rules is usually the practical limit.';
    }
}

// Make functions globally available
window.removeRule = removeRule;
window.updateRuleDescription = updateRuleDescription;

// ===== FLOW B: EXPLORE IDEA =====
function showFlowB() {
    const step2B = document.getElementById('step2B');
    step2B.style.display = 'block';
    
    // Initialize idea selection UI
    initializeIdeaSelection();
}

function initializeIdeaSelection() {
    const emptyState = document.getElementById('step2BEmptyState');
    const ideaCards = document.getElementById('ideaCards');
    
    // Show empty state initially
    emptyState.style.display = 'block';
    ideaCards.style.display = 'grid';
    
    // Handle idea card clicks
    const cards = document.querySelectorAll('.idea-card');
    cards.forEach(card => {
        card.addEventListener('click', function() {
            const idea = this.dataset.idea;
            selectIdea(idea);
        });
    });
}

function selectIdea(idea) {
    appState.idea = idea;
    
    // Update UI
    const cards = document.querySelectorAll('.idea-card');
    cards.forEach(card => {
        card.classList.remove('selected');
        if (card.dataset.idea === idea) {
            card.classList.add('selected');
        }
    });
    
    // Show chip
    const chip = document.getElementById('ideaChip');
    const chipText = document.getElementById('ideaChipText');
    const emptyState = document.getElementById('step2BEmptyState');
    
    emptyState.style.display = 'none';
    chip.style.display = 'inline-flex';
    
    // Format idea name for display
    const ideaNames = {
        'trend-continuation': 'Trend continuation',
        'mean-reversion': 'Mean reversion',
        'breakout': 'Breakout',
        'liquidity-sweep': 'Liquidity sweep',
        'momentum-push': 'Momentum push'
    };
    
    chipText.textContent = ideaNames[idea] || idea;
    
    // Move to next step
    setTimeout(() => {
        showFlowBLogic();
    }, 500);
}

function showFlowBLogic() {
    const step3B = document.getElementById('step3B');
    step3B.style.display = 'block';
    
    // Scroll to step
    step3B.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Initialize logic UI
    initializeLogicUI();
    
    // Show exit & risk after primary condition is added
    const originalAddPrimary = addPrimaryCondition;
    addPrimaryCondition = function() {
        originalAddPrimary();
        setTimeout(() => {
            showExitRisk();
        }, 500);
    };
}

function initializeLogicUI() {
    // Primary condition
    const addPrimaryBtn = document.getElementById('addPrimaryConditionBtn');
    if (addPrimaryBtn) {
        addPrimaryBtn.addEventListener('click', function() {
            addPrimaryCondition();
        });
    }
    
    // Confirmation
    const addConfirmationBtn = document.getElementById('addConfirmationBtn');
    if (addConfirmationBtn) {
        addConfirmationBtn.addEventListener('click', function() {
            addConfirmation();
        });
    }
    
    // Filter
    const addFilterBtn = document.getElementById('addFilterBtn');
    if (addFilterBtn) {
        addFilterBtn.addEventListener('click', function() {
            addFilter();
        });
    }
}

function addPrimaryCondition() {
    const emptyState = document.getElementById('primaryConditionEmpty');
    const content = document.getElementById('primaryConditionContent');
    const btn = document.getElementById('addPrimaryConditionBtn');
    
    // For now, just show a placeholder
    // In full implementation, this would open a condition builder
    content.innerHTML = `
        <div class="logic-item">
            <p class="logic-item-text">Primary condition will be defined here.</p>
            <button class="btn-secondary" onclick="removePrimaryCondition()">Remove</button>
        </div>
    `;
    
    emptyState.style.display = 'none';
    content.style.display = 'block';
    btn.style.display = 'none';
    
    appState.logic.primaryCondition = { type: 'primary' };
}

function removePrimaryCondition() {
    const emptyState = document.getElementById('primaryConditionEmpty');
    const content = document.getElementById('primaryConditionContent');
    const btn = document.getElementById('addPrimaryConditionBtn');
    
    emptyState.style.display = 'block';
    content.style.display = 'none';
    btn.style.display = 'inline-flex';
    
    appState.logic.primaryCondition = null;
}

function addConfirmation() {
    const content = document.getElementById('confirmationContent');
    const btn = document.getElementById('addConfirmationBtn');
    
    content.innerHTML = `
        <div class="logic-item">
            <p class="logic-item-text">Confirmation will be defined here.</p>
            <button class="btn-secondary" onclick="removeConfirmation()">Remove</button>
        </div>
    `;
    
    content.style.display = 'block';
    btn.style.display = 'none';
    
    appState.logic.confirmation = { type: 'confirmation' };
}

function removeConfirmation() {
    const content = document.getElementById('confirmationContent');
    const btn = document.getElementById('addConfirmationBtn');
    
    content.style.display = 'none';
    btn.style.display = 'inline-flex';
    
    appState.logic.confirmation = null;
}

function addFilter() {
    const content = document.getElementById('filterContent');
    const btn = document.getElementById('addFilterBtn');
    
    content.innerHTML = `
        <div class="logic-item">
            <p class="logic-item-text">Filter will be defined here.</p>
            <button class="btn-secondary" onclick="removeFilter()">Remove</button>
        </div>
    `;
    
    content.style.display = 'block';
    btn.style.display = 'none';
    
    appState.logic.filter = { type: 'filter' };
}

function removeFilter() {
    const content = document.getElementById('filterContent');
    const btn = document.getElementById('addFilterBtn');
    
    content.style.display = 'none';
    btn.style.display = 'inline-flex';
    
    appState.logic.filter = null;
}

// Make functions globally available
window.removePrimaryCondition = removePrimaryCondition;
window.removeConfirmation = removeConfirmation;
window.removeFilter = removeFilter;

// ===== STAP 4: EXIT & RISK =====
function showExitRisk() {
    const step4 = document.getElementById('step4');
    if (step4 && step4.style.display === 'none') {
        step4.style.display = 'block';
        step4.scrollIntoView({ behavior: 'smooth', block: 'start' });
        initializeExitRisk();
        
        // Show review & run after a short delay
        setTimeout(() => {
            showReviewRun();
        }, 500);
    }
}

function initializeExitRisk() {
    const emptyState = document.getElementById('step4EmptyState');
    const form = document.getElementById('exitRiskForm');
    const stopLossInput = document.getElementById('stopLossInput');
    const takeProfitInput = document.getElementById('takeProfitInput');
    
    // Show form with defaults
    emptyState.style.display = 'none';
    form.style.display = 'block';
    
    // Update risk-reward badge
    updateRiskRewardBadge();
    
    // Handle input changes
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
}

function updateRiskRewardBadge() {
    const badge = document.getElementById('riskRewardRatio');
    if (badge) {
        const ratio = (appState.exit.takeProfit / appState.exit.stopLoss).toFixed(1);
        badge.textContent = ratio;
    }
}

// ===== STAP 5: REVIEW & RUN =====
function showReviewRun() {
    const step5 = document.getElementById('step5');
    if (step5 && step5.style.display === 'none') {
        step5.style.display = 'block';
        step5.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Generate and display summary
        generateSummary();
        
        // Handle run backtest button (only add listener once)
        const runBtn = document.getElementById('runBacktestBtn');
        if (runBtn && !runBtn.dataset.listenerAdded) {
            runBtn.addEventListener('click', function() {
                runBacktest();
            });
            runBtn.dataset.listenerAdded = 'true';
        }
    }
}

function generateSummary() {
    const summarySentence = document.getElementById('summarySentence');
    if (!summarySentence) return;
    
    const ctx = appState.marketContext;
    if (!ctx) return;
    
    let summary = '';
    
    if (appState.flow === 'A') {
        // Flow A: Clear Strategy
        const rulesCount = appState.rules.length;
        const sessionText = ctx.session && ctx.session !== 'All' ? ` during ${ctx.session}` : '';
        const rrRatio = (appState.exit.takeProfit / appState.exit.stopLoss).toFixed(1);
        
        summary = `This strategy tests an existing setup on ${ctx.market} ${ctx.timeframe}${sessionText} using ${rulesCount} rule${rulesCount !== 1 ? 's' : ''} and a 1:${rrRatio} risk–reward.`;
    } else {
        // Flow B: Explore Idea
        const ideaNames = {
            'trend-continuation': 'trend continuation',
            'mean-reversion': 'mean reversion',
            'breakout': 'breakout',
            'liquidity-sweep': 'liquidity sweep',
            'momentum-push': 'momentum push'
        };
        const ideaName = ideaNames[appState.idea] || appState.idea;
        const sessionText = ctx.session && ctx.session !== 'All' ? ` during ${ctx.session}` : '';
        const hasPrimary = appState.logic.primaryCondition !== null;
        const rrRatio = (appState.exit.takeProfit / appState.exit.stopLoss).toFixed(1);
        
        summary = `This strategy tests a ${ideaName} idea on ${ctx.market} ${ctx.timeframe}${sessionText}${hasPrimary ? ', confirmed by defined conditions' : ''} and exited at ${appState.exit.takeProfit}R / ${appState.exit.stopLoss}R.`;
    }
    
    summarySentence.textContent = summary;
}

// ===== UX RULES VALIDATION =====
function validateUXRules() {
    const violations = [];
    
    // Rule 1: Never more than 4 rules
    if (appState.rules.length > 4) {
        violations.push('Maximum 4 rules exceeded');
    }
    
    // Rule 2: Only R-based exits (no trailing stops, breakeven, etc.)
    // This is enforced by UI - only R-based inputs are available
    
    // Rule 3: Flow order must be: context → intent → rules
    if (!appState.marketContext) {
        violations.push('Market context must be set first');
    }
    if (!appState.intent) {
        violations.push('Intent must be selected after context');
    }
    
    // Rule 4: All empty states must be present (checked in HTML)
    // Rule 5: All microcopy must be present (checked in HTML)
    
    return violations;
}

function runBacktest() {
    // Validate UX rules
    const violations = validateUXRules();
    if (violations.length > 0) {
        console.warn('UX Rule violations:', violations);
    }
    
    // Validate that all required fields are filled
    if (!appState.marketContext) {
        alert('Please set the market context first.');
        return;
    }
    
    if (appState.flow === 'A' && appState.rules.length === 0) {
        alert('Please add at least one rule.');
        return;
    }
    
    if (appState.flow === 'B' && !appState.idea) {
        alert('Please select a strategy idea.');
        return;
    }
    
    if (appState.flow === 'B' && !appState.logic.primaryCondition) {
        alert('Please define a primary condition.');
        return;
    }
    
    // Prepare data for backend
    const backtestData = {
        marketContext: appState.marketContext,
        flow: appState.flow,
        intent: appState.intent,
        rules: appState.rules,
        idea: appState.idea,
        logic: appState.logic,
        exit: appState.exit
    };
    
    console.log('Running backtest with data:', backtestData);
    
    // Show loading state
    const runBtn = document.getElementById('runBacktestBtn');
    const originalText = runBtn.textContent;
    runBtn.disabled = true;
    runBtn.textContent = 'Running backtest...';
    
    // Send to backend
    fetch('/run-backtest-v3', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(backtestData)
    })
    .then(response => {
        if (response.ok) {
            // If response is HTML (results page), replace current page
            return response.text().then(html => {
                document.open();
                document.write(html);
                document.close();
            });
        } else {
            // Handle error response
            return response.json().then(data => {
                throw new Error(data.error || 'Backtest failed');
            });
        }
    })
    .catch(error => {
        console.error('Backtest error:', error);
        alert('Backtest failed: ' + error.message);
        runBtn.disabled = false;
        runBtn.textContent = originalText;
    });
}

