"""
reporter.py
===========

Professional PDF Report Generator for EdgeLab.
Premium dark theme design with modern card-based layout.
Version 4.0 - Professional Polish

Author: EdgeLab Development Team
Version: 4.0 (Professional Polish Design)
"""

import io
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF


# Professional Dark Theme Colors
COLORS = {
    'bg_dark': HexColor('#0f172a'),        # Darker, more premium
    'bg_card': HexColor('#1e293b'),        # Card background
    'bg_hover': HexColor('#334155'),       # Hover/accent bg
    'border': HexColor('#475569'),         # Card borders
    'text_white': HexColor('#f8fafc'),     # Pure white text
    'text_gray': HexColor('#cbd5e1'),      # Secondary text
    'text_muted': HexColor('#94a3b8'),     # Muted text
    'blue': HexColor('#3b82f6'),           # Primary blue
    'blue_light': HexColor('#60a5fa'),     # Light blue
    'blue_dark': HexColor('#1e40af'),      # Dark blue
    'green': HexColor('#10b981'),          # Success green
    'green_light': HexColor('#34d399'),    # Light green
    'green_dark': HexColor('#059669'),     # Dark green
    'yellow': HexColor('#f59e0b'),         # Warning yellow
    'yellow_light': HexColor('#fbbf24'),   # Light yellow
    'red': HexColor('#ef4444'),            # Error red
    'red_light': HexColor('#f87171'),      # Light red
    'red_dark': HexColor('#dc2626'),       # Dark red
    'purple': HexColor('#8b5cf6'),         # Accent purple
}


class ProfessionalReporter:
    """
    Generate premium dark-themed PDF reports with professional polish.
    Card-based layout with visual hierarchy and color-coded indicators.
    """
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 15 * mm
        self.card_padding = 4 * mm
        self.spacing_unit = 8 * mm  # Grid-based spacing
        
    def create_pdf(
        self,
        trades: List,
        analysis: Dict[str, Any],
        output_path: str = None,
        include_narrative: bool = True,
        strategy_definition = None
    ) -> bytes:
        """Generate complete professional PDF report."""
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
        
        # Page 1: Premium Cover
        elements.extend(self._create_premium_cover(analysis))
        elements.append(PageBreak())
        
        # Page 2: Executive Dashboard
        elements.extend(self._create_executive_dashboard(analysis))
        elements.append(PageBreak())
        
        # Page 3: AI Narrative
        if include_narrative:
            elements.extend(self._create_narrative_page(analysis))
            elements.append(PageBreak())
        
        # Page 4: Performance Metrics Card
        elements.extend(self._create_metrics_card(analysis))
        elements.append(PageBreak())
        
        # Page 4.5: Trade History
        elements.extend(self._create_trade_history(trades))
        elements.append(PageBreak())
        
        # Page 5: Pattern Analysis Cards
        elements.extend(self._create_pattern_cards(analysis))
        elements.append(PageBreak())
        
        # Page 6: Insights Dashboard
        elements.extend(self._create_insights_dashboard(analysis))
        elements.append(PageBreak())
        
        # Page 7: Education
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
        """Draw premium dark background with subtle gradient effect."""
        canvas.saveState()
        
        # Main background
        canvas.setFillColor(COLORS['bg_dark'])
        canvas.rect(0, 0, self.page_width, self.page_height, fill=True, stroke=False)
        
        # Top accent line
        canvas.setStrokeColor(COLORS['blue'])
        canvas.setLineWidth(2)
        canvas.line(self.margin, self.page_height - 12*mm, 
                   self.page_width - self.margin, self.page_height - 12*mm)
        
        # Footer with border
        canvas.setStrokeColor(COLORS['border'])
        canvas.setLineWidth(0.5)
        canvas.line(self.margin, 12*mm, self.page_width - self.margin, 12*mm)
        
        # Footer text
        canvas.setFillColor(COLORS['text_muted'])
        canvas.setFont('Helvetica', 8)
        canvas.drawString(self.margin, 8*mm, 
                         f"EdgeLab Analysis Report | {datetime.now().strftime('%B %d, %Y')}")
        canvas.drawRightString(self.page_width - self.margin, 8*mm, 
                              f"Page {canvas.getPageNumber()}")
        
        canvas.restoreState()
    
    def _create_card(self, width: float, height: float, bg_color=None) -> Table:
        """Create a card container with rounded corners effect."""
        if bg_color is None:
            bg_color = COLORS['bg_card']
        
        # Simple card effect using table with background
        card_data = [['']]
        card_table = Table(card_data, colWidths=[width], rowHeights=[height])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
            ('LEFTPADDING', (0, 0), (-1, -1), self.card_padding),
            ('RIGHTPADDING', (0, 0), (-1, -1), self.card_padding),
            ('TOPPADDING', (0, 0), (-1, -1), self.card_padding),
            ('BOTTOMPADDING', (0, 0), (-1, -1), self.card_padding),
        ]))
        return card_table
    
    def _create_metric_card(self, value: str, label: str, color: HexColor, 
                           width: float = 40*mm) -> List:
        """Create a color-coded metric card."""
        elements = []
        
        # Value with large font
        value_para = Paragraph(
            f'<font size="32" color="#{color.hexval()[2:]}"><b>{value}</b></font>',
            ParagraphStyle('metric_val', alignment=TA_CENTER)
        )
        
        # Label below
        label_para = Paragraph(
            f'<font size="10" color="#{COLORS["text_gray"].hexval()[2:]}">{label}</font>',
            ParagraphStyle('metric_label', alignment=TA_CENTER, spaceAfter=2*mm)
        )
        
        # Create card container
        card_data = [[value_para], [label_para]]
        card = Table(card_data, colWidths=[width], rowHeights=[20*mm, 8*mm])
        card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
            ('BOX', (0, 0), (-1, -1), 2, color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4*mm),
        ]))
        
        return card
    
    def _create_progress_bar(self, value: float, max_value: float = 100, 
                            width: float = 80*mm, height: float = 6*mm) -> Table:
        """Create a visual progress bar."""
        percentage = min(value / max_value, 1.0)
        
        # Determine color
        if percentage >= 0.75:
            bar_color = COLORS['green']
        elif percentage >= 0.5:
            bar_color = COLORS['yellow']
        else:
            bar_color = COLORS['red']
        
        filled_width = width * percentage
        empty_width = width * (1 - percentage)
        
        # Create bar using table
        if filled_width > 0 and empty_width > 0:
            bar_data = [['', '']]
            bar = Table(bar_data, colWidths=[filled_width, empty_width], 
                       rowHeights=[height])
            bar.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), bar_color),
                ('BACKGROUND', (1, 0), (1, 0), COLORS['bg_hover']),
                ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        elif filled_width > 0:
            bar_data = [['']]
            bar = Table(bar_data, colWidths=[width], rowHeights=[height])
            bar.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), bar_color),
                ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
            ]))
        else:
            bar_data = [['']]
            bar = Table(bar_data, colWidths=[width], rowHeights=[height])
            bar.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), COLORS['bg_hover']),
                ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
            ]))
        
        return bar
    
    def _get_style(self, name: str) -> ParagraphStyle:
        """Get professional paragraph styles with better hierarchy."""
        styles = {
            'title': ParagraphStyle(
                'title',
                fontName='Helvetica-Bold',
                fontSize=36,
                textColor=COLORS['text_white'],
                alignment=TA_CENTER,
                spaceAfter=4*mm,
                leading=42
            ),
            'subtitle': ParagraphStyle(
                'subtitle',
                fontName='Helvetica',
                fontSize=14,
                textColor=COLORS['text_gray'],
                alignment=TA_CENTER,
                spaceAfter=self.spacing_unit
            ),
            'heading': ParagraphStyle(
                'heading',
                fontName='Helvetica-Bold',
                fontSize=22,
                textColor=COLORS['blue_light'],
                spaceBefore=self.spacing_unit,
                spaceAfter=6*mm,
                leading=26
            ),
            'subheading': ParagraphStyle(
                'subheading',
                fontName='Helvetica-Bold',
                fontSize=16,
                textColor=COLORS['text_white'],
                spaceBefore=6*mm,
                spaceAfter=4*mm,
                leading=20
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
            'body_white': ParagraphStyle(
                'body_white',
                fontName='Helvetica',
                fontSize=11,
                textColor=COLORS['text_white'],
                spaceBefore=2*mm,
                spaceAfter=2*mm,
                leading=16
            ),
        }
        return styles.get(name, styles['body'])
    
    def _create_premium_cover(self, analysis: Dict) -> List:
        """Create premium cover page with metric cards."""
        elements = []
        
        elements.append(Spacer(1, 25*mm))
        
        # Logo/Title with gradient effect
        elements.append(Paragraph("EdgeLab", self._get_style('title')))
        elements.append(Paragraph(
            "Professional Trading Analysis",
            ParagraphStyle('subtitle_cover', fontName='Helvetica', fontSize=16,
                          textColor=COLORS['blue_light'], alignment=TA_CENTER,
                          spaceAfter=self.spacing_unit)
        ))
        
        elements.append(Spacer(1, 15*mm))
        
        # Get metrics
        winrate = analysis.get('winrate', 0)
        total_trades = analysis.get('total_trades', 0)
        esi = analysis.get('esi', 0)
        pvs = analysis.get('pvs', 0)
        
        # Row 1: Trades and Win Rate
        row1_data = [[
            self._create_metric_card(
                str(total_trades),
                'Total Trades',
                COLORS['blue'],
                width=75*mm
            ),
            '',
            self._create_metric_card(
                f"{winrate:.1f}%",
                'Win Rate',
                self._get_wr_color(winrate),
                width=75*mm
            )
        ]]
        
        row1_table = Table(row1_data, colWidths=[75*mm, 10*mm, 75*mm])
        row1_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(row1_table)
        
        elements.append(Spacer(1, 12*mm))
        
        # Row 2: ESI and PVS with progress bars
        esi_card_elements = []
        esi_card_elements.append(Paragraph(
            f'<font size="28" color="#{self._get_esi_color(esi).hexval()[2:]}"><b>{esi:.2f}</b></font>',
            ParagraphStyle('esi_val', alignment=TA_CENTER)
        ))
        esi_card_elements.append(Spacer(1, 2*mm))
        esi_card_elements.append(self._create_progress_bar(esi, 1.0, width=65*mm))
        esi_card_elements.append(Spacer(1, 2*mm))
        esi_card_elements.append(Paragraph(
            '<font size="10" color="#{0}">Edge Stability Index</font>'.format(
                COLORS['text_gray'].hexval()[2:]
            ),
            ParagraphStyle('esi_label', alignment=TA_CENTER)
        ))
        
        pvs_card_elements = []
        pvs_card_elements.append(Paragraph(
            f'<font size="28" color="#{self._get_pvs_color(pvs).hexval()[2:]}"><b>{pvs:.2f}</b></font>',
            ParagraphStyle('pvs_val', alignment=TA_CENTER)
        ))
        pvs_card_elements.append(Spacer(1, 2*mm))
        pvs_card_elements.append(self._create_progress_bar(pvs, 1.0, width=65*mm))
        pvs_card_elements.append(Spacer(1, 2*mm))
        pvs_card_elements.append(Paragraph(
            '<font size="10" color="#{0}">Prop Verification Score</font>'.format(
                COLORS['text_gray'].hexval()[2:]
            ),
            ParagraphStyle('pvs_label', alignment=TA_CENTER)
        ))
        
        # Pack into cards
        esi_card_data = [[e] for e in esi_card_elements]
        esi_card = Table(esi_card_data, colWidths=[75*mm])
        esi_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
            ('BOX', (0, 0), (-1, -1), 2, self._get_esi_color(esi)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 6*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6*mm),
            ('LEFTPADDING', (0, 0), (-1, -1), 5*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5*mm),
        ]))
        
        pvs_card_data = [[e] for e in pvs_card_elements]
        pvs_card = Table(pvs_card_data, colWidths=[75*mm])
        pvs_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
            ('BOX', (0, 0), (-1, -1), 2, self._get_pvs_color(pvs)),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 6*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6*mm),
            ('LEFTPADDING', (0, 0), (-1, -1), 5*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5*mm),
        ]))
        
        row2_data = [[esi_card, '', pvs_card]]
        row2_table = Table(row2_data, colWidths=[75*mm, 10*mm, 75*mm])
        row2_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(row2_table)
        
        elements.append(Spacer(1, 20*mm))
        
        # Date
        elements.append(Paragraph(
            f"Generated {datetime.now().strftime('%B %d, %Y')}",
            ParagraphStyle('date', fontName='Helvetica', fontSize=10,
                          alignment=TA_CENTER, textColor=COLORS['text_muted'])
        ))
        
        return elements
    
    def _create_executive_dashboard(self, analysis: Dict) -> List:
        """Create executive summary as a dashboard."""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self._get_style('heading')))
        
        winrate = analysis.get('winrate', 0)
        pf = analysis.get('profit_factor', 0)
        exp = analysis.get('expectancy', 0)
        esi = analysis.get('esi', 0)
        pvs = analysis.get('pvs', 0)
        
        # Overall verdict badge
        if winrate >= 50 and pf >= 1.5 and esi >= 0.7:
            verdict = "EDGE CONFIRMED"
            verdict_color = COLORS['green']
        elif winrate >= 45 and pf >= 1.2:
            verdict = "EDGE NEEDS IMPROVEMENT"
            verdict_color = COLORS['yellow']
        else:
            verdict = "NO CLEAR EDGE"
            verdict_color = COLORS['red']
        
        verdict_para = Paragraph(
            f'<font size="24" color="#{verdict_color.hexval()[2:]}"><b>{verdict}</b></font>',
            ParagraphStyle('verdict', alignment=TA_CENTER, spaceAfter=self.spacing_unit)
        )
        elements.append(verdict_para)
        
        # Metrics table with better styling
        summary_data = [
            [
                Paragraph('<b>METRIC</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=12)),
                Paragraph('<b>VALUE</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=12, alignment=TA_CENTER)),
                Paragraph('<b>ASSESSMENT</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=12, alignment=TA_RIGHT))
            ],
            [
                Paragraph('Win Rate', self._get_style('body_white')),
                Paragraph(f"{winrate:.2f}%", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_CENTER)),
                Paragraph(self._assess_winrate(winrate), ParagraphStyle('assess', textColor=self._get_wr_color(winrate), fontSize=11, alignment=TA_RIGHT))
            ],
            [
                Paragraph('Profit Factor', self._get_style('body_white')),
                Paragraph(f"{pf:.2f}", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_CENTER)),
                Paragraph(self._assess_pf(pf), ParagraphStyle('assess', textColor=self._get_pf_color(pf), fontSize=11, alignment=TA_RIGHT))
            ],
            [
                Paragraph('Expectancy', self._get_style('body_white')),
                Paragraph(f"{exp:.2f}R", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_CENTER)),
                Paragraph(self._assess_expectancy(exp), ParagraphStyle('assess', textColor=self._get_exp_color(exp), fontSize=11, alignment=TA_RIGHT))
            ],
            [
                Paragraph('ESI', self._get_style('body_white')),
                Paragraph(f"{esi:.2f}", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_CENTER)),
                Paragraph(self._assess_esi(esi), ParagraphStyle('assess', textColor=self._get_esi_color(esi), fontSize=11, alignment=TA_RIGHT))
            ],
            [
                Paragraph('PVS', self._get_style('body_white')),
                Paragraph(f"{pvs:.2f}", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_CENTER)),
                Paragraph(self._assess_pvs(pvs), ParagraphStyle('assess', textColor=self._get_pvs_color(pvs), fontSize=11, alignment=TA_RIGHT))
            ],
        ]
        
        summary_table = Table(summary_data, colWidths=[60*mm, 45*mm, 55*mm])
        summary_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_hover']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['text_white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            # Alternating row colors
            ('BACKGROUND', (0, 1), (-1, 1), COLORS['bg_card']),
            ('BACKGROUND', (0, 2), (-1, 2), COLORS['bg_hover']),
            ('BACKGROUND', (0, 3), (-1, 3), COLORS['bg_card']),
            ('BACKGROUND', (0, 4), (-1, 4), COLORS['bg_hover']),
            ('BACKGROUND', (0, 5), (-1, 5), COLORS['bg_card']),
            # Border
            ('BOX', (0, 0), (-1, -1), 2, COLORS['border']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['blue']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
            # Alignment
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(summary_table)
        
        return elements
    
    def _create_narrative_page(self, analysis: Dict) -> List:
        """Create AI narrative page with card styling."""
        elements = []
        
        elements.append(Paragraph("AI Analysis", self._get_style('heading')))
        
        narrative = self._generate_narrative(analysis)
        
        # Put narrative in a card
        narrative_para = Paragraph(narrative, self._get_style('body'))
        
        card_data = [[narrative_para]]
        card = Table(card_data, colWidths=[160*mm])
        card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
            ('BOX', (0, 0), (-1, -1), 2, COLORS['blue']),
            ('LEFTPADDING', (0, 0), (-1, -1), 8*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 8*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8*mm),
        ]))
        
        elements.append(card)
        
        elements.append(Spacer(1, self.spacing_unit))
        elements.append(Paragraph(
            "This analysis is generated based on statistical patterns in your data. It is not financial advice.",
            ParagraphStyle('disclaimer_small', fontName='Helvetica', fontSize=9,
                          textColor=COLORS['text_muted'], fontStyle='italic',
                          alignment=TA_CENTER)
        ))
        
        return elements
    
    def _generate_narrative(self, analysis: Dict) -> str:
        """Generate AI-powered narrative (or fallback)."""
        try:
            from core.ai_narrator import generate_analysis_narrative
            return generate_analysis_narrative(analysis)
        except:
            winrate = analysis.get('winrate', 0)
            pf = analysis.get('profit_factor', 0)
            esi = analysis.get('esi', 0)
            pvs = analysis.get('pvs', 0)
            
            parts = []
            
            if winrate < 50:
                parts.append(f"With a {winrate:.1f}% win rate and {pf:.2f} profit factor, this strategy requires optimization.")
            else:
                parts.append(f"The strategy shows positive characteristics with {winrate:.1f}% win rate and {pf:.2f} profit factor.")
            
            if esi < 0.5:
                parts.append(f"With an ESI of {esi:.2f}, the edge is not yet stable.")
            elif esi >= 0.7:
                parts.append(f"The ESI of {esi:.2f} demonstrates consistent performance.")
            
            if pvs >= 0.8:
                parts.append("The PVS score indicates prop-firm readiness.")
            elif pvs >= 0.6:
                parts.append("The PVS score is approaching prop-firm readiness.")
            else:
                parts.append("Focus on PVS improvement for prop firm readiness.")
            
            parts.append("Recommended focus: refine entry criteria, improve risk-reward ratio, analyze which market conditions work better.")
            
            return " ".join(parts)
    
    def _create_metrics_card(self, analysis: Dict) -> List:
        """Create detailed metrics in a professional card layout."""
        elements = []
        
        elements.append(Paragraph("Performance Metrics", self._get_style('heading')))
        
        metrics_data = [
            [
                Paragraph('<b>METRIC</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=11)),
                Paragraph('<b>VALUE</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=11, alignment=TA_RIGHT))
            ],
            [Paragraph('Total Trades', self._get_style('body_white')), 
             Paragraph(str(analysis.get('total_trades', 0)), ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Winning Trades', self._get_style('body_white')), 
             Paragraph(str(analysis.get('wins', 0)), ParagraphStyle('val', textColor=COLORS['green'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Losing Trades', self._get_style('body_white')), 
             Paragraph(str(analysis.get('losses', 0)), ParagraphStyle('val', textColor=COLORS['red'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Win Rate', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('winrate', 0):.2f}%", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Profit Factor', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('profit_factor', 0):.2f}", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Expectancy', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('expectancy', 0):.2f}R", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Total Profit', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('total_profit_r', 0):.2f}R", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Average Win', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('avg_win_r', 0):.2f}R", ParagraphStyle('val', textColor=COLORS['green'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Average Loss', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('avg_loss_r', 0):.2f}R", ParagraphStyle('val', textColor=COLORS['red'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Sharpe Ratio', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('sharpe_ratio', 0):.2f}", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('Max Drawdown', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('max_drawdown_pct', 0):.2f}%", ParagraphStyle('val', textColor=COLORS['red'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('ESI Score', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('esi', 0):.2f}", ParagraphStyle('val', textColor=COLORS['purple'], fontSize=11, alignment=TA_RIGHT))],
            [Paragraph('PVS Score', self._get_style('body_white')), 
             Paragraph(f"{analysis.get('pvs', 0):.2f}", ParagraphStyle('val', textColor=COLORS['purple'], fontSize=11, alignment=TA_RIGHT))],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[90*mm, 70*mm])
        metrics_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_hover']),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['text_white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            # Alternating rows
            *[('BACKGROUND', (0, i), (-1, i), COLORS['bg_card'] if i % 2 == 1 else COLORS['bg_hover']) 
              for i in range(1, len(metrics_data))],
            # Border
            ('BOX', (0, 0), (-1, -1), 2, COLORS['border']),
            ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['blue']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(metrics_table)
        
        return elements
    
    
    def _create_trade_history(self, trades: List) -> List:
        """Create detailed trade-by-trade history page."""
        elements = []
        
        elements.append(Paragraph("Trade History", self._get_style('heading')))
        
        if not trades or len(trades) == 0:
            elements.append(Paragraph(
                "No trades available.",
                ParagraphStyle('no_trades', fontSize=11, textColor=COLORS['text_muted'],
                              alignment=TA_CENTER)
            ))
            return elements
        
        # Header
        elements.append(Paragraph(
            f"📝 Complete Trade Log ({len(trades)} trades)",
            self._get_style('subheading')
        ))
        
        # Build trade table
        # Determine if we need pagination (max 25 trades per table for readability)
        max_per_table = 25
        total_trades = len(trades)
        
        for page_num, start_idx in enumerate(range(0, total_trades, max_per_table)):
            end_idx = min(start_idx + max_per_table, total_trades)
            page_trades = trades[start_idx:end_idx]
            
            # Table header
            trade_data = [
                [
                    Paragraph('<b>#</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=9, alignment=TA_CENTER)),
                    Paragraph('<b>DATE</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=9)),
                    Paragraph('<b>SYMBOL</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=9)),
                    Paragraph('<b>DIR</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=9, alignment=TA_CENTER)),
                    Paragraph('<b>PROFIT</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=9, alignment=TA_RIGHT)),
                    Paragraph('<b>RESULT</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=9, alignment=TA_CENTER))
                ]
            ]
            
            # Add trade rows
            wins = 0
            losses = 0
            total_profit = 0
            
            for idx, trade in enumerate(page_trades, start=start_idx + 1):
                # Extract trade data
                try:
                    # Handle different trade object types
                    if hasattr(trade, 'timestamp_open'):
                        date_str = trade.timestamp_open.strftime('%d-%m')
                    elif hasattr(trade, 'open_time'):
                        date_str = trade.open_time.strftime('%d-%m')
                    else:
                        date_str = 'N/A'
                    
                    symbol = getattr(trade, 'symbol', 'N/A')
                    direction = getattr(trade, 'direction', 'N/A')
                    profit_r = getattr(trade, 'profit_r', 0)
                    result = getattr(trade, 'result', 'UNKNOWN')
                    
                    # Direction abbreviation
                    dir_abbr = 'L' if direction == 'LONG' else 'S' if direction == 'SHORT' else 'N'
                    
                    # Format profit
                    profit_str = f"{profit_r:+.2f}R"
                    
                    # Result with icon
                    if result == 'WIN':
                        result_str = 'WIN ✓'
                        result_color = COLORS['green']
                        row_bg = HexColor('#1a3d2e')  # Dark green tint
                        wins += 1
                    else:
                        result_str = 'LOSS ✗'
                        result_color = COLORS['red']
                        row_bg = HexColor('#3d1a1a')  # Dark red tint
                        losses += 1
                    
                    total_profit += profit_r
                    
                    # Create row
                    trade_data.append([
                        Paragraph(str(idx), ParagraphStyle('idx', fontSize=9, textColor=COLORS['text_gray'], alignment=TA_CENTER)),
                        Paragraph(date_str, ParagraphStyle('date', fontSize=9, textColor=COLORS['text_gray'])),
                        Paragraph(symbol, ParagraphStyle('symbol', fontSize=9, textColor=COLORS['blue_light'])),
                        Paragraph(dir_abbr, ParagraphStyle('dir', fontSize=9, textColor=COLORS['text_white'], alignment=TA_CENTER)),
                        Paragraph(profit_str, ParagraphStyle('profit', fontSize=9, textColor=result_color, alignment=TA_RIGHT, fontName='Helvetica-Bold')),
                        Paragraph(result_str, ParagraphStyle('result', fontSize=9, textColor=result_color, alignment=TA_CENTER, fontName='Helvetica-Bold'))
                    ])
                
                except Exception as e:
                    # Skip malformed trades
                    continue
            
            # Create table
            trade_table = Table(
                trade_data,
                colWidths=[15*mm, 20*mm, 25*mm, 15*mm, 25*mm, 25*mm]
            )
            
            # Style table with alternating colors
            table_style = [
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_hover']),
                ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['text_white']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['blue']),
                # Border
                ('BOX', (0, 0), (-1, -1), 2, COLORS['border']),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
            
            # Alternating row backgrounds with color coding
            for i in range(1, len(trade_data)):
                row_idx = i
                # Get trade to determine color
                trade_idx = start_idx + i - 1
                if trade_idx < len(trades):
                    trade = trades[trade_idx]
                    result = getattr(trade, 'result', 'UNKNOWN')
                    
                    if result == 'WIN':
                        row_bg = HexColor('#1a3d2e') if i % 2 == 1 else HexColor('#0f2920')
                    else:
                        row_bg = HexColor('#3d1a1a') if i % 2 == 1 else HexColor('#2a1212')
                    
                    table_style.append(('BACKGROUND', (0, i), (-1, i), row_bg))
            
            trade_table.setStyle(TableStyle(table_style))
            elements.append(trade_table)
            
            # Add spacing
            elements.append(Spacer(1, 6*mm))
            
            # If multiple pages, add page break except for last
            if end_idx < total_trades:
                elements.append(Paragraph(
                    f"Continued on next page... ({end_idx}/{total_trades})",
                    ParagraphStyle('continue', fontSize=9, textColor=COLORS['text_muted'],
                                  alignment=TA_CENTER, fontStyle='italic')
                ))
                elements.append(PageBreak())
                elements.append(Paragraph("Trade History (continued)", self._get_style('heading')))
        
        # Summary footer
        winrate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        summary_elements = [
            [Paragraph(
                f"<b>Summary:</b> {wins + losses} trades • {wins} wins ({winrate:.1f}%) • {losses} losses • {total_profit:+.2f}R total",
                ParagraphStyle('summary', fontSize=10, textColor=COLORS['text_white'])
            )]
        ]
        
        summary_card = Table(summary_elements, colWidths=[150*mm])
        summary_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_hover']),
            ('BOX', (0, 0), (-1, -1), 2, COLORS['blue']),
            ('LEFTPADDING', (0, 0), (-1, -1), 6*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 4*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4*mm),
        ]))
        
        elements.append(summary_card)
        
        return elements
    
    def _create_pattern_cards(self, analysis: Dict) -> List:
        """Create pattern analysis with professional card layout."""
        elements = []
        
        elements.append(Paragraph("Pattern Analysis", self._get_style('heading')))
        
        # Session Performance Card
        timing = analysis.get('timing_analysis', {})
        if timing:
            sessions = timing.get('session_breakdown', {})
            
            if sessions:
                elements.append(Paragraph("📊 Session Performance", self._get_style('subheading')))
                
                session_data = [
                    [
                        Paragraph('<b>SESSION</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10)),
                        Paragraph('<b>TRADES</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph('<b>WIN RATE</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph('<b>EXPECTANCY</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph('<b>VERDICT</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER))
                    ]
                ]
                
                for session_name in ['Tokyo', 'London', 'NY']:
                    if session_name in sessions:
                        stats = sessions[session_name]
                        verdict = stats.get('verdict', 'N/A')
                        verdict_color = COLORS['green'] if verdict == 'FOCUS' else COLORS['yellow'] if verdict == 'NEUTRAL' else COLORS['red']
                        
                        session_data.append([
                            Paragraph(session_name, self._get_style('body_white')),
                            Paragraph(str(stats.get('total_trades', 0)), ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER)),
                            Paragraph(f"{stats.get('winrate', 0):.1f}%", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER)),
                            Paragraph(f"{stats.get('expectancy', 0):.2f}R", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER)),
                            Paragraph(verdict, ParagraphStyle('verdict', textColor=verdict_color, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold'))
                        ])
                
                session_table = Table(session_data, colWidths=[32*mm, 25*mm, 28*mm, 35*mm, 30*mm])
                session_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_hover']),
                    *[('BACKGROUND', (0, i), (-1, i), COLORS['bg_card'] if i % 2 == 1 else COLORS['bg_hover']) 
                      for i in range(1, len(session_data))],
                    ('BOX', (0, 0), (-1, -1), 2, COLORS['border']),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['blue']),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(session_table)
                
                # Best hour
                best_hour = timing.get('best_hour', {})
                if best_hour.get('hour') is not None:
                    elements.append(Spacer(1, 3*mm))
                    hour_text = f"⭐ Peak Hour: {best_hour['hour']:02d}:00 UTC ({best_hour.get('winrate', 0):.0f}% WR, {best_hour.get('expectancy', 0):.2f}R)"
                    elements.append(Paragraph(
                        hour_text,
                        ParagraphStyle('best_hour', fontName='Helvetica-Bold', fontSize=11,
                                      textColor=COLORS['green_light'])
                    ))
                
                elements.append(Spacer(1, self.spacing_unit))
        
        # Directional Analysis Card
        directional = analysis.get('directional_analysis', {})
        if directional:
            elements.append(Paragraph("⚖️ Directional Analysis", self._get_style('subheading')))
            
            dir_data = [
                [
                    Paragraph('<b>DIRECTION</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10)),
                    Paragraph('<b>TRADES</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER)),
                    Paragraph('<b>WIN RATE</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER)),
                    Paragraph('<b>EXPECTANCY</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER)),
                    Paragraph('<b>EDGE</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER))
                ]
            ]
            
            for direction_key in ['long_stats', 'short_stats']:
                data = directional.get(direction_key, {})
                dir_name = 'LONG' if 'long' in direction_key else 'SHORT'
                
                total_trades = data.get('total_trades', 0)
                if total_trades > 0:
                    edge = data.get('edge', 'NONE')
                    edge_color = COLORS['green'] if edge == 'STRONG' else COLORS['yellow'] if edge == 'WEAK' else COLORS['red']
                    
                    dir_data.append([
                        Paragraph(dir_name, self._get_style('body_white')),
                        Paragraph(str(total_trades), ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph(f"{data.get('winrate', 0):.1f}%", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph(f"{data.get('expectancy', 0):.2f}R", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph(edge, ParagraphStyle('edge', textColor=edge_color, fontSize=10, alignment=TA_CENTER, fontName='Helvetica-Bold'))
                    ])
                else:
                    dir_data.append([
                        Paragraph(dir_name, self._get_style('body_white')),
                        Paragraph('0', ParagraphStyle('val', textColor=COLORS['text_muted'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph('N/A', ParagraphStyle('val', textColor=COLORS['text_muted'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph('N/A', ParagraphStyle('val', textColor=COLORS['text_muted'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph('NO DATA', ParagraphStyle('edge', textColor=COLORS['text_muted'], fontSize=10, alignment=TA_CENTER))
                    ])
            
            dir_table = Table(dir_data, colWidths=[32*mm, 25*mm, 28*mm, 35*mm, 30*mm])
            dir_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_hover']),
                ('BACKGROUND', (0, 1), (-1, 1), COLORS['bg_card']),
                ('BACKGROUND', (0, 2), (-1, 2), COLORS['bg_hover']),
                ('BOX', (0, 0), (-1, -1), 2, COLORS['border']),
                ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['blue']),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(dir_table)
            
            bias = directional.get('bias', 'NEUTRAL')
            if bias != 'NEUTRAL':
                elements.append(Spacer(1, 3*mm))
                bias_color = COLORS['green_light']
                elements.append(Paragraph(
                    f"🎯 Detected Bias: {bias}",
                    ParagraphStyle('bias', fontName='Helvetica-Bold', fontSize=11,
                                  textColor=bias_color)
                ))
            
            elements.append(Spacer(1, self.spacing_unit))
        
        # Execution Quality Card
        execution = analysis.get('execution_analysis', {})
        if execution:
            elements.append(Paragraph("✓ Execution Quality", self._get_style('subheading')))
            
            score = execution.get('execution_score', 0)
            score_color = COLORS['green'] if score >= 75 else COLORS['yellow'] if score >= 50 else COLORS['red']
            
            # Score with progress bar
            score_para = Paragraph(
                f'<font size="20" color="#{score_color.hexval()[2:]}"><b>{score}/100</b></font>',
                ParagraphStyle('score_val', alignment=TA_LEFT)
            )
            
            exec_card_elements = [
                [score_para],
                [self._create_progress_bar(score, 100, width=150*mm)],
                [Spacer(1, 3*mm)]
            ]
            
            tp_behavior = execution.get('tp_behavior', {})
            sl_behavior = execution.get('sl_behavior', {})
            
            if tp_behavior.get('total_wins', 0) > 0:
                full_tp_pct = tp_behavior.get('full_tp_pct', 0)
                exec_card_elements.append([Paragraph(
                    f"TP Discipline: {full_tp_pct:.0f}% of wins hit full target",
                    self._get_style('body')
                )])
            
            if sl_behavior.get('total_losses', 0) > 0:
                proper_sl_pct = sl_behavior.get('proper_sl_pct', 100)
                exec_card_elements.append([Paragraph(
                    f"SL Discipline: {proper_sl_pct:.0f}% of losses respected stop",
                    self._get_style('body')
                )])
            
            exec_card = Table(exec_card_elements, colWidths=[150*mm])
            exec_card.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
                ('BOX', (0, 0), (-1, -1), 2, score_color),
                ('LEFTPADDING', (0, 0), (-1, -1), 8*mm),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8*mm),
                ('TOPPADDING', (0, 0), (-1, -1), 6*mm),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6*mm),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(exec_card)
            
            elements.append(Spacer(1, self.spacing_unit))
        
        # Loss Forensics Card
        loss_forensics = analysis.get('loss_forensics', {})
        loss_breakdown_data = loss_forensics.get('loss_breakdown', {})
        
        if loss_breakdown_data:
            proper_data = loss_breakdown_data.get('proper', {})
            panic_data = loss_breakdown_data.get('early_exits', {})
            hope_data = loss_breakdown_data.get('held_past_sl', {})
            
            proper = proper_data.get('count', 0)
            panic = panic_data.get('count', 0)
            hope = hope_data.get('count', 0)
            
            total_categorized = proper + panic + hope
            
            if total_categorized > 0:
                elements.append(Paragraph("🔍 Loss Analysis", self._get_style('subheading')))
                
                loss_data = [
                    [
                        Paragraph('<b>TYPE</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10)),
                        Paragraph('<b>COUNT</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph('<b>PERCENTAGE</b>', ParagraphStyle('th', textColor=COLORS['text_white'], fontSize=10, alignment=TA_CENTER))
                    ],
                    [
                        Paragraph('Proper SL', self._get_style('body_white')),
                        Paragraph(str(proper), ParagraphStyle('val', textColor=COLORS['green'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph(f"{(proper/total_categorized*100):.0f}%", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER))
                    ],
                    [
                        Paragraph('Panic Close', self._get_style('body_white')),
                        Paragraph(str(panic), ParagraphStyle('val', textColor=COLORS['yellow'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph(f"{(panic/total_categorized*100):.0f}%", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER))
                    ],
                    [
                        Paragraph('Held Too Long', self._get_style('body_white')),
                        Paragraph(str(hope), ParagraphStyle('val', textColor=COLORS['red'], fontSize=10, alignment=TA_CENTER)),
                        Paragraph(f"{(hope/total_categorized*100):.0f}%", ParagraphStyle('val', textColor=COLORS['blue_light'], fontSize=10, alignment=TA_CENTER))
                    ]
                ]
                
                loss_table = Table(loss_data, colWidths=[60*mm, 40*mm, 50*mm])
                loss_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), COLORS['bg_hover']),
                    ('BACKGROUND', (0, 1), (-1, 1), COLORS['bg_card']),
                    ('BACKGROUND', (0, 2), (-1, 2), COLORS['bg_hover']),
                    ('BACKGROUND', (0, 3), (-1, 3), COLORS['bg_card']),
                    ('BOX', (0, 0), (-1, -1), 2, COLORS['border']),
                    ('LINEBELOW', (0, 0), (-1, 0), 2, COLORS['red']),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(loss_table)
                
                preventable_cost = loss_forensics.get('preventable_cost', 0)
                if preventable_cost > 0:
                    elements.append(Spacer(1, 3*mm))
                    elements.append(Paragraph(
                        f"💰 Preventable Loss Cost: {preventable_cost:.2f}R",
                        ParagraphStyle('preventable', fontName='Helvetica-Bold', fontSize=11,
                                      textColor=COLORS['red_light'])
                    ))
        
        return elements
    
    def _create_insights_dashboard(self, analysis: Dict) -> List:
        """Create insights as a dashboard with cards."""
        elements = []
        
        elements.append(Paragraph("Key Insights", self._get_style('heading')))
        
        insights = analysis.get('insights', {})
        
        # Critical Findings
        critical = insights.get('critical_findings', []) or insights.get('critical_patterns', [])
        if critical:
            elements.append(Paragraph("🔴 Critical Findings", self._get_style('subheading')))
            
            for finding in critical[:5]:
                title = finding.get('title', 'Finding')
                obs = finding.get('observation', finding.get('finding', ''))
                
                # Create card for each finding
                finding_elements = [
                    [Paragraph(f'<b>{title}</b>', ParagraphStyle('finding_title', fontName='Helvetica-Bold', fontSize=12, textColor=COLORS['text_white']))],
                    [Spacer(1, 2*mm)],
                    [Paragraph(obs, self._get_style('body'))]
                ]
                
                finding_card = Table(finding_elements, colWidths=[150*mm])
                finding_card.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
                    ('BOX', (0, 0), (-1, -1), 2, COLORS['red']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6*mm),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6*mm),
                    ('TOPPADDING', (0, 0), (-1, -1), 4*mm),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4*mm),
                ]))
                
                elements.append(finding_card)
                elements.append(Spacer(1, 4*mm))
        
        # Notable Patterns
        notable = insights.get('notable_patterns', [])
        if notable:
            elements.append(Paragraph("🔵 Notable Patterns", self._get_style('subheading')))
            
            for pattern in notable[:5]:
                title = pattern.get('title', 'Pattern')
                obs = pattern.get('observation', pattern.get('finding', ''))
                
                pattern_elements = [
                    [Paragraph(f'<b>{title}</b>', ParagraphStyle('pattern_title', fontName='Helvetica-Bold', fontSize=12, textColor=COLORS['text_white']))],
                    [Spacer(1, 2*mm)],
                    [Paragraph(obs, self._get_style('body'))]
                ]
                
                pattern_card = Table(pattern_elements, colWidths=[150*mm])
                pattern_card.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
                    ('BOX', (0, 0), (-1, -1), 2, COLORS['blue']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6*mm),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6*mm),
                    ('TOPPADDING', (0, 0), (-1, -1), 4*mm),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4*mm),
                ]))
                
                elements.append(pattern_card)
                elements.append(Spacer(1, 4*mm))
        
        # Statistical Summary
        summary = insights.get('statistical_summary', {})
        if summary:
            elements.append(Paragraph("📊 Statistical Summary", self._get_style('subheading')))
            
            assessment = summary.get('overall_assessment', '')
            total_findings = summary.get('total_findings', 0)
            
            summary_elements = []
            if assessment:
                summary_elements.append([Paragraph(assessment, self._get_style('body'))])
                summary_elements.append([Spacer(1, 2*mm)])
            
            if total_findings > 0:
                critical_count = summary.get('critical_findings', 0)
                notable_count = summary.get('notable_patterns', 0)
                summary_elements.append([Paragraph(
                    f"Total patterns identified: {total_findings} ({critical_count} critical, {notable_count} notable)",
                    ParagraphStyle('summary_stat', fontName='Helvetica', fontSize=10,
                                  textColor=COLORS['text_muted'])
                )])
            
            if summary_elements:
                summary_card = Table(summary_elements, colWidths=[150*mm])
                summary_card.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
                    ('BOX', (0, 0), (-1, -1), 2, COLORS['purple']),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6*mm),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6*mm),
                    ('TOPPADDING', (0, 0), (-1, -1), 4*mm),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4*mm),
                ]))
                elements.append(summary_card)
        
        # Enhanced fallback
        if not critical and not notable:
            winrate = analysis.get('winrate', 0)
            pf = analysis.get('profit_factor', 0)
            total_trades = analysis.get('total_trades', 0)
            
            fallback_elements = [
                [Paragraph("No critical patterns detected with current dataset size.", 
                          ParagraphStyle('info', fontName='Helvetica', fontSize=11, textColor=COLORS['text_gray']))],
                [Spacer(1, 3*mm)],
                [Paragraph(f"• Win Rate: {winrate:.1f}%", self._get_style('body'))],
                [Paragraph(f"• Profit Factor: {pf:.2f}", self._get_style('body'))],
                [Paragraph(f"• Total Trades: {total_trades}", self._get_style('body'))],
                [Spacer(1, 3*mm)]
            ]
            
            if total_trades < 30:
                rec_text = "Recommendation: Continue testing with more trades for statistically significant insights."
            elif winrate >= 50 and pf >= 1.5:
                rec_text = "Performance indicators are positive. Focus on consistency and scaling."
            else:
                rec_text = "Consider optimizing entry conditions, risk-reward ratio, or market selection."
            
            fallback_elements.append([Paragraph(rec_text, self._get_style('body_white'))])
            
            fallback_card = Table(fallback_elements, colWidths=[150*mm])
            fallback_card.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
                ('BOX', (0, 0), (-1, -1), 2, COLORS['yellow']),
                ('LEFTPADDING', (0, 0), (-1, -1), 6*mm),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6*mm),
                ('TOPPADDING', (0, 0), (-1, -1), 4*mm),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4*mm),
            ]))
            elements.append(fallback_card)
        
        return elements
    
    def _create_education_page(self) -> List:
        """Create education page with card styling."""
        elements = []
        
        elements.append(Paragraph("Understanding EdgeLab Metrics", self._get_style('heading')))
        
        # ESI Card
        elements.append(Paragraph("ESI - Edge Stability Index", self._get_style('subheading')))
        
        esi_text = """The ESI measures how CONSISTENT your edge performs over time. A strategy can be profitable but unreliable if results vary significantly week-to-week.

<b>Calculation:</b> Trades are divided into 4 equal periods (quarters). Win rate is calculated per quarter. ESI = 1 - (standard deviation / mean). Less variation = higher ESI.

<b>Interpretation:</b>
• ESI ≥ 0.70: Stable edge - consistent results, reliable for scaling
• ESI 0.50-0.69: Moderate stability - results vary, more data needed
• ESI < 0.50: Unstable edge - large fluctuations, optimization needed

<b>Why it matters:</b> Prop firms seek consistency. A 60% win rate scoring 58-62% monthly is more valuable than one fluctuating 40-80%."""
        
        esi_card_elements = [[Paragraph(esi_text, ParagraphStyle(
            'esi_explain', fontName='Helvetica', fontSize=10,
            textColor=COLORS['text_gray'], leading=14
        ))]]
        
        esi_card = Table(esi_card_elements, colWidths=[150*mm])
        esi_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
            ('BOX', (0, 0), (-1, -1), 2, COLORS['purple']),
            ('LEFTPADDING', (0, 0), (-1, -1), 6*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 6*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6*mm),
        ]))
        elements.append(esi_card)
        
        elements.append(Spacer(1, self.spacing_unit))
        
        # PVS Card
        elements.append(Paragraph("PVS - Prop Verification Score", self._get_style('subheading')))
        
        pvs_text = """The PVS predicts whether your strategy would pass prop firm challenges like FTMO, MyForexFunds, or The Funded Trader.

<b>Components (weighted):</b>
• Win Rate ≥ 50% (30% weight) - Minimum profitability required
• Profit Factor ≥ 1.5 (30% weight) - Profits must exceed losses
• Max Drawdown ≤ 10% (20% weight) - Risk management crucial
• Sample Size ≥ 100 trades (20% weight) - Sufficient data for reliability

<b>Interpretation:</b>
• PVS ≥ 0.80: Prop-Ready - High probability of passing challenge
• PVS 0.60-0.79: Almost ready - Focus on weakest component
• PVS < 0.60: Not ready - Significant improvements needed

<b>Practical use:</b> Use PVS to decide if you're ready for paid challenges. PVS < 0.70 likely means wasting money on challenge fees."""
        
        pvs_card_elements = [[Paragraph(pvs_text, ParagraphStyle(
            'pvs_explain', fontName='Helvetica', fontSize=10,
            textColor=COLORS['text_gray'], leading=14
        ))]]
        
        pvs_card = Table(pvs_card_elements, colWidths=[150*mm])
        pvs_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
            ('BOX', (0, 0), (-1, -1), 2, COLORS['purple']),
            ('LEFTPADDING', (0, 0), (-1, -1), 6*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 6*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6*mm),
        ]))
        elements.append(pvs_card)
        
        return elements
    
    def _create_disclaimer_page(self) -> List:
        """Create disclaimer page with card styling."""
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
            disc_elements = [[Paragraph(f'<b>{title}:</b> {text}', ParagraphStyle(
                'disclaimer', fontName='Helvetica', fontSize=10,
                textColor=COLORS['text_gray'], leading=14
            ))]]
            
            disc_card = Table(disc_elements, colWidths=[150*mm])
            disc_card.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLORS['bg_card']),
                ('BOX', (0, 0), (-1, -1), 1, COLORS['border']),
                ('LEFTPADDING', (0, 0), (-1, -1), 4*mm),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4*mm),
                ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
            ]))
            elements.append(disc_card)
            elements.append(Spacer(1, 3*mm))
        
        return elements
    
    # Helper methods
    def _get_wr_color(self, wr):
        if wr >= 55: return COLORS['green']
        if wr >= 45: return COLORS['yellow']
        return COLORS['red']
    
    def _get_pf_color(self, pf):
        if pf >= 1.5: return COLORS['green']
        if pf >= 1.2: return COLORS['yellow']
        return COLORS['red']
    
    def _get_exp_color(self, exp):
        if exp >= 0.5: return COLORS['green']
        if exp >= 0.2: return COLORS['yellow']
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


# Backward compatibility alias
ModernReporter = ProfessionalReporter