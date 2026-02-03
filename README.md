# IP Intelligence - AML Risk Engine

A FastAPI-based IP intelligence service for Anti-Money Laundering (AML) risk assessment. Detects VPN, Proxy, Tor, and geographic anomalies to identify potential fraud or evasion attempts.

## Features

- **Real-time IP Analysis**: Check IP addresses against multiple data sources
- **Hybrid Database**: MongoDB for caching + External API (vpnapi.io) for fresh data
- **Risk Scoring Engine**: Rule-based risk assessment with configurable thresholds
- **Geographic Validation**: Detects country mismatches and geo-masking
- **Auto-Learning**: Caches API results for faster subsequent queries
- **Production Ready**: Async architecture, structured logging, health checks

## Quick Start

```bash
# 1. Navigate to module
cd IP_Intelligence

# 2. Install dependencies
pip install -r requirements.txt

# 3. Update geo data (optional)
python geo_data_fetch.py

# 4. Configure environment
# Edit .env with your settings

# 5. Start MongoDB (required)

# 6. Run the application
python main.py
```

Access Swagger UI: `http://localhost:8000/api/v1/docs`

---

## API Endpoint

### POST `/api/v1/screen`

Screen a transaction for AML risk based on IP and user location.

**Request Body:**
```json
{
  "transaction_id": "txn_123",
  "user_id": "user_456",
  "user_country": "US",
  "ip_address": "1.2.3.4"
}
```

**Response:**
```json
{
  "status": "success",
  "screening_id": "SCR-ABC123XYZ",
  "risk_score": 85,
  "risk_level": "high",
  "should_block": false,
  "confidence": 0.99,
  "user_country": "US",
  "detected_country": "DE",
  "countries_match": false,
  "security": {
    "is_vpn": true,
    "is_proxy": false,
    "is_tor": false,
    "is_relay": false
  },
  "triggered_rules": [
    {
      "rule_name": "Geo-Masking VPN",
      "severity": "high",
      "description": "VPN detected matching user country",
      "score_contribution": 85
    }
  ],
  "recommendation": "Flag for Manual Review",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## Risk Levels

| Level | Score | Action |
|-------|-------|--------|
| `LOW` | 0 | Safe - Location Matches |
| `MEDIUM` | 1-59 | Monitor |
| `HIGH` | 60-89 | Flag for Manual Review |
| `CRITICAL` | 90-100 | BLOCK |

---

## Detection Rules

| Rule | Condition | Score |
|------|-----------|-------|
| **Tor Network** | Tor exit node detected | 100 |
| **Sanctioned Jurisdiction** | IP/User in high-risk country | 95 |
| **Geo-Masking VPN** | VPN in same country as user | 85 |
| **Commercial VPN** | VPN in different country | 75 |
| **Location Mismatch** | User country != IP country | 60 |

**High-Risk Countries:** MM, KP, IR, SY, YE, DZ, AO, BO, BG, CM, CI, HT, KE, LB, LA, MC, NA, NP, SS, VE, VN, RU

---

## Project Structure

```
IP_Intelligence/
├── main.py                    # FastAPI entry point
├── geo_data_fetch.py          # Fetch country borders from REST Countries API
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create from example)
├── .gitignore
└── app/
    ├── __init__.py
    ├── config.py              # Pydantic settings
    ├── database.py            # MongoDB connection
    ├── models.py              # Pydantic request/response models
    ├── schemas.py             # MongoDB document schemas
    ├── geodata.json           # Country borders/regions (auto-generated)
    ├── routes/
    │   ├── __init__.py
    │   └── screening.py       # /screen endpoint
    └── services/
        ├── __init__.py
        ├── external_api.py    # vpnapi.io client
        ├── geo_data.py        # Borders/regions lookup
        └── ip_intelligence.py # Core risk engine
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | AML Risk Engine V4 |
| `VERSION` | Version string | 4.0.0 |
| `DEBUG` | Debug mode | True |
| `MONGODB_URL` | MongoDB connection string | mongodb://localhost:27017 |
| `DB_NAME` | Database name | vpn_detector |
| `GEOIP_API_URL` | vpnapi.io base URL | https://vpnapi.io/api |
| `VPNAPI_KEY` | vpnapi.io API key | - |
| `GEOIP_TIMEOUT` | API timeout (seconds) | 5 |
| `API_PREFIX` | API prefix | /api/v1 |
| `HOST` | Bind host | 0.0.0.0 |
| `PORT` | Bind port | 8000 |

---

## How It Works

```
1. User calls POST /api/v1/screen with IP address
                    │
                    ▼
2. Check MongoDB (Waterfall: tor_ips → vpn_ips → clean_ips)
                    │
         ┌─────────┴─────────┐
         │                   │
    Found in DB         Not Found
         │                   │
         ▼                   ▼
3. Extract security    4. Call vpnapi.io API
   flags from source
         │                   │
         │                   ▼
         │            5. Parse response
         │            (is_vpn, is_proxy, is_tor)
         │                   │
         │                   ▼
         │            6. Save to MongoDB (learn)
         │                   │
         └─────────┬─────────┘
                   ▼
7. Apply Risk Rules (Tor → Sanctions → VPN → Geo Mismatch)
                   │
                   ▼
8. Return Screening Result with risk_score, level, and recommendation
```

---

## Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "operational",
  "version": "4.0.0",
  "mode": "debug"
}
```

---

## Dependencies

- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **motor** - Async MongoDB driver
- **httpx** - HTTP client
- **pydantic** - Data validation
- **pydantic-settings** - Environment configuration

---

## License

Internal use only.
