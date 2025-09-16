"""Trading strategy that converts bulletin analysis into actionable orders."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .bulletin_analyzer import BulletinAnalysis


@dataclass
class TradeDecision:
    symbol: str
    action: str
    confidence: float
    reason: str

    def should_trade(self) -> bool:
        return self.action in {"buy", "sell"}


class SentimentStrategy:
    """Apply simple heuristics on sentiment scores to decide trades."""

    def __init__(self, buy_threshold: float = 0.25, sell_threshold: float = -0.25):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def decide(
        self,
        symbol: str,
        analyses: Iterable[BulletinAnalysis],
        research_summary: Optional[str] = None,
    ) -> TradeDecision:
        analyses = list(analyses)
        if not analyses:
            return TradeDecision(
                symbol=symbol,
                action="hold",
                confidence=0.0,
                reason="No bulletin data available",
            )

        avg_sentiment = sum(analysis.sentiment_score for analysis in analyses) / len(analyses)
        strongest_bulletin = max(analyses, key=lambda a: abs(a.sentiment_score))

        reason_parts = [
            f"Average sentiment {avg_sentiment:+.2f} from {len(analyses)} bulletins",
            f"Strongest bulletin '{strongest_bulletin.bulletin.title}' is {strongest_bulletin.sentiment_label}",
        ]

        if research_summary:
            reason_parts.append(f"ChatGPT summary: {research_summary.splitlines()[0]}")

        action = "hold"
        confidence = min(1.0, abs(avg_sentiment))

        if avg_sentiment >= self.buy_threshold:
            action = "buy"
        elif avg_sentiment <= self.sell_threshold:
            action = "sell"

        return TradeDecision(
            symbol=symbol,
            action=action,
            confidence=confidence,
            reason="; ".join(reason_parts),
        )
