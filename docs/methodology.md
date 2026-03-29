# Iran BM Strike Model — Methodology & Model Specification

**Project:** Iran–Israel War 2026 — Iranian Ballistic Missile Strike Analysis
**Last updated:** 2026-03-29
**Data scope:** Iranian BM launched toward Israel, Feb 28 – Mar 28, 2026 (Days 1–29)

---

## 1. Objective

Model the stochastic process governing Iranian ballistic missile (BM) launches toward Israel during Phase III of the war, and generate calibrated daily and weekly forecasts for April 2026.

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
| Phase I | 1–4 | `bbc_prop` | JINSA Mar5 PDF direct count scaled by BBC/IDF 128 anchor |
| Phase I residual | 5 | `bbc_residual` | 128 minus sum of Days 1–4 estimates |
| Transition | 6–10 | `anchor_prop` | Alma waves proportioned to 150-BM budget (300−128−22) |
| Phase III early | 11 | `jinsa_direct` | JINSA Mar11 PDF direct Israel count |
| Phase III | 12–17 | `wave_ratio` | Alma waves × 1.11 (ratio calibrated from JINSA÷Alma Mar18–24) |
| Phase III | 18–25 | `jinsa_direct` / `multi_source` | JINSA Mar24 PDF Chart 2 direct readings |
| Phase III late | 26–29 | `jinsa_derived` / `media_count` | Derived from global minus confirmed non-Israel |

### Anchor constraints satisfied

| Date | Cumulative | Source | Status |
|------|-----------|--------|--------|
| Mar 4 | 128 | BBC Arabic citing IDF | ✓ exact |
| Mar 10 | ~300 (precise: 285) | IDF IAF briefing via Walla/N12 | ✓ isr_cumul=301 |
| Mar 27 | >450 | Times of Israel citing IDF | ✓ isr_cumul=507 |

---

## 3. Phase Definitions

| Phase | Days | Dates | Characterisation |
|-------|------|-------|-----------------|
| I | 1–4 | Feb 28 – Mar 3 | Saturation: large coordinated salvos, 14–50 BMs/day |
| II | 5–10 | Mar 4 – Mar 9 | Rapid collapse: transition from saturation to stochastic |
| IIIa | 11–13 | Mar 10–12 | Late transition: tail of Phase II collapse still visible |
| **IIIb** | **14–29** | **Mar 13–28** | **Persistent stochastic regime: true Phase III** |

Phase III start was determined empirically via AIC minimisation across candidate start days (Day 8–15). Day 14 (Mar 13) minimises AIC and coincides with V/M ratio stabilising at 0.99 (Poisson-consistent).

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
| $t_0$ | Phase III anchor day (model-specific) |
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

Six candidate models were compared on Phase III data ($n = 19$ days):

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

### 4.6 Phase III start detection

Phase III start is identified by three converging lines of evidence, all pointing to Day 14 (Mar 13):

1. **M4 structural break.** The best-fitting piecewise Poisson model places its internal breakpoint at Day 14, after which the decay rate drops from $\alpha_1 \approx 0.149$/day (half-life 4.7 days) to $\alpha_2 \approx 0.007$/day. This break is identified on a fixed dataset and is therefore a valid within-sample comparison.

2. **Variance-to-mean ratio.** The V/M ratio $\hat{\sigma}^2 / \bar{L}$ approaches 1.0 (Poisson-consistent) in the Days 14–29 window, and all 7-day back-test windows from Day 14 onward return $|Z| < 1.1$ under both models.

3. **AIC scan (indicative).** Fitting the Poisson exponential to each candidate window $\mathcal{T}(t_0) = \{t \geq t_0\}$ and comparing AIC across candidates is **not strictly valid** — AIC is defined for fixed $n$ and rankings across different sample sizes are not meaningful. This scan is treated as suggestive only; the primary identification of $t_0 = 14$ rests on items 1 and 2.

Days 11–13 (Phase IIIa) are treated as a late-transition tail of Phase II collapse and excluded from the Phase IIIb stable regime.

---

## 5. Model Calibration

Two variants are maintained, reflecting genuine uncertainty in the forward decay rate. They differ in the choice of training set $\mathcal{T}$.

### 5.1 Model C — Conservative ("Iran sustains")

**Training set:** $\mathcal{T}_C = \{t : 14 \leq t \leq 29\}$, $n = 16$ observations (Mar 13–28).

**Rationale for anchor:** The piecewise model (best AIC) identifies a structural break at Day 14, after which the system enters a near-flat Phase IIIb regime. Model C is anchored at this settled regime, treating Days 11–13 as a transitional artefact.

**Likelihood:**

$$\ell_C(\mu_0, \alpha) = \sum_{t=14}^{29} \Bigl[ L_t\bigl(\log\mu_0 - \alpha(t - 14)\bigr) - \mu_0\,e^{-\alpha(t-14)} \Bigr]$$

**Parameters** (calibrated from the M4 post-break arm):

$$\mu_0^C = 11.75, \qquad \alpha^C = 0.007\;\text{day}^{-1}$$

> **Note:** These values correspond to the Phase IIIb segment of the jointly-fitted M4 piecewise model, not an independent MLE on Days 14–29 alone. An unconstrained MLE on Days 14–29 yields $\hat{\mu}_0 \approx 12.6$, $\hat{\alpha} \approx 0.013$ (half-life ~53 days); however, on that window the flat Poisson is preferred by AIC ($\Delta\mathrm{AIC} \approx +1.4$ for exponential vs flat), so no exponential decay is robustly identified in Phase IIIb independently. Model C is best understood as the M4-extrapolated slow-decay scenario, representing the upper end of plausible decay rates given Phase IIIb data.

**Mean function:**

$$\boxed{\mu_t^C = 11.75 \cdot \exp\!\bigl(-0.007\,(t - 14)\bigr)}$$

**Derived quantities:**

| Quantity | Value |
|----------|-------|
| Half-life $\tau_{1/2}^C = \ln 2\,/\,\hat{\alpha}^C$ | **99 days** |
| Daily capacity loss | 0.7% per day |
| $\mu_{30}^C$ (Mar 29, forecast start) | 10.51 BMs/day |
| $\mu_{61}^C$ (Apr 29, forecast end) | 8.46 BMs/day |
| Capacity retained Day 30 → Day 61 | 80% |

### 5.2 Model O — Optimistic ("Iran degrades")

**Training set:** $\mathcal{T}_O = \{t : 11 \leq t \leq 29\}$, $n = 19$ observations (Mar 10–28).

**Rationale for anchor:** The single Poisson exponential fitted to the full Phase III arc (Days 11–29, from 22 BMs/day down to 6 BMs/day) captures the overall downward trend, treating the entire decline — including IIIa — as a continuing degradation process rather than a one-off transition.

**Likelihood:**

$$\ell_O(\mu_0, \alpha) = \sum_{t=11}^{29} \Bigl[ L_t\bigl(\log\mu_0 - \alpha(t - 11)\bigr) - \mu_0\,e^{-\alpha(t-11)} \Bigr]$$

**MLEs:**

$$\hat{\mu}_0^O = 14.45, \qquad \hat{\alpha}^O = 0.021\;\text{day}^{-1}$$

**Mean function:**

$$\boxed{\mu_t^O = 14.45 \cdot \exp\!\bigl(-0.021\,(t - 11)\bigr)}$$

**Derived quantities:**

| Quantity | Value |
|----------|-------|
| Half-life $\tau_{1/2}^O = \ln 2\,/\,\hat{\alpha}^O$ | **33 days** |
| Daily capacity loss | 2.1% per day |
| $\mu_{30}^O$ (Mar 29, forecast start) | 9.70 BMs/day |
| $\mu_{61}^O$ (Apr 29, forecast end) | 5.06 BMs/day |
| Capacity retained Day 30 → Day 61 | 52% |

### 5.3 Back-test performance

Both models are evaluated on Phase III data using rolling 7-day windows. For each window $\mathcal{W} = \{t_1, \ldots, t_7\}$, the Z-score is:

$$Z_\mathcal{W}^m = \frac{W_\mathcal{W}^{\mathrm{obs}} - \Lambda_\mathcal{W}^m}{\sqrt{\Lambda_\mathcal{W}^m}}, \qquad \Lambda_\mathcal{W}^m = \sum_{t \in \mathcal{W}} \mu_t^m$$

where $W_\mathcal{W}^{\mathrm{obs}} = \sum_{t \in \mathcal{W}} L_t$ is the observed weekly total.

Results across all 13 rolling windows: $|Z| < 1.1$ for both models (threshold for concern: $|Z| > 2$). Empirical 90% PI coverage: 17/19 days = **89%** (theoretical: 90%).

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

> **Caveat — parameter uncertainty:** The prediction intervals above reflect **Poisson sampling uncertainty only**, conditional on the model parameters $(\mu_0^m, \alpha^m)$ being known. Profile likelihood 95% confidence intervals for $\alpha$ span approximately $[0.001,\, 0.044]$ day$^{-1}$ (half-life 16–693 days) for both training windows — the decay rate is poorly constrained at $n = 16$–$19$ observations. Both Model C ($\alpha = 0.007$) and Model O ($\alpha = 0.021$) lie within the same 95% CI. Parameter estimation uncertainty is the dominant source of forecast error and substantially widens the true uncertainty band beyond the reported PIs. The two-model scenario bracket is the practical substitute for a full uncertainty propagation.

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

$$\Lambda_{\mathrm{Apr}}^C = \sum_{t=33}^{61} 11.75\,e^{-0.007(t-14)} = 270.9 \;\text{ BMs} \quad [244\text{–}298 \text{ at } 90\%]$$

**Model O:**

$$\Lambda_{\mathrm{Apr}}^O = \sum_{t=33}^{61} 14.45\,e^{-0.021(t-11)} = 199.8 \;\text{ BMs} \quad [177\text{–}223 \text{ at } 90\%]$$

The gap $\Lambda_{\mathrm{Apr}}^C - \Lambda_{\mathrm{Apr}}^O = 71$ BMs (Model C is 36% higher).

### 6.4 Weekly forecast table

| Week | Days | Dates | $\Lambda_w^C$ | 90% PI | $\Lambda_w^O$ | 90% PI |
|------|------|-------|-------------|--------|-------------|--------|
| 1 | 30–36 | Mar 29–Apr 4 | 72.0 | [58–86] | 63.8 | [51–77] |
| 2 | 37–43 | Apr 5–11 | 68.6 | [55–82] | 55.1 | [43–68] |
| 3 | 44–50 | Apr 12–18 | 65.3 | [52–79] | 47.5 | [37–59] |
| 4 | 51–57 | Apr 19–25 | 62.2 | [50–75] | 41.0 | [31–52] |
| 5 | 58–61 | Apr 26–29 | 34.2 | [25–44] | 20.9 | [14–29] |
| **Total** | **33–61** | **Apr 1–29** | **270.9** | **[244–298]** | **199.8** | **[177–223]** |

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
| 80% | 0.842 | 2.49 | **19** | **Apr 16** |
| 90% | 1.282 | 2.93 | **22** | **Apr 19** |
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
python model/poisson_model.py --backtest         # Phase III Z-score back-test
python model/poisson_model.py --verify           # observed vs predicted Phase III
```

**Run diagnostics:**
```bash
python model/model_diagnostics.py           # full model comparison and diagnostics
```
