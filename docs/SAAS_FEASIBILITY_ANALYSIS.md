# SaaS Feasibility Analysis - V4 Backtest System

> **⚠️ BUILD CONTRACT WAARSCHUWING:** Dit document bevat suggesties voor async queues (Celery/Redis) die op de [Build Contract No-Go lijst](BUILD_CONTRACT.md) staan. Deze oplossingen zijn alleen relevant bij **bewezen pijn**. Focus eerst op Quick Test mode en caching (geen async queues).

## Het Probleem

**Huidige situatie:**
- Elke backtest duurt 3-5 minuten
- Gebruiker moet wachten op resultaten
- Niet geschikt voor SaaS/abonnement model

**Acceptabele wachttijden voor SaaS:**
- **Snelle test (< 30 seconden)**: Acceptabel, gebruiker blijft engaged
- **Uitgebreide test (30-60 seconden)**: Acceptabel met loading indicator
- **Complexe test (1-2 minuten)**: Acceptabel met progress updates
- **3-5 minuten**: ❌ Te lang, gebruikers verlaten de pagina

## Oplossingen

### Optie 1: Asynchrone Backtests met Progress Updates ⚠️ **NO-GO** (Staat op Build Contract No-Go lijst)

**Implementatie:**
```python
# Frontend: Start backtest
POST /run-backtest-v4-async
→ Returns: { "job_id": "abc123", "status": "queued" }

# Frontend: Poll voor updates
GET /backtest-status/{job_id}
→ Returns: { 
    "status": "processing", 
    "progress": 45,  # percentage
    "current_step": "Calculating indicators...",
    "estimated_time_remaining": 120  # seconds
}

# Frontend: Get results wanneer klaar
GET /backtest-results/{job_id}
→ Returns: { "status": "completed", "trades": [...], "pdf": "..." }
```

**Voordelen:**
- Gebruiker kan andere dingen doen terwijl backtest draait
- Progress updates houden gebruiker engaged
- Kan meerdere backtests tegelijk draaien
- Betere UX

**Nadelen:**
- ⚠️ **Staat op Build Contract No-Go lijst** ("async queues")
- Complexer om te implementeren
- Vereist job queue (Redis/Celery of simpelere oplossing)
- **Alleen implementeren bij bewezen pijn** (niet voor MVP)

### Optie 2: Aggressieve Caching

**Implementatie:**
```python
# Cache key: hash van (symbol, timeframe, period, modules, config)
cache_key = hashlib.md5(
    f"{symbol}_{timeframe}_{period}_{module_ids}_{config_hash}".encode()
).hexdigest()

# Check cache eerst
if cache.exists(cache_key):
    return cached_results  # Instant!

# Run backtest en cache result
results = run_backtest(...)
cache.set(cache_key, results, ttl=3600)  # 1 hour
```

**Voordelen:**
- Herhaalde tests zijn instant
- Eenvoudig te implementeren
- Grote performance boost voor veel gebruikers

**Nadelen:**
- Helpt niet bij eerste test
- Cache invalidation complex
- Memory/disk usage

### Optie 3: Snellere Backtest Engine

**Optimalisaties:**
1. **Parallel module processing** (als modules onafhankelijk zijn)
2. **Lazy evaluation** (bereken alleen wat nodig is)
3. **Data sampling** (gebruik minder data voor snelle test)
4. **Incremental calculation** (cache intermediate results)

**Voordelen:**
- Fundamenteel sneller
- Betere user experience

**Nadelen:**
- Complex om te implementeren
- Kan accuracy beïnvloeden (bij sampling)

### Optie 4: Hybrid Approach (Aangepast) ⭐ AANBEVOLEN VOOR MVP

**⚠️ Noot:** Async backtests (Celery/Redis) zijn verwijderd - staat op No-Go lijst. Focus op Quick Test + Caching alleen.

**Combineer:**
1. **Quick Test** (< 30 sec): 
   - Minder data (30 dagen i.p.v. 60)
   - Minder modules (max 3-4)
   - Snelle preview

2. **Full Test** (1-2 min):
   - Volledige data
   - Alle modules
   - Asynchroon met progress

3. **Caching**:
   - Cache populaire strategieën
   - Instant results voor veel gebruikers

**Implementatie:**
```python
# Frontend: Quick test button
POST /run-backtest-v4-quick
→ Fast mode: 30 days, max 4 modules, simplified logic
→ Returns results in < 30 seconds

# Frontend: Full test button  
POST /run-backtest-v4-full
→ Full mode: All data, all modules
→ Returns job_id, poll for results
```

## Aanbeveling: Hybrid Approach

### Fase 1: Quick Test (Week 1)
- Implementeer "Quick Test" mode
- 30 dagen data, max 4 modules
- Doel: < 30 seconden
- Gebruikers krijgen snelle feedback

### Fase 2: Caching (Week 2)
- Implementeer Redis/Memcached caching
- Cache key: hash van parameters
- TTL: 1-24 uur (afhankelijk van data freshness)
- Instant results voor herhaalde tests

### Fase 3: ~~Async Backtests~~ → **GEANNULEERD** (Staat op No-Go lijst)

**⚠️ Aangepast Plan:**
- Focus op Quick Test mode optimalisatie (geen async queue)
- Caching voor herhaalde tests (in-memory of Redis zonder Celery)
- Progress updates via polling (geen job queue)
- **Async queues alleen implementeren bij bewezen pijn** (na product-market fit)

## Technische Implementatie

### Quick Test Mode
```python
def run_backtest_quick(symbol, timeframe, modules, ...):
    # Limit data
    period_days = min(30, period_days)  # Max 30 days
    
    # Limit modules
    modules = modules[:4]  # Max 4 modules
    
    # Simplified logic
    # ... fast path ...
    
    return results  # < 30 seconds
```

### Caching Layer
```python
import redis
import hashlib
import json

redis_client = redis.Redis(host='localhost', port=6379)

def get_cache_key(symbol, timeframe, period, modules, config):
    # Create unique key from parameters
    key_str = f"{symbol}_{timeframe}_{period}_{json.dumps(modules, sort_keys=True)}"
    return hashlib.md5(key_str.encode()).hexdigest()

def get_cached_backtest(cache_key):
    cached = redis_client.get(f"backtest:{cache_key}")
    if cached:
        return json.loads(cached)
    return None

def cache_backtest(cache_key, results, ttl=3600):
    redis_client.setex(
        f"backtest:{cache_key}",
        ttl,
        json.dumps(results)
    )
```

### Async Job Queue (Simple Version)
```python
# Simple in-memory queue (voor MVP)
# Later: Celery + Redis voor production

backtest_jobs = {}  # {job_id: {status, progress, results}}

@app.route('/run-backtest-v4-async', methods=['POST'])
def run_backtest_async():
    job_id = str(uuid.uuid4())
    backtest_jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'results': None
    }
    
    # Start background thread
    thread = threading.Thread(
        target=run_backtest_worker,
        args=(job_id, request.get_json())
    )
    thread.start()
    
    return {'job_id': job_id, 'status': 'queued'}

def run_backtest_worker(job_id, data):
    try:
        backtest_jobs[job_id]['status'] = 'processing'
        backtest_jobs[job_id]['progress'] = 10
        
        # Run backtest with progress updates
        results = run_backtest_with_progress(data, job_id)
        
        backtest_jobs[job_id]['status'] = 'completed'
        backtest_jobs[job_id]['progress'] = 100
        backtest_jobs[job_id]['results'] = results
    except Exception as e:
        backtest_jobs[job_id]['status'] = 'failed'
        backtest_jobs[job_id]['error'] = str(e)
```

## Conclusie

**Is het systeem geschikt voor SaaS?**
- ❌ **Niet in huidige vorm** (3-5 minuten is te lang)
- ✅ **Wel met optimizations** (Quick test + Caching + Async)

**Aangepaste roadmap (volgens Build Contract):**
1. **Week 1**: Quick test mode (< 30 sec) ✅ **GO**
2. **Week 2**: Caching layer (in-memory of Redis, geen Celery) ✅ **GO**
3. **Week 3-4**: ~~Async backtests~~ → **PARKEREN** (staat op No-Go lijst)
   - Focus in plaats daarvan op PDF polish en error handling

**Resultaat:**
- Quick tests: < 30 seconden ✅
- Cached tests: Instant ✅
- Full tests: 1-2 minuten asynchroon ✅

Dit maakt het systeem geschikt voor SaaS!

