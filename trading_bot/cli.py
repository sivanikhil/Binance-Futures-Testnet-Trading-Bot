"""Command line entry point for the Binance Futures testnet trading bot."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is listed, fallback keeps import robust
    load_dotenv = None

from bot.client import BinanceFuturesClient, TESTNET_BASE_URL
from bot.exceptions import BinanceAPIError, TradingBotError, ValidationError
from bot.logging_config import setup_logging
from bot.orders import OrderService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET and LIMIT orders on Binance USDT-M Futures Testnet."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair symbol, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity, e.g. 0.001")
    parser.add_argument("--price", help="Required for LIMIT orders")
    parser.add_argument("--base-url", default=TESTNET_BASE_URL, help="Binance Futures testnet base URL")
    parser.add_argument("--log-file", default="logs/trading_bot.log", help="Path to log file")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print the request without sending it")
    parser.add_argument("--verbose", action="store_true", help="Also print debug logs to the console")
    return parser


def print_order_summary(order: dict[str, str], dry_run: bool) -> None:
    print("\nOrder Request Summary")
    print("---------------------")
    for key in ["symbol", "side", "type", "quantity", "price", "timeInForce"]:
        if key in order:
            print(f"{key}: {order[key]}")
    if dry_run:
        print("mode: DRY RUN (no API request sent)")


def print_order_response(response: dict[str, Any]) -> None:
    print("\nOrder Response Details")
    print("----------------------")
    fields = {
        "orderId": response.get("orderId"),
        "status": response.get("status"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice"),
        "clientOrderId": response.get("clientOrderId"),
    }
    for key, value in fields.items():
        if value is not None:
            print(f"{key}: {value}")


def main(argv: list[str] | None = None) -> int:
    if load_dotenv:
        load_dotenv()

    parser = build_parser()
    args = parser.parse_args(argv)
    logger = setup_logging(args.log_file, verbose=args.verbose)

    try:
        placeholder_client = None
        if not args.dry_run:
            api_key = os.getenv("BINANCE_API_KEY", "")
            api_secret = os.getenv("BINANCE_API_SECRET", "")
            if not api_key or not api_secret:
                raise ValidationError(
                    "BINANCE_API_KEY and BINANCE_API_SECRET must be set, or use --dry-run"
                )
            placeholder_client = BinanceFuturesClient(
                api_key=api_key,
                api_secret=api_secret,
                base_url=args.base_url,
                logger=logger,
            )

        service = OrderService(placeholder_client, logger=logger)  # type: ignore[arg-type]
        order = service.build_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
        print_order_summary(order, dry_run=args.dry_run)
        logger.info("Order request summary | dry_run=%s order=%s", args.dry_run, order)

        if args.dry_run:
            print("\nSuccess: order input is valid. No API request was sent.")
            logger.info("Dry run successful | order=%s", order)
            return 0

        response = service.place_order(order)
        print_order_response(response)
        print("\nSuccess: order submitted to Binance Futures Testnet.")
        return 0

    except ValidationError as exc:
        logger.error("Validation failure | error=%s", exc)
        print(f"\nFailure: {exc}", file=sys.stderr)
        return 2
    except BinanceAPIError as exc:
        logger.error("API failure | error=%s", exc)
        print(f"\nFailure: {exc}", file=sys.stderr)
        return 1
    except TradingBotError as exc:
        logger.error("Trading bot failure | error=%s", exc)
        print(f"\nFailure: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - final safety net for CLI users
        logger.exception("Unexpected failure | error=%s", exc)
        print(f"\nFailure: unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

