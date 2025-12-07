# Developed by Montassar Bellah Abdallah

import json
import os
import time
from config import output_dir
from crewai import Crew, Process
from queries_agent.queries_agent import search_queries_recommendation_agent, search_queries_recommendation_task
from search_agent.search_agent import search_engine_agent, search_engine_task
from web_scraping_agent.web_scraping_agent import scraping_agent, scraping_task

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
        "product_category": "produits électroniques contrefaits",
        "platforms_list": [],
        "no_keywords": 3,
        "language": "french",
        "score_th": current_score_th,
        "max_search_results": current_max_results,
    }

    results1 = crew1.kickoff(inputs=inputs_1_2)

    # Wait 60 seconds to respect Gemini API rate limit (5 RPM)
    time.sleep(60)

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
        break  # Exit the retry loop
    else:
        if attempt < MAX_ATTEMPTS:
            print(f"No search results found. Retrying with adjusted parameters...")
        else:
            print("Maximum attempts reached. No suspicious products detected.")
