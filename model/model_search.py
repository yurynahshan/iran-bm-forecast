"""
Model Search Framework — Physical Launcher Constraint Grid Search
=================================================================

Explores the (N_launchers, avg_fires_per_launcher) parameter space,
evaluates each candidate on Phase IIIb data, and reports fit / stability
metrics to support model selection.

Physical constraint:
    total_phase3_missiles = N_launchers × avg_fires
    alpha = mu0 / total_phase3_missiles
    (mu0 fitted by closed-form MLE conditional on alpha)

Metrics reported per candidate:
    - alpha, half-life, mu0
    - Log-likelihood (LL)
    - AIC  (relative to best candidate — not compared across different n)
    - Pearson dispersion D = X²/(n-p)
    - Ljung-Box p-value (lag 3)
    - April total forecast
    - Stability: change in April forecast when last obs shifted ±4 BMs
    - Back-test: max |Z| across rolling 7-day windows

Usage:
    python model/model_search.py              # grid search + summary table
    python model/model_search.py --verbose    # also prints per-window Z-scores

"""

import argparse
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import poisson as poisson_dist, chi2

warnings.filterwarnings("ignore")

DATA_FILE  = Path(__file__).parent.parent / "data" / "israel_daily_estimate.csv"
INTEL_FILE = Path(__file__).parent.parent / "data" / "launcher_intel.csv"

PHASE3B_START = 14   # Phase IIIb stable regime start
PHASE3_START  = 11   # Phase III (including IIIa transition)


# ── Data ──────────────────────────────────────────────────────────────────────

def load_launcher_intel():
    """
    Return intelligence-derived alpha and its uncertainty range.
    Uses two launcher-count snapshots to compute fractional attrition rate.
    """
    df = pd.read_csv(INTEL_FILE, parse_dates=["date"])
    df = df.sort_values("day_num").reset_index(drop=True)
    if len(df) < 2:
        return None
    # Use earliest and latest snapshots
    t1, L1_mid, L1_lo, L1_hi = (
        df.iloc[0]["day_num"],
        df.iloc[0]["total_launchers"],
        df.iloc[0]["launcher_low"],
        df.iloc[0]["launcher_high"],
    )
    t2, L2_mid, L2_lo, L2_hi = (
        df.iloc[-1]["day_num"],
        df.iloc[-1]["total_launchers"],
        df.iloc[-1]["launcher_low"],
        df.iloc[-1]["launcher_high"],
    )
    dt = t2 - t1
    alpha_mid  = math.log(L1_mid / L2_mid) / dt
    alpha_low  = math.log(L1_lo  / L2_hi)  / dt   # most conservative (slow decay)
    alpha_high = math.log(L1_hi  / L2_lo)  / dt   # most optimistic (fast decay)
    return {
        "t1": int(t1), "L1": int(L1_mid), "L1_src": df.iloc[0]["source"],
        "t2": int(t2), "L2": int(L2_mid), "L2_src": df.iloc[-1]["source"],
        "alpha_mid":  round(alpha_mid,  5),
        "alpha_low":  round(max(alpha_low, 0.0001), 5),
        "alpha_high": round(alpha_high, 5),
        "hl_mid":     round(math.log(2) / alpha_mid, 1),
        "hl_low":     round(math.log(2) / alpha_high, 1),
        "hl_high":    round(math.log(2) / alpha_low, 1),
    }


def load_phase3b():
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    df = df.sort_values("day_num").reset_index(drop=True)
    p3b = df[df["day_num"] >= PHASE3B_START].dropna(subset=["isr_bm"])
    return p3b["day_num"].values, p3b["isr_bm"].values


def load_phase3():
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    df = df.sort_values("day_num").reset_index(drop=True)
    p3 = df[df["day_num"] >= PHASE3_START].dropna(subset=["isr_bm"])
    return p3["day_num"].values, p3["isr_bm"].values


# ── Core model math ────────────────────────────────────────────────────────────

def fit_mu0(alpha: float, days: np.ndarray, obs: np.ndarray, t0: int) -> float:
    """Closed-form MLE for mu0 given alpha."""
    denom = sum(math.exp(-alpha * (t - t0)) for t in days)
    if denom <= 0:
        return float("nan")
    return float(obs.sum()) / denom


def mus(alpha: float, mu0: float, days: np.ndarray, t0: int) -> np.ndarray:
    return np.array([mu0 * math.exp(-alpha * (t - t0)) for t in days])


def log_likelihood(mu_arr: np.ndarray, obs: np.ndarray) -> float:
    ll = 0.0
    for m, y in zip(mu_arr, obs):
        if m <= 0:
            return -1e9
        ll += y * math.log(m) - m - math.lgamma(y + 1)
    return ll


def aic(ll: float, n_params: int) -> float:
    return 2 * n_params - 2 * ll


def pearson_dispersion(mu_arr: np.ndarray, obs: np.ndarray, n_params: int) -> float:
    resid_sq = sum((y - m) ** 2 / m for m, y in zip(mu_arr, obs) if m > 0)
    df = len(obs) - n_params
    return resid_sq / df if df > 0 else float("nan")


def ljung_box_pvalue(residuals: np.ndarray, lags: int = 3) -> float:
    n = len(residuals)
    if n < lags + 5:
        return float("nan")
    r_mean = residuals.mean()
    r_centered = residuals - r_mean
    r_var = (r_centered ** 2).mean()
    if r_var == 0:
        return float("nan")
    acf = [
        float(np.correlate(r_centered[k:], r_centered[: n - k])[0] / (n * r_var))
        for k in range(1, lags + 1)
    ]
    lb = n * (n + 2) * sum(rho ** 2 / (n - k) for k, rho in enumerate(acf, 1))
    from scipy.stats import chi2 as chi2_dist
    return float(1 - chi2_dist.cdf(lb, df=lags))


def zscore_window(days_w, obs_w, alpha, mu0, t0):
    E = sum(mu0 * math.exp(-alpha * (t - t0)) for t in days_w)
    W = float(sum(obs_w))
    return (W - E) / math.sqrt(E) if E > 0 else float("nan")


def backtest_max_z(alpha: float, mu0: float, days: np.ndarray, obs: np.ndarray,
                   t0: int) -> tuple[float, int]:
    """Max |Z| and number of STABLE windows across rolling 7-day Phase III windows."""
    p3_days, p3_obs = load_phase3()
    n = len(p3_days)
    max_z = 0.0
    stable_count = 0
    total_windows = 0
    for i in range(n - 6):
        wd = p3_days[i: i + 7]
        wo = p3_obs[i: i + 7]
        z = zscore_window(wd, wo, alpha, mu0, t0)
        if not math.isnan(z):
            total_windows += 1
            if abs(z) < 2.0:
                stable_count += 1
            max_z = max(max_z, abs(z))
    return max_z, stable_count, total_windows


def april_total(alpha: float, mu0: float, t0: int) -> float:
    """Expected total BMs Days 33–61 (Apr 1–29)."""
    return sum(mu0 * math.exp(-alpha * (t - t0)) for t in range(33, 62))


def stability_delta(alpha: float, t0: int, days: np.ndarray, obs: np.ndarray,
                    perturb: float = 4.0) -> float:
    """
    How much does the April forecast change when the LAST observation is
    perturbed by +perturb BMs?  Measures model robustness to measurement noise.
    """
    mu0_base = fit_mu0(alpha, days, obs, t0)
    apr_base = april_total(alpha, mu0_base, t0)

    obs_perturbed = obs.copy()
    obs_perturbed[-1] += perturb
    mu0_perturbed = fit_mu0(alpha, days, obs_perturbed, t0)
    apr_perturbed = april_total(alpha, mu0_perturbed, t0)

    return abs(apr_perturbed - apr_base)


# ── Grid search ────────────────────────────────────────────────────────────────

def evaluate_candidate(n_launchers: int, avg_fires: float,
                        days: np.ndarray, obs: np.ndarray,
                        t0: int = PHASE3B_START,
                        label: str = "") -> dict:
    total_missiles = n_launchers * avg_fires
    # Initial mu0 estimate from mean
    mu0_init = float(obs.mean())
    alpha = mu0_init / total_missiles

    # One fixed-point iteration: refit mu0 with the derived alpha
    mu0 = fit_mu0(alpha, days, obs, t0)
    # alpha is now consistent: mu0/alpha ≈ total_missiles (within rounding)
    alpha_final = mu0 / total_missiles   # may differ slightly from initial

    mu_arr = mus(alpha_final, mu0, days, t0)

    ll = log_likelihood(mu_arr, obs)
    aic_val = aic(ll, 2)   # mu0, alpha = 2 params
    disp = pearson_dispersion(mu_arr, obs, 2)

    pearson_resid = np.array([(y - m) / math.sqrt(m) for m, y in zip(mu_arr, obs)])
    lb_p = ljung_box_pvalue(pearson_resid)

    max_z, stable_wins, total_wins = backtest_max_z(alpha_final, mu0, days, obs, t0)
    apr = april_total(alpha_final, mu0, t0)
    delta = stability_delta(alpha_final, t0, days, obs, perturb=4.0)

    hl = math.log(2) / alpha_final if alpha_final > 0 else float("inf")

    return {
        "label":          label or f"N={n_launchers}, f={avg_fires}",
        "n_launchers":    n_launchers,
        "avg_fires":      avg_fires,
        "total_missiles": round(total_missiles),
        "mu0":            round(mu0, 2),
        "alpha":          round(alpha_final, 4),
        "half_life_days": round(hl, 0),
        "ll":             round(ll, 2),
        "aic":            round(aic_val, 2),
        "dispersion_D":   round(disp, 3),
        "lb_p":           round(lb_p, 3),
        "april_total":    round(apr, 1),
        "max_z":          round(max_z, 2),
        "stable_windows": stable_wins,
        "total_windows":  total_wins,
        "stability_d4":   round(delta, 1),   # April forecast change for +4 BM perturbation
    }


# ── Display ────────────────────────────────────────────────────────────────────

def intel_marker(alpha: float, intel: dict) -> str:
    """Mark whether this alpha is in the intelligence-derived range."""
    if intel is None:
        return ""
    lo, hi = intel["alpha_low"], intel["alpha_high"]
    mid = intel["alpha_mid"]
    if lo <= alpha <= hi:
        if abs(alpha - mid) < 0.001:
            return " ◄ intel-mid"
        return " ◄ intel-range"
    return ""


def print_search_results(results: list[dict], aic_min: float, intel: dict = None):
    """Print the full comparison table."""
    intel_lo  = intel["alpha_low"]  if intel else None
    intel_hi  = intel["alpha_high"] if intel else None

    print(f"\n{'─'*140}")
    header = (f"  {'Scenario':<22} {'N':>4} {'f':>4} {'total':>6}  "
              f"{'mu0':>5} {'alpha':>6} {'HL':>5}  "
              f"{'ΔAIC':>5} {'D':>5} {'LB-p':>5}  "
              f"{'Apr':>6} {'max|Z|':>6} {'stbl':>5}  "
              f"{'Δfcst±4':>8}  verdict")
    print(header)
    print(f"{'─'*140}")

    for r in results:
        d_aic = r["aic"] - aic_min
        stbl_str = f"{r['stable_windows']}/{r['total_windows']}"

        # Validity flags — note: D < 0.75 means underdispersion; 0.75-1.3 is acceptable
        ok_disp = 0.75 <= r["dispersion_D"] <= 1.3
        ok_lb   = r["lb_p"] > 0.05
        ok_z    = r["max_z"] < 2.0
        ok_stab = r["stability_d4"] <= 20.0
        ok_hl   = r["half_life_days"] <= 200

        issues = []
        if not ok_disp: issues.append(f"D={r['dispersion_D']:.2f}!")
        if not ok_lb:   issues.append(f"LB-p={r['lb_p']:.3f}!")
        if not ok_z:    issues.append(f"max|Z|={r['max_z']:.2f}!")
        if not ok_stab: issues.append(f"Δ={r['stability_d4']:.1f}!")
        if not ok_hl:   issues.append(f"HL={r['half_life_days']:.0f}d!")

        verdict = "✓ OK" if not issues else "⚠ " + ", ".join(issues)

        # Intel marker
        intel_flag = ""
        if intel_lo is not None and intel_lo <= r["alpha"] <= intel_hi:
            intel_flag = " ◄ INTEL"

        print(f"  {r['label']:<22} {r['n_launchers']:>4} {r['avg_fires']:>4.1f} "
              f"{r['total_missiles']:>6}  "
              f"{r['mu0']:>5.2f} {r['alpha']:>6.4f} {r['half_life_days']:>5.0f}  "
              f"{d_aic:>5.1f} {r['dispersion_D']:>5.3f} {r['lb_p']:>5.3f}  "
              f"{r['april_total']:>6.1f} {r['max_z']:>6.2f} {stbl_str:>5}  "
              f"{r['stability_d4']:>8.1f}  {verdict}{intel_flag}")

    print(f"{'─'*140}")
    if intel:
        print(f"\n  ◄ INTEL = alpha within intelligence-derived range "
              f"[{intel_lo:.4f}–{intel_hi:.4f}] "
              f"(HL {intel['hl_low']:.0f}–{intel['hl_high']:.0f} days; "
              f"mid={intel['alpha_mid']:.4f}/day, HL={intel['hl_mid']:.0f}d)")
    print(f"\n  Columns: N=launchers, f=fires/launcher, HL=half-life(days), ΔAIC=vs best,")
    print(f"  D=Pearson dispersion (target ≈1.0), LB-p=Ljung-Box p-val (target >0.05),")
    print(f"  Apr=April forecast (BMs), max|Z|=worst backtest Z, stbl=stable 7d windows,")
    print(f"  Δfcst±4=April forecast change when last obs ±4 BMs (stability metric).")


def print_intel_section(intel: dict, days: np.ndarray, obs: np.ndarray):
    """Print the intelligence-derived alpha and its model implications."""
    if intel is None:
        return
    print(f"\n{'═'*80}")
    print("  INTELLIGENCE-DERIVED LAUNCHER ATTRITION RATE")
    print(f"{'═'*80}")
    print(f"  Day {intel['t1']} ({intel['L1']} total launchers)  →  "
          f"Day {intel['t2']} ({intel['L2']} total launchers)")
    print(f"  Source: {intel['L1_src']} → {intel['L2_src']}")
    print(f"\n  Implied alpha_total_launchers:")
    print(f"    Mid estimate: {intel['alpha_mid']:.4f}/day  "
          f"(HL = {intel['hl_mid']:.0f} days)")
    print(f"    Range (accounting for source uncertainty): "
          f"[{intel['alpha_low']:.4f}–{intel['alpha_high']:.4f}]/day  "
          f"(HL {intel['hl_low']:.0f}–{intel['hl_high']:.0f} days)")
    print(f"\n  Note: This alpha measures TOTAL launcher attrition (all targets).")
    print(f"  For Israel-specific launches, alpha may be equal (if strikes are")
    print(f"  proportional) or higher (if Israel-facing assets are priority targets).")
    print(f"  IDF reported >80% of Israel-facing capacity neutralized by Day 12,")
    print(f"  suggesting remaining Israel-facing launchers may be harder to destroy.")
    mu0_intel = fit_mu0(intel["alpha_mid"], days, obs, PHASE3B_START)
    apr_intel = april_total(intel["alpha_mid"], mu0_intel, PHASE3B_START)
    stab_intel = stability_delta(intel["alpha_mid"], PHASE3B_START, days, obs, 4.0)
    print(f"\n  At alpha_mid={intel['alpha_mid']:.4f}: mu0={mu0_intel:.2f}, "
          f"April forecast={apr_intel:.1f} BMs, stability Δ={stab_intel:.1f} BMs")


def print_recommendation(results: list[dict], aic_min: float, intel: dict = None):
    """Identify recommended Conservative and Optimistic models."""
    # Filter to physically/statistically valid candidates
    valid = [r for r in results
             if r["dispersion_D"] < 1.4
             and r["dispersion_D"] > 0.75
             and r["lb_p"] > 0.04
             and r["max_z"] < 2.0
             and r["stability_d4"] <= 20.0
             and r["half_life_days"] <= 200]

    if not valid:
        print("\n  No candidate passes all validity filters.")
        return

    # Intelligence-grounded candidates (if intel provided)
    intel_valid = []
    if intel is not None:
        intel_valid = [r for r in valid
                       if intel["alpha_low"] <= r["alpha"] <= intel["alpha_high"]]

    # Conservative = longest half-life among valid; prefer intel-consistent if available
    c_pool = intel_valid if intel_valid else valid
    best_c = max(c_pool, key=lambda r: r["half_life_days"])

    # Optimistic = shortest half-life among valid (intel-consistent or unconstrained)
    best_o = min(valid, key=lambda r: r["half_life_days"])

    print(f"\n{'═'*80}")
    print("  RECOMMENDED MODELS")
    print(f"{'═'*80}")
    if intel_valid:
        print(f"  (Model C selected from intelligence-consistent candidates;")
        print(f"   Model O from full valid set)")

    note_c = "intelligence-grounded" if best_c in intel_valid else "statistical best"
    pairs = [
        ("Conservative (C) — Iran sustains:", best_c, note_c),
        ("Optimistic   (O) — Iran degrades:", best_o, "fastest valid decay"),
    ]
    for label, r, note in pairs:
        print(f"\n  {label}  [{note}]")
        print(f"    Physical:  N={r['n_launchers']} launchers × {r['avg_fires']} fires "
              f"= {r['total_missiles']} total missiles")
        print(f"    mu0={r['mu0']}, alpha={r['alpha']:.4f}/day, HL={r['half_life_days']:.0f} days")
        print(f"    April forecast: {r['april_total']:.1f} BMs")
        print(f"    Stability (±4 BM noise → forecast change): {r['stability_d4']:.1f} BMs")
        print(f"    ΔAIC vs best: {r['aic'] - aic_min:+.1f}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Model search framework")
    parser.add_argument("--verbose", action="store_true",
                        help="Print per-window Z-scores for each candidate")
    args = parser.parse_args()

    days, obs = load_phase3b()
    intel = load_launcher_intel()

    print("═" * 140)
    print("  Model Search Framework — Physical Launcher Constraint Grid")
    print(f"  Data: Phase IIIb Days 14–29 (n={len(days)}, Σ={int(obs.sum())} BMs)")
    print(f"  Physical constraint: alpha = mu0 / (N_launchers × avg_fires)")
    print("═" * 140)

    if intel:
        print_intel_section(intel, days, obs)

    # ── Define candidate grid ──────────────────────────────────────────────────
    # N_launchers × avg_fires combinations covering the realistic range
    # Iran's Israel-capable TELs estimated 200–700; fires 1.5–3.5 per TEL
    candidates = []

    grid = [
        # (n_launchers, avg_fires, label)
        # Very optimistic for Israel: few launchers, few fires
        (200, 1.5, "N=200 f=1.5 [very-O]"),
        (250, 1.5, "N=250 f=1.5"),
        (300, 2.0, "N=300 f=2.0"),
        (300, 2.5, "N=300 f=2.5"),
        (350, 2.0, "N=350 f=2.0"),
        (400, 2.0, "N=400 f=2.0"),
        (400, 2.5, "N=400 f=2.5"),
        (450, 2.5, "N=450 f=2.5"),
        (500, 2.0, "N=500 f=2.0"),
        (500, 2.5, "N=500 f=2.5"),
        # Intelligence-grounded zone (alpha ≈ 0.008/day corresponds to HL ≈ 83 days)
        (500, 3.0, "N=500 f=3.0 [intel-mid]"),
        (600, 2.5, "N=600 f=2.5 [intel-mid]"),
        (600, 3.0, "N=600 f=3.0"),
        (700, 2.5, "N=700 f=2.5"),
        (700, 3.0, "N=700 f=3.0"),
        (700, 3.5, "N=700 f=3.5 [very-C]"),
    ]

    results = []
    for n, f, lbl in grid:
        r = evaluate_candidate(n, f, days, obs, t0=PHASE3B_START, label=lbl)
        results.append(r)

    # Sort by alpha (descending = optimistic first)
    results.sort(key=lambda r: -r["alpha"])

    aic_min = min(r["aic"] for r in results)

    print_search_results(results, aic_min, intel)
    print_recommendation(results, aic_min, intel)

    # ── Summary statistics ─────────────────────────────────────────────────────
    print(f"\n{'─'*80}")
    print("  APRIL FORECAST RANGE ACROSS ALL CANDIDATES")
    aprs = [r["april_total"] for r in results]
    print(f"  Min: {min(aprs):.1f} BMs  |  Max: {max(aprs):.1f} BMs  |  "
          f"Mean: {sum(aprs)/len(aprs):.1f} BMs")

    valid_aprs = [r["april_total"] for r in results
                  if r["dispersion_D"] < 1.4 and r["max_z"] < 2.0 and r["stability_d4"] <= 20.0]
    if valid_aprs:
        print(f"  Valid candidates only: {min(valid_aprs):.1f} – {max(valid_aprs):.1f} BMs")


if __name__ == "__main__":
    main()
