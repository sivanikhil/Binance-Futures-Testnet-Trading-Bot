"""Small Binance USDT-M Futures testnet REST client."""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from typing import Any
from urllib.parse import urlencode

try:
    import requests
except ImportError:  # pragma: no cover - handled when live API calls are attempted
    requests = None  # type: ignore[assignment]

from .exceptions import BinanceAPIError

TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceFuturesClient:
    """Signed REST client for Binance Futures Testnet."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = TESTNET_BASE_URL,
        timeout: int = 10,
        logger: logging.Logger | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("API key is required")
        if not api_secret:
            raise ValueError("API secret is required")

        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        if requests is None:
            raise BinanceAPIError("Missing dependency: install requests with `pip install -r requirements.txt`")

        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": api_key})
        self.logger = logger or logging.getLogger("trading_bot")

    def _sign(self, params: dict[str, Any]) -> str:
        query = urlencode(params, doseq=True)
        return hmac.new(self.api_secret, query.encode("utf-8"), hashlib.sha256).hexdigest()

    def _request(self, method: str, path: str, params: dict[str, Any], signed: bool = True) -> dict[str, Any]:
        request_params = dict(params)
        if signed:
            request_params["timestamp"] = int(time.time() * 1000)
            request_params["recvWindow"] = 5000
            request_params["signature"] = self._sign(request_params)

        url = f"{self.base_url}{path}"
        log_params = {key: value for key, value in request_params.items() if key != "signature"}
        self.logger.info("API request | method=%s path=%s params=%s", method, path, log_params)

        try:
            response = self.session.request(method, url, params=request_params, timeout=self.timeout)
        except requests.RequestException as exc:
            self.logger.exception("Network failure | method=%s path=%s error=%s", method, path, exc)
            raise BinanceAPIError(f"Network failure while calling Binance: {exc}") from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}

        self.logger.info(
            "API response | method=%s path=%s status_code=%s payload=%s",
            method,
            path,
            response.status_code,
            payload,
        )

        if response.status_code >= 400:
            message = payload.get("msg") if isinstance(payload, dict) else response.text
            code = payload.get("code") if isinstance(payload, dict) else response.status_code
            raise BinanceAPIError(f"Binance API error {code}: {message}")

        if not isinstance(payload, dict):
            raise BinanceAPIError("Unexpected Binance API response format")

        return payload

    def place_order(self, order: dict[str, str]) -> dict[str, Any]:
        """Place a MARKET or LIMIT order on Binance Futures testnet."""
        return self._request("POST", "/fapi/v1/order", order, signed=True)
