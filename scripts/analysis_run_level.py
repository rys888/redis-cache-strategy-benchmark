from __future__ import annotations

import os
from pathlib import Path
import math
import warnings

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
# Input and output locations can be overridden without editing this script:
#   RUN_LEVEL_CSV=/path/to/run_level.csv ANALYSIS_OUT=/path/to/out python analysis_run_level.py
INPUT = Path(os.environ.get("RUN_LEVEL_CSV", ROOT / "data/run_level/run_level.csv"))
OUT = Path(os.environ.get("ANALYSIS_OUT", ROOT / "analysis"))
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20260928
RNG = np.random.default_rng(SEED)
BOOT = 10000
METRICS = {
    "AvgRT": {"transform": "log", "unit": "ms"},
    "P95": {"transform": "log", "unit": "ms"},
    "Throughput": {"transform": "raw", "unit": "req/s"},
}
STRATEGIES = ["cache-aside", "read-through"]
CONCURRENCIES = [25, 50, 100]


def fmt(x, digits=4):
    if pd.isna(x):
        return "NA"
    if abs(x) < 0.0001 and x != 0:
        return f"{x:.3e}"
    return f"{x:.{digits}f}"


class HC3Model:
    def __init__(self, frame: pd.DataFrame, metric: str, include_order: bool = False):
        s = (frame["strategy"].to_numpy() == "read-through").astype(float)
        c50 = (frame["concurrency"].to_numpy() == 50).astype(float)
        c100 = (frame["concurrency"].to_numpy() == 100).astype(float)
        cols = [np.ones(len(frame)), s, c50, c100, s * c50, s * c100]
        self.names = ["Intercept", "Strategy[read-through]", "Concurrency[50]", "Concurrency[100]", "Strategy×Concurrency[50]", "Strategy×Concurrency[100]"]
        if include_order:
            cols.append(frame["order_in_block"].to_numpy(dtype=float))
            self.names.append("order_in_block")
        self.X = np.column_stack(cols)
        raw_y = frame[metric].to_numpy(dtype=float)
        self.y = np.log(raw_y) if METRICS[metric]["transform"] == "log" else raw_y
        self.n, self.p = self.X.shape
        self.df_resid = self.n - self.p
        xtx_inv = np.linalg.inv(self.X.T @ self.X)
        self.params = xtx_inv @ self.X.T @ self.y
        self.fitted = self.X @ self.params
        self.resid = self.y - self.fitted
        leverage = np.einsum("ij,jk,ik->i", self.X, xtx_inv, self.X)
        hc3_weight = (self.resid / (1 - leverage)) ** 2
        meat = self.X.T @ (self.X * hc3_weight[:, None])
        self.cov = xtx_inv @ meat @ xtx_inv
        self.cov = (self.cov + self.cov.T) / 2
        self.bse = np.sqrt(np.maximum(np.diag(self.cov), 0))
        self.tvalues = np.divide(self.params, self.bse, out=np.full_like(self.params, np.nan), where=self.bse > 0)
        self.pvalues = 2 * stats.t.sf(np.abs(self.tvalues), self.df_resid)

    def conf_int(self, alpha=0.05):
        crit = stats.t.ppf(1 - alpha / 2, self.df_resid)
        return np.column_stack([self.params - crit * self.bse, self.params + crit * self.bse])

    def f_test(self, R):
        R = np.atleast_2d(R)
        q = R.shape[0]
        rb = R @ self.params
        middle = np.linalg.pinv(R @ self.cov @ R.T)
        fvalue = float(rb.T @ middle @ rb / q)
        pvalue = float(stats.f.sf(fvalue, q, self.df_resid))
        return fvalue, pvalue


def fit_model(frame: pd.DataFrame, metric: str):
    model = HC3Model(frame, metric)
    return model, model


def robust_table(robust, metric: str) -> pd.DataFrame:
    names = robust.names
    ci = np.asarray(robust.conf_int(alpha=0.05))
    rows = []
    for i, name in enumerate(names):
        beta = float(robust.params[i])
        lo, hi = map(float, ci[i])
        if METRICS[metric]["transform"] == "log" and name != "Intercept":
            interpreted = 100 * np.expm1(beta)
            ilo, ihi = 100 * np.expm1(lo), 100 * np.expm1(hi)
            effect_scale = "percent change"
        elif METRICS[metric]["transform"] == "log":
            interpreted = math.exp(beta)
            ilo, ihi = math.exp(lo), math.exp(hi)
            effect_scale = "geometric mean at reference cell"
        else:
            interpreted, ilo, ihi = beta, lo, hi
            effect_scale = "req/s difference"
        rows.append(
            {
                "outcome": metric,
                "term": name,
                "coefficient": beta,
                "std_error_HC3": float(robust.bse[i]),
                "df_resid": float(robust.df_resid),
                "ci95_low": lo,
                "ci95_high": hi,
                "t": float(robust.tvalues[i]),
                "p": float(robust.pvalues[i]),
                "interpreted_effect": interpreted,
                "interpreted_ci95_low": ilo,
                "interpreted_ci95_high": ihi,
                "interpreted_scale": effect_scale,
            }
        )
    return pd.DataFrame(rows)


def term_indices(names):
    strategy = [i for i, n in enumerate(names) if n.startswith("Strategy[")]
    concurrency = [i for i, n in enumerate(names) if n.startswith("Concurrency[")]
    interaction = [i for i, n in enumerate(names) if n.startswith("Strategy×Concurrency[")]
    return {"Strategy": strategy, "Concurrency": concurrency, "Strategy × Concurrency": interaction}


def f_test_rows(robust, metric: str) -> pd.DataFrame:
    names = robust.names
    sidx = names.index("Strategy[read-through]")
    c50 = names.index("Concurrency[50]")
    c100 = names.index("Concurrency[100]")
    i50 = names.index("Strategy×Concurrency[50]")
    i100 = names.index("Strategy×Concurrency[100]")
    # Equal-weight marginal main effects, equivalent to Type-III tests under sum coding.
    r_strategy = np.zeros((1, len(names)))
    r_strategy[0, [sidx, i50, i100]] = [1, 1 / 3, 1 / 3]
    r_concurrency = np.zeros((2, len(names)))
    r_concurrency[0, [c50, i50]] = [1, 0.5]
    r_concurrency[1, [c100, i100]] = [1, 0.5]
    r_interaction = np.zeros((2, len(names)))
    r_interaction[0, i50] = 1
    r_interaction[1, i100] = 1
    matrices = {
        "Strategy (equal-weight marginal)": r_strategy,
        "Concurrency (equal-weight marginal)": r_concurrency,
        "Strategy × Concurrency": r_interaction,
    }
    rows = []
    for term, R in matrices.items():
        fvalue, pvalue = robust.f_test(R)
        rows.append(
            {
                "outcome": metric,
                "term": term,
                "df_num": int(R.shape[0]),
                "df_den": float(robust.df_resid),
                "F_HC3": fvalue,
                "p_HC3": pvalue,
            }
        )
    return pd.DataFrame(rows)


def contrast(robust, vector: np.ndarray):
    estimate = float(vector @ robust.params)
    se = float(np.sqrt(vector @ robust.cov @ vector))
    tval = estimate / se
    p = float(2 * stats.t.sf(abs(tval), robust.df_resid))
    crit = stats.t.ppf(0.975, robust.df_resid)
    return estimate, se, estimate - crit * se, estimate + crit * se, tval, p


def strategy_contrasts(robust, metric: str) -> pd.DataFrame:
    names = robust.names
    sidx = names.index("Strategy[read-through]")
    interaction = {n: i for i, n in enumerate(names) if n.startswith("Strategy×Concurrency[")}
    rows = []
    for conc in CONCURRENCIES:
        v = np.zeros(len(names))
        v[sidx] = 1
        if conc != 25:
            idx = [i for n, i in interaction.items() if f"[{conc}]" in n][0]
            v[idx] = 1
        est, se, lo, hi, tval, p = contrast(robust, v)
        if METRICS[metric]["transform"] == "log":
            effect, elo, ehi = 100 * np.expm1(est), 100 * np.expm1(lo), 100 * np.expm1(hi)
            scale = "read-through vs cache-aside (%)"
        else:
            effect, elo, ehi = est, lo, hi
            scale = "read-through minus cache-aside (req/s)"
        rows.append(
            {
                "outcome": metric,
                "contrast": f"read-through - cache-aside at concurrency {conc}",
                "estimate_model_scale": est,
                "std_error_HC3": se,
                "ci95_low_model_scale": lo,
                "ci95_high_model_scale": hi,
                "t": tval,
                "p": p,
                "interpreted_effect": effect,
                "interpreted_ci95_low": elo,
                "interpreted_ci95_high": ehi,
                "interpreted_scale": scale,
            }
        )
    v = np.zeros(len(names))
    v[sidx] = 1
    for idx in interaction.values():
        v[idx] = 1 / 3
    est, se, lo, hi, tval, p = contrast(robust, v)
    if METRICS[metric]["transform"] == "log":
        effect, elo, ehi = 100 * np.expm1(est), 100 * np.expm1(lo), 100 * np.expm1(hi)
        scale = "equal-weight marginal read-through vs cache-aside (%)"
    else:
        effect, elo, ehi = est, lo, hi
        scale = "equal-weight marginal read-through minus cache-aside (req/s)"
    rows.append(
        {
            "outcome": metric,
            "contrast": "equal-weight marginal strategy effect",
            "estimate_model_scale": est,
            "std_error_HC3": se,
            "ci95_low_model_scale": lo,
            "ci95_high_model_scale": hi,
            "t": tval,
            "p": p,
            "interpreted_effect": effect,
            "interpreted_ci95_low": elo,
            "interpreted_ci95_high": ehi,
            "interpreted_scale": scale,
        }
    )
    return pd.DataFrame(rows)


def anova_ss(values: np.ndarray, strategy: np.ndarray, concurrency: np.ndarray):
    grand = values.mean()
    means_a = {a: values[strategy == a].mean() for a in STRATEGIES}
    means_b = {b: values[concurrency == b].mean() for b in CONCURRENCIES}
    means_ab = {(a, b): values[(strategy == a) & (concurrency == b)].mean() for a in STRATEGIES for b in CONCURRENCIES}
    n = 5
    ss_a = len(CONCURRENCIES) * n * sum((means_a[a] - grand) ** 2 for a in STRATEGIES)
    ss_b = len(STRATEGIES) * n * sum((means_b[b] - grand) ** 2 for b in CONCURRENCIES)
    ss_ab = n * sum(
        (means_ab[(a, b)] - means_a[a] - means_b[b] + grand) ** 2
        for a in STRATEGIES for b in CONCURRENCIES
    )
    ss_e = sum(
        ((values[(strategy == a) & (concurrency == b)] - means_ab[(a, b)]) ** 2).sum()
        for a in STRATEGIES for b in CONCURRENCIES
    )
    return {"Strategy": ss_a, "Concurrency": ss_b, "Strategy × Concurrency": ss_ab}, ss_e


def partial_eta_bootstrap(frame: pd.DataFrame, metric: str):
    values = np.log(frame[metric].to_numpy()) if METRICS[metric]["transform"] == "log" else frame[metric].to_numpy()
    strategy = frame["strategy"].to_numpy()
    concurrency = frame["concurrency"].to_numpy()
    ss, sse = anova_ss(values, strategy, concurrency)
    estimates = {term: val / (val + sse) for term, val in ss.items()}
    boots = {term: [] for term in ss}
    cell_indices = [np.flatnonzero((strategy == a) & (concurrency == b)) for a in STRATEGIES for b in CONCURRENCIES]
    for _ in range(BOOT):
        sampled = np.concatenate([RNG.choice(idx, size=len(idx), replace=True) for idx in cell_indices])
        bs, be = anova_ss(values[sampled], strategy[sampled], concurrency[sampled])
        for term, val in bs.items():
            denom = val + be
            boots[term].append(val / denom if denom > 0 else np.nan)
    rows = []
    for term in ss:
        arr = np.asarray(boots[term], dtype=float)
        rows.append(
            {
                "outcome": metric,
                "term": term,
                "partial_eta_squared": estimates[term],
                "bootstrap_ci95_low": np.nanpercentile(arr, 2.5),
                "bootstrap_ci95_high": np.nanpercentile(arr, 97.5),
                "bootstrap_reps": BOOT,
            }
        )
    return pd.DataFrame(rows)


def cohens_d(x, y):
    nx, ny = len(x), len(y)
    pooled = math.sqrt(((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1)) / (nx + ny - 2))
    return (np.mean(y) - np.mean(x)) / pooled if pooled > 0 else np.nan


def d_bootstrap(frame: pd.DataFrame, metric: str):
    rows = []
    for conc in CONCURRENCIES:
        ca = frame[(frame.strategy == "cache-aside") & (frame.concurrency == conc)][metric].to_numpy()
        rt = frame[(frame.strategy == "read-through") & (frame.concurrency == conc)][metric].to_numpy()
        estimate = cohens_d(ca, rt)
        boot = []
        for _ in range(BOOT):
            d = cohens_d(RNG.choice(ca, len(ca), replace=True), RNG.choice(rt, len(rt), replace=True))
            if np.isfinite(d):
                boot.append(d)
        rows.append(
            {
                "outcome": metric,
                "concurrency": conc,
                "cohens_d_readthrough_minus_cacheaside": estimate,
                "bootstrap_ci95_low": np.percentile(boot, 2.5),
                "bootstrap_ci95_high": np.percentile(boot, 97.5),
                "valid_bootstrap_reps": len(boot),
            }
        )
    return pd.DataFrame(rows)


def diagnostics(frame, metric, ols):
    groups_raw = [
        g[metric].to_numpy()
        for _, g in frame.groupby(["strategy", "concurrency"], sort=True)
    ]
    modeled = frame.copy()
    modeled["modeled"] = np.log(modeled[metric]) if METRICS[metric]["transform"] == "log" else modeled[metric]
    groups_model = [g["modeled"].to_numpy() for _, g in modeled.groupby(["strategy", "concurrency"], sort=True)]
    lev_raw = stats.levene(*groups_raw, center="median")
    lev_model = stats.levene(*groups_model, center="median")
    shap = stats.shapiro(ols.resid)
    return pd.DataFrame(
        [
            {"outcome": metric, "test": "Levene (raw scale, 6 cells, median centered)", "statistic": lev_raw.statistic, "df1": 5, "df2": 24, "p": lev_raw.pvalue},
            {"outcome": metric, "test": "Levene (modeled scale, 6 cells, median centered)", "statistic": lev_model.statistic, "df1": 5, "df2": 24, "p": lev_model.pvalue},
            {"outcome": metric, "test": "Shapiro-Wilk (model residuals)", "statistic": shap.statistic, "df1": np.nan, "df2": np.nan, "p": shap.pvalue},
        ]
    )


def order_effect(frame, metric):
    raw_rho, raw_p = stats.spearmanr(frame["order_in_block"], frame[metric])
    rob = HC3Model(frame, metric, include_order=True)
    idx = rob.names.index("order_in_block")
    ci = rob.conf_int()[idx]
    beta, lo, hi = rob.params[idx], ci[0], ci[1]
    if METRICS[metric]["transform"] == "log":
        eff, elo, ehi, scale = 100 * np.expm1(beta), 100 * np.expm1(lo), 100 * np.expm1(hi), "% per one position later"
    else:
        eff, elo, ehi, scale = beta, lo, hi, "req/s per one position later"
    return {
        "outcome": metric,
        "raw_spearman_rho": raw_rho,
        "raw_spearman_p": raw_p,
        "adjusted_order_coefficient_model_scale": beta,
        "std_error_HC3": rob.bse[idx],
        "adjusted_ci95_low_model_scale": lo,
        "adjusted_ci95_high_model_scale": hi,
        "adjusted_t": rob.tvalues[idx],
        "adjusted_p": rob.pvalues[idx],
        "interpreted_effect": eff,
        "interpreted_ci95_low": elo,
        "interpreted_ci95_high": ehi,
        "interpreted_scale": scale,
    }


def loo(frame: pd.DataFrame, metric: str, full_robust) -> pd.DataFrame:
    names = full_robust.names
    sidx = names.index("Strategy[read-through]")
    iidx = [i for i, n in enumerate(names) if n.startswith("Strategy×Concurrency[")]

    def vectors(model_names):
        si = model_names.index("Strategy[read-through]")
        ints = {n: i for i, n in enumerate(model_names) if n.startswith("Strategy×Concurrency[")}
        out = {}
        vm = np.zeros(len(model_names)); vm[si] = 1
        for idx in ints.values(): vm[idx] = 1 / 3
        out["marginal strategy"] = vm
        for conc in CONCURRENCIES:
            v = np.zeros(len(model_names)); v[si] = 1
            if conc != 25:
                idx = [i for n, i in ints.items() if f"[{conc}]" in n][0]
                v[idx] = 1
            out[f"strategy at c{conc}"] = v
        return out

    full_vectors = vectors(names)
    full_results = {label: contrast(full_robust, v) for label, v in full_vectors.items()}
    R_full = np.zeros((len(iidx), len(names)))
    for j, idx in enumerate(iidx): R_full[j, idx] = 1
    _, full_inter_p = full_robust.f_test(R_full)

    records = []
    for drop_idx in frame.index:
        _, rob = fit_model(frame.drop(index=drop_idx), metric)
        for label, v in vectors(rob.names).items():
            est, _, _, _, _, p = contrast(rob, v)
            records.append({"component": label, "estimate": est, "p": p})
        ri = [i for i, n in enumerate(rob.names) if "×" in n]
        R = np.zeros((len(ri), len(rob.names)))
        for j, idx in enumerate(ri): R[j, idx] = 1
        _, p = rob.f_test(R)
        records.append({"component": "omnibus interaction", "estimate": np.nan, "p": p})
    rec = pd.DataFrame(records)
    rows = []
    for component, g in rec.groupby("component", sort=False):
        if component == "omnibus interaction":
            full_p = full_inter_p
            rows.append(
                {
                    "outcome": metric,
                    "component": component,
                    "full_estimate_model_scale": np.nan,
                    "loo_min_estimate": np.nan,
                    "loo_max_estimate": np.nan,
                    "sign_reversals": np.nan,
                    "full_p": full_p,
                    "loo_min_p": g.p.min(),
                    "loo_max_p": g.p.max(),
                    "significant_loo_models_of_30": int((g.p < 0.05).sum()),
                    "significance_flips": int(((g.p < 0.05) != (full_p < 0.05)).sum()),
                }
            )
        else:
            full_est, _, _, _, _, full_p = full_results[component]
            rows.append(
                {
                    "outcome": metric,
                    "component": component,
                    "full_estimate_model_scale": full_est,
                    "loo_min_estimate": g.estimate.min(),
                    "loo_max_estimate": g.estimate.max(),
                    "sign_reversals": int((np.sign(g.estimate) != np.sign(full_est)).sum()),
                    "full_p": full_p,
                    "loo_min_p": g.p.min(),
                    "loo_max_p": g.p.max(),
                    "significant_loo_models_of_30": int((g.p < 0.05).sum()),
                    "significance_flips": int(((g.p < 0.05) != (full_p < 0.05)).sum()),
                }
            )
    return pd.DataFrame(rows)


def make_plots(frame, models):
    sns.set_theme(style="whitegrid", context="talk")
    palette = {"cache-aside": "#2F6BFF", "read-through": "#E45756"}
    fig, axes = plt.subplots(1, 3, figsize=(19, 5.8))
    for ax, metric in zip(axes, METRICS):
        # deterministic horizontal offsets show all five run-level observations.
        offsets = {"cache-aside": -1.5, "read-through": 1.5}
        for strategy in STRATEGIES:
            sub = frame[frame.strategy == strategy]
            x = sub.concurrency.to_numpy(dtype=float) + offsets[strategy]
            ax.scatter(x, sub[metric], s=38, alpha=0.55, color=palette[strategy], label=None)
            grouped = sub.groupby("concurrency")[metric]
            means = grouped.mean().reindex(CONCURRENCIES)
            sems = grouped.sem().reindex(CONCURRENCIES)
            ci = stats.t.ppf(0.975, 4) * sems
            ax.errorbar(
                np.asarray(CONCURRENCIES, dtype=float) + offsets[strategy], means, yerr=ci,
                marker="o", linewidth=2.2, capsize=5, color=palette[strategy], label=strategy,
            )
        ax.set_title(metric)
        ax.set_xlabel("Concurrency (categorical)")
        ax.set_xticks(CONCURRENCIES)
        ax.set_ylabel(f"{metric} ({METRICS[metric]['unit']})")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle("Run-level observations and group means with 95% t confidence intervals", y=0.995)
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.945), ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(OUT / "group_results.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(3, 2, figsize=(13, 15))
    for row, metric in enumerate(METRICS):
        ols = models[metric][0]
        axes[row, 0].scatter(ols.fitted, ols.resid, s=46, alpha=0.8, color="#2F6BFF")
        axes[row, 0].axhline(0, color="black", linewidth=1)
        axes[row, 0].set_title(f"{metric}: residuals vs fitted")
        axes[row, 0].set_xlabel("Fitted value (model scale)")
        axes[row, 0].set_ylabel("Residual")
        stats.probplot(ols.resid, dist="norm", plot=axes[row, 1])
        axes[row, 1].set_title(f"{metric}: normal Q-Q")
    fig.tight_layout()
    fig.savefig(OUT / "model_diagnostics.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def markdown_table(df, columns=None, digits=4):
    show = df if columns is None else df[columns]
    display = show.copy()
    for col in display.columns:
        if pd.api.types.is_float_dtype(display[col]):
            display[col] = display[col].map(lambda x: fmt(x, digits))
    headers = [str(c) for c in display.columns]
    rows = [[str(v) for v in row] for row in display.itertuples(index=False, name=None)]
    widths = [max(len(headers[j]), *(len(row[j]) for row in rows)) for j in range(len(headers))]
    line1 = "| " + " | ".join(headers[j].ljust(widths[j]) for j in range(len(headers))) + " |"
    line2 = "| " + " | ".join("-" * widths[j] for j in range(len(headers))) + " |"
    body = ["| " + " | ".join(row[j].ljust(widths[j]) for j in range(len(headers))) + " |" for row in rows]
    return "\n".join([line1, line2, *body])


def main():
    warnings.filterwarnings("ignore", category=FutureWarning)
    df = pd.read_csv(INPUT)
    assert len(df) == 30
    assert set(df.strategy) == set(STRATEGIES)
    assert set(df.concurrency) == set(CONCURRENCIES)
    assert df.groupby(["strategy", "concurrency"]).size().eq(5).all()
    assert not df[list(METRICS)].isna().any().any()

    desc_rows = []
    tcrit = stats.t.ppf(0.975, 4)
    for (strategy, concurrency), group in df.groupby(["strategy", "concurrency"], sort=True):
        for metric in METRICS:
            mean, sd = group[metric].mean(), group[metric].std(ddof=1)
            margin = tcrit * sd / math.sqrt(len(group))
            desc_rows.append(
                {"strategy": strategy, "concurrency": concurrency, "outcome": metric, "n": len(group), "mean": mean, "sd": sd, "ci95_low": mean - margin, "ci95_high": mean + margin}
            )
    descriptive = pd.DataFrame(desc_rows)

    models = {metric: fit_model(df, metric) for metric in METRICS}
    coefficients = pd.concat([robust_table(models[m][1], m) for m in METRICS], ignore_index=True)
    omnibus = pd.concat([f_test_rows(models[m][1], m) for m in METRICS], ignore_index=True)
    simple = pd.concat([strategy_contrasts(models[m][1], m) for m in METRICS], ignore_index=True)
    tests = pd.concat([diagnostics(df, m, models[m][0]) for m in METRICS], ignore_index=True)
    eta = pd.concat([partial_eta_bootstrap(df, m) for m in METRICS], ignore_index=True)
    d = pd.concat([d_bootstrap(df, m) for m in METRICS], ignore_index=True)
    order = pd.DataFrame([order_effect(df, m) for m in METRICS])
    loo_results = pd.concat([loo(df, m, models[m][1]) for m in METRICS], ignore_index=True)

    outputs = {
        "descriptive_statistics.csv": descriptive,
        "assumption_tests.csv": tests,
        "model_coefficients_HC3.csv": coefficients,
        "omnibus_tests_HC3.csv": omnibus,
        "strategy_contrasts_HC3.csv": simple,
        "effect_sizes_partial_eta2.csv": eta,
        "effect_sizes_cohens_d.csv": d,
        "order_effects.csv": order,
        "leave_one_out.csv": loo_results,
    }
    for name, table in outputs.items():
        table.to_csv(OUT / name, index=False)

    make_plots(df, models)

    report = []
    report.append("# Run-level statistical analysis\n")
    report.append(
        "Statistical unit is one independent run (N=30). Request-level JTL data were not used. "
        "Concurrency is treated as a categorical factor. AvgRT and P95 are modelled on the natural "
        "log scale; Throughput is modelled on its original scale. All model coefficients, contrasts "
        "and omnibus tests use HC3 heteroskedasticity-robust standard errors; 95% CIs are two-sided.\n"
    )
    report.append("## Descriptive statistics\n")
    report.append(markdown_table(descriptive, digits=3) + "\n")
    report.append("## Variance homogeneity and residual normality\n")
    report.append(markdown_table(tests, digits=5) + "\n")
    report.append("## HC3 main model coefficients\n")
    report.append(markdown_table(coefficients[["outcome", "term", "coefficient", "std_error_HC3", "df_resid", "ci95_low", "ci95_high", "t", "p", "interpreted_effect", "interpreted_ci95_low", "interpreted_ci95_high", "interpreted_scale"]], digits=5) + "\n")
    report.append("## HC3 omnibus tests\n")
    report.append(markdown_table(omnibus, digits=5) + "\n")
    report.append("The omnibus interaction test has 2 df; the two individual interaction coefficients each have 1 df.\n")
    report.append("## Strategy simple effects and marginal effects\n")
    report.append(markdown_table(simple, digits=5) + "\n")
    report.append("## Partial eta-squared (model scale; stratified bootstrap 95% CI)\n")
    report.append(markdown_table(eta, digits=5) + "\n")
    report.append("## Cohen's d (read-through minus cache-aside; original scale; stratified bootstrap 95% CI)\n")
    report.append(markdown_table(d, digits=4) + "\n")
    report.append("## order_in_block\n")
    report.append(markdown_table(order, digits=5) + "\n")
    report.append("## Leave-one-out robustness\n")
    report.append(markdown_table(loo_results, digits=6) + "\n")
    report.append(
        "## Figures\n\n"
        "- `group_results.png`: the 30 run-level observations, cell means, and 95% t intervals with df=4.\n"
        "- `model_diagnostics.png`: residual-versus-fitted and Q-Q plots for the three main models.\n"
    )
    report.append(
        "## Method and limitations\n\n"
        "- Each cell contains only 5 runs. The power of the Levene and Shapiro-Wilk tests is limited; "
        "failing to reject an assumption does not establish that it holds.\n"
        "- P95 values are integers because they are aggregated from request-level quantiles, and the two "
        "read-through cells at concurrency 50 and 100 have zero within-cell SD. Their linear-model "
        "inference should be treated as approximate; interpret direction, intervals and the leave-one-out "
        "results rather than point significance.\n"
        "- HC3 handles heteroskedasticity of general form, but N=30 remains small. Effect-size bootstrap "
        "confidence intervals may be wide or unstable when each cell has only n=5.\n"
        "- The data come from a single application instance, a single dataset size and one continuous "
        "experimental session. Conclusions are limited to the current implementation and environment.\n"
        "- The raw correlation of `order_in_block` is confounded with strategy and concurrency; the HC3 "
        "order coefficient that controls the full factorial structure is the appropriate summary.\n"
    )
    (OUT / "statistical_report.md").write_text("\n".join(report), encoding="utf-8")

    print(f"Wrote analysis outputs to {OUT}")
    print(f"Rows: {len(df)}; cells: {df.groupby(['strategy','concurrency']).size().to_dict()}")


if __name__ == "__main__":
    main()
