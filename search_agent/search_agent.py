
from pydantic import BaseModel, Field
from typing import List
import os
from crewai_tools import SerperDevTool
from crewai import Agent, Task
from config import basic_llm, output_dir, SERPER_API_KEY

#Agent 2 - Search Engine Agent
class SingleSearchResult(BaseModel):
    title: str
    url: str = Field(..., title="the product page url")
    content: str
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
    tools=[SerperDevTool(api_key=SERPER_API_KEY)]
)

search_engine_task = Task(
    description="\n".join([
        "The task is to search for suspicious products based on the suggested search queries.",
        "You have to collect results from multiple search queries.",
        "Ignore any suspicious links or links that are not e-commerce product pages.",
        "Ignore any search results with confidence score less than ({score_th}).",
        "Limit the total number of collected search results to {max_search_results}.",
        "Focus on finding products that may be counterfeit, undeclared, or illegally imported.",
        "The search results will be used to identify and analyze potentially illicit products.",
        "Ensure the output is valid JSON: escape all internal quotes with \\\", use \\\\ for backslashes, \\\n for newlines, \\\t for tabs, and avoid unescaped HTML, quotes, or special characters in strings to prevent validation errors.",
    ]),
    expected_output="A JSON object containing the search results for suspicious products.",
    output_json=AllSearchResults,
    output_file=os.path.join(output_dir, "step_2_search_results.json"),
    max_retries=10,
    agent=search_engine_agent
)
