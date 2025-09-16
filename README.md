# Bulletin Driven Alpaca Trading Bot

This project demonstrates how to connect three different data sources to drive fully automated 
stock trades:

1. **Bulletins** – curated text files summarising catalysts affecting a company.
2. **ChatGPT research** – optional context from OpenAI's chat completions API.
3. **Alpaca** – a brokerage API used to place trades (paper or live accounts).

The sample bot analyses local bulletin documents, feeds the context to ChatGPT for a high level
summary, and then decides whether to buy, sell, or hold a symbol before optionally submitting the
order to Alpaca.

## Getting started

1. Create and activate a Python 3.11 environment.
2. (Optional) Install the development dependency used by the unit tests:

   ```bash
   pip install -r requirements.txt
   ```

3. Add the `src` directory to your `PYTHONPATH` so Python can locate the package:

   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

4. Export the credentials used by the integrations (only the Alpaca keys are required for live
   trading; the OpenAI key enables the research step):

   ```bash
   export ALPACA_API_KEY="your alpaca key"
   export ALPACA_SECRET_KEY="your alpaca secret"
   export OPENAI_API_KEY="sk-..."  # optional
   ```

   The bot defaults to the Alpaca paper trading base URL. Set `ALPACA_BASE_URL` if you want to point
   at a different environment.

5. Prepare a directory of bulletin `.txt` files. Two sample bulletins are provided under
   `data/bulletins` and are automatically loaded by default.

6. Run the bot in dry-run mode (no orders will be transmitted) and inspect the decision making
   output:

   ```bash
   python -m trading_bot.main MEGATECH
   ```

   When you are satisfied with the behaviour, remove the dry-run guard and let the bot submit real
   orders:

   ```bash
   python -m trading_bot.main MEGATECH --live --qty 5
   ```

   All thresholds are configurable via command line flags.

## Project layout

```
src/trading_bot/
├── alpaca_trader.py      # Thin REST client for Alpaca orders
├── bulletin_analyzer.py  # Keyword + sentiment scoring for bulletin text
├── bulletin_loader.py    # Utilities to load bulletin documents from disk
├── chatgpt_researcher.py # Optional ChatGPT integration via the REST API
├── config.py             # Environment variable based configuration helpers
├── main.py               # Command line orchestration and decision making
└── strategy.py           # Converts sentiment metrics into trade decisions
```

The unit tests exercise the sentiment scoring logic to ensure that positive and negative bulletins
influence the aggregate score as expected:

```bash
pytest
```

## Extending the bot

* Replace the heuristic sentiment lists in `bulletin_analyzer.py` with a full NLP library such as
  spaCy, TextBlob, or a transformer model.
* Swap the bulletin loader to pull from RSS feeds, a CMS, or internal research notes instead of
  static files.
* Introduce position sizing logic that adjusts order quantity based on confidence or account equity.
* Schedule the bot (e.g. via cron or a workflow orchestrator) so that new bulletins automatically
  result in timely trading decisions.
