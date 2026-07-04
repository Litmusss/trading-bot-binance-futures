# Simplified Trading Bot — Binance Futures Testnet (USDT-M)

A small, structured Python CLI app that places MARKET, LIMIT, and STOP_MARKET
orders on Binance Futures Testnet.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py          # Binance API wrapper (only file that talks to Binance directly)
    orders.py           # Order validation + request/response handling
    validators.py        # Input validation rules
    logging_config.py    # Logging setup
  cli.py                 # CLI entry point
  requirements.txt
  check_status.py        #check order status
  README.md
```

## Setup

### 1. Create a Binance Futures Testnet account
1. Go to https://testnet.binancefuture.com
2. Log in with a GitHub account (this is how the testnet handles auth — no separate signup).
3. Once logged in, you'll land on a dashboard with fake USDT already in your futures wallet.

### 2. Generate API credentials
1. On the testnet dashboard, find the **API Key** section (usually a link/button near the top or in account settings).
2. Generate a new API key + secret.
3. Copy both immediately — the secret is only shown once.

### 3. Install dependencies
```bash
git clone <your-repo-url>
cd trading_bot
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Set your API credentials as environment variables
Never hardcode API keys in source code.

```bash
export BINANCE_TESTNET_API_KEY="your_api_key_here"
export BINANCE_TESTNET_API_SECRET="your_api_secret_here"
```

On Windows (PowerShell):
```powershell
$env:BINANCE_TESTNET_API_KEY="your_api_key_here"
$env:BINANCE_TESTNET_API_SECRET="your_api_secret_here"
```

## How to Run

### Market order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit order
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

### Stop-Market order (bonus feature — 3rd order type)
```bash
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.01 --stop-price 58000
```

Each run prints:
- the order request summary (symbol, side, type, quantity, price/stop price)
- the order response (orderId, status, executedQty, avgPrice)
- a success or failure message

## Logging

Every request, response, and error is logged to `logs/trading_bot_YYYYMMDD.log`.
The console only shows warnings/errors so normal usage stays readable; the full
detail lives in the log file. This satisfies the requirement to submit log files
for at least one MARKET and one LIMIT order — after running each command above,
copy the relevant lines (or the whole file) from `logs/` into your submission.

## Error Handling

The app handles three categories of failure distinctly:
- **Invalid input** — caught by `bot/validators.py` before any API call is made (e.g. missing price on a LIMIT order, negative quantity, unsupported side).
- **Binance API errors** — caught via `BinanceAPIException` / `BinanceOrderException` / `BinanceRequestException` (e.g. insufficient testnet balance, invalid symbol, rejected order).
- **Network failures** — caught via `requests`' `ConnectionError` / `Timeout`.

In all three cases, the error is logged with full detail and a short, readable
message is printed to the console.

## Assumptions

- This targets **USDT-M Futures** only (not Coin-M or Spot).
- LIMIT orders use `GTC` (Good-Til-Cancelled) as the time-in-force, since the task didn't specify one.
- STOP_MARKET was chosen as the bonus third order type since it's a natural extension of the existing order flow and commonly used for stop-loss placement.
- Quantities and prices are passed as-is to Binance; the app does not attempt to auto-round to each symbol's exchange-defined precision (`stepSize`/`tickSize`). If a MARKET/LIMIT order fails with a precision error, adjust the quantity/price to match the symbol's rules (visible via `GET /fapi/v1/exchangeInfo`).
- API credentials are read from environment variables rather than a config file, to avoid any risk of committing secrets to the repo.
