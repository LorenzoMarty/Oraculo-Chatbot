import os

from agno.agent import Agent
from agno.models.groq import Groq
from core.knowledge.vectorstore import knowledge


agent = Agent(
    model=Groq(
        id=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        api_key=os.getenv("GROQ_API_KEY"),
    ),
    knowledge=knowledge,
    add_knowledge_to_context=True,
    search_knowledge=False,
    instructions=open("core/prompts/oraculo.md").read(),
)
