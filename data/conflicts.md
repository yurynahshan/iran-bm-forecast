# Data Conflicts and Open Questions

Last updated: 2026-03-28

Rows in `strikes_israel_daily.csv` with a `CONFLICT` or `DATE_DISPUTE` flag are described here. This file is the single place to track unresolved source contradictions.

---

## CONFLICT-1: Phase I Israel BM Count (Days 1–5, Feb 28–Mar 4)

**Status:** Unresolved — three incompatible readings

**The three readings:**

| Reading | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 | 5-day sum | Source |
|---|---|---|---|---|---|---|---|
| A (JINSA Mar5 PDF — old) | 73 | 57 | 28 | 20 | 9 | **187** | JINSA_MAR5_PDF (Perplexity R7) |
| B (BBC/IDF anchor) | — | — | — | — | — | **~128** | BBC_ARABIC citing IDF |
| C (JINSA Mar5 PDF — new) | 200 | 105 | 68 | 37 | 20 | **430** | JINSA_MAR5_PDF (Perplexity R14) |

**Why these cannot all be correct:**
- Readings A and C are both claimed to come from the same JINSA Mar5 PDF "against Israel" column. One must be a misread.
- Reading C (sum=430 by Mar4) makes the Mar10 cumul=300 anchor physically impossible (you cannot have 430 by Day 5 and only 300 by Day 10).
- Reading A (sum=187) conflicts with BBC/IDF anchor of 128 — JINSA Mar5 preliminary counts are known to overcount (Day 3: 186→138 global; Day 4: 108→68 global — 35-59% overcount). Israel-specific similarly overcounted.
- BBC/IDF 128 is a primary source statement, not a chart reading.

**Supporting evidence for higher counts (Reading C direction):**
- CSIS: "On the first day of the war, Iran launched about 438 ballistic missiles, roughly half against Israel and half at Gulf targets" → ~219 at Israel on Day 1.
- CAPSS/CHPM cites ">300 MRBMs at Israel by Mar 10." If "MRBMs" is the correct scope for the 300 figure, then total BMs at Israel by Mar10 could be much higher.
- derived_max on Day 1 = 301 (global 438 - UAE 137). Reading C (200) fits within this constraint.

**Supporting evidence for lower counts (Reading B direction):**
- BBC Arabic cites IDF/defense ministry directly for the 128 figure — primary attribution.
- Mar10 cumul=300 from IDF (via JINSA Mar11 PDF) is explicitly "BM launched at Israel." If already 430 by Mar4, the total by Mar10 would be 550+, not 300.
- Perplexity has a documented history of misreading this specific JINSA PDF (e.g., the 428 global-as-Israel error).

**Current data treatment:**
- `strikes_israel_daily.csv` Days 1–5: est = BBC-proportioned values (50/39/19/14/6); max = JINSA Mar5 reading A (73/57/28/20/9).
- `sources/perplexity/estimates.csv`: Reading C documented with `accepted=contested`.
- **Do not update primary data until verified against the actual JINSA Mar5 PDF.**

**Resolution path:** Read the JINSA Mar5 PDF directly to determine whether it contains one "Israel" column or two (one labeled "against Israel" and one global). URL: https://jinsa.org/wp-content/uploads/2026/03/Irans-Firepower-2026-03-05-1.pdf

**Additional evidence from R15 (new internal inconsistency):** Perplexity R15 provides both Phase I estimates (200/105/68/37/20 = 430 cumul by Mar4) AND independent Mar5–9 estimates (35+22+40+29+43 = 169), giving a cumulative of 599 by Mar9. Perplexity simultaneously states "anchors put total at ~300 by Mar10." This is a 599 vs 300 contradiction *within the same estimate set*. This indicates Perplexity's Mar5–9 estimates were computed against the BBC 128 anchor (not their own Phase I total of 430) — the two blocks were never cross-checked. This internal inconsistency further undermines confidence in the Phase I Reading C.

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
