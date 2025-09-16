from trading_bot.bulletin_analyzer import BulletinAnalyzer
from trading_bot.bulletin_loader import Bulletin


def make_bulletin(content: str) -> Bulletin:
    return Bulletin(title="Test", content=content, source="test", path=None)  # type: ignore[arg-type]


def test_positive_bulletin_scores_above_zero():
    analyzer = BulletinAnalyzer()
    bulletin = make_bulletin("Strong growth and bullish profit outlook with record demand")
    analysis = analyzer.analyze(bulletin)
    assert analysis.sentiment_score > 0
    assert "growth" in analysis.keywords


def test_negative_bulletin_scores_below_zero():
    analyzer = BulletinAnalyzer()
    bulletin = make_bulletin("Analysts warn of weak demand and falling revenue leading to loss")
    analysis = analyzer.analyze(bulletin)
    assert analysis.sentiment_score < 0


def test_aggregate_sentiment():
    analyzer = BulletinAnalyzer()
    positive = analyzer.analyze(make_bulletin("bullish profit rally"))
    negative = analyzer.analyze(make_bulletin("bearish loss risk"))
    average = analyzer.aggregate([positive, negative])
    assert abs(average) < max(abs(positive.sentiment_score), abs(negative.sentiment_score))
