# KuCoin Triangular Arbitrage Engine

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A production-quality Python market scanner and paper-trading system for detecting and simulating triangular arbitrage opportunities on KuCoin Spot markets.

## 🎯 Purpose

This application is designed to:

- **Discover eligible markets dynamically** from KuCoin's current Spot trading catalogue
- **Build a directed conversion graph** of all available trading pairs
- **Enumerate triangular arbitrage cycles** (A → B → C → A) automatically
- **Stream real-time order-book data** via KuCoin's public WebSocket feeds
- **Simulate fee-aware conversions** using exact Decimal arithmetic across multi-level depth
- **Persist simulated performance** to SQLite with full ledger reconciliation
- **Provide operational dashboards** with FastAPI and admin authentication
- **Maintain operational resilience** through graceful reconnection and recovery
- **Never submit live orders** – this is a scanner and paper-trading tool only

## ✅ Safety & Compliance

- **Zero authenticated trading paths**: No live order submission, cancellation, or modification
- **Paper-only execution**: All simulations use virtual capital from a persistent ledger
- **Deterministic tests**: Comprehensive unit and integration test suite with network mocks
- **Risk controls**: Configurable limits on returns, slippage, market-data age, and concurrent simulations
- **Emergency pause**: Can disable all cycle processing on command
- **Audit trail**: Every decision, rejection, and fee calculation is logged to SQLite

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Git
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ahat1993-wq/kucoin-triangular-arbitrage.git
   cd kucoin-triangular-arbitrage
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Run the application**
   ```bash
   python -m kucoin_triangular_bot.main
   ```

### Docker Deployment

```bash
docker-compose up -d
```

Access the dashboard at `http://localhost:8000`

## 📊 Core Components

### Market Discovery (`market_catalog.py`)
- Fetches all eligible KuCoin Spot markets via public REST API
- Validates trading state, quote asset, and product type
- Filters unsupported futures, margin, and leveraged products
- Refreshes periodically for symbol additions and suspensions

### Conversion Graph (`conversion_graph.py`)
- Represents assets as nodes and trading pairs as directed edges
- Maintains symbol metadata and price references per edge
- Supports efficient neighbor lookups and connectivity queries

### Cycle Discovery (`cycle_discovery.py`)
- Enumerates exactly-3-node cycles using depth-first search
- Deduplicates cycles to avoid redundant processing
- Ranks cycles by estimated net return
- Supports configurable starting assets (default: USDT)

### Order Book Management (`orderbook_manager.py`)
- Maintains per-symbol order-book snapshots
- Validates freshness and sequence continuity
- Detects stale, missing, or corrupted data
- Triggers resynchronization on gaps

### Profit Calculation (`profit_calculator.py`)
- Simulates multi-level order-book execution using Decimal arithmetic
- Applies configurable fee model exactly once per leg
- Enforces minimum order quantities and precision constraints
- Calculates gross profit, fees, slippage, and net return percentage
- Never assumes top-of-book liquidity for entire trade quantity

### Paper Execution Engine (`paper_execution.py`)
- Maintains virtual portfolio balances in SQLite
- Records simulated conversions with full audit trail
- Implements deduplication to prevent replay on restart
- Tracks rejected opportunities with reasons
- Calculates daily performance summaries

### Risk Controls (`risk_controls.py`)
- Validates cycles against minimum return, slippage, and data-age thresholds
- Enforces maximum concurrent simulations and capital allocation
- Supports emergency pause for all cycle processing
- Provides rejection reasons for every filtered opportunity

### Dashboard (`dashboard.py`)
- FastAPI-based lightweight web interface
- Real-time scanner status and opportunity metrics
- Virtual balance tracking and daily summaries
- Admin authentication (configurable)
- CSV export endpoints

## 📁 Project Structure

```
kucoin-triangular-arbitrage/
├── src/kucoin_triangular_bot/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration and environment
│   ├── database.py             # SQLite persistence layer
│   ├── kucoin_public_client.py # KuCoin REST/WS client
│   ├── market_catalog.py       # Market discovery and filtering
│   ├── conversion_graph.py     # Graph data structure
│   ├── cycle_discovery.py      # Cycle enumeration
│   ├── orderbook_manager.py    # Order book caching
│   ├── profit_calculator.py    # Fee-aware conversion engine
│   ├── paper_execution.py      # Virtual ledger and simulation
│   ├── risk_controls.py        # Safety constraints
│   └── dashboard.py            # FastAPI dashboard
├── tests/
│   ├── unit/
│   │   ├── test_conversion_graph.py
│   │   ├── test_cycle_discovery.py
│   │   ├── test_profit_calculator.py
│   │   ├── test_paper_execution.py
│   │   ├── test_risk_controls.py
│   │   ├── test_orderbook_manager.py
│   │   └── test_config.py
│   └── integration/
│       └── test_public_market_access.py
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── README.md
├── SECURITY.md
└── LICENSE
```

## 🔧 Configuration

Key settings in `.env`:

```env
# Market filtering
BASE_ASSET=USDT
SUPPORTED_QUOTE_ASSETS=USDT,BTC,ETH,KCS,SOL,BNB

# Risk thresholds
MIN_ESTIMATED_NET_RETURN=0.0005      # 0.05% minimum profit
MAX_SLIPPAGE=0.01                    # 1% maximum slippage
MAX_CYCLE_CAPITAL=100                # Virtual capital per cycle
MAX_MARKET_DATA_AGE_SECONDS=10       # Reject stale data

# Paper trading
STARTING_CAPITAL=100                 # Initial virtual USDT

# Dashboard
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your-secure-password
```

## 📈 How It Works

### Initialization Phase
1. Fetch all eligible KuCoin Spot markets
2. Build directed conversion graph
3. Discover and rank triangular cycles
4. Initialize virtual ledger with starting capital
5. Subscribe to WebSocket order-book feeds

### Continuous Operation
1. Monitor incoming order-book updates
2. Validate data freshness and continuity
3. Evaluate affected cycles for arbitrage
4. Apply risk filters and safety constraints
5. Simulate eligible cycles with current depth
6. Persist results and update balances
7. Publish metrics to dashboard

### Cycle Evaluation
1. Fetch current order books for all three pairs
2. Check data age and sequence validity
3. Simulate conversions with multi-level depth
4. Calculate net profit after fees and slippage
5. Compare against minimum return threshold
6. Record decision (accept/reject) with full reasoning

## 🧪 Testing

### Run All Tests
```bash
pytest -v
```

### Run Unit Tests Only
```bash
pytest tests/unit/ -v
```

### Run with Coverage
```bash
pytest --cov=src/kucoin_triangular_bot tests/ -v
```

### Test Categories
- **Unit tests**: Graph construction, cycle enumeration, profit calculations, ledger operations
- **Integration tests**: Public KuCoin API access (requires network)
- **Safety tests**: Verify no live-order code paths exist

## 📊 Dashboard & Monitoring

Access the dashboard:
```
http://localhost:8000
```

**Health check endpoint** (no auth required):
```bash
curl http://localhost:8000/health
```

**Status endpoint** (requires admin auth):
```bash
curl -u admin:password http://localhost:8000/status
```

**Export daily performance**:
```bash
curl -u admin:password http://localhost:8000/reports/daily > performance.csv
```

## 🛡️ Security Considerations

1. **No Authenticated Trading**: The application uses only KuCoin's **public API**. No trading keys or secrets are required or stored.
2. **Dashboard Authentication**: Basic HTTP auth protects admin endpoints. Use HTTPS in production.
3. **Database Isolation**: SQLite file-based database; ensure file permissions are restrictive.
4. **Input Validation**: All market data is validated against schema and freshness rules.
5. **Rate Limiting**: Respects KuCoin's public API rate limits; implements backoff and retry logic.

See [SECURITY.md](SECURITY.md) for detailed security guidance.

## 📝 Logging

Logs are written to stdout and can be captured to files:

```bash
python -m kucoin_triangular_bot.main > logs/bot.log 2>&1
```

Set `LOG_LEVEL` in `.env` to control verbosity:
- `DEBUG`: Verbose trace of all operations
- `INFO`: Standard operation messages
- `WARNING`: Issues that may need attention
- `ERROR`: Failures and exceptions

## 📦 Database Schema

The SQLite database includes:

- `market_snapshots`: Symbol metadata and trading state
- `cycles`: Discovered triangular cycles and their edges
- `opportunity_observations`: Real-time market opportunities
- `simulation_decisions`: Accept/reject decisions with reasons
- `simulated_conversions`: Completed virtual trades with profit/loss
- `ledger_balances`: Current virtual portfolio by asset
- `errors`: Operational failures and recovery events
- `daily_performance`: Daily summaries of simulated activity

## 🐛 Troubleshooting

### Market data not updating
- Check WebSocket connection status in logs
- Verify `KUCOIN_PUSH_BASE` endpoint is current
- Ensure firewall allows outbound WebSocket connections

### Low cycle discovery rate
- Expand `SUPPORTED_QUOTE_ASSETS` to include more trading pairs
- Lower `MIN_ESTIMATED_NET_RETURN` threshold (with caution)
- Check that multiple symbols have adequate liquidity

### Dashboard auth failures
- Verify `DASHBOARD_USERNAME` and `DASHBOARD_PASSWORD` in `.env`
- Ensure proper HTTP Basic auth credentials in requests

### Stale data warnings
- Increase `MAX_MARKET_DATA_AGE_SECONDS` if network latency is high
- Check for WebSocket disconnections in logs
- Verify stable internet connectivity

## 📚 Additional Resources

- [KuCoin API Documentation](https://www.kucoin.com/docs-new)
- [Spot Market Data Endpoints](https://www.kucoin.com/docs-new/3470221w0)
- [WebSocket Streams Documentation](https://www.kucoin.com/docs-new/websocket)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License – see [LICENSE](LICENSE) for details.

## ⚠️ Disclaimer

This application is provided for educational and research purposes. It is a paper-trading simulator and does not execute real orders. 

**Use at your own risk.** While the system includes safety controls, market conditions can change rapidly. Always validate calculations independently and consult financial professionals before making trading decisions.

---

**Status**: Production-ready for paper trading and market analysis. Safe for continuous operation.

**Last Updated**: October 2024