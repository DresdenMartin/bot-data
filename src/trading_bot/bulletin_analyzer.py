"""Analyze raw bulletin text to derive trading signals."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List

from .bulletin_loader import Bulletin

POSITIVE_WORDS = {
    "beat",
    "bullish",
    "buy",
    "climb",
    "expand",
    "growth",
    "improve",
    "optimistic",
    "outperform",
    "profit",
    "rally",
    "record",
    "surge",
    "support",
}

NEGATIVE_WORDS = {
    "bearish",
    "concern",
    "contraction",
    "decline",
    "downgrade",
    "drop",
    "fall",
    "fear",
    "loss",
    "lower",
    "miss",
    "risk",
    "sell",
    "slip",
    "slow",
    "uncertain",
    "weak",
}

STOPWORDS = {
    "a",
    "an",
    "the",
    "and",
    "or",
    "but",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "by",
    "is",
    "are",
    "was",
    "were",
    "be",
    "as",
    "that",
    "this",
    "it",
    "from",
    "at",
    "after",
    "before",
    "over",
    "under",
    "about",
    "into",
    "their",
    "its",
    "they",
    "will",
}


TOKEN_RE = re.compile(r"[A-Za-z']+")


def tokenize(text: str) -> List[str]:
    return [token.lower() for token in TOKEN_RE.findall(text)]


@dataclass
class BulletinAnalysis:
    """Result of analyzing a single bulletin."""

    bulletin: Bulletin
    sentiment_score: float
    keywords: List[str]
    positive_mentions: int
    negative_mentions: int

    @property
    def sentiment_label(self) -> str:
        if self.sentiment_score > 0.1:
            return "positive"
        if self.sentiment_score < -0.1:
            return "negative"
        return "neutral"


class BulletinAnalyzer:
    """Perform lightweight sentiment analysis on market bulletins."""

    def __init__(self, positive_words: Iterable[str] = POSITIVE_WORDS, negative_words: Iterable[str] = NEGATIVE_WORDS):
        self.positive_words = set(positive_words)
        self.negative_words = set(negative_words)

    def analyze(self, bulletin: Bulletin) -> BulletinAnalysis:
        tokens = tokenize(bulletin.content)
        token_counts = Counter(tokens)

        positive = sum(token_counts[word] for word in self.positive_words)
        negative = sum(token_counts[word] for word in self.negative_words)
        total = positive + negative

        sentiment_score = 0.0
        if total:
            sentiment_score = (positive - negative) / math.sqrt(total)

        keywords = [word for word, count in token_counts.most_common() if word not in STOPWORDS][:5]

        return BulletinAnalysis(
            bulletin=bulletin,
            sentiment_score=sentiment_score,
            keywords=keywords,
            positive_mentions=positive,
            negative_mentions=negative,
        )

    def aggregate(self, analyses: Iterable[BulletinAnalysis]) -> float:
        scores = [analysis.sentiment_score for analysis in analyses]
        if not scores:
            return 0.0
        return sum(scores) / len(scores)
