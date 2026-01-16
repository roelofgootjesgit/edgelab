# QuantMetrics.io — Architecture Guardrails (v1.0)
Datum: 2026-01-16  
Scope: Strategy Builder V4/V5 platform (Flask-based), module registry, storage abstraction.

> **Relatie met Build Contract:** Deze guardrails beschermen de technische architectuur, terwijl het [Build Contract](BUILD_CONTRACT.md) de product-focus en scope bewaakt. Beide documenten werken samen om technische schuld en scope creep te voorkomen.

---

## Doel
Dit document beschermt de kern van de architectuur tegen "handige shortcuts" die later maanden refactor kosten.
Alles wat hieronder staat is een **guardrail**: veranderen mag, maar alleen bewust en met expliciete reden.

---

## Guardrails (Niet onderhandelbaar)

### G1 — Decision Block Model blijft de bron van waarheid
- **Declarative input** (Decision Blocks / ICT config) is altijd leidend.
- Converters mogen uitbreiden, maar nooit de UI laten afhangen van imperatieve engine-details.
- Geen "hard-coded strategy logic" in routes of templates.

**Waarom:** dit is je moat. Dit maakt het product verkoopbaar als builder, niet als losse backtester.

**Build Contract Alignment:** Ondersteunt "Time-to-value" (1-click template run) en "Explainability" (declarative = begrijpelijk).

---

### G2 — Modules blijven stateless + config per request
- Modules bewaren **geen state** tussen requests.
- `calculate(data, config)` is pure-ish: input → output kolommen.
- Geen singletons met mutable state in modules.
- Module init krijgt **geen config**; config wordt geïnjecteerd per run.

**Waarom:** concurrency, testbaarheid, parallelisering later.

**Build Contract Alignment:** Ondersteunt "Reliability" (geen race conditions, reproduceerbare resultaten).

---

### G3 — Registry blijft de enige module-ingang
- Nieuwe modules komen alleen binnen via:
  - auto-discovery + registry
  - module_id als primaire sleutel
- Geen directe imports van module classes in business logic.

**Waarom:** plugin-achtig uitbreiden zonder coupling.

**Build Contract Alignment:** Ondersteunt "Time-to-value" (nieuwe modules zonder code changes) en extensibility.

---

### G4 — Storage is pluggable via één interface
- Business logic praat alleen met `DataManager` + `DataStorage` interface.
- Local (Parquet) en Cloud (S3+PG) blijven drop-in.
- Geen "even snel een query" in de engine zonder repository/adapter.

**Waarom:** later migreren zonder breken.

**Build Contract Alignment:** Ondersteunt toekomstige schaling zonder refactoring (aligns met Build Contract's "bewezen schaal" filosofie).

---

### G5 — BacktestEngine is deterministisch op dezelfde input
- Zelfde input JSON + dezelfde data snapshot = zelfde output (binnen floating tolerance).
- Geen hidden randomness zonder seed.
- Logging en report moeten reproduceerbaar zijn.

**Waarom:** vertrouwen, debugging, "evidence" richting traders.

**Build Contract Alignment:** Core voor "Trust / evidence" en "PDF rapport" - traders moeten kunnen vertrouwen op resultaten.

---

## Guardrails (Sterk aanbevolen)

### G6 — API versioning vanaf nu
- Nieuwe endpoints gaan onder `/api/v1/...`
- UI routes mogen blijven zoals ze zijn.

**Waarom:** je gaat breken, dus vang het nu op.

**Build Contract Alignment:** Ondersteunt "Reliability" (geen breaking changes voor gebruikers).

---

### G7 — Eén error contract overal
- Elke error terug als:
  - `success=false`, `code`, `error`, `details`
- Geen "print + 500" in productie.

**Build Contract Alignment:** Ondersteunt "Reliability" ("heldere errors, geen silent failures").

---

### G8 — Resource limits zijn verplicht
Hard limits (config):
- max candles / max period
- max modules per strategy
- max concurrent runs per IP/user

**Waarom:** misbruik + kostenbeheersing.

**Build Contract Alignment:** Ondersteunt "Monetization" (kostenbeheersing) en "Reliability" (prevente van DoS).

---

## Toegestane evolutie (Roadmap-proof)

### E1 — Async pas als noodzaak bewezen is
Async queue (Celery/Redis) pas invoeren als:
- p95 backtest latency structureel > 25-30s **of**
- users willen batch/backtests draaien zonder wachten.

Tot die tijd: sync + goede UX + hard limits.

**Build Contract Alignment:** ✅ **In lijn met No-Go lijst** - "async queues" alleen bij bewezen pijn. Focus eerst op Quick Test mode (geen async).

---

### E2 — PDF generatie ontkoppelen
Toegestaan:
- HTML results direct
- PDF via aparte endpoint/button (on-demand)

**Build Contract Alignment:** Ondersteunt "PDF rapport (core output)" - PDF blijft het product, maar mag async worden gegenereerd als UX beter is.

---

### E3 — Engine-strategypattern mag later
Toegestaan:
- meerdere engines (walk-forward, Monte Carlo, live sim)
Maar alleen achter een interface: `IBacktestEngine`.

**Build Contract Alignment:** Toekomstige extensie zonder architecturale schuld. Aligns met "bewezen pijn" filosofie.

---

## Anti-patterns (Verboden zonder expliciete beslissing)

- Microservices split "omdat het kan"
- Modules met globale state / caches in modulefiles
- Route handlers die business rules bevatten
- Data provider calls vanuit engine zonder throttling/fallback
- "Even snel" opslaan van user strategies zonder versie/owner model

**Build Contract Alignment:** Veel anti-patterns staan ook op Build Contract No-Go lijst:
- ❌ "Microservices" → No-Go lijst
- ❌ Business rules in routes → Breekt G1 (Decision Block Model)
- ❌ Global state in modules → Breekt G2 (stateless modules)

---

## Implementatie Checklist

### Bij elke nieuwe feature:
- [ ] Respecteert G1-G5 (niet onderhandelbaar)?
- [ ] Volgt G6-G8 (sterk aanbevolen)?
- [ ] Gebruikt toegestane evolutie (E1-E3) waar nodig?
- [ ] Vermijdt anti-patterns?
- [ ] Past binnen Build Contract Core Value criteria?

### Bij code review:
- [ ] Modules stateless? (G2)
- [ ] Module via registry? (G3)
- [ ] Storage via interface? (G4)
- [ ] Deterministic engine? (G5)
- [ ] Error contract gevolgd? (G7)
- [ ] Resource limits toegepast? (G8)

---

## Uitzonderingen

**Guardrails kunnen worden gebroken alleen met:**
1. Expliciete architect beslissing
2. Gedocumenteerde reden
3. Plan voor toekomstige fix/refactor
4. Goedkeuring van tech lead / architect

**Voorbeeld uitzondering:**
- "Tijdelijk directe import in route voor hotfix, maar in backlog voor G3 compliance"

---

## Evolutie van dit document

**Versie 1.0 (2026-01-16):** Initial guardrails voor V4/V5 platform.

**Toekomstige revisies:**
- Bij architectuurwijzigingen
- Bij nieuwe patterns/problemen
- Bij Build Contract wijzigingen die architectuur beïnvloeden

---

**Gerelateerde documenten:**
- [Build Contract](BUILD_CONTRACT.md) - Product focus en scope
- [Technical Architecture Report](../TECHNICAL_ARCHITECTURE_REPORT.md) - Gedetailleerde architectuur
- [Build Contract Alignment](BUILD_CONTRACT_ALIGNMENT.md) - Alignment review
