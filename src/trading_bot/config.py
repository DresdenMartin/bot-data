"""Configuration helpers for the trading bot."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AlpacaConfig:
    """Configuration required to interact with the Alpaca trading API."""

    api_key: str
    api_secret: str
    base_url: str = "https://paper-api.alpaca.markets"

    @classmethod
    def from_env(cls) -> "AlpacaConfig":
        """Create a configuration object from environment variables."""

        api_key = os.environ.get("ALPACA_API_KEY", "").strip()
        api_secret = os.environ.get("ALPACA_SECRET_KEY", "").strip()
        base_url = os.environ.get("ALPACA_BASE_URL", cls.base_url).strip()

        if not api_key or not api_secret:
            raise ValueError(
                "Alpaca API credentials are missing. "
                "Please set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables."
            )

        return cls(api_key=api_key, api_secret=api_secret, base_url=base_url)


@dataclass
class OpenAIConfig:
    """Configuration for the optional ChatGPT research integration."""

    api_key: str
    model: str = "gpt-3.5-turbo"
    base_url: str = "https://api.openai.com/v1"

    @classmethod
    def from_env(cls) -> Optional["OpenAIConfig"]:
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            return None

        model = os.environ.get("OPENAI_MODEL", cls.model).strip() or cls.model
        base_url = os.environ.get("OPENAI_BASE_URL", cls.base_url).strip() or cls.base_url
        return cls(api_key=api_key, model=model, base_url=base_url)


@dataclass
class BotConfig:
    """Aggregate configuration for the trading bot."""

    alpaca: Optional[AlpacaConfig]
    openai: Optional[OpenAIConfig]

    @classmethod
    def from_env(cls, require_alpaca: bool = False) -> "BotConfig":
        alpaca_cfg: Optional[AlpacaConfig] = None
        if require_alpaca:
            alpaca_cfg = AlpacaConfig.from_env()
        else:
            try:
                alpaca_cfg = AlpacaConfig.from_env()
            except ValueError:
                alpaca_cfg = None

        openai_cfg = OpenAIConfig.from_env()
        return cls(alpaca=alpaca_cfg, openai=openai_cfg)
