"""
Iranian Ballistic Missile Strike Model — Phase III NB Stochastic Model

L_t ~ NegativeBinomial(mu_t, k)
mu_t = mu0 * exp(-alpha * (t - t0))

Phase III starts Day 8 (Mar 7), model becomes statistically valid ~Mar 18-20.
t0 is calibrated to the start of the stochastic regime (Mar 8 = Day 9).

Usage:
    python nb_model.py               # fit + weekly Z-scores + April forecast
    python nb_model.py --backtest    # sequential 7-day window backtest
"""

import argparse
import math
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
from scipy.stats import nbinom
from scipy.optimize import minimize

DATA_FILE = Path(__file__).parent.parent / "data" / "israel_daily_estimate.csv"

# ── default parameters (from methodology doc) ────────────────────────────────
DEFAULT_MU0 = 5.8
DEFAULT_ALPHA = 0.03
DEFAULT_K = 9.0
PHASE_III_START_DAY = 9  # Day 9 = Mar 8 (first full stochastic day after collapse)


# ── data loading ─────────────────────────────────────────────────────────────

def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.sort_values("day_num").reset_index(drop=True)
    return df


def phase3_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Rows where bm_il_est is available and day is in Phase III."""
    p3 = df[df["day_num"] >= PHASE_III_START_DAY].copy()
    p3 = p3[p3["bm_il_est"].notna()].copy()
    return p3


# ── model ─────────────────────────────────────────────────────────────────────

def mu_t(day_num: float, mu0: float, alpha: float, t0: int = PHASE_III_START_DAY) -> float:
    """Expected daily missile count on given day_num."""
    return mu0 * math.exp(-alpha * (day_num - t0))


def nb_mean_var(mu: float, k: float):
    """NB mean and variance."""
    return mu, mu + mu**2 / k


def nb_pmf(x: int, mu: float, k: float) -> float:
    """P(L=x) under NB(mu, k)."""
    p = k / (k + mu)
    return nbinom.pmf(x, k, p)


def nb_logpmf(x: float, mu: float, k: float) -> float:
    """
    Log PMF of NB(mu, k) using gamma functions — valid for non-integer k.
    P(X=x) = Gamma(x+k)/(Gamma(k)*x!) * (k/(k+mu))^k * (mu/(k+mu))^x
    """
    x = int(round(x))
    if mu <= 0 or k <= 0 or x < 0:
        return -1e12
    return (
        math.lgamma(x + k) - math.lgamma(k) - math.lgamma(x + 1)
        + k * math.log(k / (k + mu))
        + x * math.log(mu / (k + mu))
    )


def neg_log_likelihood(params, days, obs):
    """NLL for fitting mu0, alpha, k to observed Phase III data."""
    mu0, alpha, log_k = params
    k = math.exp(log_k)
    if mu0 <= 0 or alpha <= 0 or k <= 0:
        return 1e12
    nll = 0.0
    for d, y in zip(days, obs):
        mu = mu_t(d, mu0, alpha)
        if mu <= 0:
            return 1e12
        nll -= nb_logpmf(y, mu, k)
    return nll


# ── fitting ──────────────────────────────────────────────────────────────────

def fit_model(df: pd.DataFrame, fit_start_day: int = 20, fixed_k: float = None):
    """
    MLE fit of (mu0, alpha[, k]) using Phase III observed/derived rows
    from fit_start_day onward (default Day 20 = Mar 19, where JINSA direct
    readings make estimates most reliable).

    If fixed_k is provided, only mu0 and alpha are optimized (k is held fixed).
    """
    p3 = phase3_rows(df)
    fit_rows = p3[p3["day_num"] >= fit_start_day]

    if len(fit_rows) < 4:
        print(f"  [warn] only {len(fit_rows)} rows for fitting — using doc defaults")
        return DEFAULT_MU0, DEFAULT_ALPHA, DEFAULT_K

    days = fit_rows["day_num"].values
    obs = fit_rows["bm_il_est"].values

    if fixed_k is not None:
        # Only fit mu0 and alpha
        def nll_fixed_k(params):
            mu0, alpha = params
            k = fixed_k
            if mu0 <= 0 or alpha <= 0:
                return 1e12
            return sum(
                -nb_logpmf(y, mu_t(d, mu0, alpha), k)
                for d, y in zip(days, obs)
            )
        x0 = [DEFAULT_MU0, DEFAULT_ALPHA]
        bounds = [(0.1, 200), (0.001, 0.5)]
        res = minimize(nll_fixed_k, x0, method="L-BFGS-B", bounds=bounds)
        if res.success:
            mu0_fit, alpha_fit = res.x
            return mu0_fit, alpha_fit, fixed_k
        else:
            print("  [warn] MLE did not converge — using doc defaults")
            return DEFAULT_MU0, DEFAULT_ALPHA, fixed_k

    x0 = [DEFAULT_MU0, DEFAULT_ALPHA, math.log(DEFAULT_K)]
    bounds = [(0.1, 200), (0.001, 0.5), (math.log(0.5), math.log(500))]

    res = minimize(
        neg_log_likelihood,
        x0,
        args=(days, obs),
        method="L-BFGS-B",
        bounds=bounds,
    )

    if res.success:
        mu0_fit, alpha_fit, log_k_fit = res.x
        return mu0_fit, alpha_fit, math.exp(log_k_fit)
    else:
        print("  [warn] MLE did not converge — using doc defaults")
        return DEFAULT_MU0, DEFAULT_ALPHA, DEFAULT_K


# ── weekly Z-score ────────────────────────────────────────────────────────────

def weekly_zscore(days, obs, mu0, alpha, k, t0=PHASE_III_START_DAY):
    """
    Compute Z = (W_obs - E[W]) / sqrt(Var[W]) for a window of days.

    Returns (W_obs, E_W, Var_W, Z).
    """
    W_obs = sum(obs)
    E_W = sum(mu_t(d, mu0, alpha, t0) for d in days)
    Var_W = sum(
        mu_t(d, mu0, alpha, t0) + mu_t(d, mu0, alpha, t0) ** 2 / k for d in days
    )
    Z = (W_obs - E_W) / math.sqrt(Var_W) if Var_W > 0 else float("nan")
    return W_obs, E_W, Var_W, Z


def zscore_label(z: float) -> str:
    az = abs(z)
    if az < 2:
        return "✅ STABLE"
    elif az < 3:
        return "⚠  MILD DEVIATION"
    else:
        return "🚨 MODEL BREAK"


# ── sequential 7-day backtest ─────────────────────────────────────────────────

def backtest(df: pd.DataFrame, mu0: float, alpha: float, k: float):
    print("\n── Sequential 7-day window backtest ──────────────────────────────────")
    print(f"  Parameters: mu0={mu0:.3f}  alpha={alpha:.4f}  k={k:.2f}")
    print()
    print(f"  {'Window':<22} {'W_obs':>6} {'E[W]':>6} {'σ':>5} {'Z':>6}  Status")
    print("  " + "-" * 68)

    p3 = phase3_rows(df)
    days_all = p3["day_num"].values
    obs_all = p3["bm_il_est"].values
    dates_all = p3["date"].dt.strftime("%b%d").values

    n = len(days_all)
    for i in range(n - 6):
        window_days = days_all[i : i + 7]
        window_obs = obs_all[i : i + 7]
        W_obs, E_W, Var_W, Z = weekly_zscore(window_days, window_obs, mu0, alpha, k)
        sigma = math.sqrt(Var_W)
        start = dates_all[i]
        end = dates_all[i + 6]
        label = zscore_label(Z)
        print(
            f"  {start}–{end:<12}  {W_obs:>6.0f} {E_W:>6.1f} {sigma:>5.1f} {Z:>+6.2f}  {label}"
        )


# ── April 2026 forecast ───────────────────────────────────────────────────────

def april_forecast(mu0: float, alpha: float, k: float, last_day: int = 29):
    """Forecast for April 2026 (Days 30–58)."""
    import datetime

    print("\n── April 2026 Forecast ────────────────────────────────────────────────")
    print(f"  Parameters: mu0={mu0:.3f}  alpha={alpha:.4f}  k={k:.2f}")
    print()
    print(f"  {'Week':<8} {'Days':<12} {'Dates':<20} {'E[W]':>6} {'σ':>5}  "
          f"{'90% PI':>14}  {'99% PI':>14}")
    print("  " + "-" * 80)

    war_start = datetime.date(2026, 2, 28)
    weeks = [
        ("Week 1", range(30, 37)),
        ("Week 2", range(37, 44)),
        ("Week 3", range(44, 51)),
        ("Week 4", range(51, 58)),
    ]

    for week_name, day_range in weeks:
        day_nums = list(day_range)
        dates = [war_start + datetime.timedelta(days=d - 1) for d in day_nums]
        date_str = f"{dates[0].strftime('%b%d')}–{dates[-1].strftime('%b%d')}"

        E_W = sum(mu_t(d, mu0, alpha) for d in day_nums)
        Var_W = sum(
            mu_t(d, mu0, alpha) + mu_t(d, mu0, alpha) ** 2 / k for d in day_nums
        )
        sigma = math.sqrt(Var_W)

        # Monte Carlo for PI
        rng = np.random.default_rng(42)
        sims = np.zeros(20000)
        for d in day_nums:
            mu = mu_t(d, mu0, alpha)
            # Draw Gamma(k, mu/k) then Poisson — gives exact NB(mu, k)
            lambdas = rng.gamma(shape=k, scale=mu / k, size=20000)
            sims += rng.poisson(lambdas)

        lo90, hi90 = np.percentile(sims, [5, 95])
        lo99, hi99 = np.percentile(sims, [0.5, 99.5])

        print(
            f"  {week_name:<8} Day{day_nums[0]}–{day_nums[-1]:<6}  {date_str:<20} "
            f"{E_W:>6.1f} {sigma:>5.1f}  "
            f"[{lo90:.0f}–{hi90:.0f}]{' ':>4}  [{lo99:.0f}–{hi99:.0f}]"
        )


# ── daily diagnostic table ────────────────────────────────────────────────────

def daily_table(df: pd.DataFrame, mu0: float, alpha: float, k: float):
    print("\n── Phase III Daily Model vs Observed ─────────────────────────────────")
    print(f"  {'Date':<12} {'Day':>3} {'Obs':>5} {'E[L]':>6} {'Min':>5} {'Max':>5} "
          f"{'Resid':>6}  {'Data type':<20}")
    print("  " + "-" * 72)

    p3 = df[df["day_num"] >= PHASE_III_START_DAY].copy()
    for _, row in p3.iterrows():
        d = int(row["day_num"])
        mu = mu_t(d, mu0, alpha)
        _, var = nb_mean_var(mu, k)
        sigma = math.sqrt(var)
        lo = max(0, round(mu - 1.645 * sigma))
        hi = round(mu + 1.645 * sigma)
        obs = row["bm_il_est"]
        resid = f"{(obs - mu):+.1f}" if pd.notna(obs) else "   n/a"
        obs_str = f"{obs:5.0f}" if pd.notna(obs) else "   —"
        dtype = str(row.get("data_type", "")) if pd.notna(row.get("data_type")) else ""
        date_str = row["date"].strftime("%b %d")
        print(
            f"  {date_str:<12} {d:>3} {obs_str}  {mu:>6.1f} {lo:>5} {hi:>5} "
            f"{resid:>6}  {dtype:<20}"
        )


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Iran BM NB stochastic model")
    parser.add_argument("--backtest", action="store_true", help="Run 7-day backtest")
    parser.add_argument("--fit-start", type=int, default=20,
                        help="First day_num used for MLE fitting (default: 20)")
    parser.add_argument("--mu0", type=float, default=None)
    parser.add_argument("--alpha", type=float, default=None)
    parser.add_argument("--k", type=float, default=None,
                        help="Fix k (dispersion) and fit only mu0+alpha")
    args = parser.parse_args()

    df = load_data()

    print("═" * 70)
    print("  Iran BM Stochastic Model  —  L_t ~ NB(mu0·e^(-α·t), k)")
    print("═" * 70)

    # parameter resolution
    if args.mu0 and args.alpha and args.k:
        mu0, alpha, k = args.mu0, args.alpha, args.k
        print(f"\n  Using user-supplied parameters")
    elif args.k:
        print(f"\n  Fitting model with fixed k={args.k} (Day ≥ {args.fit_start})...")
        mu0, alpha, k = fit_model(df, fit_start_day=args.fit_start, fixed_k=args.k)
    else:
        print(f"\n  Fitting model to Phase III data (Day ≥ {args.fit_start})...")
        mu0, alpha, k = fit_model(df, fit_start_day=args.fit_start)

    print(f"  mu0={mu0:.3f}  alpha={alpha:.4f}  k={k:.2f}")
    print(f"  Half-life: {math.log(2)/alpha:.1f} days  "
          f"(mu drops to 50% after this many days in Phase III)")

    # daily table
    daily_table(df, mu0, alpha, k)

    # most recent complete 7-day window Z-score
    p3 = phase3_rows(df)
    if len(p3) >= 7:
        last7 = p3.tail(7)
        W_obs, E_W, Var_W, Z = weekly_zscore(
            last7["day_num"].values, last7["bm_il_est"].values, mu0, alpha, k
        )
        sigma = math.sqrt(Var_W)
        start = last7["date"].iloc[0].strftime("%b %d")
        end = last7["date"].iloc[-1].strftime("%b %d")
        print(f"\n── Latest 7-day window ({start}–{end}) ──────────────────────")
        print(f"  W_obs={W_obs:.0f}  E[W]={E_W:.1f}  σ={sigma:.1f}  Z={Z:+.2f}  "
              f"{zscore_label(Z)}")

    if args.backtest:
        backtest(df, mu0, alpha, k)

    april_forecast(mu0, alpha, k, last_day=int(p3["day_num"].max()))


if __name__ == "__main__":
    main()
