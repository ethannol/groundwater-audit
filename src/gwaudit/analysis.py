"""Reference analysis: coverage, comparability-aware summaries, cohort comparison,
censoring-aware change, and well-level uncertainty.

Reads data/processed/analysis_samples.csv and data/processed/replicates.csv.
Writes reports/results.json, reports/tables/*.csv and reports/figures/*.png.

Run: python -m gwaudit.analysis

Target quantity (one sentence): for each constituent, the direction and size of
change in observed dissolved concentration at the same well between the early
period and the late period, using the last routine groundwater sample of each
period, over wells sampled in both periods (the consistent cohort).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from gwaudit.censoring import interval_compare, km_quantile, substitute

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
REP = ROOT / "reports"
FIG = REP / "figures"
TAB = REP / "tables"

FAMILIES = {"arsenic": "Arsenic, dissolved (ug/L)", "nitrate_as_n": "Nitrate as N, dissolved (mg/L)"}
THRESHOLD = {"arsenic": 10.0, "nitrate_as_n": 10.0}  # US EPA MCLs, used only as descriptive reference levels
PERIODS = {"early": (2000, 2011), "late": (2012, 2023)}
SEED = 20261007
N_BOOT = 2000


def period_of(year: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=year.index, dtype="object")
    for name, (a, b) in PERIODS.items():
        out[(year >= a) & (year <= b)] = name
    return out


# ---------------------------------------------------------------- coverage
def coverage(d: pd.DataFrame) -> dict:
    per_well = d.groupby("site_id").size()
    gaps = d.sort_values("date").groupby("site_id")["date"].diff().dt.days.dropna()
    return {
        "rows": int(len(d)), "wells": int(d["site_id"].nunique()),
        "first_date": str(d["date"].min().date()), "last_date": str(d["date"].max().date()),
        "samples_per_well": {"1": int((per_well == 1).sum()), "2": int((per_well == 2).sum()),
                             "3-5": int(per_well.between(3, 5).sum()), "6+": int((per_well >= 6).sum())},
        "median_days_between_samples_same_well": float(gaps.median()) if len(gaps) else None,
        "censored": int(d["censored"].sum()), "censored_share": round(float(d["censored"].mean()), 4),
        "dnq": int(d["dnq"].sum()), "estimated": int(d["estimated"].sum()),
        "detected_without_limit": int((~d["censored"] & d["dl_missing"]).sum()),
        "time_missing": int((d["time"] == "").sum()),
        "status": d["status"].value_counts().to_dict(),
        "labs": d["lab"].replace("", "(blank)").value_counts().to_dict(),
        "methods": d["method_id"].replace("", "(blank)").value_counts().head(8).to_dict(),
        "aquifers": d["aquifer"].fillna("").replace("", "(blank)").value_counts().to_dict(),
        "same_day_multiple_activities_rows": int((d["same_day_activities"] > 1).sum()),
    }


def limits_by_year(d: pd.DataFrame) -> pd.DataFrame:
    nd = d[d["censored"]]
    g = nd.groupby("year")["dl"].agg(["count", "min", "median", "max"]).round(3)
    g["n_all"] = d.groupby("year").size()
    g["censored_share"] = (g["count"] / g["n_all"]).round(3)
    return g.reset_index()


# ---------------------------------------------------------------- summaries
def censored_summary(lower, upper, threshold) -> dict:
    lower = np.asarray(lower, float); upper = np.asarray(upper, float)
    n = len(lower)
    out = {"n": int(n), "censored": int((lower < upper).sum())}
    if n == 0:
        return out
    out["km_median"] = km_quantile(lower, upper, 0.5)
    out["km_p75"] = km_quantile(lower, upper, 0.75)
    # share above threshold is identifiable only when no censored interval straddles it
    straddle = (lower < threshold) & (upper > threshold) & (lower < upper)
    out["above_threshold_share"] = round(float((lower > threshold).mean()), 4) if not straddle.any() else None
    out["above_threshold_undetermined"] = int(straddle.sum())
    out["sub_half_median"] = float(np.median(substitute(lower, upper, "half")))
    out["sub_zero_median"] = float(np.median(substitute(lower, upper, "zero")))
    out["sub_limit_median"] = float(np.median(substitute(lower, upper, "limit")))
    return out


def last_per_well_period(d: pd.DataFrame) -> pd.DataFrame:
    d = d.dropna(subset=["period"]).sort_values(["site_id", "date"])
    return d.groupby(["site_id", "period"], as_index=False).tail(1)


def pooled_vs_cohort(d: pd.DataFrame, fam: str) -> dict:
    thr = THRESHOLD[fam]
    out = {"periods": PERIODS}
    for p in PERIODS:
        s = d[d["period"] == p]
        out[f"pooled_{p}"] = {"wells": int(s["site_id"].nunique()), **censored_summary(s["lower"], s["upper"], thr)}
    one = last_per_well_period(d)
    for p in PERIODS:
        s = one[one["period"] == p]
        out[f"one_per_well_{p}"] = {"wells": int(len(s)), **censored_summary(s["lower"], s["upper"], thr)}
    both = one.groupby("site_id")["period"].nunique()
    cohort_ids = both[both == len(PERIODS)].index
    out["cohort_wells"] = int(len(cohort_ids))
    out["wells_only_early"] = int(((one["period"] == "early") & ~one["site_id"].isin(cohort_ids)).sum())
    out["wells_only_late"] = int(((one["period"] == "late") & ~one["site_id"].isin(cohort_ids)).sum())
    coh = one[one["site_id"].isin(cohort_ids)]
    for p in PERIODS:
        s = coh[coh["period"] == p]
        out[f"cohort_{p}"] = {"wells": int(len(s)), **censored_summary(s["lower"], s["upper"], thr)}
    return out, coh


def paired_change(coh: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    e = coh[coh["period"] == "early"].set_index("site_id")
    l = coh[coh["period"] == "late"].set_index("site_id")
    ids = e.index.intersection(l.index)
    pairs = pd.DataFrame({
        "early_lower": e.loc[ids, "lower"], "early_upper": e.loc[ids, "upper"], "early_date": e.loc[ids, "date"],
        "late_lower": l.loc[ids, "lower"], "late_upper": l.loc[ids, "upper"], "late_date": l.loc[ids, "date"],
    })
    pairs["years_apart"] = (pairs["late_date"] - pairs["early_date"]).dt.days / 365.25
    pairs["direction"] = [interval_compare(a, b, c, d) for a, b, c, d in
                          zip(pairs["early_lower"], pairs["early_upper"], pairs["late_lower"], pairs["late_upper"])]
    both_det = (pairs["early_lower"] == pairs["early_upper"]) & (pairs["late_lower"] == pairs["late_upper"])
    pairs["change_if_both_detected"] = np.where(both_det, pairs["late_lower"] - pairs["early_lower"], np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        pairs["log_ratio_if_both_detected"] = np.where(both_det & (pairs["early_lower"] > 0) & (pairs["late_lower"] > 0),
                                                       np.log(pairs["late_lower"] / pairs["early_lower"]), np.nan)
    counts = pairs["direction"].value_counts().to_dict()
    n_dec, n_inc = counts.get("decline", 0), counts.get("increase", 0)
    n_det = n_dec + n_inc
    res = {
        "n_pairs": int(len(pairs)), "decline": int(n_dec), "increase": int(n_inc),
        "indeterminate": int(counts.get("indeterminate", 0)),
        "median_years_apart": round(float(pairs["years_apart"].median()), 2) if len(pairs) else None,
        "both_detected": int(both_det.sum()),
    }
    if n_det > 0:
        bt = stats.binomtest(n_dec, n_det, 0.5)
        res["sign_test"] = {"declines_among_determinate": int(n_dec), "determinate": int(n_det),
                            "share_declining": round(n_dec / n_det, 4), "p_two_sided": round(bt.pvalue, 4),
                            "ci95_share_declining": [round(x, 4) for x in bt.proportion_ci(0.95)]}
    rng = np.random.default_rng(SEED)
    n = len(pairs)
    if n >= 10:
        dirs = pairs["direction"].to_numpy()
        lr = pairs["log_ratio_if_both_detected"].to_numpy()
        share_dec, med_lr = [], []
        for _ in range(N_BOOT):
            idx = rng.integers(0, n, n)
            share_dec.append((dirs[idx] == "decline").mean())
            v = lr[idx]; v = v[~np.isnan(v)]
            med_lr.append(np.median(v) if len(v) else np.nan)
        res["bootstrap_wells"] = {
            "n_boot": N_BOOT, "seed": SEED,
            "share_declining_all_pairs": round(float((dirs == "decline").mean()), 4),
            "share_declining_ci95": [round(float(x), 4) for x in np.percentile(share_dec, [2.5, 97.5])],
            "median_log_ratio_both_detected": round(float(np.nanmedian(lr)), 4) if both_det.any() else None,
            "median_log_ratio_ci95": [round(float(x), 4) for x in np.nanpercentile(med_lr, [2.5, 97.5])] if both_det.any() else None,
        }
        # Wilcoxon signed-rank on log ratios for the both-detected subset (secondary; ignores censored pairs)
        v = lr[~np.isnan(lr)]
        if len(v) >= 10 and np.any(v != 0):
            w = stats.wilcoxon(v)
            res["wilcoxon_both_detected"] = {"n": int(len(v)), "p_two_sided": round(float(w.pvalue), 4),
                                             "median_ratio_late_over_early": round(float(np.exp(np.median(v))), 4)}
    # substitution sensitivity for the median within-well change
    sens = {}
    for how in ["zero", "half", "limit"]:
        e_v = substitute(pairs["early_lower"], pairs["early_upper"], how)
        l_v = substitute(pairs["late_lower"], pairs["late_upper"], how)
        sens[how] = {"median_change": round(float(np.median(l_v - e_v)), 4) if n else None,
                     "share_declining": round(float(np.mean(l_v < e_v)), 4) if n else None}
    res["substitution_sensitivity"] = sens
    return res, pairs.reset_index().rename(columns={"index": "site_id"})


def per_well_kendall(d: pd.DataFrame, min_n: int = 6) -> pd.DataFrame:
    rows = []
    for sid, g in d.sort_values("date").groupby("site_id"):
        if len(g) < min_n:
            continue
        lo, hi = g["lower"].to_numpy(), g["upper"].to_numpy()
        S = 0; npairs = 0
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                c = interval_compare(lo[i], hi[i], lo[j], hi[j])
                S += {"increase": 1, "decline": -1, "indeterminate": 0}[c]
                npairs += 1
        rows.append({"site_id": sid, "n": len(g), "years": round((g["date"].max() - g["date"].min()).days / 365.25, 1),
                     "censored": int(g["censored"].sum()), "kendall_S": S, "tau": round(S / npairs, 3)})
    return pd.DataFrame(rows)


def replicate_precision(reps: pd.DataFrame, d: pd.DataFrame, fam: str) -> dict:
    r = reps[(reps["family"] == fam) & (reps["pcode_role"] == "primary") & ~reps["censored"]]
    s = d[~d["censored"]]
    m = r.merge(s[["site_id", "date", "value"]], on=["site_id", "date"], suffixes=("_rep", "_routine"))
    m = m.drop_duplicates(["site_id", "date", "value_rep"])
    if len(m) == 0:
        return {"pairs": 0}
    rpd = 200 * (m["value_rep"] - m["value_routine"]).abs() / (m["value_rep"] + m["value_routine"])
    return {"pairs": int(len(m)), "median_rpd_pct": round(float(rpd.median()), 2),
            "p90_rpd_pct": round(float(rpd.quantile(0.9)), 2)}


# ---------------------------------------------------------------- figures
def figures(data: dict[str, pd.DataFrame], pairs: dict[str, pd.DataFrame], results: dict) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, (fam, d) in zip(axes, data.items()):
        g = d.groupby(["year", "censored"]).size().unstack(fill_value=0)
        ax.bar(g.index, g.get(False, 0), color="#3b6ea5", label="detected")
        ax.bar(g.index, g.get(True, 0), bottom=g.get(False, 0), color="#d08c3a", label="non-detect")
        ax.set_title(FAMILIES[fam]); ax.set_xlabel("year"); ax.set_ylabel("routine groundwater samples")
        ax.axvspan(PERIODS["early"][0] - 0.5, PERIODS["early"][1] + 0.5, color="grey", alpha=0.08)
        ax.legend(frameon=False)
    fig.suptitle("Figure 1. Sampling coverage by year (shaded: early period)")
    fig.tight_layout(); fig.savefig(FIG / "fig1_coverage.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, (fam, d) in zip(axes, data.items()):
        nd = d[d["censored"]]
        for lab, g in nd.groupby(nd["lab"].replace("", "(blank)")):
            ax.scatter(g["date"], g["dl"], s=12, alpha=0.6, label=lab[:28])
        ax.set_yscale("log"); ax.set_title(FAMILIES[fam]); ax.set_ylabel("reporting limit of non-detects")
        ax.legend(frameon=False, fontsize=7)
    fig.suptitle("Figure 2. Reporting limits of non-detects over time, by laboratory")
    fig.tight_layout(); fig.savefig(FIG / "fig2_limits.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, fam in zip(axes, data):
        p = pairs[fam]
        if len(p) == 0:
            ax.set_title(FAMILIES[fam] + " (no cohort pairs)"); continue
        floor = max(min(p["early_upper"].min(), p["late_upper"].min()) * 0.5, 1e-3)
        x = np.where(p["early_lower"] == p["early_upper"], p["early_lower"], p["early_upper"])
        y = np.where(p["late_lower"] == p["late_upper"], p["late_lower"], p["late_upper"])
        x = np.maximum(x, floor); y = np.maximum(y, floor)
        cens = (p["early_lower"] < p["early_upper"]) | (p["late_lower"] < p["late_upper"])
        colors = p["direction"].map({"decline": "#2a7f62", "increase": "#b5443c", "indeterminate": "#888888"})
        ax.scatter(x[~cens], y[~cens], c=colors[~cens], s=18, alpha=0.8, label="both detected")
        ax.scatter(x[cens], y[cens], facecolors="none", edgecolors=colors[cens], s=22, label="≥1 non-detect (plotted at limit)")
        lim = [floor, max(x.max(), y.max()) * 1.3]
        ax.plot(lim, lim, "k--", lw=0.8); ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(lim); ax.set_ylim(lim)
        ax.set_xlabel(f"early period ({PERIODS['early'][0]}–{PERIODS['early'][1]}), last sample")
        ax.set_ylabel(f"late period ({PERIODS['late'][0]}–{PERIODS['late'][1]}), last sample")
        r = results[fam]["paired_change"]
        ax.set_title(f"{FAMILIES[fam]}\n{r['n_pairs']} wells: {r['decline']} decline, {r['increase']} increase, {r['indeterminate']} indeterminate")
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Figure 3. Consistent cohort: same well, early vs late (green: decline, red: increase, grey: indeterminate)")
    fig.tight_layout(); fig.savefig(FIG / "fig3_cohort_pairs.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    for ax, fam in zip(axes, data):
        r = results[fam]["pooled_vs_cohort"]
        labels, vals, wells = [], [], []
        for kind in ["pooled", "one_per_well", "cohort"]:
            for p in PERIODS:
                s = r[f"{kind}_{p}"]
                labels.append(f"{kind}\n{p}"); vals.append(s.get("km_median") or np.nan); wells.append(s["wells"])
        xs = np.arange(len(labels))
        ax.bar(xs, vals, color=["#9bb7d4", "#3b6ea5"] * 3)
        for xi, w, v in zip(xs, wells, vals):
            ax.text(xi, (0 if np.isnan(v) else v), f"n={w}", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(xs); ax.set_xticklabels(labels, fontsize=7); ax.set_ylabel("Kaplan–Meier median")
        ax.set_title(FAMILIES[fam])
    fig.suptitle("Figure 4. Period medians: all samples, one per well, and the consistent cohort")
    fig.tight_layout(); fig.savefig(FIG / "fig4_pooled_vs_cohort.png", dpi=150); plt.close(fig)


# ---------------------------------------------------------------- main
def run() -> dict:
    d_all = pd.read_csv(PROC / "analysis_samples.csv", dtype={"site_id": str, "time": str, "lab": str, "method_id": str,
                                                              "aquifer": str, "status": str}, keep_default_na=False,
                        na_values={"value": [""], "dl": [""], "lower": [""], "upper": [""], "value_num": [""], "dl_num": [""]})
    d_all["date"] = pd.to_datetime(d_all["date"])
    d_all["period"] = period_of(d_all["year"])
    reps = pd.read_csv(PROC / "replicates.csv", dtype=str, keep_default_na=False)
    reps["date"] = pd.to_datetime(reps["date"]); reps["value"] = pd.to_numeric(reps["value"].replace("", np.nan))
    reps["censored"] = reps["censored"] == "True"
    TAB.mkdir(parents=True, exist_ok=True)
    results, data, pairs_all = {"periods": PERIODS, "thresholds_reference_only": THRESHOLD}, {}, {}
    for fam in FAMILIES:
        d = d_all[d_all["family"] == fam].copy()
        data[fam] = d
        res = {"label": FAMILIES[fam], "coverage": coverage(d)}
        lby = limits_by_year(d); lby.to_csv(TAB / f"{fam}_limits_by_year.csv", index=False)
        res["limits_by_year"] = lby.to_dict("records")
        res["pooled_vs_cohort"], coh = pooled_vs_cohort(d, fam)
        res["paired_change"], pairs = paired_change(coh)
        pairs.to_csv(TAB / f"{fam}_cohort_pairs.csv", index=False)
        pairs_all[fam] = pairs
        kt = per_well_kendall(d); kt.to_csv(TAB / f"{fam}_per_well_kendall.csv", index=False)
        res["per_well_kendall"] = {"wells_with_6plus_samples": int(len(kt)),
                                   "tau_le_-0.5": int((kt["tau"] <= -0.5).sum()) if len(kt) else 0,
                                   "tau_ge_0.5": int((kt["tau"] >= 0.5).sum()) if len(kt) else 0,
                                   "median_tau": round(float(kt["tau"].median()), 3) if len(kt) else None}
        res["replicate_precision"] = replicate_precision(reps, d, fam)
        results[fam] = res
    figures(data, pairs_all, results)
    (REP / "results.json").write_text(json.dumps(results, indent=2, default=str) + "\n")
    return results


if __name__ == "__main__":
    r = run()
    for fam in FAMILIES:
        print("=====", fam)
        print(json.dumps({k: r[fam][k] for k in ["coverage", "pooled_vs_cohort", "paired_change", "per_well_kendall", "replicate_precision"]}, indent=1, default=str))
