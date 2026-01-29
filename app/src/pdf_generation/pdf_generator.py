# Developed by Montassar Bellah Abdallah

import os
import logging
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Frame, PageTemplate, PageBreak
)

# Setup logging for error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PDF output directory
pdf_output_dir = "./pdf-output"
os.makedirs(pdf_output_dir, exist_ok=True)

# Import our modular components
from .pdf_styles import PDFStyles
from .pdf_content import PDFContent

class PDFGenerator:
    """PDF Generator for WHOIS information with professional styling"""
    
    def __init__(self):
        self.styles = PDFStyles()
        self.content = PDFContent(self.styles)
    
    def generate_whois_pdf(self, domain: str, whois_info: dict, error: str = None):
        """
        Generate a professional PDF with WHOIS information
        
        Args:
            domain (str): The domain name
            whois_info (dict): WHOIS information dictionary
            error (str, optional): Error message if WHOIS lookup failed
        
        Returns:
            bytes: PDF content as bytes
        """
        try:
            # Create buffer for PDF
            buffer = BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=60,
                bottomMargin=60
            )
            
            # Create page template with header and footer
            frame = Frame(
                doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                id='normal'
            )
            
            template = PageTemplate(
                id='whois_template',
                frames=frame,
                onPage=self.styles.create_header,
                onPageEnd=self.styles.create_footer
            )
            
            doc.addPageTemplates([template])
            
            # Build PDF content using our content module
            story = self.content.build_whois_content(domain, whois_info, error)
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"WHOIS PDF generated successfully for domain: {domain}")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating WHOIS PDF for domain {domain}: {str(e)}")
            raise Exception(f"Erreur lors de la génération du PDF WHOIS: {str(e)}")

    def generate_analysis_pdf(self, product_category: str, products: list, search_results: list = None, using_fallback: bool = False):
        """
        Generate a professional PDF with analysis results
        
        Args:
            product_category (str): The product category that was analyzed
            products (list): List of analyzed products with their details
            search_results (list, optional): List of search results that weren't fully analyzed
            using_fallback (bool): Whether fallback data is being used
        
        Returns:
            bytes: PDF content as bytes
        """
        try:
            # Create buffer for PDF
            buffer = BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=30,
                leftMargin=30,
                topMargin=60,
                bottomMargin=60
            )
            
            # Create page template with header and footer
            frame = Frame(
                doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                id='normal'
            )
            
            template = PageTemplate(
                id='analysis_template',
                frames=frame,
                onPage=self.styles.create_header,
                onPageEnd=self.styles.create_footer
            )
            
            doc.addPageTemplates([template])
            
            # Build PDF content using our content module
            story = self.content.build_analysis_content(
                product_category, products, search_results, using_fallback
            )
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Analysis PDF generated successfully for category: {product_category}")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating analysis PDF for category {product_category}: {str(e)}")
            raise Exception(f"Erreur lors de la génération du PDF d'analyse: {str(e)}")

def generate_whois_pdf(domain: str, whois_info: dict = None, error: str = None):
    """
    Convenience function to generate WHOIS PDF
    
    Args:
        domain (str): The domain name
        whois_info (dict, optional): WHOIS information dictionary
        error (str, optional): Error message if WHOIS lookup failed
    
    Returns:
        bytes: PDF content as bytes
    """
    generator = PDFGenerator()
    return generator.generate_whois_pdf(domain, whois_info or {}, error)

def generate_analysis_pdf(product_category: str, products: list, search_results: list = None, using_fallback: bool = False):
    """
    Convenience function to generate analysis PDF
    
    Args:
        product_category (str): The product category that was analyzed
        products (list): List of analyzed products with their details
        search_results (list, optional): List of search results that weren't fully analyzed
        using_fallback (bool): Whether fallback data is being used
    
    Returns:
        bytes: PDF content as bytes
    """
    generator = PDFGenerator()
    return generator.generate_analysis_pdf(product_category, products, search_results or [], using_fallback)