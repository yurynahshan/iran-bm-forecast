# Iran BM Capabilities — Analytical Conclusions

**Project:** Iran–Israel War 2026 — Iranian Ballistic Missile Strike Analysis
**Last updated:** 2026-03-29
**Assessment period:** Feb 28 – Mar 28, 2026 (Days 1–29, full first month)
**Model version:** Decoupled calibration — Poisson process from Phase IIIb data; α from Phase IIIb data (Model O) or launcher intelligence (Model C)

---

## 1. Executive Summary

Iran's ballistic missile campaign against Israel has undergone a fundamental transformation in its first month. It opened with a brief, high-intensity Saturation phase (Days 1–4, over 100 BMs/day globally, 14–50 BMs/day at Israel) then collapsed rapidly into a persistent, low-rate stochastic regime (~10–12 BMs/day) that has been stable since mid-March.

The statistical model used for April forecasting is a **Poisson process with exponential decay**. The formal best-fit model on Transition + Attrition data is a piecewise Poisson (structural break at Day 14); the single exponential is within ΔAIC < 0.3 and is retained for tractable scenario forecasting. The Poisson-with-decay pattern is consistent with a **distributed system undergoing gradual attrition** — this document explores what that interpretation implies operationally if correct.

The model uses a **decoupled calibration approach**: the Poisson process structure is calibrated from Attrition phase launch data, while the decay rate α is derived separately for each scenario. The two models bracket the plausible range: the Observable model derives α from the strike data itself (after noise removal); the Conservative model derives α independently from published intelligence on launcher counts. Reality is expected to lie between them.

**Key findings:**
1. Iran's BM campaign has shifted from a **strategic coordinated offensive** to what appears to be a **distributed attrition campaign**, where the statistical pattern is consistent with launcher nodes operating with high autonomy and gradual capacity erosion.
2. Iranian BM launches toward Israel exhibit **statistical independence** consistent with autonomous launcher operation — the absence of detectable coordination or central scheduling is the simplest explanation, though this structural interpretation is a hypothesis rather than a proven fact.
3. The capabilities of those autonomous units **decrease slowly over time** at a constant fractional rate of 0.83–2.0% per day. The Observable model (2.0%/day) is derived from the strike data after noise removal; the Conservative model (0.83%/day) is derived independently from published intelligence on total launcher counts. Reality is expected between the two.

---

## 2. Campaign Phases

Iran's BM campaign against Israel has passed through four operationally distinct phases. It opened with a brief **Saturation** period (Feb 28 – Mar 3, ~35 BMs/day at Israel), followed by a rapid **Collapse** (Mar 4–9) as Iran's first-echelon infrastructure was degraded. A brief **Transition** period (Mar 10–12) marks the tail of that collapse, when the rate was still elevated and declining. Since Mar 13 the campaign has been in a stable **Attrition** phase (~10–12 BMs/day) — this is the regime the statistical model is trained on.

Full phase characterisation — scale, statistical properties, and detection methodology — is in [methodology.md](methodology.md).

---

## 3. What the Poisson Model Reveals

### 3.0 The Poisson model — background and fit

The **Poisson process** is one of the most fundamental models in probability. It describes situations where events occur randomly, independently, and at a constant average rate. Classic examples include phone calls arriving at a switchboard, radioactive particle emissions from a source, or equipment failures across a large fleet. The defining property is that each event happens without regard to when the last one occurred — no memory, no coordination, no pattern.

When the underlying rate is not constant but **declining over time**, the model is extended to a **Poisson process with exponential decay**: the average rate μ_t = μ₀ · e^(−αt) falls geometrically each day. This specific combination — random independent events with a decaying rate — is the mathematical fingerprint of a **depleting population under constant fractional attrition**. The textbook analogue is radioactive decay: a large number of atoms each independently decaying with a fixed daily probability, producing a random number of emissions that follows Poisson statistics at a rate that declines smoothly as the source depletes.

The Poisson-exponential pattern is consistent with the following physical structure:
- **Many independent nodes** (launchers distributed across Iran) each acting autonomously
- **Each node has a fixed daily probability of being destroyed** or rendered non-operational by Israeli strikes
- **Each surviving node fires randomly** when local conditions allow — no central coordination

This is the most parsimonious explanation of the observed pattern, not a uniquely proven mechanism. Alternative explanations — command pacing at a slow tempo, logistics-driven variability, or mixed command structures — would need to generate a similar statistical signature to be ruled out.

The Poisson fit was validated through overdispersion tests, autocorrelation tests, formal model comparison (Negative Binomial rejected), and rolling in-sample Z-score checks — all within normal bounds. Full diagnostics are in [methodology.md](methodology.md).

**Primary operational interpretation:** Iran's Attrition phase launch pattern is most simply explained by a distributed network of units each operating on its own cycle, collectively producing a smoothly declining random output. The rate of decline is a candidate measure of Israeli strike effectiveness — subject to the caveats above.

### 3.1 Each launch is statistically independent

**Confirmed by:** Zero autocorrelation in daily residuals (statistical independence test passed).

**Military meaning:** The most parsimonious interpretation is that each launcher node makes its own firing decision based on local conditions — missile availability, targeting solution, crew readiness, suppression status — with no central daily quota and no coordinated scheduling across sites. Under this model, destroying one node would not signal or suppress others. At $n = 19$ days of data, alternative coordination models (command pacing, mixed processes) cannot be statistically ruled out; this is a structural hypothesis consistent with the data, not a uniquely proven mechanism.

**Inconsistent with:**
- Central command throttling output up or down day-to-day
- Planned pause-and-surge cycles (no periodicity detected)
- Strategic accumulation for large salvos (the Mar 19=19 and Mar 25=15 peaks are consistent with Poisson variability under a slowly varying mean; at n=19 this cannot be proven conclusively)

### 3.2 The stockpile is not the binding constraint

**Evidence:** If Iran were drawing from a nearly exhausted missile inventory, firing more today would leave fewer for tomorrow → negative day-to-day autocorrelation. None detected.

**Military meaning:** The absence of negative autocorrelation is consistent with Iran's usable missile stockpile being large enough that daily depletion is operationally negligible. The most parsimonious explanation is that the binding constraint is **operational launcher capacity** — launchers that are ready, undetected, and loaded — rather than total missile inventory. This inference is indirect; stockpile effects could be masked if replenishment keeps pace with consumption, or if the stockpile is large relative to daily draw-down.

### 3.3 The exponential decay is launcher attrition, not stockpile exhaustion

**Physical interpretation:** Each operational launcher has a daily probability of being destroyed, suppressed, or rendered non-operational by Israeli strikes. If that probability is roughly constant and each launcher is independent, the expected number of operational launchers — and therefore the expected daily launch rate — follows exponential decay. This is mathematically identical to radioactive decay: a large number of independent emitters, each decaying at a fixed rate, producing a smoothly declining total output.

**Two models, two scenarios:**

The models use a **decoupled calibration approach**: the Poisson statistical structure is calibrated from Phase IIIb launch data (Days 14–29), while the decay rate α is fixed externally for each model rather than jointly optimised with μ₀. This stabilises forecasts — fixing α means individual observation noise cannot distort the decay estimate. Exact parameter derivations are in [methodology.md](methodology.md).

**Observable model (O) — "Iran degrades":** α is derived empirically from the Phase IIIb launch data using weighted log-linear regression on weekly aggregates. Applied to three windows (Days 14–20, 21–27, 28–29), this gives α = 0.020/day. This is the *observed* decay rate — it reflects all factors currently suppressing Iran's output: physical launcher destruction, crew attrition, logistics degradation, and coordination disruption. **Model O is a projection of current conditions forward**: it holds as long as these underlying parameters do not materially change. Result: a **half-life of 35 days** — Iran retains only ~39% of its current capacity by end of April.

**Conservative model (C) — "Iran sustains":** α is derived independently from published intelligence on Iran's *total* launcher fleet: ~160 operational at Day 12 (IDF via Algemeiner) declining to ~140 at Day 28 (ISW/IDF). This total-fleet attrition rate (0.0083/day) is slower than what the data implies, because intelligence counts only physically destroyed launchers — whereas the observed launch rate is further suppressed by operational factors: crew availability, logistics degradation, coordination disruption, and launchers that remain physically intact but operationally unavailable (e.g. stuck in tunnels, awaiting resupply). **Model C can materialise if Iran actively resolves these operational constraints** — improving logistics throughput, restoring crew readiness, or bringing currently dormant launchers back into rotation. Under that scenario, Iran's effective firing rate would converge toward the physical launcher count, and Model C's slower decay would reflect reality. This gives a **half-life of 83 days** — Iran retains ~68% of its current launch capacity through end of April.

> **"Observable"** = empirical projection of current conditions; holds unless parameters change. **"Conservative"** = physical launcher attrition floor; can materialise if Iran resolves operational bottlenecks. Reality is expected between them.

**Decay rates at a glance:**
- Model O: α = 0.020/day — 2.0% of remaining capacity lost per day (HL = 35 days) — *data-derived*
- Model C: α = 0.0083/day — 0.83% of remaining capacity lost per day (HL = 83 days) — *intelligence-derived*

**Uncertainty:** The two models bracket plausible outcomes. The intelligence-based α has source uncertainty (±5–10 launchers per snapshot), giving an April forecast range of ~240–330 BMs under the conservative scenario.

### 3.4 The system has deep redundancy

**Evidence:** After the Phase IIIa→IIIb structural break at Day 14, the Poisson model fits smoothly with no further sudden drops, spikes, or regime shifts within the Attrition phase (all 13 7-day in-sample windows: |Z| < 1.6 for both models).

**Military meaning:** A system with few, large launcher clusters would show sudden step-drops when clusters are destroyed. The smooth exponential decline is consistent with many small, independent nodes distributed geographically, each contributing marginally to total capacity. This is the most natural interpretation of the Poisson-exponential pattern, but it cannot be uniquely identified from count data — concentrated infrastructure with sufficient internal redundancy could produce similar statistics.

---

## 4. Capability Assessment by Dimension

### Launch rate

| Period | Observed mean | Trend |
|--------|--------------|-------|
| Phase I — Saturation (Days 1–4) | ~35/day at Israel | Deterministic saturation |
| Phase II — Collapse (Days 5–10) | ~26/day | Rapid collapse |
| Phase IIIa — Transition (Days 11–13) | ~15/day | Late transition |
| Phase IIIb — Attrition (Days 14–29) | ~11.7/day | Slowly declining, stochastic |

The ~11.7/day Attrition phase mean (187 BMs over 16 days) has been stable across a 16-day window (Mar 13–28). This is Iran's **sustainable campaign rate** — the output of its surviving distributed launcher network operating at maximum consistent tempo.

### Warhead sophistication

Cluster munition usage increased from ~50% (Mar 8–10) to confirmed majority (>50%) through late March. This is consistent with the Poisson/launcher-constrained model: when you cannot increase launch volume, you increase per-missile effect radius. Cluster usage is a **compensatory adaptation** to launcher attrition, not a strategic escalation.

### Geographic targeting

Iran continued targeting Israel across multiple regions throughout the Attrition phase. The persistence of geographic spread despite launcher attrition confirms that surviving nodes are **distributed across Iran's launch territory**, not concentrated in a single zone that could be eliminated by targeted strikes.

### Operational continuity

No operational pauses detected. The Poisson process produces some low days (Mar 14=8, among the lowest observed) purely from random variation — not from operational decisions to pause. Iran is not pacing itself; it is firing whenever it has the opportunity.

---

## 5. What Israel's Strikes Are Achieving

The decay parameter α measures the rate at which Iran's effective launch capacity is being reduced each week:

- At α=0.020/day (Model O): ~13% of remaining capacity lost per week. This reflects all current suppression factors combined — Israeli strikes, crew attrition, logistics degradation, and coordination disruption. It is the empirically observed rate; Israeli strike effectiveness is a major contributor but cannot be isolated from the other factors.
- At α=0.0083/day (Model C): ~5.6% of remaining capacity lost per week, consistent with the observed physical launcher count decline (160→140 over Days 12–28). Under this model, only physical destruction by Israeli strikes drives the decay — operational suppression factors are assumed negligible.

**Key implication:** The smooth exponential decline is inconsistent with single decisive strikes on concentrated high-value launchers — those would produce step-drops, not a smooth curve. The pattern is consistent with gradually accumulated attrition across a distributed network, though operational tempo reduction by choice and logistics degradation are alternative explanations that cannot be excluded from count data alone.

The 92% interception rate (late March, IDF confirmed) means that of ~11.7 BMs/day launched, only ~0.9 reach their target unintercepted. The damage-limiting value of the Iron Dome/David's Sling system is very high, while the attrition value of Israeli offensive strikes is real but operates on a longer timescale.

---

## 6. April 2026 Outlook

### Forecast range

| Model | Alpha (source) | April total | 90% PI | Daily rate (Apr 29) |
|-------|---------------|------------|--------|---------------------|
| **Conservative (C)** | 0.0083/day — intelligence (160→140 launchers) | **~275 BMs** | [248–302] | **~8.4/day** |
| **Observable (O)** | 0.020/day — denoised strike data | **~206 BMs** | [182–229] | **~5.3/day** |
| **Midpoint** | *(arithmetic blend — not a probability-weighted forecast)* | **~240 BMs** | — | **~7/day** |

Under either model, Iran retains meaningful BM strike capability throughout April. There is no scenario in the current model where Iran's Attrition phase rate collapses to near-zero during April.

> **Uncertainty note:** The prediction intervals reflect Poisson sampling variability at fixed model parameters. The intelligence-derived α range of [0.004–0.014] day⁻¹ translates to an April forecast range of approximately 240–330 BMs under the conservative scenario — substantially wider than the per-model PIs. The two-scenario bracket conveys this uncertainty.

### Weekly breakdown and rate of decline

| Week | Dates | Model C | Model O | C week-on-week | O week-on-week |
|------|-------|---------|---------|----------------|----------------|
| Week 1 | Mar 29–Apr 4 | 74.3 | 64.8 | — | — |
| Week 2 | Apr 5–11 | 70.1 | 56.3 | −5.6% | −13.1% |
| Week 3 | Apr 12–18 | 66.2 | 49.0 | −5.6% | −13.1% |
| Week 4 | Apr 19–25 | 62.4 | 42.6 | −5.6% | −13.1% |
| Week 5 | Apr 26–29 | 34.1 | 21.8 | — (4 days) | — (4 days) |
| **April total** | **Apr 1–29** | **274.8** | **205.5** | | |

The weekly decline is constant in percentage terms — a direct consequence of exponential decay. Under Model C, each week sees ~5.6% fewer launches than the previous week; under Model O, ~13.1% fewer. By end of April, the daily rate falls to ~8.4/day (Model C) or ~5.3/day (Model O), down from ~10–11/day in late March.

### Launcher attrition through April

Starting from the intelligence-confirmed baseline of **~140 operational launchers at Day 28 (Mar 27)**:

| Date | Model C — physical launchers | Model O — effective capacity |
|------|------------------------------|------------------------------|
| Mar 27 (baseline) | 140 | 140 |
| Apr 1 | ~134 (6 destroyed) | ~127 (13 lost) |
| Apr 8 | ~127 (13 destroyed) | ~110 (30 lost) |
| Apr 15 | ~120 (20 destroyed) | ~96 (44 lost) |
| Apr 22 | ~113 (27 destroyed) | ~83 (57 lost) |
| Apr 29 | **~107 (34 destroyed)** | **~72 (68 lost)** |

Under **Model C**, Israeli strikes are expected to physically destroy ~34 additional launchers during April — roughly 2–3 per week. Under **Model O**, effective operational capacity declines by ~68 units — nearly half the current baseline — driven by a combination of physical destruction, crew attrition, and logistics degradation.

> **Interpretation note:** Model C's launcher count tracks physical destruction only. Model O's "effective capacity" reflects all suppression factors combined and is not directly comparable to an intelligence-reported launcher count.

### Launcher depletion timeline

Projecting the current attrition rates forward from 140 launchers, assuming no change in Israeli strike effectiveness or Iranian adaptation:

| Threshold | Model C date | Model O date |
|-----------|-------------|-------------|
| 100 launchers | May 6, 2026 | Apr 12, 2026 |
| 70 launchers | Jun 18, 2026 | Apr 30, 2026 |
| 50 launchers | Jul 29, 2026 | May 17, 2026 |
| 20 launchers | Nov 16, 2026 | Jul 2, 2026 |
| 10 launchers | Feb 7, 2027 | Aug 5, 2026 |

Under **Model O**, Iran would fall below 50 effective operational launcher-equivalents by mid-May, and below 20 by early July. Under **Model C**, the same thresholds are not reached until late July and mid-November respectively. These projections assume the current exponential decay continues without structural change — a decisive Israeli strike campaign or a significant Iranian adaptation would shift these dates substantially.

### What would change the picture

The forecasts and launcher projections above assume current conditions persist. Four scenarios would materially shift them:

**Iranian operational recovery** — Model C materialises (Z_C stable, Z_O above +2):
- April total tracks toward ~275 BMs; weekly totals stay near 70+ through April
- Launcher depletion timeline shifts to Model C column: below 100 launchers not until May, below 50 not until late July
- Signal: Iran has resolved operational bottlenecks — logistics throughput restored, dormant launchers brought back into rotation, crew readiness improved
- The ~13%/week decline rate (Model O) would flatten to ~5.6%/week (Model C)

**Israeli strikes accelerate** — Model O confirmed or exceeded (Z_O stable, Z_C below −2):
- April total tracks toward ~206 BMs or below; weekly totals fall below 50 by Week 3
- Launcher depletion accelerates: below 70 effective capacity by end of April, below 50 by mid-May
- Signal: Israeli targeting is destroying both physical launchers and operational capacity at the observed 2%/day rate
- The ~5.6%/week decline rate (Model C) would steepen to ~13%/week (Model O) or faster

**No meaningful attrition** — flat regime (both Z-scores above +2):
- April total ~330 BMs at ~11.4/day throughout; weekly totals near 80 and stable
- Launcher count effectively not declining — Israeli strikes insufficient to erode either physical or operational capacity
- This scenario is above Model C and would imply the current observed decline in late March was transient noise, not structural decay

**Structural break — escalation or collapse** (both Z-scores exceed +2, or both drop below −2):
- Upward break: activation of an unused launcher reserve, transfer from strategic stockpile, or political decision to surge before ceasefire pressure
- Downward break: decisive strike on a logistics hub or major launcher cluster; would appear as a sudden step-drop rather than the current smooth decay — inconsistent with the distributed-network pattern seen so far

The model discrimination checkpoint is **Apr 15–18**: by then, 18–21 days of April data provide 80–90% statistical power to distinguish Model C from Model O (see methodology.md §7 for power analysis).

---

## 7. Strategic Conclusions

**1. Iran has shifted to a war of attrition, not a war of shock**
The Saturation phase ended within 4 days. Iran either chose not to or could not sustain that tempo. The Attrition phase is a fundamentally different mode of warfare — persistent low-rate harassment that imposes continuous costs on Israeli civilian life and air defence system operation without risking total capability collapse.

**2. Iran's BM threat does not collapse easily**
The count statistics are consistent with a distributed system that would be inherently resilient to individual strikes. Under the launcher-attrition interpretation, destroying any individual node causes a proportional marginal reduction rather than a cascade failure — though this structural conclusion is an interpretation of the model, not a uniquely proven fact from the data.

**3. The system is self-limiting but slowly**
At α=0.0083–0.020/day, Iran's launch capacity has a half-life of 35–83 days. Absent strategic shocks, Iran retains a meaningful BM threat for weeks to months, not days.

**4. Cluster munitions are a capability hedge**
Increased cluster warhead usage compensates for the declining volume of launches. Even as the number of missiles per day falls, the area-effect damage potential per missile rises. This is evidence of deliberate operational adaptation.

**5. The first month established an equilibrium**
The Saturation and Collapse phases were exceptional. The Attrition phase is the steady state. Unless something structurally changes — a decisive Israeli strike campaign against launcher infrastructure, or Iran's strategic decision to escalate — the rate is likely to persist through April, declining gradually from ~10–11/day (late March) to ~8–10/day (end April under Model C) or ~5–7/day (end April under Model O).

---

## 8. Confidence Assessment

| Claim | Confidence | Basis |
|-------|-----------|-------|
| Poisson distribution in Attrition phase | **High** | Overdispersion, autocorrelation tests passed; Negative Binomial rejected; 89% back-test PI coverage |
| Attrition phase start ~Mar 13–14 | **Medium** | Statistical structural break identified at Day 14; Poisson-consistent variance from that point onward |
| Exponential decay is real | **Medium** | Decay trend confirmed by denoised weekly averages and Attrition phase arc; poorly identified on Days 14–29 alone (n=16) |
| Decay rate α_C = 0.0083/day | **Medium-High** | Derived from two authoritative launcher-count snapshots (IDF/Algemeiner Day 12; ISW/IDF Day 28); source uncertainty gives range [0.004–0.014] |
| Decay rate α_O = 0.020/day | **Medium** | Derived from denoised Attrition phase data (WLS on weekly aggregates); independently cross-checked against Alma attack-wave data (same method, independent source → α=0.024/day, 20% higher); corroborated by IDF report of >80% Israel-facing capacity neutralised by Day 12 |
| Launcher capacity (not stockpile) is binding constraint | **Medium** | Intelligence confirms ~140 launchers vs ~1,500 missiles remaining; data shows no stockpile-depletion signal |
| April forecast ~206–275 BMs | **Medium** | Conditional on current suppression factors persisting (Model O) or physical attrition rate holding (Model C); wider range ~240–330 if α uncertainty included |
| No strategic pause or accumulation occurring | **Medium-High** | Supported by statistical independence test; limited power at current sample size |
