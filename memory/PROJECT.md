# PROJECT.md — decision record

The state of the project as *decisions*, not as narrative. `AGENTS.md` says how to work here;
this file says **why the code is shaped the way it is**, which the code cannot say about itself.

Written for an agent arriving with no prior context. Sections: where things stand, decisions in
force, options rejected (so they are not re-proposed), questions still open (with how confident
the project is about each), and ideas parked.

Dates are the date the decision was taken. A decision without a **criterion** is an opinion;
each one below records what would have to be true to overturn it.

> **This file is public.** Since 2026-10-07 the agent context (`AGENTS.md`, `CLAUDE.md`,
> `SETUP.md`, this file, the skills) is committed with the code. Write it accordingly: no
> balances, no account names, no personal tax or residency situation, no names. "The
> maintainer" decides; the reasoning is what gets recorded.

## 0. Where this stands

**2026-10-07 — the agent context became part of the repository.** It had been gitignored since
2026-08-29 and copied to a private side repository by `tools/backup_context.py`. That split
left the decision record with no history and, once, with no copy inside the project at all. It
is now committed, kept neutral, and the backup tool is retired. *Overturn if:* the context
starts needing personal material to be useful — then that material goes in a separate private
place, not back into an ignored file here.

**2026-10-07 — the paper PDFs left the project.** SSRN's terms allow a personal download, not
redistribution, so the local `academic-papers/` folder is retired. Each strategy has a
paper-side spec in `strategy_specs/` that links its paper; specs also exist for the seven
papers with no implementation (FAA, MAA, MPT, EAA, CAA, LAA, RAA). The specs are the
reference ahead of any other doc. Verifying a disputed rule means downloading the PDF from the
spec's SSRN link, outside the repository.

**2026-10-05 — git is used normally again.** The history was reset to a single commit once, at
publication (2026-08-29); since 2026-10-05 changes are ordinary commits, pushed normally, and
the history is the way back. A single-commit reset is reserved for a specific case (a leak, a
visibility change) and is the maintainer's call. *Consequence:* the "why" can again live in a
commit message, but decisions with a criterion still belong here, because a commit message is
not found by someone reading the code.

**2026-09-23 — the era moved to 2000-01, and `DM_G8_Composite` left the registry.** The
numbers changed with the set of strategies selected, because the shared window depended on
it. The question became how to measure every strategy through a real crisis, uniformly.
Synthetic data and a shorter history were rejected; the chosen route was longer history on
admitted donors.

* **Donors, admitted by a yardstick the market sets.** `common/data_engine.HISTORY_BACKFILL`
  splices an older index mutual fund or a published index (and the LBMA gold fixing, the one
  non-Yahoo source, fetched once into `data/cache/donor_*.csv`) before each ETF's inception.
  *Criterion:* a donor is admissible when it sits no further from its ETF than a SECOND REAL
  ETF of the same asset class does, in 13612U sign agreement — not a threshold chosen for the
  purpose (the first thresholds tried would have failed DBC against GSG). Every donor carries
  its evidence; `tools/proxy_fidelity.py` re-measures it.
  *Overturn if:* a re-measurement moves a donor outside its yardstick pair.
* **`DM_G8_Composite` deleted** (36 -> 35). Its REM leg had no admissible donor: the mortgage
  REITs still listed lost 9% through the GFC where REM lost 52% — survivorship bias, on the
  crisis itself. Kept, it alone held the shared window at 2008-07, and it had never
  distinguished itself. *Known cost, recorded in `strategy_specs/dm.md`:* it was the most
  decorrelated entry (ρ_max 0.705). *Overturn if:* a DAILY mortgage-REIT index without
  survivorship becomes available.
* **Era 2004-11 -> 2000-01; `DATA_START_DATE` 1998-11, derived from it.** All seventeen
  published entries open 2000-01, so no segment is a leaderboard of one. The dot-com bear is
  back: `bear_dotcom`, `contraction_2001`, four new monetary segments, and the `dotcom`
  episode. The 2000-2004 dates were re-derived from FRED (USREC, CPIAUCNS, DFEDTAR) and ^GSPC,
  not typed from memory.
* **A pre-existing defect fixed on the way:** entries measurable before the era opened ONE
  MONTH LATE (the clamp used the era's first day, not the decision before it). Pinned by
  `tests/test_eras.py::TestTheEraOpensOnItsFirstMonth`.
* **The robustness story weakened, and the prose says so.** PBO 34.9% -> 45.5%; family-level
  pooling no longer helps (50.6%); only mechanism-level does (38.0%). "Prefer HAA" is now the
  modal answer, not the stable one. Not decomposed between the new years and the deletion.
* **The leverage tables were re-measured** over 2000-01..2026-08 (`LEVERAGE.md` §§1, 2, 5,
  5.4, 6; README's margin table). The one that changed an argument: full Kelly on SPY fell
  4.49x -> **3.18x** (μ 11.15% -> 7.29%, σ barely moved), so 2x now sits ABOVE half Kelly
  (1.49-1.59x), at two thirds of full, and 3x is roughly AT full Kelly. The margin
  conclusions held in every row (signal-following beats flat; 1.3x buys +0.64..+1.26pp CAGR
  and worsens DD, Sortino and UPI in all six). Sustainable margin at k=3: best 1.30x
  (HAA_G8_Balanced), HAA_G12 1.29x; k=5 admits two entries at 1.02-1.03x. The §8 wrap tables
  are bound by their own products' inceptions and were NOT re-run.

**The Canadian execution layer** (`common/ca_mapping.py`, `common/ca_execution.py`,
`common/live_guards.py`, `tools/fx_rate.py`, `tools/ca_orders.py`, `tools/ca_execution_gap.py`,
`EXECUTION_CA.md`, the offline demonstration in `examples/`). `HAA_G12_CA` is an EXECUTION
layer, deliberately not a registry entry, so it is absent from the GUI by design. Its real book
is the gitignored `ca_execution.json`; `ca_execution.example.json` is fictional. Building the
demonstration found three defects in `build_orders`, each fixed and pinned: a fund leaving the
target sold one unit short (float floor); `prefer_usd_units` converted a CAD-only book to USD
to buy the thinner `.U` classes, contrary to its own comment; and whole-unit rounding was
reported per sleeve as "NOT fully invested", burying real shortfalls.

**The savings projection** (`common/projection.py`, `tools/projection.py`, dashboard
**Projection** tab). The HAIRCUT backtest is the only return source (no typed rate, no raw
CAGR): `SR_used × σ` over the era's cash rate, the record's
demeaned excess resampled for the spread. `margin_sizing.haircut_sharpe` was extracted from
`recommend_leverage` so both read one definition (golden master unmoved). Tax by account type
on user-entered rates, no tax rule in the code; starting balances from `BROKER_ACCOUNTS`. The
tab never copies the example's fictional account kinds onto real accounts: a kind is chosen.
Limits in `KNOWN_GAPS.md` §4 — above all that recentring keeps the sample's SHAPE, so HAA's
shallow record projects near-zero odds of ending below the money put in.
*Overturn if:* a typed return is preferred to the haircut one. The projection is **currency-neutral**: no FX model; amounts are entered in one
declared currency (`PROJECTION.currency`) and also shown in the other at today's USD/CAD, held
constant (`tools/fx_rate.py`; no default rate).

**2026-09-01 — the adjustment-vintage incident.** `PriceStore` had been holding **two
dividend-adjustment vintages spliced at the refresh-window edge**. Momentum across the seam read
too LOW, always in that direction, and it flipped a live HAA canary from alive to dead — a book
would have gone to cash a month early on a number no market produced. Measured over 260
decisions, 10 baskets change (3.8%). Five rounds of QA had missed it, structurally: every test
reads frozen fixtures and every audit reproduced the repo's numbers from the repo's own cache,
so a data layer wrong in a *self-consistent* way was invisible by construction. The response:

1. the vintage splice fixed, per-ticker re-download on restatement;
2. an OFFLINE integrity guard — `f = adj_close/close` can only rise, so a seam is a downward
   step; 37 tickers in 108 ms, no network;
3. the restatement priced in momentum points, and a live run capped so it cannot throttle away
   its own verification;
4. a second-vendor cross-check (`tools/vendor_crosscheck.py`; default source now Nasdaq's
   public quotes, first full run 2026-10-04: 35 of 35 agree);
5. `run_facts.json` — documentation checked against generated numbers;
6. the margin haircut anchored to the registry rather than the run.

**There is no assigned next task.** An arriving agent should expect to be given one. The
standing backlog, in the order the project would take it:

1. **Extend the annotation coverage.** `LEVERAGE.md` carries ~1 500 lines of measured tables
   and only a handful of figures are annotated against `run_facts.json`. The mechanism is
   there; the work is deciding which numbers deserve pinning.
2. **The parameter sweep** (§3) — the largest gap between what this repo reports and what a
   reader may assume. **Do not start it unasked**; it is a research project.

**Do not propose** implementing live leverage deployment, re-raising the `account_balance`
equity-vs-buying-power question, or adding leveraged variants of VAA/PAA. All three are
settled — see §2 and §3.

### What this repository is for

A working engine that produces live monthly signals, **and** a public reference implementation
of Keller's canon. The second purpose shapes real decisions: README and the public docs are
read by strangers evaluating the work, which is why the tone stays factual about defects — the
audits, the vintage incident, `KNOWN_GAPS.md` — rather than promotional. The candour is the
strongest thing the repository has to show. The project deliberately carries **no maturity
label**.

## 1. Decisions in force

### Engine and execution

**Execution is priced at the session AFTER the decision** (2026-07-28).
`EXECUTION_CONVENTION='next_open'` in `common/ledger.py`. A signal computed from a month-end
close cannot be filled at that same close, which is what the pre-rebuild engine did.
*Criterion:* the fill must be reachable by a person acting on the signal. `signal_close`
survives only to reproduce pre-audit numbers — never quote it as a result.
*Measured worth:* ≈ +0.37 pp of CAGR on HAA-G8. An earlier "+2.09 pp" compared a full holding
period against a truncated one and was ~5.6× too large — **do not re-cite it**.

**The execution ledger is an explicit object** (2026-07-28). Before the rebuild, one vectorised
expression silently decided execution price, rebalance date, the meaning of a missing price,
the meaning of cost and the meaning of cash. Five audit findings, one missing abstraction.
*Criterion:* every one of those five must be separately readable and testable.

**`BaseStrategy.sleeves()` is a mandatory explicit declaration** (2026-07-28). It raises; there
is deliberately no inferred default. *Criterion:* the resolver it replaced sniffed five
different attribute names for a strategy's cash bucket and silently returned an empty set for a
strategy that used a sixth. Silence was the defect, so the replacement must refuse rather than
guess.

**Costs are one-way, per leg** (`COST_PCT_PER_SIDE = 0.001`, so an A→B rotation costs 0.2%).
*Criterion:* Keller states 0.1% one-way; the old `TRANSACTION_COST_PCT` key halved it by
construction. It still loads, now meaning twice what it used to.

**The signal is always computed on original (1x) ETFs**; leverage is applied only at execution.
*Criterion:* baking LETF tickers into a signal universe makes the momentum ranking a function
of the leverage product's decay, which is not the strategy anyone published.

### Data

**Pre-inception history is constructed, and fenced** (2026-07-29, extended 2026-09-23 by the
donors in §0). `common/data_engine.py` splices same-index predecessors and builds a **synthetic
BIL from `^IRX`** (discount → bond-equivalent, ACT/360, less BIL's fee). *Criterion:* a
constructed span must end before the real inception, show no step at the junction, and never
reach live sizing — tests enforce this. **SHY was rejected as the cash proxy**: it returned
+6.62% in 2008 against BIL's +1.59%, which would manufacture the crisis result.

**Complete months only, and the daily store is part of the contract.** `load_data(config)`
returns **four** values `(prices, scores_w, scores_u, store)`; `run_backtest(..., store=store)`
raises without it. *Criterion:* execution is priced at the session after the decision, which a
monthly panel cannot express.

**One engine vendor (Yahoo), stamped not assumed.** Provenance hash + `STRICT_GAPS` guard on by
default; a second vendor is consulted only by `tools/vendor_crosscheck.py`, outside the engine.

### Leverage — the subsystem is theoretical preparation, not a deployment plan

**Two independent mechanisms that compose by design** (LETF products × `LEVERAGE_FACTOR`
margin). A 2x LETF strategy at 1.3x margin ≈ 2.6x effective exposure. This is coherent, not a
bug. LETF internal financing is already inside the real price history and is not re-modelled.

**Offence is leveraged, defence is held at 1x** — enforced in code
(`letf_mapper.assert_unlevered_defensive`, called by `run_backtest`). A levered *credit*
product would be admissible in the offensive sleeve; nothing levered is admissible in the
defensive one.

**Leverage homogeneity is a hard rule** (2026-07-28). The whole offensive sleeve must execute at
ONE multiple; canaries and the defensive sleeve are exempt by design.
*Criterion:* an unmapped offensive asset falls through to 1x inside `translate()` and nothing in
the output says so, making effective leverage a function of the monthly signal draw — the
backtest then describes no portfolio anyone holds. Enforced by `LETFMapper.validate_universe()`
**at construction**.

**`MARGIN_FOLLOWS_SIGNAL` defaults to True** (2026-07-28). Borrowing is scaled by the offensive
weight; interest accrues day-counted on what was actually drawn. *Criterion:* LETFs de-lever for
free (rotating UPRO→IEF drops exposure to 1x) while flat margin keeps the loan drawn and buys
the defensive sleeve with borrowed money. *Residual risk not removed:* a margin account can be
called intramonth; an LETF cannot. Set the flag False to reproduce flat-margin results.

**3x entries carry `role='exploratory'`** (2026-07-29): registered, measured and reported in
full, excluded from every selection statistic, barred from setting the ranked window.
*Criterion to promote to `role='strategy'`:* new evidence about **depth**, not shape. ρ ≈
0.996–0.999 against the 2X siblings describes the shape; 4 of 4 measured pairs deepen drawdown
13–22 pp, and no 3x product predates 2008-11, so none has bear-market history.

**Registry admission is a pre-registered structural rule, never read off the leaderboard**
(2026-07-28). An entry is registered only if it is a published universe and parameterisation, or
a G3/G4 size *forced by* what has admissible leverage products — the latter labelled `custom`.
*Criterion:* leveraged variants need not match Keller (they have no author to defer to) but
must be theoretically justified, and *not every model needs a leveraged version*. Admission
rules must be checkable with no returns open.

**Published, reproducible rules only.** Every registered rule traces to a paper, a book or a
published decision tree that anyone can re-derive. A commercial signal service that shows
better numbers without its method is not a benchmark: the usual explanations are leverage
(often near a Kelly fraction, plus crash protection) or the choice of metric (the Martin ratio
flatters frequent rebalancing), and neither can be checked. *Criterion:* a result this
repository cannot reproduce is not evidence here.

**The `Type` column is two independent attributes.** `fidelity` (did anyone publish this?)
requires a `source` citation; `role` (would you hold it?) governs the statistics. A single-asset
degenerate case can be perfectly `faithful` and still be a `control`.

### Analysis layer

**The ranked window is set by `role='strategy'` entries only** (`RANKED_WINDOW_POLICY='strategies'`,
2026-07-29). *Criterion:* letting `custom`/late-arriving entries bind the shared window moved the
headline table to 2010-02 — cross-validating a momentum leaderboard over a window containing no
crisis.

**`common_frame(..., ranked_only=True)`** applies the same principle inside `robustness.py`
(2026-08-01). Admitting every trial let a 2010-starting wrap set the intersection; PBO went from
a flattering 23.6% to an honest 35.9%. *Criterion, stated generally and used repeatedly here:*
**when a correction makes the number worse, the worse number is the honest one.**

**The robustness section nets Sharpes at the run's realised risk-free rate** (2026-08-02,
audit finding AUD-02). `robustness.realised_rf()` resolves it exactly as
`leverage_advice.build_policy` does, and every report block prints the rate it used.
*Criterion:* the ordering being cross-validated must be the ordering being displayed. Netting at
rf = 0 beside a leaderboard netted at ~1.25%/yr shifted each entry by rf/vol — enough to flip
near-ties. (Current PBO figures: §0, 2026-09-23.)

**The claim that survives resampling is "hold a canary-protected family, prefer HAA."** No finer
claim does. Quote it at that granularity, not at the variant level.

**Sizing advice is a band, not a number.** `common/margin_sizing.py` stands *beside* the engine:
`run_ledger` never tests a maintenance requirement and this does not change that. The band's
position is set almost entirely by the safety factor `k` — over the 2000-01 era k=5 admits
almost nothing (1.03x at best), k=3 tops out around 1.30x, k=2 around 1.49x. Quote the band and
the binding cap, never a single figure.
*The leverage frontier brackets it from the other side:* month-end margin calls become material
only near 2.0x while the advice sits at 1.0–1.3x, and the gap **is** the intraperiod factor plus
k×DD_adj. Two methods sharing only `m` and the borrow rate, agreeing from opposite directions.

**Sortino is a same-leverage metric.** It is the best single number for comparing entries at
one leverage level, and insufficient across levels: a 3x entry can out-score its 2x sibling on
Sortino while its drawdown is far deeper and its destruction risk much higher. Across leverage
levels, read Sortino with max drawdown, CAGR, UPI and recovery time (`LEVERAGE.md` §7).
Whether CAGR or a risk-adjusted metric should decide is a property of the investor — what
drawdown they would actually sit through — not of the mathematics.

### Operations and privacy

**All personal settings live in gitignored `user_config.json`** (2026-07-01); `main.py` keeps
documented sanitized defaults via `_UC.get()`; `user_config.example.json` is the committed
template. *Criterion:* the tracked tree must be fully anonymised so that any commit is safe by
construction. **Never put personal values back into `main.py`** — nor into these context files.

**Balances stay out of transcripts.** Because `BROKER_ACCOUNTS` lives in the gitignored
`user_config.json`, code reading it raises no repository issue; the only exposure is a
transcript, a report or a screenshot. That is why every tool that reads balances is verified
with `--demo` or the safe-backtest driver, and why the dashboard's Live tab is never read.

**Live sizing is at 1x with a loud warning, and that is the intended resting state** — not a
stopgap awaiting a "real" implementation.

**Live orders are sized at the latest market quote, not the monthly cache** (2026-07-01). The
monthly panel's adjusted closes are days old and dividend-adjusted; sizing on them oversized
orders and got them rejected by the broker. With a price cap configured, shares are sized **at
the cap** so the broker's funds check passes by construction.

**The engine proposes orders; a person places them.** Execution stays manual until a live track
record shows signals matching the backtest. With twelve decisions a year the main risk of
automation is a script bug acting unseen, not a broker API failure.

**Compute/presentation split.** `size_positions` and `compute_live_signals` return plain data;
`run_live_mode` is the CLI printer and the GUI's Live tab is the other consumer. Keep new engine
features print-free.

## 2. Options rejected — do not re-propose without new evidence

| Rejected | Date | Why |
|---|---|---|
| **Leveraged variants of VAA and PAA** | 2026-07-29 | RULE 4: a wrap may change what is *held*, never what decides to *de-risk*. Both protect by counting breadth over their own offensive universe, so restricting that universe rewrites the protection rule. **Settled, not an omission.** |
| Full-universe wraps (`DAA/VAA/BAA/PAA_Leveraged`) and all G6/G8 sizes | 2026-07-28 | Keller's G12 universes need VGK/EWJ/VWO/VNQ/GSG/HYG/LQD, none of which has an admissible leveraged product — part of the offensive sleeve silently executed at 1x. The few that do have one (EFO/EURL, URE/DRN, UJB) sit under the $100M AUM floor (`LEVERAGE.md` L3). |
| G2 sizes (`*_G2_Leveraged_2X`, SPY + QQQ) | 2026-07-28 | ρ(SPY, QQQ) ≈ 0.91-0.92: a two-asset momentum choice between near-identical assets is not a choice. Their striking pre-rebuild figures came from a defective engine (below) and a US-dominated window. |
| `DAA_G3_Leveraged_2X` | 2026-07-29 | RULE 5: a cash ladder must survive the restriction. It held 2x equity through COVID (−35.1%) because one dead canary rounded to zero de-risking. |
| **A trailing stop on top of the canary** | 2026-06 | Found by an in-sample sweep (7 stop levels × 4 modes, best picked, no out-of-sample test, no theory for why 5%). Keller's and Keuning's designs protect with the canary and the cash rotation alone. A parameter that needs a sweep to find its "optimum" is a fit, not a rule. The code was removed. |
| **Stacking extra canaries or filters** on a published model | 2026-06 | A second filter becomes a veto on the first: false-positive rates multiply, exposure (the source of the momentum premium) falls, and the model stops being the one published. |
| **GMA** — DAA's structure with HAA's TIP canary on a QQQ/EEM/GLD/TLT "macro regime" universe, Top 1 | 2026-06 | Three liberties at once (canary, universe, selection count); it underperformed in the pre-rebuild engine. Later formalised by L5/L6 in `LEVERAGE.md`: each wrap keeps its own family's canary. |
| Manually switching strategy by market regime ("safe model now, levered one after a crash") | 2026-06 | Timing on top of timing: no objective switch signal, the recovery is missed, and the canary already is the regime switch. If a blend is wanted, it must be a fixed systematic allocation. |
| `degradation_slope` in `robustness.py` | 2026-08-01 | Non-monotone in the injected edge (−0.56 null → −0.29 mild → **−1.00 strong**): once one strategy wins every split the regression recovers the identity IS+OOS = 2×full-sample mean and nothing else. Absence is pinned by a test **because it is an obvious thing to add back**. |
| Keuning's "DAA on Steroids" as corroboration | 2026-07-29 | It is 2x on part of the full R12 with UST defensively — not 3x on a reduced universe, and its mixed 1x/2x sleeve breaks RULE 1. He is the counterexample, not the corroboration (`KNOWN_GAPS.md`). |
| Making `SMA13` and `SMA10` "consistent" | 2026-07-29 | BAA n.5 says thirteen prices including the present; **Faber's SMA10 genuinely is 10 prices.** Two different authors, two correct answers. |
| Removing VAA's `> 0` offensive filter | 2026-07-29 | The identical line was a real defect in DAA and is deliberately **left in place** in VAA: provably unreachable at VAA's registered T/B, 0% measured divergence. |
| Date pickers / arbitrary start dates | 2026-07-28 | Replaced by `common/eras.py`: a derived era floor and four exhaustive, disjoint partitions dated by outside bodies (NBER, S&P bull/bear, FOMC, BLS). Choosing a start date is choosing a result. |
| Re-modelling LETF financing cost or decay | — | Already inside the products' real price history. Re-charging it double-counts. |
| Deciding leverage admission from backtest results | 2026-07-29 | Once the numbers exist they will be read, so the admission rule must be structural and pre-registered, or the measurement is contaminated by it. |

**Every figure produced before the 2026-07-28 rebuild is void.** The pre-rebuild engine filled
at the signal close, halved costs, and at one point gave DAA, VAA, PAA and RAA identical
leveraged results because all four ran the same simplified base class. Conclusions drawn from
those runs (G2 "breakthrough" Sortinos, trailing-stop optima, the GMA comparison) survive here
only as the reasons above, never as numbers.

## 3. Open questions

**The parameter sweep — the acknowledged blind spot.** *(High confidence that it matters; not
started.)* PBO measures whether *our* ranking of these entries is stable. The choices made
before the data reached this repository — a 13-month lookback, a top-N, a breadth threshold, all
fitted on these same decades — are **invisible to it**. A low PBO would say "our leaderboard is
reproducible", never "these strategies are not overfitted". Only a sweep that re-runs the engine
across parameter values can address the second claim. **Do not start it without an explicit
request** — it is a research project, not a fix.

**PAA's cash universe: paper §3 vs the BAA restatement.** *(Open, documented in
`strategies/paa.py`.)* The 2016 original and Keller's later restatement disagree. Standing rule:
the original paper governs the entry whose `source` cites it.

**Generate, don't type, every number that prose quotes.** *(Mechanism DONE 2026-09-01 —
`common/facts.py`, `tools/emit_facts.py`, and the `<!-- facts:path:fmt -->` annotation checked by
`tests/test_paper_rules.py`. Coverage partial: LEVERAGE.md is largely unannotated.)*

**The multiple-testing haircut population.** *(AUD-06 — FIXED 2026-09-01: the population comes
from `run_facts.json`, with a loud fallback.)* Selecting 3 entries used to yield a milder
haircut than the full registry, in the flattering direction.

**Whether the maintenance test belongs inside the ledger.** *(Deliberately unresolved.)*
`run_ledger` does not test a maintenance requirement, and `margin_sizing` therefore stands beside
it rather than inside it. Every levered row is bannered accordingly. Moving it inside would make
the ledger's job "simulate a broker", which is a different and much larger contract.

**Leverage deployment.** *(Out of scope, not scheduled.)* The engine sizes live orders at 1x.
The preconditions for ever reconsidering are process maturity rather than a market view: a live
track record of signals matching the backtest, a margin-capable account, and the parameter sweep
above. Registered (tax-sheltered) accounts generally cannot borrow, so there LETFs are the only
leverage available and margin is not. **Do not propose implementing live leverage deployment**,
and do not re-raise whether `account_balance` means equity or buying power — deferred
indefinitely.

## 4. Ideas parked

Not rejected, not scheduled. Each would need to pass the registry admission rule (§1) before a
line of code.

- **TIP as the canary of a leveraged wrap.** HAA's TIP canary is exogenous and never traded, so
  it needs no leveraged product — which is why `HAA_G*_Leveraged_*` pass RULE 4 most cleanly
  (`strategy_specs/haa.md`). Grafting TIP onto another family's wrap is the GMA error above;
  the open question is only whether HAA's own wraps deserve `role='strategy'` status at more
  sizes.
- **A dated reading of a canary death.** Measured over 259 decisions (2005-01..2026-07), the
  HAA TIP canary is dead **24.3% of the time**; the next month's P(SPY < −5%) is 16.1% when dead
  against 7.1% when alive, but the median dead-month return is still positive and the 6-month
  forward return is *higher* after death than after life. Of the 15 worst SPY months, 8 were
  covered and 7 were not — the fast crashes (2020-02/03, 2008-08) happened with the canary
  alive. The two longest dead episodes cost +20.3% and +10.0% of forgone SPY. It is a
  short-horizon risk indicator, not a bear-market forecast. **Do not narrate a canary death as
  a market call.** A tool that prints these statistics beside a live decision is the parked
  idea.
- **A second engine vendor** is not wanted; the cross-check outside the engine is the chosen
  design. Revisit only if Nasdaq's public quotes stop answering.
