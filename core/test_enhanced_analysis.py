"""
Test enhanced analysis pipeline
CSV → Parser → Enhanced Analyzer → Results
"""

from core.csv_parser import CSVParser
from core.analyzer import BasicAnalyzer

def test_enhanced_pipeline():
    """Test complete pipeline met pattern analysis"""
    
    print("=" * 60)
    print("ENHANCED ANALYSIS TEST")
    print("=" * 60)
    
    # Step 1: Parse CSV
    print("\n1. Parsing CSV...")
    parser = CSVParser()
    trades = parser.parse('tests/sample_data/trades_sample.csv')
    print(f"   ✓ Parsed {len(trades)} trades")
    
    # Step 2: Run enhanced analysis
    print("\n2. Running enhanced analysis...")
    analyzer = BasicAnalyzer()
    results = analyzer.calculate(trades)
    
    # Step 3: Display basic metrics
    print("\n3. BASIC METRICS")
    print("-" * 60)
    print(f"   Total Trades: {results['total_trades']}")
    print(f"   Win Rate: {results['winrate']}%")
    print(f"   Profit Factor: {results['profit_factor']}")
    print(f"   Expectancy: {results['expectancy']}R")
    print(f"   ESI: {results['esi']}")
    print(f"   PVS: {results['pvs']}")
    
    # Step 4: Display timing analysis
    print("\n4. TIMING ANALYSIS")
    print("-" * 60)
    timing = results['timing_analysis']
    
    if 'session_breakdown' in timing:
        for session_name, session_data in timing['session_breakdown'].items():
            print(f"\n   {session_name}:")
            print(f"   - Trades: {session_data['trades']}")
            print(f"   - Win Rate: {session_data['winrate']:.1f}%")
            if 'verdict' in session_data:
                print(f"   - Verdict: {session_data['verdict']}")
    
    if 'best_hour' in timing:
        print(f"\n   Best Hour: {timing['best_hour']}")
    
    # Step 5: Display directional analysis
    print("\n5. DIRECTIONAL ANALYSIS")
    print("-" * 60)
    directional = results['directional_analysis']
    
    if 'long_performance' in directional:
        long = directional['long_performance']
        print(f"\n   LONG:")
        print(f"   - Trades: {long['trades']}")
        print(f"   - Win Rate: {long['winrate']:.1f}%")
        if 'edge_strength' in long:
            print(f"   - Edge: {long['edge_strength']}")
    
    if 'short_performance' in directional:
        short = directional['short_performance']
        print(f"\n   SHORT:")
        print(f"   - Trades: {short['trades']}")
        print(f"   - Win Rate: {short['winrate']:.1f}%")
        if 'edge_strength' in short:
            print(f"   - Edge: {short['edge_strength']}")
    
    # Step 6: Display execution analysis
    print("\n6. EXECUTION QUALITY")
    print("-" * 60)
    execution = results['execution_analysis']
    
    if 'quality_score' in execution:
        print(f"   Quality Score: {execution['quality_score']}/100")
    
    if 'tp_analysis' in execution:
        tp = execution['tp_analysis']
        print(f"   TP Hits: {tp.get('proper_tp_hits', 0)}")
    
    if 'sl_analysis' in execution:
        sl = execution['sl_analysis']
        print(f"   SL Discipline: {sl.get('proper_sl_hits', 0)}")
    
    # Step 7: Display insights
    print("\n7. KEY INSIGHTS")
    print("-" * 60)
    insights = results['insights']
    
    if 'critical_patterns' in insights and insights['critical_patterns']:
        print("\n   CRITICAL:")
        for i, pattern in enumerate(insights['critical_patterns'], 1):
            print(f"   {i}. {pattern['title']}")
            print(f"      → {pattern['finding']}")
    
    if 'notable_patterns' in insights and insights['notable_patterns']:
        print("\n   NOTABLE:")
        for i, pattern in enumerate(insights['notable_patterns'], 1):
            print(f"   {i}. {pattern['title']}")
            print(f"      → {pattern['finding']}")
    
    # Step 8: Show complete structure (debug)
    print("\n8. OUTPUT STRUCTURE")
    print("-" * 60)
    print(f"   Keys available: {list(results.keys())}")
    
    print("\n" + "=" * 60)
    print("✓ ENHANCED ANALYSIS COMPLETE")
    print("=" * 60)
    
    return results


if __name__ == '__main__':
    results = test_enhanced_pipeline()