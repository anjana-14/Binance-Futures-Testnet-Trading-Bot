"""Binance USDT-M Futures Testnet API client."""

import hashlib
import hmac
import logging
import os
import time
from typing import Any
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

from bot.exceptions import BinanceAPIError, NetworkError

logger = logging.getLogger("trading_bot.client")

DEFAULT_BASE_URL = "https://testnet.binancefuture.com"
REQUEST_TIMEOUT = 15
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 1.0


class BinanceFuturesClient:
    """Thin wrapper around Binance Futures REST endpoints."""

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        base_url: str | None = None,
    ):
        load_dotenv()

        self.api_key = api_key or os.getenv("BINANCE_API_KEY", "").strip()
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET", "").strip()
        self.base_url = (base_url or os.getenv("BINANCE_FUTURES_TESTNET_URL") or DEFAULT_BASE_URL).rstrip("/")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file."
            )

    def _sign_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Add timestamp and HMAC signature required for signed endpoints."""
        signed = {**params, "timestamp": int(time.time() * 1000)}
        query_string = urlencode(signed)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signed["signature"] = signature
        return signed

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        signed: bool = False,
    ) -> dict[str, Any]:
        """
        Send an HTTP request to Binance Futures Testnet.

        Retries once on transient network failures.
        """
        url = f"{self.base_url}{path}"
        request_params = dict(params or {})

        if signed:
            request_params = self._sign_params(request_params)

        headers = {"X-MBX-APIKEY": self.api_key}
        last_error: Exception | None = None

        logger.info(
            "API request | method=%s path=%s params=%s signed=%s",
            method,
            path,
            {k: v for k, v in request_params.items() if k != "signature"},
            signed,
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=request_params if method.upper() == "GET" else None,
                    data=request_params if method.upper() != "GET" else None,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                )
            except requests.Timeout as exc:
                last_error = exc
                logger.warning("Request timed out (attempt %d/%d): %s", attempt, MAX_RETRIES, path)
            except requests.ConnectionError as exc:
                last_error = exc
                logger.warning("Connection error (attempt %d/%d): %s", attempt, MAX_RETRIES, exc)
            except requests.RequestException as exc:
                logger.error("Unexpected request failure: %s", exc)
                raise NetworkError(f"Request failed: {exc}") from exc
            else:
                return self._parse_response(response)

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

        raise NetworkError(
            f"Could not reach Binance after {MAX_RETRIES} attempts. "
            f"Check your internet connection and try again. Last error: {last_error}"
        )

    def _parse_response(self, response: requests.Response) -> dict[str, Any]:
        """Parse JSON response and raise on API-level errors."""
        try:
            payload = response.json()
        except ValueError as exc:
            logger.error("Non-JSON response | status=%s body=%s", response.status_code, response.text[:500])
            raise BinanceAPIError(
                f"Unexpected response from Binance (status {response.status_code})",
                status_code=response.status_code,
            ) from exc

        if response.status_code >= 400:
            error_msg = payload.get("msg", response.text)
            error_code = payload.get("code")
            logger.error(
                "API error | status=%s code=%s message=%s",
                response.status_code,
                error_code,
                error_msg,
            )
            raise BinanceAPIError(
                f"Binance API error: {error_msg}",
                status_code=response.status_code,
                error_code=error_code,
            )

        logger.info("API response | status=%s payload=%s", response.status_code, payload)
        return payload

    def ping(self) -> dict[str, Any]:
        """Check connectivity to the testnet server."""
        return self._request("GET", "/fapi/v1/ping")

    def place_order(self, order_params: dict[str, Any]) -> dict[str, Any]:
        """Submit a new order to the futures testnet."""
        return self._request("POST", "/fapi/v1/order", params=order_params, signed=True)
