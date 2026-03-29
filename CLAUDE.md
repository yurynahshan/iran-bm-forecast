# Iran Missile Strike Analysis

## Goal
Model and monitor Iranian ballistic missile strike capacity during the 2026 Iran-Israel war.

## Purpose
Infer Iran's underlying **system capacity** (launcher availability, logistics, operational doctrine) from observable strike data — not just count missiles.

## Intent
- Maintain and improve a validated stochastic model (`L_t ~ NB(mu_t, k)`)
- Track weekly deviations from model predictions via Z-scores
- Detect structural changes in Iranian military capability
- Produce actionable April 2026 forecasts updated as new data arrives

## Project Structure

```
iran_war/
├── data/         ← primary model inputs (CSV files + registry)
│   └── archive/  ← versioned snapshots before major restructures
├── docs/         ← methodology docs (initial strikes model.docx)
├── model/        ← Python model scripts (NB model, Z-score monitor)
└── reports/      ← source PDFs (JINSA, ISW, etc.)
```

## Data Structure

All model input data lives in `data/`. Scope: Iranian BM toward Israel only; Gulf/Iraq data stored as estimation support.

### Primary Files

| File | Purpose | Model role |
|------|---------|------------|
| `israel_daily_estimate.csv` | Israel-specific BM data, Feb 28–Mar 28, with method column | **Direct model input** (`L_t`) |
| `all_sources_daily.csv` | All raw source columns side-by-side (JINSA/IDF/Alma/Perplexity) | Cross-source comparison |
| `inventory.csv` | BM/launcher stock snapshots by weapon type | Context for capacity constraints |

### `data_type` + `method` Columns (`israel_daily_estimate.csv`)
**`data_type`** — epistemic status of the estimate:
- `observed` — source directly states per-day BM count at Israel
- `observed_partial` — confirmed data but incomplete (floor from casualties, or single confirmed event)
- `derived` — calculated from `bm_global − confirmed_non_israel`
- `proxy_est` — estimated indirectly (wave ratio or anchor-proportioning)

**`method`** — specific calculation used for `bm_il_est`:
- `bbc_prop` — Phase I: `est = JINSA_direct × (128/187)`; min uses BBC lower bound 115; max = JINSA direct
- `bbc_residual` — Day 5 only: `est = 128 − Σ(Phase_I_ests)`
- `anchor_prop` — Days 6–10: `est = 150 × waves_i / Σwaves(6–10)`; 150 = 300−128−22; range ±20%
- `wave_ratio` — Days 12–18: `est = alma_waves × 1.11`; ratio calibrated from Mar18–24 JINSA/Alma; range ±25%
- `jinsa_direct` — Day 11 + Days 19–25: JINSA stated per-country count; range = est ± 2 (chart precision)
- `jinsa_derived` — Days 26–27: `est = JINSA_global − Σ(confirmed non-Israel)`; range up to derived ceiling
- `media_count` — Days 28–29: IDF statement + media siren/barrage count + JINSA constraint
- `multi_source` — Days 18, 20, 27: weighted blend of JINSA (w=3), Alma wave_ratio (w=2), Perp accepted (w=2), Perp accepted_partial (w=1); constrained to [observed_floor, derived_ceiling]

### Key Data Facts
- **War start:** Feb 28, 2026 (Day 1)
- **Phases:** I = Days 1–4 (saturation), II = Days 5–7 (rapid collapse), III = Day 8+ (stochastic)
- **Alma waves** = Iran-origin attack waves toward Israel; includes Iranian BM + Iranian UAV; excludes Hezbollah
- **JINSA counts** = global all-target totals, NOT Israel-specific
- **ISW/UAE MoD chart** = daily UAE breakdown (BM + CM + drones) Feb 28–Mar 24; fills `bm_uae` column
- **Cumulative BM at Israel anchors:** ~128 by Mar 4, ~300 by Mar 10, >290 by Mar 15, >450 by Mar 27
- **Phase I direct Israel BM (JINSA Mar5 PDF):** 73/57/28/20/9 per day (Days 1–5) — ⚠ preliminary, conflicts with ~128 anchor
- **Late March context:** Iran targets 6+ countries; Israel = 15–29% of total attacks; ~10–15 BM/day at Israel
- **Interception rate:** 92% aggregate (late March); ~50% cluster warheads through Mar 10
- **Global totals:** 1,556 BM + 3,670+ drones + 28 cruise missiles launched by Mar 24 (JINSA)
- **Source PDFs:** see `reports/` directory (JINSA 3/5 and 3/24 PDFs parsed directly)

### Phase I Data Conflict (partially resolved)
JINSA Mar5 PDF states 73+57+28+20+9 = **187 BM at Israel** (Days 1–5). BBC/IDF anchor = **~128**. The JINSA Mar5 global totals were revised down 20–37% by Mar24 final counts — Israel-specific likely also overcounted. Both values are documented; `isr_cumul=128` retained as primary anchor. Perplexity reading of 200/105/68/37/20 eliminated (2026-03-29) — was 2025 war "Rising Lion" column misread, not 2026 data.
