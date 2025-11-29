import requests
import json
from crewai.tools import BaseTool
from config import SERPER_API_KEY

class CustomSerperTool(BaseTool):
    name: str = "Custom Serper Search"
    description: str = "Search the web using Serper API with Tunisian location settings"

    def _run(self, query: str) -> str:
        url = "https://google.serper.dev/search"

        payload = json.dumps({
            "q": query,
            "location": "Tunisia",
            "gl": "tn",
            "hl": "fr"
        })
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)
        data = response.json()

        # Parse organic results
        results = []
        if 'organic' in data:
            for i, result in enumerate(data['organic']):
                score = max(0.1, 1.0 - (i / 10.0))  # Decreasing score based on position
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "score": score,
                    "search_query": query
                })

        return json.dumps({"results": results})
#TODO: Add time range filter to the search query (day, week, month, year)