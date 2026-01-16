# Technical Architecture Report - QuantMetrics.io
**Voor:** Data Engineers & Software Architects  
**Datum:** December 2024  
**Versie:** 4.0 (Strategy Builder V4)

> **⚠️ IMPORTANT NOTE:** Dit document beschrijft technische mogelijkheden en architecturale opties. **Implementatie prioriteiten volgen het [Build Contract](docs/BUILD_CONTRACT.md)**. Items zoals async queues, microservices, en enterprise auth staan op de No-Go lijst en worden alleen geïmplementeerd bij bewezen pijn. Focus in MVP fase op Time-to-value, Reliability, en Verkoopbaarheid (PDF polish).

---

## Executive Summary

**Architectuur Type:** Modular Monolith Architecture (Flask-based)  
**Storage Pattern:** Strategy Pattern met Pluggable Storage Backends  
**Data Flow:** Synchronous Request-Response (MVP)  
**Current Scale:** MVP (1-50 concurrent users)  
**Target Scale:** Production (50-200 users) → Scale-up later bij bewezen schaal

**⚠️ Build Contract Note:** Microservices, async queues, en enterprise scale staan op de No-Go lijst. Focus eerst op product-market fit met monolith + worker processes.

**Key Architectural Decisions:**
1. **Modular Strategy System** - Auto-discovery module registry voor 66+ trading modules
2. **Pluggable Storage Layer** - Abstract interface met LocalStorage (Parquet) en CloudStorage (S3+PostgreSQL) implementations
3. **Decision Block Model** - Declarative strategy definition → imperative execution conversion
4. **Caching Strategy** - Multi-layer (in-memory, Parquet files, future: Redis)
5. **Schema-Based Configuration** - Dynamic UI rendering gebaseerd op module config schemas

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   V4     │  │   V5     │  │ Templates│  │   CSV    │       │
│  │ Simulator│  │ ICT Sim  │  │ Selector │  │ Upload   │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                         │ HTTP/JSON
        ┌────────────────▼────────────────┐
        │      Flask Application Layer     │
        │  ┌──────────────────────────┐   │
        │  │   Route Handlers         │   │
        │  │  /run-backtest-v4        │   │
        │  │  /run-backtest-v5        │   │
        │  │  /api/modules            │   │
        │  └──────────┬───────────────┘   │
        └─────────────┼───────────────────┘
                      │
        ┌─────────────▼───────────────────┐
        │     Business Logic Layer        │
        │  ┌──────────┐  ┌─────────────┐ │
        │  │ Decision │  │  Backtest   │ │
        │  │  Blocks  │─▶│   Engine    │ │
        │  │ Converter│  └──────┬──────┘ │
        │  └──────────┘         │        │
        └───────────────────────┼────────┘
                                │
        ┌───────────────────────▼─────────┐
        │      Module System Layer        │
        │  ┌──────────────────────────┐  │
        │  │   Module Registry        │  │
        │  │  (Auto-discovery, 66+)   │  │
        │  └──────┬───────────────────┘  │
        │         │                       │
        │  ┌──────▼───────────────────┐  │
        │  │  Strategy Modules        │  │
        │  │  - indicator/            │  │
        │  │  - ict/                  │  │
        │  │  - trend/                │  │
        │  │  - momentum/             │  │
        │  └──────┬───────────────────┘  │
        └─────────┼───────────────────────┘
                  │
        ┌─────────▼───────────────────────┐
        │      Data Access Layer          │
        │  ┌──────────────────────────┐  │
        │  │    DataManager           │  │
        │  │  (Unified Interface)     │  │
        │  └──────┬───────────────────┘  │
        │         │                       │
        │  ┌──────▼───────────────────┐  │
        │  │  Storage Interface       │  │
        │  │  (Abstract Base Class)   │  │
        │  └──────┬───────────┬───────┘  │
        └─────────┼───────────┼──────────┘
                  │           │
        ┌─────────▼──┐  ┌─────▼───────────┐
        │  Local     │  │   Cloud         │
        │  Storage   │  │   Storage       │
        │ (Parquet)  │  │ (S3+PostgreSQL) │
        └────────────┘  └─────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **Flask App** | HTTP routing, request handling | Flask 2.x |
| **Decision Block Converter** | Strategy definition → execution conditions | Python |
| **BacktestEngine** | Trade simulation loop, indicator calculation | Pandas, NumPy |
| **Module Registry** | Auto-discovery, module lifecycle management | Python importlib |
| **DataManager** | Unified data access, caching orchestration | Pandas |
| **Storage Interface** | Abstract storage backend contract | ABC Pattern |
| **LocalStorage** | Parquet file-based storage (MVP) | Parquet, Pathlib |
| **CloudStorage** | S3 + PostgreSQL storage (Production) | Boto3, Psycopg2 |

---

## 2. Data Flow Architecture

### 2.1 Backtest Execution Flow

```
User Request (JSON)
    │
    ├─▶ Decision Blocks (Declarative)
    │
    ▼
[convert_decision_blocks_to_conditions()]
    │
    ├─▶ Module ID Resolution
    │   ├─▶ Explicit moduleId (preferred)
    │   └─▶ Label-based mapping (fallback)
    │
    ├─▶ Module Instantiation (via Registry)
    │
    └─▶ Condition Objects (Imperative)
            │
            ▼
    [BacktestEngine.run_modular()]
            │
            ├─▶ DataManager.get_data()
            │   ├─▶ Check LocalStorage cache
            │   ├─▶ If missing: DataDownloader.download()
            │   └─▶ Save to cache (Parquet)
            │
            ├─▶ Data Cleaning & Standardization
            │   ├─▶ Remove duplicates
            │   ├─▶ Fix DatetimeIndex
            │   └─▶ Sort by timestamp
            │
            ├─▶ Module Calculation Loop
            │   ├─▶ For each module in conditions:
            │   │   ├─▶ module.calculate(data, config)
            │   │   └─▶ Add column to DataFrame
            │   └─▶ All columns now available
            │
            ├─▶ Trade Simulation Loop
            │   ├─▶ For each candle:
            │   │   ├─▶ Evaluate all conditions (AND logic)
            │   │   ├─▶ If true: Open trade
            │   │   ├─▶ Track entry price, SL, TP
            │   │   ├─▶ If exit conditions met: Close trade
            │   │   └─▶ Generate QuantMetricsTrade object
            │   └─▶ Return List[QuantMetricsTrade]
            │
            ▼
    [BasicAnalyzer.calculate()]
            │
            ├─▶ Calculate metrics (WR, PF, ESI, PVS, etc.)
            │
            └─▶ Generate AnalysisResult
                    │
                    ▼
    [PlaywrightReportGenerator.generate_report()]
            │
            └─▶ PDF Report (via Playwright)
                    │
                    ▼
    HTTP Response (HTML Results Page + PDF Download)
```

### 2.2 Data Storage Flow

```
External Data Source (Yahoo Finance)
    │
    ▼
[DataDownloader.download()]
    │
    ├─▶ Convert to Pandas DataFrame
    │   ├─▶ OHLCV columns
    │   ├─▶ DatetimeIndex
    │   └─▶ Standardize format
    │
    ▼
[DataManager.get_data()]
    │
    ├─▶ Check Storage Backend
    │   ├─▶ LocalStorage.get_data()?
    │   │   ├─▶ Read metadata.json
    │   │   ├─▶ Check cache freshness (TTL)
    │   │   ├─▶ If fresh: Read Parquet file
    │   │   └─▶ Return DataFrame
    │   │
    │   └─▶ If missing/stale:
    │       ├─▶ DataDownloader.download()
    │       ├─▶ LocalStorage.save_data()
    │       │   ├─▶ Write Parquet file
    │       │   ├─▶ Update metadata.json
    │       │   └─▶ Track size, timestamp
    │       └─▶ Return DataFrame
    │
    ▼
[BacktestEngine] uses data
    │
    └─▶ No direct writes (read-only during backtest)
```

**Caching Strategy:**
- **L1 Cache:** In-memory DataFrame (per-request, short-lived)
- **L2 Cache:** Parquet files on disk (persistent, TTL-based refresh)
- **L3 Cache (Future):** Redis for backtest results (planned)

---

## 3. Module System Architecture

### 3.1 Module Registry Pattern

```python
# Auto-discovery via file system scanning
ModuleRegistry
    ├─▶ discover_modules()
    │   ├─▶ Scan core/strategy_modules/{category}/
    │   ├─▶ Import each .py file
    │   ├─▶ Find BaseModule subclasses
    │   └─▶ Register by module_id (filename)
    │
    ├─▶ get_module(module_id) → Type[BaseModule]
    ├─▶ get_modules_by_category(category) → List[Type[BaseModule]]
    └─▶ list_available_modules() → Dict[str, List[str]]

# Module Interface Contract
BaseModule (ABC)
    ├─▶ calculate(data: DataFrame, config: Dict) → DataFrame
    │   └─▶ Adds column(s) to DataFrame
    │
    ├─▶ get_config_schema() → Dict
    │   └─▶ Fields: type, default, min, max, step, options
    │
    └─▶ validate_config(config: Dict) → bool
```

### 3.2 Module Categories & Distribution

| Category | Module Count | Examples |
|----------|-------------|----------|
| **indicator** | 5 | rsi, sma, macd, bollinger, stochastic |
| **ict** | 11 | market_structure_shift, premium_discount_zones, liquidity_sweep, fair_value_gaps, displacement, order_blocks, kill_zones, breaker_blocks, mitigation_blocks, imbalance_zones, inducement |
| **trend** | 8 | adx, aroon, ichimoku, parabolic_sar, supertrend, pivot_points |
| **momentum** | 8 | momentum_indicator, cci, mfi, roc, williams_r, ultimate_oscillator, tsi |
| **moving_averages** | 8 | sma, ema, wma, dema, tema, hull_ma, zlema |
| **volatility** | 6 | atr, keltner_channels, donchian_channels, bollinger_width |
| **volume** | 6 | vwap, volume_profile, obv, cmf, ad_line |
| **support_resistance** | 4 | pivot_points, fibonacci, camarilla, sr_zones |
| **custom** | 12 | choppiness, kaufman_adaptive_ma, vortex_indicator |
| **mtf** | 0 | (Future: multi-timeframe support) |
| **position_sizing** | 0 | (Future: position sizing algorithms) |

**Total:** 66+ modules (auto-discovered, extensible)

### 3.3 Module Lifecycle

```
1. Application Startup
    │
    ├─▶ get_registry() called (singleton pattern)
    │
    ├─▶ ModuleRegistry.__init__()
    │   └─▶ Initialize empty _modules dict
    │
    ├─▶ discover_modules()
    │   ├─▶ Scan directory tree
    │   ├─▶ Import each module file
    │   ├─▶ Extract BaseModule subclasses
    │   └─▶ Register by module_id
    │
    └─▶ Modules ready (no instantiation yet)

2. Request Processing
    │
    ├─▶ Decision Blocks → Conditions conversion
    │
    ├─▶ For each condition:
    │   ├─▶ registry.get_module(module_id)
    │   │   └─▶ Returns Type[BaseModule] (class, not instance)
    │   │
    │   ├─▶ module_class()  # Instantiate (no config in __init__)
    │   │   └─▶ Creates module_instance
    │   │
    │   └─▶ Store: {module, module_id, config, operator, value}
    │
    └─▶ Pass to BacktestEngine

3. Backtest Execution
    │
    ├─▶ For each module in conditions:
    │   ├─▶ module_instance.calculate(data, config)
    │   │   ├─▶ Reads existing columns from data
    │   │   ├─▶ Calculates indicator values
    │   │   └─▶ Adds new column(s) to data
    │   │
    │   └─▶ Data now contains all indicator columns
    │
    └─▶ Trade simulation uses indicator columns
```

**Design Benefits:**
- **Lazy Instantiation:** Modules only created when needed
- **Stateless Modules:** No shared state, safe for concurrent requests
- **Config Injection:** Config passed per-request, not at init time
- **Extensibility:** Add new modules by creating file in category directory

---

## 4. Storage Architecture

### 4.1 Storage Interface Pattern

```python
# Abstract Contract
class DataStorage(ABC):
    @abstractmethod
    def get_data(symbol, timeframe, start, end) -> DataFrame
    
    @abstractmethod
    def save_data(symbol, timeframe, data: DataFrame) -> None
    
    @abstractmethod
    def has_cached_data(symbol, timeframe, start, end) -> bool

# Implementations
LocalStorage(DataStorage)
    ├─▶ Uses Parquet files on filesystem
    ├─▶ Metadata stored in JSON
    └─▶ Thread-safe via RLock

CloudStorage(DataStorage)  # Future
    ├─▶ Uses S3 for Parquet files
    ├─▶ PostgreSQL for metadata
    └─▶ Redis for hot cache
```

### 4.2 Data Storage Schema

**File Structure (LocalStorage):**
```
data/market_cache/
    ├── metadata.json
    │   └── {
    │       "XAUUSD": {
    │           "15m": {
    │               "file_path": "XAUUSD/15m.parquet",
    │               "size_bytes": 1024000,
    │               "last_updated": "2024-12-29T10:00:00Z",
    │               "row_count": 10000,
    │               "date_range": {
    │                   "start": "2024-01-01T00:00:00Z",
    │                   "end": "2024-12-29T23:59:59Z"
    │               }
    │           }
    │       }
    │   }
    │
    └── XAUUSD/
        ├── 1m.parquet
        ├── 5m.parquet
        ├── 15m.parquet
        ├── 1h.parquet
        └── 4h.parquet
```

**Parquet Schema:**
```python
DataFrame columns:
    - timestamp: datetime64[ns] (index)
    - open: float64
    - high: float64
    - low: float64
    - close: float64
    - volume: float64
```

**Metadata Schema:**
- **Purpose:** Avoid reading Parquet files for cache checks
- **Size:** ~10-50 KB per symbol/timeframe
- **Update:** On every save_data() call

### 4.3 Caching Strategy

**Multi-Layer Cache Architecture:**

| Layer | Type | Location | TTL | Purpose |
|-------|------|----------|-----|---------|
| **L1** | In-memory | DataFrame (per-request) | Request duration | Avoid duplicate reads |
| **L2** | File-based | Parquet files | 24 hours (configurable) | Persistent cache |
| **L3** | Application | Backtest results cache | 1 hour (planned) | Reuse identical backtests |
| **L4** | Distributed | Redis (future) | 3600s | Multi-server cache |

**Cache Invalidation:**
- **Time-based:** TTL (24 hours default)
- **Size-based:** Cleanup old files if cache > MAX_CACHE_SIZE_GB
- **Manual:** `DataManager.clear_old_cache(days=30)`

**Cache Key Generation:**
```python
# For market data
cache_key = f"{symbol}_{timeframe}_{start}_{end}"

# For backtest results (current: in-memory dict)
cache_key = hashlib.md5(
    json.dumps({
        'symbol': symbol,
        'timeframe': timeframe,
        'direction': direction,
        'period': period,
        'modules': [c.get('module_id') for c in conditions],
        'configs': [c.get('config') for c in conditions]
    }, sort_keys=True).encode()
).hexdigest()
```

---

## 5. API Design

### 5.1 REST API Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/run-backtest-v4` | POST | Execute Decision Block strategy | JSON: Decision Blocks | HTML: Results page |
| `/run-backtest-v5` | POST | Execute ICT strategy | JSON: ICT config | HTML: Results page |
| `/api/modules` | GET | List all available modules | None | JSON: Module list by category |
| `/api/modules/<id>/schema` | GET | Get module config schema | None | JSON: Schema definition |
| `/api/modules/<id>` | GET | Get module details | None | JSON: Full module info |

### 5.2 Request/Response Patterns

**Decision Block Model (V4):**
```json
// Request
{
  "marketContext": {
    "market": "XAUUSD",
    "timeframe": "15m",
    "direction": "Long",
    "testPeriod": "2mo",
    "session": "London"
  },
  "decisionBlocks": [
    {
      "label": "Market Structure",
      "subConfirmations": [
        {
          "label": "Market Structure Shift",
          "moduleId": "market_structure_shift",
          "selected": true,
          "config": {
            "operator": "==",
            "value": "bullish",
            "period": 14
          }
        }
      ]
    }
  ],
  "exit": {
    "takeProfit": 2.0,
    "stopLoss": 1.0
  },
  "quickTest": false
}

// Response
HTML page with:
  - Metrics (WR, PF, ESI, PVS, etc.)
  - Trade list
  - Charts (equity curve, drawdown)
  - PDF download link
```

**Module Schema Response:**
```json
{
  "module_id": "rsi",
  "name": "RSI",
  "category": "indicator",
  "schema": {
    "fields": [
      {
        "name": "period",
        "type": "number",
        "default": 14,
        "min": 2,
        "max": 200,
        "step": 1,
        "title": "RSI Period"
      },
      {
        "name": "overbought",
        "type": "number",
        "default": 70,
        "min": 50,
        "max": 95,
        "step": 1,
        "title": "Overbought Level"
      }
    ]
  }
}
```

### 5.3 Error Handling Strategy

**Error Response Format:**
```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "MODULE_NOT_FOUND",
  "details": {
    "module_id": "invalid_module",
    "available_modules": [...]
  }
}
```

**Error Categories:**
- **400 Bad Request:** Invalid input (missing fields, invalid values)
- **404 Not Found:** Module not found, data not available
- **500 Internal Server Error:** Backend exceptions (with detailed logging)

---

## 6. Performance Characteristics

### 6.1 Backtest Execution Performance

**Current Performance (Single-threaded):**

| Operation | Time | Notes |
|-----------|------|-------|
| **Data Download** | 2-5s | First-time download (Yahoo Finance) |
| **Data Load (cached)** | 0.1-0.5s | Read from Parquet |
| **Module Calculation** | 0.5-2s per module | Depends on data size |
| **Trade Simulation** | 0.5-3s | Depends on number of conditions |
| **Analysis** | 0.1-0.3s | Calculate metrics |
| **PDF Generation** | 2-7s | Playwright rendering |

**Total Backtest Time:**
- **Cached data:** 3-10 seconds (typical)
- **Uncached data:** 5-15 seconds
- **Complex strategies (4+ modules):** 8-20 seconds

### 6.2 Bottlenecks & Optimization Opportunities

**Identified Bottlenecks:**

1. **Data Download (Yahoo Finance)**
   - **Issue:** Rate limiting, network latency
   - **Solution:** Aggressive caching, pre-loading popular symbols
   - **Impact:** 50-80% reduction in wait time

2. **PDF Generation (Playwright)**
   - **Issue:** Synchronous rendering, slow
   - **Solution:** Async generation, template caching
   - **Impact:** 30-50% reduction in response time

3. **Module Calculation (Sequential)**
   - **Issue:** Modules calculated one-by-one
   - **Solution:** Parallel module calculation (multiprocessing)
   - **Impact:** 40-60% reduction for multi-module strategies

4. **In-Memory DataFrame Operations**
   - **Issue:** Large DataFrames (100K+ rows) slow operations
   - **Solution:** Chunked processing, NumPy vectorization
   - **Impact:** 20-30% improvement

### 6.3 Scalability Analysis

**Current Limits (MVP):**
- **Concurrent Users:** ~10-20 (single Flask process)
- **Data Storage:** ~50GB (local filesystem)
- **Backtest Throughput:** ~6-10 backtests/minute

**Production Scaling (Estimated):**
- **Horizontal Scaling:** Add Flask workers (Gunicorn/uWSGI)
  - 4 workers = ~40-80 concurrent users
  - 8 workers = ~80-160 concurrent users
- **Data Storage:** Migrate to S3 (unlimited)
- **Backtest Throughput:** Async queue (Celery/Redis)
  - ~50-100 backtests/minute (queue-based)

**Scaling Strategy:**
1. **Phase 1 (50-100 users):** Add worker processes, optimize caching
2. **Phase 2 (100-500 users):** Migrate to CloudStorage, add Redis cache
3. **Phase 3 (500+ users):** Async backtest queue, load balancing, CDN

---

## 7. Technical Debt & Known Issues

### 7.1 Architecture Debt

| Issue | Impact | Priority | Estimated Effort |
|-------|--------|----------|------------------|
| **Synchronous Backtest Execution** | User waits 3-10s | High | 3-5 days |
| **In-Memory Backtest Cache** | Lost on restart, single-server only | Medium | 2-3 days |
| **No Module Dependency Graph** | Can't detect circular dependencies | Low | 1-2 days |
| **Monkey-Patching in Legacy Code** | Hard to debug, error-prone | Low | 2-3 days (cleanup) |

### 7.2 Data Engineering Debt

| Issue | Impact | Priority | Estimated Effort |
|-------|--------|----------|------------------|
| **Yahoo Finance Rate Limiting** | Downloads fail under load | High | 1-2 days (throttling) |
| **No Data Validation** | Invalid data can cause crashes | Medium | 2-3 days |
| **Parquet Metadata Not Versioned** | Cache invalidation issues | Low | 1 day |
| **No Data Quality Monitoring** | Can't detect data issues early | Low | 2-3 days |

### 7.3 Code Quality Debt

| Issue | Impact | Priority | Estimated Effort |
|-------|--------|----------|------------------|
| **Inconsistent Error Handling** | Some errors not caught | Medium | 2-3 days |
| **Missing Type Hints** | Harder to refactor | Low | 1-2 weeks (gradual) |
| **No API Versioning** | Breaking changes affect clients | Medium | 1-2 days |
| **Limited Logging** | Hard to debug production issues | Medium | 2-3 days |

---

## 8. Deployment Architecture

### 8.1 Current Deployment (MVP)

```
Single VPS/Server
    ├─▶ Python 3.11+
    ├─▶ Flask (development server)
    ├─▶ LocalStorage (Parquet files)
    └─▶ Port 5000 (HTTP)

No load balancing, no redundancy
```

### 8.2 Recommended Production Architecture

```
┌─────────────────────────────────────────┐
│        Load Balancer (Nginx)            │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Flask  │ │Flask  │ │Flask  │
│Worker │ │Worker │ │Worker │
│  (4)  │ │  (4)  │ │  (4)  │
└───┬───┘ └───┬───┘ └───┬───┘
    │          │          │
    └──────────┼──────────┘
               │
    ┌──────────▼──────────┐
    │   Redis Cache       │
    │  (Backtest Results) │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   Celery Queue      │
    │  (Async Backtests)  │
    └──────────┬──────────┘
               │
    ┌──────────▼──────────┐
    │   Data Layer        │
    │  ┌──────┬────────┐  │
    │  │  S3  │  PG    │  │
    │  │(Parq)│(Meta)  │  │
    │  └──────┴────────┘  │
    └─────────────────────┘
```

**Components:**
- **Nginx:** Reverse proxy, SSL termination, static file serving
- **Gunicorn/uWSGI:** WSGI server, multiple workers
- **Redis:** Cache layer, Celery broker
- **Celery:** Async task queue for long-running backtests
- **S3:** Object storage for Parquet files
- **PostgreSQL:** Metadata, user data, strategy configurations

### 8.3 Environment Configuration

**Development:**
```env
STORAGE_TYPE=local
DATA_PATH=data/market_cache
DEBUG=true
FLASK_ENV=development
```

**Production:**
```env
STORAGE_TYPE=cloud
S3_BUCKET=quantmetrics-data
PG_HOST=prod-db.example.com
REDIS_URL=redis://prod-redis:6379/0
DEBUG=false
FLASK_ENV=production
```

---

## 9. Security Considerations

### 9.1 Current Security Posture

| Aspect | Status | Notes |
|--------|--------|-------|
| **Authentication** | ❌ Not implemented | No user auth (MVP) |
| **Authorization** | ❌ Not implemented | No role-based access |
| **Input Validation** | ⚠️ Partial | Some validation, not comprehensive |
| **SQL Injection** | ✅ N/A | No SQL queries (using ORM/Parquet) |
| **XSS Protection** | ⚠️ Partial | Flask auto-escaping, but verify templates |
| **CSRF Protection** | ❌ Not implemented | Should add Flask-WTF |
| **Rate Limiting** | ❌ Not implemented | Can be abused |
| **Secrets Management** | ⚠️ .env file | Should use secrets manager (AWS Secrets Manager) |

### 9.2 Recommendations

**Short-term (Before Production):**
1. **Add Rate Limiting:** Flask-Limiter (10 requests/minute per IP)
2. **Input Sanitization:** Validate all JSON inputs, reject invalid data
3. **CSRF Protection:** Flask-WTF for form submissions
4. **Secrets Rotation:** Use environment variables from secure vault

**Medium-term (Production):**
1. **User Authentication:** JWT tokens or OAuth2
2. **Role-Based Access:** Free/Pro/Elite tiers
3. **API Keys:** For programmatic access
4. **Audit Logging:** Track all backtest requests

~~**Long-term (Enterprise):**~~ → **PARKEREN** (Staat op Build Contract No-Go lijst: "enterprise auth/security")

**Aangepast Plan (volgens Build Contract):**
1. ⚠️ ~~Multi-Factor Authentication~~ → **PARKEREN** (enterprise auth op No-Go lijst)
2. ✅ **Data Encryption:** Encrypt Parquet files at rest (S3 SSE) - OK voor productie
3. ⚠️ ~~VPC, security groups, WAF~~ → **PARKEREN** (enterprise security op No-Go lijst)
4. ✅ **Compliance:** GDPR compliance voor EU users - OK (basis vereiste)

**Focus:** Eenvoudige JWT auth voor Free/Pro tiers, geen enterprise security features.

---

## 10. Monitoring & Observability

### 10.1 Current Monitoring

**Available:**
- Console logging (stdout)
- Performance tracking decorator (`@track_performance`)
- Error logging (try/except with print statements)

**Missing:**
- Structured logging (JSON format)
- Metrics collection (Prometheus)
- Distributed tracing (OpenTelemetry)
- Error tracking (Sentry)
- Performance monitoring (APM)

### 10.2 Recommended Monitoring Stack

**Logging:**
- **Format:** JSON structured logs
- **Aggregation:** ELK Stack (Elasticsearch, Logstash, Kibana) or CloudWatch Logs
- **Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

**Metrics:**
- **Backend:** Prometheus + Grafana
- **Metrics:**
  - Backtest execution time (histogram)
  - Backtest success rate (counter)
  - Cache hit rate (gauge)
  - Module calculation time (histogram)
  - Data download time (histogram)

**Tracing:**
- **Tool:** OpenTelemetry
- **Spans:** Request → Backtest → Module Calculation → Data Fetch

**Error Tracking:**
- **Tool:** Sentry
- **Alerts:** Email/Slack on critical errors

---

## 11. Future Architecture Considerations

### 11.1 Planned Enhancements

1. ~~**Async Backtest Execution**~~ → **PARKEREN** (Staat op Build Contract No-Go lijst: "async queues")
   - **Pattern:** Queue-based (Celery/Redis) - **NIET voor MVP**
   - **Benefits:** Non-blocking, progress updates, retry logic
   - **Complexity:** Medium (3-5 days)
   - **Status:** Alleen implementeren bij bewezen pijn (na product-market fit)

2. **Multi-Timeframe Support**
   - **Pattern:** MTF module category
   - **Benefits:** HTF bias + LTF entry strategies
   - **Complexity:** High (1-2 weeks)

3. **Distributed Caching**
   - **Pattern:** Redis cluster
   - **Benefits:** Shared cache across workers
   - **Complexity:** Low (2-3 days)

4. ~~**Microservices Split**~~ → **PARKEREN** (Staat op Build Contract No-Go lijst: "microservices")
   - **Pattern:** Separate services for data, backtest, analysis - **NIET voor MVP**
   - **Benefits:** Independent scaling, technology diversity
   - **Complexity:** Very High (1-2 months)
   - **Status:** Alleen implementeren bij bewezen schaal (na product-market fit, waarschijnlijk nooit nodig)

### 11.2 Technology Evolution

**Potential Migrations:**
- **Flask → FastAPI:** Better async support, automatic API docs
- **Pandas → Polars:** Faster DataFrame operations (Rust-based)
- **Playwright → ReportLab:** Faster PDF generation (no browser)
- **Yahoo Finance → Paid Data Provider:** More reliable, higher rate limits

**When to Migrate:**
- **FastAPI:** When async becomes critical (100+ concurrent users)
- **Polars:** When data processing is bottleneck (large datasets)
- **ReportLab:** When PDF generation is slow (currently 2-7s)
- **Paid Data:** When Yahoo Finance rate limits hit frequently

---

## 12. Recommendations for Data Engineers

### 12.1 Data Pipeline Improvements

1. **Implement Data Validation Layer**
   - Validate OHLCV data (high >= low, etc.)
   - Check for gaps in time series
   - Detect anomalies (spikes, zeros)

2. **Add Data Quality Metrics**
   - Missing data percentage
   - Data freshness (last update timestamp)
   - Completeness score (expected vs actual rows)

3. **Create Data Lineage Tracking**
   - Track data source → cache → backtest usage
   - Enable data provenance queries

### 12.2 Storage Optimization

1. **Partition Parquet Files by Date**
   - Current: Single file per symbol/timeframe
   - Recommended: Partition by year/month
   - Benefits: Faster queries, smaller file sizes

2. **Implement Column Pruning**
   - Only load required columns for backtest
   - Reduces memory usage, faster I/O

3. **Add Compression**
   - Use Snappy or Zstd compression for Parquet
   - Trade-off: Slightly slower reads, 50-70% size reduction

---

## 13. Recommendations for Software Architects

### 13.1 Architecture Improvements

1. **Implement Dependency Injection**
   - Current: Direct instantiation (tight coupling)
   - Recommended: DI container for services
   - Benefits: Easier testing, configuration flexibility

2. **Add Circuit Breaker Pattern**
   - Protect against external service failures (Yahoo Finance)
   - Fallback to cached data when external service is down

3. **Implement Strategy Pattern for Backtest Engines**
   - Current: Single BacktestEngine class
   - Recommended: Interface with multiple implementations
   - Benefits: Easier to add new engine types (e.g., walk-forward)

### 13.2 Code Organization

1. **Split Large Files**
   - `app.py` is 1200+ lines (should be ~200-300)
   - Extract route handlers to separate modules
   - Extract business logic to service layer

2. **Add Domain Models**
   - Current: Dictionaries and dataclasses
   - Recommended: Rich domain models with methods
   - Benefits: Better encapsulation, easier to test

3. **Implement Repository Pattern**
   - Abstract data access behind interfaces
   - Easier to swap storage backends
   - Better testability (mock repositories)

---

## Appendix A: Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.11+ | Backend development |
| **Web Framework** | Flask | 2.x | HTTP server, routing |
| **Data Processing** | Pandas | 2.x | DataFrame operations |
| **Numerical Computing** | NumPy | 1.x | Vectorized operations |
| **Data Storage** | Parquet | - | Columnar storage format |
| **Data Download** | yfinance | Latest | Yahoo Finance API client |
| **PDF Generation** | Playwright | Latest | Browser-based PDF rendering |
| **Caching (Future)** | Redis | 7.x | Distributed cache |
| **Task Queue (Future)** | Celery | 5.x | Async task processing |
| **Database (Future)** | PostgreSQL | 14+ | Metadata storage |
| **Object Storage (Future)** | S3 | - | Parquet file storage |

---

## Appendix B: Key Design Patterns Used

1. **Strategy Pattern:** Storage backends (LocalStorage, CloudStorage)
2. **Registry Pattern:** Module discovery and management
3. **Factory Pattern:** Storage backend creation (`get_storage_backend()`)
4. **Adapter Pattern:** Decision Blocks → Conditions conversion
5. **Singleton Pattern:** Module registry (`get_registry()`)
6. **Template Method Pattern:** BaseModule.calculate() interface

---

**Laatste Update:** December 2024  
**Volgende Review:** Na implementatie async backtest execution (indien bewezen nodig)

---

## Appendix C: Architecture Guardrails

**⚠️ CRITICAL:** Dit rapport beschrijft technische mogelijkheden. Voor daadwerkelijke implementatie, zie [Architecture Guardrails](docs/ARCHITECTURE_GUARDRAILS.md).

**Key Guardrails:**
- **G1:** Decision Block Model blijft bron van waarheid
- **G2:** Modules stateless + config per request
- **G3:** Registry enige module-ingang
- **G4:** Storage pluggable via interface
- **G5:** BacktestEngine deterministisch
- **G6-G8:** API versioning, error contract, resource limits

**Toegestane evolutie:**
- **E1:** Async alleen bij bewezen noodzaak (aligns met Build Contract)
- **E2:** PDF ontkoppelen (OK voor UX)
- **E3:** Engine strategy pattern (toekomst)

Deze guardrails voorkomen architecturale schuld en behouden codebase gezondheid.

**Gerelateerde documenten:**
- [Build Contract](docs/BUILD_CONTRACT.md) - Product focus en scope
- [30/60/90 Roadmap](docs/30_60_90_ROADMAP.md) - Concrete implementatie roadmap (0-90 dagen)
- [Architecture Guardrails](docs/ARCHITECTURE_GUARDRAILS.md) - Volledige guardrails definitie (G1-G8)
- [Build Contract Alignment](docs/BUILD_CONTRACT_ALIGNMENT.md) - Alignment review
