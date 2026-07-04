
"""
CLI entry point for the trading bot.

Two ways to run it:

1. Flag-driven (fast, scriptable):
     python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
     python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
     python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 58000

2. Interactive (no flags — guided menus and prompts):
     python cli.py
"""

import argparse
import os
import sys

from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException
from requests.exceptions import ConnectionError, Timeout
from dotenv import load_dotenv

load_dotenv()

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient
from bot.orders import OrderRequest, execute_order, format_result
from bot.validators import ValidationError
from bot.interactive import run_interactive_flow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Place MARKET, LIMIT, or STOP_MARKET orders on Binance Futures Testnet (USDT-M). "
                    "Run with no arguments for an interactive guided mode."
    )
    parser.add_argument("--symbol", required=False, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=False, help="BUY or SELL")
    parser.add_argument("--type", required=False, dest="order_type",
                         help="MARKET, LIMIT, or STOP_MARKET")
    parser.add_argument("--quantity", required=False, help="Order quantity")
    parser.add_argument("--price", required=False, help="Required for LIMIT orders")
    parser.add_argument("--stop-price", required=False, dest="stop_price",
                         help="Required for STOP_MARKET orders")
    return parser


def get_credentials():
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
    if not api_key or not api_secret:
        print("ERROR: Set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET in your .env file.")
        sys.exit(1)
    return api_key, api_secret


def place_and_report(logger, order: OrderRequest):
    print(order.summary())
    print()

    api_key, api_secret = get_credentials()

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


def main():
    logger = setup_logging()

    if len(sys.argv) == 1:
        collected = run_interactive_flow()
        if collected is None:
            sys.exit(0)
        try:
            order = OrderRequest(**collected)
        except ValidationError as e:
            logger.error(f"Validation failed: {e}")
            print(f"\nInvalid input: {e}")
            sys.exit(1)
        place_and_report(logger, order)
        return

    parser = build_parser()
    args = parser.parse_args()

    missing = [name for name in ("symbol", "side", "order_type", "quantity")
               if getattr(args, name) is None]
    if missing:
        print(f"Missing required flag(s): {', '.join('--' + m.replace('order_type', 'type') for m in missing)}")
        print("Tip: run 'python cli.py' with no arguments for guided interactive mode.")
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

    place_and_report(logger, order)


if __name__ == "__main__":
    main()