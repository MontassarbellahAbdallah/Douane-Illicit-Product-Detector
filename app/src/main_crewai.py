# Developed by Montassar Bellah Abdallah

import json
import os
import time
import shutil
import logging
from datetime import datetime
from urllib.parse import urlparse
import whois
from config import output_dir
from crewai import Crew, Process
from queries_agent.queries_agent import search_queries_recommendation_agent, search_queries_recommendation_task
from search_agent.search_agent import search_engine_agent, search_engine_task
from web_scraping_agent.web_scraping_agent import scraping_agent, scraping_task

# Setup logging for error tracking (internal only, not shown to user)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def copy_fallback_data():
    """Copy fallback data from ./fallback to ./ai-agent-output directory"""
    # Get the project root directory (2 levels up from this script's location)
    script_dir = os.path.dirname(os.path.abspath(__file__))  # app/src/
    project_root = os.path.dirname(os.path.dirname(script_dir))  # diwena_detect/
    fallback_dir = os.path.join(project_root, "fallback")
    
    if not os.path.exists(fallback_dir):
        logger.error(f"Fallback directory not found at: {fallback_dir}")
        return False
    
    try:
        # Copy all files from fallback to output directory
        for filename in os.listdir(fallback_dir):
            if filename.endswith('.json'):
                src = os.path.join(fallback_dir, filename)
                dst = os.path.join(output_dir, filename)
                shutil.copy2(src, dst)
                logger.info(f"Copied fallback file: {filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy fallback data: {e}")
        return False

def load_fallback_if_needed(file_path, fallback_filename):
    """Load fallback data if the main file doesn't exist or is corrupted"""
    # Get the project root directory (2 levels up from this script's location)
    script_dir = os.path.dirname(os.path.abspath(__file__))  # app/src/
    project_root = os.path.dirname(os.path.dirname(script_dir))  # diwena_detect/
    fallback_path = os.path.join(project_root, "fallback", fallback_filename)
    
    if os.path.exists(fallback_path):
        try:
            with open(fallback_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Copy fallback to output directory for consistency
            shutil.copy2(fallback_path, file_path)
            logger.info(f"Using fallback data for {fallback_filename}")
            return data
        except Exception as e:
            logger.error(f"Failed to load fallback data for {fallback_filename}: {e}")
    return None

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

def run_analysis(product_category: str, excluded_platforms_list: list) -> bool:
    """
    Run the complete analysis workflow with comprehensive error handling.
    Returns True if successful, False if fallback was used or all attempts failed.
    """
    # Retry loop
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n=== Attempt {attempt}/{MAX_ATTEMPTS} ===")

        # Adjust parameters for retry attempts
        current_score_th = base_score_th * (0.9 ** (attempt - 1))  # Lower threshold each attempt
        current_max_results = base_max_search_results + (attempt - 1)  # Increase max results each attempt

        print(f"Using score_threshold: {current_score_th:.2f}, max_search_results: {current_max_results}")

        try:
            # Run first two agents with error handling
            print("Running queries and search agents...")
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
                "product_category": product_category,
                #"platforms_list": [],
                "excluded_platforms_list": excluded_platforms_list,
                "no_keywords": 3,
                "language": "french",
                "score_th": current_score_th,
                "max_search_results": current_max_results,
            }

            results1 = crew1.kickoff(inputs=inputs_1_2)
            print("Queries and search agents completed successfully.")

        except Exception as e:
            logger.error(f"Agent execution failed on attempt {attempt}: {str(e)}")
            print(f"Agent execution error (attempt {attempt}): {type(e).__name__}")
            
            # Check if this is the last attempt
            if attempt == MAX_ATTEMPTS:
                print("All attempts failed. Using fallback data...")
                if copy_fallback_data():
                    print("Fallback data successfully loaded.")
                    return True  # Indicate success with fallback data
                else:
                    print("Failed to load fallback data.")
                    return False
            else:
                print(f"Retrying... ({attempt}/{MAX_ATTEMPTS})")
                continue

        # Wait 60 seconds to respect Gemini API rate limit (5 RPM)
        print("Waiting 60 seconds to respect API rate limits...")
        time.sleep(60)
        

        # Load search results with error handling
        search_results_path = os.path.join(output_dir, "step_2_search_results.json")
        try:
            with open(search_results_path, "r") as f:
                search_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load search results: {str(e)}")
            print(f"Error loading search results: {e}")
            search_data = {"results": []}

        results_list = search_data.get("results", [])
        print(f"Found {len(results_list)} search results")

        # Check if there are any search results
        if results_list:
            try:
                # Run scraping agent with error handling
                print("Search results found! Running web scraping agent...")
                crew2 = Crew(
                    agents=[
                        scraping_agent
                    ],
                    tasks=[
                        scraping_task
                    ],
                    process=Process.sequential,
                )

                inputs_3 = {
                    "search_results": json.dumps(search_data),
                }

                results2 = crew2.kickoff(inputs=inputs_3)
                print("Web scraping agent completed successfully.")

                # Post-process: Add WHOIS information with error handling
                scraped_products_path = os.path.join(output_dir, "step_3_scraped_products.json")
                try:
                    with open(scraped_products_path, "r", encoding="utf-8") as f:
                        scraped_data = json.load(f)
                    products = scraped_data.get("products", [])
                    for product in products:
                        website = product.get("business_website")
                        if website:
                            try:
                                parsed = urlparse(website)
                                domain = parsed.netloc or parsed.path
                                if domain.startswith("www."):
                                    domain = domain[4:]
                                w = whois.whois(domain)
                                product["whois_info"] = convert_datetimes_to_strings(dict(w))
                            except Exception as e:                        
                                product["whois_info"] = {"error": str(e)}
                        else:
                            product["whois_info"] = None
                    with open(scraped_products_path, "w", encoding="utf-8") as f:
                        json.dump(scraped_data, f, indent=2, ensure_ascii=False)
                    print("WHOIS information added to scraped products.")
                except Exception as e:
                    logger.error(f"Error processing WHOIS information: {str(e)}")
                    print(f"Error processing WHOIS: {e}")
                
                return True  # Exit the retry loop and indicate success
            except Exception as e:
                logger.error(f"Web scraping agent failed: {str(e)}")
                print(f"Web scraping error: {type(e).__name__}")
                
                # Check if this is the last attempt
                if attempt == MAX_ATTEMPTS:
                    print("All attempts failed. Using fallback data...")
                    if copy_fallback_data():
                        print("Fallback data successfully loaded.")
                        return True  # Indicate success with fallback data
                    else:
                        print("Failed to load fallback data.")
                        return False
                else:
                    print(f"Retrying... ({attempt}/{MAX_ATTEMPTS})")
                    continue
        else:
            if attempt < MAX_ATTEMPTS:
                print(f"No search results found. Retrying with adjusted parameters...")
            else:
                print("Maximum attempts reached. No suspicious products detected.")
                print("Using fallback data...")
                if copy_fallback_data():
                    print("Fallback data successfully loaded.")
                    return True  # Indicate success with fallback data
                else:
                    print("Failed to load fallback data.")
                    return False
    
    return False  # Indicate failure if max attempts reached and no results
