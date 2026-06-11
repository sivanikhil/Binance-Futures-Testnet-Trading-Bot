"""Order placement orchestration."""

from __future__ import annotations

import logging
from typing import Any

from .client import BinanceFuturesClient
from .validators import validate_order_args


class OrderService:
    """Validates order inputs and delegates placement to the API client."""

    def __init__(self, client: BinanceFuturesClient, logger: logging.Logger | None = None) -> None:
        self.client = client
        self.logger = logger or logging.getLogger("trading_bot")

    def build_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: str | None = None,
    ) -> dict[str, str]:
        return validate_order_args(symbol, side, order_type, quantity, price)

    def place_order(self, order: dict[str, str]) -> dict[str, Any]:
        self.logger.info("Placing order | order=%s", order)
        response = self.client.place_order(order)
        self.logger.info(
            "Order placed | orderId=%s status=%s executedQty=%s",
            response.get("orderId"),
            response.get("status"),
            response.get("executedQty"),
        )
        return response

