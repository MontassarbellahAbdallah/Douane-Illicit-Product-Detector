# Developed by Montassar Bellah Abdallah

import os
import logging
import agentops
from dotenv import load_dotenv
from crewai import  LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

load_dotenv()

GOOGLE_API_KEY=os.environ.get("GOOGLE_API_KEY")
AGENTOPS_API_KEY=os.environ.get("AGENTOPS_API_KEY")
SERPER_API_KEY=os.environ.get("SERPER_API_KEY")
SCRAPFLY_API_KEY=os.environ.get("SCRAPFLY_API_KEY")

agentops.init(
    api_key=AGENTOPS_API_KEY,
    skip_auto_end_session=True,
    default_tags=['crewai']
)

# Disable AgentOps INFO logging to avoid Unicode encoding issues on Windows
logging.getLogger('agentops').setLevel(logging.WARNING)

output_dir = "./ai-agent-output"
os.makedirs(output_dir, exist_ok=True)

basic_llm = LLM(
    model="gemini/gemini-2.5-flash-lite",
    temperature=0.7
)

scraping_llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.0
)

# Knowledge Source - Context about the Tunisian Customs
about_customs = """
The Tunisian Customs monitors online sales platforms to detect illicit products.
Suspicious products include: undeclared products, counterfeits, illegally imported goods,
or products sold outside official channels.
The objective is to automatically identify suspicious sales to strengthen the fight
against digital fraud and smuggling.
"""

customs_context = StringKnowledgeSource(
    content=about_customs
)
