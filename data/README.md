# Iran War Data Directory

## Scope

All data tracks **Iranian ballistic missiles (BM) launched toward Israel** during the 2026 Iran–Israel war (Feb 28–present).

Supporting data from other targets (UAE, Kuwait, Bahrain, Iraq, Saudi Arabia) is stored only to derive the Israel-specific ceiling.

**Excluded from all tables:**
- Hezbollah rockets/missiles/UAVs (tracked separately by Alma — not in this dataset)
- Houthi (Yemen) strikes
- Iranian drone/UAV/Shahed launches (even Iran-origin)
- Iranian BM targeting Gulf states, Saudi Arabia, Iraq (stored in `sources/` for reference only)

---

## File Structure

```
data/
├── all_sources_daily.csv        ← ALL-SOURCES COMPARISON TABLE (one row per day, one column per source)
├── israel_daily_estimate.csv    ← CONSOLIDATED MODEL INPUT (clean best-estimate per day, with method column)
├── inventory.csv                ← Iranian BM/launcher stock snapshots
├── conflicts.md                 ← Unresolved source conflicts with resolution paths
├── metadata.json                ← Provenance, methodology, update log
│
├── sources/                     ← Raw per-source data
│   ├── registry.csv             ← All sources: URL, tier, type, access status
│   ├── jinsa/
│   │   ├── reports.csv          ← JINSA PDF index: URL, date, key claims
│   │   ├── global_daily.csv     ← Daily global BM: preliminary (Mar5 PDF) vs final (Mar24 PDF)
│   │   ├── country_splits.csv   ← Per-country daily BM (UAE, Bahrain, Kuwait, Iraq, Israel direct)
│   │   └── hits_daily.csv       ← Projectile hits at Israel per day (JINSA Chart 4)
│   ├── alma/
│   │   ├── reports.csv          ← Confirmed Alma daily report URLs
│   │   ├── waves_daily.csv      ← Daily waves + cumulative anchors
│   │   └── geographic.csv       ← Geographic distribution at key dates
│   ├── idf/
│   │   └── statements.csv       ← IDF official cumulative anchors + interception rates
│   ├── isw/
│   │   └── uae_daily.csv        ← UAE MoD daily BM/drone/CM Feb28–Mar24
│   ├── media/
│   │   ├── barrages.csv         ← Hebrew/English press barrage/siren counts
│   │   └── events.csv           ← Confirmed impact events with location + casualties
│   └── perplexity/
│       └── estimates.csv        ← Perplexity estimates by search round (accepted/rejected)
│
└── archive/
    └── pre_restructure_2026-03-28/   ← Snapshot of flat-file structure before reorganisation
```

---

## `all_sources_daily.csv` — Column Reference

One row per day. Each column comes from a specific source. No synthesised estimates.

### JINSA columns
*(Source: JINSA PDFs — see `sources/jinsa/`)*

| Column | What it is | Where it comes from |
|--------|-----------|---------------------|
| `jinsa_bm_global` | Total Iranian BMs fired **globally** (all targets) that day | JINSA Mar24 PDF Chart 1 (final counts). For Days 1–5 the Mar5 PDF gave preliminary figures revised down 6–59% in the final. |
| `jinsa_bm_israel` | BMs fired specifically **at Israel** that day, as stated by JINSA | Days 1–5: JINSA Mar5 PDF table (73/57/28/20/9) — **contested**, see below. Days 18–24 (Mar18–24): JINSA Mar24 PDF Chart 2 direct per-country readings (±2). Blank all other days — no JINSA direct Israel figure exists. |
| `jinsa_bm_uae` | BMs fired at **UAE** that day | ISW/UAE Ministry of Defense daily chart (Feb28–Mar24). Same source chain as JINSA. |
| `israel_bm_ceiling` | **Maximum** BMs Israel could have received that day | Derived: `jinsa_bm_global − jinsa_bm_uae`. Where other confirmed non-Israel allocations are known (Bahrain, Kuwait, Iraq), those are also subtracted to give a tighter ceiling (see notes column in `sources/jinsa/country_splits.csv`). Not a JINSA-stated figure — a mathematical upper bound. |

**Why `jinsa_bm_israel` is blank for most days:** JINSA published daily global totals for all 29 days but only broke out the Israel-specific count in two places: (1) the Mar5 PDF preliminary table for Days 1–5, and (2) Chart 2 in the Mar24 PDF for Mar18–24. There is no publicly available JINSA per-day Israel figure for Mar5–17 or Mar25–28.

**Phase I conflict (Days 1–5):** The `jinsa_bm_israel` values 73/57/28/20/9 = 187 total conflict with the BBC/IDF cumulative anchor of ~128 for the same 5 days. A separate Perplexity reading of the same JINSA PDF claims 200/105/68/37/20 = 430 total. All three readings are mutually incompatible. See `conflicts.md` CONFLICT-1 for full analysis.

---

### IDF/Official columns
*(Source: IDF statements via BBC Arabic, JINSA Mar11 PDF, INSS/FDD, Times of Israel — see `sources/idf/statements.csv`)*

| Column | What it is | Notes |
|--------|-----------|-------|
| `idf_bm_cumul` | **Cumulative** BMs launched at Israel since war start, as stated by IDF/official sources | Only populated at 4 anchor dates: Mar4 (~128), Mar10 (~300), Mar15 (>290), Mar27 (>450). Blank all other days — IDF did not publish a daily running total. |
| `idf_intercept_pct` | IDF-stated interception rate | 92% confirmed as a late-March aggregate (not a daily figure). Populated from Mar18 onward where IDF confirmed this rate. |

**Why `idf_bm_cumul` has so few values:** IDF released cumulative totals only at press moments, not daily. The Mar15 figure (>290) is a lower bound from INSS/FDD citing IDF, already exceeded by the Mar10 figure of ~300 — it is included for completeness but carries no new information.

---

### Alma columns
*(Source: Alma Research and Education Center daily reports — see `sources/alma/`)*

| Column | What it is | Notes |
|--------|-----------|-------|
| `alma_waves` | Daily count of **Iranian attack waves** toward Israel | Alma definition: one "wave" = a grouped launch event. Includes Iranian BMs **and** Iranian UAVs/drones — **not BM-only**. Excludes Hezbollah entirely. Confirmed from Alma's own bar-chart infographics and Statista (which mirrors Alma data). |
| `alma_waves_cumul` | Cumulative waves since war start | Populated only at confirmed Alma anchor dates: Mar14 (235), Mar19 (300), Mar21 (329), Mar24 (346), Mar26 (377). **Do not recompute by summing daily values** — a confirmed 7-wave discrepancy exists between the Mar21 and Mar24 anchors (see `conflicts.md` CONFLICT-4). |

**Alma waves ≠ BM count.** The Mar18–24 period shows a calibrated ratio of ~1.1 BMs per wave (derived from JINSA Chart 2 ÷ Alma waves for the same days). This ratio is used in `israel_daily_estimate.csv` to estimate BMs on days with no direct JINSA Israel reading.

---

### Perplexity columns
*(Source: Perplexity R15 full-war synthesis — see `sources/perplexity/estimates.csv`)*

| Column | What it is | Notes |
|--------|-----------|-------|
| `perplexity_min` | Perplexity lower bound for BMs at Israel that day | |
| `perplexity_max` | Perplexity upper bound | |
| `perplexity_est` | Perplexity central estimate | |

**What Perplexity R15 is:** A secondary synthesis estimate produced by querying Perplexity AI with the full war dataset as context. It is not a primary source. Its estimates for individual days are constrained by JINSA global counts, INSS/Walla cumulative figures, Alma/Statista wave counts, and Hebrew/English media descriptions.

**Reliability by period:**

| Days | Status | Reason |
|------|--------|--------|
| Feb28–Mar4 | Contested | Same Phase I conflict as `jinsa_bm_israel` above |
| Mar5–Mar9 | Partial | Internally inconsistent with Perplexity's own Phase I figures (see below) |
| Mar10 | Rejected | est=30 exceeds JINSA global=29 — physically impossible |
| Mar11–Mar16 | Rejected | Flawed anchor logic: treats INSS ">290 by Mar15" as approximately equal to IDF "~300 by Mar10", inferring near-zero BM increment over 6 days |
| Mar17 | Accepted | Within range; confirms Hebron fatal hit on Mar17 |
| Mar18–Mar19 | Confirmed | Exact match with JINSA Chart 2 direct readings |
| Mar20, Mar25–Mar27 | Accepted | Consistent with primary sources |
| Mar21–Mar23 | Rejected | Over-infers BM count from casualty totals; ignores cluster munition amplification |
| Mar24 | Partial | Slightly exceeds derived ceiling |
| Mar28 | Contested | Higher than IDF "small salvo" characterisation |

**Perplexity internal inconsistency (Phase I + Mar5–9):** Perplexity R15 gives Phase I total = 430 BMs at Israel and Mar5–9 total = 169 BMs, implying 599 cumulative by Mar9. Perplexity simultaneously states the cumulative by Mar10 is "~300." This is a 599 vs 300 contradiction within the same estimate set — the two blocks were computed against different anchor assumptions and never cross-checked. Full detail in `conflicts.md` CONFLICT-1.

---

### `cluster_pct` column

Percentage of BMs at Israel carrying **cluster warheads** (vs standard unitary warhead), sourced from FDD and Times of Israel/IDF statements.

| Value | Meaning | Source |
|-------|---------|--------|
| `50` | ~50% confirmed | FDD analysis + JINSA Mar11 PDF, covering Mar8–10 |
| `>50` | Majority (>50%) confirmed | Times of Israel: "majority of ballistic missiles at Israel had cluster bomb warheads", stated late March |
| blank | Unknown or not stated | |

Cluster warheads release submunitions over a wide area — a single BM can cause casualties at multiple locations. This is why Mar21 Arad (64 injured from 1–2 BMs) should not be used to infer a high BM count.

---

## `israel_daily_estimate.csv` — Column Reference

The consolidated model input. One best estimate per day with inline notes describing the estimation basis. No raw source detail.

| Column | Description |
|--------|-------------|
| `bm_il_est` | Best single estimate for BMs at Israel that day |
| `bm_il_min` | Lower bound (see estimation methods below) |
| `bm_il_max` | Upper bound (see estimation methods below) |
| `alma_waves` | Daily count of Iranian attack waves toward Israel (Alma). One wave = one grouped launch event. Includes Iranian BMs + Iranian UAVs/drones combined; **not BM-only**. Excludes Hezbollah. Used as proxy input via `est = waves × 1.11` (ratio calibrated from JINSA÷Alma Mar18–24). |
| `bm_il_cumul` | Running cumulative BM total at Israel (computed from `bm_il_est`). Cross-check against official IDF anchors: 128 by Mar4, ~300 by Mar10, >450 by Mar27. |
| `cluster_pct` | Cluster warhead % (`50` = ~50% confirmed Mar8–10; `>50` = majority confirmed Mar18+; blank = unknown) |
| `confidence` | `high` / `medium` / `low` — reflects data quality of underlying sources |
| `primary_source` | Key into `sources/registry.csv` |
| `notes` | Free-text description of the estimation method and data basis for that day |
| `flags` | `CONFLICT` = unresolved source conflict (see `conflicts.md`) |

**Estimation methods used (referenced in `notes` column):**

| Method | Days | Formula | Range |
|--------|------|---------|-------|
| `bbc_prop` | 1–4 | `est = JINSA_direct × 128/187` | min = JINSA × 115/187; max = JINSA direct |
| `bbc_residual` | 5 | `est = 128 − Σ(est days 1–4)` | min = est; max = JINSA direct day 5 |
| `anchor_prop` | 6–10 | `est = 150 × waves_i / Σwaves(6–10)` where 150 = 300−128−22 | min = est×0.80; max = est×1.20; Day 10 floor from FDD observed impact |
| `wave_ratio` | 12–17 | `est = alma_waves × 1.11` (calibrated Mar18–24) | min = est×0.75; max = est×1.25; observed floor retained where available |
| `jinsa_direct` | 11, 19–25 | JINSA stated per-country daily count | min = est−2; max = min(est+2, derived_ceiling) |
| `jinsa_derived` | 26 | `est = JINSA_global − Σ(confirmed non-Israel)` | min = JINSA text lower bound; max = derived ceiling |
| `media_count` | 28–29 | IDF statement + media siren/barrage count + JINSA global constraint | contextual min/max |
| `multi_source` | 18, 20, 27 | Weighted blend: JINSA direct w=3, Alma wave_ratio w=2, Perp accepted w=2, Perp accepted_partial w=1. `est = round(Σ(signal×weight)/Σ(weight))`, constrained to [observed_floor, derived_ceiling] | range = [min-of-sources, max-of-sources] ∩ [floor, ceiling] |

**Anchor consistency check (all three IDF anchors satisfied):**
- Cumul est Days 1–5 = **128** ✓ (BBC/IDF Mar 4 anchor)
- Cumul est Days 1–11 = **301 ≈ 300** ✓ (IDF Mar 10 anchor)
- Cumul est Days 1–28 = **501 > 450** ✓ (IDF Mar 27 anchor)

---

## Cumulative BM at Israel — Official Anchors

| Date | Value | Source | Scope |
|------|-------|--------|-------|
| Mar 4 | ~128 | BBC Arabic citing IDF | 5-day total Feb28–Mar4; possibly includes small non-BM fraction |
| Mar 10 | ~300 | IDF (via JINSA Mar11 PDF) | BM-only confirmed |
| Mar 15 | >290 | INSS/FDD | BM-only; non-binding lower bound (already exceeded by Mar10 value) |
| Mar 27 | >450 | Times of Israel citing IDF | BM at home front |

---

## Alma Wave Cumulative Anchors

| Date | Cumulative waves | Source report |
|------|-----------------|---------------|
| Mar 14 | 235 | Alma Mar13–14 weekend infographic |
| Mar 19 | 300 | Alma Mar20 16:00 report |
| Mar 21 | 329 | Alma Mar22 18:00 report |
| Mar 24 | 346 | Alma Mar25 18:00 report |
| Mar 26 | 377 | Alma Mar26 report |

**Do not chain daily values between anchors** — a confirmed 7-wave discrepancy between the Mar21 (329) and Mar24 (346) anchors means the intermediate daily values do not sum correctly. Use stated anchors only.

---

## Data Quality by Period

| Period | `jinsa_bm_israel` | `israel_bm_ceiling` | `alma_waves` | `idf_bm_cumul` |
|--------|------------------|---------------------|-------------|----------------|
| Feb28–Mar4 | ✓ direct (contested) | ✓ | ✓ | Mar4: 128 |
| Mar5–Mar10 | — | ✓ | ✓ | Mar10: 300 |
| Mar11–Mar17 | — | ✓ | ✓ | Mar15: >290 |
| Mar18–Mar24 | ✓ JINSA Chart 2 | ✓ | ✓ | — |
| Mar25–Mar26 | — | partial | ✓ | — |
| Mar27–Mar28 | — | partial | — | Mar27: >450 |

---

## Open Conflicts

See `conflicts.md` for full detail. Summary:

| ID | Issue | Status |
|----|-------|--------|
| CONFLICT-1 | Phase I Israel BM count: 3 incompatible readings (73/128/200-series) | **Unresolved** — requires reading JINSA Mar5 PDF directly |
| CONFLICT-2 | Hebron fatal hit date: Mar17 vs Mar23 | **Resolved** — confirmed Mar17 (R15 co-citation with Alma Mar17 report) |
| CONFLICT-3 | BBC ~128 scope: all-BM vs MRBM-only | **Open question** |
| CONFLICT-4 | Alma 7-wave discrepancy Mar21→Mar24 | **Accepted as real** — use stated anchors only |
