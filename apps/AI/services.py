import os

from agno.agent import Agent
from agno.models.groq import Groq
from core.knowledge.knowledge import knowledge


agent = Agent(
    model=Groq(
        id=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        api_key=os.getenv("GROQ_API_KEY"),
    ),
    knowledge=knowledge,
    add_knowledge_to_context=True,
    search_knowledge=False,
    instructions=[
        "Voce e um assistente chamado Oraculo.",
        "Use o conhecimento fornecido para responder.",
        "Se nao houver contexto suficiente, diga claramente.",
        "Nunca mostre chamadas de ferramenta ou tags como <function=...>.",
        "Quando houver referencias do documento, responda somente com base nelas.",
    ],
)
