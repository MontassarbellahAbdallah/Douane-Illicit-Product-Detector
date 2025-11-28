import streamlit as st
import json

st.title("Douane - Détecteur de Produits Illicites")

try:
    with open('ai-agent-output/step_3_scraped_products.json', 'r') as f:
        data = json.load(f)

    products = data.get('products', [])
    st.header(f"Produits Analysés: {len(products)}")

    for i, product in enumerate(products, start=1):
        with st.container():
            st.subheader(f"{i}. {product.get('product_title', 'Titre Inconnu')}")

            # Display suspicion score prominently
            score = product.get('suspicion_score', 0)
            if score >= 7:
                st.error(f"Score de Suspicion: {score}/10 - Très Suspicious")
            elif score >= 4:
                st.warning(f"Score de Suspicion: {score}/10 - Suspicious Modéré")
            else:
                st.success(f"Score de Suspicion: {score}/10 - Faible Risque")

            # Product image
            img_url = product.get('product_image_url')
            if img_url:
                try:
                    st.image(img_url, width=200)
                except Exception as e:
                    st.write(f"Erreur chargement image: {img_url}")

            # Pricing information
            current_price = product.get('product_current_price')
            original_price = product.get('product_original_price')
            discount = product.get('product_discount_percentage')

            st.write("**Prix:**")
            if current_price:
                st.write(f"Prix Actuel: {current_price} TND")
            if original_price:
                st.write(f"Prix Original: {original_price} TND")
            if discount:
                st.write(f"Remise: {discount:.1f}%")

            # Product specifications
            specs = product.get('product_specs', [])
            if specs:
                st.write("**Spécifications:**")
                spec_dict = {spec['specification_name']: spec['specification_value'] for spec in specs}
                st.table(spec_dict)

            # Suspicion reasons
            reasons = product.get('suspicion_reasons', [])
            if reasons:
                st.write("**Raisons de Suspicion:**")
                for reason in reasons:
                    st.markdown(f"- {reason}")

            # Link to product
            product_url = product.get('product_url')
            if product_url:
                st.link_button("Voir le Produit", product_url)

            st.divider()

except FileNotFoundError:
    st.error("Fichier ai-agent-output/step_3_scraped_products.json non trouvé. Veuillez exécuter l'agent d'abord.")
