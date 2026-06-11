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
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(14, 165, 233, 0.20), transparent 34rem),
            radial-gradient(circle at top right, rgba(34, 197, 94, 0.18), transparent 30rem),
            linear-gradient(135deg, #020617 0%, #0f172a 52%, #111827 100%);
        background-size: 120% 120%;
        animation: bgShift 12s ease-in-out infinite alternate;
        color: #e5e7eb;
    }
    @keyframes bgShift {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 55%; }
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background:
            linear-gradient(rgba(148, 163, 184, 0.045) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148, 163, 184, 0.045) 1px, transparent 1px);
        background-size: 42px 42px;
        mask-image: linear-gradient(to bottom, rgba(0,0,0,0.80), transparent 82%);
        animation: gridDrift 18s linear infinite;
    }
    @keyframes gridDrift {
        from { transform: translateY(0); }
        to { transform: translateY(42px); }
    }
    .main .block-container {
        padding-top: 2rem;
        max-width: 1180px;
    }
    .hero {
        position: relative;
        overflow: hidden;
        padding: 1.7rem 1.8rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.94) 0%, rgba(17, 24, 39, 0.92) 55%, rgba(6, 78, 59, 0.92) 100%);
        color: white;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(148, 163, 184, 0.22);
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
        animation: fadeUp 650ms ease-out both;
    }
    .hero::after {
        content: "";
        position: absolute;
        width: 18rem;
        height: 18rem;
        right: -7rem;
        top: -7rem;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.34), transparent 65%);
        animation: floatGlow 5s ease-in-out infinite alternate;
    }
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(14px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes floatGlow {
        from { transform: translate3d(0, 0, 0) scale(1); opacity: 0.72; }
        to { transform: translate3d(-34px, 24px, 0) scale(1.08); opacity: 1; }
    }
    .hero h1 {
        margin: 0;
        font-size: 2.1rem;
    }
    .hero p {
        margin: 0.35rem 0 0;
        color: #cbd5e1;
    }
    .ticker-strip {
        display: flex;
        gap: 0.75rem;
        overflow: hidden;
        margin: 0.75rem 0 1.35rem;
        padding: 0.35rem 0;
    }
    .ticker-track {
        display: flex;
        gap: 0.75rem;
        min-width: max-content;
        animation: tickerMove 18s linear infinite;
    }
    .ticker-chip {
        padding: 0.55rem 0.85rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(56, 189, 248, 0.22);
        color: #e0f2fe;
        white-space: nowrap;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
    }
    @keyframes tickerMove {
        from { transform: translateX(0); }
        to { transform: translateX(-50%); }
    }
    [data-testid="stSidebar"] {
        background: rgba(2, 6, 23, 0.94);
        border-right: 1px solid rgba(148, 163, 184, 0.16);
    }
    [data-testid="stSidebar"] * {
        color: #e5e7eb;
    }
    [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.74);
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.22);
        animation: fadeUp 760ms ease-out both;
    }
    h1, h2, h3, h4, label, .stMarkdown, .stCaptionContainer {
        color: #e5e7eb !important;
    }
    .stTextInput input,
    .stSelectbox [data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.95);
        color: #f8fafc;
        border-color: rgba(148, 163, 184, 0.35);
        border-radius: 10px;
    }
    .stTextInput input:focus {
        border-color: #38bdf8;
        box-shadow: 0 0 0 1px #38bdf8;
    }
    [data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        padding: 0.9rem 1rem;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.20);
        transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.55);
        box-shadow: 0 18px 38px rgba(14, 165, 233, 0.18);
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }
    .stButton button {
        border-radius: 12px;
        border: 0;
        background: linear-gradient(135deg, #0ea5e9, #22c55e, #0ea5e9);
        background-size: 220% 220%;
        color: white;
        font-weight: 700;
        min-height: 3rem;
        box-shadow: 0 14px 32px rgba(14, 165, 233, 0.24);
        animation: buttonFlow 4s ease infinite;
        transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
    }
    @keyframes buttonFlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .stButton button:hover {
        border: 0;
        filter: brightness(1.08);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 18px 42px rgba(34, 197, 94, 0.22);
    }
    div[data-testid="stAlert"] {
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.20);
    }
    hr {
        border-color: rgba(148, 163, 184, 0.18);
    }
    .live-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.45rem 0.7rem;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.28);
        color: #bbf7d0;
        font-size: 0.9rem;
        font-weight: 650;
        margin-bottom: 0.75rem;
    }
    .live-dot {
        width: 0.55rem;
        height: 0.55rem;
        border-radius: 999px;
        background: #22c55e;
        box-shadow: 0 0 0 rgba(34, 197, 94, 0.55);
        animation: pulseDot 1.6s infinite;
    }
    @keyframes pulseDot {
        0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.60); }
        70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
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

st.markdown(
    """
    <div class="ticker-strip">
      <div class="ticker-track">
        <span class="ticker-chip">BTCUSDT • Live Price Preview</span>
        <span class="ticker-chip">Dry Run Mode • No API Keys</span>
        <span class="ticker-chip">Market / Limit Orders</span>
        <span class="ticker-chip">Validation + Estimated Value</span>
        <span class="ticker-chip">Safe Public Demo</span>
        <span class="ticker-chip">BTCUSDT • Live Price Preview</span>
        <span class="ticker-chip">Dry Run Mode • No API Keys</span>
        <span class="ticker-chip">Market / Limit Orders</span>
        <span class="ticker-chip">Validation + Estimated Value</span>
        <span class="ticker-chip">Safe Public Demo</span>
      </div>
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
    st.markdown(
        '<div class="live-pill"><span class="live-dot"></span>Live public testnet price</div>',
        unsafe_allow_html=True,
    )
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
