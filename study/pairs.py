"""Priors for study 1.

These are written BEFORE any measurement. If the metric cannot recover
these, it is wrong, not the priors. A prior is a claim about demand, not
about price correlation: two stocks can move together every day and still
be substitutes (Coke and Pepsi do exactly that).

Labels:
  substitute  people buy one INSTEAD of the other
  complement  good news for one is good news for the other
  control     unrelated, expect a neutral reading
"""

PAIRS = [
    # Substitutes
    {"x": "KO", "y": "PEP", "sector_etf": "XLP",
     "prior": "substitute",
     "why": "Cola. The textbook substitute pair."},
    {"x": "V", "y": "MA", "sector_etf": "XLF",
     "prior": "substitute",
     "why": "Payment networks. A merchant or cardholder picks one rail."},
    {"x": "HD", "y": "LOW", "sector_etf": "XLI",
     "prior": "substitute",
     "why": "Home improvement. Same customer, same trip, one store."},
    # Complements
    {"x": "NVDA", "y": "TSM", "sector_etf": "XLK",
     "prior": "complement",
     "why": "TSM fabricates NVDA chips. NVDA demand is TSM demand."},
    {"x": "AAPL", "y": "TSM", "sector_etf": "XLK",
     "prior": "complement",
     "why": "TSM fabricates AAPL chips. Same supply chain link."},
    # Control
    {"x": "KO", "y": "NVDA", "sector_etf": "XLP",
     "prior": "control",
     "why": "Unrelated businesses. Expect a neutral reading."},
]

MARKET = "SPY"
PERIOD = "2y"
