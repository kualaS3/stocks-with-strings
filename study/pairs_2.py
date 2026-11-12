"""Priors for study 2.

Written BEFORE any holdings numbers are pulled. The six study 1 pairs
carry their priors over unchanged. The three new pairs get their priors
stated here, before measurement, the same way study 1 did.

A prior is a claim about demand, not about price correlation: two stocks
can move together every day and still be substitutes (Coke and Pepsi do
exactly that).

Labels:
  substitute  people buy one INSTEAD of the other
  complement  good news for one is good news for the other
  control     unrelated, expect a neutral reading
"""

PAIRS = [
    # Substitutes (study 1)
    {"x": "KO", "y": "PEP", "sector_etf": "XLP",
     "prior": "substitute",
     "why": "Cola. The textbook substitute pair."},
    {"x": "V", "y": "MA", "sector_etf": "XLF",
     "prior": "substitute",
     "why": "Payment networks. A merchant or cardholder picks one rail."},
    {"x": "HD", "y": "LOW", "sector_etf": "XLI",
     "prior": "substitute",
     "why": "Home improvement. Same customer, same trip, one store."},
    # Substitutes (new)
    {"x": "WMT", "y": "TGT", "sector_etf": "XLP",
     "prior": "substitute",
     "why": "Big box retail. Same weekly shop, one store or the other."},
    {"x": "XOM", "y": "CVX", "sector_etf": "XLE",
     "prior": "substitute",
     "why": "Oil majors. Same barrel, same pump, one producer or the other."},
    # Complements (study 1)
    {"x": "NVDA", "y": "TSM", "sector_etf": "XLK",
     "prior": "complement",
     "why": "TSM fabricates NVDA chips. NVDA demand is TSM demand."},
    {"x": "AAPL", "y": "TSM", "sector_etf": "XLK",
     "prior": "complement",
     "why": "TSM fabricates AAPL chips. Same supply chain link."},
    # Complements (new)
    {"x": "AMD", "y": "TSM", "sector_etf": "XLK",
     "prior": "complement",
     "why": "TSM fabricates AMD chips. Same supply chain link as NVDA."},
    # Control (study 1)
    {"x": "KO", "y": "NVDA", "sector_etf": "XLP",
     "prior": "control",
     "why": "Unrelated businesses. Expect a neutral reading."},
]

# CUSIP of the common stock for each ticker. These are the identifiers
# the SEC full text search looks for inside 13F information tables.
CUSIP = {
    "KO": "191216100", "PEP": "713448108",
    "V": "92826C839", "MA": "57636Q104",
    "HD": "437076102", "LOW": "548661107",
    "WMT": "931142103", "TGT": "87612E106",
    "XOM": "30231G102", "CVX": "166764100",
    "NVDA": "67066G104", "TSM": "874039100",
    "AAPL": "037833100", "AMD": "007903107",
}

# Sector ETF per stock, for the residual step of the price test.
SECTOR = {
    "KO": "XLP", "PEP": "XLP", "WMT": "XLP", "TGT": "XLP",
    "V": "XLF", "MA": "XLF",
    "HD": "XLI", "LOW": "XLI",
    "XOM": "XLE", "CVX": "XLE",
    "NVDA": "XLK", "TSM": "XLK", "AAPL": "XLK", "AMD": "XLK",
}

MARKET = "SPY"

# 13F quarters. The filing window is when managers file for that quarter
# end, 45 days after the quarter closes. Q3 2025 holdings are dated
# 30 Sep 2025, before the holdout year starts, so they can predict it
# without lookahead on positions. The filings themselves land by 14 Nov
# 2025, which is a data availability lag, not a position lookahead.
QUARTERS = {
    "Q3-2025": {"period_end": "2025-09-30",
                "file_start": "2025-10-01", "file_end": "2025-11-14"},
    "Q2-2026": {"period_end": "2026-06-30",
                "file_start": "2026-07-01", "file_end": "2026-08-14"},
}

# Price windows. The cached prices run 2024-11-11 to 2026-11-11, so the
# first year is the training window and the last year is the holdout.
TRAIN_END = "2025-11-11"
HOLDOUT_START = "2025-11-12"
