# Developed by Montassar Bellah Abdallah

import os
import logging
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Frame, PageTemplate, 
)

from reportlab.lib.enums import TA_CENTER


# Setup logging for error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PDF output directory
pdf_output_dir = "./pdf-output"
os.makedirs(pdf_output_dir, exist_ok=True)

class PDFGenerator:
    """PDF Generator for WHOIS information with professional styling"""
    
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
            textColor=colors.HexColor('#1e40af'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Subheader style
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#7c3aed'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Domain style
        self.styles.add(ParagraphStyle(
            name='Domain',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#ef4444'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Field label style
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        # Field value style
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=8
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            spaceBefore=12
        ))

    def _create_header(self, canvas_obj, doc):
        """Create header for each page"""
        canvas_obj.saveState()
        
        # Draw header background
        canvas_obj.setFillColor(colors.HexColor('#1e40af'))
        canvas_obj.rect(0, 750, 612, 50, fill=1)
        
        # Draw header text
        canvas_obj.setFillColor(colors.white)
        canvas_obj.setFont('Helvetica-Bold', 12)
        canvas_obj.drawString(30, 765, "Douane - Détecteur de Produits Illicites")
        
        # Draw page number
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.drawString(500, 765, f"Page {doc.page}")
        
        canvas_obj.restoreState()

    def _create_footer(self, canvas_obj, doc):
        """Create footer for each page"""
        canvas_obj.saveState()
        
        # Draw footer line
        canvas_obj.setStrokeColor(colors.HexColor('#e5e7eb'))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(30, 50, 582, 50)
        
        # Draw footer text
        canvas_obj.setFillColor(colors.HexColor('#6b7280'))
        canvas_obj.setFont('Helvetica-Oblique', 8)
        canvas_obj.drawString(30, 35, "Confidentiel - Tunisian Customs Authority")
        canvas_obj.drawString(450, 35, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        canvas_obj.restoreState()

    def _format_field_value(self, value):
        """Format field values for better display"""
        if value is None:
            return "Non disponible"
        elif isinstance(value, list):
            if len(value) == 1:
                return str(value[0])
            elif len(value) > 1:
                return ", ".join(str(v) for v in value)
        elif isinstance(value, datetime):
            return value.strftime('%d/%m/%Y %H:%M:%S')
        return str(value)

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
                id='whos_template',
                frames=frame,
                onPage=self._create_header,
                onPageEnd=self._create_footer
            )
            
            doc.addPageTemplates([template])
            
            # Build PDF content
            story = []
            
            # Title section
            #story.append(Paragraph("🛡️ DOUANE - RECHERCHE WHOIS", self.styles['Header']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Informations d'enregistrement de domaine", self.styles['SubHeader']))
            story.append(Spacer(1, 20))
            
            # Domain name
            story.append(Paragraph(f"Domaine: {domain}", self.styles['Domain']))
            story.append(Spacer(1, 20))
            
            # Current date and time
            current_time = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
            story.append(Paragraph(f"Date de génération: {current_time}", self.styles['FieldValue']))
            story.append(Spacer(1, 20))
            
            if error:
                # Error case
                story.append(Paragraph("❌ ERREUR DE RECHERCHE", self.styles['FieldLabel']))
                story.append(Paragraph(f"Message d'erreur: {error}", self.styles['FieldValue']))
                story.append(Spacer(1, 20))
            else:
                # Success case - display WHOIS information
                story.append(Paragraph("📋 INFORMATIONS WHOIS", self.styles['FieldLabel']))
                story.append(Spacer(1, 10))
                
                # Organize WHOIS data into sections
                sections = self._organize_whois_data(whois_info)
                
                for section_title, section_data in sections.items():
                    if section_data:
                        story.append(Paragraph(f"<b>{section_title}</b>", self.styles['FieldLabel']))
                        story.append(Spacer(1, 5))
                        
                        for field_name, field_value in section_data.items():
                            formatted_value = self._format_field_value(field_value)
                            
                            # Create table for better alignment
                            data = [
                                [Paragraph(f"<b>{field_name}:</b>", self.styles['FieldLabel']),
                                 Paragraph(formatted_value, self.styles['FieldValue'])]
                            ]
                            
                            table = Table(data, colWidths=[150, 350])
                            table.setStyle(TableStyle([
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                            ]))
                            
                            story.append(table)
                        
                        story.append(Spacer(1, 10))
            
            # Add signature section
            #story.append(PageBreak())
            story.append(Paragraph("📝 SIGNATURE ET VALIDATION", self.styles['FieldLabel']))
            story.append(Spacer(1, 20))
            
            # Signature table
            signature_data = [
                ["Agent Douanier:", "__________________________"],
                ["Date de vérification:", current_time],
                ["Validité du document:", "30 jours à compter de la génération"]
            ]
            
            signature_table = Table(signature_data, colWidths=[200, 300])
            signature_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(signature_table)
            story.append(Spacer(1, 20))
            
            # Footer note
            story.append(Paragraph(
                "Ce document est généré automatiquement par le système de détection de produits illicites de la Douane Tunisienne. "
                "Il contient des informations officielles d'enregistrement de domaine et doit être traité avec confidentialité.",
                self.styles['Footer']
            ))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF generated successfully for domain: {domain}")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error generating PDF for domain {domain}: {str(e)}")
            raise Exception(f"Erreur lors de la génération du PDF: {str(e)}")

    def _organize_whois_data(self, whois_info: dict):
        """Organize WHOIS data into logical sections"""
        sections = {
            "Informations Générales": {},
            "Coordonnées du Propriétaire": {},
            "Serveurs de Noms (DNS)": {},
            "Dates Importantes": {},
            "Informations Techniques": {}
        }
        
        # Mapping of WHOIS fields to sections
        field_mapping = {
            # General Information
            'domain_name': 'Informations Générales',
            'registrar': 'Informations Générales',
            'registrar_url': 'Informations Générales',
            'registrar_iana_id': 'Informations Générales',
            'whois_server': 'Informations Générales',
            'referral_url': 'Informations Générales',
            
            # Owner Contact
            'name': 'Coordonnées du Propriétaire',
            'organization': 'Coordonnées du Propriétaire',
            'org': 'Coordonnées du Propriétaire',
            'address': 'Coordonnées du Propriétaire',
            'street': 'Coordonnées du Propriétaire',
            'city': 'Coordonnées du Propriétaire',
            'state': 'Coordonnées du Propriétaire',
            'country': 'Coordonnées du Propriétaire',
            'zipcode': 'Coordonnées du Propriétaire',
            'zip': 'Coordonnées du Propriétaire',
            'email': 'Coordonnées du Propriétaire',
            'phone': 'Coordonnées du Propriétaire',
            'fax': 'Coordonnées du Propriétaire',
            
            # DNS Servers
            'name_servers': 'Serveurs de Noms (DNS)',
            'nameservers': 'Serveurs de Noms (DNS)',
            
            # Important Dates
            'creation_date': 'Dates Importantes',
            'updated_date': 'Dates Importantes',
            'expiration_date': 'Dates Importantes',
            'last_updated': 'Dates Importantes',
            
            # Technical Information
            'dnssec': 'Informations Techniques',
            'status': 'Informations Techniques',
            'statuses': 'Informations Techniques'
        }
        
        for field, value in whois_info.items():
            field_lower = field.lower()
            section = None
            
            # Find the appropriate section for this field
            for key, sec in field_mapping.items():
                if key in field_lower or field_lower in key:
                    section = sec
                    break
            
            if section is None:
                section = 'Informations Techniques'
            
            # Format field name for display
            display_name = self._format_field_name(field)
            sections[section][display_name] = value
        
        return sections

    def _format_field_name(self, field_name: str):
        """Format field name for display"""
        # Common field name mappings
        mappings = {
            'domain_name': 'Nom de domaine',
            'registrar': 'Registrar',
            'registrar_url': 'URL du Registrar',
            'registrar_iana_id': 'ID IANA du Registrar',
            'whois_server': 'Serveur WHOIS',
            'referral_url': 'URL de référence',
            'name': 'Nom',
            'organization': 'Organisation',
            'org': 'Organisation',
            'address': 'Adresse',
            'street': 'Rue',
            'city': 'Ville',
            'state': 'État/Région',
            'country': 'Pays',
            'zipcode': 'Code postal',
            'zip': 'Code postal',
            'email': 'Email',
            'phone': 'Téléphone',
            'fax': 'Fax',
            'name_servers': 'Serveurs de noms',
            'nameservers': 'Serveurs de noms',
            'creation_date': 'Date de création',
            'updated_date': 'Date de mise à jour',
            'expiration_date': 'Date d\'expiration',
            'last_updated': 'Dernière mise à jour',
            'dnssec': 'DNSSEC',
            'status': 'Statut',
            'statuses': 'Statuts'
        }
        
        field_lower = field_name.lower()
        if field_lower in mappings:
            return mappings[field_lower]
        else:
            # Convert camelCase or snake_case to readable format
            formatted = field_name.replace('_', ' ').replace('-', ' ')
            formatted = formatted.title()
            return formatted

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