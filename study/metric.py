"""The substitute vs complement metric.

The idea: raw correlation cannot answer this question, because two stocks
in the same sector move together for reasons that have nothing to do with
substitution. So the metric works in two steps.

Step 1, strip the common factors. Each stock return is regressed on the
market (SPY) and its sector ETF. What is left, the residual, is the part
that belongs to that stock alone.

Step 2, watch shock days. Take the days when stock X had an unusually big
residual move, a shock that belongs to X. Then look at what stock Y did on
those same days:
  Y moved the opposite way   money rotated from Y to X, or the reverse.
                              That is substitution.
  Y moved the same way       good news for X was good news for Y.
                              That is complementarity.

The headline number is the correlation between the two residuals on X shock
days. Negative reads substitute, positive reads complement. Both directions
are measured (X shocks and Y shocks) and averaged, because the relation
should be symmetric if it is real.

Significance comes from a permutation test, not from a t table. Shuffle Y
residuals, recompute the same number, and count how often the shuffled
version is at least as extreme. If it happens often, the reading is noise.

The full sample residual correlation is also reported, as the portfolio
side definition. When the two definitions disagree, that disagreement is
itself a finding: it means the pair looks like a complement to a portfolio
and a substitute to a customer, or the reverse.
"""

import numpy as np


def stock_residuals(returns, market, sector_map):
    """Residuals where each stock is regressed on the market plus ITS sector.

    A pair spans two sectors, so one shared factor set would be wrong. Each
    stock gets SPY plus its own sector ETF. Returns a frame of residuals.
    """
    import pandas as pd

    out = {}
    for col in returns.columns:
        factors = pd.DataFrame({"mkt": market, "sec": sector_map[col]})
        frame = pd.concat([returns[col], factors], axis=1, join="inner").dropna()
        x = np.column_stack([np.ones(len(frame)), frame["mkt"].values,
                             frame["sec"].values])
        y = frame[col].values
        beta, *_ = np.linalg.lstsq(x, y, rcond=None)
        out[col] = pd.Series(y - x @ beta, index=frame.index)
    return pd.DataFrame(out)


def residuals(returns, factors):
    """OLS residuals of each return series on the factor returns.

    Returns a frame with the same columns, aligned to the intersection of
    dates where every series is present.
    """
    frame = returns.join(factors, how="inner").dropna()
    out = {}
    x = np.column_stack([np.ones(len(frame))] + [frame[c].values for c in factors.columns])
    for col in returns.columns:
        y = frame[col].values
        beta, *_ = np.linalg.lstsq(x, y, rcond=None)
        out[col] = y - x @ beta
    import pandas as pd

    return pd.DataFrame(out, index=frame.index)


def shock_days(resid, top_pct=0.05):
    """Boolean mask of the days with the largest absolute residuals."""
    cutoff = np.quantile(np.abs(resid), 1 - top_pct)
    return np.abs(resid) >= cutoff


def shock_response(resid_x, resid_y, top_pct=0.05):
    """What Y did on X shock days.

    Returns the shock day correlation, the mean Y residual on X up shock
    days, the mean Y residual on X down shock days, and the shock day count.
    """
    mask = shock_days(resid_x, top_pct)
    n = int(mask.sum())
    if n < 10:
        return {"corr": float("nan"), "up": float("nan"),
                "down": float("nan"), "n": n}
    xs = resid_x[mask]
    ys = resid_y[mask]
    corr = float(np.corrcoef(xs, ys)[0, 1])
    up = float(ys[xs > 0].mean()) if (xs > 0).any() else float("nan")
    down = float(ys[xs < 0].mean()) if (xs < 0).any() else float("nan")
    return {"corr": corr, "up": up, "down": down, "n": n}


def permutation_p(resid_x, resid_y, top_pct=0.05, n_perm=5000, seed=0):
    """Two sided permutation p value for the shock day correlation."""
    rng = np.random.default_rng(seed)
    observed = shock_response(resid_x, resid_y, top_pct)["corr"]
    if not np.isfinite(observed):
        return float("nan"), observed
    mask = shock_days(resid_x, top_pct)
    xs = resid_x[mask].values
    shuffled = rng.permuted(np.tile(resid_y.values, (n_perm, 1)), axis=1)
    ys_shuffled = shuffled[:, mask.values]
    corrs = np.array([np.corrcoef(xs, row)[0, 1] for row in ys_shuffled])
    p = float((np.abs(corrs) >= abs(observed)).mean())
    return p, observed


def pair_metric(resid_x, resid_y, top_pct=0.05, n_perm=5000, seed=0):
    """Full metric for one pair, both directions plus the contrasts."""
    fwd = shock_response(resid_x, resid_y, top_pct)
    bwd = shock_response(resid_y, resid_x, top_pct)
    corr = float(np.corrcoef(resid_x, resid_y)[0, 1])
    p_fwd, _ = permutation_p(resid_x, resid_y, top_pct, n_perm, seed)
    p_bwd, _ = permutation_p(resid_y, resid_x, top_pct, n_perm, seed + 1)
    avg_corr = float(np.nanmean([fwd["corr"], bwd["corr"]]))
    return {
        "shock_corr_xy": fwd["corr"],
        "shock_corr_yx": bwd["corr"],
        "shock_corr_avg": avg_corr,
        "p_xy": p_fwd,
        "p_yx": p_bwd,
        "n_shocks_xy": fwd["n"],
        "n_shocks_yx": bwd["n"],
        "y_on_x_up": fwd["up"],
        "y_on_x_down": fwd["down"],
        "x_on_y_up": bwd["up"],
        "x_on_y_down": bwd["down"],
        "resid_corr_full": corr,
    }


def read_metric(avg_corr, p_xy, p_yx):
    """Plain language reading of one pair result."""
    p = max(p_xy, p_yx)
    if not np.isfinite(avg_corr):
        return "unreadable"
    if p > 0.10:
        return "neutral (not significant)"
    if avg_corr < -0.15:
        return "substitute"
    if avg_corr > 0.15:
        return "complement"
    return "neutral (weak)"
