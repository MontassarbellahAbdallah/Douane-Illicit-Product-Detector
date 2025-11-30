
# Developed by Montassar Bellah Abdallah

from pydantic import BaseModel, Field
from typing import List
import os
from crewai import Agent, Task
from config import basic_llm, output_dir
from .tools.custom_serper_tool import CustomSerperTool

#Agent 2 - Search Engine Agent
class SingleSearchResult(BaseModel):
    title: str
    url: str = Field(..., title="the product page url")
    score: float
    search_query: str

class AllSearchResults(BaseModel):
    results: List[SingleSearchResult]

search_engine_agent = Agent(
    role="Search Engine Agent",
    goal="To search for suspicious products based on the suggested search queries",
    backstory="The agent is designed to help Tunisian Customs identify illicit products by searching for products based on the suggested search queries from online marketplaces.",
    llm=basic_llm,
    verbose=True,
    tools=[CustomSerperTool()]
)

search_engine_task = Task(
    description="\n".join([
        "The task is to search for suspicious products based on the suggested search queries.",
        "You have to collect results from multiple search queries.",
        "Only consider URLs that end with '.tn' to ensure searches are limited to Tunisian domains. Ignore any results from other domains.",
        "Ignore any products that are 'En rupture de stock' (out of stock).",
        "Ignore any suspicious links or links that are not e-commerce product pages.",
        "Ignore any search results with confidence score less than ({score_th}).",
        "Limit the total number of collected search results to at most {max_search_results}.",
        "Focus on finding products that may be counterfeit, undeclared, or illegally imported.",
        "The search results will be used to identify and analyze potentially illicit products.",
        "**IMPORTANT**Ensure the output is valid JSON",
    ]),
    expected_output="A JSON object containing the search results for suspicious products.",
    output_json=AllSearchResults,
    output_file=os.path.join(output_dir, "step_2_search_results.json"),
    agent=search_engine_agent
)
