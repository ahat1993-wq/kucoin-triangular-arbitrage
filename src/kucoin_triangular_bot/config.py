"""Configuration management for KuCoin triangular arbitrage engine.

Handles environment variables, default values, and configuration validation.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


@dataclass
class Config:
    """Application configuration.

    All values are read from environment variables with sensible defaults.
    Monetary values are stored as Decimal for precision.
    """

    # Application identity
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "kucoin_triangular_bot"))
    env: str = field(default_factory=lambda: os.getenv("APP_ENV", "dev"))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # KuCoin API endpoints (public only)
    kucoin_rest_base: str = field(
        default_factory=lambda: os.getenv("KUCOIN_REST_BASE", "https://api.kucoin.com")
    )
    kucoin_ws_base: str = field(
        default_factory=lambda: os.getenv("KUCOIN_WS_BASE", "wss://ws-api-spot.kucoin.com")
    )
    kucoin_push_base: str = field(
        default_factory=lambda: os.getenv("KUCOIN_PUSH_BASE", "wss://x-push-spot.kucoin.com")
    )

    # Market filtering
    base_asset: str = field(default_factory=lambda: os.getenv("BASE_ASSET", "USDT"))
    supported_quote_assets: set[str] = field(
        default_factory=lambda: set(
            a.upper().strip() for a in os.getenv("SUPPORTED_QUOTE_ASSETS", "USDT,BTC,ETH,KCS,SOL,BNB").split(",")
        )
    )
    min_quote_volume: Decimal = field(
        default_factory=lambda: Decimal(os.getenv("MIN_QUOTE_VOLUME", "0"))
    )
    min_liquidity_usd: Decimal = field(
        default_factory=lambda: Decimal(os.getenv("MIN_LIQUIDITY_USD", "0"))
    )
    required_market_states: set[str] = field(default_factory=lambda: {"normal", "live"})
    max_cycles: int = field(default_factory=lambda: int(os.getenv("MAX_CYCLES", "200")))

    # Data quality and risk controls
    max_market_data_age_seconds: int = field(
        default_factory=lambda: int(os.getenv("MAX_MARKET_DATA_AGE_SECONDS", "10"))
    )
    max_consecutive_data_failures: int = field(
        default_factory=lambda: int(os.getenv("MAX_CONSECUTIVE_FAILURES", "5"))
    )
    max_simultaneous_simulations: int = field(
        default_factory=lambda: int(os.getenv("MAX_SIMULATIONS", "4"))
    )
    min_estimated_net_return: Decimal = field(
        default_factory=lambda: Decimal(os.getenv("MIN_ESTIMATED_NET_RETURN", "0.0005"))
    )
    max_slippage: Decimal = field(
        default_factory=lambda: Decimal(os.getenv("MAX_SLIPPAGE", "0.01"))
    )
    max_cycle_capital: Decimal = field(
        default_factory=lambda: Decimal(os.getenv("MAX_CYCLE_CAPITAL", "100"))
    )
    emergency_pause: bool = field(
        default_factory=lambda: os.getenv("EMERGENCY_PAUSE", "false").lower() in ("true", "1", "yes")
    )

    # Virtual ledger (paper trading)
    starting_capital: Decimal = field(
        default_factory=lambda: Decimal(os.getenv("STARTING_CAPITAL", "100"))
    )
    paper_currency: str = field(default_factory=lambda: os.getenv("PAPER_CURRENCY", "USDT"))

    # Database
    db_path: str = field(default_factory=lambda: os.getenv("DB_PATH", "data/kucoin_bot.sqlite"))
    csv_export_dir: str = field(
        default_factory=lambda: os.getenv("CSV_EXPORT_DIR", "data/reports")
    )

    # Network configuration
    request_timeout: float = field(
        default_factory=lambda: float(os.getenv("REQUEST_TIMEOUT", "10.0"))
    )
    ws_heartbeat_interval: float = field(
        default_factory=lambda: float(os.getenv("WS_HEARTBEAT_INTERVAL", "20.0"))
    )
    ws_reconnect_delay: float = field(
        default_factory=lambda: float(os.getenv("WS_RECONNECT_DELAY", "3.0"))
    )

    # Dashboard security
    dashboard_username: str = field(
        default_factory=lambda: os.getenv("DASHBOARD_USERNAME", "admin")
    )
    dashboard_password: str = field(
        default_factory=lambda: os.getenv("DASHBOARD_PASSWORD", "change-me")
    )
    dashboard_auth_enabled: bool = field(
        default_factory=lambda: os.getenv("DASHBOARD_AUTH_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    dashboard_host: str = field(
        default_factory=lambda: os.getenv("DASHBOARD_HOST", "127.0.0.1")
    )
    dashboard_port: int = field(
        default_factory=lambda: int(os.getenv("DASHBOARD_PORT", "8000"))
    )

    def __post_init__(self) -> None:
        """Validate and normalize configuration after initialization."""
        # Create data directories
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.csv_export_dir).mkdir(parents=True, exist_ok=True)

        # Normalize assets to uppercase
        self.base_asset = self.base_asset.upper()
        self.supported_quote_assets = {a.upper() for a in self.supported_quote_assets}
        self.paper_currency = self.paper_currency.upper()

        # Validate Decimal values
        self.min_quote_volume = Decimal(str(self.min_quote_volume))
        self.min_liquidity_usd = Decimal(str(self.min_liquidity_usd))
        self.starting_capital = Decimal(str(self.starting_capital))
        self.max_cycle_capital = Decimal(str(self.max_cycle_capital))
        self.min_estimated_net_return = Decimal(str(self.min_estimated_net_return))
        self.max_slippage = Decimal(str(self.max_slippage))

        # Validate ranges
        if self.starting_capital <= 0:
            raise ValueError("starting_capital must be positive")
        if self.max_cycle_capital <= 0:
            raise ValueError("max_cycle_capital must be positive")
        if self.request_timeout <= 0:
            raise ValueError("request_timeout must be positive")
        if self.max_market_data_age_seconds <= 0:
            raise ValueError("max_market_data_age_seconds must be positive")

        # Log configuration
        logger.info(
            "Configuration loaded: env=%s, base=%s, quotes=%s, min_return=%.4f%%",
            self.env,
            self.base_asset,
            ",".join(sorted(self.supported_quote_assets)),
            float(self.min_estimated_net_return) * 100,
        )
