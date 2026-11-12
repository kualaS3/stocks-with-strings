# Study 1 results

Window: 2024-11-12 to 2026-11-11 (501 trading days).

Shock days are the top 5% of absolute residual days for the shocked
stock. Residuals come from regressing each stock on SPY plus its own
sector ETF. P values come from a 5000 draw permutation test.

| pair     | prior      | reading                   | match   |   shock_corr_avg |   shock_corr_xy |   shock_corr_yx |   p_xy |   p_yx |   resid_corr_full |   raw_corr |   n_shocks |
|:---------|:-----------|:--------------------------|:--------|-----------------:|----------------:|----------------:|-------:|-------:|------------------:|-----------:|-----------:|
| KO/PEP   | substitute | neutral (not significant) | False   |            0.113 |           0.026 |           0.2   |  0.899 |  0.328 |             0.143 |      0.613 |         26 |
| V/MA     | substitute | complement                | False   |            0.858 |           0.902 |           0.813 |  0     |  0     |             0.76  |      0.892 |         26 |
| HD/LOW   | substitute | complement                | False   |            0.94  |           0.955 |           0.925 |  0     |  0     |             0.862 |      0.894 |         26 |
| NVDA/TSM | complement | complement                | True    |            0.498 |           0.495 |           0.501 |  0.01  |  0.008 |             0.25  |      0.716 |         26 |
| AAPL/TSM | complement | neutral (not significant) | False   |           -0.287 |          -0.137 |          -0.437 |  0.511 |  0.025 |            -0.134 |      0.271 |         26 |
| KO/NVDA  | control    | neutral (not significant) | True    |            0.009 |           0.099 |          -0.08  |  0.651 |  0.696 |             0.046 |     -0.259 |         26 |

Score: 2/6 priors recovered.

Reading the contrasts: raw_corr is what a naive correlation says.
resid_corr_full is the portfolio side definition. shock_corr_avg is
the demand side metric this study is testing.

## Interpretation

Score 2/6. The metric fails, and it fails in a systematic way: both
substitute pairs with a shared sub sector read as strong complements
(V/MA +0.86, HD/LOW +0.94, p < 0.001 in both directions). That is not
noise. The residuals still contain a sub sector factor that the broad
sector ETF does not remove, so most shock days are sector news hitting
both stocks together.

The earnings day diagnostic (results/earnings_diagnostic.csv) cannot
confirm or refute this yet. With 2 years of data each stock has 8
earnings days, and even the control pair KO/NVDA reads +0.4 there.
The test needs a longer window before it has power.

Next: study 1 v2 with a 5 to 10 year window, a peer basket factor, and
the 13F holdings angle as an independent check.
