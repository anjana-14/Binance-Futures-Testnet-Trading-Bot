"""Order placement logic for Binance Futures Testnet."""

import logging
from dataclasses import dataclass
from typing import Any

from bot.client import BinanceFuturesClient
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_symbol,
)

logger = logging.getLogger("trading_bot.orders")


@dataclass
class OrderRequest:
    """Validated order parameters ready for the API."""

    symbol: str
    side: str
    order_type: str
    quantity: str
    price: str | None = None

    def to_api_params(self) -> dict[str, Any]:
        """Convert to the parameter dict Binance expects."""
        params: dict[str, Any] = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
        }

        if self.order_type == "LIMIT":
            params["price"] = self.price
            params["timeInForce"] = "GTC"

        return params

    def summary(self) -> str:
        """Human-readable summary for CLI output."""
        lines = [
            f"  Symbol:    {self.symbol}",
            f"  Side:      {self.side}",
            f"  Type:      {self.order_type}",
            f"  Quantity:  {self.quantity}",
        ]
        if self.price:
            lines.append(f"  Price:     {self.price}")
        return "\n".join(lines)


def build_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
) -> OrderRequest:
    """
    Validate raw CLI inputs and return a structured order request.

    Raises ValidationError if any field is invalid.
    """
    validated_type = validate_order_type(order_type)
    validated_price = validate_price(price, validated_type)

    request = OrderRequest(
        symbol=validate_symbol(symbol),
        side=validate_side(side),
        order_type=validated_type,
        quantity=validate_quantity(quantity),
        price=validated_price,
    )

    logger.debug("Built order request: %s", request.to_api_params())
    return request


def place_order(client: BinanceFuturesClient, order: OrderRequest) -> dict[str, Any]:
    """Place an order using the provided client and validated request."""
    params = order.to_api_params()
    logger.info("Placing %s %s order for %s %s", order.side, order.order_type, order.quantity, order.symbol)
    return client.place_order(params)


def format_order_response(response: dict[str, Any]) -> str:
    """Format the API response fields we care about for console output."""
    fields = [
        ("orderId", "Order ID"),
        ("status", "Status"),
        ("executedQty", "Executed Qty"),
        ("avgPrice", "Avg Price"),
        ("origQty", "Original Qty"),
        ("price", "Price"),
        ("updateTime", "Update Time"),
    ]

    lines = []
    for key, label in fields:
        value = response.get(key)
        if value is not None and value != "" and value != "0":
            lines.append(f"  {label}: {value}")

    if not lines:
        return "  (no detail fields returned)"

    return "\n".join(lines)
