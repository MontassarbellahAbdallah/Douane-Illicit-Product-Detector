# Developed by Montassar Bellah Abdallah

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
        "To provide a list of suggested search queries specifically targeting illicit products.",
        "Each query must include terms indicating illicit nature like 'réplique', 'copie', 'contrefait', 'générique', 'non originale', 'importé clandestinement', or 'sans déclaration'.",
        "Focus exclusively on counterfeit, undeclared, or illegally imported products.",
        "Avoid generic terms like 'bas prix', 'pas cher', or 'prix incroyable' alone as they may return legitimate products."
    ]),
    backstory="The agent is designed to help Tunisian Customs detect illicit products by providing a list of targeted search queries based on product categories commonly involved in fraud and smuggling.",
    llm=basic_llm,
    verbose=True,
)

# Task Definition
search_queries_recommendation_task = Task(
    description="\n".join([
        "The Tunisian Customs is looking for illicit {product_category} on online sales platforms.",
        #"The target platforms include: {platforms_list}",
        "IMPORTANT: Don't do the search on these platforms: {excluded_platforms_list}",
        "The objective is to identify counterfeit, undeclared, or illegally imported products.",
        "The searches must target the Tunisian market or sites accessible from Tunisia.",
        "Generate a maximum of {no_keywords} search queries.",
        "The search keywords must be in {language} language.",
        #"Each query must include at least one term indicating an illicit product: 'replica', 'copy', 'counterfeit', 'generic', 'non-original', 'illegally imported', 'undeclared', 'black market', etc.",
        "Avoid generic terms like 'low price', 'cheap', 'amazing price' alone as they may return legitimate products.",
        #"The queries must be specific: include particular brands, types, or models.",
        "Target real product pages, not blogs or listing pages."
    ]),
    expected_output="A JSON object containing a list of suggested search queries for detecting illicit products.",
    output_json=SuggestedSearchQueries,
    output_file=os.path.join(output_dir, "step_1_suggested_search_queries.json"),
    agent=search_queries_recommendation_agent
)
#TODO: when the user provide a product_category and language in french it should be translated to english before being used in the prompt.

