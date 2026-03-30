"""
Generate README figures for iran-bm-forecast.

Outputs (saved to figures/):
  fig1_launch_timeline.png    — March actuals + model fit + forward forecast with 90% bands
  fig2_launcher_depletion.png — Launcher count projection for both models (step/integer)
  fig3_march_data.png          — March daily BM bar chart, multi-source comparison

Usage:
    pip install matplotlib
    python model/plot_figures.py
"""

import datetime
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy.stats import poisson as poisson_dist

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO = Path(__file__).parent.parent
DATA_FILE    = REPO / "data" / "israel_daily_estimate.csv"
SOURCES_FILE = REPO / "data" / "all_sources_daily.csv"
OUT_DIR = REPO / "figures"
OUT_DIR.mkdir(exist_ok=True)

WAR_START = datetime.date(2026, 2, 28)

# ── Model parameters (identical to poisson_model.py) ─────────────────────────
MODELS = {
    "C": {"label": "Model C — Conservative (HL 83d)", "mu0": 12.43, "alpha": 0.0083, "t0": 14,
          "color": "#E07B39", "color_fill": "#E07B39"},
    "O": {"label": "Model O — Observable (HL 35d)",   "mu0": 13.52, "alpha": 0.020,  "t0": 14,
          "color": "#3A7DC9", "color_fill": "#3A7DC9"},
}

FORECAST_END          = 306   # Day 306 ≈ Dec 29, 2026
LAUNCHER_BASELINE_DAY = 28
LAUNCHER_BASELINE_N   = 140

WAVE_RATIO = 1.11   # Alma waves → BM estimate calibration factor

# ── Phase definitions ──────────────────────────────────────────────────────────
PHASES = [
    (1,  4,  "Phase I — Saturation",    "#FF4444"),
    (5,  7,  "Phase II — Collapse",     "#FF8800"),
    (8,  13, "Phase IIIa — Transition", "#AA88FF"),
    (14, 29, "Phase IIIb — Attrition",  "#44BB44"),
]


def day_to_date(day_num: int) -> datetime.date:
    return WAR_START + datetime.timedelta(days=day_num - 1)


def mu(day_num: int, model: dict) -> float:
    return model["mu0"] * math.exp(-model["alpha"] * (day_num - model["t0"]))


def pi90(day_num: int, model: dict):
    m = mu(day_num, model)
    return poisson_dist.ppf(0.05, m), poisson_dist.ppf(0.95, m)


def launcher_count(day_num: int, model: dict, baseline: float = LAUNCHER_BASELINE_N) -> float:
    return baseline * math.exp(-model["alpha"] * (day_num - LAUNCHER_BASELINE_DAY))


def launcher_zero_day(model: dict) -> int:
    """Day when expected launcher count first drops below 1 (last launcher gone)."""
    return int(LAUNCHER_BASELINE_DAY + math.log(LAUNCHER_BASELINE_N) / model["alpha"])


def load_data():
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    return df.sort_values("day_num").reset_index(drop=True)


def load_sources():
    df = pd.read_csv(SOURCES_FILE, parse_dates=["date"])
    return df.sort_values("day_num").reset_index(drop=True)


# ── Shared style ───────────────────────────────────────────────────────────────
def apply_style():
    plt.rcParams.update({
        "figure.facecolor":  "#0D1117",
        "axes.facecolor":    "#0D1117",
        "axes.edgecolor":    "#30363D",
        "axes.labelcolor":   "#C9D1D9",
        "xtick.color":       "#8B949E",
        "ytick.color":       "#8B949E",
        "text.color":        "#C9D1D9",
        "grid.color":        "#21262D",
        "grid.linewidth":    0.6,
        "font.family":       "DejaVu Sans",
        "font.size":         10,
        "legend.facecolor":  "#161B22",
        "legend.edgecolor":  "#30363D",
    })


# ── Fig 1: Launch timeline ─────────────────────────────────────────────────────
def fig1_launch_timeline(df):
    apply_style()
    fig, ax = plt.subplots(figsize=(14, 6))

    zero_O = launcher_zero_day(MODELS["O"])   # ~Day 276, late Nov

    # ── Forecast model lines + bands ──
    for key, m in MODELS.items():
        end = min(FORECAST_END, zero_O) if key == "O" else FORECAST_END
        fdays = list(range(30, end + 1))
        fdates = [day_to_date(d) for d in fdays]
        mu_v  = [mu(d, m) for d in fdays]
        lo_v  = [pi90(d, m)[0] for d in fdays]
        hi_v  = [pi90(d, m)[1] for d in fdays]

        ax.plot(fdates, mu_v, color=m["color"], linewidth=2, label=m["label"], zorder=4)
        ax.fill_between(fdates, lo_v, hi_v, color=m["color_fill"], alpha=0.18, zorder=2)

        if key == "O":
            term_date = day_to_date(end)
            ax.axvline(term_date, color=m["color"], linewidth=1.2,
                       linestyle=":", alpha=0.7, zorder=3)
            ax.annotate("last launcher\n(Model O)",
                        xy=(term_date, mu_v[-1]),
                        xytext=(term_date, mu_v[-1] + 4),
                        fontsize=7.5, color=m["color"], ha="center",
                        arrowprops=dict(arrowstyle="-", color=m["color"], alpha=0.5))

    # ── Model fit dashed lines over Phase IIIb training window ──
    fit_days  = list(range(14, 30))
    fit_dates = [day_to_date(d) for d in fit_days]
    for key, m in MODELS.items():
        ax.plot(fit_dates, [mu(d, m) for d in fit_days],
                color=m["color"], linewidth=1.8, linestyle="--", alpha=0.65, zorder=4)

    # ── Actual daily BM bars ──
    hist = df.dropna(subset=["isr_bm"])
    ax.bar([d.date() for d in hist["date"]], hist["isr_bm"],
           width=0.7, color="#58A6FF", alpha=0.75,
           label="Observed daily BM (Israel)", zorder=3)

    # ── Phase shading (no text labels) ──
    phase_patches = []
    for d0, d1, label, col in PHASES:
        ax.axvspan(day_to_date(d0), day_to_date(d1 + 1), alpha=0.07, color=col, zorder=1)
        phase_patches.append(mpatches.Patch(color=col, alpha=0.5, label=label))

    # ── Half-life markers (from Phase IIIb anchor t0=Day 14) ──
    for key, m in MODELS.items():
        hl_days   = math.log(2) / m["alpha"]
        hl_day    = int(m["t0"] + hl_days)
        hl_date   = day_to_date(hl_day)
        hl_mu     = mu(hl_day, m)   # = mu0/2
        ax.axvline(hl_date, color=m["color"], linewidth=1.2,
                   linestyle="-.", alpha=0.55, zorder=3)
        ax.annotate(f"HL (Model {key})\n{hl_date.strftime('%b %d')}",
                    xy=(hl_date, hl_mu),
                    xytext=(hl_date, hl_mu + 2.5),
                    fontsize=7, color=m["color"], ha="center", va="bottom",
                    arrowprops=dict(arrowstyle="-", color=m["color"], alpha=0.4))

    # ── 1 BM/day vertical markers (when each model crosses μ=1) ──
    ONE_BM_COLOR = "#60AAFF"
    for key, m in MODELS.items():
        t_cross = m["t0"] + math.log(m["mu0"]) / m["alpha"]
        if t_cross <= FORECAST_END:
            cross_date = day_to_date(int(t_cross))
            ax.axvline(cross_date, color=ONE_BM_COLOR, linewidth=1.2,
                       linestyle=":", alpha=0.7, zorder=3)
            ax.annotate(f"1 BM/day\n(Model {key})\n{cross_date.strftime('%b %d')}",
                        xy=(cross_date, 1),
                        xytext=(cross_date, 4),
                        fontsize=7, color=ONE_BM_COLOR, ha="center", va="bottom",
                        arrowprops=dict(arrowstyle="-", color=ONE_BM_COLOR, alpha=0.5))

    # ── Forecast boundary ──
    ax.axvline(day_to_date(30), color="#8B949E", linewidth=1, linestyle=":", alpha=0.7)
    ax.text(day_to_date(30), 1.01, " Forecast →",
            transform=ax.get_xaxis_transform(),
            ha="left", va="bottom", fontsize=8.5, color="#8B949E")

    # ── Month grid ──
    for month in range(4, 13):
        ax.axvline(datetime.date(2026, month, 1), color="#21262D", linewidth=0.8, zorder=1)

    ax.set_xlim(day_to_date(1), day_to_date(FORECAST_END))
    ax.set_ylim(0, None)
    ax.set_xlabel("Date (2026)", labelpad=8)
    ax.set_ylabel("BMs launched at Israel / day")
    ax.set_title("Iranian Ballistic Missile Strikes at Israel — March 2026 to End-2026\n"
                 "Shaded bands = 90% prediction interval  ·  dashed = Phase IIIb model fit",
                 fontsize=12, fontweight="bold", pad=12)

    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax.grid(axis="y", zorder=0)

    # ── Interleaved legend: left col = model items, right col = phases ──
    # Build handles manually to guarantee correct ordering (bypasses get_legend_handles_labels)
    from matplotlib.lines import Line2D
    h_mc  = Line2D([0], [0], color=MODELS["C"]["color"], lw=2,
                   label=MODELS["C"]["label"])
    h_mo  = Line2D([0], [0], color=MODELS["O"]["color"], lw=2,
                   label=MODELS["O"]["label"])
    h_obs = mpatches.Patch(color="#58A6FF", alpha=0.75,
                            label="Observed daily BM (Israel)")
    h_fan = mpatches.Patch(color="#888888", alpha=0.35, label="90% PI band")

    # Interleave: row-by-row [left, right] with ncol=2
    # Row 0: Model C | Phase I    Row 1: Model O | Phase II
    # Row 2: Observed | Phase IIIa  Row 3: 90% PI | Phase IIIb
    # matplotlib ncol fills column-by-column (top→bottom per col, then next col)
    # So to get left=[MC,MO,Obs,Fan] right=[PI,PII,PIIIa,PIIIb]: concatenate, don't interleave
    left_col  = [h_mc, h_mo, h_obs, h_fan]
    right_col = phase_patches          # [PhaseI, PhaseII, PhaseIIIa, PhaseIIIb]

    ax.legend(handles=left_col + right_col,
              loc="upper right", fontsize=8.5, framealpha=0.85, ncol=2,
              handlelength=1.5, columnspacing=1.0)

    fig.tight_layout()
    out = OUT_DIR / "fig1_launch_timeline.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ── Fig 2: Launcher depletion (step chart) ────────────────────────────────────
def fig2_launcher_depletion():
    apply_style()
    fig, ax = plt.subplots(figsize=(12, 5.5))

    days  = list(range(LAUNCHER_BASELINE_DAY, FORECAST_END + 1))
    dates = [day_to_date(d) for d in days]

    for key, m in MODELS.items():
        raw     = [launcher_count(d, m) for d in days]
        floored = [max(0, int(math.floor(v))) for v in raw]
        lo = [max(0, int(math.floor(launcher_count(d, m, LAUNCHER_BASELINE_N * 0.85)))) for d in days]
        hi = [max(0, int(math.ceil( launcher_count(d, m, LAUNCHER_BASELINE_N * 1.15)))) for d in days]

        ax.step(dates, floored, where="post", color=m["color"], linewidth=2.2,
                label=m["label"], zorder=4)
        ax.fill_between(dates, lo, hi, step="post",
                        color=m["color_fill"], alpha=0.13, zorder=2)

    # ── Half-life reference lines (from launcher baseline Day 28) ──
    for key, m in MODELS.items():
        hl_days = math.log(2) / m["alpha"]
        hl_day_num = int(LAUNCHER_BASELINE_DAY + hl_days)
        hl_date = day_to_date(hl_day_num)
        hl_count = int(LAUNCHER_BASELINE_N / 2)
        ax.axvline(hl_date, color=m["color"], linewidth=1.2, linestyle="-.",
                   alpha=0.55, zorder=3)
        ax.text(hl_date, 75 if key == "C" else 85,
                f" HL\n (Model {key})\n {hl_date.strftime('%b %d')}",
                fontsize=7.5, color=m["color"], alpha=0.85, ha="left", va="top")

    # ── Model O zero-launcher vertical line ──
    zero_O = launcher_zero_day(MODELS["O"])
    zero_O_date = day_to_date(zero_O)
    ax.axvline(zero_O_date, color=MODELS["O"]["color"], linewidth=1.5,
               linestyle="--", alpha=0.75, zorder=4)
    ax.text(zero_O_date, 8,
            f"  {zero_O_date.strftime('%b %d')}\n  Model O → 0",
            fontsize=8, color=MODELS["O"]["color"], alpha=0.9, va="bottom")

    # ── Threshold reference lines ──
    for val, label in [(100, "100"), (70, "70"), (50, "50"), (20, "20")]:
        ax.axhline(val, color="#8B949E", linewidth=0.8, linestyle="--", alpha=0.5, zorder=1)
        ax.text(day_to_date(FORECAST_END + 2), val, f" {label}",
                va="center", fontsize=8, color="#8B949E", clip_on=False)

    # ── Baseline marker ──
    ax.scatter([day_to_date(LAUNCHER_BASELINE_DAY)], [LAUNCHER_BASELINE_N],
               color="#FFFFFF", s=60, zorder=5)
    ax.text(day_to_date(LAUNCHER_BASELINE_DAY + 2), LAUNCHER_BASELINE_N + 4,
            "140 (Mar 27, ISW/IDF)", fontsize=8.5, color="#C9D1D9")

    # ── Threshold crossing annotations ──
    for key, thresh, label in [("C", 100, "May 6"), ("C", 50, "Jul 29"),
                                ("O", 100, "Apr 12"), ("O", 50, "May 17")]:
        m = MODELS[key]
        t = LAUNCHER_BASELINE_DAY + math.log(LAUNCHER_BASELINE_N / thresh) / m["alpha"]
        cross_date = day_to_date(int(t))
        yoff = 9 if key == "C" else -12
        ax.annotate(label, xy=(cross_date, thresh),
                    xytext=(cross_date, thresh + yoff),
                    fontsize=8, color=m["color"], ha="center", va="bottom",
                    arrowprops=dict(arrowstyle="-", color=m["color"], alpha=0.5, lw=1))

    # ── Month grid ──
    for month in range(4, 13):
        ax.axvline(datetime.date(2026, month, 1), color="#21262D", linewidth=0.8, zorder=1)

    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

    ax.set_xlim(day_to_date(LAUNCHER_BASELINE_DAY), day_to_date(FORECAST_END))
    ax.set_ylim(0, 155)
    ax.set_xlabel("Date (2026)", labelpad=8)
    ax.set_ylabel("Estimated operational launchers")
    ax.set_title("Iranian Launcher Attrition — Projected Through 2026\n"
                 "Baseline: ~140 operational at Mar 27 (ISW/IDF)  ·  band = ±15% uncertainty  ·  dash-dot = half-life",
                 fontsize=12, fontweight="bold", pad=12)

    ax.grid(axis="y", zorder=0)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.85)

    fig.tight_layout()
    out = OUT_DIR / "fig2_launcher_depletion.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ── Fig 3: March daily BM — multi-source comparison ───────────────────────────
def fig3_march_data(df, src):
    apply_style()
    fig, ax = plt.subplots(figsize=(13, 5))

    import matplotlib.dates as mdates

    # Merge primary estimates with raw source columns
    merged = df[["date", "day_num", "isr_bm", "bm_il_min", "bm_il_max"]].merge(
        src[["day_num", "jinsa_bm_israel", "alma_waves", "perplexity_est"]],
        on="day_num", how="left"
    ).dropna(subset=["isr_bm"])

    merged["alma_bm"] = merged["alma_waves"] * WAVE_RATIO

    # 4 bars per day — offsets in matplotlib date units (1 unit = 1 day)
    W  = 0.21    # bar width
    O1 = -0.33   # JINSA direct
    O2 = -0.11   # Alma wave-ratio
    O3 = +0.11   # Perplexity
    O4 = +0.33   # Primary reconciled

    bar_colors = {
        "jinsa":       ("#58A6FF", "JINSA direct Israel count"),
        "alma":        ("#56D364", f"Alma wave-ratio (×{WAVE_RATIO})"),
        "perplexity":  ("#BC8FE8", "Perplexity estimate"),
        "primary":     ("#F0883E", "Primary reconciled estimate"),
    }

    for _, row in merged.iterrows():
        d_num = mdates.date2num(row["date"].date())

        # JINSA direct (left)
        jinsa = row.get("jinsa_bm_israel", np.nan)
        if pd.notna(jinsa):
            ax.bar(d_num + O1, jinsa, width=W,
                   color=bar_colors["jinsa"][0], alpha=0.82, zorder=3)

        # Alma (left-center)
        alma = row.get("alma_bm", np.nan)
        if pd.notna(alma):
            ax.bar(d_num + O2, alma, width=W,
                   color=bar_colors["alma"][0], alpha=0.82, zorder=3)

        # Perplexity (right-center)
        perp = row.get("perplexity_est", np.nan)
        if pd.notna(perp):
            ax.bar(d_num + O3, perp, width=W,
                   color=bar_colors["perplexity"][0], alpha=0.82, zorder=3)

        # Primary reconciled (right)
        ax.bar(d_num + O4, row["isr_bm"], width=W,
               color=bar_colors["primary"][0], alpha=0.88, zorder=3)

    # ── Phase shading ──
    phase_patches = []
    for d0, d1, label, col in PHASES:
        ax.axvspan(mdates.date2num(day_to_date(d0)),
                   mdates.date2num(day_to_date(d1 + 1)),
                   alpha=0.07, color=col, zorder=1)
        phase_patches.append(mpatches.Patch(color=col, alpha=0.5, label=label))

    # ── Legend: interleave sources (left col) and phases (right col) ──
    source_patches = [
        mpatches.Patch(color=v[0], alpha=0.88, label=v[1])
        for v in bar_colors.values()
    ]
    # Pad sources to same length as phases
    src_col = source_patches[:]
    phs_col = phase_patches[:]
    while len(phs_col) < len(src_col):
        phs_col.append(mpatches.Patch(color="none", label=""))
    ax.legend(handles=src_col + phs_col,
              loc="upper right", fontsize=7.5, framealpha=0.85, ncol=2)

    # ── Axes formatting ──
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_minor_locator(mdates.DayLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

    xlo = mdates.date2num(day_to_date(1))  - 0.6
    xhi = mdates.date2num(day_to_date(29)) + 0.6
    ax.set_xlim(xlo, xhi)
    ax.set_ylim(0, None)
    ax.set_xlabel("Date (March 2026)", labelpad=8)
    ax.set_ylabel("BMs launched at Israel / day")
    ax.set_title("Iranian Ballistic Missile Strikes at Israel — March 2026\n"
                 "Multi-source comparison: JINSA direct | Alma wave-ratio | Perplexity | primary reconciled  ·  source: data/",
                 fontsize=12, fontweight="bold", pad=12)

    ax.grid(axis="y", zorder=0, color="#21262D", linewidth=0.6)

    fig.tight_layout()
    out = OUT_DIR / "fig3_march_data.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df  = load_data()
    src = load_sources()
    fig1_launch_timeline(df)
    fig2_launcher_depletion()
    fig3_march_data(df, src)
    print("Done. Figures saved to figures/")
