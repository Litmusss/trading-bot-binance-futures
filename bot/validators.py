
# Basic input checks for symbol, side, order type, quantity, price, stop price

VALID_SIDES = {"BUY", "SELL"}
VALID_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}  # STOP_MARKET is the bonus 3rd order type


class ValidationError(Exception):
    """Raised when user-supplied order input fails validation."""
    pass


def validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.isalnum():
        raise ValidationError(f"Invalid symbol: '{symbol}'. Expected something like BTCUSDT.")
    return symbol.upper()


def validate_side(side: str) -> str:
    side = (side or "").upper()
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side: '{side}'. Must be one of {sorted(VALID_SIDES)}.")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = (order_type or "").upper()
    if order_type not in VALID_TYPES:
        raise ValidationError(f"Invalid order type: '{order_type}'. Must be one of {sorted(VALID_TYPES)}.")
    return order_type


def validate_quantity(quantity) -> float:
    try:
        quantity = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")
    if quantity <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got {quantity}.")
    return quantity


def validate_price(price, order_type: str):
    """Price is required for LIMIT orders only."""
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders.")
        try:
            price = float(price)
        except (TypeError, ValueError):
            raise ValidationError(f"Price must be a number, got '{price}'.")
        if price <= 0:
            raise ValidationError(f"Price must be greater than 0, got {price}.")
        return price
    return None


def validate_stop_price(stop_price, order_type: str):
    """Stop price is required for STOP_MARKET orders only."""
    if order_type == "STOP_MARKET":
        if stop_price is None:
            raise ValidationError("Stop price is required for STOP_MARKET orders.")
        try:
            stop_price = float(stop_price)
        except (TypeError, ValueError):
            raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")
        if stop_price <= 0:
            raise ValidationError(f"Stop price must be greater than 0, got {stop_price}.")
        return stop_price
    return None
