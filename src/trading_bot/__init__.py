"""Trading bot package that links bulletin analysis, ChatGPT research, and Alpaca trading."""

from .alpaca_trader import AlpacaTrader
from .bulletin_analyzer import BulletinAnalyzer
from .bulletin_loader import Bulletin, load_bulletins
from .chatgpt_researcher import ChatGPTResearcher
from .config import BotConfig, AlpacaConfig, OpenAIConfig
from .strategy import SentimentStrategy, TradeDecision

__all__ = [
    "AlpacaTrader",
    "BulletinAnalyzer",
    "Bulletin",
    "load_bulletins",
    "ChatGPTResearcher",
    "BotConfig",
    "AlpacaConfig",
    "OpenAIConfig",
    "SentimentStrategy",
    "TradeDecision",
]
