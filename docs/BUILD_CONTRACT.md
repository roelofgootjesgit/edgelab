# QuantMetrics.io — Build Contract (Cursor)

## Rol
Je bent aan het bouwen als **product-led fintech**.
- Jij schrijft code
- Dit document bewaakt **focus, scope en beslissingen**

---

## Product (1 zin)
QuantMetrics is een **strategy builder + evidence machine** voor traders:  
bouw → test → begrijp → bewijs (PDF).

---

## Doelgroep (fase 1)
**Primary**
- ICT / SMC discretionary traders
- Prop-firm aspiranten
- Pijn: emotie, inconsistentie, geen bewijs

**Secondary**
- Signal verifiers / communities

❌ Geen quants, HF's, enterprise in deze fase.

---

## Core Value
Elke feature moet bijdragen aan minimaal **1** van deze:
1. Time-to-value (<10 min)
2. Trust / evidence
3. Explainability
4. Monetization

Faalt het op allemaal → **niet bouwen**.

---

## Heilig Pad (MVP Flow)
Template  
→ Run  
→ Analyse  
→ **PDF rapport (core output)**  
→ Uitleg: *wat werkt / wat faalt / waarom*

PDF is **geen bijzaak**, maar het product.

---

## CEO No-Go List
NIET bouwen tenzij bewezen pijn:
- microservices
- async queues
- enterprise auth/security
- data provider switches
- performance refactors zonder bottleneck

---

## 30-Dagen Focus
### 1. Time-to-Value
- 1-click template run
- Resultaat binnen minuten
- Begrijpelijke output

### 2. Reliability
- Heldere errors
- Geen silent failures
- Logging > optimalisatie

### 3. Verkoopbaar
- Deelbare PDF
- "Dit is mijn bewijs"-moment

---

## Pricing (initieel)
**Free**
- Beperkte periode
- Beperkte modules
- Beperkte PDF

**Pro (€49 richtprijs)**
- Meer modules
- Onbeperkt PDF
- Saved strategies
- Regime labels

Geen extra tiers bij launch.

---

## KPI's (waar we op sturen)
- Activation: template → run (1 sessie)
- PDF generated per user
- p95 backtest latency
- Error rate
- Free → Pro conversie
- Week 1 → week 4 retentie

---

## Operating Rules
Wekelijks:
- 1 user-facing feature
- 1 reliability fix
- 1 sell-asset (template / demo / report)

❌ Nooit 3 weken bouwen zonder zichtbare output.

---

## Decision Rules
- Kan ik dit in **1 zin** aan een trader uitleggen?
- Helpt dit hen **minder gokken**?
- Kan ik hier later **geld voor vragen**?

Nee op alle drie → **parkeren**.

---

## Eerste Publieke Demo
**ICT Kill Zone template**
→ backtest  
→ PDF  
→ uitleg waarom het werkt of faalt

Alles daarbuiten is secundair.

---

**Gerelateerde documenten:**
- [30/60/90 Roadmap](30_60_90_ROADMAP.md) - Concrete implementatie roadmap (0-90 dagen)
- [Architecture Guardrails](ARCHITECTURE_GUARDRAILS.md) - Technische guardrails (G1-G8)
