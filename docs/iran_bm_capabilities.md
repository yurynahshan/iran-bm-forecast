# Iran BM Capabilities — Analytical Conclusions

**Project:** Iran–Israel War 2026 — Iranian Ballistic Missile Strike Analysis
**Last updated:** 2026-03-29
**Assessment period:** Feb 28 – Mar 28, 2026 (Days 1–29, full first month)

---

## 1. Executive Summary

Iran's ballistic missile campaign against Israel has undergone a fundamental transformation in its first month. It opened with a brief, high-intensity saturation phase (Days 1–4, over 100 BMs/day globally, 14–50 BMs/day at Israel) then collapsed rapidly into a persistent, low-rate stochastic regime (~10–12 BMs/day) that has been stable since mid-March.

The statistical model fitted to Phase III data (Day 14+, Mar 13+) is a **Poisson process with exponential decay**. This is not merely a mathematical convenience — it is the specific signature of a **distributed system undergoing constant-rate attrition**. The model's structure directly encodes what is happening to Iranian capabilities at the operational level.

**Key findings:**
1. Iran's BM campaign has shifted from a **strategic coordinated offensive** to a **distributed attrition campaign** where independent launcher nodes fire opportunistically, and the system degrades gradually as Israeli strikes remove nodes one by one.
2. Iranian BM launches toward Israel operate as **independent autonomous units** — each launcher node makes its own firing decision with no detectable coordination or central scheduling across sites.
3. The capabilities of those autonomous units **decrease slowly over time** at a constant fractional rate of 0.7–2.1% per day, consistent with gradual Israeli attrition of distributed launch infrastructure.

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

- **Scale:** 6–19 BMs/day, mean ~11/day
- **Character:** Stochastic, independent, slowly decaying. Poisson model fits cleanly from this point onward (V/M = 0.99, all back-test Z-scores below 1.1).
- **Cumulative:** ~507 BMs at Israel by Mar 28 (Day 29)

---

## 3. What the Poisson Model Reveals

### 3.0 The Poisson model — background and fit

The **Poisson process** is one of the most fundamental models in probability. It describes situations where events occur randomly, independently, and at a constant average rate. Classic examples include phone calls arriving at a switchboard, radioactive particle emissions from a source, or equipment failures across a large fleet. The defining property is that each event happens without regard to when the last one occurred — no memory, no coordination, no pattern.

When the underlying rate is not constant but **declining over time**, the model is extended to a **Poisson process with exponential decay**: the average rate μ_t = μ₀ · e^(−αt) falls geometrically each day. This specific combination — random independent events with a decaying rate — is the mathematical fingerprint of a **depleting population under constant fractional attrition**. The textbook analogue is radioactive decay: a large number of atoms each independently decaying with a fixed daily probability, producing a random number of emissions that follows Poisson statistics at a rate that declines smoothly as the source depletes.

This model fits Iranian Phase III BM data precisely because the same physical structure is present:
- **Many independent nodes** (launchers distributed across Iran) each acting autonomously
- **Each node has a fixed daily probability of being destroyed** or rendered non-operational by Israeli strikes
- **Each surviving node fires randomly** when local conditions allow — no central coordination

The fit was validated rigorously. The Poisson assumption was confirmed by a Pearson dispersion test (χ²/df ≈ 1.0, ideal), a Ljung-Box autocorrelation test (p=0.6, no serial correlation), and formal comparison against the more general Negative Binomial distribution (which was rejected — it added no explanatory power, ΔAIC = +2 to +3). All 13 rolling 7-day back-test windows across Phase III returned Z-scores below 1.1 — well within the stability threshold of 2.

**What the model tells us:** Iran's Phase III launch system is not being managed centrally on a day-to-day basis. It is a distributed network of autonomous units, each operating on its own cycle, collectively producing a smoothly declining random output. The rate of decline directly measures Israeli strike effectiveness against that network.

### 3.1 Each launch is statistically independent

**Confirmed by:** Zero autocorrelation in daily residuals (Ljung-Box p=0.6, lag-1 AC=+0.14).

**Military meaning:** Each launcher node makes its own firing decision based on local conditions — missile availability, targeting solution, crew readiness, suppression status. There is no central daily quota, no coordinated scheduling across sites. Destroying one node does not signal or suppress others.

**Rules out:**
- Central command throttling output up or down day-to-day
- Planned pause-and-surge cycles (no periodicity detected)
- Strategic accumulation for large salvos (the Mar 19=19 and Mar 25=15 peaks are Poisson tail events, not planned escalations)

### 3.2 The stockpile is not the binding constraint

**Evidence:** If Iran were drawing from a nearly exhausted missile inventory, firing more today would leave fewer for tomorrow → negative day-to-day autocorrelation. None detected.

**Military meaning:** Iran's usable missile stockpile remains large enough that daily depletion is operationally negligible. The binding constraint is **operational launcher capacity** — the number of launchers that are ready, undetected, and loaded on any given day — not total missile inventory.

### 3.3 The exponential decay is launcher attrition, not stockpile exhaustion

**The model:** μ_t = μ₀ · e^(−αt), where α = 0.007–0.021/day.

**Physical interpretation:** Each operational launcher has a daily probability α of being destroyed, suppressed, or rendered non-operational by Israeli strikes. If the probability is constant and each launcher is independent, the expected number of operational launchers — and therefore the expected daily launch rate — follows exponential decay. This is mathematically identical to radioactive decay.

**Two calibrated models reflect genuine uncertainty in the decay rate:**

The two models differ in which portion of Phase III is used to estimate α. The **Conservative model (C)** is anchored at Day 14 (Mar 13), after the rapid IIIa transition has fully settled, and fits only the quasi-flat IIIb period. It finds a very slow decay (α=0.007/day), interpreting the early Phase III decline as a one-off transition rather than a continuing trend. The **Optimistic model (O)** is anchored at Day 11 (Mar 10) and fits the entire Phase III arc from 22 BMs/day down to 6 BMs/day, treating that full decline as a genuine continuing trend (α=0.021/day). Both models are statistically valid — they cannot be distinguished until approximately 3 weeks of April data accumulates.

**Estimated daily attrition rate:**
- Model C (Conservative): α = 0.007/day → Israeli strikes destroy ~0.7% of remaining launch capacity daily
- Model O (Optimistic): α = 0.021/day → Israeli strikes destroy ~2.1% of remaining launch capacity daily

**Half-life interpretation:**
- Model C: 99-day half-life → Iran retains ~80% of current launch capacity through end of April
- Model O: 33-day half-life → Iran retains ~52% of current launch capacity by end of April

### 3.4 The system has deep redundancy

**Evidence:** The Poisson model fits smoothly with no sudden drops, spikes, or regime breaks in Phase III (all 13 7-day back-test windows: |Z| < 1.1).

**Military meaning:** Iran's launch infrastructure is not concentrated. A system with few, large launcher clusters would show sudden step-drops when clusters are destroyed. The smooth exponential decay implies many small, independent nodes distributed geographically — each node's destruction reduces total capacity marginally and smoothly.

---

## 4. Capability Assessment by Dimension

### Launch rate

| Period | Observed mean | Trend |
|--------|--------------|-------|
| Phase I (Days 1–4) | ~35/day at Israel | Deterministic saturation |
| Phase II (Days 5–10) | ~26/day | Rapid collapse |
| Phase IIIa (Days 11–13) | ~15/day | Late transition |
| Phase IIIb (Days 14–29) | ~11/day | Quasi-stable, slowly declining |

The ~11/day Phase IIIb rate has been remarkably stable across a 16-day window (Mar 13–28). This is Iran's **sustainable campaign rate** — the output of its surviving distributed launcher network operating at maximum consistent tempo.

### Warhead sophistication

Cluster munition usage increased from ~50% (Mar 8–10) to confirmed majority (>50%) through late March. This is consistent with the Poisson/launcher-constrained model: when you cannot increase launch volume, you increase per-missile effect radius. Cluster usage is a **compensatory adaptation** to launcher attrition, not a strategic escalation.

### Geographic targeting

Iran continued targeting Israel across multiple regions throughout Phase III. The persistence of geographic spread despite launcher attrition confirms that surviving nodes are **distributed across Iran's launch territory**, not concentrated in a single zone that could be eliminated by targeted strikes.

### Operational continuity

No operational pauses detected. The Poisson process produces some low days (Mar 28=6, the minimum) purely from random variation — not from operational decisions to pause. Iran is not pacing itself; it is firing whenever it has the opportunity.

---

## 5. What Israel's Strikes Are Achieving

The decay parameter α directly measures the effectiveness of Israeli strikes against Iranian launch infrastructure:

- At α=0.021/day (Model O): Each week of Israeli strikes degrades ~14% of Iran's remaining launch capacity → meaningful cumulative effect over 4–8 weeks
- At α=0.007/day (Model C): Each week degrades ~5% → slow but sustained erosion

**Key implication:** Israel is not finding and destroying single concentrated launchers — it is applying constant attrition across a distributed network. The effect is real but gradual. There is no evidence of a decisive strike that collapsed capacity suddenly.

The 92% interception rate (late March, IDF confirmed) means that of ~11 BMs/day launched, only ~0.9 reach their target unintercepted. The damage-limiting value of the Iron Dome/David's Sling system is very high, while the attrition value of Israeli offensive strikes is real but operates on a longer timescale.

---

## 6. April 2026 Outlook

### Forecast range

| Model | Assumption | April total | Daily rate (Apr 29) |
|-------|-----------|------------|---------------------|
| **Conservative (C)** | Launcher attrition ~0.7%/day | **~271 BMs** | **~8.5/day** |
| **Optimistic (O)** | Launcher attrition ~2.1%/day | **~200 BMs** | **~5.1/day** |
| **Midpoint** | | **~236 BMs** | **~7/day** |

Under either model, Iran retains meaningful BM strike capability throughout April. There is no scenario in the current model where Iran's Phase III rate collapses to near-zero during April.

### What would change the picture

**Accelerating collapse** (both models' Z-scores go below −2):
- Successful strike on a major missile storage/transfer hub
- Successful strike that simultaneously degrades multiple launcher clusters
- Logistics interdiction cutting resupply of propellant or warheads

**Escalation** (both models' Z-scores exceed +2):
- Activation of a previously unused launcher reserve
- Transfer of additional missiles from strategic stockpile to operational units
- Political decision to escalate before ceasefire pressure builds

**Model O confirmed** (Z_O stable, Z_C below −2):
- By Apr 16–21, cumulative April total falls in the Model O prediction range
- Indicates Israeli strikes are destroying ~2%/day of capacity — effective sustained pressure

**Model C confirmed** (Z_C stable, Z_O above +2):
- Cumulative April total falls in the Model C range
- Indicates Iran has successfully maintained its distributed network against Israeli pressure

---

## 7. Strategic Conclusions

**1. Iran has shifted to a war of attrition, not a war of shock**
The Phase I saturation campaign ended within 4 days. Iran either chose not to or could not sustain that tempo. Phase III is a fundamentally different mode of warfare — persistent low-rate harassment that imposes continuous costs on Israeli civilian life and air defence system operation without risking total capability collapse.

**2. Iran's BM threat does not collapse easily**
The distributed, independent, Poisson-statistically-described system is inherently resilient. There is no single point of failure. Destroying any individual node causes a proportional marginal reduction, not a cascade failure.

**3. The system is self-limiting but slowly**
At α=0.007–0.021/day, Iran's launch capacity has a half-life of 33–101 days. Absent strategic shocks, Iran retains a meaningful BM threat for weeks to months, not days.

**4. Cluster munitions are a capability hedge**
Increased cluster warhead usage compensates for the declining volume of launches. Even as the number of missiles per day falls, the area-effect damage potential per missile rises. This is evidence of deliberate operational adaptation.

**5. The first month established the equilibrium**
Phase I and II were exceptional. Phase III is the steady state. Unless something structurally changes — a decisive Israeli strike campaign against launcher infrastructure, or Iran's strategic decision to escalate — the ~8–12 BMs/day rate is likely to persist through April, declining gradually.

---

## 8. Confidence Assessment

| Claim | Confidence | Basis |
|-------|-----------|-------|
| Poisson distribution in Phase III | **High** | Formal statistical tests; 89% PI coverage |
| Phase III start ~Mar 10–13 | **High** | AIC minimisation; V/M ratio stabilisation |
| Exponential decay is real | **Medium** | ΔAIC vs flat model = 1.1; present but not overwhelming |
| Decay rate α = 0.007–0.021/day | **Medium** | Models statistically tied; 19–24 days to discriminate |
| Launcher capacity (not stockpile) is binding constraint | **Medium** | Indirect inference from independence structure |
| April forecast ~200–271 BMs | **Medium** | Conditional on no structural break; model uncertainty is the main risk |
| No strategic pause or accumulation occurring | **High** | Directly confirmed by autocorrelation test |
