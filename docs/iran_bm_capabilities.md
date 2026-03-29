# Iran BM Capabilities — Analytical Conclusions

**Project:** Iran–Israel War 2026 — Iranian Ballistic Missile Strike Analysis
**Last updated:** 2026-03-29
**Assessment period:** Feb 28 – Mar 28, 2026 (Days 1–29, full first month)
**Model version:** Decoupled calibration — Poisson process from data, decay rate from intelligence

---

## 1. Executive Summary

Iran's ballistic missile campaign against Israel has undergone a fundamental transformation in its first month. It opened with a brief, high-intensity saturation phase (Days 1–4, over 100 BMs/day globally, 14–50 BMs/day at Israel) then collapsed rapidly into a persistent, low-rate stochastic regime (~10–12 BMs/day) that has been stable since mid-March.

The statistical model used for April forecasting is a **Poisson process with exponential decay**. The formal best-fit model on Phase III data is a piecewise Poisson (structural break at Day 14); the single exponential is within ΔAIC < 0.3 and is retained for tractable scenario forecasting. The Poisson-with-decay pattern is consistent with a **distributed system undergoing gradual attrition** — this document explores what that interpretation implies operationally if correct.

The model uses a **decoupled calibration approach**: the Poisson process structure is calibrated from Phase IIIb launch data, while the decay rate α is derived from open-source intelligence on Iranian launcher attrition — not fitted to the sparse (n=16) strike time series. This makes the forecasts stable and physically grounded.

**Key findings:**
1. Iran's BM campaign has shifted from a **strategic coordinated offensive** to what appears to be a **distributed attrition campaign**, where the statistical pattern is consistent with launcher nodes operating with high autonomy and gradual capacity erosion.
2. Iranian BM launches toward Israel exhibit **statistical independence** consistent with autonomous launcher operation — the absence of detectable coordination or central scheduling is the simplest explanation, though this structural interpretation is a hypothesis rather than a proven fact.
3. The capabilities of those autonomous units **decrease slowly over time** at a constant fractional rate of 0.83–2.0% per day (Model C and O respectively), derived from open-source intelligence on Iranian launcher counts rather than from strike data alone.

---

## 2. The Three Phases

### Phase I — Saturation (Days 1–4, Feb 28 – Mar 3)

- **Scale:** 14–50 BMs/day at Israel; 68–438 globally per day
- **Character:** Deterministic, command-driven. Iran executed a pre-planned mass-launch campaign drawing on its highest-readiness launcher inventory.
- **Statistical nature:** Not stochastic — these were coordinated operational decisions, not random events.
- **Cumulative:** ~128 BMs at Israel by Mar 4 (BBC/IDF anchor)

### Phase II — Rapid Collapse (Days 5–10, Mar 4 – Mar 9)

- **Scale:** 6–38 BMs/day; highly variable
- **Character:** Transitional. Iran's first-echelon launch infrastructure was degraded rapidly. The system shifted from command-driven to decentralized and autonomous.
- **Key event:** IDF confirms ~285–300 BMs at Israel by Mar 10 — the Phase II total of ~157 BMs arrived while the rate was collapsing from ~40 to ~22/day.

### Phase IIIa — Late Transition (Days 11–13, Mar 10–12)

- **Scale:** 15–22 BMs/day; still elevated and declining
- **Character:** Tail of Phase II collapse. The system is shifting to autonomous operation but the rate has not yet stabilised. Included in Model O training data; excluded from Model C.

### Phase IIIb — Persistent Stochastic Regime (Day 14+, Mar 13–present)

- **Scale:** 6–19 BMs/day, mean ~11.7/day
- **Character:** Stochastic, independent, slowly decaying. Poisson model fits well from this point onward (V/M ≈ 0.99, all back-test Z-scores below 1.6 for both models, 89% PI coverage).
- **Cumulative:** ~511 BMs at Israel by Mar 28 (Day 29)

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

The fit was assessed through in-sample diagnostics. The Poisson assumption is supported by a Pearson dispersion test (χ²/df ≈ 1.0 under the best-fit models M1 and M4), a Ljung-Box autocorrelation test (p=0.6, no serial correlation), and formal comparison against the Negative Binomial (rejected, ΔAIC = +2 to +3). All 13 rolling 7-day in-sample windows across Phase III returned Z-scores below 1.1 — well within the stability threshold of 2. Note: these are in-sample calibration checks on overlapping windows, not out-of-sample forecast validation.

**Primary operational interpretation:** Iran's Phase III launch pattern is most simply explained by a distributed network of units each operating on its own cycle, collectively producing a smoothly declining random output. The rate of decline is a candidate measure of Israeli strike effectiveness — subject to the caveats above.

### 3.1 Each launch is statistically independent

**Confirmed by:** Zero autocorrelation in daily residuals (Ljung-Box p=0.6, lag-1 AC=+0.14).

**Military meaning:** The most parsimonious interpretation is that each launcher node makes its own firing decision based on local conditions — missile availability, targeting solution, crew readiness, suppression status — with no central daily quota and no coordinated scheduling across sites. Under this model, destroying one node would not signal or suppress others. At $n = 19$ days of data, alternative coordination models (command pacing, mixed processes) cannot be statistically ruled out; this is a structural hypothesis consistent with the data, not a uniquely proven mechanism.

**Inconsistent with:**
- Central command throttling output up or down day-to-day
- Planned pause-and-surge cycles (no periodicity detected)
- Strategic accumulation for large salvos (the Mar 19=19 and Mar 25=15 peaks are consistent with Poisson variability under a slowly varying mean; at n=19 this cannot be proven conclusively)

### 3.2 The stockpile is not the binding constraint

**Evidence:** If Iran were drawing from a nearly exhausted missile inventory, firing more today would leave fewer for tomorrow → negative day-to-day autocorrelation. None detected.

**Military meaning:** The absence of negative autocorrelation is consistent with Iran's usable missile stockpile being large enough that daily depletion is operationally negligible. The most parsimonious explanation is that the binding constraint is **operational launcher capacity** — launchers that are ready, undetected, and loaded — rather than total missile inventory. This inference is indirect; stockpile effects could be masked if replenishment keeps pace with consumption, or if the stockpile is large relative to daily draw-down.

### 3.3 The exponential decay is launcher attrition, not stockpile exhaustion

**The model:** μ_t = μ₀ · e^(−αt), where α = 0.007–0.021/day.

**Physical interpretation:** Each operational launcher has a daily probability α of being destroyed, suppressed, or rendered non-operational by Israeli strikes. If the probability is constant and each launcher is independent, the expected number of operational launchers — and therefore the expected daily launch rate — follows exponential decay. This is mathematically identical to radioactive decay.

**Two calibrated models using decoupled calibration:**

The models use a principled separation: the **Poisson process structure** (statistical distribution of events) is calibrated from Phase IIIb launch data, while the **decay rate α** is derived from open-source intelligence on Iranian launcher counts — not fitted to the sparse (n=16) time series. This prevents observation noise from distorting the decay estimate.

The **Conservative model (C)** derives α directly from two authoritative launcher-count snapshots:
- Day 12 (Mar 11): ~160 total operational launchers (IDF assessment via Algemeiner)
- Day 28 (Mar 27): ~140 total operational launchers (ISW citing IDF: 330 of 470 destroyed)
- Implied α = ln(160/140)/16 = **0.0083/day** (HL = 83 days)

The **Optimistic model (O)** posits that Israel specifically prioritises destruction of Iran's Israel-facing assets. IDF reported >80% of Israel-facing launch capacity neutralised by Day 12 — far more than the ~20% of total fleet destroyed by then — indicating priority targeting. Model O sets α = 2.5 × α_C = **0.020/day** (HL = 35 days).

Both μ₀ values are fitted by closed-form MLE conditional on the fixed α, using all 16 Phase IIIb observations (Σ = 187 BMs).

> **"Optimistic" refers to the Israeli perspective** — faster Iranian decay is better for Israel. "Conservative" means Iran sustains its capability longer.

**Calibrated parameters:**
- Model C (Conservative): α = 0.0083/day, μ₀ = 12.43, HL = 83 days — 0.83% of remaining launch capacity destroyed daily
- Model O (Optimistic): α = 0.020/day, μ₀ = 13.52, HL = 35 days — 2.0% of remaining launch capacity destroyed daily

**Half-life interpretation:**
- Model C: 83-day half-life → Iran retains ~68% of Phase IIIb launch capacity through end of April
- Model O: 35-day half-life → Iran retains ~39% of Phase IIIb launch capacity by end of April

**Stability:** Because α is fixed externally, a ±4 BM change in any single day's estimate shifts the April forecast by only ~6 BMs (C) or ~4 BMs (O). The model is robust to observation noise by design.

**Intelligence uncertainty:** The intelligence-derived α range is [0.004, 0.014] day⁻¹ (HL 48–166 days), translating to an April forecast range of approximately 240–330 BMs under the conservative scenario. The two-model bracket conveys this uncertainty; the per-model prediction intervals convey only Poisson sampling noise.

### 3.4 The system has deep redundancy

**Evidence:** After the IIIa→IIIb structural break at Day 14, the Poisson model fits smoothly with no further sudden drops, spikes, or regime shifts within Phase IIIb (all 13 7-day in-sample windows: |Z| < 1.6 for both models).

**Military meaning:** A system with few, large launcher clusters would show sudden step-drops when clusters are destroyed. The smooth exponential decline is consistent with many small, independent nodes distributed geographically, each contributing marginally to total capacity. This is the most natural interpretation of the Poisson-exponential pattern, but it cannot be uniquely identified from count data — concentrated infrastructure with sufficient internal redundancy could produce similar statistics.

---

## 4. Capability Assessment by Dimension

### Launch rate

| Period | Observed mean | Trend |
|--------|--------------|-------|
| Phase I (Days 1–4) | ~35/day at Israel | Deterministic saturation |
| Phase II (Days 5–10) | ~26/day | Rapid collapse |
| Phase IIIa (Days 11–13) | ~15/day | Late transition |
| Phase IIIb (Days 14–29) | ~11.7/day | Slowly declining, stochastic |

The ~11.7/day Phase IIIb mean (187 BMs over 16 days) has been stable across a 16-day window (Mar 13–28). This is Iran's **sustainable campaign rate** — the output of its surviving distributed launcher network operating at maximum consistent tempo.

### Warhead sophistication

Cluster munition usage increased from ~50% (Mar 8–10) to confirmed majority (>50%) through late March. This is consistent with the Poisson/launcher-constrained model: when you cannot increase launch volume, you increase per-missile effect radius. Cluster usage is a **compensatory adaptation** to launcher attrition, not a strategic escalation.

### Geographic targeting

Iran continued targeting Israel across multiple regions throughout Phase III. The persistence of geographic spread despite launcher attrition confirms that surviving nodes are **distributed across Iran's launch territory**, not concentrated in a single zone that could be eliminated by targeted strikes.

### Operational continuity

No operational pauses detected. The Poisson process produces some low days (Mar 14=8, among the lowest observed) purely from random variation — not from operational decisions to pause. Iran is not pacing itself; it is firing whenever it has the opportunity.

---

## 5. What Israel's Strikes Are Achieving

The decay parameter α directly measures the effectiveness of Israeli strikes against Iranian launch infrastructure:

- At α=0.020/day (Model O): Each week of Israeli strikes degrades ~13% of Iran's remaining launch capacity → meaningful cumulative effect over 4–8 weeks
- At α=0.0083/day (Model C): Each week degrades ~5.7% → slow but sustained erosion; consistent with observed launcher count decline (160→140 over Days 12–28)

**Key implication:** The smooth exponential decline is inconsistent with single decisive strikes on concentrated high-value launchers — those would produce step-drops, not a smooth curve. The pattern is consistent with gradually accumulated attrition across a distributed network, though operational tempo reduction by choice and logistics degradation are alternative explanations that cannot be excluded from count data alone.

The 92% interception rate (late March, IDF confirmed) means that of ~11.7 BMs/day launched, only ~0.9 reach their target unintercepted. The damage-limiting value of the Iron Dome/David's Sling system is very high, while the attrition value of Israeli offensive strikes is real but operates on a longer timescale.

---

## 6. April 2026 Outlook

### Forecast range

| Model | Alpha (source) | April total | 90% PI | Daily rate (Apr 29) |
|-------|---------------|------------|--------|---------------------|
| **Conservative (C)** | 0.0083/day — intelligence (160→140 launchers) | **~275 BMs** | [248–302] | **~8.4/day** |
| **Optimistic (O)** | 0.020/day — 2.5× faster (priority targeting) | **~206 BMs** | [182–229] | **~5.3/day** |
| **Midpoint** | *(arithmetic blend — not a probability-weighted forecast)* | **~240 BMs** | — | **~7/day** |

Under either model, Iran retains meaningful BM strike capability throughout April. There is no scenario in the current model where Iran's Phase III rate collapses to near-zero during April.

> **Uncertainty note:** The prediction intervals reflect Poisson sampling variability at fixed model parameters. The intelligence-derived α range of [0.004–0.014] day⁻¹ translates to an April forecast range of approximately 240–330 BMs under the conservative scenario — substantially wider than the per-model PIs. The two-scenario bracket conveys this uncertainty.

### What would change the picture

**No decay (flat regime):** If the Phase IIIb rate is truly flat (no statistically detectable decay — AIC-preferred on Days 14–29 alone), the April total would be ~330 BMs at ~11.4/day. This is above Model C's 275 and represents the scenario where Israeli attrition is not meaningfully reducing Iran's launch rate during the period observed.

**Accelerating collapse** (both models' Z-scores go below −2):
- Successful strike on a major missile storage/transfer hub
- Successful strike that simultaneously degrades multiple launcher clusters
- Logistics interdiction cutting resupply of propellant or warheads

**Escalation** (both models' Z-scores exceed +2):
- Activation of a previously unused launcher reserve
- Transfer of additional missiles from strategic stockpile to operational units
- Political decision to escalate before ceasefire pressure builds

**Model O confirmed** (Z_O stable, Z_C below −2):
- By Apr 15–21, cumulative April total falls in the Model O prediction range
- Indicates Israeli strikes are destroying ~2%/day of capacity — effective sustained pressure

**Model C confirmed** (Z_C stable, Z_O above +2):
- Cumulative April total falls in the Model C range
- Indicates Iran has successfully maintained its distributed network against Israeli pressure

---

## 7. Strategic Conclusions

**1. Iran has shifted to a war of attrition, not a war of shock**
The Phase I saturation campaign ended within 4 days. Iran either chose not to or could not sustain that tempo. Phase III is a fundamentally different mode of warfare — persistent low-rate harassment that imposes continuous costs on Israeli civilian life and air defence system operation without risking total capability collapse.

**2. Iran's BM threat does not collapse easily**
The count statistics are consistent with a distributed system that would be inherently resilient to individual strikes. Under the launcher-attrition interpretation, destroying any individual node causes a proportional marginal reduction rather than a cascade failure — though this structural conclusion is an interpretation of the model, not a uniquely proven fact from the data.

**3. The system is self-limiting but slowly**
At α=0.0083–0.020/day, Iran's launch capacity has a half-life of 35–83 days. Absent strategic shocks, Iran retains a meaningful BM threat for weeks to months, not days.

**4. Cluster munitions are a capability hedge**
Increased cluster warhead usage compensates for the declining volume of launches. Even as the number of missiles per day falls, the area-effect damage potential per missile rises. This is evidence of deliberate operational adaptation.

**5. The first month established an equilibrium**
Phase I and II were exceptional. Phase III is the steady state. Unless something structurally changes — a decisive Israeli strike campaign against launcher infrastructure, or Iran's strategic decision to escalate — the rate is likely to persist through April, declining gradually from ~10–11/day (late March) to ~8–10/day (end April under Model C) or ~5–7/day (end April under Model O).

---

## 8. Confidence Assessment

| Claim | Confidence | Basis |
|-------|-----------|-------|
| Poisson distribution in Phase III | **High** | Overdispersion test D≈0.79–0.88; NB rejected; 89% back-test PI coverage |
| Phase III start ~Mar 13–14 | **Medium** | M4 structural break at Day 14; V/M ≈ 1.0 in IIIb; all back-test Z-scores < 1.6 from Day 14 |
| Exponential decay is real | **Medium** | ΔAIC vs flat ≈ 0 for IIIb alone (poorly identified); M4 and Phase III arc confirm trend |
| Decay rate α_C = 0.0083/day | **Medium-High** | Directly derived from two authoritative launcher-count snapshots (Algemeiner/IDF Day 12; ISW/IDF Day 28); range [0.004–0.014] |
| Decay rate α_O = 0.020/day | **Medium** | 2.5× multiplier on α_C; IDF >80% Israel-facing capacity neutralized by Day 12 supports priority targeting; multiplier is approximate |
| Launcher capacity (not stockpile) is binding constraint | **Medium** | Intelligence confirms ~140 launchers vs ~1,500 missiles remaining; no negative autocorrelation in data |
| April forecast ~206–275 BMs | **Medium** | Conditional on exponential decay continuing at intelligence-derived rate; intelligence uncertainty gives wider range ~240–330 |
| No strategic pause or accumulation occurring | **Medium-High** | Supported by autocorrelation test; test has limited power at n=18 |
