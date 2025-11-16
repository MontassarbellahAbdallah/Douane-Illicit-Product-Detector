from crewai import Crew, Process
from queries_agent.queries_agent import search_queries_recommendation_agent, search_queries_recommendation_task
from search_agent.search_agent import search_engine_agent, search_engine_task
from web_scraping_agent.web_scraping_agent import scraping_agent, scraping_task

# Crew Setup
customs_crew = Crew(
    agents=[
        search_queries_recommendation_agent,
        search_engine_agent,
        scraping_agent,
    ],
    tasks=[
        search_queries_recommendation_task,
        search_engine_task,
        scraping_task,
    ],
    process=Process.sequential,
)


# Execution
#no_keywords = 10
crew_results = customs_crew.kickoff(
    inputs={
        #first agent inputs
        "product_category": "produits électroniques contrefaits",
        "platforms_list": [],
        "no_keywords": 10,
        "language": "Français",
        #second agent inputs
        "score_th": 0.10,
        "max_search_results": 5,
        #third agent inputs
        "top_recommendations_no": 5,
    }   
)
