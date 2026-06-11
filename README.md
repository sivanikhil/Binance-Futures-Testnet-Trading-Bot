# Binance Futures Testnet Trading Bot

Small Python CLI application for placing `MARKET` and `LIMIT` orders on Binance USDT-M Futures Testnet.

## Features

- Places `BUY` and `SELL` orders on `https://testnet.binancefuture.com`
- Supports `MARKET` and `LIMIT` order types
- Validates CLI input before sending requests
- Separates CLI, client/API, order, validation, and logging layers
- Logs request summaries, API responses, and errors to a file
- Includes `--dry-run` mode for safe validation without sending an order

## Setup

1. Create and activate a Python 3 virtual environment.

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Create Binance Futures Testnet credentials at the Binance Futures Testnet site.

4. Copy `.env.example` to `.env` and fill in your credentials.

   ```bash
   copy .env.example .env
   ```

   Required variables:

   ```text
   BINANCE_API_KEY=your_testnet_key
   BINANCE_API_SECRET=your_testnet_secret
   ```

## Run Examples

Validate a market order without sending it:

```bash
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

Place a market order:

```bash
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Validate a limit order without sending it:

```bash
python trading_bot/cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000 --dry-run
```

Place a limit order:

```bash
python trading_bot/cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 120000
```

Use a custom log path:

```bash
python trading_bot/cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --log-file logs/market_order.log
```

## Optional Interactive Demo

This project also includes a lightweight Streamlit dry-run UI. It validates order input and shows the request payload without sending real API requests or requiring API keys.

Run it locally:

```bash
streamlit run streamlit_app.py
```

For a public demo, deploy this repository on Streamlit Community Cloud and select:

```text
streamlit_app.py
```

Do not enter real API keys into a public demo. Use the CLI for real Binance Futures Testnet orders.

## Output

The CLI prints:

- Order request summary
- Order response details: `orderId`, `status`, `executedQty`, `avgPrice` if available
- Success or failure message

## Logging

By default, logs are written to:

```text
logs/trading_bot.log
```

Each run records:

- Validated order request summary
- Signed API request metadata, excluding the signature
- Binance API response payload
- Validation, network, and API errors

Sample dry-run logs are included in `logs/sample_market_order.log` and `logs/sample_limit_order.log`. Replace them with real testnet logs after running the two live examples above with your own credentials.

## Assumptions

- This project targets Binance USDT-M Futures Testnet only.
- API credentials are loaded from environment variables or `.env`.
- `LIMIT` orders use `timeInForce=GTC`.
- The app validates basic shape and positivity of values locally. Binance remains the source of truth for symbol filters, precision, leverage, balances, and margin requirements.
