# check_status.py
import os
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()

client = Client(
    os.getenv("BINANCE_TESTNET_API_KEY"),
    os.getenv("BINANCE_TESTNET_API_SECRET"),
    testnet=True,
)
client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"

print("=== Open Orders ===")
print(client.futures_get_open_orders(symbol="BTCUSDT"))

print("\n=== All Recent Orders (last 10) ===")
orders = client.futures_get_all_orders(symbol="BTCUSDT", limit=10)
for o in orders:
    print(o)

print("\n=== Positions ===")
positions = client.futures_position_information(symbol="BTCUSDT")
for p in positions:
    print(p)

print("\n=== Account Balance ===")
print(client.futures_account_balance())