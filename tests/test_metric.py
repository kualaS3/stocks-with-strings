"""Tests for the metric, on synthetic data where the answer is known."""

import numpy as np
import pandas as pd

from study.metric import pair_metric, read_metric


def _series(kind, n=500, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    if kind == "substitute":
        y = -0.8 * x + rng.normal(0, 0.6, n)
    elif kind == "complement":
        y = 0.8 * x + rng.normal(0, 0.6, n)
    else:
        y = rng.normal(0, 1, n)
    idx = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.Series(x, index=idx), pd.Series(y, index=idx)


def test_substitute_reads_negative():
    x, y = _series("substitute")
    m = pair_metric(x, y, n_perm=500)
    assert m["shock_corr_avg"] < -0.3, m
    assert read_metric(m["shock_corr_avg"], m["p_xy"], m["p_yx"]) == "substitute"


def test_complement_reads_positive():
    x, y = _series("complement")
    m = pair_metric(x, y, n_perm=500)
    assert m["shock_corr_avg"] > 0.3, m
    assert read_metric(m["shock_corr_avg"], m["p_xy"], m["p_yx"]) == "complement"


def test_noise_reads_neutral():
    x, y = _series("noise")
    m = pair_metric(x, y, n_perm=500)
    assert read_metric(m["shock_corr_avg"], m["p_xy"], m["p_yx"]).startswith("neutral"), m
