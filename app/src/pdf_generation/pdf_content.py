"""
PDF Content Module
Handles all content generation logic for both WHOIS and analysis PDFs.
"""

import logging
from datetime import datetime, timedelta
from reportlab.platypus import Paragraph, Spacer, Table, PageBreak
from reportlab.lib import colors

# Setup logging
logger = logging.getLogger(__name__)

class PDFContent:
    """Handles PDF content generation and data organization"""
    
    def __init__(self, styles_manager):
        self.styles = styles_manager
        self.field_mappings = self._initialize_field_mappings()
    
    def _initialize_field_mappings(self):
        """Initialize field mappings for WHOIS data organization"""
        return {
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
    
    def organize_whois_data(self, whois_info: dict):
        """Organize WHOIS data into logical sections"""
        sections = {
            "Informations Générales": {},
            "Coordonnées du Propriétaire": {},
            "Serveurs de Noms (DNS)": {},
            "Dates Importantes": {},
            "Informations Techniques": {}
        }
        
        for field, value in whois_info.items():
            field_lower = field.lower()
            section = None
            
            # Find the appropriate section for this field
            for key, sec in self.field_mappings.items():
                if key in field_lower or field_lower in key:
                    section = sec
                    break
            
            if section is None:
                section = 'Informations Techniques'
            
            # Format field name for display
            display_name = self.format_field_name(field)
            sections[section][display_name] = value
        
        return sections

    def format_field_name(self, field_name: str):
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

    def analyze_suspicious_patterns(self, whois_info: dict):
        """Analyze WHOIS data for suspicious patterns"""
        suspicious_patterns = []
        
        try:
            # Check for recent domain registration (less than 1 year old)
            creation_date = whois_info.get('creation_date')
            if creation_date:
                if isinstance(creation_date, str):
                    try:
                        # Parse date string
                        if 'T' in creation_date:
                            creation_date = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                        else:
                            creation_date = datetime.strptime(creation_date.split()[0], '%Y-%m-%d')
                        
                        # Check if domain is less than 1 year old
                        if datetime.now() - creation_date < timedelta(days=365):
                            suspicious_patterns.append("Domaine récemment enregistré (moins d'un an)")
                    except:
                        pass
            
            # Check for privacy protection (often used by suspicious domains)
            registrant_name = whois_info.get('registrant_name', '').lower()
            registrant_organization = whois_info.get('registrant_organization', '').lower()
            registrant_email = whois_info.get('registrant_email', '').lower()
            
            privacy_indicators = [
                'privacy', 'whois', 'protected', 'redacted', 'anonymous', 'proxy'
            ]
            
            for indicator in privacy_indicators:
                if (indicator in registrant_name or 
                    indicator in registrant_organization or 
                    indicator in registrant_email):
                    suspicious_patterns.append("Protection de la vie privée détectée (peut cacher l'identité réelle)")
                    break
            
            # Check for suspicious email domains
            if registrant_email:
                email_domain = registrant_email.split('@')[-1].lower()
                suspicious_email_domains = [
                    'tempmail', '10minutemail', 'guerrillamail', 'throwaway',
                    'temp-mail', 'mailtemp', 'disposable'
                ]
                
                for suspicious_domain in suspicious_email_domains:
                    if suspicious_domain in email_domain:
                        suspicious_patterns.append("Adresse email temporaire détectée")
                        break
            
            # Check for missing or incomplete contact information
            required_fields = ['registrant_name', 'registrant_email', 'registrant_country']
            missing_fields = []
            
            for field in required_fields:
                value = whois_info.get(field)
                if not value or value.lower() in ['n/a', 'not provided', '']:
                    missing_fields.append(field)
            
            if missing_fields:
                suspicious_patterns.append(f"Informations de contact incomplètes: {', '.join(missing_fields)}")
            
            # Check for suspicious registrar
            registrar = whois_info.get('registrar', '').lower()
            if registrar:
                suspicious_registrars = ['unknown', 'unavailable', 'not specified']
                if any(susp_reg in registrar for susp_reg in suspicious_registrars):
                    suspicious_patterns.append("Registrar non spécifié ou inconnu")
            
            # Check for domain status issues
            status = whois_info.get('status', '').lower()
            if status:
                problematic_statuses = ['suspended', 'inactive', 'pending', 'locked']
                if any(prob_status in status for prob_status in problematic_statuses):
                    suspicious_patterns.append(f"Statut de domaine problématique: {status}")
            
            # Check for short domain name (often used for phishing)
            domain_name = whois_info.get('domain_name', '')
            if domain_name and len(domain_name.replace('.tn', '').replace('.com', '').replace('.net', '')) < 5:
                suspicious_patterns.append("Nom de domaine très court (souvent utilisé pour le phishing)")
            
        except Exception as e:
            # If analysis fails, don't add any patterns
            logger.warning(f"Error analyzing suspicious patterns: {str(e)}")
        
        return suspicious_patterns

    def build_whois_content(self, domain: str, whois_info: dict, error: str = None):
        """Build WHOIS PDF content"""
        story = []
        
        # Title section
        story.append(Spacer(1, 12))
        story.append(Paragraph("Informations d'enregistrement de domaine", self.styles.get_subheader_style()))
        story.append(Spacer(1, 20))
        
        # Domain name
        story.append(Paragraph(f"Domaine: {domain}", self.styles.get_domain_style()))
        story.append(Spacer(1, 20))
        
        # Current date and time
        current_time = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
        story.append(Paragraph(f"Date de génération: {current_time}", self.styles.get_field_value_style()))
        story.append(Spacer(1, 20))
        
        if error:
            # Error case
            story.append(Paragraph("❌ ERREUR DE RECHERCHE", self.styles.get_field_label_style()))
            story.append(Paragraph(f"Message d'erreur: {error}", self.styles.get_field_value_style()))
            story.append(Spacer(1, 20))
        else:
            # Success case - display WHOIS information
            story.append(Paragraph("📋 INFORMATIONS WHOIS", self.styles.get_field_label_style()))
            story.append(Spacer(1, 10))
            
            # Organize WHOIS data into sections
            sections = self.organize_whois_data(whois_info)
            
            for section_title, section_data in sections.items():
                if section_data:
                    story.append(Paragraph(f"<b>{section_title}</b>", self.styles.get_field_label_style()))
                    story.append(Spacer(1, 5))
                    
                    for field_name, field_value in section_data.items():
                        formatted_value = self.styles.format_field_value(field_value)
                        
                        # Create table for better alignment
                        data = [
                            [Paragraph(f"<b>{field_name}:</b>", self.styles.get_field_label_style()),
                             Paragraph(formatted_value, self.styles.get_field_value_style())]
                        ]
                        
                        table = Table(data, colWidths=[150, 350])
                        table.setStyle(self.styles.get_table_style('general'))
                        
                        story.append(table)
                    
                    story.append(Spacer(1, 10))
        
        # Add signature section
        story.append(Paragraph("📝 SIGNATURE ET VALIDATION", self.styles.get_field_label_style()))
        story.append(Spacer(1, 20))
        
        # Signature table
        signature_data = [
            ["Agent Douanier:", "__________________________"],
            ["Date de vérification:", current_time],
            ["Validité du document:", "30 jours à compter de la génération"]
        ]
        
        signature_table = Table(signature_data, colWidths=[200, 300])
        signature_table.setStyle(self.styles.get_table_style('summary'))
        
        story.append(signature_table)
        story.append(Spacer(1, 20))
        
        # Footer note
        story.append(Paragraph(
            "Ce document est généré automatiquement par le système de détection de produits illicites de la Douane Tunisienne. "
            "Il contient des informations officielles d'enregistrement de domaine et doit être traité avec confidentialité.",
            self.styles.get_footer_style()
        ))
        
        return story

    def build_analysis_content(self, product_category: str, products: list, search_results: list = None, using_fallback: bool = False):
        """Build analysis PDF content"""
        story = []
        
        # Title section
        story.append(Spacer(1, 12))
        story.append(Paragraph("Rapport d'Analyse Automatisée", self.styles.get_subheader_style()))
        story.append(Spacer(1, 20))
        
        # Analysis category
        story.append(Paragraph(f"Catégorie analysée: {product_category}", self.styles.get_domain_style()))
        story.append(Spacer(1, 20))
        
        # Current date and time
        current_time = datetime.now().strftime('%d/%m/%Y à %H:%M:%S')
        story.append(Paragraph(f"Date de génération: {current_time}", self.styles.get_field_value_style()))
        story.append(Spacer(1, 20))
        
        # Fallback indication
        if using_fallback:
            story.append(Paragraph("⚠️ AVERTISSEMENT: DONNÉES DE SECOURS UTILISÉES", self.styles.get_field_label_style()))
            story.append(Paragraph("Ce rapport a été généré à partir de données de secours en raison de l'impossibilité de récupérer les données en temps réel.", self.styles.get_field_value_style()))
            story.append(Spacer(1, 20))
        
        # Executive Summary
        total_products = len(products)
        avg_suspicion = sum(p.get("suspicion_score", 0) for p in products) / total_products if total_products > 0 else 0
        high_risk = sum(1 for p in products if p.get("suspicion_score", 0) >= 70)
        
        story.append(Paragraph("📊 RÉSUMÉ EXECUTIF", self.styles.get_field_label_style()))
        story.append(Spacer(1, 10))
        
        summary_data = [
            ["Produits analysés:", str(total_products)],
            ["Score moyen de suspicion:", f"{avg_suspicion:.1f}/100"],
            ["Produits à risque élevé:", str(high_risk)],
            ["Statut de l'analyse:", "Complétée" if not using_fallback else "Données de secours"]
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 300])
        summary_table.setStyle(self.styles.get_table_style('summary'))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Products Analysis Section
        if products:
            story.append(Paragraph("🔍 ANALYSE DÉTAILLÉE DES PRODUITS", self.styles.get_field_label_style()))
            story.append(Spacer(1, 15))
            
            for i, product in enumerate(products):
                story.append(Paragraph(f"Produit {i+1}: {product.get('product_title', 'Non spécifié')}", self.styles.get_field_label_style()))
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
                    # Add basic WHOIS info to product details
                    domain_name = whois_info.get('domain_name', 'Non disponible')
                    registrar = whois_info.get('registrar', 'Non disponible')
                    creation_date = whois_info.get('creation_date', 'Non disponible')
                    
                    product_details.extend([
                        ["Domaine enregistré:", domain_name],
                        ["Registrar:", registrar],
                        ["Date de création:", str(creation_date)]
                    ])
                    
                    
                    # Add product details to suspicious patterns section
                    product_table = Table(product_details, colWidths=[150, 350])
                    product_table.setStyle(self.styles.get_table_style('suspicious'))
                    story.append(product_table)
                    
                    story.append(Spacer(1, 10))
                    
                    # Add suspicion reasons to suspicious patterns section
                    suspicion_reasons = product.get('suspicion_reasons', [])
                    if suspicion_reasons:
                        story.append(Paragraph("Raisons de suspicion:", self.styles.get_field_label_style()))
                        for reason in suspicion_reasons:
                            story.append(Paragraph(f"• {reason}", self.styles.get_field_value_style()))
                    else:
                        story.append(Paragraph("Raisons de suspicion: Aucune raison spécifique identifiée", self.styles.get_field_value_style()))
                    
                    story.append(Spacer(1, 15))
                    
                    # Add comprehensive WHOIS analysis section
                    story.append(Paragraph("📋 INFORMATIONS WHOIS DÉTAILLÉES", self.styles.get_field_label_style()))
                    story.append(Spacer(1, 5))
                    
                    # Domain Registration Section
                    story.append(Paragraph("Domaine et Enregistrement:", self.styles.get_field_label_style()))
                    domain_data = []
                    
                    # Basic domain info
                    domain_fields = [
                        ('domain_name', 'Nom de domaine'),
                        ('registrar', 'Registrar'),
                        ('registrar_url', 'URL du Registrar'),
                        ('registrar_iana_id', 'ID IANA du Registrar'),
                        ('whois_server', 'Serveur WHOIS'),
                        ('creation_date', 'Date de création'),
                        ('updated_date', 'Date de mise à jour'),
                        ('expiration_date', 'Date d\'expiration'),
                        ('status', 'Statut'),
                        ('dnssec', 'DNSSEC')
                    ]
                    
                    for field, label in domain_fields:
                        value = whois_info.get(field)
                        if value is not None:
                            domain_data.append([label, self.styles.safe_str(value)])
                    
                    if domain_data:
                        domain_table = Table(domain_data, colWidths=[150, 350])
                        domain_table.setStyle(self.styles.get_table_style('domain'))
                        story.append(domain_table)
                    
                    # Contact Information Section
                    contact_sections = [
                        ('registrant', 'Contact Registrant'),
                        ('admin', 'Contact Administratif'),
                        ('tech', 'Contact Technique')
                    ]
                    
                    for contact_type, section_title in contact_sections:
                        contact_data = []
                        
                        # Check if this contact type exists
                        contact_prefix = contact_type + '_'
                        contact_fields = [
                            (contact_prefix + 'name', 'Nom'),
                            (contact_prefix + 'first_name', 'Prénom'),
                            (contact_prefix + 'organization', 'Organisation'),
                            (contact_prefix + 'address', 'Adresse'),
                            (contact_prefix + 'address2', 'Adresse (suite)'),
                            (contact_prefix + 'city', 'Ville'),
                            (contact_prefix + 'state', 'État/Région'),
                            (contact_prefix + 'zipcode', 'Code postal'),
                            (contact_prefix + 'country', 'Pays'),
                            (contact_prefix + 'phone', 'Téléphone'),
                            (contact_prefix + 'fax', 'Fax'),
                            (contact_prefix + 'email', 'Email')
                        ]
                        
                        for field, label in contact_fields:
                            value = whois_info.get(field)
                            if value is not None:
                                contact_data.append([label, self.styles.safe_str(value)])
                        
                        if contact_data:
                            story.append(Paragraph(section_title + ":", self.styles.get_field_label_style()))
                            contact_table = Table(contact_data, colWidths=[150, 350])
                            contact_table.setStyle(self.styles.get_table_style('contact'))
                            story.append(contact_table)
                    
                    # Name Servers Section
                    name_servers = whois_info.get('name_servers') or whois_info.get('nameservers')
                    if name_servers:
                        story.append(Paragraph("Serveurs de Noms:", self.styles.get_field_label_style()))
                        ns_data = [["Serveurs de noms:", ", ".join(self.styles.safe_str(ns) for ns in name_servers)]]
                        ns_table = Table(ns_data, colWidths=[150, 350])
                        ns_table.setStyle(self.styles.get_table_style('nameserver'))
                        story.append(ns_table)
                    
                    story.append(Spacer(1, 15))
                elif whois_info and 'error' in whois_info:
                    product_details.append(["Informations WHOIS:", f"Erreur: {whois_info['error']}"])
                else:
                    product_details.append(["Informations WHOIS:", "Non disponibles"])
                
                
                
                story.append(Spacer(1, 15))
                
                # Add page break if not the last product
                if i < len(products) - 1:
                    story.append(PageBreak())
        else:
            story.append(Paragraph("⚠️ AUCUN PRODUIT SUSPECT DÉTECTÉ", self.styles.get_field_label_style()))
            story.append(Paragraph("Aucun produit suspect n'a été détecté lors de cette analyse.", self.styles.get_field_value_style()))
            story.append(Spacer(1, 20))
        
        # Other potential products section
        if search_results and not using_fallback:
            story.append(Paragraph("🔎 AUTRES PRODUITS POTENTIELS", self.styles.get_field_label_style()))
            story.append(Spacer(1, 10))
            
            for i, result in enumerate(search_results):
                result_data = [
                    ["Titre:", result.get('title', 'Non spécifié')],
                    ["Score de suspicion:", f"{result.get('score', 0) * 100:.0f}/100"],
                    ["URL:", result.get('url', 'Non disponible')]
                ]
                
                result_table = Table(result_data, colWidths=[150, 350])
                result_table.setStyle(self.styles.get_table_style('suspicious'))
                
                story.append(result_table)
                story.append(Spacer(1, 10))
        
        # Signature section
        story.append(Paragraph("📝 SIGNATURE ET VALIDATION", self.styles.get_field_label_style()))
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
        signature_table.setStyle(self.styles.get_table_style('summary'))
        
        story.append(signature_table)
        story.append(Spacer(1, 20))
        
        # Footer note
        story.append(Paragraph(
            "Ce document est généré automatiquement par le système de détection de produits illicites de la Douane Tunisienne. "
            "Il contient des informations officielles d'analyse et doit être traité avec confidentialité.",
            self.styles.get_footer_style()
        ))
        
        return story