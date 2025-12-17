/**
 * QuantMetrics Indicator Test Suite
 * ==================================
 * Automated testing for all 66 indicators in browser console
 * 
 * Usage:
 * 1. Open http://localhost:5000/simulator-v2
 * 2. Open browser console (F12)
 * 3. Copy-paste this entire script
 * 4. Run: await testAllIndicators()
 * 
 * Author: QuantMetrics Development Team
 * Date: December 17, 2025
 */

class IndicatorTestSuite {
    constructor() {
        this.results = {
            total: 0,
            passed: 0,
            failed: 0,
            errors: [],
            timings: []
        };
        this.categories = [];
        this.indicators = {};
    }

    /**
     * Initialize - fetch all modules from API
     */
    async initialize() {
        console.log('🔄 Fetching indicator modules...');
        
        try {
            const response = await fetch('/api/modules');
            const data = await response.json();
            
            if (!data.success) {
                throw new Error('API returned failure');
            }
            
            this.indicators = data.modules;
            this.categories = Object.keys(this.indicators);
            
            // Count total indicators
            this.results.total = Object.values(this.indicators)
                .reduce((sum, mods) => sum + mods.length, 0);
            
            console.log(`✅ Loaded ${this.results.total} indicators across ${this.categories.length} categories`);
            console.log(`📊 Categories: ${this.categories.join(', ')}`);
            
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize:', error);
            return false;
        }
    }

    /**
     * Test a single indicator
     */
    async testIndicator(category, indicator, config) {
        const testName = `${category}/${indicator.id}`;
        console.log(`\n🧪 Testing: ${testName}`);
        
        const startTime = performance.now();
        
        try {
            // Build test strategy
            const strategy = {
                symbol: 'XAUUSD',
                timeframe: '15m',
                direction: 'LONG',
                period: '2mo',
                session: '',
                tp_r: 2.0,
                sl_r: 1.0,
                conditions: [{
                    category: category,
                    module: indicator.id,
                    config: config
                }]
            };
            
            // Submit backtest
            const response = await fetch('/run-backtest-v2', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(strategy)
            });
            
            const elapsed = performance.now() - startTime;
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Check if we got HTML (success) or JSON (error)
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.error || 'Unknown error');
                }
            }
            
            // If we got HTML, backtest succeeded
            const html = await response.text();
            
            if (html.includes('Analysis Results') || html.includes('Win Rate')) {
                console.log(`✅ PASSED in ${elapsed.toFixed(0)}ms`);
                this.results.passed++;
                this.results.timings.push({
                    indicator: testName,
                    time: elapsed
                });
                return { success: true, time: elapsed };
            } else {
                throw new Error('Response missing expected content');
            }
            
        } catch (error) {
            const elapsed = performance.now() - startTime;
            console.error(`❌ FAILED in ${elapsed.toFixed(0)}ms:`, error.message);
            
            this.results.failed++;
            this.results.errors.push({
                indicator: testName,
                error: error.message,
                time: elapsed
            });
            
            return { success: false, error: error.message, time: elapsed };
        }
    }

    /**
     * Get default config for an indicator
     */
    getDefaultConfig(indicator) {
        const config = {};
        
        if (!indicator.config_schema || !indicator.config_schema.properties) {
            return config;
        }
        
        // Use default values from schema
        for (const [key, prop] of Object.entries(indicator.config_schema.properties)) {
            if (prop.default !== undefined) {
                config[key] = prop.default;
            } else if (prop.type === 'number') {
                config[key] = prop.minimum || 14;
            } else if (prop.type === 'string') {
                // Use first enum option or default string
                config[key] = prop.enum ? prop.enum[0] : 'default';
            }
        }
        
        return config;
    }

    /**
     * Test all indicators in a category
     */
    async testCategory(category, delay = 2000) {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`📦 Testing Category: ${category}`);
        console.log(`${'='.repeat(60)}`);
        
        const modules = this.indicators[category];
        
        if (!modules || modules.length === 0) {
            console.log(`⚠️  No modules in category: ${category}`);
            return;
        }
        
        console.log(`Found ${modules.length} indicators`);
        
        for (const indicator of modules) {
            // Get default config
            const config = this.getDefaultConfig(indicator);
            
            // Test indicator
            await this.testIndicator(category, indicator, config);
            
            // Delay between tests to avoid overwhelming server
            if (delay > 0) {
                await this.sleep(delay);
            }
        }
    }

    /**
     * Test all indicators across all categories
     */
    async testAll(delay = 2000) {
        console.log('\n' + '='.repeat(60));
        console.log('🚀 STARTING FULL TEST SUITE');
        console.log('='.repeat(60));
        console.log(`Total indicators to test: ${this.results.total}`);
        console.log(`Delay between tests: ${delay}ms`);
        console.log('='.repeat(60));
        
        const overallStart = performance.now();
        
        for (const category of this.categories) {
            await this.testCategory(category, delay);
        }
        
        const overallTime = performance.now() - overallStart;
        
        // Generate report
        this.generateReport(overallTime);
    }

    /**
     * Generate final test report
     */
    generateReport(totalTime) {
        console.log('\n' + '='.repeat(60));
        console.log('📊 TEST REPORT');
        console.log('='.repeat(60));
        console.log(`Total Tests: ${this.results.total}`);
        console.log(`✅ Passed: ${this.results.passed} (${(this.results.passed/this.results.total*100).toFixed(1)}%)`);
        console.log(`❌ Failed: ${this.results.failed} (${(this.results.failed/this.results.total*100).toFixed(1)}%)`);
        console.log(`⏱️  Total Time: ${(totalTime/1000).toFixed(1)}s`);
        console.log(`⚡ Avg Time: ${(totalTime/this.results.total).toFixed(0)}ms per test`);
        
        if (this.results.failed > 0) {
            console.log('\n❌ FAILED TESTS:');
            console.log('='.repeat(60));
            this.results.errors.forEach((err, i) => {
                console.log(`${i+1}. ${err.indicator}`);
                console.log(`   Error: ${err.error}`);
                console.log(`   Time: ${err.time.toFixed(0)}ms\n`);
            });
        }
        
        // Performance analysis
        if (this.results.timings.length > 0) {
            const times = this.results.timings.map(t => t.time);
            const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
            const minTime = Math.min(...times);
            const maxTime = Math.max(...times);
            
            console.log('\n⚡ PERFORMANCE STATS:');
            console.log('='.repeat(60));
            console.log(`Average: ${avgTime.toFixed(0)}ms`);
            console.log(`Fastest: ${minTime.toFixed(0)}ms`);
            console.log(`Slowest: ${maxTime.toFixed(0)}ms`);
            
            // Find slowest indicators
            const slowest = this.results.timings
                .sort((a, b) => b.time - a.time)
                .slice(0, 5);
            
            console.log('\n🐌 Slowest Indicators:');
            slowest.forEach((item, i) => {
                console.log(`${i+1}. ${item.indicator}: ${item.time.toFixed(0)}ms`);
            });
        }
        
        console.log('\n' + '='.repeat(60));
        
        // Export results as JSON
        const exportData = {
            timestamp: new Date().toISOString(),
            summary: {
                total: this.results.total,
                passed: this.results.passed,
                failed: this.results.failed,
                success_rate: (this.results.passed/this.results.total*100).toFixed(1) + '%',
                total_time_seconds: (totalTime/1000).toFixed(1)
            },
            errors: this.results.errors,
            timings: this.results.timings
        };
        
        console.log('\n📥 Test results JSON:');
        console.log(JSON.stringify(exportData, null, 2));
        
        // Store in window for easy access
        window.testResults = exportData;
        console.log('\n💾 Results saved to: window.testResults');
    }

    /**
     * Sleep utility
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Quick test - single indicator
     */
    async quickTest(category, indicatorId) {
        const indicator = this.indicators[category]?.find(m => m.id === indicatorId);
        
        if (!indicator) {
            console.error(`❌ Indicator not found: ${category}/${indicatorId}`);
            return false;
        }
        
        const config = this.getDefaultConfig(indicator);
        const result = await this.testIndicator(category, indicator, config);
        
        return result.success;
    }

    /**
     * Test specific categories only
     */
    async testCategories(categoryList, delay = 2000) {
        console.log(`\n🎯 Testing specific categories: ${categoryList.join(', ')}`);
        
        for (const category of categoryList) {
            if (!this.categories.includes(category)) {
                console.warn(`⚠️  Category not found: ${category}`);
                continue;
            }
            
            await this.testCategory(category, delay);
        }
        
        this.generateReport(0);
    }
}

// ============================================================
// QUICK START FUNCTIONS
// ============================================================

/**
 * Initialize and test all indicators
 */
async function testAllIndicators(delay = 2000) {
    const suite = new IndicatorTestSuite();
    
    const initialized = await suite.initialize();
    if (!initialized) {
        console.error('❌ Failed to initialize test suite');
        return null;
    }
    
    await suite.testAll(delay);
    
    return suite;
}

/**
 * Test specific categories
 */
async function testCategories(categories, delay = 2000) {
    const suite = new IndicatorTestSuite();
    
    const initialized = await suite.initialize();
    if (!initialized) {
        console.error('❌ Failed to initialize test suite');
        return null;
    }
    
    await suite.testCategories(categories, delay);
    
    return suite;
}

/**
 * Quick test single indicator
 */
async function testOne(category, indicatorId) {
    const suite = new IndicatorTestSuite();
    
    const initialized = await suite.initialize();
    if (!initialized) {
        console.error('❌ Failed to initialize test suite');
        return false;
    }
    
    return await suite.quickTest(category, indicatorId);
}

// ============================================================
// USAGE EXAMPLES
// ============================================================

console.log(`
╔════════════════════════════════════════════════════════════╗
║     QuantMetrics Indicator Test Suite v1.0                ║
╚════════════════════════════════════════════════════════════╝

📚 USAGE:

1️⃣  Test ALL indicators (66 indicators, ~220 seconds with 2s delay):
   await testAllIndicators()

2️⃣  Test specific categories:
   await testCategories(['trend', 'momentum'])

3️⃣  Quick test single indicator:
   await testOne('trend', 'rsi')

4️⃣  Faster testing (1s delay):
   await testAllIndicators(1000)

5️⃣  Export results:
   console.log(JSON.stringify(window.testResults, null, 2))

⚙️  RECOMMENDED:
   - Start with quick test: await testOne('trend', 'rsi')
   - Then test categories: await testCategories(['trend'])
   - Finally full suite: await testAllIndicators()

🎯 Ready to start testing!
`);

// Export to window for easy access
window.IndicatorTestSuite = IndicatorTestSuite;
window.testAllIndicators = testAllIndicators;
window.testCategories = testCategories;
window.testOne = testOne;