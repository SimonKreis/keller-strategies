# MPT — Momentum, Markowitz, and Smart Beta

| | |
|---|---|
| **Source** | Keller, W.J. (2014), *Momentum, Markowitz, and Smart Beta: A Tactical, Analytical and Practical Look at Modern Portfolio Theory*, SSRN **2450017** — v0.9 (p. 1; PDF metadata "v3"), 13 June 2014 |
| **Paper** | [SSRN 2450017](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2450017) (21 pp.) — not redistributed here; download it from SSRN |
| **Implementation** | none — never implemented in this repository |
| **Family / successor** | Follow-up to MAA ([`maa.md`](maa.md)) (note 1, p. 1); revised version of the NAAIM/Wagner 2014 submission. Adds the "smart beta" sub-models MV, MD, RP. Successor: not specified (leads: unrestricted MPT via the Critical Line Algorithm, EMA/GARCH, p. 18). |

> Written from the PAPER, not from the code. Page numbers refer to the SSRN PDF. A paraphrase,
> detailed enough to reimplement without the PDF.

## Rules, as published

**Universe** (pp. 10, 14, 16):
- **N=10** (main): VTI, VGK, EWJ, EEM, IEF, TLT, IYR, RWX, DBC, GLD.
- **N=35**: VTI, IWM, VIG, QQQ, XLF, XLY, XLP, XLU, XLV, XLB, PFF, VGK, EWJ, EPP, SCZ, FXI, ILF,
  EWX, SHY, IEI, IEF, TLT, TIP, MUB, MBB, CIU, LQD, HYG, BWX, EMB, VNQ, RWX, DBE, DBC, DBP.
- **N=104**: the 100 current Nasdaq-100 constituents + IEI, IEF, TLT, EDV; stocks extended back
  to 1997 with ^NDX (note 14, p. 16).

**MAA formula** (p. 4, appendix p. 19) — long-only max Sharpe, SIM, rf = 0, index = EW:
```
(1)   w_i ~ (1 − t/t_i) · r_i / s_i        if t_i > t, else 0      t_i = r_i / b_i
(A.6) t = ( s Σ_p r_j b_j/s_j ) / ( 1 + s Σ_p b_j²/s_j )             Σ_p : assets with w_j > 0
      b_i = v_i c_i / v      s = v²      s_i = v_i² − s b_i²          c_i : correlation of i with the index
```
Solution: iterate between w and t from t = 0 until convergence (note 5, p. 4; p. 19). Weights
normalised to Σ w_i = 1.

**Sub-models** (pp. 5-6, 19):
```
MV  (r_i = constant)  : w_i ~ (1 − b_i/b) / s_i        if b_i < b      b = 1/t with r_m = 1
MD  (r_i = v_i)       : w_i ~ (1 − c_i/c) v_i / s_i    if c_i < c      c = 1/t
RP  (MD with s = 0)   : w_i ~ 1 / v_i
MAA-CC (c_i constant) : w_i ~ (1 − h/h_i) / s_i        if h_i > h      h_i = r_i / v_i, h = 1/t
EW                    : w_i = 1/N
```
**Estimation** (pp. 6-8): r_i = price ROC over the lookback; v_i, v and c_i on daily total-return
returns over the same lookback (≈ 84 days for 4 months). Only the N correlations with the index
are estimated. Default: 4 months for R, V, M, C.

**Shrinkage** (pp. 7-8) — components R, V, M, C; W = 100% no shrinkage, 0% full shrinkage:
```
r_i ← WR·r_i + (1−WR)·r_m       (note 8 ; r_m = Σ r_i / N)
v_i → cross-sectional average of the v_i   (WV)
s   → 0                                     (WM)
c_i → cross-sectional average of the c_i   (WC)
WP = 100% : r_i replaced by v_i ("Parity")
```
All averages are cross-sectional and over the same lookback (p. 8).

**Model parameters** (Table 1, p. 8):

| Model | WR | WV | WM | WC | WP |
|---|---|---|---|---|---|
| MAA | 50 | 50 | 50 | 50 | 0 |
| MAA-Off | 50 | 0 | 50 | 50 | 0 |
| MV | 0 | 50 | 50 | 50 | 0 |
| MD | 0 | 50 | 50 | 50 | 100 |
| RP | 0 | 100 | 0 | 0 | 100 |
| EW | 0 | 0 | 0 | 0 | 0 |

Universe N=104: WR = 10% for MAA and MAA-Off, WV = 10% for MAA, MV, MD (note 10, p. 8; p. 16).

**Rebalancing** (p. 9): monthly, at the first close of the new month on (adjusted) data from the
last close of the previous month; costs 10 bps; long-only, no leverage. Cash fallback: not
specified.

## Published results

Bloomberg data (N=10) and Yahoo (N=35, N=104), backtest 31 Dec 1997 – 31 Dec 2013 (pp. 9-10, 14,
16). SR with rf 2.5%, CR = Calmar with a 5% target, statistics computed on monthly data
(pp. 9-10).
- **N=10**: results only in charts (fig. 1, p. 11); MAA and MAA-Off dominate EW, MV, MD, RP on
  CR; 4-month lookback optimal over 1998-2013, ~2 months over 1998-2005 (p. 14).
- **N=35** (p. 14): MAA R 10.7%, V ≈ 8%, D ≈ 7%; MAA-Off R 14.3%, V ≈ 14%, D ≈ 17%; EW R 9.5%,
  V 14%, D 37%.
- **N=104** (p. 16): R ≈ 36% MAA-Off, 29% MAA and MD, 20% RP, 24% EW; V 13-21% excluding EW, 27%
  EW; CR ≈ 1.5 (MAA, MAA-Off), ≈ 1.1 (MV, MD), ≈ 0.4 (RP, EW; D 38% and 47%); OR ≈ 4 and
  SR ≈ 1.6 for MAA, MAA-Off, MV, MD.
- Results robust up to 50-100 bps of costs (note 11, p. 9).

## Ambiguities and implementation traps

- **Inconsistent MD**: eq. (3) gives `(1 − c_i/c) v_i / s_i`, the appendix `(1 − c_i/c) / s_i`
  (p. 19). Inference: (3) follows from r_i = v_i in (1); the appendix seems to omit v_i.
- **WP**: exact combination with WR not specified (note 9 mentions WR = 50%, WP = 50%). Is the
  substituted v_i the shrunk v_i (MD: WV = 50%)? Not specified; for RP, p. 10 says unshrunk
  volatilities, consistent with WV = 100%.
- **WM order**: b_i and s_i computed with the raw or shrunk s: not specified (same trap as MAA).
  Inference: WM applies only to the threshold t.
- **r_m < 0** with WR = 0: all r_i negative → zero weights; the paper assumes r_m = 1 for MV/MD
  (p. 19), MAA 2013 substitutes 1E-06. Fix explicitly.
- **Negative beta**: the condition t_i > t is incompatible with the "hedge" case (note 6, p. 5);
  inference: use w_i ∝ (r_i − t b_i)/s_i.
- Notation: MAA is also called "MS" (figs. 2-4, note 10); the S component of MAA 2013 becomes M
  (WM), and the shrinkage applies to c_i (correlation with the index) instead of c_ij.
- **N=104**: survivorship bias (current Nasdaq-100 constituents, extended with ^NDX); WR/WV = 10%
  chosen after the fact.
- N=10 figures not published in a table; N=35 and N=104 values approximate ("nearly double",
  "around").
