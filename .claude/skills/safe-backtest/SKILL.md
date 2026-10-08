---
name: safe-backtest
description: Run a backtest, re-measure a figure, or regenerate a report in this repository without reaching the live path that prints real brokerage account names and balances. Use before ANY measurement, and before running main.py or app.py for any reason.
---

# Measuring safely in keller-strategies

## The hazard

`user_config.json` is gitignored and, on a machine configured for live use, sets `EXECUTION_MODE=True`.
A bare `python main.py` therefore runs in **live signal mode** and prints real brokerage account
names and dollar balances into whatever is capturing output — a terminal, a transcript, a report
file, and from there potentially a commit. The only `main.py` invocation that cannot reach this
path is `--list`.

This is not a theoretical concern: the repository is public, and the tracked tree is deliberately
anonymised so that any commit is safe *by construction*. Printing a balance breaks that property.

## The procedure

**Use the committed driver.** It hard-wires `EXECUTION_MODE=False`, drops `BROKER_ACCOUNTS`, and
asserts both after applying any caller override, so the live path is unreachable rather than
merely avoided.

```bash
venv/Scripts/python.exe -m tools.backtest_driver                  # whole registry
venv/Scripts/python.exe -m tools.backtest_driver HAA_G12 DAA_G12  # named entries
```

For anything more than a glance, import it:

```python
from tools.backtest_driver import run

metrics, results, prices, store, cfg = run()          # or run(['HAA_G12'])
```

`run()` returns `(metrics_data, results, prices, store, config)` and prints no report. Compose it
with the reporting helpers in `main.py` if you need formatted output, or read `metrics_data`
directly — each entry is a dict with `name`, `cagr`, `max_dd`, `sharpe`, `sortino`, `vol`,
`rf_annual`, `returns`, `returns_full`, `in_ranked_window`, `role`, `fidelity` and the sizing
KPIs.

Every parameter is read off `main` rather than copied, so the driver cannot drift into measuring
something the engine no longer does. Override anything except the safety keys:

```python
metrics, *_ = run(['HAA_G12'], LEVERAGE_FACTOR=1.3, RANK_BY='sharpe')
```

## Rules that go with it

- **Never commit `user_config.json`**, and never echo a balance, an account name or a share
  quantity derived from one into any output.
- **The dashboard's Live tab renders real balances.** When verifying `app.py`, stay on the
  Backtest tab; do not screenshot, `read_page` or dump the Live tab into a transcript.
- **`CACHE_REFRESH_HOURS` is set to a year in the driver**, so measurements never re-download
  and are reproducible from the cache. Pass `CACHE_REFRESH_HOURS=0` deliberately if you actually
  want fresh data.
- **Write scratch analysis scripts inside the repo** (or make them derive paths from it). The
  previous incarnation of this driver lived in a scratchpad with an absolute path and broke the
  moment the project directory moved.

## After a change, read more than the CAGR column

Run a real backtest and read the coverage line, the "what was actually traded" table and the
regime panel. Numbers shift legitimately when execution conventions, leverage or defensive
handling change; the manifest saved beside each report records which conditions produced it.
