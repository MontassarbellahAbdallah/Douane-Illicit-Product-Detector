# Developed by Montassar Bellah Abdallah

from crewai_tools import ScrapflyScrapeWebsiteTool


class TextOnlyScrapflyScrapeWebsiteTool(ScrapflyScrapeWebsiteTool):
    def _run(
        self,
        url: str,
        scrape_format: str = "text",  # Override to always use text
        scrape_config: dict[str, str] | None = None,
        ignore_scrape_failures: bool | None = None,
    ):
        return super()._run(url, scrape_format, scrape_config, ignore_scrape_failures)
