# Binance Futures Testnet Trading Bot

A small CLI tool for placing MARKET and LIMIT orders on Binance USDT-M Futures Testnet. I built this as a focused take-home style project: enough structure to be reusable, but not over-engineered.

## What it does

- Places **MARKET** and **LIMIT** orders (BUY / SELL)
- Validates CLI input before hitting the API
- Logs requests, responses, and errors to a dated log file
- Reads API credentials from a `.env` file

## Prerequisites

- Python 3.10+ (uses modern type hints)
- A [Binance Futures Testnet](https://testnet.binancefuture.com/) account with API key + secret

## Setup

1. Clone or download this repo and move into the project folder:

```bash
cd trading_bot
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the example env file and add your testnet credentials:

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `.env`:

```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
BINANCE_FUTURES_TESTNET_URL=https://testnet.binancefuture.com
```

Generate keys from the testnet UI: log in → profile → **API Key**.

## Usage

Run from the `trading_bot` directory:

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 95000
```

### Expected output (successful MARKET order)

```
--- Order Request ---
  Symbol:    BTCUSDT
  Side:      BUY
  Type:      MARKET
  Quantity:  0.001

--- Order Response ---
  Order ID: 123456789
  Status: FILLED
  Executed Qty: 0.001
  Avg Price: 94250.50

Order placed successfully.
```

### Expected output (successful LIMIT order)

```
--- Order Request ---
  Symbol:    BTCUSDT
  Side:      SELL
  Type:      LIMIT
  Quantity:  0.001
  Price:     95000

--- Order Response ---
  Order ID: 123456790
  Status: NEW
  Original Qty: 0.001
  Price: 95000

Order placed successfully.
```

Exact IDs and prices depend on testnet state. LIMIT orders often return `NEW` until filled.

### Validation errors

Bad input is caught before any API call:

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001
```

```
Input error: Price is required for LIMIT orders. Example: --price 65000
```

## Project layout

```
trading_bot/
├── bot/
│   ├── client.py          # REST client + HMAC signing
│   ├── orders.py          # Order building and formatting
│   ├── validators.py      # Input validation
│   ├── logging_config.py  # File + console logging
│   └── exceptions.py      # Custom error types
├── cli.py                 # Entry point
├── logs/                  # Daily log files (created on run)
├── requirements.txt
└── .env.example
```

## Design decisions

**Direct REST instead of python-binance** — The futures testnet only needs a couple of endpoints. Using `requests` keeps dependencies light and makes it obvious how signing works. For a larger bot I'd probably reach for an SDK.

**Separate validators module** — Validation is isolated so the CLI stays thin and the same checks could be reused if I added a simple menu later.

**Custom exceptions** — `ValidationError`, `BinanceAPIError`, and `NetworkError` let the CLI print user-friendly messages while still logging the full detail.

**Retry on network failures** — One retry with a short delay handles flaky Wi-Fi without hiding persistent outages.

**LIMIT orders use GTC** — Good enough for testnet demos. Production code might expose `timeInForce` as a CLI flag.

## Logging

Logs go to `logs/trading_bot_YYYYMMDD.log` with timestamps. Each run records:

- Outgoing request parameters (signature excluded from logs)
- API responses
- Errors with status codes where available

Sample logs from test runs are in `logs/samples/`:

- `market_order_sample.log` — MARKET BUY on BTCUSDT
- `limit_order_sample.log` — LIMIT SELL on BTCUSDT

## Assumptions

- USDT-M perpetual futures only (symbols like `BTCUSDT`, not coin-margined pairs)
- One-shot CLI usage, not a long-running bot loop
- Testnet credentials only — never commit a real `.env`
- Quantity/price precision is passed through as entered; Binance will reject invalid step sizes
- No position mode or margin type configuration — testnet defaults are assumed

## Limitations

- Only MARKET and LIMIT order types (no stop-limit, OCO, etc.)
- No order cancellation or status polling
- No exchange info lookup for min quantity / tick size validation
- Network retry is basic (2 attempts, fixed delay)
- Logs may contain order details — treat log files like sensitive data in shared environments

## Troubleshooting

| Problem | Likely cause |
|---------|----------------|
| `Missing API credentials` | `.env` missing or keys not set |
| `-2019 Margin is insufficient` | Not enough testnet USDT — use the testnet faucet |
| `-1111 Precision is over the maximum` | Quantity or price has too many decimals |
| `Could not reach Binance` | Network issue or testnet downtime |

## License

For evaluation / portfolio use. Not financial advice.
