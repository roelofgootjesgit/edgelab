"""
ai_narrator.py
==============

AI-powered narrative generation for EdgeLab reports.
Uses Claude API to create personalized analysis stories.

Author: QuantMetrics Development Team
Version: 1.0
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class AINarrator:
    """Generate personalized narrative analysis using Claude API."""
    
    def __init__(self, api_key: Optional[str] = None):
        load_dotenv()
        
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                print("Warning: anthropic package not installed.")
        else:
            print("Note: No ANTHROPIC_API_KEY found.")
    
    def generate_narrative(self, analysis: Dict[str, Any]) -> str:
        """Generate a personalized narrative about the trading analysis."""
        if self.client:
            return self._generate_with_api(analysis)
        else:
            return self._generate_template(analysis)
    
    def _generate_with_api(self, analysis: Dict[str, Any]) -> str:
        """Generate narrative using Claude API."""
        try:
            metrics_summary = self._format_metrics_for_prompt(analysis)
            
            prompt = f"""Je bent een ervaren trading coach die een analyse rapport bespreekt met een trader.
Schrijf een persoonlijk, behulpzaam verhaal (2-3 korte paragrafen, max 200 woorden) over deze trading resultaten.

METRICS:
{metrics_summary}

REGELS:
- Schrijf in het Nederlands
- Wees specifiek over de cijfers
- Geef 2-3 concrete verbeterpunten
- Blijf positief maar realistisch
- GEEN financieel advies, alleen observaties
- Gebruik geen bullet points, schrijf vloeiende tekst

Begin direct met de analyse, geen intro nodig."""

            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            print(f"API error: {e}")
            return self._generate_template(analysis)
    
    def _format_metrics_for_prompt(self, analysis: Dict) -> str:
        """Format metrics for the API prompt."""
        lines = [
            f"Total Trades: {analysis.get('total_trades', 0)}",
            f"Win Rate: {analysis.get('winrate', 0)}%",
            f"Profit Factor: {analysis.get('profit_factor', 0)}",
            f"Expectancy: {analysis.get('expectancy', 0)}R per trade",
            f"Total Profit: {analysis.get('total_profit_r', 0)}R",
            f"Max Drawdown: {analysis.get('max_drawdown_pct', 0)}%",
            f"ESI (Edge Stability): {analysis.get('esi', 0)} (0-1 schaal, >0.7 is stabiel)",
            f"PVS (Prop Readiness): {analysis.get('pvs', 0)} (0-1 schaal, >0.8 is prop-ready)",
        ]
        
        timing = analysis.get('timing_analysis', {})
        if timing and 'best_session' in timing:
            best = timing.get('best_session', {})
            lines.append(f"Beste sessie: {best.get('session', 'N/A')} ({best.get('winrate', 0)}% WR)")
        
        directional = analysis.get('directional_analysis', {})
        if directional:
            long_perf = directional.get('long_performance', {})
            short_perf = directional.get('short_performance', {})
            if long_perf.get('total_trades', 0) > 0:
                lines.append(f"LONG trades: {long_perf.get('winrate', 0)}% WR")
            if short_perf.get('total_trades', 0) > 0:
                lines.append(f"SHORT trades: {short_perf.get('winrate', 0)}% WR")
        
        return "\n".join(lines)
    
    def _generate_template(self, analysis: Dict) -> str:
        """Template-based narrative fallback."""
        winrate = analysis.get('winrate', 0)
        pf = analysis.get('profit_factor', 0)
        esi = analysis.get('esi', 0)
        pvs = analysis.get('pvs', 0)
        total_trades = analysis.get('total_trades', 0)
        
        if winrate >= 55 and pf >= 1.5:
            opening = f"Deze strategie toont sterke resultaten met een win rate van {winrate}% over {total_trades} trades. De profit factor van {pf} geeft aan dat winsten significant groter zijn dan verliezen."
        elif winrate >= 50 and pf >= 1.2:
            opening = f"De resultaten zijn redelijk positief met {winrate}% win rate en een profit factor van {pf}. Er is ruimte voor verbetering, maar de basis is solide."
        else:
            opening = f"Met een win rate van {winrate}% en profit factor van {pf} vraagt deze strategie om optimalisatie."
        
        if esi >= 0.7:
            esi_text = f"De ESI score van {esi} wijst op een stabiele edge."
        elif esi >= 0.5:
            esi_text = f"De ESI van {esi} toont matige stabiliteit."
        else:
            esi_text = f"Met een ESI van {esi} is de edge nog niet stabiel."
        
        if pvs >= 0.8:
            pvs_text = "De PVS score geeft aan dat deze strategie klaar is voor prop firm evaluatie."
        elif pvs >= 0.6:
            pvs_text = "De PVS score is bijna prop-ready."
        else:
            pvs_text = "Voor prop firm challenges is verdere optimalisatie nodig."
        
        suggestions = []
        if winrate < 50:
            suggestions.append("verfijn de entry criteria")
        if pf < 1.3:
            suggestions.append("verbeter de risk-reward ratio")
        if esi < 0.6:
            suggestions.append("analyseer welke marktcondities beter werken")
        
        suggestion_text = f"Aanbevolen focus: {', '.join(suggestions)}." if suggestions else "Behoud de huidige aanpak."
        
        return f"{opening}\n\n{esi_text} {pvs_text}\n\n{suggestion_text}"


def generate_analysis_narrative(analysis: Dict[str, Any], api_key: Optional[str] = None) -> str:
    """Convenience function to generate narrative."""
    narrator = AINarrator(api_key=api_key)
    return narrator.generate_narrative(analysis)