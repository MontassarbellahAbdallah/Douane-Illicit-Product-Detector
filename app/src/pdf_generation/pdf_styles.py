"""
PDF Styles Module
Handles all PDF styling, headers, footers, and formatting functionality.
"""

import logging
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import TableStyle

# Setup logging
logger = logging.getLogger(__name__)

# Color constants for consistent theming
COLORS = {
    'HEADER_BG': colors.HexColor('#1e40af'),
    'HEADER_TEXT': colors.white,
    'SUBHEADER_TEXT': colors.HexColor('#7c3aed'),
    'DOMAIN_TEXT': colors.HexColor('#ef4444'),
    'FIELD_LABEL': colors.HexColor('#374151'),
    'FIELD_VALUE': colors.HexColor('#1f2937'),
    'FOOTER_TEXT': colors.HexColor('#6b7280'),
    'TABLE_HEADER': colors.HexColor('#f3f4f6'),
    'DOMAIN_SECTION': colors.HexColor('#f0f9ff'),
    'CONTACT_SECTION': colors.HexColor('#f3f4f6'),
    'NAMESERVER_SECTION': colors.HexColor('#fef3c7'),
    'PRODUCT_SECTION': colors.HexColor('#f9fafb'),
    'SUSPICIOUS_SECTION': colors.HexColor('#fef3c7'),
    'GRID_LINES': colors.HexColor('#e5e7eb')
}

class PDFStyles:
    """Handles PDF styling and layout configuration"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Header style
        self.styles.add(ParagraphStyle(
            name='Header',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=COLORS['HEADER_TEXT'],
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Subheader style
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=COLORS['SUBHEADER_TEXT'],
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Domain style
        self.styles.add(ParagraphStyle(
            name='Domain',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=COLORS['DOMAIN_TEXT'],
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Field label style
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=COLORS['FIELD_LABEL'],
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        # Field value style
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=COLORS['FIELD_VALUE'],
            spaceAfter=8
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=COLORS['FOOTER_TEXT'],
            alignment=TA_CENTER,
            spaceBefore=12
        ))

    def create_header(self, canvas_obj, doc):
        """Create header for each page"""
        canvas_obj.saveState()
        
        # Draw header background
        canvas_obj.setFillColor(COLORS['HEADER_BG'])
        canvas_obj.rect(0, 750, 612, 50, fill=1)
        
        # Draw header text
        canvas_obj.setFillColor(COLORS['HEADER_TEXT'])
        canvas_obj.setFont('Helvetica-Bold', 12)
        canvas_obj.drawString(30, 765, "Douane - Détecteur de Produits Illicites")
        
        # Draw page number
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.drawString(500, 765, f"Page {doc.page}")
        
        canvas_obj.restoreState()

    def create_footer(self, canvas_obj, doc):
        """Create footer for each page"""
        canvas_obj.saveState()
        
        # Draw footer line
        canvas_obj.setStrokeColor(COLORS['GRID_LINES'])
        canvas_obj.setLineWidth(1)
        canvas_obj.line(30, 50, 582, 50)
        
        # Draw footer text
        canvas_obj.setFillColor(COLORS['FOOTER_TEXT'])
        canvas_obj.setFont('Helvetica-Oblique', 8)
        canvas_obj.drawString(30, 35, "Confidentiel - Tunisian Customs Authority")
        canvas_obj.drawString(450, 35, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        canvas_obj.restoreState()

    def format_field_value(self, value):
        """Format field values for better display"""
        if value is None:
            return "Non disponible"
        elif isinstance(value, list):
            if len(value) == 1:
                return self.safe_str(value[0])
            elif len(value) > 1:
                return ", ".join(self.safe_str(v) for v in value)
        elif isinstance(value, datetime):
            return value.strftime('%d/%m/%Y %H:%M:%S')
        return self.safe_str(value)
    
    def safe_str(self, text):
        """Safely convert text to string with proper Unicode handling"""
        if isinstance(text, str):
            try:
                # First try normal UTF-8
                return text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            except:
                try:
                    # Try latin1 to UTF-8 conversion for double-encoded text
                    return text.encode('latin1').decode('utf-8', errors='replace')
                except:
                    try:
                        # Try unicode escape decoding
                        return text.encode('utf-8').decode('unicode_escape')
                    except:
                        return str(text)
        return str(text)

    def get_table_style(self, section_type='general'):
        """Get appropriate table style based on section type"""
        base_style = [
            ('GRID', (0, 0), (-1, -1), 1, COLORS['GRID_LINES']),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        if section_type == 'summary':
            base_style.extend([
                ('BACKGROUND', (0, 0), (0, -1), COLORS['TABLE_HEADER']),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ])
        elif section_type == 'domain':
            base_style.extend([
                ('BACKGROUND', (0, 0), (0, -1), COLORS['DOMAIN_SECTION']),
            ])
        elif section_type == 'contact':
            base_style.extend([
                ('BACKGROUND', (0, 0), (0, -1), COLORS['CONTACT_SECTION']),
            ])
        elif section_type == 'nameserver':
            base_style.extend([
                ('BACKGROUND', (0, 0), (0, -1), COLORS['NAMESERVER_SECTION']),
            ])
        elif section_type == 'product':
            base_style.extend([
                ('BACKGROUND', (0, 0), (0, -1), COLORS['PRODUCT_SECTION']),
            ])
        elif section_type == 'suspicious':
            base_style.extend([
                ('BACKGROUND', (0, 0), (0, -1), COLORS['SUSPICIOUS_SECTION']),
            ])
        
        return TableStyle(base_style)

    def get_field_label_style(self):
        """Get field label style"""
        return self.styles['FieldLabel']
    
    def get_field_value_style(self):
        """Get field value style"""
        return self.styles['FieldValue']
    
    def get_header_style(self):
        """Get header style"""
        return self.styles['Header']
    
    def get_subheader_style(self):
        """Get subheader style"""
        return self.styles['SubHeader']
    
    def get_domain_style(self):
        """Get domain style"""
        return self.styles['Domain']
    
    def get_footer_style(self):
        """Get footer style"""
        return self.styles['Footer']