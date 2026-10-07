# CAA — Classical Asset Allocation (Momentum and Markowitz: a Golden Combination)

| | |
|---|---|
| **Source** | Keller, W.J., Butler, A. & Kipnis, I. (2015), *Momentum and Markowitz: a Golden Combination*, SSRN **2606884** — v0.99d, 4 June 2015 (initial version 16 May 2015) |
| **Paper** | [SSRN 2606884](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2606884) (34 pp.) — not redistributed here; download it from SSRN |
| **Implementation** | none — removed from the registry on 2026-07-28 (see [`../KNOWN_GAPS.md`](../KNOWN_GAPS.md) §6) |
| **Family / successor** | Strategy named **CAA — Classical Asset Allocation**, solved with the **CLA** (Critical Line Algorithm; Kipnis's R code, appendix B). Continues FAA ([`faa.md`](faa.md)), MAA ([`maa.md`](maa.md)) and Keller 2014a ([`mpt.md`](mpt.md)); 1/3/6/12 lookback taken from EAA ([`eaa.md`](eaa.md)) (pp. 10, 12). Successor: not specified. |

> Written from the PAPER, not from the code. Page numbers refer to the SSRN PDF. A paraphrase,
> detailed enough to reimplement without the PDF. The paper is also cited as "MMGC".

## Rules, as published

**Universe** (TR indices, no tickers; pp. 9-10, 13, 15, 17). Uncapped "cash" = **3m T-Bills** and
**US Gov 10y**.
- **N=8**: S&P 500, EAFE, Emerging Markets, US Tech, Japan Topix, US High Yield, US Gov 10y, T-Bills.
- **N=16**: 10 Fama/French sectors (NoDur, Durbl, Manuf, Enrgy, HiTec, Telcm, Shops, Hlth, Utils,
  Other) + US Gov 10y, US Gov 30y, US Muni, US Corp, US High Yield, T-Bills.
- **N=39**: N=8 ∪ N=16 + US Small Caps, GSCI, Gold, Int'l Gov Bonds, US TIPS, REITs, Mortgage
  REITs, FTSE US 1000 / US 1500 / Global ex-US / Developed / EM, Japan Gov 10y, Dow Utilities /
  Transports / Industrials, FX (1x), FX (2x), Timber.

**Expected return** (pp. 10-11; `returnForecast` p. 28), simple total returns on month-end
monthly prices:
```
mu_i = ( r1 + r3 + r6 + r12 ) / 22        # rK = P_t / P_{t-K} - 1
```
The text says "average"; the code divides by 22. No effect on the target-volatility solution,
which is invariant to the scale and level of returns (p. 6 n. 3, p. 8).

**Covariance** (pp. 10-11): historical (sample) covariance of the monthly returns of the last 12
months. Daily data tested without gain (p. 10 n. 8).

**Optimisation** (pp. 5-8, 10-11; `CCLA` pp. 25-28) — long-only, fully invested MVO:
```
max_w  w'mu   s.t.  sqrt(12 · w'Σw) ≤ TV ,  Σ w_i = 1 ,  0 ≤ w_i ≤ cap_i
cap_i = 25% (risky) ; 100% (T-Bills, US Gov 10y)
```
This formulation is an **inference** equivalent to the code: the CLA starts from the
maximum-return portfolio (assets filled by `mu` rank up to their cap), walks down the frontier
corner by corner towards minimum variance and stops at the first point with annualised vol < TV,
bisecting on lambda (tol. 1e-5) between two corners. If the first corner is already < TV →
maximum return; if TV is never reached → last corner (minimum variance) (pp. 27-28).

**Code preprocessing** (pp. 25, 28): an asset is excluded for the month if it has an NA in the
window; `mu` ties broken by 1e-12·rank noise; perfectly correlated assets removed (never an
uncapped one); error if no uncapped asset.

**Defensive fallback**: no explicit rule; cash emerges from the optimisation (pp. 15, 21; fig. 19
p. 23: 100% US Gov 10y from June to Oct 2008).

**Rebalancing**: monthly, month end; weights estimated up to t, held in t+1 (pp. 10-11).

**Variants** (pp. 8-9, 11, 21-22): **CAA offensive** TV = 10%, **CAA defensive** TV = 5%, cap 25%
by default; caps tested 10/17/25/33/40/50/100%. **CAA/MSR**: maximum-Sharpe point (rf = 0) on the
same frontier; EW, MV, MD, ERC, naive RP are special cases — not backtested. Benchmark: EW (1/N)
over the full universe.

## Published results

Monthly TR data (GFD, Fama/French, Barclays, MSCI, Yahoo; details in Keller & Butler 2014b),
**Jan 1915 – Dec 2014**, lookback from Jan 1914, no costs, no IS/OS split (pp. 9, 11-12).
SR5 = (R−5%)/V; CR5 = (R−5%)/|D|.

| Cap 25% | R | V | D | SR5 | CR5 | Page |
|---|---|---|---|---|---|---|
| N=8 TV10 | 12.7% | 8.3% | −17.3% | 0.92 | 0.45 | p. 13 |
| N=8 TV5 | 10.5% | 5.8% | −10.6% | 0.95 | 0.52 | p. 13 |
| EW N=8 | 8.7% | 9.2% | −49.7% | 0.40 | 0.07 | p. 13 |
| N=16 TV10 | 11.2% | 9.4% | −19.7% | 0.66 | 0.31 | p. 15 |
| N=16 TV5 | 8.7% | 5.9% | −12.2% | 0.63 | 0.31 | p. 15 |
| EW N=16 | 8.7% | 11.5% | −64.7% | 0.33 | 0.06 | p. 15 |
| N=39 TV10 | 15.4% | 10.4% | −22.8% | 1.00 | 0.46 | p. 17 |
| N=39 TV5 | 11.8% | 7.3% | −15.6% | 0.92 | 0.43 | p. 17 |
| EW N=39 | 8.8% | 10.7% | −63.3% | 0.35 | 0.06 | p. 17 |

Best R: N=39 TV10 cap 50% = 16.3% (p. 22). Turnover ≈ 4 (N=8) to 7 (N=39) per year (p. 19 n. 9).

## Ambiguities and implementation traps

- **12 or 13 months**: the text says 12, but `returns[ep[i]:ep[i+12]]` takes **13** monthly
  returns (inference, p. 28); the first window contains a return imputed as 0.
- **Perfect-correlation removal bug**: `toRemove <- max(valid)` overwrites the `intersect` and
  removes the last capped asset, correlated or not (pp. 28-29). Affects N=39 (FX 1x/2x). Do not
  reproduce.
- The code assumes **monthly** prices; with daily data, Σ would be daily against `scale = 12`
  (inference).
- Realised vol < TV at a 25% cap; it gets closer with higher caps (p. 21).
- **Inconsistencies**: n. 9 uses R = 14.4% instead of 15.4% (p. 20); n. 2 writes v² = w'Cw then
  w'Cw/T (p. 5); sign of D varies and figure captions are shifted (pp. 15, 17).
- **Data**: century-long proxies not published, assets missing at the start/end (pp. 15, 17); any
  ETF mapping is an assumption.
- **Costs** not modelled; impact estimated ≤ 0.7%/yr (pp. 19-20 n. 9). EW rebalancing not
  specified.
- **MSR** is not invariant to the level of returns: /22 vs /4 and rf change its result (p. 6
  n. 3, p. 8).
