# Developed by Montassar Bellah Abdallah

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import List, Dict
from datetime import datetime
import os
import sys


# Add the parent directory of main_crewai.py to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from main_crewai import run_analysis # Import the refactored function
from pdf_generation import generate_whois_pdf, generate_analysis_pdf # Import PDF generation module

# Add the parent directory of main_crewai.py to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from main_crewai import run_analysis # Import the refactored function


def decode_unicode_escapes(text: str) -> str:
    """Decode Unicode escape sequences in a string."""
    if isinstance(text, str):
        try:
            # First try to decode unicode escapes
            decoded = text.encode("utf-8").decode("unicode_escape")
            # Then ensure proper UTF-8 encoding for display
            return decoded.encode("utf-8").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            try:
                # Fallback: try direct UTF-8 decoding
                return text.encode("latin1").decode("utf-8")
            except:
                try:
                    # Additional fallback for double-encoded UTF-8
                    return text.encode("utf-8").decode("utf-8", errors="ignore")
                except:
                    return text
    return text

# Page configuration
st.set_page_config(
    page_title="Douane - Détecteur de Produits Illicites",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
def load_css():
    css_file_path = os.path.join(os.path.dirname(__file__), "..", "styles", "style.css")
    with open(css_file_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Component: Header
def render_header():
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🛡️ Douane – Détecteur de Produits Illicites</div>
        <div class="header-subtitle">Analyse Automatisée des Produits Potentiellement Contrefaits</div>
    </div>
    """, unsafe_allow_html=True)

# Component: Metrics Section
def render_metrics(products: List[Dict]):
    total_products = len(products)
    avg_suspicion = sum(p["suspicion_score"] for p in products) / total_products if total_products > 0 else 0
    high_risk = sum(1 for p in products if p["suspicion_score"] >= 70)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_products}</div>
            <div class="metric-label">Produits Analysés</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_suspicion:.1f}</div>
            <div class="metric-label">Score Moyen</div>
        </div>
        """ , unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{high_risk}</div>
            <div class="metric-label">Risque Élevé</div>
        </div>
        """, unsafe_allow_html=True)

# Component: Suspicion Score Visualizer
def render_suspicion_score(score: int):
    if score < 40:
        badge_class = "score-low"
        color = "#10b981"
        label = "Faible Risque"
    elif score < 70:
        badge_class = "score-medium"
        color = "#f59e0b"
        label = "Risque Moyen"
    else:
        badge_class = "score-high"
        color = "#ef4444"
        label = "Risque Élevé"
    
    return f"""
    <div class="score-container">
        <span class="score-badge {badge_class}">Score: {score}/100 - {label}</span>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {score}%; background: {color};"></div>
        </div>
    </div>
    """

# Component: Product Card
def render_product_card(product: Dict):
    st.markdown('<div class="product-card">', unsafe_allow_html=True)

    # Create 3-column layout: Image | Product Details | Attribution Info
    col1, col2, col3 = st.columns([2, 2, 2])

    # Column 1: Product Image and Suspicion Reasons
    with col1:
        if product.get('product_image_url'):
            st.markdown(f'<img src="{product["product_image_url"]}" class="product-image" />', unsafe_allow_html=True)
        else:
            st.markdown('<div class="product-image" style="background: #334155; display: flex; align-items: center; justify-content: center; color: #64748b;">Pas d\'image</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="product-title">{product["product_title"]}</div>', unsafe_allow_html=True)

        # Price Section
        price_html = '<div class="price-container">'
        if product.get('product_current_price') is not None:
            price_html += f'<span class="current-price">{product["product_current_price"]:.2f} DT</span>'
        else:
            price_html += '<span class="current-price">Prix non disponible</span>'

        if product.get('product_original_price') and product['product_original_price'] is not None and product.get('product_current_price') is not None and product['product_original_price'] > product['product_current_price']:
            price_html += f'<span class="original-price">{product["product_original_price"]:.2f} DT</span>'

        if product.get('product_discount_percentage') and product['product_discount_percentage'] is not None and product['product_discount_percentage'] > 0:
            price_html += f'<span class="discount-badge">-{product["product_discount_percentage"]:.0f}%</span>'

        price_html += '</div>'
        st.markdown(price_html, unsafe_allow_html=True)

        # Suspicion Score
        st.markdown(render_suspicion_score(product['suspicion_score']), unsafe_allow_html=True)

        # CTA Button
        if product.get('page_url'):
            st.markdown(f'<a href="{product["page_url"]}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 0.8rem 2rem; border-radius: 12px; text-decoration: none; font-weight: 600; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); border: none; cursor: pointer; font-size: 1rem; font-family: \'Inter\', sans-serif;">Voir le Produit</a>', unsafe_allow_html=True)


    # Column 2: Product Details
    with col2:
        st.markdown("### Informations sur le Vendeur")

        attribution_fields = [
            ('business_website', 'Site Web Officiel'),
            ('whois_info', 'Informations WHOIS')
        ]

        attribution_info = []
        for field, label in attribution_fields:
            value = product.get(field)
            if value:
                if isinstance(value, dict):
                    filtered_items = [(k, v) for k, v in value.items() if v is not None]
                    if filtered_items:
                        info = f"<strong>{label}:</strong><br>"
                        for k, v in filtered_items:
                            info += f"&nbsp;&nbsp;{k}: {v}<br>"
                        attribution_info.append(info)
                else:
                    attribution_info.append(f"<strong>{label}:</strong> {value}")

        if attribution_info:
            attribution_html = '<div class="reasons-container" style="margin-top: 1rem;">'
            for info in attribution_info:
                attribution_html += f'<div class="reason-item">{info}</div>'
            attribution_html += '</div>'
            st.markdown(attribution_html, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color: #64748b; font-style: italic; margin-top: 1rem;">Aucune information d\'attribution trouvée</div>', unsafe_allow_html=True)


        
    # Column 3: Attribution Information
    with col3:
        # Suspicion Reasons moved here
        if product.get('suspicion_reasons'):
            st.markdown("### Raisons de Suspicion")
            reasons_html = '<div class="reasons-container">'
            for reason in product['suspicion_reasons']:
                reasons_html += f'<div class="reason-item">• {reason}</div>'
            reasons_html += '</div>'
            st.markdown(reasons_html, unsafe_allow_html=True)
        


# Component: Search Results Table
def render_search_results_table(results: List[Dict]):
    if not results:
        return

    # Create HTML table
    html = '<div style="overflow-x: auto; margin-top: 1rem;"><table style="width: 100%; border-collapse: collapse; background: rgba(30, 41, 59, 0.5); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);"><thead><tr style="background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%); color: white;"><th style="padding: 1rem; text-align: left; font-weight: 600; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.2);">Titre du Produit</th><th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.2);">Score de Suspicion</th><th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.2);">Action</th></tr></thead><tbody>'

    for i, result in enumerate(results):
        score = result['display_score']
        if score < 40:
            badge_class = "score-low"
        elif score < 70:
            badge_class = "score-medium"
        else:
            badge_class = "score-high"

        row_bg = "rgba(30, 41, 59, 0.3)" if i % 2 == 0 else "rgba(30, 41, 59, 0.5)"

        html += f'<tr style="background: {row_bg}; border-bottom: 1px solid rgba(255,255,255,0.05);"><td style="padding: 1rem; color: #f1f5f9; font-weight: 500; line-height: 1.4;">{result["title"]}</td><td style="padding: 1rem; text-align: center;"><span class="score-badge {badge_class}">{score}/100</span></td><td style="padding: 1rem; text-align: center;"><a href="{result["url"]}" target="_blank" class="cta-button">Voir le Produit</a></td></tr>'

    html += '</tbody></table></div>'

    components.html(html, height=400, scrolling=True)


# Sidebar
def render_sidebar():
    with st.sidebar:
        return 0, 100

# Filter Products
def filter_products(products: List[Dict], min_score: int, max_score: int):
    # Filter
    filtered = [p for p in products if min_score <= p['suspicion_score'] <= max_score]

    return filtered

# Main App
def main():
    # Initialize session state for WHOIS results
    if 'whois_result' not in st.session_state:
        st.session_state['whois_result'] = None

    load_css()

    render_header()
    #render_sidebar()
    # WHOIS Search Feature in Sidebar
    with st.sidebar:
        st.markdown("### 🌐 Recherche WHOIS")
        st.markdown("""
        Whois domain lookup vous permet de tracer la propriété et la titularité d’un nom de domaine.""")
        domain_input = st.text_input(
            "Entrez un nom de domaine",
            value="example.com",
            help="Ex: google.com, openai.com"
        )
        if st.button("Rechercher WHOIS"):
            if domain_input:
                import whois # Import whois here to avoid global import issues if not needed
                with st.spinner(f"Recherche WHOIS pour {domain_input}..."):
                    try:
                        w = whois.whois(domain_input)
                        # Convert datetime objects to strings for display
                        whois_info = {k: str(v) if isinstance(v, datetime) else v for k, v in dict(w).items()}
                        st.session_state['whois_result'] = {"domain": domain_input, "info": whois_info}
                    except Exception as e:
                        st.session_state['whois_result'] = {"domain": domain_input, "error": str(e)}
            else:
                st.sidebar.warning("Veuillez entrer un nom de domaine.")

        st.divider() # Add a divider for visual separation

    st.sidebar.title("🔎 Paramètres d'Analyse")
    st.sidebar.markdown("Détecter automatiquement les produits potentiellement illicites sur les plateformes de vente en ligne.")

    product_category_input = st.sidebar.text_input(
        "Catégorie de produit",
        value="produits électroniques",
        help="Entrez la catégorie de produits à analyser."
    )

    excluded_platforms_input = st.sidebar.text_area(
        "Plateformes à exclure (une par ligne)",
        value="mail.9annas.tn",
        help="Entrez les plateformes (domaines) à exclure, une par ligne."
    )
    excluded_platforms_list = [p.strip() for p in excluded_platforms_input.split('\n') if p.strip()]

        # Display WHOIS results if available and not currently running analysis
    if st.session_state['whois_result'] and not st.session_state.get('analysis_started', False):
        st.markdown("## Informations WHOIS")
        result = st.session_state['whois_result']
        if "error" in result:
            st.error(f"Erreur lors de la recherche WHOIS pour {result['domain']}: {result['error']}")
        else:
            st.json(result['info'])
            
            # PDF Download Button
            try:
                pdf_bytes = generate_whois_pdf(result['domain'], result['info'])
                st.download_button(
                    label="📄 Télécharger en PDF",
                    data=pdf_bytes,
                    file_name=f"whois_{result['domain']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    help="Télécharger les informations WHOIS au format PDF"
                )
            except Exception as e:
                st.error(f"Erreur lors de la génération du PDF: {str(e)}")
        
        st.divider()

    if st.sidebar.button("Démarrer l'Analyse 🚀") or st.session_state.get('analysis_started', False):
        st.session_state['analysis_started'] = True
        st.session_state['product_category'] = product_category_input
        st.session_state['excluded_platforms_list'] = excluded_platforms_list

    if st.session_state.get('analysis_started'):
        product_category_to_analyze = st.session_state['product_category']
        excluded_platforms_to_analyze = st.session_state['excluded_platforms_list']
        
        st.info(f"Lancement de l'analyse pour '{product_category_to_analyze}' (exclusion: {', '.join(excluded_platforms_to_analyze) if excluded_platforms_to_analyze else 'Aucune'}) ")
        
        with st.spinner("Analyse en cours... Cela peut prendre quelques minutes."):
            analysis_success = run_analysis(
                product_category=product_category_to_analyze,
                excluded_platforms_list=excluded_platforms_to_analyze
            )
        
        if analysis_success:
            st.success("Analyse terminée avec succès!")
            st.session_state['results_available'] = True
        else:
            st.error("L'analyse n'a pas pu détecter de produits suspects après plusieurs tentatives.")
            st.session_state['results_available'] = False
        
        # Clear analysis_started state to allow rerunning
        st.session_state['analysis_started'] = False
        st.rerun() # Rerun to display results without spinner

    if st.session_state.get('results_available'):
        # Load scraped products data with error handling
        scraped_products_path = os.path.join(os.path.dirname(__file__), 'ai-agent-output', 'step_3_scraped_products.json')
        search_results_path = os.path.join(os.path.dirname(__file__), 'ai-agent-output', 'step_2_search_results.json')

        try:
            # Try to load scraped products data
            if os.path.exists(scraped_products_path):
                with open(scraped_products_path, 'r', encoding='utf-8') as f:
                    scraped_data = json.load(f)
                scraped_products = scraped_data.get('products', [])
                # Adjust suspicion_score from 1-10 scale to 0-100 scale
                for product in scraped_products:
                    product['suspicion_score'] *= 10
                    # Decode Unicode escapes in suspicion_reasons
                    if 'suspicion_reasons' in product and product['suspicion_reasons']:
                        product['suspicion_reasons'] = [decode_unicode_escapes(reason) for reason in product['suspicion_reasons']]
            else:
                # Try to load from fallback
                fallback_path = os.path.join(os.path.dirname(__file__), '..', 'fallback', 'step_3_scraped_products.json')
                if os.path.exists(fallback_path):
                    with open(fallback_path, 'r', encoding='utf-8') as f:
                        scraped_data = json.load(f)
                    scraped_products = scraped_data.get('products', [])
                    # Adjust suspicion_score from 1-10 scale to 0-100 scale
                    for product in scraped_products:
                        product['suspicion_score'] *= 10
                        # Decode Unicode escapes in suspicion_reasons
                        if 'suspicion_reasons' in product and product['suspicion_reasons']:
                            product['suspicion_reasons'] = [decode_unicode_escapes(reason) for reason in product['suspicion_reasons']]
                    st.info("Données de secours utilisées pour les produits scrapés.")
                else:
                    st.warning("Les fichiers de résultats n'ont pas été trouvés.")
                    st.session_state['results_available'] = False
                    return

            # Try to load search results data
            if os.path.exists(search_results_path):
                with open(search_results_path, 'r', encoding='utf-8') as f:
                    search_data = json.load(f)
            else:
                # Try to load from fallback
                fallback_search_path = os.path.join(os.path.dirname(__file__), '..', 'fallback', 'step_2_search_results.json')
                if os.path.exists(fallback_search_path):
                    with open(fallback_search_path, 'r', encoding='utf-8') as f:
                        search_data = json.load(f)
                    st.info("Données de secours utilisées pour les résultats de recherche.")
                else:
                    search_data = {"results": []}

            search_results = search_data.get('results', [])
        except json.JSONDecodeError as e:
            st.error("Erreur de lecture des fichiers de résultats. Données de secours utilisées.")
            # Load fallback data
            fallback_path = os.path.join(os.path.dirname(__file__), '..', 'fallback', 'step_3_scraped_products.json')
            fallback_search_path = os.path.join(os.path.dirname(__file__), '..', 'fallback', 'step_2_search_results.json')
            
            try:
                if os.path.exists(fallback_path):
                    with open(fallback_path, 'r', encoding='utf-8') as f:
                        scraped_data = json.load(f)
                    scraped_products = scraped_data.get('products', [])
                    for product in scraped_products:
                        product['suspicion_score'] *= 10
                        if 'suspicion_reasons' in product and product['suspicion_reasons']:
                            product['suspicion_reasons'] = [decode_unicode_escapes(reason) for reason in product['suspicion_reasons']]
                
                if os.path.exists(fallback_search_path):
                    with open(fallback_search_path, 'r', encoding='utf-8') as f:
                        search_data = json.load(f)
                    search_results = search_data.get('results', [])
                else:
                    search_results = []
            except Exception:
                st.error("Impossible de charger les données de secours.")
                st.session_state['results_available'] = False
                return
        except Exception as e:
            st.error(f"Erreur inattendue lors du chargement des résultats: {str(e)}")
            st.session_state['results_available'] = False
            return

        # Get URLs of scraped products
        scraped_urls = {product['page_url'] for product in scraped_products}

        # Filter search results to exclude scraped ones
        unscraped_results = [result for result in search_results if result['url'] not in scraped_urls]

        # Convert search scores to display scale (0-100)
        for result in unscraped_results:
            result['display_score'] = round(result['score'] * 100)

        products = scraped_products
        
        # Sidebar
        min_score, max_score = render_sidebar()

        # Metrics
        render_metrics(products)

        # PDF Download Button for Analysis Results
        st.markdown("---")
        st.markdown("### 📄 Télécharger le Rapport d'Analyse")
        
        # Determine if fallback data is being used
        using_fallback = not os.path.exists(os.path.join(os.path.dirname(__file__), 'ai-agent-output', 'step_3_scraped_products.json'))
        
        # Get the product category from session state
        product_category_to_analyze = st.session_state.get('product_category', 'analyse')
        
        try:
            pdf_bytes = generate_analysis_pdf(
                product_category_to_analyze, 
                products, 
                unscraped_results, 
                using_fallback
            )
            st.download_button(
                label="📥 Télécharger le Rapport PDF",
                data=pdf_bytes,
                file_name=f"analyse_produits_{product_category_to_analyze.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                help="Télécharger le rapport d'analyse complet au format PDF"
            )
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF d'analyse: {str(e)}")

        # Filter Products
        filtered_products = filter_products(products, min_score, max_score)
        
        # Products Section
        st.markdown("## Produits Détectés")
        st.markdown(f"*Affichage de {len(filtered_products)} produit(s)*")

        if not filtered_products:
            st.warning("Aucun produit ne correspond aux filtres sélectionnés.")
        else:
            for i, product in enumerate(filtered_products):
                render_product_card(product)
                if i < len(filtered_products) - 1:
                    st.divider()

        # Other Potential Products Section
        if unscraped_results:
            st.markdown("---")
            st.markdown("## Autres Possibilités de Produits")
            #st.markdown(f"*Affichage de {len(unscraped_results)} résultat(s) de recherche supplémentaire(s) non analysés en profondeur*")

            render_search_results_table(unscraped_results)



if __name__ == "__main__":
    main()
