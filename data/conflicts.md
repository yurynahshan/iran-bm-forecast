# Data Conflicts and Open Questions

Last updated: 2026-03-29

Rows in `strikes_israel_daily.csv` with a `CONFLICT` or `DATE_DISPUTE` flag are described here. This file is the single place to track unresolved source contradictions.

---

## CONFLICT-1: Phase I Israel BM Count (Days 1–5, Feb 28–Mar 4)

**Status:** Partially resolved — reduced to two incompatible readings (Reading C eliminated)

**The three readings:**

| Reading | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | 5-day sum | Source | Status |
|---|---|---|---|---|---|---|---|---|
| A (JINSA Mar5 PDF) | 73 | 57 | 28 | 20 | 9 | **187** | JINSA_MAR5_PDF (Perplexity R7) | **Confirmed correct column** |
| B (BBC/IDF anchor) | — | — | — | — | — | **~128** | BBC_ARABIC citing IDF | **Primary source** |
| C (Perplexity R14 misread) | 200 | 105 | 68 | 37 | 20 | **430** | JINSA_MAR5_PDF (Perplexity R14) | **ELIMINATED — column misread** |

**Reading C eliminated (2026-03-29):** The JINSA Mar5 PDF chart contains two wars side by side:
- Column 1: "Rising Lion" = **2025 war**, fire against Israel only (Day 2=200, Day 3=105, Day 4=68, Day 5=37)
- Column 2: "Epic Fury & Roaring Lion: Against Israel" = **2026 war** (Day 1=73, Day 2=57, Day 3=28, Day 4=20, Day 5=9)
- Column 3: "Epic Fury & Roaring Lion: Total Fire Against All Targets" (Day 1=428, Day 2=170, Day 3=186, Day 4=108, Day 5=42)

Perplexity R14 read the **2025 Rising Lion column** (200/105/68/37) and reported it as 2026 Israel-specific data. This was a table column misread — not new information. Reading C is eliminated.

**Remaining conflict:** JINSA Mar5 PDF "Against Israel" column (187 total) vs BBC/IDF anchor (128 total). These are genuinely incompatible.

**Why 187 is likely overcounted:**
- The JINSA Mar5 PDF global totals were later revised down significantly in the Mar24 final PDF (Day 3: 186→138, Day 4: 108→68 — 28–37% overcount). The Mar5 PDF was a preliminary and the Israel-specific column likely carries the same overcount bias.
- The "Total Against All Targets" column in this chart (428/170/186/108/42) differs from our Mar24 final global totals (438/161/138/68/39) — confirming Mar5 is preliminary.

**Supporting evidence for higher counts:**
- CSIS: "roughly half" of 438 at Israel on Day 1 → ~219. The derived_max=301 (global 438 − UAE 137) is consistent.
- Note: CSIS may itself be using the Mar5 preliminary data or the 2025 Rising Lion column.

**Supporting evidence for BBC 128:**
- BBC Arabic cites IDF/defense ministry directly — primary attribution, not a chart reading.
- Mar10 cumul=300 (IDF): if 187 already by Mar4, the Mar5–10 increment would be only 113 BM — possible but tight.

**Current data treatment:**
- `israel_daily_estimate.csv` Days 1–5: est = BBC-proportioned values (50/39/19/14/6); max = JINSA Mar5 column A (73/57/28/20/9).
- `sources/perplexity/estimates.csv`: Reading C rejection reason updated to `COLUMN_MISREAD_2025_WAR`.
- **Do not update primary data until the 187 vs 128 conflict is resolved.**

**Resolution path:** The chart is now confirmed. The remaining question is whether BBC/IDF 128 is a precise count or a rounded/partial figure. If IDF separately stated 90+60+20+20+... as Phase I per-day counts (per IDF/ToI in `sources/idf/statements.csv`), those sum to ~210 — also higher than 128. CONFLICT-3 (scope of BBC 128) is relevant here.

**Additional evidence from R15 (internal inconsistency):** Perplexity R15 Phase I estimates (200/105/68/37/20 = 430) were the 2025 column misread. R15 Mar5–9 estimates (35+22+40+29+43 = 169) were computed against the BBC 128 anchor. The apparent 599 vs 300 contradiction was entirely caused by the column misread — it is no longer relevant now that Reading C is eliminated.

---

## CONFLICT-2: Hebron Fatal Hit Date (Mar 17 vs Mar 23)

**Status:** RESOLVED — **March 17**

**The event:** "At least 3 women killed near Hebron/West Bank by Iranian missile strike."

**Resolution:** Perplexity R15 cited the ToI article (https://www.timesofisrael.com/liveblog_entry/at-least-2-women-killed-in-iranian-missile-attack-near-hebron-palestinian-red-crescent/) alongside the Alma March 17 daily report (https://israel-alma.org/daily-report-second-iran-war-march-17-2026-1600/) in the same row for March 17. This co-citation with the contemporaneous Alma Mar17 report confirms the date is **March 17**.

A second ToI article (https://www.timesofisrael.com/deadly-missile-strike-in-west-bank-highlights-lack-of-protection-for-palestinians/) is a follow-up piece that may have been published later, causing the Mar23 misattribution in R12.

**Data changes from resolution:**
- `strikes_israel_daily.csv`: `DATE_DISPUTE` flag removed from Mar17 and Mar23.
- `sources/media/barrages.csv`: Mar17 and Mar23 rows updated.
- The 3 killed on Mar17 are confirmed; Mar23 casualty note corrected.

---

## CONFLICT-3: BBC 128 Anchor — Scope Ambiguity

**Status:** Open question (may be related to CONFLICT-1)

**The question:** Does BBC Arabic's "~128 BM from Iran toward Israel by Mar 4" refer to:
- (a) All ballistic missiles of any range, OR
- (b) Only medium-range ballistic missiles (MRBMs), OR
- (c) Missiles that reached/impacted Israeli territory (not all launched)

**Why this matters:** CAPSS/CHPM cites ">300 MRBMs at Israel by Mar 10" with the explicit qualifier "medium-range." If the BBC 128 figure is also MRBM-only, then total BMs at Israel in the first 5 days could be higher, potentially reconciling with the CSIS "roughly half" figure.

**Current data treatment:** 128 retained as the primary cumulative anchor for `bm_il_cumul` at Mar4. Flagged as potentially MRBM-specific in metadata.

---

## CONFLICT-4: Alma 7-Wave Anchor Discrepancy (Mar 21–Mar 24)

**Status:** Known, documented, accepted as real

**The discrepancy:**
- Mar21 anchor: cumul=329 (confirmed via Alma Mar22 18:00 report)
- Mar24 anchor: cumul=346 (confirmed via Alma Mar25 18:00 report)
- Chain from Mar21: 329 + 8(Mar22) + 7(Mar23) + 9(Mar24) = **353 ≠ 346**
- Discrepancy = 7 waves

**Resolution:** Confirmed as real per Alma OSINT community discussions. Both stated anchors (329 and 346) are authoritative. The intermediate daily counts (Mar22=8, Mar23=7) may be slightly off in one direction. **Use stated anchors only — do not chain intermediate cumuls.**

---

## FLAG REFERENCE

| Flag | Meaning | Affected rows |
|---|---|---|
| `CONFLICT` | Unresolved source conflict for this day's estimate | Days 1–5 (Phase I) |
| `DATE_DISPUTE` | Event date uncertain across sources | Mar 17, Mar 23 |
| `PARTIAL` | Data is partial or incomplete | (used in data_type column, not flags) |
| `PERP_WARN` | (reserved — not yet used in consolidated table; see perplexity/estimates.csv for rejected estimates) | — |
