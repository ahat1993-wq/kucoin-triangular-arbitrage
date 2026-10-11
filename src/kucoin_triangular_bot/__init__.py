"""KuCoin Triangular Arbitrage Scanner and Paper Trading Engine.

A production-quality market scanner and paper-trading system for detecting
triangular arbitrage opportunities on KuCoin Spot markets.

Key features:
- Dynamic market discovery and cycle enumeration
- Real-time order-book streaming via WebSocket
- Fee-aware conversion simulation with Decimal arithmetic
- Persistent virtual ledger with SQLite
- FastAPI dashboard with admin authentication
- Comprehensive safety controls and risk limits

Safety guarantee: Zero authenticated trading paths. Paper trading only.
"""

__version__ = "0.1.0"
__author__ = "Arbitrage Team"
__license__ = "MIT"

from .config import Config
from .database import AppDatabase
from .kucoin_public_client import KucoinPublicClient, OrderBookSnapshot, OrderBookLevel
from .market_catalog import MarketCatalog
from .conversion_graph import ConversionGraph
from .cycle_discovery import CycleDiscovery
from .orderbook_manager import OrderBookManager, OrderBookState
from .profit_calculator import ProfitCalculator, quantize_decimal
from .risk_controls import RiskControls
from .paper_execution import PaperExecutionEngine
from .dashboard import create_dashboard_app

__all__ = [
    "Config",
    "AppDatabase",
    "KucoinPublicClient",
    "OrderBookSnapshot",
    "OrderBookLevel",
    "MarketCatalog",
    "ConversionGraph",
    "CycleDiscovery",
    "OrderBookManager",
    "OrderBookState",
    "ProfitCalculator",
    "quantize_decimal",
    "RiskControls",
    "PaperExecutionEngine",
    "create_dashboard_app",
]