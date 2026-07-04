
# Entry point. Parses args, validates input, places the order, prints result
"""
CLI entry point for the trading bot.

Examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
  python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 58000
"""

import argparse
import os
import sys

from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException
from requests.exceptions import ConnectionError, Timeout
from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root and sets the variables it contains

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient
from bot.orders import OrderRequest, execute_order, format_result
from bot.validators import ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET, LIMIT, or STOP_MARKET orders on Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, help="BUY or SELL")
    parser.add_argument("--type", required=True, dest="order_type",
                         help="MARKET, LIMIT, or STOP_MARKET")
    parser.add_argument("--quantity", required=True, help="Order quantity")
    parser.add_argument("--price", required=False, help="Required for LIMIT orders")
    parser.add_argument("--stop-price", required=False, dest="stop_price",
                         help="Required for STOP_MARKET orders")
    return parser


def main():
    logger = setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

    if not api_key or not api_secret:
        print("ERROR: Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET in your .env file.")
        sys.exit(1)

    try:
        order = OrderRequest(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        print(f"Invalid input: {e}")
        sys.exit(1)

    print(order.summary())
    print()

    try:
        client = BinanceFuturesClient(api_key, api_secret)
        result = execute_order(client, order)
        print(format_result(result))
        print("\nOrder placed successfully.")
    except (BinanceAPIException, BinanceOrderException, BinanceRequestException) as e:
        logger.error(f"Order failed (API error): {e}")
        print(f"\nOrder failed: {e}")
        sys.exit(1)
    except (ConnectionError, Timeout) as e:
        logger.error(f"Order failed (network error): {e}")
        print(f"\nNetwork error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Order failed (unexpected error): {e}")
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()