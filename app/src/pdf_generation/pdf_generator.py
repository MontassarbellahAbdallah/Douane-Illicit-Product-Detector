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
    Frame, PageTemplate, PageBreak
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
                return self._safe_str(value[0])
            elif len(value) > 1:
                return ", ".join(self._safe_str(v) for v in value)
        elif isinstance(value, datetime):
            return value.strftime('%d/%m/%Y %H:%M:%S')
        return self._safe_str(value)
    
    def _safe_str(self, text):
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
                onPage=self._create_header,
                onPageEnd=self._create_footer
            )
            
            doc.addPageTemplates([template])
            
            # Build PDF content
            story = []
            
            # Title section
            #story.append(Paragraph("🛡️ DOUANE - ANALYSE DE PRODUITS ILICITES", self.styles['Header']))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Rapport d'Analyse Automatisée", self.styles['SubHeader']))
            story.append(Spacer(1, 20))
            
            # Analysis category
            story.append(Paragraph(f"Catégorie analysée: {product_category}", self.styles['Domain']))
            story.append(Spacer(1, 20))
            
            # Current date and time
            current_time = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
            story.append(Paragraph(f"Date de génération: {current_time}", self.styles['FieldValue']))
            story.append(Spacer(1, 20))
            
            # Fallback indication
            if using_fallback:
                story.append(Paragraph("⚠️ AVERTISSEMENT: DONNÉES DE SECOURS UTILISÉES", self.styles['FieldLabel']))
                story.append(Paragraph("Ce rapport a été généré à partir de données de secours en raison de l'impossibilité de récupérer les données en temps réel.", self.styles['FieldValue']))
                story.append(Spacer(1, 20))
            
            # Executive Summary
            total_products = len(products)
            avg_suspicion = sum(p.get("suspicion_score", 0) for p in products) / total_products if total_products > 0 else 0
            high_risk = sum(1 for p in products if p.get("suspicion_score", 0) >= 70)
            
            story.append(Paragraph("📊 RÉSUMÉ EXECUTIF", self.styles['FieldLabel']))
            story.append(Spacer(1, 10))
            
            summary_data = [
                ["Produits analysés:", str(total_products)],
                ["Score moyen de suspicion:", f"{avg_suspicion:.1f}/100"],
                ["Produits à risque élevé:", str(high_risk)],
                ["Statut de l'analyse:", "Complétée" if not using_fallback else "Données de secours"]
            ]
            
            summary_table = Table(summary_data, colWidths=[200, 300])
            summary_table.setStyle(TableStyle([
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
            
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Products Analysis Section
            if products:
                story.append(Paragraph("🔍 ANALYSE DÉTAILLÉE DES PRODUITS", self.styles['FieldLabel']))
                story.append(Spacer(1, 15))
                
                for i, product in enumerate(products):
                    story.append(Paragraph(f"Produit {i+1}: {product.get('product_title', 'Non spécifié')}", self.styles['FieldLabel']))
                    story.append(Spacer(1, 5))
                    
                    # Product details table
                    product_details = []
                    
                    # Price information
                    price_info = "Non disponible"
                    if product.get('product_current_price') is not None:
                        current_price = product['product_current_price']
                        original_price = product.get('product_original_price')
                        discount = product.get('product_discount_percentage')
                        
                        if original_price and original_price > current_price:
                            price_info = f"{current_price:.2f} DT (au lieu de {original_price:.2f} DT) -{-discount:.0f}%"
                        else:
                            price_info = f"{current_price:.2f} DT"
                    
                    product_details.extend([
                        ["Titre du produit:", product.get('product_title', 'Non spécifié')],
                        ["Prix:", price_info],
                        ["Score de suspicion:", f"{product.get('suspicion_score', 0)}/100"],
                        ["URL du produit:", product.get('page_url', 'Non disponible')],
                        ["Site vendeur:", product.get('business_website', 'Non spécifié')]
                    ])
                    
                    # WHOIS information
                    whois_info = product.get('whois_info')
                    if whois_info and not isinstance(whois_info, dict):
                        whois_info = {}
                    
                    if whois_info and 'error' not in whois_info:
                        domain_name = whois_info.get('domain_name', 'Non disponible')
                        registrar = whois_info.get('registrar', 'Non disponible')
                        creation_date = whois_info.get('creation_date', 'Non disponible')
                        
                        product_details.extend([
                            ["Domaine enregistré:", domain_name],
                            ["Registrar:", registrar],
                            ["Date de création:", str(creation_date)]
                        ])
                    elif whois_info and 'error' in whois_info:
                        product_details.append(["Informations WHOIS:", f"Erreur: {whois_info['error']}"])
                    else:
                        product_details.append(["Informations WHOIS:", "Non disponibles"])
                    
                    product_table = Table(product_details, colWidths=[150, 350])
                    product_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f9fafb')),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    
                    story.append(product_table)
                    
                    # Suspicion reasons
                    suspicion_reasons = product.get('suspicion_reasons', [])
                    if suspicion_reasons:
                        story.append(Paragraph("Raisons de suspicion:", self.styles['FieldLabel']))
                        for reason in suspicion_reasons:
                            story.append(Paragraph(f"• {reason}", self.styles['FieldValue']))
                    else:
                        story.append(Paragraph("Raisons de suspicion: Aucune raison spécifique identifiée", self.styles['FieldValue']))
                    
                    story.append(Spacer(1, 15))
                    
                    # Add page break if not the last product
                    if i < len(products) - 1:
                        story.append(PageBreak())
            else:
                story.append(Paragraph("⚠️ AUCUN PRODUIT SUSPECT DÉTECTÉ", self.styles['FieldLabel']))
                story.append(Paragraph("Aucun produit suspect n'a été détecté lors de cette analyse.", self.styles['FieldValue']))
                story.append(Spacer(1, 20))
            
            # Other potential products section
            if search_results and not using_fallback:
                story.append(Paragraph("🔎 AUTRES PRODUITS POTENTIELS", self.styles['FieldLabel']))
                story.append(Spacer(1, 10))
                
                for i, result in enumerate(search_results):
                    result_data = [
                        ["Titre:", result.get('title', 'Non spécifié')],
                        ["Score de suspicion:", f"{result.get('score', 0) * 100:.0f}/100"],
                        ["URL:", result.get('url', 'Non disponible')]
                    ]
                    
                    result_table = Table(result_data, colWidths=[150, 350])
                    result_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef3c7')),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    
                    story.append(result_table)
                    story.append(Spacer(1, 10))
            
            # Signature section
            # story.append(PageBreak())
            story.append(Paragraph("📝 SIGNATURE ET VALIDATION", self.styles['FieldLabel']))
            story.append(Spacer(1, 20))
            
            # Signature table
            signature_data = [
                ["Agent Douanier:", "__________________________"],
                ["Date d'analyse:", current_time],
                ["Catégorie analysée:", product_category],
                ["Statut de l'analyse:", "Complétée" if not using_fallback else "Données de secours"],
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
                "Il contient des informations officielles d'analyse et doit être traité avec confidentialité.",
                self.styles['Footer']
            ))
            
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
