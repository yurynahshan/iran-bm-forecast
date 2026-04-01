"""
model/benchmark.py  —  Out-of-sample forecast evaluation

Joins frozen predictions (predictions/predictions.csv) against observed
actuals (data/israel_daily_estimate.csv) on day_num.  Test window = all
days present in both files — auto-expands as new actuals arrive.

Predictions were generated on Mar 29, 2026 (Day 30) before any test-period
observations.  This file must not be regenerated retrospectively.

Four variants compared
  Model C    Conservative  α=0.0083/d  HL=83d
  Model O    Observable    α=0.020/d   HL=35d
  Mix-50     Equal-weight mean:  μ = 0.5·μ_C + 0.5·μ_O
  Mix-EW     Bayesian model averaging:  w ∝ exp(Σ log P(y|μ)) on test data so far

Per-day metrics
  residual   actual − E[L]
  Z-score    (actual − μ) / √μ      [Poisson: σ = √μ]
  log-lik    log Poisson(y | μ)     = y·log(μ) − μ − log(y!)
  in_90PI / in_50PI

Aggregate metrics
  MAE, RMSE, cumulative bias Σ(y−μ), mean Z, total log-likelihood,
  90% and 50% PI coverage rate

Usage
  python model/benchmark.py                   # all available test days
  python model/benchmark.py --days 30-32      # specific day range
  python model/benchmark.py --no-low-conf     # exclude LOW_CONFIDENCE days
  python model/benchmark.py --weekly          # show 7-day rolling Z-score table
"""

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import gammaln

PRED_FILE = Path(__file__).parent.parent / "predictions" / "predictions.csv"
DATA_FILE = Path(__file__).parent.parent / "data"        / "israel_daily_estimate.csv"
OUT_FILE  = Path(__file__).parent.parent / "predictions" / "benchmark_results.csv"

# Columns returned for each model in predictions.csv
PRED_COLS = ["day_num", "expected", "pi50_lo", "pi50_hi", "pi90_lo", "pi90_hi"]


# ── CSV parsing ───────────────────────────────────────────────────────────────

def read_estimate_csv(path: Path) -> pd.DataFrame:
    """
    Parse israel_daily_estimate.csv robustly.

    The 'notes' column (index 9) contains unquoted commas, making standard
    CSV parsers fail.  The file has a fixed structure:
      cols 0–8:  date … primary_source  (safe, no commas)
      col  9:    notes                  (may contain commas)
      col  10:   flags                  (safe)

    Strategy: split each line on comma, take first 9 fields as-is,
    join everything from field 9 to second-to-last as notes,
    take the last field as flags.  This works whether flags is empty
    (trailing comma → empty last token) or non-empty (e.g. LOW_CONFIDENCE).
    """
    header_line = None
    rows = []
    with open(path, encoding="utf-8") as f:
        for i, raw in enumerate(f):
            line = raw.rstrip("\n").rstrip("\r")
            if i == 0:
                header_line = line.split(",")
                continue
            if not line.strip():
                continue
            parts = line.split(",")
            if len(parts) < 11:
                # Pad short lines (e.g. missing trailing columns)
                parts += [""] * (11 - len(parts))
            safe  = parts[:9]                       # cols 0-8
            notes = ",".join(parts[9:-1])           # col 9 (rejoin if commas inside)
            flags = parts[-1]                       # col 10
            rows.append(safe + [notes, flags])

    df = pd.DataFrame(rows, columns=header_line)
    df["date"]    = pd.to_datetime(df["date"])
    df["day_num"] = pd.to_numeric(df["day_num"])
    df["isr_bm"]  = pd.to_numeric(df["isr_bm"],    errors="coerce")
    df["bm_il_min"] = pd.to_numeric(df["bm_il_min"], errors="coerce")
    df["bm_il_max"] = pd.to_numeric(df["bm_il_max"], errors="coerce")
    return df


# ── Math ──────────────────────────────────────────────────────────────────────

def poisson_loglik(y: float, mu: float) -> float:
    """log P(Y=y | Poisson(mu)).  Returns −inf when mu ≤ 0."""
    if mu <= 0:
        return -math.inf
    return float(y * math.log(mu) - mu - gammaln(y + 1))


def zscore(y: float, mu: float) -> float:
    """Poisson Z-score: (y − μ) / √μ."""
    return (y - mu) / math.sqrt(mu) if mu > 0 else float("nan")


def z_label(z: float) -> str:
    az = abs(z)
    if az < 2:   return "STABLE"
    elif az < 3: return "MILD DEV"
    else:        return "BREAK"


# ── Data loading ──────────────────────────────────────────────────────────────

def load_and_join(day_lo: int = None, day_hi: int = None,
                  drop_low_conf: bool = False) -> pd.DataFrame:
    """
    Load predictions and actuals, join on day_num.

    Returns one wide DataFrame row per test day with columns for both
    models and all derived metrics.  Mix-50 and Mix-EW are also computed.
    """
    preds  = pd.read_csv(PRED_FILE)
    actual = read_estimate_csv(DATA_FILE)

    # Keep only columns needed; require observed value
    actual = (actual[["day_num", "date", "isr_bm",
                       "bm_il_min", "bm_il_max", "flags"]]
              .dropna(subset=["isr_bm"]))

    if drop_low_conf:
        actual = actual[~actual["flags"].fillna("").str.contains("LOW_CONFIDENCE")]

    # Split by model and rename columns
    def model_cols(key):
        sub = (preds[preds["model"] == key][PRED_COLS]
               .rename(columns={
                   "expected": f"mu_{key}",
                   "pi50_lo": f"pi50_lo_{key}", "pi50_hi": f"pi50_hi_{key}",
                   "pi90_lo": f"pi90_lo_{key}", "pi90_hi": f"pi90_hi_{key}",
               }))
        return sub

    wide = (actual
            .merge(model_cols("C"), on="day_num")
            .merge(model_cols("O"), on="day_num"))

    if day_lo is not None:
        wide = wide[wide["day_num"] >= day_lo]
    if day_hi is not None:
        wide = wide[wide["day_num"] <= day_hi]

    wide = wide.sort_values("day_num").reset_index(drop=True)

    if len(wide) == 0:
        raise SystemExit("No test data found — check that predictions.csv covers "
                         "the requested days and actuals exist in israel_daily_estimate.csv.")

    # ── Per-day metrics for Model C and O ─────────────────────────────────────
    for key in ("C", "O"):
        mu_col = f"mu_{key}"
        wide[f"resid_{key}"] = wide["isr_bm"] - wide[mu_col]
        wide[f"z_{key}"]     = wide.apply(lambda r: zscore(r["isr_bm"], r[mu_col]), axis=1)
        wide[f"ll_{key}"]    = wide.apply(lambda r: poisson_loglik(r["isr_bm"], r[mu_col]), axis=1)
        wide[f"in90_{key}"]  = ((wide["isr_bm"] >= wide[f"pi90_lo_{key}"]) &
                                 (wide["isr_bm"] <= wide[f"pi90_hi_{key}"]))
        wide[f"in50_{key}"]  = ((wide["isr_bm"] >= wide[f"pi50_lo_{key}"]) &
                                 (wide["isr_bm"] <= wide[f"pi50_hi_{key}"]))

    # ── Mix-50: equal-weight combination ──────────────────────────────────────
    wide["mu_mix50"]    = 0.5 * wide["mu_C"] + 0.5 * wide["mu_O"]
    wide["resid_mix50"] = wide["isr_bm"] - wide["mu_mix50"]
    wide["z_mix50"]     = wide.apply(lambda r: zscore(r["isr_bm"], r["mu_mix50"]), axis=1)
    wide["ll_mix50"]    = wide.apply(lambda r: poisson_loglik(r["isr_bm"], r["mu_mix50"]), axis=1)

    # ── Mix-EW: Bayesian model averaging on all test data in window ───────────
    # w ∝ exp(Σ log P(y_i | μ_i))  with equal priors
    # Numerical stability: subtract max log-likelihood before exp
    ll_c_sum = wide["ll_C"].sum()
    ll_o_sum = wide["ll_O"].sum()
    ll_max   = max(ll_c_sum, ll_o_sum)
    w_c_raw  = math.exp(ll_c_sum - ll_max)
    w_o_raw  = math.exp(ll_o_sum - ll_max)
    w_c      = w_c_raw / (w_c_raw + w_o_raw)
    w_o      = w_o_raw / (w_c_raw + w_o_raw)

    wide["w_c_ev"]      = w_c
    wide["w_o_ev"]      = w_o
    wide["mu_mix_ev"]   = w_c * wide["mu_C"] + w_o * wide["mu_O"]
    wide["resid_mix_ev"]= wide["isr_bm"] - wide["mu_mix_ev"]
    wide["z_mix_ev"]    = wide.apply(lambda r: zscore(r["isr_bm"], r["mu_mix_ev"]), axis=1)
    wide["ll_mix_ev"]   = wide.apply(lambda r: poisson_loglik(r["isr_bm"], r["mu_mix_ev"]), axis=1)

    return wide


# ── Aggregate metrics ─────────────────────────────────────────────────────────

# (name, mu_col, z_col, ll_col, pi90_col, pi50_col)
VARIANTS = [
    ("C",      "mu_C",       "z_C",       "ll_C",       "in90_C", "in50_C"),
    ("O",      "mu_O",       "z_O",       "ll_O",       "in90_O", "in50_O"),
    ("Mix-50", "mu_mix50",   "z_mix50",   "ll_mix50",   None,     None),
    ("Mix-EW", "mu_mix_ev",  "z_mix_ev",  "ll_mix_ev",  None,     None),
]


def compute_agg(wide: pd.DataFrame) -> dict:
    y = wide["isr_bm"].values
    out = {}
    for name, mu_col, z_col, ll_col, pi90_col, pi50_col in VARIANTS:
        mu_v = wide[mu_col].values
        res  = y - mu_v
        out[name] = {
            "mae":      float(np.mean(np.abs(res))),
            "rmse":     float(np.sqrt(np.mean(res**2))),
            "bias":     float(np.sum(res)),
            "mean_z":   float(np.mean(wide[z_col].values)),
            "total_ll": float(wide[ll_col].sum()),
        }
        if pi90_col:
            out[name]["cov90"] = float(wide[pi90_col].mean())
            out[name]["cov50"] = float(wide[pi50_col].mean())
    return out


# ── Print functions ───────────────────────────────────────────────────────────

SEP = "═" * 72


def print_header(wide: pd.DataFrame):
    n    = len(wide)
    d0   = wide["date"].iloc[0].strftime("%b %d")
    d1   = wide["date"].iloc[-1].strftime("%b %d")
    day0 = int(wide["day_num"].iloc[0])
    day1 = int(wide["day_num"].iloc[-1])
    print(SEP)
    print("  Iran BM Forecast Benchmark — Out-of-Sample Evaluation")
    print(f"  Predictions generated: Mar 29, 2026 (Day 30) — frozen, pre-observation")
    print(f"  Test window: {d0}–{d1}  (Days {day0}–{day1},  n={n})")
    print(SEP)


def print_day_table(wide: pd.DataFrame):
    print("\n── Per-Day Results ───────────────────────────────────────────────────")
    # Header
    print(f"  {'Date':<10} {'Day':>3} {'Act':>4} {'[min-max]':>9}  "
          f"{'─── Model C ───':^22}  "
          f"{'─── Model O ───':^22}  "
          f"{'Mix50 μ':>7}  {'MixEW μ':>7}")
    print(f"  {'':10} {'':3} {'':4} {'':9}  "
          f"{'μ':>5} {'Z':>6} {'LL':>6} {'PI':>3}  "
          f"{'μ':>5} {'Z':>6} {'LL':>6} {'PI':>3}  "
          f"{'':7}  {'':7}")
    print("  " + "─" * 88)

    for _, r in wide.iterrows():
        flag = "*" if "LOW_CONFIDENCE" in str(r.get("flags", "")) else " "
        min_v = r.get("bm_il_min")
        max_v = r.get("bm_il_max")
        rng   = f"[{int(min_v)}-{int(max_v)}]" if pd.notna(min_v) and pd.notna(max_v) else "   —   "
        pi_c  = "✓" if r["in90_C"] else "✗"
        pi_o  = "✓" if r["in90_O"] else "✗"
        print(f"  {r['date'].strftime('%b %d'):<10} {int(r['day_num']):>3} "
              f"{r['isr_bm']:>4.0f}{flag} {rng:>9}  "
              f"{r['mu_C']:>5.2f} {r['z_C']:>+6.2f} {r['ll_C']:>6.2f} {pi_c:>3}  "
              f"{r['mu_O']:>5.2f} {r['z_O']:>+6.2f} {r['ll_O']:>6.2f} {pi_o:>3}  "
              f"{r['mu_mix50']:>7.2f}  {r['mu_mix_ev']:>7.2f}")

    if wide["flags"].fillna("").str.contains("LOW_CONFIDENCE").any():
        print("  * = LOW_CONFIDENCE observation (see flags column)")


def print_aggregate(wide: pd.DataFrame, agg: dict):
    print("\n── Aggregate Metrics ─────────────────────────────────────────────────")
    print(f"  {'Metric':<26}  {'Model C':>9}  {'Model O':>9}  "
          f"{'Mix-50':>9}  {'Mix-EW':>9}")
    print("  " + "─" * 70)

    # For MAE/RMSE/|bias|/|mean_z|: lower is better; for LL: higher is better
    metric_rows = [
        ("MAE",                "mae",      "{:9.3f}", False),
        ("RMSE",               "rmse",     "{:9.3f}", False),
        ("Cumul. bias Σ(y−μ)", "bias",     "{:+9.1f}", "near_zero"),
        ("Mean Z-score",       "mean_z",   "{:+9.3f}", "near_zero"),
        ("Total log-likelihood","total_ll", "{:9.3f}", True),
    ]

    for label, key, fmt, higher_better in metric_rows:
        vals = {v: agg[v][key] for v in ("C", "O", "Mix-50", "Mix-EW")}
        if higher_better is True:
            best = max(vals, key=vals.get)
        elif higher_better is False:
            best = min(vals, key=lambda k: abs(vals[k]))
        else:  # near_zero
            best = min(vals, key=lambda k: abs(vals[k]))

        row = f"  {label:<26}  "
        for v in ("C", "O", "Mix-50", "Mix-EW"):
            cell = fmt.format(vals[v])
            marker = " ◄" if v == best else "  "
            row += cell + marker
        print(row)

    # PI coverage (only C and O have prediction intervals)
    print(f"\n  {'90% PI coverage':<26}  "
          f"{agg['C']['cov90']:>8.0%}    "
          f"{agg['O']['cov90']:>8.0%}    "
          f"{'—':>9}    {'—':>9}    (expected 90%)")
    print(f"  {'50% PI coverage':<26}  "
          f"{agg['C']['cov50']:>8.0%}    "
          f"{agg['O']['cov50']:>8.0%}    "
          f"{'—':>9}    {'—':>9}    (expected 50%)")

    # LL ranking
    lls  = {v: agg[v]["total_ll"] for v in ("C", "O", "Mix-50", "Mix-EW")}
    best = max(lls, key=lls.get)
    print(f"\n  Log-likelihood ranking:")
    for v, ll in sorted(lls.items(), key=lambda x: -x[1]):
        delta = ll - lls[best]
        tag   = "◄ BEST" if delta == 0 else f"ΔLL={delta:+.3f}"
        print(f"    {v:<8}  LL={ll:8.3f}  {tag}")


def print_model_weights(wide: pd.DataFrame):
    w_c    = float(wide["w_c_ev"].iloc[0])
    w_o    = float(wide["w_o_ev"].iloc[0])
    ll_c   = wide["ll_C"].sum()
    ll_o   = wide["ll_O"].sum()
    n      = len(wide)

    print("\n── Bayesian Model Weights (Mix-EW) ───────────────────────────────────")
    print(f"  Estimated on all {n} test day(s) — equal priors, Poisson likelihoods.")
    if n < 7:
        print(f"  ⚠  Low power: <7 days.  Weights will stabilise by Apr 15–18 (Day 47–50).")
    print(f"  Model C: ΣLL = {ll_c:8.3f}  →  w_C = {w_c:.4f}  ({100*w_c:.1f}%)")
    print(f"  Model O: ΣLL = {ll_o:8.3f}  →  w_O = {w_o:.4f}  ({100*w_o:.1f}%)")

    # Current Mix-EW μ range across test window
    mu_ev_lo = float(wide["mu_mix_ev"].min())
    mu_ev_hi = float(wide["mu_mix_ev"].max())
    print(f"  Mix-EW μ in test window: [{mu_ev_lo:.2f}–{mu_ev_hi:.2f}] BM/day")

    diff = abs(w_c - w_o)
    if diff < 0.10:
        verdict = "Models C and O are nearly indistinguishable on current data."
    elif w_c > w_o:
        verdict = f"Weak evidence for Model C (Conservative) by {100*diff:.1f}pp."
    else:
        verdict = f"Weak evidence for Model O (Observable) by {100*diff:.1f}pp."
    print(f"\n  Signal: {verdict}")


def print_weekly_ztable(wide: pd.DataFrame):
    n = len(wide)
    print("\n── 7-Day Rolling Z-scores ────────────────────────────────────────────")
    if n < 7:
        print(f"  Need ≥7 test days (currently {n}).  Table will appear automatically.")
        return

    days  = wide["day_num"].values
    obs   = wide["isr_bm"].values
    dates = wide["date"].dt.strftime("%b%d").values

    print(f"  {'Window':<18}  {'W_obs':>6}  "
          f"{'── Model C ──':^24}  {'── Model O ──':^24}")
    print(f"  {'':18}  {'':6}  "
          f"{'E[W]':>6} {'Z':>6} {'':10}  "
          f"{'E[W]':>6} {'Z':>6} {'':10}")
    print("  " + "─" * 76)

    for i in range(n - 6):
        wd     = days[i:i+7]
        wo     = obs[i:i+7]
        win    = f"{dates[i]}–{dates[i+6]}"
        e_c    = sum(float(wide.loc[wide["day_num"]==d, "mu_C"].values[0]) for d in wd)
        e_o    = sum(float(wide.loc[wide["day_num"]==d, "mu_O"].values[0]) for d in wd)
        w_obs  = float(sum(wo))
        z_c    = (w_obs - e_c) / math.sqrt(e_c)
        z_o    = (w_obs - e_o) / math.sqrt(e_o)

        print(f"  {win:<18}  {w_obs:>6.0f}  "
              f"{e_c:>6.1f} {z_c:>+6.2f} {z_label(z_c):<10}  "
              f"{e_o:>6.1f} {z_o:>+6.2f} {z_label(z_o)}")


def print_discrimination_power(wide: pd.DataFrame):
    """How many days needed to distinguish C vs O at 80% power."""
    # At Day 30: μ_C ≈ 10.88, μ_O ≈ 9.82.  Daily gap ≈ 1.06 BM.
    # Weekly sum gap ≈ 7.4 BM over 7 days.  σ_weekly ≈ √(7 × 10.35) ≈ 8.5
    # Weekly Z separation ≈ 7.4 / 8.5 ≈ 0.87 per week.
    # Need |Z| > 1.65 for 95% one-sided power → need ~(1.65/0.87)² ≈ 3.6 weeks.
    n   = len(wide)
    mu_c_mean = float(wide["mu_C"].mean())
    mu_o_mean = float(wide["mu_O"].mean())
    gap       = mu_c_mean - mu_o_mean
    sigma_wk  = math.sqrt(7 * (mu_c_mean + mu_o_mean) / 2)
    z_sep_wk  = 7 * gap / sigma_wk
    weeks_80  = math.ceil((1.28 / z_sep_wk) ** 2)   # 80% power: z_crit = 1.28

    print("\n── Discrimination Power ──────────────────────────────────────────────")
    print(f"  Test days so far: {n}")
    print(f"  Mean μ_C={mu_c_mean:.2f}  μ_O={mu_o_mean:.2f}  "
          f"daily gap={gap:.2f} BM/day")
    print(f"  Weekly Z separation between C and O: ~{z_sep_wk:.2f}σ per 7-day window")
    print(f"  → 80% power to distinguish models needs ~{weeks_80} full week(s) "
          f"of test data ({7*weeks_80} days)")
    print(f"  → Checkpoint: Apr 15–18 (Days 47–50, ~3 weeks out-of-sample)")


def save_csv(wide: pd.DataFrame):
    cols = [
        "date", "day_num", "isr_bm", "bm_il_min", "bm_il_max", "flags",
        "mu_C",     "mu_O",     "mu_mix50",   "mu_mix_ev",
        "resid_C",  "resid_O",  "resid_mix50","resid_mix_ev",
        "z_C",      "z_O",      "z_mix50",    "z_mix_ev",
        "ll_C",     "ll_O",     "ll_mix50",   "ll_mix_ev",
        "in90_C",   "in90_O",   "in50_C",     "in50_O",
        "w_c_ev",   "w_o_ev",
    ]
    out = wide[cols].copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    out.to_csv(OUT_FILE, index=False, float_format="%.4f")
    print(f"\n  Results saved → {OUT_FILE.relative_to(OUT_FILE.parent.parent)}")


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Evaluate Models C and O on out-of-sample strike data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python model/benchmark.py
  python model/benchmark.py --days 30-32
  python model/benchmark.py --days 30-50 --weekly
  python model/benchmark.py --no-low-conf
        """)
    p.add_argument("--days",        type=str,  default=None,
                   help="Day range to evaluate, e.g. '30-35'. "
                        "Default: all days with both predictions and actuals.")
    p.add_argument("--no-low-conf", action="store_true",
                   help="Exclude LOW_CONFIDENCE observations from evaluation.")
    p.add_argument("--weekly",      action="store_true",
                   help="Show 7-day rolling Z-score table (auto-shown when n≥7).")
    return p.parse_args()


def main():
    args = parse_args()

    day_lo = day_hi = None
    if args.days:
        parts = args.days.split("-")
        if len(parts) != 2:
            raise SystemExit("--days format must be 'lo-hi', e.g. '30-35'")
        day_lo, day_hi = int(parts[0]), int(parts[1])

    wide = load_and_join(day_lo, day_hi, drop_low_conf=args.no_low_conf)
    agg  = compute_agg(wide)

    print_header(wide)
    print_day_table(wide)
    print_aggregate(wide, agg)
    print_model_weights(wide)

    if args.weekly or len(wide) >= 7:
        print_weekly_ztable(wide)

    print_discrimination_power(wide)
    save_csv(wide)


if __name__ == "__main__":
    main()
