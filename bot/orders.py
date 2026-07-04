"""
Order-level logic that sits between the CLI and the Binance client.

OrderRequest validates and holds a ready-to-submit order.
execute_order() sends it and returns a clean result dict.
format_result() turns that dict into readable CLI output.
"""

import logging

from bot.client import BinanceFuturesClient
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)

logger = logging.getLogger("trading_bot")


class OrderRequest:
    """A validated, ready-to-submit order."""

    def __init__(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        self.order_type = validate_order_type(order_type)
        self.symbol = validate_symbol(symbol)
        self.side = validate_side(side)
        self.quantity = validate_quantity(quantity)
        self.price = validate_price(price, self.order_type)
        self.stop_price = validate_stop_price(stop_price, self.order_type)

    def summary(self) -> str:
        lines = [
            "Order Request",
            f"  Symbol:     {self.symbol}",
            f"  Side:       {self.side}",
            f"  Type:       {self.order_type}",
            f"  Quantity:   {self.quantity}",
        ]
        if self.order_type == "LIMIT":
            lines.append(f"  Price:      {self.price}")
        if self.order_type == "STOP_MARKET":
            lines.append(f"  Stop Price: {self.stop_price}")
        return "\n".join(lines)


def execute_order(client: BinanceFuturesClient, order: OrderRequest) -> dict:
    """
    Sends the order via the client and returns a clean summary dict.
    Any exception from the client is left to bubble up to the caller.
    """
    response = client.place_order(
        symbol=order.symbol,
        side=order.side,
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
        stop_price=order.stop_price,
    )

    return {
        "orderId": response.get("orderId"),
        "status": response.get("status"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice"),
        "raw": response,
    }


def format_result(result: dict) -> str:
    lines = [
        "Order Response",
        f"  Order ID:     {result['orderId']}",
        f"  Status:       {result['status']}",
        f"  Executed Qty: {result['executedQty']}",
        f"  Avg Price:    {result['avgPrice']}",
    ]
    return "\n".join(lines)
