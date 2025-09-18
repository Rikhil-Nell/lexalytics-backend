from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIModelName
from pydantic_ai.providers.openai import OpenAIProvider
from app.core.config import settings

model_name: OpenAIModelName = "gpt-4.1"

model = OpenAIChatModel(
    model_name,
    provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY),
)

agent = Agent(model, instructions="Given the draft for a Ministry of Corporate affairs, summarize it in a disinterested manner")
