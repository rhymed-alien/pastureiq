# PROJECT SPEC — PastureIQ
**The single orientation document. What the tool is, what it takes in, what it puts out,
and what infrastructure must exist to support it. Read this first when picking up work —
it keeps everything pointed at the same goal.**
 
---
 
## THE GOAL (one sentence, specific)
Help a time-poor NZ hill-country sheep & beef farmer decide WHEN to buy or sell stock, by
combining weather/soil-driven pasture supply, their mob's feed demand, and market price —
delivered as a short ranked list of actions with honest, horizon-anchored confidence.
 
## NOT THE GOAL (explicit scope limits)
- NOT a breeding-economics optimiser (hogget retention, multi-year flock strategy → point to B+LNZ).
- NOT a Farm Environment Plan / regulatory compliance tool (one disclaimer line only).
- NOT a precision per-paddock tool (grid weather ≈ regional, stated as a known limit).
- NOT a replacement for farmer judgement — it informs gut-feel, doesn't override it.
---
 
## INPUT (minimum, with optional saved profile)
**Minimum to get a recommendation:**
- Region (one of three: South Waikato/King Country · South Taranaki/N. Whanganui · West Auckland)
- Effective grazing hectares
- Mob composition: stock class + count (e.g. 200 mixed-age ewes, 15 breeding cows)
**Optional (saved profile — add detail once, reused after):**
- Lamb birth/age (enables the lamb→hogget timing guard)
- Current pasture cover (kg DM/ha) if the farmer knows it — else tool estimates
- Farm-class / terrain refinement
- Specific stock liveweights
Design principle: minimum friction first; depth optional and saved, not re-entered.
 
## OUTPUT (specific)
- A RANKED LIST of 1–2 clear actions (e.g. "1. Sell store lambs within 2 weeks · 2. Hold ewes").
- Each action tagged with: a TIMING WINDOW (1, 2, or 4 weeks) and a CONFIDENCE MARKER
  (HIGH / MEDIUM / LOW), where confidence is anchored to real forecast skill at that horizon.
- Highlighted TRADE-OFFS (e.g. "waiting may catch a higher price but risks the lamb→hogget
  price drop").
- Plain language. No jargon. Readable in under 30 seconds.
---
 
## INFRASTRUCTURE TO ADD (since last push)
New folders/files that must exist so the design above is buildable and stays oriented:
 
### New folder
```
data/predictions/        ← the predictions log (Group G). Stores every forecast made,
                            for later cross-check against actual outcomes. Enables the
                            accuracy track-record AND future bias correction / learning.
```
 
### New docs (this commit)
```
docs/FORMULAS.md         ← the complete formula reference (Groups A–G incl. bias correction)
docs/PROJECT_SPEC.md     ← this file: goal, I/O, scope, infrastructure, status
```
 
### config.py additions (proposed — review before adding)
```python
# --- Feed demand ---
DM_PER_LSU_PER_YEAR = 520          # kg DM/year per stock unit (modern NZ standard)
DM_PER_LSU_PER_DAY  = 1.42         # 520 / 365 (annual average; seasonal refinement later)
MJME_PER_LSU_PER_YEAR = 6000       # energy-equivalent of 1 LSU
 
# --- Time windows & confidence (anchored to forecast skill) ---
TIME_WINDOWS_DAYS = [7, 14, 28]
CONFIDENCE_BY_HORIZON = {7: "HIGH", 14: "MEDIUM", 28: "LOW"}
WEATHER_CONFIDENCE = {7: 0.85, 14: 0.60, 28: 0.40}
 
# --- Pasture ---
MIN_RESIDUAL_COVER_KGDM = 1300     # PLACEHOLDER — verify NZ hill-country figure before use
```
 
### Predictions log schema (data/predictions/predictions_log.csv)
```
date_made, region, horizon_days, variable, predicted_value, confidence, target_date,
actual_value, error
```
(actual_value and error filled in later, when target_date matures.)
 
---
 
## BUILD STATUS — what's done, what's next
**Done & verified:**
- Repo, structure, config, secrets handling (Block A setup)
- Weather data: 3 regions, 2015→2026, daily, 0 missing, verified (Block B)
- Baseline corrected: 1 LSU = 6000 MJME = 520 kg DM/yr
- Cattle LSU derived from B+LNZ Fact Sheet 90
- Formula map defined (FORMULAS.md), confidence anchored to cited forecast-skill research
**Pending / next:**
- stock_units.py — feed-only, liveweight-based (NOT terrain). Some values pending B+LNZ reply.
- regions.csv — coords + terrain + carrying-capacity ranges (the regional layer)
- B+LNZ price data (Block D) + soil-data research (Block D)
- B+LNZ direct request for per-class conversion table (parallel contact task)
- The 4 open decisions listed in FORMULAS.md
**Parallel contact tasks (waiting on replies):**
- NIWA licensing email — sent, follow-up scheduled
- B+LNZ conversion table request — to send
*Spec v1.0 — update the BUILD STATUS and OPEN DECISIONS as work progresses.*