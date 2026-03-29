"""
Iranian Ballistic Missile Strike Model — Phase III Poisson Stochastic Model

Two calibrated variants:

  Model C (Conservative — "Iran sustains"):
      L_t ~ Poisson(mu_t),  mu_t = 11.75 * exp(-0.007 * (t - 14))
      Calibrated from M4 piecewise post-break arm (Phase IIIb).
      Half-life: 99 days.

  Model O (Optimistic — "Iran degrades"):
      L_t ~ Poisson(mu_t),  mu_t = 14.45 * exp(-0.021 * (t - 11))
      MLE on full Phase III (Days 11-29).
      Half-life: 33 days.

Usage:
    python poisson_model.py                   # daily Mar29–Apr29 forecast (both models)
    python poisson_model.py --backtest        # Phase III back-test Z-scores
    python poisson_model.py --verify          # observed vs predicted for Phase III
"""

import argparse
import datetime
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import poisson as poisson_dist

DATA_FILE = Path(__file__).parent.parent / "data" / "israel_daily_estimate.csv"
WAR_START = datetime.date(2026, 2, 28)   # Day 1

# ── Model parameters ──────────────────────────────────────────────────────────

MODELS = {
    "C": {
        "label": "Conservative (Iran sustains)",
        "mu0":   11.75,
        "alpha": 0.007,
        "t0":    14,          # Day 14 = Mar 13
        "note":  "Phase IIIb anchor; α=0.007/d; half-life 101d",
    },
    "O": {
        "label": "Optimistic (Iran degrades)",
        "mu0":   14.45,
        "alpha": 0.021,
        "t0":    11,          # Day 11 = Mar 10
        "note":  "Full Phase III trend; α=0.021/d; half-life 33d",
    },
}

PHASE3_START = 11   # first day included in Phase III back-test


# ── Core math ─────────────────────────────────────────────────────────────────

def day_to_date(day_num: int) -> datetime.date:
    return WAR_START + datetime.timedelta(days=day_num - 1)


def mu(day_num: int, model: dict) -> float:
    return model["mu0"] * math.exp(-model["alpha"] * (day_num - model["t0"]))


def pi(day_num: int, model: dict, pct_lo: float = 5, pct_hi: float = 95):
    """Exact Poisson prediction interval for a single day."""
    m = mu(day_num, model)
    lo = int(poisson_dist.ppf(pct_lo / 100, m))
    hi = int(poisson_dist.ppf(pct_hi / 100, m))
    return lo, hi


def weekly_stats(day_nums, model, n_sim=100_000):
    """Expected weekly total + 90/99% PI via Monte Carlo."""
    rng = np.random.default_rng(42)
    mus = [mu(d, model) for d in day_nums]
    E_W = sum(mus)
    Var_W = sum(mus)           # Poisson: Var = mean
    sims = sum(rng.poisson(m, n_sim) for m in mus)
    lo90, hi90 = np.percentile(sims, [5, 95])
    lo99, hi99 = np.percentile(sims, [0.5, 99.5])
    return E_W, math.sqrt(Var_W), lo90, hi90, lo99, hi99


def zscore_week(day_nums, obs, model):
    E_W = sum(mu(d, model) for d in day_nums)
    Var_W = sum(mu(d, model) for d in day_nums)
    W_obs = float(sum(obs))
    Z = (W_obs - E_W) / math.sqrt(Var_W)
    return W_obs, E_W, math.sqrt(Var_W), Z


def zscore_label(z):
    az = abs(z)
    if   az < 2: return "STABLE"
    elif az < 3: return "MILD DEVIATION"
    else:        return "MODEL BREAK"


# ── Data loading ──────────────────────────────────────────────────────────────

def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    return df.sort_values("day_num").reset_index(drop=True)


# ── Output sections ───────────────────────────────────────────────────────────

def print_model_summary():
    print("\n── Model Definitions ─────────────────────────────────────────────────")
    for key, m in MODELS.items():
        hl = math.log(2) / m["alpha"]
        print(f"  Model {key}: {m['label']}")
        print(f"    mu_t = {m['mu0']:.2f} * exp(-{m['alpha']:.4f} * (t - {m['t0']}))")
        print(f"    {m['note']}  |  mu(Day30)={mu(30,m):.2f}  mu(Day61)={mu(61,m):.2f}")


def print_daily_forecast():
    """Daily table Day 30 (Mar 29) through Day 61 (Apr 29)."""
    mc = MODELS["C"]
    mo = MODELS["O"]

    print("\n── Daily Forecast: Mar 29 – Apr 29 ──────────────────────────────────")
    print(f"  {'Date':<10} {'Day':>3}  "
          f"{'── Model C (Conservative) ──':^28}  "
          f"{'── Model O (Optimistic) ──':^28}")
    print(f"  {'':10} {'':3}  "
          f"{'E[L]':>6}  {'90% PI':^12}  {'cumul':>6}  "
          f"{'E[L]':>6}  {'90% PI':^12}  {'cumul':>6}")
    print("  " + "─" * 80)

    cumul_c = 0.0
    cumul_o = 0.0
    week_c  = 0.0
    week_o  = 0.0
    week_days = []

    for day_num in range(30, 62):
        d = day_to_date(day_num)

        e_c = mu(day_num, mc)
        e_o = mu(day_num, mo)
        cumul_c += e_c
        cumul_o += e_o

        lo_c, hi_c = pi(day_num, mc)
        lo_o, hi_o = pi(day_num, mo)

        week_c += e_c
        week_o += e_o
        week_days.append(day_num)

        # week separator
        dow = d.weekday()   # 0=Mon … 6=Sun

        print(f"  {d.strftime('%b %d, %a'):<14} {day_num:>3}  "
              f"{e_c:>6.2f}  [{lo_c:>2}–{hi_c:<2}]  {cumul_c:>8.1f}  "
              f"{e_o:>6.2f}  [{lo_o:>2}–{hi_o:<2}]  {cumul_o:>8.1f}")

        if dow == 6 or day_num == 61:   # end of week (Sun) or last day
            # weekly subtotal line
            wk_lo_c = int(poisson_dist.ppf(0.05, week_c))
            wk_hi_c = int(poisson_dist.ppf(0.95, week_c))
            wk_lo_o = int(poisson_dist.ppf(0.05, week_o))
            wk_hi_o = int(poisson_dist.ppf(0.95, week_o))
            days_in_week = len(week_days)
            label = f"  {'─'*3} Week total ({days_in_week}d)"
            print(f"{label:<29}  "
                  f"{week_c:>6.1f}  [{wk_lo_c:>2}–{wk_hi_c:<2}]  {'':>8}  "
                  f"{week_o:>6.1f}  [{wk_lo_o:>2}–{wk_hi_o:<2}]")
            print()
            week_c = 0.0
            week_o = 0.0
            week_days = []

    print(f"  {'─'*80}")
    print(f"  {'Total Apr 1–29 (days 33–61)':35}  "
          f"{sum(mu(d, mc) for d in range(33,62)):>6.1f}{'':>27}"
          f"{sum(mu(d, mo) for d in range(33,62)):>6.1f}")


def print_weekly_summary():
    mc = MODELS["C"]
    mo = MODELS["O"]

    print("\n── Weekly Summary ────────────────────────────────────────────────────")
    print(f"  {'Week':<8} {'Dates':<18}  "
          f"{'Model C':^28}  {'Model O':^28}")
    print(f"  {'':8} {'':18}  "
          f"{'E[W]':>6} {'σ':>4} {'90% PI':^14}  "
          f"{'E[W]':>6} {'σ':>4} {'90% PI':^14}")
    print("  " + "─" * 84)

    # Weeks: by calendar week starting Mon Mar 30
    week_ranges = [
        ("Week 1", range(30, 37)),   # Mar 29 – Apr 4  (Day 30–36)
        ("Week 2", range(37, 44)),   # Apr 5–11
        ("Week 3", range(44, 51)),   # Apr 12–18
        ("Week 4", range(51, 58)),   # Apr 19–25
        ("Week 5", range(58, 62)),   # Apr 26–29 (4 days)
    ]

    for wname, days in week_ranges:
        day_list = list(days)
        d0 = day_to_date(day_list[0]).strftime("%b %d")
        d1 = day_to_date(day_list[-1]).strftime("%b %d")
        date_str = f"{d0}–{d1}"

        E_c, sig_c, lo90_c, hi90_c, *_ = weekly_stats(day_list, mc)
        E_o, sig_o, lo90_o, hi90_o, *_ = weekly_stats(day_list, mo)

        print(f"  {wname:<8} {date_str:<18}  "
              f"{E_c:>6.1f} {sig_c:>4.1f} [{lo90_c:>3}–{hi90_c:<3}]{'':<4}  "
              f"{E_o:>6.1f} {sig_o:>4.1f} [{lo90_o:>3}–{hi90_o:<3}]")

    # April totals
    E_c_apr = sum(mu(d, mc) for d in range(33, 62))
    E_o_apr = sum(mu(d, mo) for d in range(33, 62))
    _, _, lo_c, hi_c, _, _ = weekly_stats(list(range(33, 62)), mc)
    _, _, lo_o, hi_o, _, _ = weekly_stats(list(range(33, 62)), mo)
    print(f"\n  {'April total':<8} {'Apr 1–29':<18}  "
          f"{E_c_apr:>6.1f}      [{lo_c:>3}–{hi_c:<3}]{'':<4}  "
          f"{E_o_apr:>6.1f}      [{lo_o:>3}–{hi_o:<3}]")

    # Gap between models
    gap = E_c_apr - E_o_apr
    print(f"\n  Model C vs O gap (April total): +{gap:.0f} BMs  "
          f"(C is {100*gap/E_o_apr:.0f}% higher than O)")


def print_backtest(df):
    print("\n── Phase III Back-test (7-day rolling Z-scores) ─────────────────────")
    print(f"  {'Window':<20}  {'W_obs':>6}  "
          f"{'Model C':^20}  {'Model O':^20}")
    print(f"  {'':20}  {'':6}  "
          f"{'E[W]':>6} {'Z':>6} {'':8}  "
          f"{'E[W]':>6} {'Z':>6} {'':8}")
    print("  " + "─" * 72)

    p3 = df[df["day_num"] >= PHASE3_START].dropna(subset=["isr_bm"])
    days_all  = p3["day_num"].values
    obs_all   = p3["isr_bm"].values
    dates_all = p3["date"].dt.strftime("%b%d").values

    n = len(days_all)
    for i in range(n - 6):
        wd = days_all[i: i + 7]
        wo = obs_all[i: i + 7]
        win = f"{dates_all[i]}–{dates_all[i+6]}"

        W, E_c, sig_c, Z_c = zscore_week(wd, wo, MODELS["C"])
        _,  E_o, sig_o, Z_o = zscore_week(wd, wo, MODELS["O"])

        lbl_c = zscore_label(Z_c)
        lbl_o = zscore_label(Z_o)

        print(f"  {win:<20}  {W:>6.0f}  "
              f"{E_c:>6.1f} {Z_c:>+6.2f} {lbl_c:<10}  "
              f"{E_o:>6.1f} {Z_o:>+6.2f} {lbl_o:<10}")


def print_verify(df):
    print("\n── Phase III Verification: Observed vs Both Models ──────────────────")
    print(f"  {'Date':<10} {'Day':>3} {'Obs':>5}  "
          f"{'Model C':^22}  {'Model O':^22}")
    print(f"  {'':10} {'':3} {'':5}  "
          f"{'E[L]':>6} {'Resid':>7} {'in PI':>6}  "
          f"{'E[L]':>6} {'Resid':>7} {'in PI':>6}")
    print("  " + "─" * 70)

    p3 = df[df["day_num"] >= PHASE3_START].dropna(subset=["isr_bm"])
    n_in_c = n_in_o = 0

    for _, row in p3.iterrows():
        d = int(row["day_num"])
        obs = row["isr_bm"]
        date_str = row["date"].strftime("%b %d")

        e_c = mu(d, MODELS["C"])
        e_o = mu(d, MODELS["O"])
        lo_c, hi_c = pi(d, MODELS["C"])
        lo_o, hi_o = pi(d, MODELS["O"])

        in_c = "✓" if lo_c <= obs <= hi_c else "✗"
        in_o = "✓" if lo_o <= obs <= hi_o else "✗"
        if in_c == "✓": n_in_c += 1
        if in_o == "✓": n_in_o += 1

        print(f"  {date_str:<10} {d:>3} {obs:>5.0f}  "
              f"{e_c:>6.2f} {obs-e_c:>+7.2f} {in_c:>6}  "
              f"{e_o:>6.2f} {obs-e_o:>+7.2f} {in_o:>6}")

    n = len(p3)
    print(f"\n  Coverage (90% PI): Model C = {n_in_c}/{n} ({100*n_in_c/n:.0f}%)  "
          f"Model O = {n_in_o}/{n} ({100*n_in_o/n:.0f}%)  "
          f"(expected ~90%)")


# ── Monitoring guide ──────────────────────────────────────────────────────────

def save_predictions(path: Path):
    rows = []
    for day_num in range(30, 62):
        d = day_to_date(day_num)
        for key, model in MODELS.items():
            e = mu(day_num, model)
            lo50, hi50 = pi(day_num, model, 25, 75)
            lo90, hi90 = pi(day_num, model, 5, 95)
            rows.append({
                "date":       d.isoformat(),
                "day_num":    day_num,
                "model":      key,
                "model_label": model["label"],
                "expected":   round(e, 3),
                "pi50_lo":    lo50,
                "pi50_hi":    hi50,
                "pi90_lo":    lo90,
                "pi90_hi":    hi90,
            })
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)
    print(f"\n  Predictions saved → {path}")


def print_monitoring_guide():
    print("\n── April Monitoring Guide ────────────────────────────────────────────")
    print("  Each week compute Z_C and Z_O on the actual 7-day total.\n")
    print(f"  {'Z_C':>7}  {'Z_O':>7}  Signal")
    print("  " + "─" * 52)
    rows = [
        ("−2 to +2", "+2 to +4", "Model C correct — Iran sustaining capacity"),
        ("−4 to −2", "−2 to +2", "Model O correct — gradual decay confirmed"),
        ("< −2",     "< −2",     "Both models too high — accelerating collapse"),
        ("> +2",     "> +4",     "Escalation — structural upward break"),
    ]
    for z_c, z_o, signal in rows:
        print(f"  {z_c:>9}  {z_o:>9}  {signal}")
    print()
    print("  Z = (W_obs − E[W]) / √E[W]   (Poisson: σ = √mean)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backtest", action="store_true",
                        help="Show Phase III rolling 7-day Z-scores")
    parser.add_argument("--verify",   action="store_true",
                        help="Show observed vs predicted for Phase III")
    args = parser.parse_args()

    print("═" * 70)
    print("  Iran BM Strike Model  —  Conservative (C) & Optimistic (O)")
    print("  L_t ~ Poisson(mu0 · exp(−α · (t − t0)))")
    print("═" * 70)

    print_model_summary()

    df = load_data()

    if args.verify:
        print_verify(df)

    if args.backtest:
        print_backtest(df)

    print_daily_forecast()
    print_weekly_summary()
    print_monitoring_guide()

    pred_path = Path(__file__).parent.parent / "predictions" / "predictions.csv"
    pred_path.parent.mkdir(exist_ok=True)
    save_predictions(pred_path)


if __name__ == "__main__":
    main()
