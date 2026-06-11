"""Interactive dry-run demo for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import json

import streamlit as st

from trading_bot.bot.exceptions import ValidationError
from trading_bot.bot.validators import validate_order_args


st.set_page_config(
    page_title="Binance Futures Testnet Bot Demo",
    page_icon="📈",
    layout="centered",
)

st.title("Binance Futures Testnet Trading Bot")
st.caption("Interactive dry-run demo. No real API request is sent from this UI.")

with st.sidebar:
    st.header("About")
    st.write(
        "This demo validates order inputs and shows the request payload that the CLI "
        "would send to Binance Futures Testnet."
    )
    st.warning("API keys are not required here. Do not enter real secrets into public demos.")

symbol = st.text_input("Symbol", value="BTCUSDT").upper()
side = st.selectbox("Side", ["BUY", "SELL"])
order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
quantity = st.text_input("Quantity", value="0.001")

price = None
if order_type == "LIMIT":
    price = st.text_input("Limit Price", value="120000")

submitted = st.button("Validate Order", type="primary", use_container_width=True)

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
        st.success("Order input is valid. Dry-run payload generated.")
        st.subheader("Order Request Summary")
        st.json(order)

        command = (
            f"py trading_bot/cli.py --symbol {order['symbol']} --side {order['side']} "
            f"--type {order['type']} --quantity {order['quantity']}"
        )
        if order["type"] == "LIMIT":
            command += f" --price {order['price']}"
        command += " --dry-run"

        st.subheader("Equivalent CLI Command")
        st.code(command, language="bash")

        st.subheader("Mock API Response Preview")
        st.json(
            {
                "orderId": "dry-run-demo",
                "status": "VALIDATED",
                "executedQty": "0",
                "avgPrice": "0",
                "request": json.loads(json.dumps(order)),
            }
        )

st.divider()
st.write(
    "For real Binance Futures Testnet orders, use the CLI with testnet API keys stored "
    "locally in a `.env` file."
)
