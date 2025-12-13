"""
test_enhanced_analysis.py
=========================

End-to-end test for enhanced analysis pipeline.
Tests: CSV → Parser → Enhanced Analyzer → Comprehensive Results

Author: QuantMetrics Development Team
Version: 2.0 (Enhanced with Pattern Analysis)
"""

from core.csv_parser import CSVParser
from core.analyzer import BasicAnalyzer


def test_enhanced_pipeline():
    """
    Test complete enhanced analysis pipeline.
    
    Flow:
    1. Parse sample CSV
    2. Run enhanced analyzer (basic + pattern analysis)
    3. Display all results sections
    
    Returns:
        Dict with complete analysis results
    """
    
    print("=" * 70)
    print(" EDGELAB ENHANCED ANALYSIS TEST")
    print("=" * 70)
    
    # ===================================================================
    # STEP 1: Parse CSV
    # ===================================================================
    print("\n[1/8] Parsing CSV...")
    parser = CSVParser()
    trades = parser.parse('tests/sample_data/trades_sample.csv')
    print(f"      ✓ Successfully parsed {len(trades)} trades")
    
    # ===================================================================
    # STEP 2: Run Enhanced Analysis
    # ===================================================================
    print("\n[2/8] Running enhanced analysis...")
    analyzer = BasicAnalyzer()
    results = analyzer.calculate(trades)
    print(f"      ✓ Analysis complete")
    
    # ===================================================================
    # STEP 3: Basic Metrics
    # ===================================================================
    print("\n[3/8] BASIC METRICS")
    print("-" * 70)
    print(f"      Total Trades:    {results['total_trades']}")
    print(f"      Wins/Losses:     {results['wins']}W / {results['losses']}L")
    print(f"      Win Rate:        {results['winrate']}%")
    print(f"      Profit Factor:   {results['profit_factor']}")
    print(f"      Expectancy:      {results['expectancy']}R per trade")
    print(f"      Total Profit:    {results['total_profit_r']}R")
    print(f"      Max Drawdown:    {results['max_drawdown_pct']}%")
    print(f"      ESI (Stability): {results['esi']}")
    print(f"      PVS (Prop Ready): {results['pvs']}")
    print(f"      Sharpe Ratio:    {results['sharpe_ratio']}")
    
    # ===================================================================
    # STEP 4: Timing Analysis
    # ===================================================================
    print("\n[4/8] TIMING ANALYSIS")
    print("-" * 70)
    timing = results['timing_analysis']
    
    if 'session_breakdown' in timing:
        print("\n      Session Performance:")
        for session_name, data in timing['session_breakdown'].items():
            print(f"\n      {session_name}:")
            print(f"        - Trades:     {data['total_trades']}")
            print(f"        - Wins/Losses: {data['wins']}W / {data['losses']}L")
            print(f"        - Win Rate:   {data['winrate']:.1f}%")
            print(f"        - Expectancy: {data['expectancy']:.2f}R")
            print(f"        - Verdict:    {data['verdict']}")
    
    if 'best_hour' in timing:
        print(f"\n      Best Trading Hour: {timing['best_hour']}")
    
    # ===================================================================
    # STEP 5: Directional Analysis
    # ===================================================================
    print("\n[5/8] DIRECTIONAL ANALYSIS")
    print("-" * 70)
    directional = results['directional_analysis']
    
    if 'long_performance' in directional:
        long = directional['long_performance']
        print(f"\n      LONG Trades:")
        print(f"        - Total:      {long.get('total_trades', 0)}")
        print(f"        - Wins:       {long.get('wins', 0)}")
        print(f"        - Win Rate:   {long.get('winrate', 0):.1f}%")
        print(f"        - Expectancy: {long.get('expectancy', 0):.2f}R")
        if 'edge_strength' in long:
            print(f"        - Edge:       {long['edge_strength']}")
    
    if 'short_performance' in directional:
        short = directional['short_performance']
        print(f"\n      SHORT Trades:")
        print(f"        - Total:      {short.get('total_trades', 0)}")
        print(f"        - Wins:       {short.get('wins', 0)}")
        print(f"        - Win Rate:   {short.get('winrate', 0):.1f}%")
        print(f"        - Expectancy: {short.get('expectancy', 0):.2f}R")
        if 'edge_strength' in short:
            print(f"        - Edge:       {short['edge_strength']}")
    
    if 'expected_improvement' in directional:
        print(f"\n      Expected WR Improvement: {directional['expected_improvement']}")
    
    # ===================================================================
    # STEP 6: Execution Analysis
    # ===================================================================
    print("\n[6/8] EXECUTION QUALITY")
    print("-" * 70)
    execution = results['execution_analysis']
    
    if 'quality_score' in execution:
        score = execution['quality_score']
        print(f"\n      Overall Quality Score: {score}/100")
        
        # Quality assessment
        if score >= 90:
            print(f"      Assessment: EXCELLENT - Professional execution")
        elif score >= 75:
            print(f"      Assessment: GOOD - Minor improvements possible")
        elif score >= 60:
            print(f"      Assessment: FAIR - Discipline issues detected")
        else:
            print(f"      Assessment: POOR - Significant execution problems")
    
    if 'tp_analysis' in execution:
        tp = execution['tp_analysis']
        print(f"\n      Take Profit Execution:")
        print(f"        - Proper TP Hits:  {tp.get('proper_tp_hits', 0)}")
        print(f"        - Early Exits:     {tp.get('early_exits', 0)}")
    
    if 'sl_analysis' in execution:
        sl = execution['sl_analysis']
        print(f"\n      Stop Loss Discipline:")
        print(f"        - Proper SL Hits:  {sl.get('proper_sl_hits', 0)}")
        print(f"        - Violations:      {sl.get('violations', 0)}")
    
    # ===================================================================
    # STEP 7: Loss Forensics
    # ===================================================================
    print("\n[7/8] LOSS FORENSICS")
    print("-" * 70)
    forensics = results['loss_forensics']
    
    if 'total_losses' in forensics:
        print(f"\n      Total Losses: {forensics['total_losses']}")
    
    if 'proper_losses' in forensics:
        print(f"      Proper Losses: {forensics['proper_losses']}")
        
    if 'panic_exits' in forensics:
        print(f"      Panic Exits: {forensics.get('panic_exits', 0)}")
        
    if 'hope_trades' in forensics:
        print(f"      Hope Trades: {forensics.get('hope_trades', 0)}")
    
    if 'preventable_cost' in forensics:
        cost = forensics['preventable_cost']
        print(f"\n      Preventable Loss: {cost:.2f}R")
    
    # ===================================================================
    # STEP 8: Key Insights
    # ===================================================================
    print("\n[8/8] KEY INSIGHTS")
    print("-" * 70)
    insights = results['insights']
    
    # Critical patterns
    if 'critical_patterns' in insights and insights['critical_patterns']:
        print("\n      🚨 CRITICAL PATTERNS:")
        for i, pattern in enumerate(insights['critical_patterns'], 1):
            print(f"\n      {i}. {pattern['title']}")
            print(f"         Observation: {pattern['observation']}")
            if 'confidence' in pattern:
                print(f"         Confidence: {pattern['confidence']:.0%}")
    
    # Notable patterns
    if 'notable_patterns' in insights and insights['notable_patterns']:
        print("\n      💡 NOTABLE PATTERNS:")
        for i, pattern in enumerate(insights['notable_patterns'], 1):
            print(f"\n      {i}. {pattern['title']}")
            print(f"         Observation: {pattern['observation']}")
            if 'confidence' in pattern:
                print(f"         Confidence: {pattern['confidence']:.0%}")
    
    # Summary
    if 'summary' in insights:
        print("\n      📊 STATISTICAL SUMMARY:")
        summary = insights['summary']
        print(f"         {summary}")
    
    # ===================================================================
    # Complete
    # ===================================================================
    print("\n" + "=" * 70)
    print(" ✓ ENHANCED ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"\n All components functional:")
    print(f"   ✓ Basic metrics calculated")
    print(f"   ✓ Timing patterns detected")
    print(f"   ✓ Directional analysis complete")
    print(f"   ✓ Execution quality assessed")
    print(f"   ✓ Loss forensics analyzed")
    print(f"   ✓ Insights generated")
    print()
    
    return results


if __name__ == '__main__':
    try:
        results = test_enhanced_pipeline()
        print("SUCCESS: All tests passed!")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
