# Developed by Montassar Bellah Abdallah

from crewai import Agent, Task
from config import scraping_llm, output_dir
import os
from .tools.crawl4ai_tool import Crawl4AIScrapeWebsiteTool
from .schema import AllExtractedProducts


# Agent 3 - Web Scraping Agent

scraping_agent = Agent(
    role="Web scraping agent",
    goal="To extract product details from e-commerce websites for customs analysis",
    backstory="The agent is designed to extract detailed product information from online marketplaces. These details will be used to identify potentially illicit, counterfeit, or undeclared products.",
    llm=scraping_llm,
    tools=[Crawl4AIScrapeWebsiteTool()],
    verbose=True,
)

scraping_task = Task(
    description="\n".join([
        "The task is to extract product details from e-commerce platform URLs.",
        "The search results are provided: {search_results}",
        "The task has to collect results from multiple page URLs identified in the provided search results.",
        "Use the web scraping tool to extract content from each URL in the search results.",
        "From the scraped content, identify and extract only the product-related information, ignoring navigation menus, footers, advertisements, customer reviews, and other non-product elements.",
        "Then, convert only that extracted product information into a JSON object with key 'products' and value as an array of product objects.",
        "Each product object should include as much information as available: page_url (original URL), product_title, product_image_url, product_current_price (numeric), suspicion_score (1-10), suspicion_reasons (array of strings), and business_website.",
        "All fields are optional - extract whatever information is present on the page.",
        "Focus on identifying red flags such as unusually low prices, missing brand information, or suspicious seller profiles.",
        #"Collect details from the top {top_recommendations_no} most suspicious products from the search results.",
        "CRITICAL: Ensure the output is PERFECTLY valid JSON. All strings must have quotes properly escaped using \\\" for any internal quotes. Use \\\\ for backslashes, \\\\n for newlines, \\\\t for tabs. Do NOT include any unescaped quotes, HTML tags, or special characters in string values. The JSON must parse correctly without any syntax errors.",
        "Output ONLY the raw JSON object - no explanations, no markdown, no extra text. Start directly with { and end with }.",
    ]),
    expected_output="A JSON object containing extracted product details with suspicion indicators",
    output_json=AllExtractedProducts,
    output_file=os.path.join(output_dir, "step_3_scraped_products.json"),
    #max_retries=10,
    agent=scraping_agent
)
