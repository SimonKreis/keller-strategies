# FAA — Generalized Momentum and Flexible Asset Allocation

| | |
|---|---|
| **Source** | Keller, W.J. & van Putten, H.S. (2012), *Generalized Momentum and Flexible Asset Allocation (FAA): An Heuristic Approach*, SSRN **2193735** — v0.98 (draft), 24 December 2012 |
| **Paper** | [SSRN 2193735](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2193735) (19 pp.) — not redistributed here; download it from SSRN |
| **Implementation** | none — removed from the registry on 2026-07-28 (see [`../KNOWN_GAPS.md`](../KNOWN_GAPS.md) §6) |
| **Family / successor** | Extends Faber's TAA (10-month MA + relative momentum) by replacing the MA with absolute momentum (Antonacci), then adds volatility and correlation (pp. 2-3). Successor: not named in the paper (the EAA paper, [`eaa.md`](eaa.md), presents itself as its generalisation). |

> Written from the PAPER, not from the code. Page numbers refer to the SSRN PDF. A paraphrase,
> detailed enough to reimplement without the PDF.

## Rules, as published

**Universe** (U = 7, index funds, p. 3): VTSMX (US), FDIVX (EAFE), VEIEX (EM), VFISX (US gov
2-3y), VBMFX (US agg bonds), QRAAX (commodities), VGSIX (REIT). Suggested ETF equivalents: VTI,
VEA, VWO, SHY, BND, GSG, VNQ (p. 3). Daily dividend-adjusted closes, in USD (p. 3, p. 18).

**Cash proxy** (`cpf`): VFISX (p. 3), which is also a member of the ranked universe.

**Factors**, all over the same window m = 4 months (pp. 4, 8, 10):
- `r_i`: return (momentum) over m months; absolute momentum (A) always uses the same window as R (p. 5).
- `v_i`: volatility of **daily** returns over m months (p. 7).
- `c_i`: average correlation of asset i with the U−1 other assets of the universe (off-diagonal elements), p. 9.

**Generalised rank score** (eq. 1/2, pp. 8-10), lower = better:
```
L_i = wR·rank(r_i) + wV·rank(v_i) + wC·rank(c_i)
rank(r) = 1 for the highest r ; rank(v) = 1 for the lowest v ;
rank(c) = 1 for the lowest c ; rank U = worst.  wR, wV, wC ≥ 0 ; normalisation wR = 1.
```

**Selection**: sort the U assets on `L_i`, keep the best N (N = 3 ≈ 40% of U), equal-weight 1/N
(pp. 4, 10).

**Absolute momentum (crash protection)**: after sorting and selection, each selected asset with
`r_i < 0` is replaced by the cash proxy (p. 8); threshold `rmin = 0` (p. 3). Published example:
Oct-Nov 2008 = 100% `$CASH$` (p. 6).

**Rebalancing**: signal at the close of the last day of the month, execution at the open of the
first day of the next month (p. 4).

**Named variants** (notation `N/U, mR/mV/mC, wR/wV/wC`):

| variant | parameters | page |
|---|---|---|
| R only | 3/7, 4m, 100/0/0, no A | p. 4 |
| R+A | 3/7, 4m, 100/0/0 | p. 6 |
| R+A+V | 3/7, 4m, 100/50/0 | p. 9 |
| **RAVC default** | 3/7, 4m/4m/4m, **100/50/50** | p. 10 |
| RAVC "optimised" (Q5 in-sample) | 3/7, 4m, **100/80/60** | p. 12 |
| RAVC leveraged | 100/80/60, lev = 2, leverage cost 3%/yr, tc = 0.1% | p. 12 |

**Extensions (not used in the backtests)** (p. 11): rank weighting
`w_i = (N+1−rank_i)/Σrank_i` (3/6, 2/6, 1/6 for N = 3) or a blend
`w_i = (1−a)/N + a·rank_i/Σrank_i` (a = 0.5 → 2.5/6, 2/6, 1.5/6); logarithmic form (eq. 3):
```
−L_i = wR·ln(r_i/rmax) + wV·ln(vmin/v_i) + wC·ln((cmin+1)/(c_i+1))
```
(requires r_i > 0; with wR = wV, wC = 0 it is equivalent to sorting on r_i/v_i.)

## Published results

Annualised statistics on monthly measurements, except V (daily); D = monthly max drawdown
(pp. 4-5).

| period | model | R | V | D | S0 | Q5 | page |
|---|---|---|---|---|---|---|---|
| IS 01/2005-12/2012 | R only | 9.1% | 14.5% | −29.2% | 0.63 | 0.14 | p. 4 |
| IS | R+A | 11.7% | 12.8% | −12.6% | 0.92 | 0.53 | p. 6 |
| IS | R+A+V | 12.5% | 11.7% | −11.4% | 1.07 | 0.66 | p. 9 |
| IS | RAVC 100/50/50 | 14.7% | 9.2% | −7.4% | 1.60 | 1.31 | p. 10 |
| IS | RAVC 100/80/60 | 13.0% | 7.4% | −5.2% | 1.76 | 1.53 | p. 12 |
| IS | Bench EW 7/7 | 5.6% | 16.6% | −46.3% | 0.34 | 0.01 | p. 4 |
| OS 01/1998-01/2005 | RAVC 100/50/50 | 13.4% | 7.7% | −5.9% | 1.73 | 1.43 | p. 13 |
| OS | Bench EW | 8.3% | 9.8% | −15.2% | 0.85 | 0.22 | p. 13 |
| 1998-2012 | RAVC 100/50/50 | 14.2% | 8.5% | −7.4% | 1.67 | 1.25 | p. 15 |
| 1998-2012 | Bench EW | 6.8% | 13.8% | −46.3% | 0.50 | 0.04 | p. 15 |

Leverage 2× + costs: IS R = 22.6%, V = 14.7%, D = −10.7% (p. 12); OS R = 21.6%, V = 14.5%,
D = −12.9% (p. 14); 1998-2012 (100/80/50) R = 23.2%, V = 15.2%, D = −16.5% (p. 15). Turnover
≈ 2.6-3.1×/yr. Robustness: 4-month window optimal among 1-12 (fig. 8, p. 15); min-max ranges
over ±1 step of the 6 parameters and removal of each fund: R = 15-24%, D = 13-24% (p. 16).
Transaction-cost threshold before falling below the benchmark: 1.20% (p. 12).

## Ambiguities and implementation traps

- **Inconsistent A threshold**: `r_i < 0` (pp. 3, 8, 11) vs `r_i <= 0` (p. 5). Inference: `<= 0`
  is the conservative choice.
- **Sort/filter order**: the A filter applies *after* selecting the best N on `L_i` (p. 8); a
  negative asset can therefore occupy a slot (→ cash) rather than give way to the positive
  (N+1)-th.
- **VFISX dual role**: ranked in the universe AND the cash proxy; if it is selected and other
  slots go to cash, its weight accumulates (cf. 66.6% `$CASH$`, p. 6). How a VFISX with `r < 0`
  is treated as cash is not specified.
- **"4 months"**: number of trading days (≈ 84) or calendar months, not specified; same for the
  correlation window and the kind of returns (daily? inference for c_i, not specified).
- **Rank ties**: handling not specified.
- **Contradictory "optimal" parameters**: 100/80/**60** in §12 (pp. 12-14) but 100/80/**50**
  presented as the best solution in §14 (pp. 15-16, without comment).
- **Internally inconsistent figures**: §11 quotes RAV at R = 12.1% and D = 10.4% (p. 10) whereas
  §9 publishes 12.5% and 11.4% (p. 9); benchmark quoted at 5.7% "par. 2" (p. 12) vs 5.6% in §5.
  In-sample window: 03/01/2005-11/12/2012 (not all of December).
- **Rank-weighting formula**: `(N+1−rank_i)/Σrank_i` is consistent with the example, but the
  blend formula writes `rank_i/Σrank_i` — the numerical example (2.5/6 to the best) requires
  `(N+1−rank_i)`.
- **Leverage**: which notional the 3%/yr cost applies to is not specified; "tc = 0.1% per
  transaction" without a defined base (one-way? inference).
- **Proxies and data**: mutual index funds rather than ETFs (p. 3); data from mid-1997, hence a
  start in 01/1998 after the 4-month window (pp. 3, 13); execution at the next-day open assumed
  slippage-free (p. 4); no costs in the unleveraged variants.
