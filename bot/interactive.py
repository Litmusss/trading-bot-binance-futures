"""
Interactive CLI mode — prompts the user step by step instead of requiring
all flags up front. Triggered when cli.py is run with no arguments.

Uses the same OrderRequest/execute_order pipeline as the flag-driven mode,
so both paths get identical validation and logging.
"""

from bot.validators import ValidationError

SIDES = ["BUY", "SELL"]
ORDER_TYPES = ["MARKET", "LIMIT", "STOP_MARKET"]


def _prompt_choice(label: str, options: list) -> str:
    """Show a numbered menu, re-ask until the user picks a valid number."""
    while True:
        print(f"\n{label}")
        for i, opt in enumerate(options, start=1):
            print(f"  {i}. {opt}")
        choice = input("Choose a number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(f"Invalid choice '{choice}'. Enter a number between 1 and {len(options)}.")


def _prompt_text(label: str) -> str:
    """Ask for free-text input, re-prompt if left blank."""
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("This field can't be empty.")


def run_interactive_flow():
    """
    Walks the user through building an order interactively.
    Returns a dict matching OrderRequest's constructor args, or None if cancelled.
    Real validation still happens in OrderRequest — this just collects input.
    """
    print("=" * 50)
    print(" Binance Futures Testnet — Interactive Order Builder")
    print("=" * 50)

    symbol = _prompt_text("Symbol (e.g. BTCUSDT)").upper()
    side = _prompt_choice("Select order side:", SIDES)
    order_type = _prompt_choice("Select order type:", ORDER_TYPES)
    quantity = _prompt_text("Quantity (e.g. 0.01)")

    price = None
    stop_price = None

    if order_type == "LIMIT":
        price = _prompt_text("Limit price")
    elif order_type == "STOP_MARKET":
        stop_price = _prompt_text("Stop trigger price")

    print("\nReview your order:")
    print(f"  Symbol:   {symbol}")
    print(f"  Side:     {side}")
    print(f"  Type:     {order_type}")
    print(f"  Quantity: {quantity}")
    if price:
        print(f"  Price:      {price}")
    if stop_price:
        print(f"  Stop Price: {stop_price}")

    confirm = input("\nConfirm and place this order? (y/n): ").strip().lower()
    if confirm != "y":
        print("Cancelled — no order was placed.")
        return None

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price,
    }