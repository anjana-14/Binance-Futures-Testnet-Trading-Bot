"""Custom exceptions for the trading bot."""


class TradingBotError(Exception):
    """Base exception for all bot-related errors."""


class ValidationError(TradingBotError):
    """Raised when user input fails validation."""


class BinanceAPIError(TradingBotError):
    """Raised when Binance returns an error response."""

    def __init__(self, message: str, status_code: int | None = None, error_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class NetworkError(TradingBotError):
    """Raised when a request fails due to connectivity issues."""
