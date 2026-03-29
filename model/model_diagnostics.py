"""
Iran BM Model Diagnostics & Model Selection

Tests the current Poisson assumption rigorously and compares:
  M0: Poisson, flat rate           (1 param)
  M1: Poisson, exponential decay   (2 params)  ← current model
  M2: NB, flat rate                (2 params)
  M3: NB, exponential decay        (3 params)
  M4: Poisson, piecewise-exp decay (3 params, structural break)
  M5: NB, piecewise-exp decay      (4 params, structural break)

Diagnostics:
  - Pearson chi-square overdispersion test
  - Lag-1 autocorrelation of Pearson residuals
  - Ljung-Box test
  - Rolling 5-day mean to visualise trend
  - AIC/BIC comparison table

Usage:
    python model_diagnostics.py
"""

import math
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import chi2 as chi2_dist

DATA_FILE = Path(__file__).parent.parent / "data" / "israel_daily_estimate.csv"
PHASE3_START = 11   # Day 11 = Mar 10 (IDF ~300 cumulative anchor; natural Phase II→III boundary)


# ── data ──────────────────────────────────────────────────────────────────────

def load_phase3():
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    df = df.sort_values("day_num").reset_index(drop=True)
    p3 = df[df["day_num"] >= PHASE3_START].dropna(subset=["isr_bm"]).copy()
    p3["t"] = p3["day_num"] - PHASE3_START   # t=0 at Phase III start
    return p3


# ── log-likelihoods ───────────────────────────────────────────────────────────

def ll_poisson(obs, mus):
    """Poisson log-likelihood sum."""
    total = 0.0
    for y, mu in zip(obs, mus):
        if mu <= 0:
            return -1e12
        total += y * math.log(mu) - mu - math.lgamma(y + 1)
    return total


def nb_logpmf(x, mu, k):
    x = int(round(x))
    if mu <= 0 or k <= 0 or x < 0:
        return -1e12
    return (
        math.lgamma(x + k) - math.lgamma(k) - math.lgamma(x + 1)
        + k * math.log(k / (k + mu))
        + x * math.log(mu / (k + mu))
    )


def ll_nb(obs, mus, k):
    return sum(nb_logpmf(y, mu, k) for y, mu in zip(obs, mus))


# ── model fits ────────────────────────────────────────────────────────────────

def fit_m0_poisson_flat(t, obs):
    """M0: Poisson flat. MLE = sample mean."""
    mu0 = np.mean(obs)
    mus = np.full(len(obs), mu0)
    ll = ll_poisson(obs, mus)
    return {"name": "M0 Poisson flat", "params": 1,
            "mu0": mu0, "alpha": 0.0, "k": np.inf,
            "ll": ll, "mus": mus}


def fit_m1_poisson_exp(t, obs):
    """M1: Poisson exponential decay."""
    def nll(p):
        mu0, log_alpha = p
        alpha = math.exp(log_alpha)
        mus = [mu0 * math.exp(-alpha * ti) for ti in t]
        return -ll_poisson(obs, mus)

    best = None
    for mu0_init in [8, 12, 16]:
        for alpha_init in [0.005, 0.02, 0.08]:
            res = minimize(nll, [mu0_init, math.log(alpha_init)],
                           method="L-BFGS-B",
                           bounds=[(0.5, 100), (math.log(0.001), math.log(0.5))])
            if best is None or res.fun < best.fun:
                best = res

    mu0, log_alpha = best.x
    alpha = math.exp(log_alpha)
    mus = [mu0 * math.exp(-alpha * ti) for ti in t]
    ll = ll_poisson(obs, mus)
    return {"name": "M1 Poisson exp", "params": 2,
            "mu0": mu0, "alpha": alpha, "k": np.inf,
            "ll": ll, "mus": mus}


def fit_m2_nb_flat(t, obs):
    """M2: NB flat rate."""
    def nll(p):
        mu0, log_k = p
        k = math.exp(log_k)
        mus = np.full(len(obs), mu0)
        return -ll_nb(obs, mus, k)

    res = minimize(nll, [np.mean(obs), math.log(9)],
                   method="L-BFGS-B",
                   bounds=[(0.5, 100), (math.log(0.3), math.log(1000))])
    mu0, log_k = res.x
    k = math.exp(log_k)
    mus = np.full(len(obs), mu0)
    ll = ll_nb(obs, mus, k)
    return {"name": "M2 NB flat", "params": 2,
            "mu0": mu0, "alpha": 0.0, "k": k,
            "ll": ll, "mus": mus}


def fit_m3_nb_exp(t, obs):
    """M3: NB exponential decay."""
    def nll(p):
        mu0, log_alpha, log_k = p
        alpha = math.exp(log_alpha)
        k = math.exp(log_k)
        mus = [mu0 * math.exp(-alpha * ti) for ti in t]
        return -ll_nb(obs, mus, k)

    best = None
    for mu0_init in [8, 12, 16]:
        for alpha_init in [0.005, 0.02, 0.08]:
            for k_init in [2, 9, 50]:
                res = minimize(nll,
                               [mu0_init, math.log(alpha_init), math.log(k_init)],
                               method="L-BFGS-B",
                               bounds=[(0.5, 100),
                                       (math.log(0.001), math.log(0.5)),
                                       (math.log(0.3), math.log(500))])
                if best is None or res.fun < best.fun:
                    best = res

    mu0, log_alpha, log_k = best.x
    alpha = math.exp(log_alpha)
    k = math.exp(log_k)
    mus = [mu0 * math.exp(-alpha * ti) for ti in t]
    ll = ll_nb(obs, mus, k)
    return {"name": "M3 NB exp", "params": 3,
            "mu0": mu0, "alpha": alpha, "k": k,
            "ll": ll, "mus": mus}


def fit_m4_poisson_piecewise(t, obs, days):
    """
    M4: Poisson piecewise-exponential.
    Before break day τ: mu_t = mu0 * exp(-alpha1 * t)
    After break day τ:  mu_t = mu_tau * exp(-alpha2 * (t - tau))
    where mu_tau = mu0 * exp(-alpha1 * tau)

    τ is searched over candidate break days; best AIC returned.
    """
    best_fit = None
    # Try each candidate internal breakpoint (must have ≥3 obs on each side)
    for break_idx in range(3, len(t) - 2):
        tau = t[break_idx]

        def nll(p):
            mu0, log_a1, log_a2 = p
            a1 = math.exp(log_a1)
            a2 = math.exp(log_a2)
            mus = []
            for ti in t:
                if ti < tau:
                    mus.append(mu0 * math.exp(-a1 * ti))
                else:
                    mu_tau = mu0 * math.exp(-a1 * tau)
                    mus.append(mu_tau * math.exp(-a2 * (ti - tau)))
            return -ll_poisson(obs, mus)

        fit_result = None
        for mu0_init in [8, 12, 16]:
            for a1_init in [0.005, 0.02]:
                for a2_init in [0.02, 0.10, 0.25]:
                    res = minimize(nll,
                                   [mu0_init, math.log(a1_init), math.log(a2_init)],
                                   method="L-BFGS-B",
                                   bounds=[(0.5, 100),
                                           (math.log(0.001), math.log(0.5)),
                                           (math.log(0.001), math.log(0.9))])
                    if fit_result is None or res.fun < fit_result.fun:
                        fit_result = res

        mu0, log_a1, log_a2 = fit_result.x
        a1, a2 = math.exp(log_a1), math.exp(log_a2)
        mus = []
        for ti in t:
            if ti < tau:
                mus.append(mu0 * math.exp(-a1 * ti))
            else:
                mu_tau = mu0 * math.exp(-a1 * tau)
                mus.append(mu_tau * math.exp(-a2 * (ti - tau)))

        ll = ll_poisson(obs, mus)
        aic = 2 * 3 - 2 * ll   # 3 params: mu0, alpha1, alpha2

        break_day = days[break_idx]
        candidate = {"name": f"M4 Poisson piecewise (break Day{break_day})",
                     "params": 3, "mu0": mu0, "alpha1": a1, "alpha2": a2,
                     "break_day": break_day, "tau": tau,
                     "ll": ll, "aic": aic, "mus": mus}
        if best_fit is None or aic < best_fit["aic"]:
            best_fit = candidate

    return best_fit


def fit_m5_nb_piecewise(t, obs, days):
    """M5: NB piecewise-exponential (structural break + overdispersion)."""
    best_fit = None
    for break_idx in range(3, len(t) - 2):
        tau = t[break_idx]

        def nll(p):
            mu0, log_a1, log_a2, log_k = p
            a1 = math.exp(log_a1)
            a2 = math.exp(log_a2)
            k = math.exp(log_k)
            mus = []
            for ti in t:
                if ti < tau:
                    mus.append(mu0 * math.exp(-a1 * ti))
                else:
                    mu_tau = mu0 * math.exp(-a1 * tau)
                    mus.append(mu_tau * math.exp(-a2 * (ti - tau)))
            return -ll_nb(obs, mus, k)

        fit_result = None
        for mu0_init in [8, 12, 16]:
            for a1_init in [0.005, 0.02]:
                for a2_init in [0.02, 0.10]:
                    for k_init in [2, 9]:
                        res = minimize(nll,
                                       [mu0_init, math.log(a1_init),
                                        math.log(a2_init), math.log(k_init)],
                                       method="L-BFGS-B",
                                       bounds=[(0.5, 100),
                                               (math.log(0.001), math.log(0.5)),
                                               (math.log(0.001), math.log(0.9)),
                                               (math.log(0.3), math.log(500))])
                        if fit_result is None or res.fun < fit_result.fun:
                            fit_result = res

        mu0, log_a1, log_a2, log_k = fit_result.x
        a1, a2, k = math.exp(log_a1), math.exp(log_a2), math.exp(log_k)
        mus = []
        for ti in t:
            if ti < tau:
                mus.append(mu0 * math.exp(-a1 * ti))
            else:
                mu_tau = mu0 * math.exp(-a1 * tau)
                mus.append(mu_tau * math.exp(-a2 * (ti - tau)))

        ll = ll_nb(obs, mus, k)
        aic = 2 * 4 - 2 * ll   # 4 params

        break_day = days[break_idx]
        candidate = {"name": f"M5 NB piecewise (break Day{break_day})",
                     "params": 4, "mu0": mu0, "alpha1": a1, "alpha2": a2, "k": k,
                     "break_day": break_day, "tau": tau,
                     "ll": ll, "aic": aic, "mus": mus}
        if best_fit is None or aic < best_fit["aic"]:
            best_fit = candidate

    return best_fit


# ── diagnostics ───────────────────────────────────────────────────────────────

def pearson_diagnostics(obs, mus, model_name, n_params):
    """
    Pearson residuals + overdispersion test.
    Under Poisson: sum(r²) / (n - p) ~ 1
    Significantly > 1 means overdispersion (NB better).
    """
    residuals = [(y - mu) / math.sqrt(mu) for y, mu in zip(obs, mus)]
    n = len(obs)
    chi2_stat = sum(r**2 for r in residuals)
    df = n - n_params
    dispersion = chi2_stat / df
    p_value = 1 - chi2_dist.cdf(chi2_stat, df)  # probability of >= this chi2 under Poisson

    # Lag-1 autocorrelation of Pearson residuals
    r = np.array(residuals)
    if len(r) > 2:
        ac1 = np.corrcoef(r[:-1], r[1:])[0, 1]
    else:
        ac1 = float("nan")

    return {
        "residuals": residuals,
        "chi2": chi2_stat,
        "df": df,
        "dispersion": dispersion,
        "p_value_overdispersion": p_value,
        "ac1": ac1,
    }


def ljung_box(residuals, lags=3):
    """Ljung-Box Q-statistic for autocorrelation up to given lags."""
    r = np.array(residuals)
    n = len(r)
    acfs = []
    for k in range(1, lags + 1):
        c = np.corrcoef(r[:-k], r[k:])[0, 1]
        acfs.append(c)
    Q = n * (n + 2) * sum(ac**2 / (n - k) for k, ac in enumerate(acfs, 1))
    p = 1 - chi2_dist.cdf(Q, lags)
    return Q, p, acfs


def rolling_mean(obs, days, dates, window=5):
    arr = np.array(obs, dtype=float)
    means = []
    for i in range(len(arr)):
        lo = max(0, i - window // 2)
        hi = min(len(arr), i + window // 2 + 1)
        means.append(arr[lo:hi].mean())
    return means


# ── AIC / BIC table ───────────────────────────────────────────────────────────

def aic_bic(ll, n_params, n_obs):
    aic = 2 * n_params - 2 * ll
    bic = math.log(n_obs) * n_params - 2 * ll
    return aic, bic


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    p3 = load_phase3()
    t = p3["t"].values
    obs = p3["isr_bm"].values
    days = p3["day_num"].values
    dates = p3["date"].dt.strftime("%b %d").values
    n = len(obs)

    print("═" * 72)
    print("  Iran BM Model Diagnostics & Model Selection")
    print(f"  Phase III data: {dates[0]} – {dates[-1]}  (n={n} days)")
    print("═" * 72)

    # ── Rolling mean (trend visualisation) ────────────────────────────────────
    print("\n── Rolling 5-day mean (trend) ────────────────────────────────────────")
    print(f"  {'Date':<10} {'Day':>3} {'Obs':>5} {'5d-avg':>7}  Trend")
    print("  " + "-" * 48)
    roll = rolling_mean(obs, days, dates)
    prev = None
    for i, (date, day, ob, rm) in enumerate(zip(dates, days, obs, roll)):
        if prev is None:
            arrow = "  "
        elif rm > prev + 0.3:
            arrow = "↑ "
        elif rm < prev - 0.3:
            arrow = "↓ "
        else:
            arrow = "→ "
        bar = "█" * int(ob)
        print(f"  {date:<10} {day:>3} {ob:>5.0f}  {rm:>6.1f}  {arrow}{bar}")
        prev = rm

    # ── Fit all models ─────────────────────────────────────────────────────────
    print("\n── Fitting models ────────────────────────────────────────────────────")
    m0 = fit_m0_poisson_flat(t, obs)
    print("  M0 done")
    m1 = fit_m1_poisson_exp(t, obs)
    print("  M1 done")
    m2 = fit_m2_nb_flat(t, obs)
    print("  M2 done")
    m3 = fit_m3_nb_exp(t, obs)
    print("  M3 done")
    m4 = fit_m4_poisson_piecewise(t, obs, days)
    print("  M4 done")
    m5 = fit_m5_nb_piecewise(t, obs, days)
    print("  M5 done")

    # ── Model comparison table ─────────────────────────────────────────────────
    print("\n── Model Comparison (AIC / BIC) ──────────────────────────────────────")
    print(f"  {'Model':<38} {'Params':>6} {'LogLik':>8} {'AIC':>8} {'BIC':>8}  Key params")
    print("  " + "-" * 90)

    all_models = [m0, m1, m2, m3, m4, m5]
    aics = []
    for m in all_models:
        a, b = aic_bic(m["ll"], m["params"], n)
        m["aic"] = a
        m["bic"] = b
        aics.append(a)

    best_aic = min(aics)
    for m in all_models:
        marker = " ◄ BEST" if abs(m["aic"] - best_aic) < 0.01 else ""
        if m.get("alpha1"):
            key = (f"mu0={m['mu0']:.2f} α1={m['alpha1']:.4f} "
                   f"α2={m['alpha2']:.4f} break=Day{m['break_day']}")
            if m.get("k"):
                key += f" k={m['k']:.1f}"
        elif m.get("alpha"):
            key = f"mu0={m['mu0']:.2f} α={m['alpha']:.4f}"
            if m.get("k") and not math.isinf(m["k"]):
                key += f" k={m['k']:.1f}"
        else:
            key = f"mu0={m['mu0']:.2f}"
            if m.get("k") and not math.isinf(m["k"]):
                key += f" k={m['k']:.1f}"
        print(f"  {m['name']:<38} {m['params']:>6} {m['ll']:>8.2f} "
              f"{m['aic']:>8.2f} {m['bic']:>8.2f}  {key}{marker}")

    delta_aics = [(m["aic"] - best_aic, m["name"]) for m in all_models]
    print(f"\n  ΔAIC from best:")
    for da, name in sorted(delta_aics):
        support = "strong support" if da < 2 else ("weak" if da < 4 else ("none" if da < 10 else "reject"))
        print(f"    {name:<38}  ΔAIC={da:>6.2f}  ({support})")

    # ── Overdispersion test on best Poisson model ──────────────────────────────
    print("\n── Overdispersion / Residual Diagnostics (Poisson models) ───────────")
    for m in [m0, m1, m4]:
        diag = pearson_diagnostics(obs, m["mus"], m["name"], m["params"])
        Q, pQ, acfs = ljung_box(diag["residuals"], lags=3)
        print(f"\n  {m['name']}")
        print(f"    Pearson χ²/df = {diag['chi2']:.2f} / {diag['df']} "
              f"= {diag['dispersion']:.3f}  "
              f"(p={diag['p_value_overdispersion']:.3f})")
        print(f"    Interpretation: ", end="")
        d = diag["dispersion"]
        if d < 0.7:
            print("underdispersed — Poisson may overfit this data")
        elif d < 1.3:
            print("well-calibrated — Poisson assumption plausible")
        elif d < 2.0:
            print("mildly overdispersed — consider NB")
        else:
            print("strongly overdispersed — NB needed")
        print(f"    Lag-1 autocorrelation of residuals: {diag['ac1']:+.3f}", end="")
        if abs(diag["ac1"]) > 0.3:
            print("  ← notable autocorrelation")
        else:
            print("  (low)")
        print(f"    Ljung-Box Q(3) = {Q:.2f}  p = {pQ:.3f}", end="")
        print("  ← serial correlation likely" if pQ < 0.05 else "  (no serial correlation)")
        print(f"    ACF(1,2,3): {acfs[0]:+.3f}  {acfs[1]:+.3f}  {acfs[2]:+.3f}")

    # ── Structural break detail ────────────────────────────────────────────────
    print(f"\n── Structural Break Analysis ─────────────────────────────────────────")
    print(f"  Best piecewise Poisson (M4): break at Day {m4['break_day']}")
    print(f"    Phase IIIa: α1={m4['alpha1']:.4f}/day  "
          f"half-life={math.log(2)/m4['alpha1']:.1f} days")
    print(f"    Phase IIIb: α2={m4['alpha2']:.4f}/day  "
          f"half-life={math.log(2)/m4['alpha2']:.1f} days")
    print(f"    ΔAIC vs M1 (single decay): {m4['aic'] - m1['aic']:+.2f}")
    if m4["aic"] < m1["aic"] - 2:
        print("    → Structural break strongly supported (ΔAIC < −2)")
    elif m4["aic"] < m1["aic"]:
        print("    → Structural break weakly supported")
    else:
        print("    → Structural break not supported (single decay better)")

    print(f"\n  Best piecewise NB (M5): break at Day {m5['break_day']}")
    print(f"    Phase IIIa: α1={m5['alpha1']:.4f}/day  "
          f"half-life={math.log(2)/m5['alpha1']:.1f} days")
    print(f"    Phase IIIb: α2={m5['alpha2']:.4f}/day  "
          f"half-life={math.log(2)/m5['alpha2']:.1f} days")
    print(f"    k={m5['k']:.1f}   ΔAIC vs M3 (single NB decay): {m5['aic'] - m3['aic']:+.2f}")

    # ── Best model daily table ─────────────────────────────────────────────────
    best_m = all_models[aics.index(best_aic)]
    print(f"\n── Best Model ({best_m['name']}) — Daily fit ─────────────────────────")
    print(f"  {'Date':<10} {'Day':>3} {'Obs':>5} {'Pred':>6} {'Resid':>7}  PI-90")
    print("  " + "-" * 55)
    for i, (date, day, ob) in enumerate(zip(dates, days, obs)):
        mu = best_m["mus"][i]
        resid = ob - mu
        sigma = math.sqrt(mu * (1 + mu / best_m["k"]) if not math.isinf(best_m.get("k", np.inf)) else mu)
        lo = max(0, round(mu - 1.645 * sigma))
        hi = round(mu + 1.645 * sigma)
        flag = " ◄" if abs(resid) > 1.645 * sigma else ""
        print(f"  {date:<10} {day:>3} {ob:>5.0f}  {mu:>6.2f} {resid:>+7.2f}  "
              f"[{lo}–{hi}]{flag}")

    # ── April forecast under best model ───────────────────────────────────────
    import datetime
    war_start = datetime.date(2026, 2, 28)

    print(f"\n── April 2026 Forecast ({best_m['name']}) ─────────────────────────")

    rng = np.random.default_rng(42)

    # Build mu function for the best model
    def mu_april(day_num):
        ti = day_num - PHASE3_START
        if "alpha1" in best_m:
            tau = best_m["tau"]
            if ti < tau:
                return best_m["mu0"] * math.exp(-best_m["alpha1"] * ti)
            else:
                mu_tau = best_m["mu0"] * math.exp(-best_m["alpha1"] * tau)
                return mu_tau * math.exp(-best_m["alpha2"] * (ti - tau))
        elif best_m.get("alpha", 0) > 0:
            return best_m["mu0"] * math.exp(-best_m["alpha"] * ti)
        else:
            return best_m["mu0"]

    k_forecast = best_m.get("k", np.inf)

    print(f"  {'Week':<8} {'Dates':<18} {'E[W]':>6} {'σ':>5}  {'90% PI':>10}  Daily")
    print("  " + "-" * 62)

    for wk, (wname, day_range) in enumerate([
        ("Week 1", range(30, 37)),
        ("Week 2", range(37, 44)),
        ("Week 3", range(44, 51)),
        ("Week 4", range(51, 58)),
    ]):
        day_nums = list(day_range)
        dates_w = [war_start + datetime.timedelta(days=d - 1) for d in day_nums]
        date_str = f"{dates_w[0].strftime('%b%d')}–{dates_w[-1].strftime('%b%d')}"

        mus_w = [mu_april(d) for d in day_nums]
        E_W = sum(mus_w)
        if math.isinf(k_forecast):
            Var_W = sum(mus_w)
        else:
            Var_W = sum(mu + mu**2 / k_forecast for mu in mus_w)
        sigma = math.sqrt(Var_W)

        # Monte Carlo PI
        sims = np.zeros(50000)
        for mu in mus_w:
            if math.isinf(k_forecast):
                sims += rng.poisson(mu, size=50000)
            else:
                lam = rng.gamma(shape=k_forecast, scale=mu / k_forecast, size=50000)
                sims += rng.poisson(lam)

        lo90, hi90 = np.percentile(sims, [5, 95])
        print(f"  {wname:<8} {date_str:<18} {E_W:>6.1f} {sigma:>5.1f}  "
              f"[{lo90:.0f}–{hi90:.0f}]{'':<4}  {E_W/7:.1f}/day")

    # ── Hypothesis summary ─────────────────────────────────────────────────────
    print(f"\n── Hypothesis Assessment ─────────────────────────────────────────────")
    print(f"  H1 (Poisson flat):         AIC={m0['aic']:.1f} — baseline")
    print(f"  H2 (Poisson exp decay):    AIC={m1['aic']:.1f}  ΔAIC={m1['aic']-best_aic:+.1f}")
    print(f"  H3 (NB flat):              AIC={m2['aic']:.1f}  ΔAIC={m2['aic']-best_aic:+.1f}")
    print(f"  H4 (NB exp decay):         AIC={m3['aic']:.1f}  ΔAIC={m3['aic']-best_aic:+.1f}")
    print(f"  H5 (Poisson piecewise):    AIC={m4['aic']:.1f}  ΔAIC={m4['aic']-best_aic:+.1f}")
    print(f"  H6 (NB piecewise):         AIC={m5['aic']:.1f}  ΔAIC={m5['aic']-best_aic:+.1f}")

    print(f"\n  Overdispersion: Pearson χ²/df under best Poisson model = "
          f"{pearson_diagnostics(obs, best_m['mus'], '', 0)['dispersion']:.3f}")
    print(f"  (1.0 = perfectly Poisson; >1.5 = NB warranted)")


if __name__ == "__main__":
    main()
