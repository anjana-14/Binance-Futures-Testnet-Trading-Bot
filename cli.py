#!/usr/bin/env python3
"""CLI entry point for placing orders on Binance Futures Testnet."""

import argparse
import sys

from bot.client import BinanceFuturesClient
from bot.exceptions import BinanceAPIError, NetworkError, TradingBotError, ValidationError
from bot.logging_config import setup_logging
from bot.orders import build_order_request, format_order_response, place_order


def build_parser() -> argparse.ArgumentParser:
    """Configure CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Place MARKET or LIMIT orders on Binance USDT-M Futures Testnet.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001\n"
            "  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500\n"
        ),
    )

    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        help="Order type",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", help="Limit price (required for LIMIT orders)")
    parser.add_argument(
        "--log-dir",
        default="logs",
        help="Directory for log files (default: logs)",
    )

    return parser


def run(args: argparse.Namespace) -> int:
    """
    Execute the order flow: validate, submit, print results.

    Returns 0 on success, 1 on failure.
    """
    logger = setup_logging(args.log_dir)

    try:
        order = build_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 1

    print("\n--- Order Request ---")
    print(order.summary())

    try:
        client = BinanceFuturesClient()
        response = place_order(client, order)
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        print(f"\nSetup error: {exc}", file=sys.stderr)
        return 1
    except NetworkError as exc:
        logger.error("Network failure: %s", exc)
        print(f"\nNetwork error: {exc}", file=sys.stderr)
        return 1
    except BinanceAPIError as exc:
        logger.error("API rejection: %s", exc)
        print(f"\nOrder failed: {exc}", file=sys.stderr)
        return 1
    except TradingBotError as exc:
        logger.exception("Unexpected bot error")
        print(f"\nUnexpected error: {exc}", file=sys.stderr)
        return 1

    print("\n--- Order Response ---")
    print(format_order_response(response))
    print("\nOrder placed successfully.")
    return 0


def main() -> None:
    """Parse arguments and run the CLI."""
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
