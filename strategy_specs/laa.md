# LAA — Lethargic Asset Allocation (Growth-Trend Timing and 60-40 Variations)

| | |
|---|---|
| **Source** | Keller, W.J. (2019), *Growth-Trend Timing and 60-40 Variations: Lethargic Asset Allocation (LAA)*, SSRN **3498092** — v0.972, 16 Jan 2020 (first version 4 Dec 2019) |
| **Paper** | [SSRN 3498092](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3498092) (15 pp.) — not redistributed here; download it from SSRN |
| **Implementation** | none — removed from the registry on 2026-07-28 (see [`../KNOWN_GAPS.md`](../KNOWN_GAPS.md) §6) |
| **Family / successor** | Applies Philosophical Economics' (2016) Growth-Trend (GT) timing to equal-weight variations of the SPY-IEF 60-40; positioned as less defensive than DAA (canary) and VAA (breadth) (p. 1). Successor: RAA ([`raa.md`](raa.md)), which presents itself as a more aggressive version of LAA. |

> Written from the PAPER, not from the code. Page numbers refer to the SSRN PDF. A paraphrase,
> detailed enough to reimplement without the PDF.

## Rules, as published

**GT signal** (p. 1, n. 4; p. 14). Month end, two trends, both as "SMA" momentum:
```
MOMx(P) = P_t / AVERAGE(P_{t-x+1} .. P_t) - 1        # SMA including the current month (n. 4, p. 1)
recession   = MOM12(UE) > 0                           # UE = FRED UNRATE, SMA12
market_down = MOM10(SPY) < 0                          # dividend-adjusted SPY, SMA10
risk_off    = recession AND market_down
```
Outside a recession the portfolio stays risky whatever SPY does; the switch happens only if both
are bearish (p. 1).

**Portfolios** (p. 10, fig. 12; recipe p. 14):
```
risky (risk_off = False) : QQQ, IWD, GLD, IEF   — 25% each
cash  (risk_off = True)  : SHY, IWD, GLD, IEF   — 25% each
```
The switch touches only 25%: QQQ ↔ SHY (p. 10).

**Portfolio selection** (pp. 5–10): fixed, no relative momentum or rotation. Obtained by a
stepwise search maximising the UPI (excess return / Ulcer index) over the IS Feb 1949 – Jun 1981:
IWD, then GLD, then QQQ added to IEF (figs. 5–7); then, in the cash basket, QQQ replaced by the
best IS bond among BIL, SHV, SHY, IEF, TLT → SHY (p. 10, n. 15).

**Rebalancing** (p. 1, p. 5): monthly, at the close of the last trading day; monthly return to
equal weights (not counted in TTC). The author suggests that in practice one can rebalance only
at a switch or annually (p. 5).

**Costs**: 0.1% per transaction, one side (p. 4); test at 1%: FS R 10.5 → 10.2% (p. 10, n. 16).

**Named variants / robustness**
- **LAA-G4** (p. 11, fig. 16): QQQ replaced by a constructed "WRLD",
  `r_WRLD = (3·SPY + 2·VEA + 1·VWO)/6` (n. 17); cash = IWD, GLD, SHY, IEF; GT stays US.
- Intermediate predecessor, fig. 7: QQQ+IWD+GLD+IEF → 100% IEF (best IS UPI, more turnover).
- UE publication lag +1 month (fig. 17, p. 12), SMA5 for UE (fig. 18), SMA5 for SPY (fig. 19),
  both (fig. 20, p. 13).

## Published results

Data: ETF proxies adjusted for dividends and fees since Dec 1947 (Ibbotson, Fama-French; QQQ
pre-1970 = FF HiTech sector) (p. 2, n. 7). UE from FRED, Jan 1948 – Oct 2019. Backtest Feb 1949 –
Oct 2019; IS Feb 1949 – Jun 1981, OS Jun 1981 – Oct 2019, RS2/RS1 = last 20/10 years. D = monthly
max drawdown; no Sharpe, UPI instead.

| Strategy (FS) | R | D | V | UPI | CF | TTC | Page |
|---|---|---|---|---|---|---|---|
| **LAA** (fig. 12/21) | 10.5% | 15.0% | 8.5% | 1.86 | 13.4% | 0.03% | pp. 10, 14 |
| LAA, UE lag +1 month (fig. 17) | 10.4% | 15.0% | 8.6% | 1.63 | 12.5% | 0.03% | p. 12 |
| QQQ+IWD+GLD+IEF → IEF (fig. 7) | 11.2% | 15.1% | 8.6% | 2.46 | 13.4% | 0.10% | p. 7 |
| LAA-G4 (fig. 16) | 9.5% | 14.6% | 7.5% | 1.85 | 13.4% | 0.03% | p. 11 |
| Benchmark 60-40 SPY-IEF (fig. 2) | 9.5% | 29.5% | 9.0% | 1.02 | 0 | 0 | p. 3 |

LAA RS1 (Oct 2009 – Oct 2019): R 9.5%, D 5.5%, UPI 5.13 vs 60-40 R 10.2%, UPI 6.21 (p. 10).
Robustness: R > 10% and D < 16% for SMA6–12 on UE or SPY; SMA5 on both: R 9.9%, D 20.2% (p. 13).
On average one switch every ~3 years (p. 7).

## Ambiguities and implementation traps

- **UE look-ahead**: the main variant (fig. 12) uses the same month's UE rate at its month end
  (n. 4, p. 1), unavailable in reality; the author acknowledges it (p. 12). Implement with a +1
  month lag and target fig. 17, not fig. 12.
- **Tie at zero**: behaviour if MOM = 0 not specified (inference: strict `> 0` / `< 0` as above).
- **SPY SMA definition**: SMA10 on adjusted or unadjusted price not specified; only the general
  mention "ETF proxies, including the GT's SPY, dividend-adjusted" (p. 2) suggests total return
  (inference).
- **Typos**: IWD and IWF labelled the wrong way round ("Large Cap Growth" for IWD, pp. 2, 5)
  whereas IWD is value (p. 5 correct); "QQQ, IWN, GLD, IEF" p. 9 instead of IWD; IS given once as
  "Feb 1949 – Oct 2019" (p. 3) and "Oct 1981" (p. 5) instead of Jun 1981; reference to a
  non-existent fig. 15 (p. 11); FS UPI quoted 1.83 (p. 12) against 1.86 in the table; "both slow
  trends" for SMA5 (p. 13), read "fast".
- **K25 formula** (n. 9): unclosed parenthesis, `R*(1-2*D/(1-2*D)`; exact form cannot be
  determined here.
- **Rebalancing**: backtest monthly to equal weights, but TTC does not count this rebalancing
  (p. 5) → published turnover understated.
- **Selection bias**: candidate universe chosen by the author; IS 1949–1981 entirely on proxies
  (QQQ pre-1970 = FF HiTech).
