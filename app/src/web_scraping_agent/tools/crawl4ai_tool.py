# Developed by Montassar Bellah Abdallah

import asyncio
import json
import os
import time
import traceback
from crawl4ai import AsyncWebCrawler, LLMExtractionStrategy, LLMConfig, CrawlerRunConfig
from crewai.tools import BaseTool
from ..schema import SingleExtractedProduct, generate_schema_string
from config import GOOGLE_API_KEY, output_dir


def get_search_score_for_url(url: str) -> int:
    """Get the search score for a URL from step_2_search_results.json and convert to suspicion_score (1-10)."""
    from urllib.parse import urlparse
    search_results_path = os.path.join(output_dir, "step_2_search_results.json")
    try:
        with open(search_results_path, 'r', encoding='utf-8') as f:
            search_data = json.load(f)

        # Extract base URL (without query parameters and fragments) for comparison
        parsed_input_url = urlparse(url)
        input_base_url = f"{parsed_input_url.scheme}://{parsed_input_url.netloc}{parsed_input_url.path}"

        for result in search_data.get('results', []):
            result_url = result.get('url', '')
            parsed_result_url = urlparse(result_url)
            result_base_url = f"{parsed_result_url.scheme}://{parsed_result_url.netloc}{parsed_result_url.path}"

            # Match by base URL (ignoring query parameters)
            if input_base_url == result_base_url:
                score = result.get('score', 0.0)
                # Convert 0-1 score to 1-10 suspicion_score
                suspicion_score = max(1, min(10, round(score * 10)))
                return suspicion_score
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    return 1  # Default low suspicion if not found


class Crawl4AIScrapeWebsiteTool(BaseTool):
    name: str = "Crawl4AI Website Scraper"
    description: str = "Scrape website content using Crawl4AI with LLM for structured product extraction"

    def _run(self, url: str) -> str:
        """Scrape the given URL using Crawl4AI with LLM extraction and return structured product data as JSON."""
        # Generate schema string from Pydantic model
        schema_str = generate_schema_string(SingleExtractedProduct)

        # Create LLM extraction strategy for product details
        extraction_strategy = LLMExtractionStrategy(
            llm_config=LLMConfig(
                provider="gemini/gemini-2.5-flash",
                api_token=GOOGLE_API_KEY,
            ),
            instruction="Extract product information from this e-commerce product page. Extract exactly one product object with whatever information is available. Include title, image URL, product URL, current price, original price if discounted, discount percentage. Also provide suspicion reasons based on available data and indicators like low price, missing brand info, or suspicious seller. Do not assign suspicion_score - it will be set from search relevance. All fields are optional.",
            extract_type="schema",
            schema=schema_str,
            extra_args={
                "temperature": 0.0,
                "max_tokens": 4096,
            },
            verbose=True,
        )

        config = CrawlerRunConfig(extraction_strategy=extraction_strategy)

        async def scrape():
            try:
                async with AsyncWebCrawler() as crawler:
                    results = await crawler.arun(url, config=config)
                    if results and results[0].success:
                        return results[0].extracted_content
                    else:
                        return json.dumps({"error": "Failed to extract structured data"})
            except Exception as e:
                return json.dumps({"error": f"Error in scrape function: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"})

        try:
            extracted_json = asyncio.run(scrape())
            # Validate it's proper JSON and matches the schema
            data = json.loads(extracted_json)
            # Handle if data is a list (take the most suspicious product)
            if isinstance(data, list):
                if len(data) == 0:
                    # No products extracted
                    return json.dumps({"error": "No product data extracted from page"})
                elif len(data) == 1:
                    data = data[0]
                else:
                    # Take the product with the highest suspicion_score (default to 0 for None)
                    data = max(data, key=lambda x: x.get('suspicion_score') or 0)
            # Set suspicion_score from search results
            data['suspicion_score'] = get_search_score_for_url(url)
            # Validate against Pydantic model
            product = SingleExtractedProduct(**data)
            # Wait 15 seconds to respect Gemini API rate limit
            time.sleep(15)
            return json.dumps(data)
        except Exception as e:
            error_msg = f"Error scraping {url}: {str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
            # Wait even on error to maintain rate limiting
            time.sleep(15)
            return json.dumps({"error": error_msg})
