"""Command line entry point for the Alpaca + ChatGPT powered trading bot."""
from __future__ import annotations

import argparse
import logging
import textwrap
from typing import List, Optional

from .alpaca_trader import AlpacaTrader
from .bulletin_analyzer import BulletinAnalyzer
from .bulletin_loader import Bulletin, load_bulletins
from .chatgpt_researcher import ChatGPTResearcher
from .config import BotConfig
from .strategy import SentimentStrategy


LOGGER = logging.getLogger("trading_bot")


def format_context(bulletins: List[Bulletin], max_chars: int = 1200) -> str:
    sections: List[str] = []
    for bulletin in bulletins:
        snippet = textwrap.shorten(bulletin.content.replace("\n", " "), width=240, placeholder="...")
        sections.append(f"{bulletin.title}: {snippet}")
    context = "\n".join(sections)
    return context[:max_chars]


def run_bot(
    symbol: str,
    bulletin_dir: str,
    quantity: int,
    dry_run: bool,
    buy_threshold: float,
    sell_threshold: float,
) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    bulletins = load_bulletins(bulletin_dir)
    if not bulletins:
        LOGGER.warning("No bulletins found in %s", bulletin_dir)

    analyzer = BulletinAnalyzer()
    analyses = [analyzer.analyze(bulletin) for bulletin in bulletins]

    bot_config = BotConfig.from_env(require_alpaca=not dry_run)

    research_summary: Optional[str] = None
    if bot_config.openai and bulletins:
        try:
            researcher = ChatGPTResearcher(bot_config.openai)
            research = researcher.research(symbol=symbol, context=format_context(bulletins))
            research_summary = research.summary
        except Exception as exc:  # pragma: no cover - network failure is hard to simulate
            LOGGER.error("ChatGPT research failed: %s", exc)
    elif not bot_config.openai:
        LOGGER.info("OPENAI_API_KEY not set; skipping ChatGPT research integration")

    strategy = SentimentStrategy(buy_threshold=buy_threshold, sell_threshold=sell_threshold)
    decision = strategy.decide(symbol, analyses, research_summary)

    LOGGER.info("Decision for %s: %s (confidence %.2f)", symbol, decision.action, decision.confidence)
    LOGGER.info("Reason: %s", decision.reason)

    if not decision.should_trade():
        LOGGER.info("No trade executed; action is HOLD")
        return

    if bot_config.alpaca is None:
        LOGGER.warning("Alpaca credentials missing; cannot submit order")
        return

    trader = AlpacaTrader(bot_config.alpaca)
    try:
        result = trader.submit_order(
            symbol=symbol,
            qty=quantity,
            side=decision.action,
            dry_run=dry_run,
        )
    except Exception as exc:  # pragma: no cover - depends on remote API
        LOGGER.error("Failed to submit order: %s", exc)
        return

    if result.submitted:
        LOGGER.info("Order submitted: %s", result.detail.get("id", "<no id>"))
    else:
        LOGGER.info("Dry run order payload: %s", result.detail)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the bulletin driven Alpaca trading bot")
    parser.add_argument("symbol", help="Ticker symbol to trade, e.g. AAPL")
    parser.add_argument(
        "--bulletin-dir",
        default="data/bulletins",
        help="Directory containing bulletin .txt files",
    )
    parser.add_argument("--qty", type=int, default=1, help="Number of shares to trade")
    parser.add_argument("--live", action="store_true", help="Disable dry-run mode and submit real orders")
    parser.add_argument(
        "--buy-threshold",
        type=float,
        default=0.25,
        help="Average sentiment required before placing a buy order",
    )
    parser.add_argument(
        "--sell-threshold",
        type=float,
        default=-0.25,
        help="Average sentiment required before placing a sell order",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_bot(
        symbol=args.symbol.upper(),
        bulletin_dir=args.bulletin_dir,
        quantity=args.qty,
        dry_run=not args.live,
        buy_threshold=args.buy_threshold,
        sell_threshold=args.sell_threshold,
    )


if __name__ == "__main__":
    main()
