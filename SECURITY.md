# Security Policy

## Overview

This document outlines the security architecture and practices for the KuCoin Triangular Arbitrage Engine.

## Key Security Principles

### 1. No Authenticated Trading

- **Zero trading keys required**: This application uses only KuCoin's public API endpoints
- **No secret storage**: No API keys, secrets, or authentication tokens are stored or transmitted
- **Read-only access**: All market-data endpoints are unauthenticated public feeds
- **Code audit result**: Zero code paths for order submission, cancellation, or modification

### 2. Paper Trading Only

- All conversions are simulated against virtual USDT balances
- No real capital is ever at risk
- Simulated results are stored in local SQLite database
- Cannot affect real exchange accounts

### 3. Input Validation

- All market data from KuCoin is validated against schema
- Order books are checked for:
  - Completeness (both bid and ask levels present)
  - Freshness (timestamp within configured tolerance)
  - Sequence continuity (gap detection on WebSocket)
  - Logical validity (ask > bid, positive quantities)
- Configuration values are type-checked and range-validated

### 4. Database Security

- SQLite database file should be readable only by the application process
- Set appropriate file permissions:
  ```bash
  chmod 600 data/kucoin_bot.sqlite
  ```
- No passwords or secrets stored in database
- All monetary values stored as text strings (Decimal precision)

### 5. Network Security

- WebSocket connections use KuCoin's standard public endpoints
- No proxy or VPN bypass required
- TLS/SSL encryption for all connections
- No sensitive data transmitted

### 6. Dashboard Access Control

- Admin endpoints protected by HTTP Basic Authentication
- Default credentials must be changed in production:
  ```bash
  DASHBOARD_USERNAME=secure-admin-username
  DASHBOARD_PASSWORD=very-secure-password-change-me
  ```
- Run behind HTTPS reverse proxy in production (e.g., nginx, caddy)
- Implement rate limiting on authentication endpoints

## Best Practices for Deployment

### Local Development

1. Use default `.env.example` settings
2. Dashboard accessible only on localhost:8000
3. Database file in local directory with restricted permissions

### Docker Deployment

1. Do not expose port 8000 to the internet without HTTPS
2. Use environment variables for all sensitive configuration
3. Mount database volume with appropriate permissions
4. Run container with minimal privileges (non-root user)

### Production Deployment

1. **HTTPS**: Always use HTTPS for dashboard access
   ```nginx
   server {
       listen 443 ssl http2;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       location / {
           proxy_pass http://localhost:8000;
       }
   }
   ```

2. **Authentication**: Change default credentials immediately
   ```bash
   export DASHBOARD_PASSWORD="$(openssl rand -base64 32)"
   ```

3. **Rate Limiting**: Implement on authentication endpoints
   ```nginx
   limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
   location /status {
       limit_req zone=auth burst=5 nodelay;
       proxy_pass http://localhost:8000;
   }
   ```

4. **Firewall**: Restrict dashboard access to trusted networks

5. **Monitoring**: Log all authentication attempts and errors

6. **Backups**: Regularly backup SQLite database
   ```bash
   cp data/kucoin_bot.sqlite backups/kucoin_bot_$(date +%Y%m%d_%H%M%S).sqlite
   ```

## Incident Response

### Dashboard Compromise

If authentication credentials are exposed:

1. Stop the application: `docker-compose down`
2. Change credentials in `.env`
3. Review SQLite audit trail in `simulation_decisions` and `errors` tables
4. Restart application: `docker-compose up -d`

### Data Corruption

If SQLite database becomes corrupted:

1. Stop the application
2. Restore from most recent backup
3. Application will continue with restored ledger state
4. Simulated cycles are deduped on restart, so no profit double-counting

### Network Issues

If WebSocket connection is compromised:

1. Application automatically detects stale data
2. Cycle evaluation is paused for affected symbols
3. Reconnection with exponential backoff is attempted
4. No trades are executed during data outage

## Security Testing

### Automated Checks

Verify no order-execution code:

```bash
# Should return zero results
grep -r "place.*order\|submit.*trade\|execute.*trade" src/ tests/
grep -r "cancel.*order\|modify.*order" src/ tests/
grep -r "auth.*token\|api.*key" src/ tests/
```

Verify Decimal arithmetic (no float rounding errors):

```bash
pytest tests/unit/test_profit_calculator.py -v
```

### Manual Verification

1. **Code Review**: Inspect all files in `src/` for trading logic
2. **Database Schema**: Verify no fields for order IDs or trading state
3. **Configuration**: Confirm no KuCoin API keys in default `.env.example`
4. **Network Trace**: Monitor WebSocket connections – only subscription/update payloads, no order payloads

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not open a public GitHub issue**
2. **Email security details** to: dev@example.com
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested remediation

4. **Timeline**: Security team will respond within 48 hours

## Compliance

- This application is a **market scanner and paper-trading tool only**
- **No real trading capability** – cannot violate exchange terms of service
- **No personal data collection** – no user accounts or PII stored
- **Public market data only** – adheres to KuCoin's fair-use policy
- **No financial advice** – purely analytical and educational

## Third-Party Dependencies

Keep all dependencies up to date:

```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```

Notable dependencies:
- **aiohttp**: Secure HTTP/WebSocket client with TLS support
- **fastapi**: Secure web framework with input validation
- **pydantic**: Type validation and schema enforcement
- **sqlalchemy-style**: Type-safe database access patterns

## Conclusion

This application is designed with security and safety as first-class concerns. The restriction to paper trading and use of only public APIs eliminates the most common attack vectors. Deploy with confidence, but maintain standard operational security practices.

---

**Security Review**: This implementation has been designed to eliminate financial risk through architecture. No trading capability exists. All market data is read-only and public.

**Questions?** Contact: dev@example.com