"""
EdgeLab PDF Reporter
====================
Modern 2026-style professional PDF reports with pattern analysis.

Design Philosophy:
- Clean, minimal design
- Data-driven insights
- Visual hierarchy
- Professional typography
- Subtle colors
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import List, Dict, Any
import io

# Modern 2026 color palette
COLORS = {
    'primary': colors.HexColor('#2563eb'),      # Modern blue
    'success': colors.HexColor('#10b981'),      # Green
    'warning': colors.HexColor('#f59e0b'),      # Amber
    'danger': colors.HexColor('#ef4444'),       # Red
    'neutral_dark': colors.HexColor('#1f2937'), # Near black
    'neutral': colors.HexColor('#6b7280'),      # Gray
    'neutral_light': colors.HexColor('#f3f4f6'),# Light gray
    'background': colors.HexColor('#ffffff'),   # White
    'accent': colors.HexColor('#8b5cf6'),       # Purple
}


class ModernReporter:
    """Generate modern, professional PDF reports."""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 20 * mm
        self.content_width = self.width - (2 * self.margin)
        
    def create_pdf(
        self, 
        trades: List[Any],
        analysis: Dict[str, Any],
        output_path: str = None
    ) -> bytes:
        """
        Generate complete PDF report.
        
        Args:
            trades: List of EdgeLabTrade objects
            analysis: Full analysis dict with patterns and insights
            output_path: Optional file path to save
            
        Returns:
            PDF bytes
        """
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=self.margin,
            rightMargin=self.margin,
            topMargin=self.margin,
            bottomMargin=self.margin,
            title='EdgeLab Analysis Report'
        )
        
        # Build content
        story = []
        
        # Cover page
        story.extend(self._build_cover(analysis))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._build_executive_summary(analysis))
        story.append(PageBreak())
        
        # Core metrics
        story.extend(self._build_metrics_page(analysis))
        story.append(PageBreak())
        
        # Pattern analysis pages (if available)
        if analysis.get('timing'):
            story.extend(self._build_timing_page(analysis['timing']))
            story.append(PageBreak())
            
        if analysis.get('directional'):
            story.extend(self._build_directional_page(analysis['directional']))
            story.append(PageBreak())
            
        if analysis.get('execution'):
            story.extend(self._build_execution_page(analysis['execution']))
            story.append(PageBreak())
            
        # Key insights
        if analysis.get('insights'):
            story.extend(self._build_insights_page(analysis['insights']))
            story.append(PageBreak())
        
        # Disclaimer
        story.extend(self._build_disclaimer())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, 
                  onLaterPages=self._add_header_footer)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _build_cover(self, analysis: Dict) -> List:
        """Modern cover page."""
        styles = getSampleStyleSheet()
        story = []
        
        # Logo/Brand
        story.append(Spacer(1, 40*mm))
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=36,
            textColor=COLORS['primary'],
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph('EdgeLab', title_style))
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=COLORS['neutral'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        story.append(Paragraph('Trading Performance Analysis', subtitle_style))
        
        # Key stats card
        story.append(Spacer(1, 20*mm))
        
        stats_data = [
            ['Total Trades', str(analysis.get('total_trades', 0))],
            ['Win Rate', f"{analysis.get('win_rate', 0):.1f}%"],
            ['ESI Score', f"{analysis.get('esi', 0):.2f}"],
            ['PVS Score', f"{analysis.get('pvs', 0):.2f}"],
        ]
        
        stats_table = Table(stats_data, colWidths=[80*mm, 60*mm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLORS['neutral_light']),
            ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['neutral_dark']),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        story.append(stats_table)
        
        # Date
        story.append(Spacer(1, 40*mm))
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=COLORS['neutral'],
            alignment=TA_CENTER
        )
        today = datetime.now().strftime('%B %d, %Y')
        story.append(Paragraph(f'Generated on {today}', date_style))
        
        return story
    
    def _build_executive_summary(self, analysis: Dict) -> List:
        """Executive summary page."""
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(self._section_title('Executive Summary'))
        story.append(Spacer(1, 5*mm))
        
        # Overall assessment
        wr = analysis.get('win_rate', 0)
        esi = analysis.get('esi', 0)
        pvs = analysis.get('pvs', 0)
        
        if wr >= 55 and esi >= 0.7:
            verdict = "STRONG EDGE DETECTED"
            verdict_color = COLORS['success']
        elif wr >= 50 and esi >= 0.6:
            verdict = "EDGE PRESENT"
            verdict_color = COLORS['primary']
        elif wr >= 45:
            verdict = "MARGINAL EDGE"
            verdict_color = COLORS['warning']
        else:
            verdict = "NO CLEAR EDGE"
            verdict_color = COLORS['danger']
        
        verdict_style = ParagraphStyle(
            'Verdict',
            parent=styles['Heading2'],
            fontSize=20,
            textColor=verdict_color,
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(verdict, verdict_style))
        story.append(Spacer(1, 5*mm))
        
        # Key metrics grid
        metrics_data = [
            ['METRIC', 'VALUE', 'ASSESSMENT'],
            ['Win Rate', f'{wr:.1f}%', self._assess_metric('wr', wr)],
            ['Profit Factor', f'{analysis.get("profit_factor", 0):.2f}', 
             self._assess_metric('pf', analysis.get('profit_factor', 0))],
            ['Expectancy', f'{analysis.get("expectancy", 0):.2f}R', 
             self._assess_metric('exp', analysis.get('expectancy', 0))],
            ['ESI', f'{esi:.2f}', self._assess_metric('esi', esi)],
            ['PVS', f'{pvs:.2f}', self._assess_metric('pvs', pvs)],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[50*mm, 40*mm, 60*mm])
        metrics_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['neutral_dark']),
            ('FONTNAME', (0, 1), (1, -1), 'Helvetica'),
            ('FONTNAME', (2, 1), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            # Styling
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['neutral_light']),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(metrics_table)
        
        # Top findings
        if analysis.get('insights', {}).get('critical'):
            story.append(Spacer(1, 10*mm))
            story.append(self._subsection_title('Critical Findings'))
            
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=COLORS['neutral_dark']
            )
            
            for i, insight in enumerate(analysis['insights']['critical'][:3], 1):
                text = f"<b>{i}.</b> {insight.get('observation', '')}"
                story.append(Paragraph(text, body_style))
                story.append(Spacer(1, 3*mm))
        
        return story
    
    def _build_metrics_page(self, analysis: Dict) -> List:
        """Detailed metrics page."""
        story = []
        
        story.append(self._section_title('Performance Metrics'))
        story.append(Spacer(1, 5*mm))
        
        # All metrics in clean grid
        all_metrics = [
            ['METRIC', 'VALUE'],
            ['Total Trades', str(analysis.get('total_trades', 0))],
            ['Winning Trades', str(analysis.get('wins', 0))],
            ['Losing Trades', str(analysis.get('losses', 0))],
            ['Win Rate', f"{analysis.get('win_rate', 0):.1f}%"],
            ['Profit Factor', f"{analysis.get('profit_factor', 0):.2f}"],
            ['Expectancy', f"{analysis.get('expectancy', 0):.2f}R"],
            ['Total Profit', f"{analysis.get('total_profit_r', 0):.2f}R"],
            ['Sharpe Ratio', f"{analysis.get('sharpe_ratio', 0):.2f}"],
            ['Max Drawdown', f"{analysis.get('max_drawdown', 0):.1f}%"],
            ['ESI Score', f"{analysis.get('esi', 0):.2f}"],
            ['PVS Score', f"{analysis.get('pvs', 0):.2f}"],
        ]
        
        metrics_table = Table(all_metrics, colWidths=[90*mm, 60*mm])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['neutral_dark']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['neutral_dark']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['neutral_light']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORS['neutral_light']]),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(metrics_table)
        
        return story
    
    def _build_timing_page(self, timing: Dict) -> List:
        """Timing intelligence page."""
        story = []
        
        story.append(self._section_title('Timing Intelligence'))
        story.append(Spacer(1, 5*mm))
        
        # Session breakdown
        if timing.get('sessions'):
            story.append(self._subsection_title('Session Performance'))
            
            session_data = [['SESSION', 'TRADES', 'WIN RATE', 'EXPECTANCY', 'VERDICT']]
            
            for session in ['Tokyo', 'London', 'NY']:
                if session in timing['sessions']:
                    s = timing['sessions'][session]
                    session_data.append([
                        session,
                        str(s.get('trades', 0)),
                        f"{s.get('win_rate', 0):.1f}%",
                        f"{s.get('expectancy', 0):.2f}R",
                        s.get('verdict', 'N/A')
                    ])
            
            session_table = Table(session_data, colWidths=[30*mm, 25*mm, 30*mm, 30*mm, 35*mm])
            session_table.setStyle(self._get_data_table_style())
            story.append(session_table)
            story.append(Spacer(1, 5*mm))
        
        # Best time window
        if timing.get('best_window'):
            story.append(self._info_box(
                'Peak Performance',
                f"{timing['best_window'].get('hour', 'N/A')}: "
                f"{timing['best_window'].get('win_rate', 0):.1f}% WR "
                f"({timing['best_window'].get('trades', 0)} trades)",
                COLORS['success']
            ))
        
        return story
    
    def _build_directional_page(self, directional: Dict) -> List:
        """Directional analysis page."""
        story = []
        
        story.append(self._section_title('Directional Analysis'))
        story.append(Spacer(1, 5*mm))
        
        # LONG vs SHORT comparison
        dir_data = [['DIRECTION', 'TRADES', 'WIN RATE', 'EXPECTANCY', 'EDGE']]
        
        for direction in ['LONG', 'SHORT']:
            if direction in directional:
                d = directional[direction]
                dir_data.append([
                    direction,
                    str(d.get('trades', 0)),
                    f"{d.get('win_rate', 0):.1f}%",
                    f"{d.get('expectancy', 0):.2f}R",
                    d.get('edge_strength', 'NONE')
                ])
        
        dir_table = Table(dir_data, colWidths=[35*mm, 25*mm, 35*mm, 35*mm, 35*mm])
        dir_table.setStyle(self._get_data_table_style())
        story.append(dir_table)
        
        # Bias insight
        if directional.get('bias'):
            story.append(Spacer(1, 5*mm))
            story.append(self._info_box(
                'Directional Bias',
                directional['bias'].get('description', ''),
                COLORS['primary']
            ))
        
        return story
    
    def _build_execution_page(self, execution: Dict) -> List:
        """Execution quality page."""
        story = []
        
        story.append(self._section_title('Execution Quality'))
        story.append(Spacer(1, 5*mm))
        
        # Quality score
        score = execution.get('quality_score', 0)
        score_color = (COLORS['success'] if score >= 80 else 
                      COLORS['primary'] if score >= 60 else 
                      COLORS['warning'] if score >= 40 else 
                      COLORS['danger'])
        
        story.append(self._info_box(
            'Overall Score',
            f"{score}/100",
            score_color
        ))
        story.append(Spacer(1, 5*mm))
        
        # Issues
        if execution.get('issues'):
            story.append(self._subsection_title('Identified Issues'))
            
            styles = getSampleStyleSheet()
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=COLORS['neutral_dark']
            )
            
            for issue in execution['issues']:
                text = f"• {issue.get('description', '')}"
                story.append(Paragraph(text, body_style))
                story.append(Spacer(1, 2*mm))
        
        return story
    
    def _build_insights_page(self, insights: Dict) -> List:
        """Key insights summary page."""
        story = []
        
        story.append(self._section_title('Key Insights'))
        story.append(Spacer(1, 5*mm))
        
        styles = getSampleStyleSheet()
        
        # Critical insights
        if insights.get('critical'):
            story.append(self._subsection_title('Critical Patterns'))
            
            for i, insight in enumerate(insights['critical'], 1):
                # Title
                title_style = ParagraphStyle(
                    'InsightTitle',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=COLORS['danger'],
                    fontName='Helvetica-Bold',
                    spaceAfter=3
                )
                story.append(Paragraph(f"{i}. {insight.get('category', 'Finding')}", title_style))
                
                # Observation
                body_style = ParagraphStyle(
                    'Body',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    textColor=COLORS['neutral_dark'],
                    leftIndent=5*mm
                )
                story.append(Paragraph(insight.get('observation', ''), body_style))
                story.append(Spacer(1, 5*mm))
        
        # Notable insights
        if insights.get('notable'):
            story.append(self._subsection_title('Notable Patterns'))
            
            for insight in insights['notable']:
                body_style = ParagraphStyle(
                    'Body',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    textColor=COLORS['neutral_dark']
                )
                story.append(Paragraph(f"• {insight.get('observation', '')}", body_style))
                story.append(Spacer(1, 3*mm))
        
        return story
    
    def _build_disclaimer(self) -> List:
        """Legal disclaimer page."""
        story = []
        
        story.append(self._section_title('Important Disclaimer'))
        story.append(Spacer(1, 5*mm))
        
        styles = getSampleStyleSheet()
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=COLORS['neutral'],
            alignment=TA_LEFT
        )
        
        disclaimer_text = """
        <b>No Financial Advice:</b> This report provides statistical analysis of historical 
        trading data only. It does not constitute financial advice, trading recommendations, 
        or investment guidance.
        <br/><br/>
        <b>Past Performance:</b> Past performance is not indicative of future results. 
        Market conditions change continuously and historical patterns may not repeat.
        <br/><br/>
        <b>Risk Warning:</b> Trading financial instruments involves substantial risk of loss. 
        You should not trade with money you cannot afford to lose.
        <br/><br/>
        <b>Statistical Analysis:</b> All observations in this report are based purely on 
        statistical patterns in the provided data. Users must conduct their own due diligence 
        and make independent decisions.
        <br/><br/>
        <b>No Guarantees:</b> EdgeLab makes no guarantees about the accuracy, completeness, 
        or reliability of any analysis. Users accept all risks associated with trading decisions.
        <br/><br/>
        <b>Educational Purpose:</b> This analysis is provided for educational and informational 
        purposes only.
        """
        
        story.append(Paragraph(disclaimer_text, disclaimer_style))
        
        return story
    
    # Helper methods for styling
    
    def _section_title(self, text: str) -> Paragraph:
        """Create section title."""
        styles = getSampleStyleSheet()
        style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=COLORS['primary'],
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        return Paragraph(text, style)
    
    def _subsection_title(self, text: str) -> Paragraph:
        """Create subsection title."""
        styles = getSampleStyleSheet()
        style = ParagraphStyle(
            'SubsectionTitle',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=COLORS['neutral_dark'],
            fontName='Helvetica-Bold',
            spaceAfter=5
        )
        return Paragraph(text, style)
    
    def _info_box(self, title: str, content: str, color) -> Table:
        """Create colored info box."""
        data = [[title], [content]]
        table = Table(data, colWidths=[self.content_width])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, 1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, 1), COLORS['neutral_dark']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, color),
        ]))
        return table
    
    def _get_data_table_style(self) -> TableStyle:
        """Standard data table styling."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['neutral_dark']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['neutral_light']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORS['neutral_light']]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ])
    
    def _assess_metric(self, metric_type: str, value: float) -> str:
        """Assess metric value."""
        if metric_type == 'wr':
            if value >= 55: return 'STRONG'
            if value >= 50: return 'GOOD'
            if value >= 45: return 'FAIR'
            return 'WEAK'
        elif metric_type == 'pf':
            if value >= 2.0: return 'EXCELLENT'
            if value >= 1.5: return 'GOOD'
            if value >= 1.2: return 'FAIR'
            return 'POOR'
        elif metric_type == 'exp':
            if value >= 0.5: return 'STRONG'
            if value >= 0.3: return 'GOOD'
            if value >= 0.1: return 'FAIR'
            return 'WEAK'
        elif metric_type in ['esi', 'pvs']:
            if value >= 0.8: return 'EXCELLENT'
            if value >= 0.7: return 'GOOD'
            if value >= 0.6: return 'FAIR'
            return 'NEEDS WORK'
        return 'N/A'
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to pages."""
        canvas.saveState()
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(COLORS['neutral'])
        
        footer_text = f"EdgeLab Analysis Report | Generated {datetime.now().strftime('%Y-%m-%d')}"
        canvas.drawCentredString(
            self.width / 2,
            15*mm,
            footer_text
        )
        
        # Page number
        page_num = f"Page {doc.page}"
        canvas.drawRightString(
            self.width - self.margin,
            15*mm,
            page_num
        )
        
        canvas.restoreState()