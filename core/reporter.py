"""
reporter.py
===========

PDF report generation for EdgeLab.
Creates professional analysis reports from AnalysisResult.

Usage:
    generator = ReportGenerator()
    pdf_bytes = generator.create_report(analysis_result, trades)
    
Output:
    Professional PDF with metrics, charts, and recommendations

Author: EdgeLab Development Team
Version: 1.0
"""

from typing import List
from datetime import datetime
from io import BytesIO
import tempfile
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

from core.edgelab_schema import EdgeLabTrade, AnalysisResult


class ChartBuilder:
    """
    Build charts for PDF reports using matplotlib.
    
    Charts:
    - Equity curve (cumulative P&L over time)
    - Win/Loss distribution
    - Session performance
    """
    
    def __init__(self):
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def create_equity_curve(self, trades: List[EdgeLabTrade], width: float = 6, height: float = 3) -> str:
        """
        Create equity curve chart showing cumulative profit over time.
        
        Args:
            trades: List of trades
            width: Chart width in inches
            height: Chart height in inches
            
        Returns:
            Path to saved PNG image
        """
        
        fig, ax = plt.subplots(figsize=(width, height))
        
        # Calculate cumulative equity
        timestamps = [t.timestamp_close for t in trades]
        cumulative_r = []
        running_total = 0.0
        
        for trade in trades:
            running_total += trade.profit_r
            cumulative_r.append(running_total)
        
        # Plot equity curve
        ax.plot(timestamps, cumulative_r, linewidth=2, color='#2c5aa0', label='Equity Curve')
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        
        # Formatting
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Cumulative Profit (R)', fontsize=10)
        ax.set_title('Equity Curve', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # Save to file
        temp_dir = tempfile.gettempdir()
        chart_path = os.path.join(temp_dir, 'equity_curve.png')
        
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def create_winloss_distribution(self, trades: List[EdgeLabTrade], width: float = 6, height: float = 3) -> str:
        """
        Create bar chart showing distribution of wins vs losses.
        
        Returns:
            Path to saved PNG image
        """
        
        fig, ax = plt.subplots(figsize=(width, height))
        
        # Count results
        wins = sum(1 for t in trades if t.result == "WIN")
        losses = sum(1 for t in trades if t.result == "LOSS")
        timeouts = sum(1 for t in trades if t.result == "TIMEOUT")
        
        # Create bar chart
        categories = ['Wins', 'Losses', 'Timeouts']
        values = [wins, losses, timeouts]
        colors_list = ['green', 'red', 'orange']
        
        bars = ax.bar(categories, values, color=colors_list, alpha=0.7)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Formatting
        ax.set_ylabel('Count', fontsize=10)
        ax.set_title('Trade Distribution', fontsize=12, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        
        # Save to file
        temp_dir = tempfile.gettempdir()
        chart_path = os.path.join(temp_dir, 'winloss_distribution.png')
        
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def create_session_performance(self, trades: List[EdgeLabTrade], width: float = 6, height: float = 3) -> str:
        """
        Create bar chart showing performance by trading session.
        
        Returns:
            Path to saved PNG image
        """
        
        fig, ax = plt.subplots(figsize=(width, height))
        
        # Group by session
        sessions = {}
        for trade in trades:
            session = trade.session if hasattr(trade, 'session') else "Unknown"
            if session not in sessions:
                sessions[session] = {'wins': 0, 'total': 0, 'profit': 0.0}
            
            sessions[session]['total'] += 1
            sessions[session]['profit'] += trade.profit_r
            if trade.result == "WIN":
                sessions[session]['wins'] += 1
        
        # Prepare data
        session_names = list(sessions.keys())
        profits = [sessions[s]['profit'] for s in session_names]
        
        # Create bar chart
        colors_list = ['green' if p > 0 else 'red' for p in profits]
        bars = ax.bar(session_names, profits, color=colors_list, alpha=0.7)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}R',
                   ha='center', va='bottom' if height > 0 else 'top', 
                   fontsize=10, fontweight='bold')
        
        # Formatting
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_ylabel('Total Profit (R)', fontsize=10)
        ax.set_title('Performance by Trading Session', fontsize=12, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        
        # Save to file
        temp_dir = tempfile.gettempdir()
        chart_path = os.path.join(temp_dir, 'session_performance.png')
        
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path


class ReportGenerator:
    """
    Generate professional PDF reports from analysis results.
    
    Features:
    - Executive summary
    - Detailed metrics table
    - Charts (equity curve, heatmaps)
    - Actionable recommendations
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """
        Define custom text styles for report.
        """
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=20
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#2c5aa0'),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
    
    def create_report(self, 
                     results: AnalysisResult, 
                     trades: List[EdgeLabTrade],
                     filename: str = "edgelab_analysis.pdf") -> bytes:
        """
        Generate complete PDF report with charts.
        
        Args:
            results: AnalysisResult from analyzer
            trades: Original trade list
            filename: Output filename
            
        Returns:
            PDF as bytes (can be saved or downloaded)
        """
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Add title page
        story.extend(self._build_title_page(results, trades))
        
        # Add metrics summary
        story.extend(self._build_metrics_summary(results))
        
        # Add charts
        story.extend(self._build_charts_section(trades))
        
        # Add recommendations
        story.extend(self._build_recommendations(results))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _build_title_page(self, results: AnalysisResult, trades: List[EdgeLabTrade]) -> list:
        """
        Create title page with executive summary.
        """
        
        elements = []
        
        # Title
        title = Paragraph("EdgeLab Trading Analysis", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Date range
        if trades:
            start_date = trades[0].timestamp_open.strftime("%Y-%m-%d")
            end_date = trades[-1].timestamp_close.strftime("%Y-%m-%d")
            date_range = Paragraph(
                f"<b>Analysis Period:</b> {start_date} to {end_date}",
                self.styles['Normal']
            )
            elements.append(date_range)
            elements.append(Spacer(1, 0.2 * inch))
        
        # Generated date
        gen_date = Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
            self.styles['Normal']
        )
        elements.append(gen_date)
        elements.append(Spacer(1, 0.5 * inch))
        
        # Key metrics highlight
        key_metrics = [
            ['Metric', 'Value', 'Status'],
            ['Total Trades', str(results.total_trades), ''],
            ['Win Rate', f"{results.winrate}%", self._get_status(results.winrate, 50, 55)],
            ['Profit Factor', str(results.profit_factor), self._get_status(results.profit_factor, 1.5, 2.0)],
            ['Expectancy', f"{results.expectancy}R", self._get_status(results.expectancy, 0.3, 0.5)],
            ['ESI Score', str(results.esi), self._get_status(results.esi, 0.6, 0.7)],
            ['PVS Score', str(results.pvs), self._get_status(results.pvs, 0.6, 0.8)],
        ]
        
        table = Table(key_metrics, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_metrics_summary(self, results: AnalysisResult) -> list:
        """
        Create detailed metrics table.
        """
        
        elements = []
        
        # Section title
        title = Paragraph("Detailed Performance Metrics", self.styles['CustomSubtitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Metrics table
        metrics_data = [
            ['Category', 'Metric', 'Value'],
            ['Trading Activity', 'Total Trades', str(results.total_trades)],
            ['', 'Wins', str(results.wins)],
            ['', 'Losses', str(results.losses)],
            ['Performance', 'Win Rate', f"{results.winrate}%"],
            ['', 'Profit Factor', str(results.profit_factor)],
            ['', 'Expectancy', f"{results.expectancy}R"],
            ['', 'Total Profit', f"{results.total_profit_r}R"],
            ['Risk Management', 'Average Win', f"{results.avg_win_r}R"],
            ['', 'Average Loss', f"{results.avg_loss_r}R"],
            ['', 'Max Drawdown', f"{results.max_drawdown_pct}%"],
            ['Advanced', 'ESI (Edge Stability)', str(results.esi)],
            ['', 'PVS (Prop Score)', str(results.pvs)],
            ['', 'Sharpe Ratio', str(results.sharpe_ratio)],
            ['Patterns', 'Best Session', results.best_session],
            ['', 'Best Hour', results.best_hour],
        ]
        
        table = Table(metrics_data, colWidths=[1.8*inch, 2.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    def _build_charts_section(self, trades: List[EdgeLabTrade]) -> list:
        """
        Create charts section with visualizations.
        """
        
        elements = []
        
        # Section title
        title = Paragraph("Visual Analysis", self.styles['CustomSubtitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Generate charts
        chart_builder = ChartBuilder()
        
        try:
            # Equity curve
            equity_path = chart_builder.create_equity_curve(trades, width=5.5, height=2.5)
            img = Image(equity_path, width=5.5*inch, height=2.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Win/Loss distribution
            winloss_path = chart_builder.create_winloss_distribution(trades, width=5.5, height=2.5)
            img = Image(winloss_path, width=5.5*inch, height=2.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2 * inch))
            
            # Session performance
            session_path = chart_builder.create_session_performance(trades, width=5.5, height=2.5)
            img = Image(session_path, width=5.5*inch, height=2.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.2 * inch))
            
        except Exception as e:
            # If chart generation fails, show error message
            error_msg = Paragraph(
                f"<i>Chart generation unavailable: {str(e)}</i>",
                self.styles['Normal']
            )
            elements.append(error_msg)
        
        return elements
    
    def _build_recommendations(self, results: AnalysisResult) -> list:
        """
        Create recommendations section.
        """
        
        elements = []
        
        # Section title
        title = Paragraph("Analysis & Recommendations", self.styles['CustomSubtitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))
        
        # Recommendation text
        rec_text = Paragraph(results.recommendation, self.styles['Normal'])
        elements.append(rec_text)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Disclaimer
        disclaimer = Paragraph(
            "<i>Disclaimer: This analysis is for educational purposes only. "
            "Past performance does not guarantee future results. "
            "Trading involves substantial risk of loss.</i>",
            self.styles['Normal']
        )
        elements.append(disclaimer)
        
        return elements
    
    def _get_status(self, value: float, threshold_ok: float, threshold_good: float) -> str:
        """
        Determine status emoji/text based on thresholds.
        """
        
        if value >= threshold_good:
            return "✓✓"
        elif value >= threshold_ok:
            return "✓"
        else:
            return "✗"