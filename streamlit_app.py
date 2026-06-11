"""Interactive dry-run demo for the Binance Futures Testnet trading bot."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

import requests
import streamlit as st

from trading_bot.bot.exceptions import ValidationError
from trading_bot.bot.validators import validate_order_args

BINANCE_PRICE_URL = "https://testnet.binancefuture.com/fapi/v1/ticker/price"


st.set_page_config(
    page_title="Binance Futures Testnet Bot Demo",
    page_icon="BT",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 1180px;
    }
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 14px;
        background: linear-gradient(135deg, #0f172a 0%, #111827 55%, #064e3b 100%);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.1rem;
    }
    .hero p {
        margin: 0.35rem 0 0;
        color: #cbd5e1;
    }
    .status-card {
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def parse_decimal(value: str) -> Decimal | None:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return parsed if parsed > 0 else None


@st.cache_data(ttl=15)
def fetch_latest_price(symbol: str) -> tuple[Decimal | None, str | None]:
    try:
        response = requests.get(BINANCE_PRICE_URL, params={"symbol": symbol}, timeout=8)
        response.raise_for_status()
        payload = response.json()
        return Decimal(payload["price"]), None
    except Exception as exc:
        return None, str(exc)


st.markdown(
    """
    <div class="hero">
      <h1>Binance Futures Testnet Trading Dashboard</h1>
      <p>Live public price lookup + safe dry-run order validation. No API keys. No real orders.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("About")
    st.write(
        "This public demo uses Binance Futures Testnet public market data and validates "
        "the same order inputs used by the CLI bot."
    )
    st.info("Public demo mode: no API keys required.")
    st.warning("For real testnet orders, run the CLI locally with your private `.env` file.")

form_col, market_col = st.columns([1.05, 1], gap="large")

with form_col:
    st.subheader("Order Ticket")
    symbol = st.text_input("Symbol", value="BTCUSDT", help="Example: BTCUSDT, ETHUSDT").upper()
    order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
    side = st.selectbox("Side", ["BUY", "SELL"])
    quantity = st.text_input("Quantity", value="0.001")

    price = None
    if order_type == "LIMIT":
        price = st.text_input("Limit Price", value="120000")

    submitted = st.button("Validate Dry-Run Order", type="primary", use_container_width=True)

with market_col:
    st.subheader("Market Snapshot")
    latest_price, price_error = fetch_latest_price(symbol)
    qty_decimal = parse_decimal(quantity)

    if latest_price is not None:
        st.metric("Latest Testnet Price", f"{latest_price:,.2f} USDT")
    else:
        st.metric("Latest Testnet Price", "Unavailable")
        st.caption(f"Price lookup failed: {price_error}")

    if latest_price is not None and qty_decimal is not None:
        estimated_value = latest_price * qty_decimal
        st.metric("Estimated Notional", f"{estimated_value:,.2f} USDT")
    else:
        st.metric("Estimated Notional", "-")

    st.markdown("#### Demo Mode")
    st.info("Validation only. This dashboard does not submit orders.")

if submitted:
    try:
        order = validate_order_args(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )
    except ValidationError as exc:
        st.error(f"Validation failed: {exc}")
    else:
        st.success("Order input is valid.")

        st.subheader("Validated Order Preview")
        preview_cols = st.columns(5)
        preview_cols[0].metric("Symbol", order["symbol"])
        preview_cols[1].metric("Side", order["side"])
        preview_cols[2].metric("Type", order["type"])
        preview_cols[3].metric("Quantity", order["quantity"])

        preview_price = order.get("price")
        if preview_price:
            preview_cols[4].metric("Limit Price", f"{Decimal(preview_price):,.2f}")
        elif latest_price is not None:
            preview_cols[4].metric("Reference Price", f"{latest_price:,.2f}")
        else:
            preview_cols[4].metric("Reference Price", "-")

        order_qty = Decimal(order["quantity"])
        reference_price = Decimal(order["price"]) if order.get("price") else latest_price
        if reference_price is not None:
            st.metric("Estimated Order Value", f"{(reference_price * order_qty):,.2f} USDT")

        if order["side"] == "BUY":
            st.caption("BUY preview: this represents opening or increasing long exposure in testnet mode.")
        else:
            st.caption("SELL preview: this represents opening or increasing short exposure in testnet mode.")

        st.info("Status: validated in dry-run demo mode. No private API request was sent.")

st.divider()
st.caption(
    "Public data source: Binance Futures Testnet ticker endpoint. Real order placement is intentionally limited to the local CLI."
)
