# Developed by Montassar Bellah Abdallah

import streamlit as st
import streamlit.components.v1 as components
import json
from typing import List, Dict
import base64

def decode_unicode_escapes(text: str) -> str:
    """Decode Unicode escape sequences in a string."""
    if isinstance(text, str):
        try:
            return text.encode('utf-8').decode('unicode_escape')
        except (UnicodeDecodeError, UnicodeEncodeError):
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
    st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Header Section */
    .header-container {
        background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(124, 58, 237, 0.3);
        text-align: center;
    }
    
    .header-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: #e0e7ff;
        font-weight: 400;
    }
    
    /* Metrics Cards */
    .metric-card {
        background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(124, 58, 237, 0.4);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #a78bfa;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    
    
    .product-image {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .product-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 1rem;
        line-height: 1.4;
    }
    
    /* Price Section */
    .price-container {
        background: rgba(30, 41, 59, 0.5);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .current-price {
        font-size: 2rem;
        font-weight: 700;
        color: #10b981;
    }
    
    .original-price {
        font-size: 1.2rem;
        color: #94a3b8;
        text-decoration: line-through;
        margin-left: 1rem;
    }
    
    .discount-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-left: 1rem;
        box-shadow: 0 2px 10px rgba(239, 68, 68, 0.4);
    }
    
    /* Suspicion Score */
    .score-container {
        margin: 1.5rem 0;
        padding: 1rem;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .score-badge {
        display: inline-block;
        padding: 0.6rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .score-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .score-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .score-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .progress-bar {
        width: 100%;
        height: 10px;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Suspicion Reasons */
    .reasons-container {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .reason-item {
        color: #fca5a5;
        margin: 0.5rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Specs Table */
    .specs-table {
        width: 100%;
        margin-top: 1rem;
        border-collapse: collapse;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        overflow: hidden;
    }

    .spec-row {
        background: rgba(30, 41, 59, 0.5);
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .spec-row:last-child {
        border-bottom: none;
    }

    .spec-name {
        padding: 0.8rem;
        color: #f1f5f9;
        font-weight: 400;
        border-radius: 0 8px 8px 0;
    }
    
    /* Buttons */
    .cta-button {
        display: inline-block;
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        border: none;
        cursor: pointer;
        font-size: 1rem;
    }
    
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #0f172a;
    }
    
    .sidebar-content {
        color: #e2e8f0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 8px;
        color: #e2e8f0;
        font-weight: 500;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

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
    avg_suspicion = sum(p['suspicion_score'] for p in products) / total_products if total_products > 0 else 0
    high_risk = sum(1 for p in products if p['suspicion_score'] >= 70)
    
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
        """, unsafe_allow_html=True)
    
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
    # Image and Title
    col1, col2 = st.columns([1, 2])

    with col1:
        if product.get('product_image_url'):
            st.markdown(f'<img src="{product["product_image_url"]}" class="product-image" />', unsafe_allow_html=True)
        else:
            st.markdown('<div class="product-image" style="background: #334155; display: flex; align-items: center; justify-content: center; color: #64748b;">Pas d\'image</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="product-title">{product["product_title"]}</div>', unsafe_allow_html=True)

        # Price Section
        price_html = '<div class="price-container">'
        price_html += f'<span class="current-price">{product["product_current_price"]:.2f} DT</span>'

        if product.get('product_original_price') and product['product_original_price'] > product['product_current_price']:
            price_html += f'<span class="original-price">{product["product_original_price"]:.2f} DT</span>'

        if product.get('product_discount_percentage') and product['product_discount_percentage'] > 0:
            price_html += f'<span class="discount-badge">-{product["product_discount_percentage"]:.0f}%</span>'

        price_html += '</div>'
        st.markdown(price_html, unsafe_allow_html=True)

        # Suspicion Score
        st.markdown(render_suspicion_score(product['suspicion_score']), unsafe_allow_html=True)

        # CTA Button
        if product.get('product_url'):
            st.markdown(f'<a href="{product["product_url"]}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 0.8rem 2rem; border-radius: 12px; text-decoration: none; font-weight: 600; text-align: center; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); border: none; cursor: pointer; font-size: 1rem; font-family: \'Inter\', sans-serif;">Voir le Produit</a>', unsafe_allow_html=True)

    # Suspicion Reasons
    if product.get('suspicion_reasons'):
        st.markdown("### Raisons de Suspicion")
        reasons_html = '<div class="reasons-container">'
        for reason in product['suspicion_reasons']:
            reasons_html += f'<div class="reason-item">• {reason}</div>'
        reasons_html += '</div>'
        st.markdown(reasons_html, unsafe_allow_html=True)

    # Product Specifications Table
    if product.get('product_specs'):
        st.markdown("### Spécifications du Produit")
        specs_html = '<table class="specs-table">'
        for spec in product['product_specs']:
            specs_html += f'<tr class="spec-row"><td class="spec-name"><strong>{spec["specification_name"]}:</strong> {spec["specification_value"]}</td></tr>'
        specs_html += '</table>'
        st.markdown(specs_html, unsafe_allow_html=True)

# Component: Search Results Table
def render_search_results_table(results: List[Dict]):
    if not results:
        return

    # Create HTML with inline CSS for the iframe
    css = '''
    <style>
    .score-badge {
        display: inline-block;
        padding: 0.6rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .score-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    .score-medium {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    .score-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    .cta-button {
        display: inline-block;
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 600;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        border: none;
        cursor: pointer;
        font-size: 1rem;
        font-family: 'Inter', sans-serif;
    }
    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
    }
    </style>
    '''

    # Create HTML table
    html = css + '<div style="overflow-x: auto; margin-top: 1rem;"><table style="width: 100%; border-collapse: collapse; background: rgba(30, 41, 59, 0.5); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);"><thead><tr style="background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%); color: white;"><th style="padding: 1rem; text-align: left; font-weight: 600; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.2);">Titre du Produit</th><th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.2);">Score de Suspicion</th><th style="padding: 1rem; text-align: center; font-weight: 600; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.2);">Action</th></tr></thead><tbody>'

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
def render_sidebar(products: List[Dict]):
    with st.sidebar:
        st.markdown("### ℹ️ À Propos")
        st.markdown("""
        Cette application analyse automatiquement les produits en ligne pour détecter
        les contrefaçons potentielles basées sur plusieurs indicateurs.

        **Développé par Montassar Bellah Abdallah**
        """)

        return 0, 100

# Filter Products
def filter_products(products: List[Dict], min_score: int, max_score: int):
    # Filter
    filtered = [p for p in products if min_score <= p['suspicion_score'] <= max_score]

    return filtered

# Main App
def main():
    load_css()

    # Load scraped products data
    with open('ai-agent-output/step_3_scraped_products.json', 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)

    scraped_products = scraped_data.get('products', [])
    # Adjust suspicion_score from 1-10 scale to 0-100 scale
    for product in scraped_products:
        product['suspicion_score'] *= 10
        # Decode Unicode escapes in suspicion_reasons
        if 'suspicion_reasons' in product and product['suspicion_reasons']:
            product['suspicion_reasons'] = [decode_unicode_escapes(reason) for reason in product['suspicion_reasons']]

    # Load search results data
    with open('ai-agent-output/step_2_search_results.json', 'r', encoding='utf-8') as f:
        search_data = json.load(f)

    search_results = search_data.get('results', [])

    # Get URLs of scraped products
    scraped_urls = {product['page_url'] for product in scraped_products}

    # Filter search results to exclude scraped ones
    unscraped_results = [result for result in search_results if result['url'] not in scraped_urls]

    # Convert search scores to display scale (0-100)
    for result in unscraped_results:
        result['display_score'] = round(result['score'] * 100)

    products = scraped_products
    
    # Sidebar
    min_score, max_score = render_sidebar(products)

    # Header
    render_header()

    # Metrics
    render_metrics(products)


    # Filter Products
    filtered_products = filter_products(products, min_score, max_score)
    
    # Products Section
    st.markdown("## Produits Détectés")
    st.markdown(f"*Affichage de {len(filtered_products)} produit(s)*")

    if not filtered_products:
        st.warning("Aucun produit ne correspond aux filtres sélectionnés.")
    else:
        for product in filtered_products:
            render_product_card(product)

    # Other Potential Products Section
    if unscraped_results:
        st.markdown("---")
        st.markdown("## Autres Possibilités de Produits")
        #st.markdown(f"*Affichage de {len(unscraped_results)} résultat(s) de recherche supplémentaire(s) non analysés en profondeur*")

        render_search_results_table(unscraped_results)



if __name__ == "__main__":
    main()
