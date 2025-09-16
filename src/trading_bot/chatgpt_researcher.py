"""Integration with the OpenAI Chat Completions API for market research."""
from __future__ import annotations

from dataclasses import dataclass

from .config import OpenAIConfig
from .http import post_json


DEFAULT_PROMPT = """
You are a financial analyst helping to contextualize equity market news. Provide a concise
three bullet point summary about {symbol} given the following bulletin excerpts:
{context}
End with a short sentence indicating whether the tone is bullish, bearish, or neutral.
""".strip()


@dataclass
class ResearchResult:
    symbol: str
    summary: str


class ChatGPTResearcher:
    """Lightweight wrapper around the OpenAI chat completions API."""

    def __init__(self, config: OpenAIConfig):
        self.config = config

    def research(self, symbol: str, context: str, prompt_template: str = DEFAULT_PROMPT) -> ResearchResult:
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "You are an assistant that writes finance bulletins."},
                {"role": "user", "content": prompt_template.format(symbol=symbol, context=context)},
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
        }

        response = post_json(
            f"{self.config.base_url}/chat/completions",
            payload=payload,
            headers=headers,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenAI API request failed with status {response.status_code}: {response.text[:200]}"
            )

        data = response.json()
        message = data["choices"][0]["message"]["content"].strip()
        return ResearchResult(symbol=symbol, summary=message)
