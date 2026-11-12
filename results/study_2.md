# Study 2 results

Replication of Anton and Polk (2014): does 13F common ownership
predict the shock day sign, and does it predict plain comovement?

Price window: 2024-11-13 to 2026-11-11 (500 trading days). Train year ends 2025-11-11, holdout year starts 2025-11-12.

Holdings: Q3 2025 (period end 2025-09-30, filed 1 Oct to 14 Nov 2025) is measured before the holdout year, so it predicts the holdout without lookahead on positions. The positions are as of 30 Sep 2025, before the holdout starts. The filings themselves arrive by 14 Nov, two days into the holdout, but a filing cannot change the positions it reports. Q2 2026 (period end 2026-06-30) is the most recent complete quarter, shown as a robustness check against the full window.

Lift is observed overlap over chance overlap: filers holding both
stocks, divided by what independence would predict from the two
holder counts and the total filer count. 1 is chance. Jaccard is
the share of the combined holder set that holds both.

| pair     | prior      |   lift_q32025 |   jaccard_q32025 |   n_both_q32025 |   n_x_q32025 |   n_y_q32025 |   lift_q22026 |   jaccard_q22026 |   n_both_q22026 |   n_x_q22026 |   n_y_q22026 |   train_shock_corr |   train_p_max | train_reading             |   train_resid_corr |   train_raw_corr |   holdout_shock_corr |   holdout_p_max | holdout_reading           |   holdout_resid_corr |   holdout_raw_corr |   full_shock_corr |   full_p_max | full_reading              |   full_resid_corr |   full_raw_corr | match_holdout   |
|:---------|:-----------|--------------:|-----------------:|----------------:|-------------:|-------------:|--------------:|-----------------:|----------------:|-------------:|-------------:|-------------------:|--------------:|:--------------------------|-------------------:|-----------------:|---------------------:|----------------:|:--------------------------|---------------------:|-------------------:|------------------:|-------------:|:--------------------------|------------------:|----------------:|:----------------|
| KO/PEP   | substitute |         1.786 |            0.558 |            2330 |         3237 |         3272 |         1.301 |            0.355 |            1942 |         3802 |         3618 |              0.224 |         0.995 | neutral (not significant) |              0.155 |            0.614 |               -0.088 |           0.575 | neutral (not significant) |                0.114 |              0.615 |             0.09  |        0.959 | neutral (not significant) |             0.143 |           0.613 | False           |
| V/MA     | substitute |         1.38  |            0.483 |            2524 |         4276 |         3473 |         1.044 |            0.311 |            2019 |         4746 |         3756 |              0.927 |         0     | complement                |              0.735 |            0.91  |                0.804 |           0.01  | complement                |                0.77  |              0.876 |             0.856 |        0     | complement                |             0.76  |           0.892 | False           |
| HD/LOW   | substitute |         1.615 |            0.458 |            2073 |         3992 |         2611 |         1.327 |            0.324 |            1737 |         4280 |         2818 |              0.915 |         0     | complement                |              0.824 |            0.882 |                0.931 |           0     | complement                |                0.882 |              0.901 |             0.938 |        0     | complement                |             0.862 |           0.893 | False           |
| WMT/TGT  | substitute |         1.694 |            0.319 |            1361 |         3983 |         1638 |         1.44  |            0.278 |            1433 |         4596 |         1995 |              0.167 |         0.966 | neutral (not significant) |             -0.067 |            0.254 |               -0.31  |           0.707 | neutral (not significant) |               -0.051 |              0.329 |             0.001 |        0.919 | neutral (not significant) |            -0.039 |           0.282 | False           |
| XOM/CVX  | substitute |         1.473 |            0.556 |            2825 |         4156 |         3747 |         0.954 |            0.278 |            1830 |         4067 |         4344 |              0.355 |         0.842 | neutral (not significant) |              0.124 |            0.849 |               -0.109 |           0.747 | neutral (not significant) |                0.091 |              0.867 |             0.184 |        0.856 | neutral (not significant) |             0.103 |           0.856 | False           |
| NVDA/TSM | complement |         1.1   |            0.329 |            2010 |         5327 |         2786 |         0.752 |            0.231 |            1844 |         6173 |         3662 |              0.324 |         0.295 | neutral (not significant) |              0.186 |            0.771 |                0.197 |           0.955 | neutral (not significant) |                0.201 |              0.664 |             0.501 |        0.013 | complement                |             0.252 |           0.718 | False           |
| AAPL/TSM | complement |         1.052 |            0.316 |            2000 |         5542 |         2786 |         0.724 |            0.224 |            1838 |         6387 |         3662 |             -0.416 |         0.21  | neutral (not significant) |             -0.182 |            0.404 |               -0.264 |           0.892 | neutral (not significant) |               -0.104 |              0.107 |            -0.271 |        0.543 | neutral (not significant) |            -0.134 |           0.271 | False           |
| AMD/TSM  | complement |         1.628 |            0.373 |            1475 |         2640 |         2786 |         0.988 |            0.262 |            1611 |         4104 |         3662 |              0.187 |         0.675 | neutral (not significant) |              0.154 |            0.627 |                0.428 |           0.146 | neutral (not significant) |                0.193 |              0.71  |             0.227 |        0.392 | neutral (not significant) |             0.148 |           0.669 | False           |
| KO/NVDA  | control    |         1.245 |            0.447 |            2645 |         3237 |         5327 |         0.829 |            0.269 |            2112 |         3802 |         6173 |              0.052 |         0.593 | neutral (not significant) |              0.06  |           -0.229 |                0.255 |           0.555 | neutral (not significant) |                0.08  |             -0.301 |             0.013 |        0.711 | neutral (not significant) |             0.048 |          -0.259 | True            |

Holdout shock day score: 1/9 priors recovered.

## Verdict: clean negative, the project stops here

The sketch said the project continues only if holdings and TNIC
agree and the shock day metric disagrees, which would blame the
factor model. That condition cannot be met, for two reasons.
First, the ETNIC check is blocked (see above), and even
unblocked it measures relatedness, not direction, so it could
never have adjudicated substitute vs complement. Second, the
holdings test itself fails: pre holdout lift does not predict
the holdout shock day sign (Pearson r=0.069, p=0.860, Spearman
rho=-0.017, p=0.966), and it does not predict holdout
comovement either (residual correlation r=0.173, p=0.656, raw
correlation r=0.402, p=0.283). The mean lift also runs the
wrong way: substitutes 1.59, complements 1.26, control 1.245.
Direct rivals share more owners than complements do, so common
ownership cannot rescue the sign. It points the wrong way.

The shock day failure is also stable, not a window fluke. The
two wrong sign pairs from study 1 read as complements again in
the untouched holdout year: V/MA +0.804 (p=0.010) and HD/LOW
+0.931 (p=0.000). They already read that way in the train year
too (V/MA +0.927, HD/LOW +0.915, both p=0.000). The factor
model leaves a sub sector factor in the residuals, so shock
days are mostly shared sector news, and no holdings adjustment
tested here fixes it.

Part 2, the profit strategy, stays off the table. The metric
does not recover substitute vs complement, and common ownership
does not explain or fix it.

Sanity check: the full window reproduces study 1 for the six
original pairs within 0.01 (V/MA +0.856 vs +0.858, HD/LOW
+0.938 vs +0.940, KO/PEP +0.090 vs +0.113, NVDA/TSM +0.501 vs
+0.498, AAPL/TSM -0.271 vs -0.287, KO/NVDA +0.013 vs neutral),
so the pipeline is consistent and the holdout result is not a
coding change.

## Cross pair tests (9 pairs)

Pearson r and Spearman rho, with p values. The holdings score is
Q3 2025 lift unless stated.

- lift_q32025_vs_holdout_shock: Pearson r=0.069 (p=0.860), Spearman rho=-0.017 (p=0.966)
- lift_q32025_vs_holdout_resid: Pearson r=0.173 (p=0.656), Spearman rho=0.133 (p=0.732)
- lift_q32025_vs_holdout_raw: Pearson r=0.402 (p=0.283), Spearman rho=0.217 (p=0.576)
- lift_q22026_vs_full_shock: Pearson r=0.245 (p=0.525), Spearman rho=0.250 (p=0.516)
- lift_q22026_vs_full_resid: Pearson r=0.299 (p=0.435), Spearman rho=0.300 (p=0.433)
- lift_q22026_vs_full_raw: Pearson r=0.233 (p=0.547), Spearman rho=0.333 (p=0.381)

## Mean Q3 2025 lift by prior

- complement: 1.26
- control: 1.245
- substitute: 1.59

## ETNIC cross check: blocked (and what it could and could not
have shown)

ETNIC is the preferred version over baseline TNIC: it replaces
exact keyword matching with Doc2Vec embeddings, so it catches
synonyms and semantic context, and it covers every Compustat
firm with a 10-K link, not just CRSP firms. The ETNIC-3 file
is freely downloadable from the Hoberg-Phillips data library
and was downloaded for this study (data-tnic/etnic3_data.zip,
221 MB, coverage 1989 to 2023, ETNIC3_data.txt). Its columns,
checked directly in the file, are year, gvkey1, gvkey2, score.
Firms are keyed by Compustat GVKEY only. There is no ticker,
CIK or CUSIP column, and no free ticker to GVKEY crosswalk
exists: the link table lives in WRDS/Compustat, which is
licensed, and the public crosswalks I found are either
licensed data or need a platform login. The GVKEYs were not
guessed. So there are no ETNIC numbers in this study, and no
baseline TNIC numbers either. The holdings test below stands
on its own.

Even if the join had worked, ETNIC could not have settled the
substitute vs complement question. Baseline TNIC and ETNIC
measure product market relatedness, not direction: a high
similarity score picks up direct rivals and complementary
ecosystem partners alike, because cosine similarity has no
directional context. A chipmaker and an operating system
developer share words like mobile and wireless and score high,
even though they are complements, not rivals. So ETNIC would
have been the are they related at all axis only. The direction
has to come from the holdings score and the shock day sign.
That is why the verdict below rests on those two, not on
ETNIC. No LLM was used to classify the pairs either: an LLM
trained on later outcomes would leak the answer into a
historical test. Vertical TNIC, which adds supply chain
direction from BEA input output tables, is a possible future
step and is out of scope for this study.

## Limits

- 13F is quarterly and long only, and only managers over $100M
  file. Shorts, small funds and non US holders are invisible.
- Counts are filings, not filers: about 3% of hits are amendments,
  so a filer who amended is counted twice, in the numerator and
  the denominator alike.
- N includes notice filers who hold nothing, which pulls every
  lift down by the same small amount. Rankings are unaffected.
- Nine pairs is a small cross section. A correlation across nine
  points is weak evidence either way, and the per pair readings
  are the main result.
- The holdout shock day test uses about 13 shock days per pair,
  so the per pair p values are noisy.
- The ETNIC relatedness check is missing (blocked, see above),
  so there is no independent text based confirmation that the
  pairs are product market related at all.
