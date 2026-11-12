# Stocks with strings — v2 as a replication study

Status: sketch only, written 12 Nov 2026. No code, no repo push. Read it when
you want, change it or bin it.

## The question after study 1

Study 1 failed. The shock day metric got Visa vs Mastercard and Home Depot
vs Lowes backwards, both highly significant. The likely cause is a shared
sub sector factor left in the residuals. So the honest next step is not a
bigger version of the same metric. It is to test whether a known result
replicates with the same data I can actually get for free.

## The replication target: Anton and Polk (2014)

Anton and Polk, Journal of Finance 2014, "Connected Stocks". Their claim:
stocks that share active mutual fund owners move together more, even after
controlling for industry, size and style. They built a trading strategy
off it earning over 9 percent a year before costs, in 2014.

Why this one:

- It is the holdings angle from the original plan, so it is an independent
  check on the shock day idea, not a tweak of it.
- It uses 13F filings, which are free from SEC EDGAR. No paid data needed.
- It has a clear pass or fail: does shared ownership predict comovement
  in my sample, yes or no.

## What v2 would actually do

1. Pick the same six pairs from study 1, plus a few more known pairs, and
   state the priors before measuring anything, same as study 1.
2. Pull 13F holdings for the funds holding each stock. For each pair,
   compute a common ownership score: how much of the two stocks is held
   by the same funds, against what chance would predict.
3. Test one thing: does the common ownership score predict the shock day
   sign from study 1, and does it predict plain comovement after stripping
   the market and sector.
4. Cross check with Hoberg and Phillips TNIC text similarity, which is the
   standard product market version of "these two are substitutes". If
   holdings and TNIC agree and the shock day metric disagrees, the shock
   day metric is the problem, not the pairs.
5. Hold out the last year of data and score it untouched. No tuning on
   the holdout.

## What would count as a win

- The common ownership score lines up with the known pairs, and it lines
  up with TNIC. That would mean the holdings angle works, and study 1
  failed because of the factor model, not because the question is bad.
- If it does not line up, the project stops as a study with a clean
  negative result, and part 2 (a profit strategy) stays off the table.

## Limits to keep in mind

- 13F is quarterly and only covers long positions. It is slow and partial.
- Anton and Polk is a decade old and pre costs. Even a clean replication
  does not mean a tradable strategy.
- Koijen and Yogo (2019) built the full demand system version of this
  question, and the live debate is whether their framework assumes away
  the exact substitute vs complement distinction I want to measure. So
  this stays a learning replication, not a new discovery.

## Cost

No build yet. The sketch is the whole deliverable. If you say go, v2 is
a small data pull plus one test, not another big prototype.
