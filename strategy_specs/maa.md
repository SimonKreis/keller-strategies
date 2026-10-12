# MAA — Tactical MPT and Momentum: the Modern Asset Allocation

| | |
|---|---|
| **Source** | Keller, W.J. & van Putten, H.S. (2013), *Tactical MPT and Momentum: the Modern Asset Allocation (MAA)*, SSRN **2373086** — v1.0 (PDF metadata), 30 December 2013 |
| **Paper** | [SSRN 2373086](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2373086) (47 pp.) — not redistributed here; download it from SSRN |
| **Implementation** | none — removed from the registry on 2026-07-28 (see [`../KNOWN_GAPS.md`](../KNOWN_GAPS.md) §6) |
| **Family / successor** | Extends FAA ([`faa.md`](faa.md)): FAA is presented as its non-parametric variant (ranks, equal-weight Top-X) (p. 10). Announced follow-up: the risk-parity family as a special case (note 9, p. 9) → treated in MPT ([`mpt.md`](mpt.md)). |

> Written from the PAPER, not from the code. Page numbers refer to the SSRN PDF. A paraphrase,
> detailed enough to reimplement without the PDF.

## Rules, as published

**Universe** (pp. 13, 24-31, appendix B pp. 38-43). Main variant N=7 (index funds): VTSMX,
FDIVX, VEIEX, VBMFX, VFISX, VGSIX, QRAAX (ETF equivalents: VTI, VEA, VWO, BND, IEI, VNQ, DBC).
Other universes tested:
- N=8: IYR, RWX, GLD, DBC, DBE, IEI, IEF, TLT (p. 24)
- N=11: SPY, FMCSX, FBGRX, FDIVX, FEMKX, FBNDX, FGOVX, FHIGX, FFXSX, FAGIX, FNMIX (p. 25)
- N=12: XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY, IEI, IEF, TLT (p. 26)
- N=15: SHY, IEI, IEF, TIP, TLT, MBB, MUB, CIU, LQD, JNK, HYG, PCY, EMB, BWX, WIP (p. 27)
- N=26c (23 countries + IEI, IEF, TLT), N=26 (multi-asset), N=60, N=130: lists pp. 40-43 (not reproduced).

History extended before the ETF launches by splicing with similar index funds (appendix B).

**Model** (pp. 3-4): long-only Sharpe maximisation, no leverage, rf = 0, under Elton's (1976)
single-index model (SIM), market index = EW of the universe (rebalanced monthly).
```
(4)  w_i = s_p · (1 − t/t_i) · r_i / s_i     if t_i > t, else w_i = 0
     t_i = r_i / b_i                           (Treynor ratio)
(A.5) t = ( s · Σ_p r_j b_j / s_j ) / ( 1 + s · Σ_p b_j² / s_j )   Σ_p : assets with w_j > 0
```
`s_p` = normalising constant (Σ w_i = 1). Solution (pp. 7, 36): start from t = 0, compute w,
recompute t over the retained assets, iterate until convergence (also works with b_i < 0);
alternative: Elton's sort by decreasing t_i if all b_i ≥ 0.

**Estimation** (p. 7): r_i = price ROC (adjusted close) over the lookback; volatilities and
correlations on daily returns over the same lookback (≈ 84 days for 4 months). Default: 4 months
for R, V and C (p. 11).
```
(6) s_ij = v_i v_j c_ij        (7) s = ΣΣ s_ij / N²        (8) b_i = Σ_j s_ij / (s N)
(2) s_i = s_ii − s b_i²        (idiosyncratic variance)
```
**Shrinkage** (pp. 8-9), weight W ∈ [0,1] (1 = no shrinkage):
```
(9)  r_i  = WR r_i^s  + (1−WR) r_a^s
(10) v_i  = WV v_i^s  + (1−WV) v_a^s
(11) c_ij = WC c_ij^s + (1−WC) c_a^s     (i ≠ j)
(12) s    = WS s^s
```
r_a, v_a, c_a = cross-sectional averages (return, volatility, cross-correlation). r_a = r_m
unless r_m < 0: then r_a = a small positive constant (e.g. 1E-06) (p. 9, note 8).

**Default parameters**: WR = WV = WC = WS = 0.5, lookback 4/4/4 months (pp. 11-12).

**Named variants** (pp. 9, 14, 19, 22-23): EW (WR=WV=WC=0); A (sign r_i, equal weights on
r_i > 0); AR-50; ARV-50 (WC=WS=0, eq. 5: w_i ∝ r_i/s_ii for r_i > 0); ARVS-50 (WC=0: constant
correlation); MV = VCS-50 (WR=0, eq. 13: w_i ∝ (1−b_i/b)/s_i for b_i < b); MAA-100 (all at 1);
**MAA-TV**: WV calibrated over the whole backtest to maximise R subject to V ≤ 10% (N=7:
WV = 18%); MAA-Opt (WR=30, WV=0, WC=100, WS=100%, calibrated 1997-2001); MAA-TV1 (WV=7%),
MAA-TV2 (WV=30%). MAA-TV's WV per universe: N=8 25, N=11 12, N=12 18, N=26c 59, N=26 22, N=60 36,
N=130 47.5; N=15: WR=100, WV=0 (pp. 24-31).

**Cash**: no cash asset; cash only if all w_i = 0 (pp. 10-11). Short Treasury funds (VFISX/SHY)
serve as quasi-cash (note 4, p. 4).

**Rebalancing** (p. 12): monthly, executed at the first close of the new month on data from the
last close of the previous month; costs 10 bps one-way.

## Published results

Yahoo adjusted-close data, 1 Nov 1997 – 15 Nov 2013 (p. 12). Sharpe with rf 2.5%, Q5 = Calmar
with a 5% target.

| N=7 (pp. 13-23) | R | V | D | T | S | Q5 |
|---|---|---|---|---|---|---|
| MAA (50/50/50/50) | 9.30 | 6.20 | 5.20 | 1.85 | 1.11 | 0.83 |
| MAA-TV (WV=18) | 11.80 | 10.00 | 9.60 | 2.60 | 0.93 | 0.71 |
| MAA-Opt | 12.70 | 9.80 | 8.50 | 2.51 | 1.05 | 0.91 |
| MAA-100 | 7.10 | 9.00 | 24.30 | 2.97 | 0.51 | 0.08 |
| MV (VCS-50) | 5.20 | 4.60 | 17.80 | 0.38 | 0.59 | 0.01 |
| EW | 6.70 | 13.40 | 46.30 | 0.03 | 0.31 | 0.04 |

Average over the 9 universes (p. 44): MAA R 9.10 / V 7.63 / D 9.18 / S 0.90 / Q5 0.50; MAA-TV
10.36 / 9.74 / 12.07 / 0.81 / 0.45; EW 7.48 / 12.52 / 37.29 / 0.43 / 0.07. Robustness N=7:
4-month lookback optimal among 1-12 (p. 21); MAA stays ahead of EW up to ~80 bps of costs (p. 22).

## Ambiguities and implementation traps

- **Order of the shrinkage of s**: not specified whether b_i (8) and s_i (2) use s^s or
  s = WS·s^s. With a shrunk s in (8), b_i is divided by WS and s_i can turn negative. Inference:
  compute b_i and s_i with s^s, apply WS·s^s only in t (A.5).
- **Negative beta**: the condition "t_i > t" would exclude an asset with b_i < 0, r_i > 0,
  whereas the text says it acts as a hedge with (1−t/t_i) > 1 (p. 6). Inference: use the
  equivalent form w_i ∝ (r_i − t·b_i)/s_i, retained if positive.
- **ROC**: exact definition (price or total return, calendar window or 84 sessions) not
  specified; daily volatility possibly not annualised — inference: the formula is invariant to a
  common scale factor on r or on the variances.
- **c_a**: average of the off-diagonal correlations (inference from "average (cross)
  correlation"); note 6 (p. 7) says one can use only the correlations with the EW index.
- **r_m < 0**: the 1E-06 constant applies only to the shrinkage target; if WR > 0 and all
  r_i ≤ 0, all w_i = 0 → cash, whose asset is not specified.
- **MAA-TV**: calibration over the full sample = acknowledged look-ahead (note 10, pp. 11-12);
  do not treat it as out-of-sample.
- Typos: appendix B.3 titled "N=8" but lists 11 funds; §9.6 refers to "8.4" for bonds (read
  9.4); backtester string p. 38 "50/18/50/0/50%" has five fields, fifth weight unexplained.
- Drawdown measurement frequency (daily or monthly): not specified.
