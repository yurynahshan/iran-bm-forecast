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
| `strikes_israel_daily.csv` | Israel-specific BM data, Feb 28–Mar 28 | **Direct model input** (`L_t`) |
| `alma_proxy.csv` | Alma wave series — continuous Iran→Israel proxy | Proxy for `L_t` where direct data is missing |
| `global_splits_daily.csv` | JINSA global totals + UAE/Kuwait/Bahrain/Iraq splits | Supports derivation of Israel estimates |
| `inventory.csv` | BM/launcher stock snapshots by weapon type | Context for capacity constraints |
| `events.csv` | Confirmed specific impact events with location/casualties | Qualitative validation |

### `data_type` Column (`strikes_israel_daily.csv`)
Every row is tagged with its epistemic status:
- `observed` — source directly states per-day BM count at Israel
- `observed_partial` — confirmed data but incomplete (e.g. hits only, or minimum from casualties)
- `derived` — calculated from `bm_global − UAE − Bahrain − Kuwait − Iraq`
- `proxy_est` — estimated from Alma waves or model
- `anchor_only` — only a cumulative total exists; no daily breakdown
- `gap` — no data

### Key Data Facts
- **War start:** Feb 28, 2026 (Day 1)
- **Phases:** I = Days 1–4 (saturation), II = Days 5–7 (rapid collapse), III = Day 8+ (stochastic)
- **Alma waves** = Iran-origin attack waves toward Israel; includes Iranian BM + Iranian UAV; excludes Hezbollah
- **JINSA counts** = global all-target totals, NOT Israel-specific
- **ISW/UAE MoD chart** = daily UAE breakdown (BM + CM + drones) Feb 28–Mar 24; fills `bm_uae` column
- **Cumulative BM at Israel anchors:** ~128 by Mar 4, ~300 by Mar 10, >290 by Mar 15, >400 by Mar 27
- **Phase I direct Israel BM (JINSA Mar5 PDF):** 73/57/28/20/9 per day (Days 1–5) — ⚠ preliminary, conflicts with ~128 anchor
- **Late March context:** Iran targets 6+ countries; Israel = 15–29% of total attacks; ~10–15 BM/day at Israel
- **Interception rate:** 92% aggregate (late March); ~50% cluster warheads through Mar 10
- **Global totals:** 1,556 BM + 3,670+ drones + 28 cruise missiles launched by Mar 24 (JINSA)
- **Source PDFs:** see `reports/` directory (JINSA 3/5 and 3/24 PDFs parsed directly)

### Phase I Data Conflict (unresolved)
JINSA Mar5 PDF states 73+57+28+20+9 = **187 BM at Israel** (Days 1–5). BBC/IDF anchor = **~128**. The JINSA Mar5 global totals were revised down 20–37% by Mar24 final counts — Israel-specific likely also overcounted. Both values are documented; `bm_il_cumul=128` retained as primary anchor.
