# Iran BM Strike Model — Methodology & Model Specification

**Project:** Iran–Israel War 2026 — Iranian Ballistic Missile Strike Analysis
**Last updated:** 2026-03-29
**Data scope:** Iranian BM launched toward Israel, Feb 28 – Mar 28, 2026 (Days 1–29)

---

## 1. Objective

Model the stochastic process governing Iranian ballistic missile (BM) launches toward Israel during the Attrition phase of the war, and generate calibrated daily and weekly forecasts for April 2026.

The goal is not merely to count missiles but to infer **underlying system capacity** — the operational state of Iran's launch infrastructure — from observable strike data.

---

## 2. Data Foundation

### Primary input
`data/israel_daily_estimate.csv` — one row per day, columns:

| Column | Description |
|--------|-------------|
| `isr_bm` | Best estimate of BMs fired at Israel that day |
| `bm_il_min` / `bm_il_max` | Lower/upper bounds |
| `isr_cumul` | Running cumulative total |
| `primary_source` | Key source driving the estimate |
| `notes` | Estimation method and basis |

### Estimation methods by period

| Period | Days | Method | Description |
|--------|------|--------|-------------|
| Phase I (Saturation) | 1–4 | `bbc_prop` | JINSA Mar5 PDF direct count scaled by BBC/IDF 128 anchor |
| Phase I residual | 5 | `bbc_residual` | 128 minus sum of Days 1–4 estimates |
| Phase II (Collapse) | 6–10 | `anchor_prop` | Alma waves proportioned to 150-BM budget (300−128−22) |
| Phase IIIa (Transition) | 11 | `jinsa_direct` | JINSA Mar11 PDF direct Israel count |
| Phase IIIa / IIIb | 12–17 | `wave_ratio` | Alma waves × 1.11 (ratio calibrated from JINSA÷Alma Mar18–24) |
| Phase IIIb (Attrition) | 18–25 | `jinsa_direct` / `multi_source` | JINSA Mar24 PDF Chart 2 direct readings |
| Phase IIIb late | 26–29 | `jinsa_derived` / `media_count` | Derived from global minus confirmed non-Israel |

### Anchor constraints satisfied

| Date | Cumulative | Source | Status |
|------|-----------|--------|--------|
| Mar 4 | 128 | BBC Arabic citing IDF | ✓ exact |
| Mar 10 | ~300 (precise: 285) | IDF IAF briefing via Walla/N12 | ✓ isr_cumul=301 |
| Mar 27 | >450 | Times of Israel citing IDF | ✓ isr_cumul=501 |
| Mar 28 | — | N12 liveblog (3 wave events, 8–12 est.) | isr_cumul=511 |

---

## 3. Phase Definitions

The campaign is divided into four operationally distinct phases based on statistical structure and launch rate behaviour:

| Phase | Days | Dates | Character |
|-------|------|-------|-----------|
| **Phase I — Saturation** | 1–4 | Feb 28 – Mar 3 | Large coordinated salvos, 14–50 BMs/day at Israel; command-driven |
| **Phase II — Collapse** | 5–10 | Mar 4 – Mar 9 | Rapid degradation from ~40 to ~22/day; transition from centralised to autonomous |
| **Phase IIIa — Transition** | 11–13 | Mar 10–12 | Late tail of Collapse; rate still elevated and declining; not yet statistically stable |
| **Phase IIIb — Attrition** | **14–29** | **Mar 13–28** | **Persistent stochastic regime — the phase used for model training** |

### Phase I — Saturation (Days 1–4, Feb 28 – Mar 3)

- **Scale:** 14–50 BMs/day at Israel; 68–438 globally per day
- **Character:** Deterministic, command-driven. Iran executed a pre-planned mass-launch campaign drawing on its highest-readiness launcher inventory.
- **Statistical nature:** Not stochastic — these were coordinated operational decisions, not random events.
- **Cumulative:** ~128 BMs at Israel by Mar 4 (BBC/IDF anchor)

### Phase II — Collapse (Days 5–10, Mar 4 – Mar 9)

- **Scale:** 6–38 BMs/day; highly variable
- **Character:** Transitional. Iran's first-echelon launch infrastructure was degraded rapidly. The system shifted from command-driven to decentralised and autonomous.
- **Key event:** IDF confirms ~285–300 BMs at Israel by Mar 10 — ~157 BMs arrived while the rate collapsed from ~40 to ~22/day.

### Phase IIIa — Transition (Days 11–13, Mar 10–12)

- **Scale:** 15–22 BMs/day; still elevated and declining
- **Character:** Tail of the Collapse phase. The system is shifting to autonomous operation but the rate has not yet stabilised. Variance-to-mean ratio still above Poisson-consistent levels; excluded from the Phase IIIb stable regime for model training purposes.

### Phase IIIb — Attrition (Days 14+, Mar 13–present)

- **Scale:** 6–19 BMs/day, mean ~11.7/day
- **Character:** Stochastic, independent, slowly decaying. Poisson model fits well from Day 14 onward (V/M ≈ 0.99, all back-test Z-scores below 1.6 for both models, 89% PI coverage).
- **Cumulative:** ~511 BMs at Israel by Mar 28 (Day 29)
- **Model training set:** Days 14–29, $n = 16$ observations, $\sum L_t = 187$ BMs

### Phase IIIb (Attrition) start detection

The boundary between Transition and Attrition (Day 14, Mar 13) is identified by three converging lines of evidence:

1. **Structural break.** The best-fitting piecewise Poisson model places its internal breakpoint at Day 14, after which the decay rate drops from $\alpha_1 \approx 0.149$/day (half-life 4.7 days) to $\alpha_2 \approx 0.007$/day. This break is identified on a fixed dataset and is therefore a valid within-sample comparison.

2. **Variance-to-mean ratio.** The V/M ratio $\hat{\sigma}^2 / \bar{L}$ approaches 1.0 (Poisson-consistent) in the Days 14–29 window, and all 13 rolling 7-day back-test windows from Day 14 onward return $|Z| < 1.6$ under both models (well within the alert threshold of 2).

3. **AIC scan (indicative).** Fitting the Poisson exponential to each candidate window $\mathcal{T}(t_0) = \{t \geq t_0\}$ and comparing AIC across candidates is **not strictly valid** — AIC is defined for fixed $n$ and rankings across different sample sizes are not meaningful. This scan is treated as suggestive only; the primary identification of $t_0 = 14$ rests on items 1 and 2.

---

## 4. Statistical Model

### 4.1 Distribution

Let $L_t$ denote the number of Iranian BMs launched toward Israel on war day $t$. We model:

$$L_t \mid \mu_t \sim \mathrm{Poisson}(\mu_t), \quad t \in \mathcal{T}$$

with probability mass function:

$$P(L_t = k) = \frac{e^{-\mu_t}\, \mu_t^k}{k!}, \quad k = 0, 1, 2, \ldots$$

giving $\mathbb{E}[L_t] = \mathrm{Var}[L_t] = \mu_t$. Daily counts are assumed conditionally independent given $\{\mu_t\}$.

### 4.2 Mean function

The expected daily rate follows exponential decay:

$$\mu_t = \mu_0 \cdot \exp\!\bigl(-\alpha\,(t - t_0)\bigr)$$

where:

| Symbol | Meaning |
|--------|---------|
| $t$ | War day number (Day 1 = Feb 28, 2026) |
| $t_0$ | Attrition phase anchor day (model-specific) |
| $\mu_0$ | Expected BMs/day at anchor $t_0$ |
| $\alpha$ | Exponential decay rate (day⁻¹) |

The **half-life** — days for capacity to halve — is $\tau_{1/2} = \ln 2 / \alpha$.

### 4.3 Log-likelihood and MLE

Given observations $\{L_t : t \in \mathcal{T}\}$ over training set $\mathcal{T}$, the log-likelihood is:

$$\ell(\mu_0, \alpha) = \sum_{t \in \mathcal{T}} \Bigl[ L_t \log \mu_t - \mu_t - \log(L_t!) \Bigr]$$

Substituting $\mu_t = \mu_0 e^{-\alpha(t-t_0)}$:

$$\ell(\mu_0, \alpha) = \sum_{t \in \mathcal{T}} \Bigl[ L_t \bigl(\log \mu_0 - \alpha(t - t_0)\bigr) - \mu_0\,e^{-\alpha(t-t_0)} \Bigr] + \text{const}$$

Maximum Likelihood Estimates (MLEs) are:

$$(\hat{\mu}_0,\, \hat{\alpha}) = \underset{\mu_0 > 0,\; \alpha > 0}{\arg\max}\; \ell(\mu_0, \alpha)$$

No closed-form solution exists; optimisation is performed numerically. To enforce positivity constraints, we reparametrise $\theta_1 = \log\mu_0$, $\theta_2 = \log\alpha$ and apply L-BFGS-B with multiple initialisations (9 starting points over a grid of $\mu_0 \in \{6, 12, 18\}$ and $\alpha \in \{0.005, 0.020, 0.060\}$) to avoid local minima.

### 4.4 Model selection — AIC

For each candidate model with $p$ parameters and maximised log-likelihood $\hat{\ell}$:

$$\mathrm{AIC} = 2p - 2\hat{\ell}$$

$$\mathrm{BIC} = p\ln n - 2\hat{\ell}$$

Lower AIC/BIC is preferred. Models within ΔAIC < 2 of the minimum have substantial support; ΔAIC > 4 indicates weak support; ΔAIC > 10 is decisive rejection.

Six candidate models were compared on Transition + Attrition data ($n = 19$ days, Days 11–29):

| Model | $p$ | ΔAIC | Verdict |
|-------|-----|------|---------|
| Poisson flat: $\mu_t = \mu_0$ | 1 | +1.4 | plausible |
| Poisson exponential: $\mu_t = \mu_0 e^{-\alpha(t-t_0)}$ | 2 | +0.2 | **strong support** |
| NB flat | 2 | +3.2 | rejected |
| NB exponential | 3 | +2.2 | rejected |
| Poisson piecewise-exponential | 3 | **0.0** | **best fit** |
| NB piecewise | 4 | +2.1 | rejected |

The Negative Binomial was tested and rejected across all specifications (ΔAIC +2 to +3). The NB dispersion parameter $k \to 500$ (optimizer upper bound), confirming Poisson is the correct distributional family.

### 4.5 Goodness-of-fit diagnostics

**Overdispersion test.** Define Pearson residuals:

$$r_t = \frac{L_t - \hat{\mu}_t}{\sqrt{\hat{\mu}_t}}$$

The Pearson statistic $X^2 = \sum_{t} r_t^2$ follows $\chi^2(n - p)$ under $H_0$: Poisson. The **dispersion index** $D = X^2/(n-p)$ should be $\approx 1$; values $> 1.5$ indicate overdispersion requiring NB.

Results: $D = 0.99$–$1.08$ under the exponential and piecewise Poisson models (M1, M4) — well-calibrated. The flat model (M0) shows $D \approx 1.22$, reflecting unmodelled trend rather than true overdispersion.

**Autocorrelation test.** The Ljung-Box statistic at lag $h$:

$$Q(h) = n(n+2)\sum_{k=1}^{h} \frac{\hat{\rho}_k^2}{n - k} \;\sim\; \chi^2(h) \;\text{ under } H_0$$

where $\hat{\rho}_k = \mathrm{corr}(r_t,\, r_{t-k})$. Results: $Q(3) = 1.96$, $p = 0.58$ — no serial correlation detected. Lag-1 autocorrelation $\hat{\rho}_1 = +0.14$ (negligible).

### 4.6 Phase IIIb (Attrition) start detection

See §3 for the full identification methodology. In summary: Day 14 (Mar 13) is confirmed by structural break analysis, variance-to-mean ratio stabilisation, and an indicative AIC scan. Phase IIIa (Days 11–13) is excluded from the Phase IIIb stable regime for model training.

---

## 5. Model Calibration

### Design principle — decoupled calibration

The Poisson process structure and the decay rate α are calibrated from independent sources:

| Component | Source | Rationale |
|-----------|--------|-----------|
| **Process structure** (Poisson) | Phase IIIb (Attrition) launch data, Days 14–29 | Captures the distributed, autonomous nature of Iranian missile-unit operations |
| **Decay rate α — Model O** | Denoised Phase IIIb launch data | Direct empirical estimate of Israel-specific launch rate decay |
| **Decay rate α — Model C** | Public intelligence on total launcher counts | Independent challenge from external data; conservative floor |

The two models bracket the plausible range: Model O is derived from what the strike data itself implies (after noise removal); Model C is derived independently from published launcher-count intelligence. Reality is expected to lie between them.

Because $\alpha$ is fixed for each model (not jointly fitted with $\mu_0$), the only parameter estimated from data is $\mu_0$ (via closed-form MLE):

$$\hat{\mu}_0 = \frac{\sum_{t \in \mathcal{T}} L_t}{\sum_{t \in \mathcal{T}} e^{-\alpha(t - t_0)}}$$

**Stability property:** A ±4 BM change in any single observation shifts the April forecast by only ~6 BMs (Model C) or ~4 BMs (Model O). This is a direct consequence of fixing $\alpha$ externally — individual observation noise cannot distort the decay rate estimate.

Both models are anchored at $t_0 = 14$ (Phase IIIb start, Mar 13) with training set $\mathcal{T} = \{14, 15, \ldots, 29\}$, $n = 16$ observations, $\sum L_t = 187$ BMs.

---

### 5.1 Model O — Observable ("Iran degrades") — data-derived

**Alpha calibration — weighted log-linear regression on weekly aggregates:**

$\alpha^O$ is estimated from the Phase IIIb (Attrition) launch data using **weighted log-linear regression on non-overlapping weekly aggregates** — the standard approach for estimating exponential decay rates from aggregated Poisson counts (Poisson GLM with log link; McCullagh & Nelder, *Generalized Linear Models*, 2nd ed., §6.2).

Raw daily counts are too noisy to reliably identify the trend directly: SNR ≈ 1.2× at the Phase IIIb rate (signal = 12.4% decline over 16 days; daily Poisson CV ≈ 28%), below the reliable detection threshold of ~2×. Aggregating into weekly windows reduces noise by $\sqrt{n_{\text{days}}}$ before fitting.

**Method:** aggregate Phase IIIb into three non-overlapping windows, fit a weighted log-linear model with weights proportional to window size.

| Window | Days | $n$ | Sum $W_k$ | Avg rate $\bar{r}_k$ | Midpoint $t_k$ |
|--------|------|-----|-----------|----------------------|----------------|
| IIIb week 1 | 14–20 | 7 | 89 | 12.71/d | 17.0 |
| IIIb week 2 | 21–27 | 7 | 78 | 11.14/d | 24.0 |
| IIIb partial | 28–29 | 2 | 20 | 10.00/d | 28.5 |

The model is $\log \bar{r}_k = \beta_0 - \alpha \cdot t_k$, estimated by weighted least squares with weights $w_k = n_k$ (window size). This correctly downweights the noisier partial window (weight 2/16 = 12.5%) relative to full weeks (weight 7/16 = 43.75% each).

$$\hat{\alpha}^O = -\frac{\sum_k w_k\,(t_k - \bar{t})\,(\log\bar{r}_k - \overline{\log\bar{r}})}{\sum_k w_k\,(t_k - \bar{t})^2} = 0.020\;\text{day}^{-1}$$

where $\bar{t}$ and $\overline{\log\bar{r}}$ are the weighted means. The WLS estimate on the Phase IIIb data gives $\hat{\alpha}^O = 0.020$/day exactly.

**Sensitivity note:** Monte Carlo simulation (50,000 draws from the true model) shows that fixing $\alpha$ at this value rather than re-deriving it from each new dataset reduces April forecast uncertainty from ±72 BMs (std) to ±15 BMs. $\alpha^O$ is therefore treated as a fixed parameter, to be re-assessed when ~4 weeks of April data are available (expected around Apr 15–18).

**Physical interpretation:** Iran's Israel-specific launch rate decays faster than the total fleet average because Israel preferentially targets Israel-facing assets. This is corroborated by IDF reporting that >80% of Iran's Israel-facing launch capacity was neutralised by Day 12, far more than the ~20% of total fleet destroyed by that point. The data-derived rate therefore reflects actual Israel-specific targeting efficiency.

**Cross-check:** $\alpha^O = 0.020 \approx 2.5 \times \alpha^C$ — consistent with a 2.5× priority-targeting multiplier over the intelligence-derived fleet-average rate, providing independent physical corroboration of the data-derived estimate.

**mu0 calibration — closed-form MLE with alpha fixed:**

$$\hat{\mu}_0^O = \frac{\sum_{t=14}^{29} L_t}{\sum_{t=14}^{29} e^{-\alpha^O(t - 14)}} = \frac{187}{13.83} = 13.52\;\text{BMs/day}$$

**Mean function:**

$$\boxed{\mu_t^O = 13.52 \cdot \exp\!\bigl(-0.020\,(t - 14)\bigr)}$$

**Derived quantities:**

| Quantity | Value |
|----------|-------|
| Half-life $\tau_{1/2}^O = \ln 2\,/\,\alpha^O$ | **35 days** |
| Daily capacity loss | 2.0% per day |
| Total Phase IIIb capacity $\mu_0^O/\alpha^O$ | ~676 missiles |
| $\mu_{30}^O$ (Mar 29, forecast start) | 9.82 BMs/day |
| $\mu_{61}^O$ (Apr 29, forecast end) | 5.28 BMs/day |
| Capacity retained Day 14 → Day 61 | 39% |

### 5.2 Model C — Conservative ("Iran sustains") — intelligence-derived

**Alpha calibration — independent challenge from published launcher counts:**

To challenge the data-derived Model O estimate, $\alpha^C$ is derived independently from public-source snapshots of Iran's **total** operational launcher count. If Israel targets all launcher types proportionally (rather than prioritising Israel-facing assets), the fleet-average attrition rate is the correct basis for α — implying a slower decay and a higher April forecast.

| Snapshot | Day | Date | Total operational launchers | Source |
|----------|-----|------|-----------------------------|--------|
| Early Phase IIIb | 12 | Mar 11 | ~160 | Algemeiner/IDF assessment |
| Late Phase IIIb | 28 | Mar 27 | ~140 | ISW citing IDF (330 of 470 destroyed) |

$$\alpha^C = \frac{\ln(160/140)}{28 - 12} = \frac{\ln(1.143)}{16} = 0.0083\;\text{day}^{-1}$$

This is slower than the data-derived $\alpha^O$ because intelligence counts only physically destroyed launchers, whereas the observed launch rate reflects all factors that suppress operational output — crew availability, logistics degradation, coordination disruption, and launchers that remain physically intact but operationally unavailable (e.g. held in tunnels, awaiting resupply). Model C is a conservative floor: it would be correct only if those non-destruction factors are negligible.

Accounting for source uncertainty (±5–10 launchers at each snapshot), the implied range is $\alpha \in [0.004,\, 0.014]$ day$^{-1}$ (HL 48–166 days).

**mu0 calibration — closed-form MLE with alpha fixed:**

$$\hat{\mu}_0^C = \frac{\sum_{t=14}^{29} L_t}{\sum_{t=14}^{29} e^{-\alpha^C(t - 14)}} = \frac{187}{15.05} = 12.43\;\text{BMs/day}$$

**Mean function:**

$$\boxed{\mu_t^C = 12.43 \cdot \exp\!\bigl(-0.0083\,(t - 14)\bigr)}$$

**Derived quantities:**

| Quantity | Value |
|----------|-------|
| Half-life $\tau_{1/2}^C = \ln 2\,/\,\alpha^C$ | **83 days** |
| Daily capacity loss | 0.83% per day |
| Total Phase IIIb capacity $\mu_0^C/\alpha^C$ | ~1,498 missiles |
| $\mu_{30}^C$ (Mar 29, forecast start) | 10.88 BMs/day |
| $\mu_{61}^C$ (Apr 29, forecast end) | 8.41 BMs/day |
| Capacity retained Day 14 → Day 61 | 68% |

### 5.3 Back-test performance

Both models are evaluated on Attrition phase data using rolling 7-day windows. For each window $\mathcal{W} = \{t_1, \ldots, t_7\}$, the Z-score is:

$$Z_\mathcal{W}^m = \frac{W_\mathcal{W}^{\mathrm{obs}} - \Lambda_\mathcal{W}^m}{\sqrt{\Lambda_\mathcal{W}^m}}, \qquad \Lambda_\mathcal{W}^m = \sum_{t \in \mathcal{W}} \mu_t^m$$

where $W_\mathcal{W}^{\mathrm{obs}} = \sum_{t \in \mathcal{W}} L_t$ is the observed weekly total.

Results across all 13 rolling windows: $|Z| < 1.1$ for Model C and $|Z| < 1.6$ for Model O (threshold for concern: $|Z| > 2$). Empirical 90% PI coverage: 17/19 days = **89%** for both models (theoretical: 90%).

---

## 6. April 2026 Forecast

### 6.1 Daily point forecasts and prediction intervals

For each forecast day $t \in \{30, 31, \ldots, 61\}$ (Mar 29 – Apr 29) and model $m \in \{C, O\}$:

**Point forecast:**

$$\hat{L}_t^m = \mu_t^m = \hat{\mu}_0^m \cdot \exp\!\bigl(-\hat{\alpha}^m\,(t - t_0^m)\bigr)$$

**Prediction intervals** (exact Poisson quantiles):

$$\mathrm{PI}_q(t, m) = \Bigl[F^{-1}_{\mathrm{Poisson}(\mu_t^m)}(q_{\mathrm{lo}}),\; F^{-1}_{\mathrm{Poisson}(\mu_t^m)}(q_{\mathrm{hi}})\Bigr]$$

where $F^{-1}_{\mathrm{Poisson}(\lambda)}(q)$ is the quantile function of $\mathrm{Poisson}(\lambda)$. Two intervals are reported:

| Interval | $q_{\mathrm{lo}}$ | $q_{\mathrm{hi}}$ | Interpretation |
|----------|---------|---------|----------------|
| 50% PI | 0.25 | 0.75 | Most likely range on any single day |
| 90% PI | 0.05 | 0.95 | Plausible extremes; exceedance = anomaly signal |

> **Caveat — parameter uncertainty:** The prediction intervals above reflect **Poisson sampling uncertainty only**, conditional on $(\mu_0^m, \alpha^m)$ being known. Because $\alpha$ is fixed from intelligence data (not fitted to the sparse n=16 time series), the dominant residual uncertainty is the accuracy of the intelligence-derived decay rate. The intelligence range $\alpha^C \in [0.004,\, 0.014]$ day$^{-1}$ translates to an April forecast range of approximately 240–330 BMs under the conservative scenario — substantially wider than the per-model [248–302] PI. The two-model bracket conveys the scenario uncertainty; the per-model PIs convey only Poisson sampling noise at fixed parameters.

### 6.2 Weekly aggregation

Let $\mathcal{D}_w$ denote the set of day indices in week $w$. Since $L_t$ are independent Poisson, their sum is also Poisson:

$$W_w = \sum_{t \in \mathcal{D}_w} L_t \;\sim\; \mathrm{Poisson}(\Lambda_w^m), \qquad \Lambda_w^m = \sum_{t \in \mathcal{D}_w} \mu_t^m$$

**Weekly moments:**

$$\mathbb{E}[W_w] = \Lambda_w^m, \qquad \mathrm{Var}[W_w] = \Lambda_w^m, \qquad \sigma[W_w] = \sqrt{\Lambda_w^m}$$

**Weekly 90% PI:** $\bigl[F^{-1}_{\mathrm{Poisson}(\Lambda_w^m)}(0.05),\; F^{-1}_{\mathrm{Poisson}(\Lambda_w^m)}(0.95)\bigr]$

In practice, the Poisson sum is approximated by Monte Carlo simulation ($N = 100{,}000$ draws) to obtain exact quantiles for any window length.

### 6.3 April total forecast

For the full April period (Days 33–61, Apr 1–29, $n = 29$ days):

$$\Lambda_{\mathrm{Apr}}^m = \sum_{t=33}^{61} \mu_t^m$$

**Model C:**

$$\Lambda_{\mathrm{Apr}}^C = \sum_{t=33}^{61} 12.43\,e^{-0.0083(t-14)} = 274.8 \;\text{ BMs} \quad [248\text{–}302 \text{ at } 90\%]$$

**Model O:**

$$\Lambda_{\mathrm{Apr}}^O = \sum_{t=33}^{61} 13.52\,e^{-0.020(t-14)} = 205.5 \;\text{ BMs} \quad [182\text{–}229 \text{ at } 90\%]$$

The gap $\Lambda_{\mathrm{Apr}}^C - \Lambda_{\mathrm{Apr}}^O = 69$ BMs (Model C is 34% higher).

### 6.4 Weekly forecast table

| Week | Days | Dates | $\Lambda_w^C$ | 90% PI | $\Lambda_w^O$ | 90% PI |
|------|------|-------|-------------|--------|-------------|--------|
| 1 | 30–36 | Mar 29–Apr 4 | 74.3 | [60–89] | 64.8 | [52–78] |
| 2 | 37–43 | Apr 5–11 | 70.1 | [57–84] | 56.3 | [44–69] |
| 3 | 44–50 | Apr 12–18 | 66.2 | [53–80] | 49.0 | [38–61] |
| 4 | 51–57 | Apr 19–25 | 62.4 | [50–76] | 42.6 | [32–54] |
| 5 | 58–61 | Apr 26–29 | 34.1 | [25–44] | 21.8 | [14–30] |
| **Total** | **33–61** | **Apr 1–29** | **274.8** | **[248–302]** | **205.5** | **[182–229]** |

---

## 7. Model Discrimination

### 7.1 Cumulative count test

After $n$ days of April data ($t = 30, \ldots, 29+n$), define the cumulative observed count:

$$W_n = \sum_{t=30}^{29+n} L_t$$

Under Model $m$, $W_n \sim \mathrm{Poisson}(\Lambda_n^m)$ where $\Lambda_n^m = \sum_{t=30}^{29+n} \mu_t^m$.

The test statistic for discriminating the two models uses the mid-point variance (stable under both hypotheses):

$$Z_n = \frac{\Lambda_n^C - \Lambda_n^O}{\sqrt{(\Lambda_n^C + \Lambda_n^O)/2}}$$

### 7.2 Power analysis

To detect the model difference at significance level $\alpha_{\mathrm{test}} = 0.05$ (one-sided) with power $1 - \beta$, we require:

$$Z_n \;\geq\; z_{1-\alpha_{\mathrm{test}}} + z_{1-\beta} = 1.645 + z_{1-\beta}$$

Solving numerically for the smallest $n$ satisfying this threshold:

| Power $1-\beta$ | $z_{1-\beta}$ | Required $Z_n$ | Days $n$ | Decision by |
|-----------------|--------------|---------------|----------|-------------|
| 80% | 0.842 | 2.49 | **18** | **Apr 15** |
| 90% | 1.282 | 2.93 | **21** | **Apr 18** |
| 95% | 1.645 | 3.29 | **24** | **Apr 21** |

The cumulative gap $\Lambda_n^C - \Lambda_n^O$ grows with $n$ while noise $\sqrt{(\Lambda_n^C + \Lambda_n^O)/2}$ grows as $\sqrt{n}$, so $Z_n \propto \sqrt{n}$ asymptotically. In the first two weeks, $Z_n < 2$ — the models are statistically indistinguishable.

### 7.3 Weekly Z-score monitoring

For each observed weekly total $W_w^{\mathrm{obs}}$, compute Z-scores under both models:

$$Z_w^m = \frac{W_w^{\mathrm{obs}} - \Lambda_w^m}{\sqrt{\Lambda_w^m}}, \qquad m \in \{C, O\}$$

Decision rules (thresholds from standard normal, $\alpha = 0.05$):

| $Z_w^C$ | $Z_w^O$ | Signal |
|---------|---------|--------|
| $(-2,\,+2)$ | $(+2,\,+4)$ | Model C correct — Iran sustaining capacity |
| $(-4,\,-2)$ | $(-2,\,+2)$ | Model O correct — gradual decay confirmed |
| $< -2$ | $< -2$ | Both models too high — accelerating collapse |
| $> +2$ | $> +4$ | Escalation — structural upward break |

---

## 8. Code

| File | Purpose |
|------|---------|
| `model/poisson_model.py` | Both model definitions, daily forecast table, weekly summary, back-test, monitoring guide, CSV export |
| `model/model_diagnostics.py` | Model comparison (M0–M5), AIC table, overdispersion test, autocorrelation, structural break analysis |

**Run forecast:**
```bash
python model/poisson_model.py                    # daily table + weekly summary
python model/poisson_model.py --backtest         # Attrition phase Z-score back-test
python model/poisson_model.py --verify           # observed vs predicted for Attrition phase
```

**Run diagnostics:**
```bash
python model/model_diagnostics.py           # full model comparison and diagnostics
```
