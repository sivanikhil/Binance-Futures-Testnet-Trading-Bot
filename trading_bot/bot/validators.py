"""Input validation helpers for order commands."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from .exceptions import ValidationError

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


def normalize_symbol(symbol: str) -> str:
    value = symbol.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(value):
        raise ValidationError("symbol must be 5-20 uppercase letters/numbers, e.g. BTCUSDT")
    return value


def normalize_side(side: str) -> str:
    value = side.strip().upper()
    if value not in VALID_SIDES:
        raise ValidationError("side must be BUY or SELL")
    return value


def normalize_order_type(order_type: str) -> str:
    value = order_type.strip().upper()
    if value not in VALID_ORDER_TYPES:
        raise ValidationError("order type must be MARKET or LIMIT")
    return value


def parse_positive_decimal(name: str, value: str | float | int | None) -> Decimal:
    if value is None:
        raise ValidationError(f"{name} is required")

    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{name} must be a valid number") from exc

    if decimal_value <= 0:
        raise ValidationError(f"{name} must be greater than zero")

    return decimal_value


def decimal_to_api_string(value: Decimal) -> str:
    return format(value.normalize(), "f")


def validate_order_args(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
) -> dict[str, str]:
    normalized_type = normalize_order_type(order_type)
    validated = {
        "symbol": normalize_symbol(symbol),
        "side": normalize_side(side),
        "type": normalized_type,
        "quantity": decimal_to_api_string(parse_positive_decimal("quantity", quantity)),
    }

    if normalized_type == "LIMIT":
        validated["price"] = decimal_to_api_string(parse_positive_decimal("price", price))
        validated["timeInForce"] = "GTC"
    elif price is not None:
        raise ValidationError("price is only accepted for LIMIT orders")

    return validated

