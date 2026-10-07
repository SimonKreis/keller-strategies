# EAA — A Century of Generalized Momentum: from FAA to Elastic Asset Allocation

| | |
|---|---|
| **Source** | Keller, W.J. & Butler, A. (2014), *A Century of Generalized Momentum; From Flexible Asset Allocations (FAA) to Elastic Asset Allocation (EAA)*, SSRN **2543979** — v0.92, 16 January 2015 (v0.90 of 30 December 2014) |
| **Paper** | [SSRN 2543979](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2543979) (32 pp.) — not redistributed here; download it from SSRN |
| **Implementation** | none — removed from the registry on 2026-07-28 (see [`../KNOWN_GAPS.md`](../KNOWN_GAPS.md) §6) |
| **Family / successor** | Generalises FAA ([`faa.md`](faa.md)): ordinal ranks → cardinal scores with elasticities; starts from MAA ([`maa.md`](maa.md), [`mpt.md`](mpt.md)), of which it is a proxy (pp. 1-2, appendix A). Successor: not named. |

> Written from the PAPER, not from the code. Page numbers refer to the SSRN PDF. A paraphrase,
> detailed enough to reimplement without the PDF.

## Rules, as published

**Universe** (monthly total-return indices, dividends reinvested; no ETF tickers published, p. 7):
- **N = 7**: SP500, EAFE, EEM, US Tech, Japan Topix, US Gov10y, US HighYield.
- **N = 15**: 10 Fama/French US sectors + Gov10y, Gov30y, US Muni, US Corp, US HighYield (growing
  universe: N = 2 in 1914 → 15 from 1927, p. 14).
- **N = 38**: all of the above + US SmallCaps, GSCI, Gold, Foreign bonds, US TIPS, REIT, NAREIT
  (p. 7: US Composite REITs, US Mortgage REITs), 5× FTSE (US 1000, US 1500, Global ex US,
  Developed, EM), JapanGov10y, Dow Util/Transport/Industry, FX-1x, FX-2x, Timber (pp. 7, 17).
  Variable universe: N and NTop follow data availability (pp. 10, 17).

**Estimators** (max window 12 months, p. 9):
```
r_i = average of the EXCESS total returns over 1, 3, 6 and 12 months   (step 9)
      excess relative to the 13-week T-Bill
v_i = standard deviation of the last 12 NOMINAL monthly returns
c_i = correlation of the last 12 nominal monthly returns with the index
index = equal-weight (1/N) nominal monthly return of the N assets of the universe
```

**Generalised momentum score** (eq. 4, p. 4; general form eq. 1, p. 3):
```
z_i = ( r_i^wR · (1 − c_i)^wC / v_i^wV )^(wS + ε)   if r_i > 0,  else z_i = 0
wR = 1 (normalisation), ε = 1E-6 (p. 5, p. 10)
```
wS → 0 gives an EW of the TopX ranked on the base score (FAA-like, p. 5); a large wS
concentrates on the best asset.

**In-sample parameters retained**: `wV = 0` for all tests (V judged to have no effect, collinear
with C, p. 10); sweep wS, wC ∈ {0, 0.25, 0.5, 0.75, 1, 1.5, 2} (49 scenarios), criterion CR5
(p. 10). Scenario number = 7·idx(wS) + idx(wC) + 1 (inference, consistent with the tables).

**"Golden" variants** (p. 19):
```
Golden Defensive : wS = 0.5 ; wC = 1   →  z_i = sqrt( r_i · (1 − c_i) )      (eq. 11)
Golden Offensive : wS = 2   ; wC = 0.5 →  z_i = (1 − c_i) · r_i²              (eq. 12)
for r_i > 0, else z_i = 0
```

**TopX** (p. 4, note 4 p. 10):
```
NTop = Min( 1 + Roundup(Sqrt(N)), Rounddown(N/2) )     → 3 (N=7), 5 (N=15), 8 (N=38)
```
Only assets with `z_i > 0` are eligible; if fewer than NTop are positive, fewer are kept (p. 4).

**Crash protection** (eq. 3, p. 4; p. 10):
```
wCP = (number of assets in the universe N with r_i <= 0) / N        → "safe" asset
Σ_{j ∈ Top} w_j = 1 − wCP,   w_j ∝ z_j
```
Published example: N = 11, 7 assets ≤ 0 → 64% cash, 36% spread over the 4 positive ones (p. 4).

**Safe asset**: US Gov10y for all universes (best in-sample against the T-Bill and other bonds,
p. 10).

**Rebalancing**: end of each month, end-of-month monthly data (p. 7). Transaction cost 0.1%
one-way, no leverage (p. 10).

**Special cases** (eq. 5-9, pp. 5-6; appendix A): EW (all exponents zero), naive risk parity
(wV = 1), inverse variance (wV = 2), `r_i/v_i²` (wR = 1, wV = 2), Maximum Diversification proxy
`(1−c_i)^wC / v_i` (wR = 0, wV = 1, wC = 1/c).

## Published results

IS = end of April 1914 – March 1964; OS = April 1964 – August 2014 (p. 6). Benchmark = universe
EW rebalanced monthly (p. 11). R = CAGR net of costs; CR5 = (R − 5%)/D (eq. 10, p. 9).

**OS, Golden models**:

| universe | model | R | V | D | CR5 | SR (rf) | page |
|---|---|---|---|---|---|---|---|
| N=7 | Def. | 13.1% | 9.7% | 19.1% | 42.4% | 0.83 | p. 20 |
| N=7 | Off. | 14.5% | 11.4% | 25.3% | 37.6% | 0.83 | p. 20 |
| N=7 | EW | 9.5% | 11.3% | 43.4% | 10.4% | 0.40 | p. 20 |
| N=15 | Def. | 10.3% | 8.8% | 12.5% | 42.6% | ≈0.60 | p. 22 (table is an image, read by OCR) |
| N=15 | Off. | 11.7% | 10.1% | 12.5% | 53.4% | ≈0.66 | p. 22 (OCR) |
| N=15 | EW | 9.6% | 10.7% | 34.8% | 13.4% | 0.43 | p. 22 |
| N=38 | Def. | 12.8% | 7.9% | 8.6% | 90.2% | 0.97 | p. 24 |
| N=38 | Off. | 14.3% | 10.1% | 14.1% | 65.7% | 0.91 | p. 24 |
| N=38 | EW | 9.6% | 9.6% | 36.7% | 12.6% | 0.48 | p. 24 |
| — | SP500 | 9.9% | 15.0% | 50.8% | 9.6% | 0.32 | p. 20 |

**IS, best CR5**: N=7 scen. 10 (wS 0.25/wC 0.5) R 13.1%, D 11.5% vs EW 8.9%/54.9% (pp. 13-14);
N=15 scen. 20 (0.5/1.5) R 8.6%, D 12.5% vs EW 8.0%/67.6% (p. 16); N=38 scen. 19 (= Golden Def.)
R 11.5%, D 10.9% vs EW 8.0%/65.1% (p. 18). Annual costs ≈ 0.4-0.6%. Note 6 (p. 27): the N=38
Offensive stays above EW as long as the one-way cost < 0.7%.

## Ambiguities and implementation traps

- **Computing r_i**: "average of the 1/3/6/12-month excess returns" — non-annualised cumulative
  returns (inference: the unweighted 13612 form); how the T-Bill is subtracted (annual rate
  prorated to each horizon?) is not specified. Since r_i is raised to the power wS·wR, its scale
  is neutral (p. 5), but its **sign** is not: the CP filter applies to the excess return.
- **Safe asset ∈ universe**: Gov10y is in all three universes; if it is also selected in the Top,
  the weights accumulate — not addressed. What to do if Gov10y itself has r ≤ 0: not specified.
- **CP over a variable N**: wCP = share of the universe *available* at the date (inference,
  consistent with NTop following N); the EW index also follows the variable N.
- **v_i**: sample or population standard deviation, not specified (no effect since wV = 0 in all
  published tests).
- **Timing**: rebalancing at month end on month-end data — same close as the signal (execution
  look-ahead); the authors themselves suggest a test with a one-month delay (p. 27).
- **Typos**: "US 33-month Treasury Bill" (p. 10, inference: 3-month); "1<=ci<=1" (p. 5, read
  −1 ≤ c_i ≤ 1); "N=388" (p. 17).
- **Incomplete N=38 universe**: the list on p. 17 repeats US Gov10y and omits US Tech (included
  per p. 7, "all of the above"); the reconstruction to 38 is an inference. No source or ticker
  per series is given; exact reproduction is impossible without the dataset (MSCI, Fama/French,
  Ibbotson, Barclays, GFD, p. 7).
- **Golden ≠ optimum per universe**: chosen to behave well on all three universes at once
  (pp. 18-19); for N=7 its own optima were 0.25/0.5 and 0.5/0.5.
- **Historical frictions**: 0.1% one-way is unrealistic before index funds (p. 27); index data,
  no management fees.
