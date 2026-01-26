# Developed by Montassar Bellah Abdallah

import json
import os
import time
from datetime import datetime
from urllib.parse import urlparse
import whois
from config import output_dir
from crewai import Crew, Process
from queries_agent.queries_agent import search_queries_recommendation_agent, search_queries_recommendation_task
from search_agent.search_agent import search_engine_agent, search_engine_task
from web_scraping_agent.web_scraping_agent import scraping_agent, scraping_task

def convert_datetimes_to_strings(obj):
    """Recursively convert datetime objects to strings in a dict/list structure."""
    if isinstance(obj, dict):
        return {k: convert_datetimes_to_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetimes_to_strings(item) for item in obj]
    elif isinstance(obj, datetime):
        return str(obj)
    else:
        return obj

# Configuration
MAX_ATTEMPTS = 3
base_score_th = 0.1
base_max_search_results = 1

# Retry loop
for attempt in range(1, MAX_ATTEMPTS + 1):
    print(f"\n=== Attempt {attempt}/{MAX_ATTEMPTS} ===")

    # Adjust parameters for retry attempts
    current_score_th = base_score_th * (0.9 ** (attempt - 1))  # Lower threshold each attempt
    current_max_results = base_max_search_results + (attempt - 1)  # Increase max results each attempt

    print(f"Using score_threshold: {current_score_th:.2f}, max_search_results: {current_max_results}")

    # Run first two agents
    crew1 = Crew(
        agents=[
            search_queries_recommendation_agent,
            search_engine_agent,
        ],
        tasks=[
            search_queries_recommendation_task,
            search_engine_task,
        ],
        process=Process.sequential,
    )

    # Inputs for first two agents (with adjusted parameters)
    inputs_1_2 = {
        "product_category": "produits électroniques",
        #"platforms_list": [],
        "excluded_platforms_list": ["www.facebook.com", "www.instagram.com", "mail.9annas.tn"],
        "no_keywords": 3,
        "language": "french",
        "score_th": current_score_th,
        "max_search_results": current_max_results,
    }

    results1 = crew1.kickoff(inputs=inputs_1_2)

    # Wait 60 seconds to respect Gemini API rate limit (5 RPM)
    #print("Waiting 60 seconds to respect API rate limits...")
    #time.sleep(60)
    

    # Load search results
    search_results_path = os.path.join(output_dir, "step_2_search_results.json")
    try:
        with open(search_results_path, 'r') as f:
            search_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading search results: {e}")
        search_data = {"results": []}

    results_list = search_data.get("results", [])
    print(f"Found {len(results_list)} search results")

    # Check if there are any search results
    if results_list:
        # Run scraping agent
        print("Search results found! Running web scraping agent...")
        crew2 = Crew(
            agents=[scraping_agent],
            tasks=[scraping_task],
            process=Process.sequential,
        )

        inputs_3 = {
            "search_results": json.dumps(search_data),
        }

        results2 = crew2.kickoff(inputs=inputs_3)
        print("Web scraping agent completed successfully.")

        # Post-process: Add WHOIS information
        scraped_products_path = os.path.join(output_dir, "step_3_scraped_products.json")
        try:
            with open(scraped_products_path, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
            products = scraped_data.get('products', [])
            for product in products:
                website = product.get('business_website')
                if website:
                    try:
                        parsed = urlparse(website)
                        domain = parsed.netloc or parsed.path
                        if domain.startswith('www.'):
                            domain = domain[4:]
                        w = whois.whois(domain)
                        product['whois_info'] = convert_datetimes_to_strings(dict(w))
                    except Exception as e:
                        product['whois_info'] = {"error": str(e)}
                else:
                    product['whois_info'] = None
            with open(scraped_products_path, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, indent=2, ensure_ascii=False)
            print("WHOIS information added to scraped products.")
        except Exception as e:
            print(f"Error processing WHOIS: {e}")

        break  # Exit the retry loop
    else:
        if attempt < MAX_ATTEMPTS:
            print(f"No search results found. Retrying with adjusted parameters...")
        else:
            print("Maximum attempts reached. No suspicious products detected.")
