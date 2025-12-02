"""
HTML-based PDF report generator for EdgeLab
Uses pdfkit + wkhtmltopdf for professional PDF output with EdgeLab branding
"""

import pdfkit
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os


class HTMLReportGenerator:
    """Generate professional PDFs from HTML templates with EdgeLab branding"""
    
    def __init__(self):
        """Initialize with wkhtmltopdf configuration"""
        # Point to wkhtmltopdf binary
        self.config = pdfkit.configuration(
            wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        )
        
        # Setup Jinja2 template environment
        template_dir = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'templates', 
            'reports'
        )
        self.env = Environment(loader=FileSystemLoader(template_dir))
        
        # PDF generation options
        self.pdf_options = {
            'page-size': 'A4',
            'margin-top': '0mm',
            'margin-right': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None,
            'print-media-type': None,
        }
    
    def generate_report(self, results, trades, strategy=None):
        """
        Generate PDF report from analysis results
        
        Args:
            results (dict): Analysis results with metrics and insights
            trades (DataFrame): Trading data
            strategy (dict): Optional strategy definition for backtests
        
        Returns:
            bytes: PDF file content
        """
        # Prepare template context
        context = {
            # Basic info
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'total_trades': len(trades),
            'strategy': strategy,
            
            # Core metrics
            'results': results,
            
            # Pattern analysis (if available)
            'timing': results.get('timing_analysis', {}),
            'directional': results.get('directional_analysis', {}),
            'execution': results.get('execution_analysis', {}),
            'insights': results.get('insights', {}),
        }
        
        # Render HTML from template
        template = self.env.get_template('report_edgelab.html')
        html_content = template.render(**context)
        
        # Convert HTML to PDF
        pdf_bytes = pdfkit.from_string(
            html_content,
            False,  # False = return bytes instead of file
            configuration=self.config,
            options=self.pdf_options
        )
        
        return pdf_bytes
