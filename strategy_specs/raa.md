# RAA — Resilient Asset Allocation (Lazy Momentum with Growth-Trend Timing)

| | |
|---|---|
| **Source** | Keller, W.J. (2020), *Lazy Momentum with Growth-Trend Timing: Resilient Asset Allocation (RAA)*, SSRN **3752294** — v0.981, 12 Jan 2021 (first version 20 Dec 2020) |
| **Paper** | [SSRN 3752294](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3752294) (9 pp.) — not redistributed here; download it from SSRN |
| **Implementation** | none — removed from the registry on 2026-07-28 (see [`../KNOWN_GAPS.md`](../KNOWN_GAPS.md) §6) |
| **Family / successor** | A "more aggressive and more robust" version of LAA ([`laa.md`](laa.md)); takes the VWO/BND canary and the 13612W from DAA ([`daa.md`](daa.md)) (p. 1). Successor: not specified. **Distinct from Gray's RAA.** |

> Written from the PAPER, not from the code. Page numbers refer to the SSRN PDF. A paraphrase,
> detailed enough to reimplement without the PDF.

## Rules, as published

Three modifications of LAA (pp. 1–2), recipe p. 7.

**1. Unemployment trend "UE1" — RET12 with lag** (p. 2; p. 6, n. 10; p. 7 step 1):
```
UE1(t) = UE(t) / UE(t-12) - 1          # UE = FRED UNRATE, published with a 1-month delay
# i.e., at the end of month m : UE1 = UNRATE[m-1] / UNRATE[m-13] - 1   (inference on the indexing)
ue_bear = UE1 > 0                       # unemployment higher than 12 months ago
```
Replaces LAA's SMA12; the K25-optimal IS choice among SMAx and RETx, x = 1..12 (n. 10).

**2. Market trend — DAA canary, B = 1** (p. 5, n. 8–9; p. 7 step 2):
```
13612W = (12·r1 + 4·r3 + 2·r6 + 1·r12) / 4     # r_k = total return over k months
mkt_bear = 13612W(VWO) "bad" OR 13612W(BND) "bad"
```
A single bearish canary is enough (B = 1, against B = 2 in DAA; K25-optimal IS, n. 9). Replaces
SPY's SMA10.

**3. GT decision** (p. 7 steps 3–4):
```
if ue_bear and mkt_bear :  cash  = IEF, TLT                — 50% each (EW2)
else                    :  risky = QQQ, IWN, IEF, TLT, GLD — 20% each (EW5)
```
The canary is consulted only if unemployment is rising (p. 5, p. 7). No relative momentum or
Top-N: two static portfolios.

**Construction** (pp. 1, 3–4): from LAA's risky portfolio (QQQ, IWD, IEF, GLD), IWD → IWN (Golden
Butterfly, diversification), TLT added (Dalio's All Weather, equal weights instead of risk
parity). Cash = the risky portfolio's two bonds, K25-optimal IS among the subsets of the risky
portfolio (n. 7, p. 4).

**Rebalancing** (p. 7 step 1; n. 11, p. 6): signal at month end; backtest rebalanced every month
to equal weights; the author estimates that rebalancing only at a switch or annually would change
little.

**Costs**: 0.1% per transaction, one side (p. 3).

**Intermediate variants**: fig. 4 (EW5/EW2, LAA GT: SPY SMA10 + UE SMA12); fig. 5 (DAA canary +
UE SMA12); fig. 6 = RAA.

## Published results

ETF proxies since Dec 1969 (Keller 2016; pre-1970 judged poor, QQQ/IWN/IWD based on Fama-French)
(p. 2, n. 4). FS Dec 1970 – Nov 2020; IS Dec 1970 – Nov 1993; OS Nov 1993 – Nov 2020; RS2/RS1 =
last 20/10 years. IS optimisation criterion: **K25** (not UPI as in LAA). D = monthly max
drawdown.

| Strategy (FS) | R | D | V | K25 | UPI | CF | TTC | Page |
|---|---|---|---|---|---|---|---|---|
| **RAA** (fig. 6) | 12.3% | 11.8% | 8.9% | 8.5% | 2.83 | 15.5% | 0.16% | p. 6 |
| EW5 → EW2, canary + UE SMA12 (fig. 5) | 12.0% | 13.4% | 9.0% | 7.6% | 2.62 | 16.8% | 0.19% | p. 5 |
| EW5 → EW2, LAA GT (fig. 4) | 11.9% | 15.1% | 9.2% | 6.8% | 2.43 | 12.2% | 0.06% | p. 5 |
| LAA over the same period (fig. 3) | 11.5% | 15.0% | 9.5% | 6.6% | 1.73 | 12.2% | 0.03% | p. 4 |
| Static EW5 (fig. 2) | 10.8% | 17.1% | 9.4% | 5.2% | 1.62 | 0 | 0 | p. 4 |
| Benchmark 60/40 SPY/IEF | 9.7% | 29.5% | — | — | — | — | — | p. 3 |

RAA RS1 (Nov 2010 – Nov 2020): R 8.5%, D 5.8%, UPI 4.21 vs LAA 9.7% / 8.4% (pp. 6–7). RAA IS:
R 14.0%, D 11.8%. On average one trading month per year (p. 6, p. 7).

## Ambiguities and implementation traps

- **Canary threshold**: "bad" is not defined in the paper; it refers to DAA (inference: 13612W
  momentum ≤ 0, the DAA convention). VWO/BND data before their launch: proxies not described
  here.
- **UE lag indexing**: n. 10 writes `UE(t)/UE(t-12)-1` while the text (p. 2, p. 7) imposes a
  one-month publication delay; the exact indexing (m-1 vs m-13) is an inference. Tie
  (UE1 = 0): not specified (text: "higher" → strict).
- **Lag in the comparisons**: unknown whether fig. 3 (LAA) and fig. 5 (UE SMA12) include the
  one-month lag; the LAA/RAA comparison may mix the two conventions. LAA's RS1 CF = 0.0% here vs
  1.7% in the LAA paper (different periods).
- **Rebalancing**: n. 11 speaks of 20% per asset; in cash mode, 50/50 IEF/TLT (inference: same
  monthly rebalancing).
- **SSRN identifier**: the PDF footer carries "abstract=3764846" whereas SSRN page 3752294 is
  indeed this paper (revised 10 March 2021); keep 3752294.
- **Typos**: Golden Butterfly described with IEF (p. 3) instead of TLT (as in LAA, p. 8 of LAA);
  "CF = 40%" attributed to the static 60/40 (p. 4); unclosed parenthesis in the K25 formula (n. 5).
- **Turnover**: TTC probably excludes the monthly rebalancing to equal weights, as in LAA
  (inference); "turnover 160%" quoted on p. 2 without definition.
- **Parameters optimised IS**: B = 1, RET12 and IEF/TLT cash chosen over IS 1970–1993; pre-1970
  is discarded because it was already used as DAA's IS (n. 4).
