
from pydantic import BaseModel, Field
from typing import List, Optional
from crewai import Agent, Task
from config import basic_llm, output_dir, SCRAPFLY_API_KEY
import os
from crewai_tools import ScrapflyScrapeWebsiteTool
from crewai.tools import BaseTool


class TextOnlyScrapflyScrapeWebsiteTool(ScrapflyScrapeWebsiteTool):
    def _run(
        self,
        url: str,
        scrape_format: str = "text",  # Override to always use text
        scrape_config: dict[str, str] | None = None,
        ignore_scrape_failures: bool | None = None,
    ):
        return super()._run(url, scrape_format, scrape_config, ignore_scrape_failures)


# Agent 3 - Web Scraping Agent
class ProductSpec(BaseModel):
    specification_name: str
    specification_value: str

class SingleExtractedProduct(BaseModel):
    page_url: str = Field(..., title="The original url of the product page")
    product_title: str = Field(..., title="The title of the product")
    product_image_url: str = Field(..., title="The url of the product image")
    product_url: str = Field(..., title="The url of the product")
    product_current_price: float = Field(..., title="The current price of the product")
    product_original_price: Optional[float] = Field(title="The original price of the product before discount. Set to None if no discount", default=None)
    product_discount_percentage: Optional[float] = Field(title="The discount percentage of the product. Set to None if no discount", default=None)

    product_specs: List[ProductSpec] = Field(..., title="The key specifications of the product for authenticity verification", min_items=1, max_items=5)

    suspicion_score: int = Field(..., title="Suspicion level of the product being illicit (1-10, where 10 is highly suspicious)")
    suspicion_reasons: List[str] = Field(..., title="Reasons why this product is flagged as potentially illicit or counterfeit")

class AllExtractedProducts(BaseModel):
    products: List[SingleExtractedProduct]

scraping_agent = Agent(
    role="Web scraping agent",
    goal="To extract product details from e-commerce websites for customs analysis",
    backstory="The agent is designed to extract detailed product information from online marketplaces. These details will be used to identify potentially illicit, counterfeit, or undeclared products.",
    llm=basic_llm,
    tools=[TextOnlyScrapflyScrapeWebsiteTool(api_key=SCRAPFLY_API_KEY)],
    verbose=True,
)

scraping_task = Task(
    description="\n".join([
        "The task is to extract product details from e-commerce platform URLs.",
        "The task has to collect results from multiple page URLs identified in the search results.",
        "Use the web scraping tool with selective parameters: set only_main_content=True and use css_selector targeting product sections (e.g., '.product-details', '.product-info', or specific IDs for title, price, specs). This prevents scraping entire page content which can be overwhelming.",
        "First, identify and extract only the product-related information from the scraped content, ignoring navigation menus, footers, advertisements, customer reviews, and other non-product elements.",
        "Then, convert only that extracted product information into a JSON object with key 'products' and value as an array of product objects.",
        "Each product object must include: page_url (original URL), product_title, product_image_url, product_url, product_current_price (numeric), product_specs (array of 1-5 objects with specification_name and specification_value), suspicion_score (1-10), suspicion_reasons (array of strings).",
        "Optional fields: product_original_price and product_discount_percentage (set to null if not applicable).",
        "Focus on identifying red flags such as unusually low prices, missing brand information, or suspicious seller profiles.",
        "Collect details from the top {top_recommendations_no} most suspicious products from the search results.",
        "Ensure the output is valid JSON: escape all internal quotes with \\\", use \\\\ for backslashes, \\\n for newlines, \\\t for tabs, and avoid unescaped HTML, quotes, or special characters in strings to prevent validation errors.",
        "Output only the raw JSON object without markdown code blocks or any extra text.",
    ]),
    expected_output="A JSON object containing extracted product details with suspicion indicators",
    output_json=AllExtractedProducts,
    output_file=os.path.join(output_dir, "step_3_scraped_products.json"),
    #max_retries=10,
    agent=scraping_agent
)
