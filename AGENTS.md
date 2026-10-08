# AGENTS.md — Keller Strategies

Guidance for AI agents working in this repository.

## Start here (read in this order)

1. This file — conventions, invariants, commands, traps.
2. [`SETUP.md`](SETUP.md) — what to install and configure before running anything.
3. [`memory/PROJECT.md`](memory/PROJECT.md) — the decision record: what was decided, on what
   criterion, what was rejected and why, and what is still open. It is the file that answers
   "why is it like this", which the code cannot.
4. [`KNOWN_GAPS.md`](KNOWN_GAPS.md) — **before quoting any number to anyone.**

> ### ⚠️ Three things that will bite you first
>
> **1. Never run `main.py` bare.** `user_config.json` (gitignored, present on any machine
> configured for live use) sets `EXECUTION_MODE=True`, so a bare `python main.py` runs in **LIVE mode and
> prints real brokerage account names and dollar balances**. For any measurement, use a
> backtest-only driver with `EXECUTION_MODE=False` and no `BROKER_ACCOUNTS` — the procedure
> is `.claude/skills/safe-backtest/SKILL.md`, and it exists because this output has to stay
> out of transcripts, reports and commits. Never commit `user_config.json`; never echo a
> balance into any output.
>
> **2. This file is public.** Since 2026-10-07 `AGENTS.md`, `CLAUDE.md`, `SETUP.md`,
> `memory/PROJECT.md` and the skills are committed with the code. Write them so that any
> commit stays safe: no balances, no account names, no personal tax or residency situation, no
> names. Personal values live only in the gitignored `user_config.json` and `ca_execution.json`.
>
> **3. Put the "why" in a file.** Git is used normally (ordinary commits since 2026-10-05; the
> history before that was reset to one commit at publication). A decision with a criterion
> still belongs in `memory/PROJECT.md`, because nobody reading the code finds a commit
> message. The harness's own memory directory is keyed by the project's PATH and is orphaned
> by every move, so durable knowledge never goes there.

## What this is

A quantitative **Tactical Asset Allocation (TAA) backtesting engine** implementing
Dr. Wouter Keller's canon (HAA, DAA, VAA, BAA, PAA) plus a custom four-module dual-momentum
sleeve, Faber's GTAA, and leveraged-ETF variants. 35 registered variants, each labelled
`faithful` / `proxy` / `custom` / `control` / `benchmark` in the report.

> The engine was rebuilt on 2026-07-28 around an explicit execution ledger, after an
> adversarial audit found that execution, cost, cash, the rebalance date and the meaning of a
> missing price were all implied by a single vectorised expression. Two further audits on
> 2026-07-29 found two Keller-compliance defects that had survived it — see
> `tests/test_paper_rules.py`, which exists so that class of defect cannot survive again.
> **[`KNOWN_GAPS.md`](KNOWN_GAPS.md) is the standing list of what the engine still cannot
> establish, and now the only record of what the audits found — read it before quoting any
> number.**

- **Language:** Python 3.11+ (`requirements.txt`: pandas, numpy, yfinance, matplotlib, nicegui;
  `requirements.lock` pins the exact environment that produced the current numbers)
- **Data:** Yahoo Finance via `yfinance`, **daily** bars cached to `data/cache/daily_*.csv`,
  from 1998-11. Before each ETF's inception the store splices an admitted DONOR (an older
  index mutual fund or a published index; the LBMA gold fixing for GLD, cached in
  `data/cache/donor_*.csv`) — `common/data_engine.HISTORY_BACKFILL`, re-measurable with
  `tools/proxy_fidelity.py`. Every published strategy is measured from **2000-01**.
- **Vibecoded origin:** prefer validating behavior by running code over assuming from names.

## How to run

```bash
pip install -r requirements.txt
python main.py                 # ⚠️ MAY RUN LIVE — see the warning above, use a driver instead
python main.py --live          # force live signal mode (prints real balances)
python main.py --list          # list all available strategy keys (always safe)
python main.py --strategy HAA_G12 DAA_G12   # run specific strategies
python app.py                  # NiceGUI desktop dashboard (Backtest, Projection, Live tabs)
```

`--list` is safe. Everything else that loads `user_config.json` can reach the live path on
a configured machine: to measure anything, use the backtest-only driver from
`.claude/skills/safe-backtest/SKILL.md`. The dashboard's **Live tab displays real balances**
— when verifying the GUI, stay on the Backtest tab and avoid `read_page`/screenshots of the
Live tab.

All user-facing knobs are **documented with defaults** in the USER DASHBOARD block at
the top of `main.py` and **overridden per key by `user_config.json`** (gitignored —
holds the user's personal values: broker balances, strategy picks, dates, leverage;
template in `user_config.example.json`). Never put personal values back into `main.py`.
Precedence for strategy selection: CLI `--strategy` > `user_config.json` `STRATEGIES`
> the `STRATEGIES_TO_RUN` catalog.

## Architecture (3 layers)

```
DATA      common/data_engine.py     PriceStore — DAILY bars, real trading dates, complete
                                    months only, provenance hash, adjustment-vintage check
SIGNAL    strategies/*.py           momentum/canary logic → weights on ORIGINAL ETFs
EXECUTION common/ledger.py          fill date, fill price, drift, per-leg cost, cash
                                    account, margin and day-counted interest
GUARDS    common/coverage.py        from when a strategy can honestly be measured
REPORTING main.py + common/         metrics (incl. UPI), regimes, selection stats, manifests
SIZING    common/margin_sizing.py   sustainable MARGIN leverage from a model's KPIs. Stands
                                    BESIDE the engine, not inside it: run_ledger never tests a
                                    maintenance requirement, and this does not change that
          common/leverage_advice.py the driver for it — broker assumptions, trial count, one
                                    recommendation per metrics row. Feeds the report's
                                    SUSTAINABLE MARGIN LEVERAGE section and the GUI column
DOUBT     common/robustness.py      how much of the leaderboard survives a different sample:
                                    PBO by CSCV (deterministic, no seed), the ranking rebuilt
                                    on joint stationary-bootstrap resamples, both POOLED by
                                    family and by de-risking mechanism, and the LEVERAGE
                                    FRONTIER — the same resampled histories walked at
                                    constant margin, cross-checking CAP 1 from an
                                    independent direction. Answers "how much of rank 1 is
                                    search", NOT "what happens next"
PROJECT   common/projection.py      savings carried forward on the HAIRCUT record, after tax
                                    by account type — the one forward-looking computation,
                                    an assumption printed as one (KNOWN_GAPS.md §4)
UI        app.py (NiceGUI)          thin GUI over main.load_data / run_backtest /
                                    compute_live_signals — no strategy logic
```

`load_data(config)` returns **four** values: `(prices, scores_w, scores_u, store)`. The store
is part of the contract because execution is priced at the session *after* the decision, which
a monthly panel cannot express. `run_backtest(..., store=store)` raises without it.

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full model.

Compute/presentation split: `size_positions` and `compute_live_signals` return plain
data structures (orders, warnings, canary states); `run_live_mode` is the CLI printer
and the GUI's Live tab is the other consumer. Keep new engine features print-free.

Live sizing prices: the monthly signal decides WHAT to hold, but live-mode share
quantities are sized at the latest market quote (`get_live_prices`, raw Close), with
loud fallback to the month-end close when offline. Never size live orders on the
monthly cache alone — its adjusted closes can be days old and dividend-adjusted,
which oversizes orders and gets them rejected by the broker.

Key invariant: **the signal is always computed on original (1x) ETFs.** Leverage is
applied only at execution — never bake LETF tickers into a signal universe.

## How leverage works (important — two independent mechanisms)

1. **Leveraged ETFs (2x/3x):** realized through the *real* price history of products
   like UPRO/TQQQ/TMF (mapping in `common/letf_mapper.py`). Their internal financing
   cost and volatility decay are already in those prices — do not re-model them.
2. **Margin (`LEVERAGE_FACTOR`):** borrowed money (brokerage margin / credit line)
   applied to active strategies' returns. `MARGIN_BORROW_RATE` charges interest on the
   borrowed portion. The two compose: a 2x LETF strategy at `LEVERAGE_FACTOR=1.3` ≈ 2.6x
   effective exposure.

**`MARGIN_FOLLOWS_SIGNAL` (default True) — margin de-levers with the signal.** LETFs
de-lever for free: rotating from UPRO into IEF drops exposure to 1x. Flat margin does not
— the loan stays drawn, so the defensive sleeve is bought with borrowed money and the
portfolio rides the drawdown levered. With the flag on, borrowing is scaled by the
offensive weight:

```
effective_leverage_t = 1 + (LEVERAGE_FACTOR - 1) x offensive_weight_t
interest             = debt_actually_drawn x rate x days / 365   (settled each rebalance)
```

so the offensive contribution is levered, the defensive contribution is not, and interest
accrues only on what was actually drawn — day-counted, not a flat monthly twelfth.

`BaseStrategy.offensive_weight()` / `defensive_mask()` resolve the sleeve split from each
strategy's **`sleeves()` declaration**. They no longer infer anything: the attribute-sniffing
resolver they replaced looked for five different names for a strategy's cash bucket and
silently returned an empty set for a strategy that used a sixth. Dual-role assets (TLT/DBC/LQD
in BAA, IEF in HAA) are resolved by the canary and default to **offensive** when there is no
canary — never claim de-escalation the signal cannot prove.

One subtlety worth knowing: a *deliberate* cash-ticker holding follows the mode's rule (flat
margin stays drawn through it), while only the **uninvested residue** is always unlevered.
Forcing both to 1x made "flat" not flat and blurred the very A/B this flag exists to make. Set
the flag to False to reproduce flat-margin results.

Design rules baked into the code:
- **Offence is leveraged, defence is held at 1x.** `letf_mapper.translate()` maps the
  offensive sleeve to LETFs and passes unmapped (defensive) assets — IEF/SHY/BIL/BND/
  LQD/HYG/TIP — through at 1x on their own ticker, so defensive months earn the real
  bond/cash return rather than 0%.
- **Passive benchmarks (SPY_Benchmark, Golden_Butterfly) run at 1x** — they are a
  clean reference and are excluded from margin leverage.
- **The offensive sleeve must execute at ONE uniform multiple.** A universe that lands
  partly on 3x products and partly on 2x products (or on unleveraged originals) has an
  effective leverage that drifts with the monthly signal draw, so the backtest stops
  describing the portfolio held. `LETFMapper.validate_universe()` enforces this and is
  called from every leveraged strategy's constructor — an inadmissible universe raises
  at construction rather than failing silently at execution. The defensive sleeve and
  the canaries are deliberately exempt: defence is held at 1x by design.

## Leveraged variants — all use the wrap pattern

Every leveraged variant subclasses its canonical strategy, runs that exact signal, then
calls `LETFMapper.translate(...)`. No separate simplified signal logic exists.

- **Sized variants** in `strategies/*_leveraged.py` apply the canonical algorithm to a
  restricted universe that is fully executable at one ratio. These sizes were never
  defined by Keller — they are custom universes, but the signal math is the faithful one.

  | Universe | Assets | Admissible ratios | Registered |
  |---|---|---|---|
  | G2 | SPY, QQQ | 2x, 3x | **deleted 2026-07-28** — ρ(SPY, QQQ) ≈ 0.92 |
  | G3 | SPY, QQQ, IWM | 2x, 3x | 2x as `strategy`, 3x as `exploratory` |
  | G4 (2x) | SPY, QQQ, IWM, GLD | 2x only — no 3x gold product exists | 2x as `strategy` |
  | G4 (3x) / G5 | + EEM and/or TLT (both 3x-only tickers) | 3x only | 3x as `exploratory` |

  NAMING HAZARD: `G{n}` counts offensive assets, and at n=4 the admissible universe DIFFERS
  BY RATIO (`*_G4_Leveraged_2X` ends in GLD; `BAA_G4_Leveraged_3X` ends in EEM). Read the
  factory, not the key — the full ladder is documented in `strategies/haa_leveraged.py`.
  The same label also differs between 1x and leveraged entries: `DAA_G4` is Keller's R4
  (SPY, VEA, VWO, BND) while `DAA_G4_Leveraged_2X` is SPY, QQQ, IWM, GLD. That is
  intentional — a leveraged universe holds only assets with admissible products — and an
  earlier audit flagged it as a bug. Do not.

  **2x entries are `role='strategy'`; 3x entries are `role='exploratory'`** — registered,
  measured and reported in full, excluded from every selection statistic and barred from
  setting the ranked window (`strategies/base.py`). The registry WAS all-2x from 2026-07-28
  to 2026-07-29; the 3x entries were then admitted under this role because ρ ≈ 0.996-0.999
  against the 2X siblings describes the SHAPE and says nothing about the DEPTH — 4 of 4
  measured pairs deepen drawdown 13-22 pp — and no 3x product predates 2008-11, so none has
  bear-market history. Do not promote a 3x entry to `role='strategy'` without new evidence.

- `DM_G3_Leveraged_2X` is a single-module dual-momentum sleeve (relative + absolute vs the
  BIL T-bill return) on `{SPY, QQQ, IWM}` — a universe chosen by what has 2x products, hence
  `custom`. It is a different object from `DM_G8_Composite` (deleted 2026-09-23), which
  was Antonacci's published four-module portfolio.
- **Full-universe wraps were removed** (`DAA_Leveraged`, `VAA_Leveraged`, `BAA_Leveraged`,
  `PAA_Leveraged`, the four-module DM wrap) along with the G6/G8 sizes. Keller's G12 universes need
  VGK/EWJ/VWO/VNQ/GSG/HYG/LQD, none of which has an admissible leveraged product, so part
  of their offensive sleeve silently executed at 1x. Do not reintroduce them.

## Conventions

- The `strategy_specs/` files are the source of truth for strategy logic, ahead of any other
  doc; each links its SSRN paper (the PDFs are not kept in the repo or
  beside it). Check an implementation against its spec.
- **Execution is priced at the session AFTER the decision** (`EXECUTION_CONVENTION='next_open'`,
  `common/ledger.py`). A signal computed from the month-end close cannot be filled at that same
  close, which is what the pre-audit engine did. Measured worth of the difference: ≈ +0.37 pp of
  CAGR on HAA-G8, up to +0.87 pp levered. (An earlier +2.09 pp figure compared a full holding
  period against a truncated one and was ~5.6x too large; see `KNOWN_GAPS.md` §7.)
  `signal_close` still
  exists as a convention, purely to reproduce pre-audit numbers; never quote it as a result.
- **Every new strategy MUST implement `sleeves()`** returning
  `{'offensive': set, 'defensive': set, 'canary': list}`. `BaseStrategy.sleeves()` raises;
  there is deliberately no inferred default. A leveraged wrap must declare the **LETF images**
  it actually holds, not the 1x signal assets — mix in `LeveragedWrapMixin` and it is handled.
  This replaced a resolver that sniffed five attribute names and silently returned an empty
  set for a strategy that used a sixth.
- **Costs are one-way, per leg.** `COST_PCT_PER_SIDE = 0.001` means a full A→B rotation costs
  0.2% of notional. The old `TRANSACTION_COST_PCT` key still loads, with the same value now
  meaning twice what it used to.
- **The daily cache re-checks Yahoo at most every `CACHE_REFRESH_HOURS` (default 6).** It
  used to re-download a 90-day window of every ticker on EVERY run — 9.1s and a ~10MB CSV
  rewrite, to learn nothing, because the only guard compared the newest bar against the
  calendar date and that is false all day. A skipped refresh is printed in the report
  header, never silent. `--refresh` or `CACHE_REFRESH_HOURS=0` forces it.
- Don't refactor purely for style. Prefer targeted bug fixes and well-scoped features.

## Verifying changes

```bash
venv/Scripts/python.exe -m unittest discover -s tests    # expect: Ran 762 tests ... OK
```

Measured 2026-10-04 on `venv/Scripts/python.exe` (3.14.6, pandas 3.0.3, numpy 2.5.0,
nicegui 3.14.0): **762 tests, OK** (510 on 2026-08-29; the Canadian execution layer, its
order driver, the 2000-era history extension and the savings projection, the dashboard table tests and the execution-gap report added the rest). Use the venv interpreter, not a bare `python` — a
2026-08-19 measurement of "421 tests, 1 load error" was an interpreter without `nicegui`,
which silently drops the 56 tests in `tests/test_dashboard_render.py`. If your count is not
762, check `SETUP.md` before believing the number: a missing optional dependency here removes
tests rather than failing them.

There is **no build step, no linter and no type checker** configured — do not go looking for
one. `python -m compileall common strategies tools main.py app.py` is the closest thing to a
syntax gate, and the test suite is the real one.

Deterministic and network-free. Three things it checks that are worth knowing about:

1. **Golden master** (`tests/test_golden_master.py`) pins 8 strategies × 6 metrics over a
   frozen daily fixture. If your change moves a number, this fails **on purpose**. Regenerate
   with `python -m tests.test_golden_master --record` and commit the JSON *in the same commit
   as the change*, with a new entry appended to its `history` array. Never regenerate it to
   make a test go green.
2. **Guards** (`tests/test_guards.py`) assert what the engine must REFUSE: an incomplete
   month, a window predating a strategy's own products, weights that do not sum to 1, a held
   ticker with no price, a data gap longer than 5 trading days, a canary reading bullish on
   NaN.
3. **Paper rules** (`tests/test_paper_rules.py`) compare each family's allocations against
   its published rule, re-derived on hand-built panels. This file exists because two
   Keller-compliance defects survived two audits and 131 self-consistency tests. The
   standard it must meet is stated in its docstring: change `rolling(13)` to `rolling(9)`,
   drop DAA's cash slots, swap 13612W for 13612U, invert a BAA canary comparison — each has
   to break an assertion THERE. A golden master can only say a number moved; it cannot say
   which rule is right.
4. **Anchors** (`tests/test_anchors.py`) compare against things the code did not produce:
   momentum scores derived from a closed form in the test file, HAA baskets worked out by
   hand, Keller's stated 0.1% one-way cost expressed as arithmetic, the HAA paper's published
   result shape as a sanity band, and the registry count.

That third category is the point. Before 2026-07-28 all 55 tests asserted `f(x) == f(x)`, and
every one of them passed against an engine with four critical defects. **A new test that only
compares the code to itself adds coverage but no assurance.**

After a change also run a real backtest and read the coverage line, the "what was actually
traded" table and the regime panel — not just the CAGR column. Numbers shift legitimately when
execution conventions, leverage or defensive handling change; the manifest beside each saved
report records which conditions produced it.

## Known traps (each one cost a session)

- **Re-derive a number before writing it into a permanent doc.** Three figures carried across
  a context compaction in prose were wrong when re-measured (a Kelly optimum off by 0.7x, an
  inverted volatility comparison, and a published design attributed to an author who never
  published it). A summary preserves conclusions but not the convention that produced them.
  State the convention inline and cross-check against something the engine already prints.
- **Verify an external audit before applying it.** Findings must be checked against the code
  *and* against the spec in `strategy_specs/` (and the SSRN paper it links, downloaded on demand). Of three external audits, two contained
  findings that were refuted on the primary source — and the original paper governs the entry
  whose `source` cites it, not a later restatement by the same author. Refusing an audit
  recommendation is fine when the refusal is evidenced; the procedure is
  `.claude/skills/audit-response/SKILL.md`.
- **Prose that quotes a count is a cache, and caches go stale.** The registry size has drifted
  out of the docs five separate times, once within a day of the test that was supposed to pin
  it. `tests/test_paper_rules.py::TestDocsQuoteTheRegistrySize` now pins four phrasings across
  four documents — **if you rename or add a doc, update its `DOCS` tuple**, which is exactly
  the failure that greeted this handoff (`AGENTS.md` was renamed to `CLAUDE.md` and two tests
  went red).
- **`python -m unittest discover -s tests -t .` fails** with "Start directory is not
  importable". The working command is `discover -s tests`, nothing more.
- **Do not `grep -r` from the repo root** — `venv/` is enormous and shell greps time out. Use
  the agent's own search tool, or exclude `venv/`.
- **The scratchpad drivers are not portable.** Any helper written outside the repo hardcodes
  an absolute path, and the project directory has moved four times. Derive paths from the
  repo, or keep the driver inside it — `tools/backtest_driver.py` is the committed one.
- **Never put a module constant in a default argument.** `def f(path=SOME_CONST)` binds the
  VALUE at import, so `patch.object(module, 'SOME_CONST', ...)` leaves `f` reading the real
  one — and a test written that way believes it is isolated while it is not. This bit three
  times in a single day (2026-09-01): `vendor_crosscheck.crosscheck`, its `main` resolving
  through `PROVIDERS`, and `leverage_advice.registry_trial_population`. In the first case the
  test opened a real socket and the vendor answered. Resolve the default INSIDE the function
  (`path = path or SOME_CONST`), and where the stakes are isolation, add a module-wide lock
  that makes the escape an error rather than a slow test.
- **Always pass `encoding='utf-8'` to `subprocess` on this project.** `text=True` alone decodes
  with the platform codec — cp1252 on Windows — which cannot decode bytes `0x81/0x8D/0x8F/
  0x90/0x9D`. A single emoji variation selector anywhere in `git diff` output was enough to
  raise inside subprocess's reader thread, get swallowed by a broad `except`, and make
  `manifest.git_state` report a **modified worktree as clean with no diff hash** (found and
  fixed 2026-08-29, pinned by `tests/test_guards.py`). Note the shape of that bug, not just
  the fix: a guard that fails *open*, in the permissive direction, in silence.

## Key documentation

- `KNOWN_GAPS.md` — **read this before quoting any number.** What the engine cannot establish,
  what it does not model, and the eight findings deleted with their code rather than fixed.
- `memory/PROJECT.md` — the decision record: active decisions with their decision criterion,
  rejected options with the reason, open questions with a confidence level.
- `SETUP.md` — environment, dependencies, configuration, and what must exist outside the repo.
- `ARCHITECTURE.md` — module layout and the execution model
- `LEVERAGE.md` — leverage rationale, measured: Kelly (§1), volatility decay (§2),
  lifecycle investing (§4), LETFs vs margin (§5), the canary's effect (§6), 3x destruction
  risk (§7), which families admit a wrap (§8) and every liberty taken (§9). Start there
  for any leverage question.
- `EXECUTION_CA.md` — HAA_G12 executed in Canadian-listed funds (`tools/ca_orders.py`). An
  execution layer, NOT a registry entry. Its real book is the gitignored `ca_execution.json`;
  never run the driver against it in a transcript — it prints real balances, like `--live`.
  `tools/ca_execution_gap.py` measures each Canadian fund's drift from its US ETF (public
  prices only, no book); its figures live in `EXECUTION_CA.md`.
- Savings projection (`tools/projection.py`, `common/projection.py`) — `BROKER_ACCOUNTS`
  carried forward with contributions, tax by account type and inflation, on the haircut
  record (`margin_sizing.haircut_sharpe`), never the raw CAGR. Its limits are in
  `KNOWN_GAPS.md` §4. It prints the starting balances, so verify it with `--demo`.
- `WHY_TAA.md` — the case for tactical asset allocation
- `TIMELINE.md` — evolution of TAA from Faber to Keller
- `strategy_specs/` — one paper-side spec per strategy, implemented or not, indexed in
  `strategy_specs/README.md`. The reference for any rule, ahead of every other doc.
- `.claude/skills/` — validated repeatable procedures (safe backtesting, audit response,
  golden-master regeneration). Mirrored at `.agents/skills/` for non-Claude harnesses; edit
  both copies together.
- `tools/vendor_crosscheck.py` — the second opinion on the price panel. Lives in `tools/`
  and NOT in `tests/` on purpose: `unittest discover` collects every `test_*.py`, and the
  only way to guarantee the suite never opens a socket is to keep the networking code out
  of the directory it scans. Default source: Nasdaq's public historical quotes (Stooq has
  gated automated access since 2026-09-01). First full run, 2026-10-04: 35 of 35 agree.
  `unavailable` never counts as agreement.
