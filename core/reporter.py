"""
reporter.py
===========

Modern Dark Theme PDF Report Generator for EdgeLab.
Professional design matching the web interface.
Includes AI-powered narrative analysis.

Author: EdgeLab Development Team
Version: 3.0 (Dark Theme + AI Narrative)
"""

import io
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas


# Dark Theme Colors
COLORS = {
    'bg_dark': HexColor('#111827'),
    'bg_card': HexColor('#1f2937'),
    'bg_light': HexColor('#374151'),
    'text_white': HexColor('#ffffff'),
    'text_gray': HexColor('#9ca3af'),
    'text_muted': HexColor('#6b7280'),
    'blue': HexColor('#3b82f6'),
    'blue_light': HexColor('#60a5fa'),
    'green': HexColor('#22c55e'),
    'green_light': HexColor('#4ade80'),
    'yellow': HexColor('#eab308'),
    'red': HexColor('#ef4444'),
    'red_light': HexColor('#f87171'),
}


class ModernReporter:
    """
    Generate professional dark-themed PDF reports.
    Matches EdgeLab web interface design.
    """
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 20 * mm
        
    def create_pdf(
        self,
        trades: List,
        analysis: Dict[str, Any],
        output_path: str = None,
        include_narrative: bool = True
    ) -> bytes:
        """
        Generate complete PDF report.
        """
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin
        )
        
        elements = []
        
        # Page 1: Cover
        elements.extend(self._create_cover_page(analysis))
        elements.append(PageBreak())
        
        # Page 2: Executive Summary
        elements.extend(self._create_summary_page(analysis))
        elements.append(PageBreak())
        
        # Page 3: AI Narrative
        if include_narrative:
            elements.extend(self._create_narrative_page(analysis))
            elements.append(PageBreak())
        
        # Page 4: Detailed Metrics
        elements.extend(self._create_metrics_page(analysis))
        elements.append(PageBreak())
        
        # Page 5: Pattern Analysis
        elements.extend(self._create_patterns_page(analysis))
        elements.append(PageBreak())
        
        # Page 6: Insights
        elements.extend(self._create_insights_page(analysis))
        elements.append(PageBreak())
        
        # Page 7: ESI/PVS Education
        elements.extend(self._create_education_page())
        elements.append(PageBreak())
        
        # Page 8: Disclaimer
        elements.extend(self._create_disclaimer_page())
        
        doc.build(elements, onFirstPage=self._draw_background, onLaterPages=self._draw_background)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _draw_background(self, canvas, doc):
        """Draw dark background on each page."""
        canvas.saveState()
        canvas.setFillColor(COLORS['bg_dark'])
        canvas.rect(0, 0, self.page_width, self.page_height, fill=True, stroke=False)
        
        canvas.setStrokeColor(COLORS['bg_light'])
        canvas.setLineWidth(1)
        canvas.line(self.margin, self.page_height - 15*mm, self.page_width - self.margin, self.page_height - 15*mm)
        
        canvas.setFillColor(COLORS['text_muted'])
        canvas.setFont('Helvetica', 8)
        canvas.drawString(self.margin, 10*mm, f"EdgeLab Analysis Report | Generated {datetime.now().strftime('%Y-%m-%d')}")
        canvas.drawRightString(self.page_width - self.margin, 10*mm, f"Page {canvas.getPageNumber()}")
        
        canvas.restoreState()
    
    def _get_style(self, name: str) -> ParagraphStyle:
        """Get predefined paragraph styles."""
        styles = {
            'title': ParagraphStyle(
                'title',
                fontName='Helvetica-Bold',
                fontSize=32,
                textColor=COLORS['text_white'],
                alignment=TA_CENTER,
                spaceAfter=10*mm
            ),
            'subtitle': ParagraphStyle(
                'subtitle',
                fontName='Helvetica',
                fontSize=14,
                textColor=COLORS['text_gray'],
                alignment=TA_CENTER,
                spaceAfter=5*mm
            ),
            'heading': ParagraphStyle(
                'heading',
                fontName='Helvetica-Bold',
                fontSize=20,
                textColor=COLORS['blue_light'],
                spaceBefore=8*mm,
                spaceAfter=5*mm
            ),
            'subheading': ParagraphStyle(
                'subheading',
                fontName='Helvetica-Bold',
                fontSize=14,
                textColor=COLORS['text_white'],
                spaceBefore=5*mm,
                spaceAfter=3*mm
            ),
            'body': ParagraphStyle(
                'body',
                fontName='Helvetica',
                fontSize=11,
                textColor=COLORS['text_gray'],
                spaceBefore=2*mm,
                spaceAfter=2*mm,
                leading=16
            ),
        }
        return styles.get(name, styles['body'])
    
    def _create_cover_page(self, analysis: Dict) -> List:
        """Create cover page with key stats."""
        elements = []
        
        elements.append(Spacer(1, 30*mm))
        elements.append(Paragraph("EdgeLab", self._get_style('title')))
        elements.append(Paragraph("Trading Performance Analysis", self._get_style('subtitle')))
        elements.append(Spacer(1, 20*mm))
        
        winrate = analysis.get('winrate', 0)
        total_trades = analysis.get('total_trades', 0)
        esi = analysis.get('esi', 0)
        pvs = analysis.get('pvs', 0)
        
        metrics_data = [
            [self._metric_box("Total Trades", str(total_trades), COLORS['blue_light']),
             self._metric_box("Win Rate", f"{winrate}%", self._get_wr_color(winrate))],
            [self._metric_box("ESI Score", f"{esi}", self._get_esi_color(esi)),
             self._metric_box("PVS Score", f"{pvs}", self._get_pvs_color(pvs))]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[80*mm, 80*mm], rowHeights=[45*mm, 45*mm])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_dark']),
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 20*mm))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')}",
            self._get_style('subtitle')
        ))
        
        return elements
    
    def _metric_box(self, label: str, value: str, color) -> Table:
        """Create a single metric box."""
        data = [[Paragraph(f'<font color="#{color.hexval()[2:]}">{value}</font>', 
                          ParagraphStyle('v', fontName='Helvetica-Bold', fontSize=28, alignment=TA_CENTER))],
                [Paragraph(label, ParagraphStyle('l', fontName='Helvetica', fontSize=10, 
                          textColor=COLORS['text_muted'], alignment=TA_CENTER))]]
        
        t = Table(data, colWidths=[70*mm], rowHeights=[15*mm, 8*mm])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
            ('BOX', (0, 0), (-1, -1), 1, COLORS['bg_light']),
        ]))
        return t
    
    def _create_summary_page(self, analysis: Dict) -> List:
        """Create executive summary page."""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self._get_style('heading')))
        
        winrate = analysis.get('winrate', 0)
        pf = analysis.get('profit_factor', 0)
        esi = analysis.get('esi', 0)
        
        if winrate >= 55 and pf >= 1.5 and esi >= 0.6:
            verdict = "STRONG EDGE DETECTED"
            verdict_color = COLORS['green']
        elif winrate >= 50 and pf >= 1.2:
            verdict = "MODERATE EDGE"
            verdict_color = COLORS['yellow']
        else:
            verdict = "EDGE NEEDS IMPROVEMENT"
            verdict_color = COLORS['red']
        
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph(
            f'<font color="#{verdict_color.hexval()[2:]}">{verdict}</font>',
            ParagraphStyle('verdict', fontName='Helvetica-Bold', fontSize=24, alignment=TA_CENTER)
        ))
        elements.append(Spacer(1, 10*mm))
        
        summary_data = [
            ['METRIC', 'VALUE', 'ASSESSMENT'],
            ['Win Rate', f"{analysis.get('winrate', 0)}%", self._assess_winrate(analysis.get('winrate', 0))],
            ['Profit Factor', f"{analysis.get('profit_factor', 0)}", self._assess_pf(analysis.get('profit_factor', 0))],
            ['Expectancy', f"{analysis.get('expectancy', 0)}R", self._assess_expectancy(analysis.get('expectancy', 0))],
            ['ESI', f"{analysis.get('esi', 0)}", self._assess_esi(analysis.get('esi', 0))],
            ['PVS', f"{analysis.get('pvs', 0)}", self._assess_pvs(analysis.get('pvs', 0))],
        ]
        
        summary_table = Table(summary_data, colWidths=[50*mm, 40*mm, 50*mm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_light']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['text_white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), COLORS['bg_card']),
            ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text_gray']),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, COLORS['bg_light']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(summary_table)
        
        return elements
    
    def _create_narrative_page(self, analysis: Dict) -> List:
        """Create AI-generated narrative page."""
        elements = []
        
        elements.append(Paragraph("Persoonlijke Analyse", self._get_style('heading')))
        
        # Generate narrative
        narrative = self._generate_narrative(analysis)
        
        elements.append(Spacer(1, 5*mm))
        
        narrative_style = ParagraphStyle(
            'narrative',
            fontName='Helvetica',
            fontSize=11,
            textColor=COLORS['text_white'],
            leading=18,
            spaceBefore=5*mm,
            spaceAfter=5*mm,
            leftIndent=10,
            rightIndent=10
        )
        
        paragraphs = narrative.split('\n\n')
        for para in paragraphs:
            if para.strip():
                elements.append(Paragraph(para.strip(), narrative_style))
                elements.append(Spacer(1, 3*mm))
        
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(
            "<i>Deze analyse is gegenereerd op basis van statistische patronen in je data. "
            "Het is geen financieel advies.</i>",
            ParagraphStyle('ai_note', fontName='Helvetica-Oblique', fontSize=9, 
                          textColor=COLORS['text_muted'], alignment=TA_CENTER)
        ))
        
        return elements
    
    def _generate_narrative(self, analysis: Dict) -> str:
        """Generate narrative using AI or fallback to template."""
        try:
            from core.ai_narrator import generate_analysis_narrative
            return generate_analysis_narrative(analysis)
        except Exception as e:
            print(f"AI narrative error: {e}, using fallback")
            return self._fallback_narrative(analysis)
    
    def _fallback_narrative(self, analysis: Dict) -> str:
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
            opening = f"Met een win rate van {winrate}% en profit factor van {pf} vraagt deze strategie om optimalisatie. De huidige resultaten suggereren dat aanpassingen nodig zijn."
        
        if esi >= 0.7:
            esi_text = f"De ESI score van {esi} wijst op een stabiele edge die consistent presteert over tijd."
        elif esi >= 0.5:
            esi_text = f"De ESI van {esi} toont matige stabiliteit. De resultaten varieren tussen periodes."
        else:
            esi_text = f"Met een ESI van {esi} is de edge nog niet stabiel. Overweeg strengere filters."
        
        if pvs >= 0.8:
            pvs_text = "De PVS score geeft aan dat deze strategie klaar is voor prop firm evaluatie."
        elif pvs >= 0.6:
            pvs_text = "De PVS score is bijna prop-ready. Focus op consistentie en drawdown management."
        else:
            pvs_text = "Voor prop firm challenges is verdere optimalisatie nodig."
        
        suggestions = []
        if winrate < 50:
            suggestions.append("verfijn de entry criteria")
        if pf < 1.3:
            suggestions.append("verbeter de risk-reward ratio")
        if esi < 0.6:
            suggestions.append("analyseer welke marktcondities beter werken")
        
        if suggestions:
            suggestion_text = f"Aanbevolen focus: {', '.join(suggestions)}."
        else:
            suggestion_text = "Behoud de huidige aanpak en monitor de consistentie."
        
        return f"{opening}\n\n{esi_text} {pvs_text}\n\n{suggestion_text}"
    
    def _create_metrics_page(self, analysis: Dict) -> List:
        """Create detailed metrics page."""
        elements = []
        
        elements.append(Paragraph("Performance Metrics", self._get_style('heading')))
        
        metrics_data = [
            ['METRIC', 'VALUE'],
            ['Total Trades', str(analysis.get('total_trades', 0))],
            ['Winning Trades', str(analysis.get('wins', 0))],
            ['Losing Trades', str(analysis.get('losses', 0))],
            ['Win Rate', f"{analysis.get('winrate', 0)}%"],
            ['Profit Factor', str(analysis.get('profit_factor', 0))],
            ['Expectancy', f"{analysis.get('expectancy', 0)}R"],
            ['Total Profit', f"{analysis.get('total_profit_r', 0)}R"],
            ['Average Win', f"{analysis.get('avg_win_r', 0)}R"],
            ['Average Loss', f"{analysis.get('avg_loss_r', 0)}R"],
            ['Sharpe Ratio', str(analysis.get('sharpe_ratio', 0))],
            ['Max Drawdown', f"{analysis.get('max_drawdown_pct', 0)}%"],
            ['ESI Score', str(analysis.get('esi', 0))],
            ['PVS Score', str(analysis.get('pvs', 0))],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[80*mm, 60*mm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['blue']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['text_white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), COLORS['bg_card']),
            ('BACKGROUND', (0, 2), (-1, 2), COLORS['bg_light']),
            ('BACKGROUND', (0, 3), (-1, 3), COLORS['bg_card']),
            ('BACKGROUND', (0, 4), (-1, 4), COLORS['bg_light']),
            ('BACKGROUND', (0, 5), (-1, 5), COLORS['bg_card']),
            ('BACKGROUND', (0, 6), (-1, 6), COLORS['bg_light']),
            ('BACKGROUND', (0, 7), (-1, 7), COLORS['bg_card']),
            ('BACKGROUND', (0, 8), (-1, 8), COLORS['bg_light']),
            ('BACKGROUND', (0, 9), (-1, 9), COLORS['bg_card']),
            ('BACKGROUND', (0, 10), (-1, 10), COLORS['bg_light']),
            ('BACKGROUND', (0, 11), (-1, 11), COLORS['bg_card']),
            ('BACKGROUND', (0, 12), (-1, 12), COLORS['bg_light']),
            ('BACKGROUND', (0, 13), (-1, 13), COLORS['bg_card']),
            ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text_gray']),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, COLORS['bg_dark']),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(metrics_table)
        
        return elements
    
    def _create_patterns_page(self, analysis: Dict) -> List:
        """Create pattern analysis page."""
        elements = []
        
        elements.append(Paragraph("Pattern Analysis", self._get_style('heading')))
        
        # Timing Analysis
        timing = analysis.get('timing_analysis', {})
        if timing and 'session_breakdown' in timing:
            elements.append(Paragraph("Session Performance", self._get_style('subheading')))
            
            session_data = [['SESSION', 'TRADES', 'WIN RATE', 'EXPECTANCY', 'VERDICT']]
            
            for session, data in timing.get('session_breakdown', {}).items():
                session_data.append([
                    session,
                    str(data.get('total_trades', 0)),
                    f"{data.get('winrate', 0):.1f}%",
                    f"{data.get('expectancy', 0):.2f}R",
                    data.get('verdict', 'N/A')
                ])
            
            session_table = Table(session_data, colWidths=[35*mm, 25*mm, 30*mm, 35*mm, 35*mm])
            session_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_light']),
                ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['text_white']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (-1, -1), COLORS['bg_card']),
                ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text_gray']),
                ('GRID', (0, 0), (-1, -1), 1, COLORS['bg_dark']),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(session_table)
            elements.append(Spacer(1, 8*mm))
        
        # Directional Analysis
        directional = analysis.get('directional_analysis', {})
        if directional:
            elements.append(Paragraph("Directional Analysis", self._get_style('subheading')))
            
            dir_data = [['DIRECTION', 'TRADES', 'WIN RATE', 'EXPECTANCY', 'EDGE']]
            
            for direction in ['long_performance', 'short_performance']:
                data = directional.get(direction, {})
                if data.get('total_trades', 0) > 0:
                    dir_name = 'LONG' if 'long' in direction else 'SHORT'
                    dir_data.append([
                        dir_name,
                        str(data.get('total_trades', 0)),
                        f"{data.get('winrate', 0):.1f}%",
                        f"{data.get('expectancy', 0):.2f}R",
                        data.get('edge_strength', 'N/A')
                    ])
            
            if len(dir_data) > 1:
                dir_table = Table(dir_data, colWidths=[35*mm, 25*mm, 30*mm, 35*mm, 35*mm])
                dir_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_light']),
                    ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['text_white']),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 1), (-1, -1), COLORS['bg_card']),
                    ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['text_gray']),
                    ('GRID', (0, 0), (-1, -1), 1, COLORS['bg_dark']),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(dir_table)
        
        # Execution Quality
        execution = analysis.get('execution_analysis', {})
        if execution and 'quality_score' in execution:
            elements.append(Spacer(1, 8*mm))
            elements.append(Paragraph("Execution Quality", self._get_style('subheading')))
            
            score = execution.get('quality_score', 0)
            score_color = COLORS['green'] if score >= 75 else COLORS['yellow'] if score >= 50 else COLORS['red']
            
            elements.append(Paragraph(
                f'Quality Score: <font color="#{score_color.hexval()[2:]}">{score}/100</font>',
                ParagraphStyle('score', fontName='Helvetica-Bold', fontSize=16, textColor=COLORS['text_white'])
            ))
        
        return elements
    
    def _create_insights_page(self, analysis: Dict) -> List:
        """Create insights page."""
        elements = []
        
        elements.append(Paragraph("Key Insights", self._get_style('heading')))
        
        insights = analysis.get('insights', {})
        
        critical = insights.get('critical_findings', []) or insights.get('critical_patterns', [])
        if critical:
            elements.append(Paragraph("Critical Findings", self._get_style('subheading')))
            for finding in critical[:5]:
                title = finding.get('title', 'Finding')
                obs = finding.get('observation', finding.get('finding', ''))
                elements.append(Paragraph(
                    f'<font color="#ef4444">&#8226;</font> <b>{title}</b>',
                    ParagraphStyle('finding', fontName='Helvetica', fontSize=11, textColor=COLORS['text_white'])
                ))
                elements.append(Paragraph(
                    obs,
                    ParagraphStyle('obs', fontName='Helvetica', fontSize=10, textColor=COLORS['text_gray'], leftIndent=15)
                ))
                elements.append(Spacer(1, 3*mm))
        
        notable = insights.get('notable_patterns', [])
        if notable:
            elements.append(Spacer(1, 5*mm))
            elements.append(Paragraph("Notable Patterns", self._get_style('subheading')))
            for pattern in notable[:5]:
                title = pattern.get('title', 'Pattern')
                obs = pattern.get('observation', pattern.get('finding', ''))
                elements.append(Paragraph(
                    f'<font color="#3b82f6">&#8226;</font> <b>{title}</b>',
                    ParagraphStyle('pattern', fontName='Helvetica', fontSize=11, textColor=COLORS['text_white'])
                ))
                elements.append(Paragraph(
                    obs,
                    ParagraphStyle('obs', fontName='Helvetica', fontSize=10, textColor=COLORS['text_gray'], leftIndent=15)
                ))
                elements.append(Spacer(1, 3*mm))
        
        if not critical and not notable:
            elements.append(Paragraph(
                "Analysis complete. Review the metrics and patterns above for detailed performance insights.",
                self._get_style('body')
            ))
            
            winrate = analysis.get('winrate', 0)
            pf = analysis.get('profit_factor', 0)
            
            if winrate >= 50 and pf >= 1.2:
                summary = "Your strategy shows positive characteristics. Focus on consistency and risk management."
            else:
                summary = "Consider optimizing entry conditions or adjusting risk parameters to improve performance."
            
            elements.append(Spacer(1, 5*mm))
            elements.append(Paragraph(summary, self._get_style('body')))
        
        return elements
    
    def _create_education_page(self) -> List:
        """Create ESI/PVS education page."""
        elements = []
        
        elements.append(Paragraph("Understanding EdgeLab Metrics", self._get_style('heading')))
        
        # ESI
        elements.append(Paragraph("ESI - Edge Stability Index", self._get_style('subheading')))
        
        esi_text = """De ESI meet hoe CONSISTENT je edge presteert over tijd. Een strategie kan winstgevend zijn maar toch onbetrouwbaar als de resultaten sterk varieren per week of maand.

<b>Hoe wordt ESI berekend?</b>
Je trades worden verdeeld in 4 gelijke periodes (kwartalen). Per kwartaal berekenen we de win rate. ESI = 1 - (standaarddeviatie / gemiddelde). Hoe minder variatie tussen kwartalen, hoe hoger de ESI.

<b>Interpretatie:</b>
ESI 0.70 of hoger: Stabiele edge - consistente resultaten, betrouwbaar voor scaling.
ESI 0.50-0.69: Matige stabiliteit - resultaten varieren, meer data nodig.
ESI onder 0.50: Instabiele edge - grote schommelingen, optimalisatie nodig.

<b>Waarom is dit belangrijk?</b>
Prop firms en professionele traders zoeken consistentie. Een 60% win rate die elke maand 58-62% scoort is waardevoller dan een die schommelt tussen 40-80%."""
        
        elements.append(Paragraph(esi_text, ParagraphStyle(
            'esi_explain', fontName='Helvetica', fontSize=10, 
            textColor=COLORS['text_gray'], leading=14, spaceBefore=3*mm
        )))
        
        elements.append(Spacer(1, 8*mm))
        
        # PVS
        elements.append(Paragraph("PVS - Prop Verification Score", self._get_style('subheading')))
        
        pvs_text = """De PVS voorspelt of je strategie zou slagen voor een prop firm challenge zoals FTMO, MyForexFunds, of The Funded Trader.

<b>PVS Componenten (gewogen score):</b>
Win Rate minimaal 50% (30% gewicht) - Minimale winstgevendheid vereist.
Profit Factor minimaal 1.5 (30% gewicht) - Winsten moeten verliezen overtreffen.
Max Drawdown maximaal 10% (20% gewicht) - Risicobeheer is cruciaal.
Sample Size minimaal 100 trades (20% gewicht) - Voldoende data voor betrouwbaarheid.

<b>Interpretatie:</b>
PVS 0.80 of hoger: Prop-Ready - Grote kans op slagen van challenge.
PVS 0.60-0.79: Bijna klaar - Focus op je zwakste component.
PVS onder 0.60: Niet klaar - Significante verbeteringen nodig.

<b>Praktisch gebruik:</b>
Gebruik PVS om te beslissen of je klaar bent voor een betaalde challenge. Een PVS onder 0.70 betekent dat je waarschijnlijk geld verspilt aan challenge fees."""
        
        elements.append(Paragraph(pvs_text, ParagraphStyle(
            'pvs_explain', fontName='Helvetica', fontSize=10, 
            textColor=COLORS['text_gray'], leading=14, spaceBefore=3*mm
        )))
        
        return elements
    
    def _create_disclaimer_page(self) -> List:
        """Create disclaimer page."""
        elements = []
        
        elements.append(Paragraph("Important Disclaimer", self._get_style('heading')))
        
        disclaimers = [
            ("No Financial Advice", "This report provides statistical analysis of trading data only. It does not constitute financial advice, trading recommendations, or investment guidance."),
            ("Past Performance", "Past performance is not indicative of future results. Market conditions change continuously and historical patterns may not repeat."),
            ("Risk Warning", "Trading financial instruments involves substantial risk of loss. You should not trade with money you cannot afford to lose."),
            ("Statistical Analysis", "All observations in this report are based purely on statistical patterns in the provided data. Users must conduct their own due diligence."),
            ("No Guarantees", "EdgeLab makes no guarantees about the accuracy, completeness, or reliability of any analysis."),
            ("Educational Purpose", "This analysis is provided for educational and informational purposes only."),
        ]
        
        for title, text in disclaimers:
            elements.append(Paragraph(
                f'<b>{title}:</b> {text}',
                ParagraphStyle('disclaimer', fontName='Helvetica', fontSize=10, 
                              textColor=COLORS['text_gray'], spaceBefore=3*mm, spaceAfter=2*mm, leading=14)
            ))
        
        return elements
    
    # Helper methods
    def _get_wr_color(self, wr):
        if wr >= 55: return COLORS['green']
        if wr >= 45: return COLORS['yellow']
        return COLORS['red']
    
    def _get_esi_color(self, esi):
        if esi >= 0.7: return COLORS['green']
        if esi >= 0.5: return COLORS['yellow']
        return COLORS['red']
    
    def _get_pvs_color(self, pvs):
        if pvs >= 0.8: return COLORS['green']
        if pvs >= 0.6: return COLORS['yellow']
        return COLORS['red']
    
    def _assess_winrate(self, wr):
        if wr >= 55: return "STRONG"
        if wr >= 50: return "FAIR"
        return "WEAK"
    
    def _assess_pf(self, pf):
        if pf >= 1.5: return "STRONG"
        if pf >= 1.2: return "FAIR"
        return "WEAK"
    
    def _assess_expectancy(self, exp):
        if exp >= 0.5: return "STRONG"
        if exp >= 0.2: return "FAIR"
        return "WEAK"
    
    def _assess_esi(self, esi):
        if esi >= 0.7: return "STABLE"
        if esi >= 0.5: return "MODERATE"
        return "NEEDS WORK"
    
    def _assess_pvs(self, pvs):
        if pvs >= 0.8: return "READY"
        if pvs >= 0.6: return "CLOSE"
        return "NEEDS WORK"