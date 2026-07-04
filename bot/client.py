# Wrapper around python-binance for Futures Testnet
# Keeps all direct Binance API calls in one place

import logging

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

logger = logging.getLogger("trading_bot")

FUTURES_TESTNET_URL = "https://testnet.binancefuture.com/fapi"


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")

        logger.info("Initializing Binance Futures Testnet client")
        self.client = Client(api_key, api_secret, testnet=True)
        # Explicitly pin the futures endpoint to testnet, since testnet=True
        # mainly guarantees the spot endpoint — this line makes sure futures
        # orders never accidentally hit the live exchange.
        self.client.FUTURES_URL = FUTURES_TESTNET_URL

    def place_order(self, symbol: str, side: str, order_type: str,
                     quantity: float, price: float = None, stop_price: float = None) -> dict:
        """
        Places an order on Binance Futures Testnet.
        Raises BinanceAPIException / BinanceOrderException / BinanceRequestException on failure.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"  # Good-Til-Cancelled, required for LIMIT orders

        if order_type == "STOP_MARKET":
            params["stopPrice"] = stop_price

        logger.info(f"Sending order request: {params}")

        try:
            response = self.client.futures_create_order(**params)
            logger.info(f"Order response: {response}")
            return response
        except (BinanceAPIException, BinanceOrderException, BinanceRequestException) as e:
            logger.error(f"Binance API error while placing order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while placing order: {e}")
            raise

    def get_account_balance(self):
        """Optional helper, handy for sanity-checking testnet funds before placing orders."""
        try:
            balances = self.client.futures_account_balance()
            logger.info(f"Fetched account balance: {balances}")
            return balances
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Error fetching balance: {e}")
            raise
