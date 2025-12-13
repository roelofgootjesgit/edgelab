"""
EdgeLab PDF Report Generator - Playwright Version
Generates professional PDF reports using Playwright (Chrome headless)
"""

from playwright.sync_api import sync_playwright
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os


class PlaywrightReportGenerator:
    """
    Generate PDF reports using Playwright's Chrome rendering engine.
    
    Benefits over wkhtmltopdf:
    - Modern CSS support (gradients, flexbox, grid)
    - Reliable image loading (base64, URLs, local files)
    - JavaScript execution support
    - Active development
    """
    
    def __init__(self, template_dir='templates/reports'):
        """Initialize the reporter with template directory."""
        self.template_dir = template_dir
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
    def generate_report(self, results, trades, strategy=None, insights=None):
        """
        Generate a PDF report from trading results.
        
        Args:
            results: AnalysisResults object with metrics
            trades: List of QuantMetricsTrade objects
            strategy: Optional strategy info
            insights: Optional dict with pattern analysis insights
            
        Returns:
            bytes: PDF file content
        """
        # Load template
        template = self.env.get_template('report_edgelab.html')
        
        # Prepare context
        context = self._prepare_context(results, trades, strategy, insights)
        
        # Render HTML
        html_content = template.render(**context)
        
        # Generate PDF using Playwright
        pdf_bytes = self._html_to_pdf(html_content)
        
        return pdf_bytes
    
    def _prepare_context(self, results, trades, strategy, insights):
        """Prepare template context from analysis results."""
        
        # Default insights if not provided
        if insights is None:
            insights = {
                'critical_findings': [],
                'notable_patterns': []
            }
        
        # Timing analysis (from session data if available)
        timing = {
            'best_session': getattr(results, 'best_session', 'NY Session'),
            'worst_session': getattr(results, 'worst_session', 'London')
        }
        
        context = {
            'results': results,
            'total_trades': len(trades),
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'insights': type('Insights', (), insights),  # Convert dict to object
            'timing': type('Timing', (), timing)
        }
        
        return context
    
    def _html_to_pdf(self, html_content):
        """
        Convert HTML to PDF using Playwright.
        
        Args:
            html_content: HTML string
            
        Returns:
            bytes: PDF content
        """
        with sync_playwright() as p:
            # Launch browser (headless)
            browser = p.chromium.launch(headless=True)
            
            # Create page
            page = browser.new_page()
            
            # Set content
            page.set_content(html_content, wait_until='load')
            
            # Wait a bit for any base64 images to decode
            page.wait_for_timeout(1000)
            
            # Generate PDF
            pdf_bytes = page.pdf(
                format='A4',
                margin={
                    'top': '0mm',
                    'right': '0mm',
                    'bottom': '0mm',
                    'left': '0mm'
                },
                print_background=True,  # Important for gradients/colors
                prefer_css_page_size=False
            )
            
            # Cleanup
            browser.close()
            
            return pdf_bytes
    
    def save_report(self, results, trades, output_path, strategy=None, insights=None):
        """
        Generate and save PDF report to file.
        
        Args:
            results: AnalysisResults object
            trades: List of trades
            output_path: Path to save PDF
            strategy: Optional strategy info
            insights: Optional insights dict
        """
        pdf_bytes = self.generate_report(results, trades, strategy, insights)
        
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return output_path
