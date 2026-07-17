# B+LNZ Stock Unit Conversions — Source Record
 
**Source:** Beef + Lamb New Zealand, Economic Service (Sheep & Beef Farm Survey)
**Received:** via email, June 2026 (direct response to student data request)
**Status:** Current survey standard. B+LNZ noted these conversions are **under review**;
they have been held constant for many years to preserve a consistent timeseries.
 
## Important framing (per B+LNZ, quote from email)
 
> "Overall, stock units in the Sheep & Beef Farm Survey provide a general guide for
> 'policy purposes' to implied feed utilisation. Detailed farm management decisions at
> the farm level are best carried out by feed budgeting."
 
**Implication for PastureIQ:** these values are the correct *national, feed-only* baseline
for the feed-demand layer. They are NOT a substitute for farm-level feed budgeting and
should be represented in documentation as B+LNZ's survey-standard policy conversions.
 
## Stock Unit Conversion Ratios (as supplied)
 
### Sheep
| Class | Stock Units |
|---|---|
| Ewes | 1.0 |
| Hoggets | 0.7 |
| Wethers | 0.7 |
| Rams | 0.8 |
| Grazing Sheep (from 2009-10 Survey) | 0.7 |
 
### Beef Cattle
| Class | Cattle Equivalent | Stock Units |
|---|---|---|
| M.A. Cows | 1.0 | 5.5 |
| Heifers 2.5 Yr | 1.0 | 5.5 |
| Heifers 1.5 Yr | 0.8 | 4.5 |
| Heifers Weaner | 0.6 | 3.5 |
| Bulls Weaner | 0.8 | 4.5 |
| Steers Weaner | 0.8 | 4.5 |
| Steers 1.5 Yr | 0.9 | 5.0 |
| Steers 2.5 Yr | 1.0 | 5.5 |
| Bull Beef 1.5 Yr+ | 1.0 | 5.5 |
| Bulls Breeding | 1.0 | 5.5 |
 
### Dairy (grazing on sheep & beef farms)
| Class | Cattle Equivalent | Stock Units |
|---|---|---|
| R2 Dairy Heifers | 0.8 | 4.5 |
| R1 Dairy Heifers | | 3.5 |
| Dairy Cows (Winter) | | 1.1 |
 
## Reconciliation notes — values that CHANGED from earlier project assumptions
 
These figures supersede earlier placeholders. A full sweep of FORMULAS.md and the MRC is
needed to apply them consistently. Beef cow held at national 5.5 (B+LNZ). The earlier 5.8 estimate folded hard-hill-country terrain effect into the LSU value; that terrain adjustment now lives in the carrying-capacity modifier instead, keeping LSU feed-only and national per design
 
- **Beef cow: 5.5** — supersedes both RuralFind's 4.4 AND the project's earlier
  B+LNZ-derived estimate of 5.8. Use 5.5 (B+LNZ survey authoritative).
- **Hogget: 0.7** — supersedes the MRC placeholder of 1.0.
- Use the **Stock Units** column (right) for feed-demand maths, NOT the Cattle Equivalent
  column (which is a within-cattle relative ratio, not a feed figure).
## Pending from same source
- Farmgate price trend timeseries — promised in follow-up email, awaited.
 