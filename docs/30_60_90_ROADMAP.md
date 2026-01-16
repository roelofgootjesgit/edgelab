# QuantMetrics.io — 30/60/90 Roadmap (v1.0)
Datum: 2026-01-16  
Doel: Van werkende builder → verkoopbaar product → schaalbaar platform.

> **Build Contract Alignment:** Deze roadmap volgt de [Build Contract](BUILD_CONTRACT.md) prioriteiten:
> - **0-30 dagen:** Time-to-value (<10 min), Reliability (heldere errors), Verkoopbaar (PDF polish)
> - **31-60 dagen:** Differentiatie (regime labels, saved strategies)
> - **61-90 dagen:** Production-ready (accounts, tiers, schaal zonder enterprise complexity)

---

## North Star
Een trader kan binnen 10 minuten:
1) template kiezen
2) 3-5 modules tunen
3) backtest draaien
4) een PDF/rapport delen
5) en snappen: "welke markt/regime past hierbij?"

**Build Contract Core Value:** Time-to-value (<10 min), Trust/evidence (PDF), Explainability (regime context)

---

## 0–30 dagen: Verkoopbaarheid & betrouwbaarheid (P0)

**Focus volgens Build Contract:**
- ✅ Time-to-value (<10 min)
- ✅ Reliability (heldere errors, geen silent failures)
- ✅ Verkoopbaar (deelbare PDF, "Dit is mijn bewijs"-moment)

### Product
- [ ] Template flow: "Kies → Configureer → Run → Result"
- [ ] Strategy fingerprint: unieke hash op input + data snapshot
- [ ] "Generate PDF" knop los van backtest (snellere UX)

**Build Contract:** Ondersteunt "Heilig Pad" (Template → Run → Analyse → PDF)

### Engineering
- [ ] API versioning `/api/v1`
- [ ] Eén error contract + consistente validation
- [ ] Hard limits (modules/period/candles) + rate limiting (basic)
- [ ] Structured logging (json logs minimaal)

**Architecture Guardrails:**
- G6: API versioning (sterk aanbevolen)
- G7: Eén error contract (sterk aanbevolen)
- G8: Resource limits (verplicht)

### Data
- [ ] Yahoo throttling + jitter + cache-first fallback
- [ ] Data freshness zichtbaar in UI ("cached as of …")

**Build Contract:** Ondersteunt "Reliability" (geen failures door rate limits)

### Output (definition of done)
- Backtest p95 < 15s (cached) bij 3-4 modules
- 0 "mysterieuze" 500's zonder error code/details
- PDF los te genereren zonder de hele run opnieuw

**Build Contract KPI's:** p95 backtest latency, Error rate

---

## 31–60 dagen: Differentiatie (P1)

**Focus volgens Build Contract:**
- ✅ Differentiatie (regime labels, "why failed")
- ✅ Saved strategies (Pro tier feature)
- ✅ Monetization (regime labels = Pro feature)

### Product
- [ ] Regime / context label in output (trend/range/volatile)
- [ ] "Why this failed" hints (top 3 failure modes)
- [ ] Saved strategies (local json of DB light), versiebeheer

**Build Contract:** Regime labels in Pro tier (€49), Saved strategies in Pro tier

### Engineering
- [ ] Parallel module calc (alleen als >4 modules winst geeft)
- [ ] Result cache (Redis of file-based) op fingerprint
- [ ] Observability light: metrics (duration, cache hit, success rate)

**Build Contract:** Performance optimalisatie alleen bij bewezen bottleneck (>4 modules winst)

### Output (definition of done)
- 1-click shareable report
- Result caching werkt en scheelt zichtbaar tijd
- Eerste "premium worthy" feature: context/regime + guidance

**Build Contract:** "Verkoopbaar" - "Dit is mijn bewijs"-moment met regime context

---

## 61–90 dagen: Production-ready schaal (P2)

**Focus volgens Build Contract:**
- ✅ Accounts + tiers (Free/Pro - geen Elite)
- ✅ Quota model (Free vs Pro limits)
- ✅ Schaal zonder enterprise complexity

### Product
- [ ] Accounts + tiers (Free/Pro) minimal
- [ ] Quota model: runs/day, max period, pdf exports

**Build Contract:** Free/Pro tiers (€49 Pro), geen extra tiers bij launch

### Engineering
- [ ] Gunicorn workers + Nginx reverse proxy (prod)
- [ ] Redis voor cache (als multi-worker)
- [ ] Basis auth (JWT) + audit logging

**Build Contract:** ✅ Eenvoudige JWT auth (geen enterprise auth op No-Go lijst)
**Architecture Guardrails:** G4 (pluggable storage), G6 (API versioning)

### Optioneel (alleen bij bewezen noodzaak)
- [ ] Async queue (Celery) voor lange jobs / batch runs

**⚠️ Build Contract No-Go:** Async queues alleen bij bewezen pijn (p95 > 25-30s structureel of users willen batch zonder wachten)

### Output (definition of done)
- 50–100 users aan zonder downtime
- Duidelijke grenzen per tier
- Monitoring op p95 latency + error rate

**Build Contract KPI's:** p95 backtest latency, Error rate, Free → Pro conversie

---

## Wat we NIET doen in 90 dagen

**Build Contract No-Go Items:**
- ❌ Microservices split → **PARKEREN** (No-Go lijst)
- ❌ Polars migratie "voor snelheid" → **PARKEREN** (performance refactor zonder bottleneck)
- ❌ Enterprise compliance stack → **PARKEREN** (enterprise auth/security op No-Go lijst)
- ❌ Paid data provider (tenzij Yahoo aantoonbaar blokkeert op load) → **PARKEREN** (data provider switches op No-Go lijst)

**Architecture Guardrails:** Anti-patterns vermijden - "Microservices split 'omdat het kan'"

---

## Success Metrics (volgens Build Contract KPI's)

### 0-30 dagen:
- ✅ Activation: template → run (1 sessie)
- ✅ p95 backtest latency < 15s (cached)
- ✅ Error rate < 1% (geen "mysterieuze" 500's)
- ✅ PDF generated per user

### 31-60 dagen:
- ✅ PDF generated per user (verhoogd)
- ✅ Free → Pro conversie (regime labels = Pro feature)
- ✅ Week 1 → week 4 retentie

### 61-90 dagen:
- ✅ 50-100 users zonder downtime
- ✅ Free → Pro conversie rate
- ✅ p95 latency < 15s (cached) bij 50-100 users
- ✅ Error rate < 1%

---

## Risico's & Mitigaties

### Risico: Yahoo Finance rate limiting
**Mitigatie:** Throttling + jitter + cache-first (0-30 dagen)

### Risico: Backtest latency > 15s
**Mitigatie:** Quick Test mode, caching, parallel calc (>4 modules)

### Risico: PDF generatie te traag
**Mitigatie:** PDF los van backtest, on-demand generatie

### Risico: Schaalbaarheid bij 50-100 users
**Mitigatie:** Gunicorn workers + Redis cache (61-90 dagen)

---

## Rollout Plan

### Week 1-2 (0-30 start):
- Template flow polish
- Error contract implementatie
- Structured logging

### Week 3-4 (0-30 afronding):
- PDF on-demand
- Data freshness UI
- Hard limits + rate limiting

### Week 5-6 (31-60 start):
- Regime labels in output
- "Why failed" hints
- Saved strategies (JSON)

### Week 7-8 (31-60 afronding):
- Parallel module calc
- Result caching
- Observability metrics

### Week 9-10 (61-90 start):
- Accounts + tiers (Free/Pro)
- Quota model
- Basis JWT auth

### Week 11-12 (61-90 afronding):
- Production deployment (Gunicorn + Nginx)
- Redis cache
- Monitoring dashboard

---

## Definition of Done per Fase

### 0-30 dagen (Verkoopbaar):
- [ ] Template flow werkt end-to-end < 10 minuten
- [ ] PDF kan on-demand gegenereerd worden
- [ ] Alle errors hebben code + details
- [ ] p95 latency < 15s (cached)

### 31-60 dagen (Differentiatie):
- [ ] Regime labels zichtbaar in output
- [ ] "Why failed" hints aanwezig
- [ ] Saved strategies werken (JSON/light DB)
- [ ] Result caching scheelt zichtbaar tijd

### 61-90 dagen (Production-ready):
- [ ] Accounts + Free/Pro tiers werkend
- [ ] Quota model enforced
- [ ] 50-100 users zonder downtime
- [ ] Monitoring op p95 + error rate

---

**Gerelateerde documenten:**
- [Build Contract](BUILD_CONTRACT.md) - Product focus en KPI's
- [Architecture Guardrails](ARCHITECTURE_GUARDRAILS.md) - Technische guardrails
- [Technical Architecture Report](../TECHNICAL_ARCHITECTURE_REPORT.md) - Gedetailleerde architectuur

---

**Laatste Update:** 2026-01-16  
**Volgende Review:** Na 30 dagen milestone
