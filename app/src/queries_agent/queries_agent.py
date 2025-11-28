import os
from config import basic_llm, output_dir
from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task

## Setup Agent
# Output Model
class SuggestedSearchQueries(BaseModel):
    queries: List[str] = Field(
        ...,
        title="Suggested search queries to detect illicit products on online platforms",
        min_items=1,
    )

# Agent Definition
search_queries_recommendation_agent = Agent(
    role="Search Queries Recommendation Agent",
    goal="\n".join([
        "To provide a list of suggested search queries to be passed to the search engine.",
        "The queries must be varied and looking for specific suspicious products.",
        "Focus on products that might be illicit, counterfeit, or undeclared."
    ]),
    backstory="The agent is designed to help Tunisian Customs detect illicit products by providing a list of targeted search queries based on product categories commonly involved in fraud and smuggling.",
    llm=basic_llm,
    verbose=True,
)

# Task Definition
search_queries_recommendation_task = Task(
    description="\n".join([
        "La Douane tunisienne recherche des {product_category} suspects sur les plateformes de vente en ligne.",
        "Les plateformes cibles incluent: {platforms_list}",
        "L'objectif est d'identifier tous les produits potentiellement illicites pour analyse ultérieure.",
        "Les recherches doivent cibler le marché tunisien ou les sites accessibles depuis la Tunisie.",
        "Générer au maximum {no_keywords} requêtes de recherche.",
        "Les mots-clés de recherche doivent être en langue {language}.",
        "Les requêtes doivent être spécifiques: inclure des marques, types, ou modèles particuliers.",
        "Éviter les mots-clés génériques. Cibler des pages produits réelles, pas des blogs ou pages de listing."
    ]),
    expected_output="A JSON object containing a list of suggested search queries for detecting illicit products.",
    output_json=SuggestedSearchQueries,
    output_file=os.path.join(output_dir, "step_1_suggested_search_queries.json"),
    #max_retries=10,
    agent=search_queries_recommendation_agent
)
