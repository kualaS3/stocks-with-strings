# Stocks with strings

## Where this came from

Back around Covid I watched Bitcoin crash and Nvidia fall with it, right down to levels where I wanted to buy. That stuck with me. Crypto miners buy GPUs, so when crypto booms or busts, chip demand moves with it. I read crypto and chipmakers like Nvidia and AMD as complements, and with AI on the horizon Nvidia looked like an attractive bet.

That was the spark for the question behind this repo. It is not proof of anything, crypto is not even a stock. It just made me want to know if you can tell substitutes from complements using market data.

I want to know if two stocks are substitutes or complements, and whether
you can actually tell that from market data instead of just guessing from
what the companies do.

Substitutes means people buy one instead of the other. Coke vs Pepsi.
Complements means good news for one is good news for the other. Nvidia
vs TSMC, because TSMC makes Nvidia chips.

This repo has two parts. Part 1 is the study: build a metric and test
whether it recovers pairs I already know the answer for. Part 2 is a
profit driven strategy, and it only happens if part 1 works. There is no
point building a strategy on a metric that cannot tell Coke from Pepsi.

## Study 1 verdict: the first metric failed

The metric ranks each stock against the market and its sector ETF, then
looks at what the other stock does on the first stock's big shock days.
Negative co movement reads substitute, positive reads complement.

It recovered 2 of 6 priors. Worse, it got the substitute pairs backwards:
Visa vs Mastercard reads +0.86 and Home Depot vs Lowes reads +0.94,
both highly significant, both the wrong sign. Nvidia vs TSMC read
correct as a complement, and the unrelated control pair read neutral.

The likely reason is the factor model is too coarse. XLF is banks and
insurance, not payments. XLI is broad industrials, not home retail. So
the residuals still hold a shared sub sector factor, and most shock days
are sector news hitting both stocks, not firm specific news. The metric
is measuring that shared factor, not substitution.

I checked earnings days as the cleaner shock, since an earnings surprise
belongs to one firm alone. With two years of data that is only 8 days
per stock, and even the unrelated control pair reads +0.4 there. Too
noisy to confirm or refute anything.

## Study 2 verdict: the holdings rescue did not work

Study 1 told me my shock day metric reads two famous rival pairs as
complements, which is backwards. In study 2 I asked whether fund
holdings could explain that away. The idea, from Anton and Polk (2014),
is that stocks owned by the same funds move together, so maybe the wrong
sign was really a holdings effect, not a product market effect.

I pulled every 13F filing for two quarters from SEC EDGAR and scored
each pair by how much more its two stocks share owners than chance
would predict. I scored the price side on a full year I had held out
untouched, so nothing was tuned to fit it.

It did not work. The holdings score has basically no link to the holdout
shock day sign (correlation 0.07, p 0.86), and no real link to plain
comovement either. The holdout score is 1 out of 9, and the only hit is
the control pair that was supposed to be neutral. Worse, the two wrong
sign pairs from study 1 show up wrong again in the holdout year, with
strong significance (Visa and Mastercard +0.80, p 0.01, and Home Depot
and Lowes +0.93, p below 0.001). So the failure is stable, not a fluke
of one window.

One more surprise: direct rivals share more owners than complements do
(average lift 1.59 for substitutes, 1.26 for complements). Funds that
hold one big soda or card stock tend to hold the rival too. So common
ownership points the wrong way for rescuing the sign.

I also tried to cross check with ETNIC, the text similarity data from
Hoberg and Phillips, which is the upgraded version of their TNIC
measure. The file is free and I downloaded it, but it keys firms by a
Compustat code I cannot map to tickers without a licensed database, so
that check is blocked. And even if it had worked, it could only have
told me whether two firms are related at all, not whether they are
rivals or partners, because a similarity score has no direction in it.

So this is a clean negative. My shock day metric does not recover
substitute versus complement, and fund holdings do not explain or fix
it. I am stopping here. There is no part 2 profit strategy built on
this metric.

## What study 1 version 2 needs

- A longer window, 5 to 10 years, so the earnings day test has enough
  days to mean something.
- A finer factor than the broad sector ETF, for example a basket of the
  closest peers, or a sub sector ETF where one exists.
- The holdings angle as an independent check: 13F filings show whether
  funds hold the pair together or pick one instead of the other.

## How to run it

```bash
pip install -r requirements.txt
python -m study.run_study
python -m study.earnings_diagnostic
python -m study.run_study_2
python -m pytest tests/ -q
```

Results land in `results/`. Priors live in `study/pairs.py` and are
written before any measurement. If the metric cannot recover them, the
metric is wrong, not the priors.
