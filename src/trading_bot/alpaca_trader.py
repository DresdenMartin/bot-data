"""Simple REST client for submitting orders to Alpaca."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .config import AlpacaConfig
from .http import post_json


@dataclass
class OrderResult:
    """Response returned after attempting to submit an order."""

    submitted: bool
    detail: Dict[str, Any]


class AlpacaTrader:
    """Interact with the Alpaca REST API."""

    def __init__(self, config: AlpacaConfig):
        self.config = config

    def submit_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = "market",
        time_in_force: str = "gtc",
        dry_run: bool = True,
    ) -> OrderResult:
        """Submit an order to Alpaca.

        When ``dry_run`` is ``True`` the order is not actually transmitted and a
        simulated response is returned instead.
        """

        payload = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
        }

        if dry_run:
            return OrderResult(submitted=False, detail={"order": payload, "message": "dry run"})

        headers = {
            "APCA-API-KEY-ID": self.config.api_key,
            "APCA-API-SECRET-KEY": self.config.api_secret,
        }

        response = post_json(
            f"{self.config.base_url}/v2/orders",
            payload=payload,
            headers=headers,
        )

        if response.status_code >= 300:
            raise RuntimeError(
                f"Alpaca order request failed with status {response.status_code}: {response.text[:200]}"
            )

        return OrderResult(submitted=True, detail=response.json())
