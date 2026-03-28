# Data Directory

## Scope

**All data = Iranian ballistic missiles (BM) targeting Israel.**
Supporting data from other targets (UAE, Kuwait, Bahrain, Iraq) is stored to enable estimation of the Israel-specific series.

Excluded from all tables:
- Hezbollah rockets/missiles/UAVs
- Iraqi militia or Houthi strikes
- Iranian Shahed/drone/UAV launches (even Iran-origin)

---

## File Structure

```
data/
├── strikes_israel_daily.csv   ← PRIMARY model input
├── global_splits_daily.csv    ← JINSA global totals + per-country splits
├── alma_proxy.csv             ← Alma wave series (continuous proxy)
├── inventory.csv              ← Iranian BM/launcher inventory snapshots
├── events.csv                 ← Confirmed specific strike events
├── sources.csv                ← Source registry with confidence tiers
├── metadata.json              ← Provenance, update log, resolved discrepancies
└── archive/
    └── strikes_daily_v1.csv  ← Pre-restructure combined table
```

---

## Table Descriptions

### `strikes_israel_daily.csv` — PRIMARY MODEL INPUT
One row per day (Feb 28 – Mar 28). All columns are Israel-specific.

| Column | Description |
|--------|-------------|
| `bm_il_min/max` | Range of BM launched toward Israel that day |
| `bm_il_est` | Best single estimate |
| `bm_il_hits` | Confirmed impacts (not intercepted) |
| `bm_il_cumul` | Cumulative anchor — populated ONLY at confirmed anchor dates |
| `intercept_pct` | Interception rate (92% confirmed for late March aggregate) |
| `cluster_pct` | % of BM with cluster warheads (~50% through Mar 10) |
| `data_type` | **See data type taxonomy below** |

**`data_type` taxonomy:**
- `observed` — source directly states per-day BM count at Israel
- `observed_partial` — some observed data (e.g. hits only, or min count from casualties)
- `derived` — calculated: `bm_global − UAE − Bahrain − Kuwait − Iraq`
- `proxy_est` — estimated from Alma wave series or model
- `anchor_only` — only a cumulative anchor exists; no daily breakdown
- `gap` — no data of any kind

---

### `global_splits_daily.csv` — JINSA GLOBAL + TARGET SPLITS
Supports derivation of Israel-specific estimates. JINSA counts are global (all targets).

| Column | Description |
|--------|-------------|
| `bm_global` | Total Iranian BM launched globally that day (JINSA) |
| `bm_uae/bahrain/kuwait/iraq` | Per-country BM counts where stated |
| `bm_non_israel` | Sum of confirmed non-Israel targets |
| `bm_il_derived_min/max` | `bm_global − bm_non_israel` (bounds on Israel share) |
| `israel_all_attacks_share_pct` | Israel's share of ALL Iranian attacks (BM+drones), from JINSA |

**Coverage:** Feb 28 (global=428), Mar 22–27 (daily JINSA PDFs).

---

### `alma_proxy.csv` — CONTINUOUS PROXY SERIES
Alma-definition Iranian attack waves toward Israel. Includes both Iranian BM and Iranian UAV. Excludes Hezbollah.

| Column | Description |
|--------|-------------|
| `alma_waves_daily` | Attack waves that day |
| `alma_waves_cumul` | Cumulative waves since Feb 28 |
| `data_quality` | `direct` / `statista` / `derived` / `gap` |

**Coverage:** Continuous Feb 28–Mar 26 (with gap Mar 2, Mar 20-21 daily unknown, Mar 27-28).
**Statista fills:** Mar 12–14 filled from Statista (confirmed = Alma source from Mar 11+).

**Cumulative integrity note:** Running sum 300(Mar19)+29(Mar20-21)+8(Mar22)+7(Mar23)+9(Mar24)=353 ≠ 346(stated Mar25). 7-wave discrepancy unresolved. **Use stated anchor values only — do not recompute running cumulative between anchors.**

---

### `inventory.csv` — BM INVENTORY SNAPSHOTS
Snapshot rows by (date × weapon_type).

| Weapon type | Key figures |
|-------------|-------------|
| BM_all | Pre-war: 2500; Launched globally by Mar 26: 1625; Remaining: 500-700 |
| BM_launchers | Pre-war: ~400; 75%+ neutralized by Mar 5-16 |
| MRBM | Pre-war: ~2000; 47-73% lost by Mar 5 |
| SRBM | Pre-war: 6000-8000; 23-52% lost by Mar 5 |

---

### `events.csv` — CONFIRMED STRIKE EVENTS
One row per confirmed specific impact event (location, casualties, weapon type).
Scope: Iran BM impacts in Israel only.

---

## BM at Israel — Cumulative Anchors

| Date | Cumulative | Source | Scope |
|------|-----------|--------|-------|
| Mar 4 | ~128 | BBC Arabic / IDF | 5-day total Feb28-Mar4; may include small non-BM |
| Mar 10 | ~300 | IDF (via JINSA 3/11 PDF) | **BM-only confirmed** |
| Mar 15 | >290 | INSS/FDD | **BM-only confirmed** |
| Mar 27 | >400 | IDF / JNS | BM at home front |

Note: Mar 10 (~300) and Mar 15 (>290) are consistent — IDF rounded ~290 to ~300 in the Mar 10 statement.

### Phase I Direct Israel BM Series (JINSA Mar 5 PDF — preliminary)

The JINSA Mar 5 PDF ("Iran's Missile Firepower Has Almost Run Out") provides the **only direct per-day Israel BM counts for Phase I**, from a table comparing 2025 and 2026 wars:

| Day | Date | JINSA Mar5 (Israel) | JINSA Mar5 (Global) | Mar24 Final (Global) |
|-----|------|---------------------|---------------------|----------------------|
| 1 | Feb 28 | **73** | 428 | 438 |
| 2 | Mar 1 | **57** | 170 | 161 |
| 3 | Mar 2 | **28** | 186 | 138 |
| 4 | Mar 3 | **20** | 108 | 68 |
| 5 | Mar 4 | **9** | 42 | 39 |
| **Total** | | **187** | **934** | **834** |

**⚠ Critical conflict:** JINSA Mar5 5-day Israel total = **187** vs BBC Arabic/IDF anchor = **~128**. Discrepancy = 59 BMs.

**Resolution:** The Mar5 global counts are systematically higher than the Mar24 final counts (Day 3: +35%; Day 4: +59%), confirming these were preliminary figures later revised downward. The Israel-specific numbers are treated as upper bounds; the BBC/IDF anchor (~128) is retained as the primary cumulative constraint. The daily JINSA Mar5 values are used as `observed` (best available per-day data) with ranges reflecting the overcount risk.

### Cross-check: Gulf totals as model constraint

- **551 projectiles** at Israel + Gulf 4 by **Mar 4** (BBC Arabic/IDF) — ⚠ likely includes drones, not BM-only
  - Israel BM share = ~128 → remaining ~423 at Gulf (mixed BM+drone)
- **605 BM** at Gulf 4 in **Feb 28–Mar 10** (CAPSS/CHPM citing Reuters)
  - Combined with ~300 at Israel = ~905 BM at these 5 targets in 10 days
  - Global through Mar 10 = ~1,103 BM → ~198 BM for all other targets (Saudi/Iraq/Jordan/etc.) in first 10 days

---

## Data Coverage by Period

| Period | Alma waves | Israel BM (daily) | Global BM | Target splits | Israel hits |
|--------|-----------|-------------------|-----------|---------------|-------------|
| Feb 28–Mar 4 | ✓ complete | ✓ **observed** JINSA Mar5 (73/57/28/20/9) ⚠ conflicts with ~128 anchor | ✓ Chart 1 | Gulf agg: 423 BM (est) | ✓ Chart 4 |
| Mar 5–Mar 10 | ✓ complete | **anchor only** (~300 by Mar 10) | ✓ Chart 1 | Gulf agg: 605 BM Feb28-Mar10 | ✓ Chart 4 |
| Mar 11–Mar 14 | ✓ (direct+Statista) | **gap** | ✓ Chart 1 | — | ✓ Chart 4 |
| Mar 15–Mar 17 | ✓ complete | **anchor only** (>290 by Mar 15) | ✓ Chart 1 | — | ✓ Chart 4 |
| Mar 18–Mar 19 | ✓ complete | ✓ **observed** Chart 2 (~15, ~18) | ✓ Chart 1 | — | ✓ Chart 4 |
| Mar 20–Mar 21 | combined only | ✓ **observed** Chart 2 (~12, ~8) | ✓ Chart 1 | — | ✓ Chart 4 |
| Mar 22–Mar 26 | mostly ✓ | ✓ **observed** Chart 2 + JINSA | ✓ daily | ✓ Mar 22-24; Jordan=5 Mar 25 | ✓ Chart 4 |
| Mar 27–Mar 28 | gap | **anchor** >400 by Mar 27 | Mar 27 partial | Kuwait=4, Saudi=6 Mar 27 | — |

**Data completeness verdict:** All publicly available sources have been exhausted. No per-day Israel BM series exists for Mar 1–17 in open sources. Remaining gaps require interpolation between cumulative anchors. — |

### Notes on Chart Sources (JINSA_MAR24_PDF)
Four charts from the JINSA Mar 24 2026 report provide systematic coverage:
- **Chart 1** ("Iranian Missiles Launched Per Day"): Global daily BM for all days Feb 28–Mar 24. Total=1556 BM, 108 global impacts.
- **Chart 2** ("Iranian Missiles Launched During the Past Week"): Absolute BM per country, stacked bar, Mar 18–24. Direct Israel BM readings used as `observed` data.
- **Chart 3** ("Targets of Iranian Attacks"): % share of ALL attack types (BM+drones) per country, Feb 28–Mar 24. Used for `israel_all_attacks_share_pct` in `global_splits_daily.csv`. **Do not apply directly to BM-only derivation** — drone volume dilutes Israel% especially in late March when Saudi Arabia/Gulf drone attacks dominate.
- **Chart 4** ("Number of Iranian Projectile Hits"): All-projectile hits (BM+drones+cruise) per country per day. Used as `bm_il_hits` notes in `strikes_israel_daily.csv`. **Caveat**: includes drone hits at Israel, not BM-only; mark confidence accordingly.

---

## Source Confidence Tiers

| Tier | Type | Sources |
|------|------|---------|
| 1 | Statistical orgs | JINSA, FDD, INSS, ISW, ACLED |
| 2 | Official gov/military | IDF, Gov.il, Iran Watch |
| 3 | Research + Israeli media | Alma, JNS, Times of Israel, Walla, FPRI |
| 4 | International wire | Reuters, BBC Arabic |
| 5 | 3rd country media | WaPo, WSJ, Guardian, NYPost, CNN, Asharq |
| 6 | Aggregated/OSINT | Hebrew Wikipedia, Arabic Wikipedia, Wikipedia EN, Statista |

---

## Key Contextual Finding (Late March)

By late March, Iran is targeting 6+ countries simultaneously. Israel receives ~10–15 BM/day but represents only **15–29% of total Iranian attack events**. Saudi Arabia is the largest attack-event target by count (mostly drones). Gulf states (Kuwait, Bahrain, UAE) + Iraq receive significant BM volumes. This multi-front distribution is critical context for interpreting the Israel-specific daily rate and model parameters.
