from agno.agent import Agent
from agno.models.groq import Groq
from core.knowledge.knowledge import knowledge


agent = Agent(
    model=Groq(id="llama-3.1-8b-instant"),
    knowledge=knowledge,
    instructions=[
        "Você é um assistente chamado Oráculo",
        "Use o conhecimento fornecido para responder",
        "Se não souber, diga claramente",
    ],
)
