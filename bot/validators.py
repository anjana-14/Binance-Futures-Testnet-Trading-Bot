"""Input validation for CLI order parameters."""

from decimal import Decimal, InvalidOperation

from bot.exceptions import ValidationError

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


def validate_symbol(symbol: str) -> str:
    """Normalize and validate a futures trading pair symbol."""
    if not symbol or not symbol.strip():
        raise ValidationError("Symbol cannot be empty. Example: BTCUSDT")

    normalized = symbol.strip().upper()

    if not normalized.isalnum():
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Use alphanumeric pairs like BTCUSDT or ETHUSDT."
        )

    if len(normalized) < 5:
        raise ValidationError(
            f"Symbol '{normalized}' looks too short. Did you mean something like BTCUSDT?"
        )

    return normalized


def validate_side(side: str) -> str:
    """Validate order side (BUY or SELL)."""
    normalized = side.strip().upper()

    if normalized not in VALID_SIDES:
        raise ValidationError(
            f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}"
        )

    return normalized


def validate_order_type(order_type: str) -> str:
    """Validate order type (MARKET or LIMIT)."""
    normalized = order_type.strip().upper()

    if normalized not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}"
        )

    return normalized


def validate_quantity(quantity: str) -> str:
    """Validate order quantity is a positive number."""
    try:
        value = Decimal(quantity.strip())
    except (InvalidOperation, AttributeError):
        raise ValidationError(
            f"Invalid quantity '{quantity}'. Provide a positive number, e.g. 0.001"
        ) from None

    if value <= 0:
        raise ValidationError(f"Quantity must be greater than zero, got {quantity}")

    # Strip trailing zeros but keep enough precision for the API
    normalized = format(value.normalize(), "f")
    return normalized


def validate_price(price: str | None, order_type: str) -> str | None:
    """Validate limit price when required."""
    if order_type == "MARKET":
        if price is not None and str(price).strip():
            raise ValidationError("Price should not be provided for MARKET orders.")
        return None

    if price is None or not str(price).strip():
        raise ValidationError("Price is required for LIMIT orders. Example: --price 65000")

    try:
        value = Decimal(str(price).strip())
    except (InvalidOperation, AttributeError):
        raise ValidationError(
            f"Invalid price '{price}'. Provide a positive number, e.g. 65000.50"
        ) from None

    if value <= 0:
        raise ValidationError(f"Price must be greater than zero, got {price}")

    return format(value.normalize(), "f")
