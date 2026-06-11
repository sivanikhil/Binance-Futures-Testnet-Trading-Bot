"""Application-specific exceptions."""


class TradingBotError(Exception):
    """Base exception for expected trading bot failures."""


class ValidationError(TradingBotError):
    """Raised when CLI input is invalid."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an API error response."""

