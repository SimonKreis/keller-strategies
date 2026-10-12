# SETUP.md

Everything that must exist **outside** the repository before the code runs, and the commands to
put it there. If you are an agent arriving on a fresh clone, this is the second file to read
after `AGENTS.md`.

## 1. Interpreter and dependencies

Python **3.11+**; the environment the current numbers were produced with is **3.14.6**.

```bash
python -m venv venv
venv/Scripts/python.exe -m pip install -r requirements.txt      # Windows
# python -m venv venv && venv/bin/python -m pip install -r requirements.txt   # POSIX
```

`requirements.txt` carries the floors (and explains why `pandas>=2.2` is a floor and not a
preference — `pct_change` forward-filled across gaps through 2.1, which resurrects a delisted
product's last price into a live momentum score). `requirements.lock` pins the exact versions
that produced the published figures; install from the lock when reproducing a number.

**Use the venv interpreter explicitly.** A bare `python` may resolve to an interpreter without
these packages, and the failure mode is quiet: `nicegui` missing removes the 56 tests in
`tests/test_dashboard_render.py` from the run rather than failing them, so the suite reports
~421 tests and still says `OK`. **The correct count is 762** (2026-10-04).

`pywebview` is optional and only affects the dashboard's native window; without it the GUI opens
in a browser.

## 2. Configuration

| File | Tracked? | Purpose |
|---|---|---|
| `user_config.example.json` | yes | Template. Copy it to start. |
| `user_config.json` | **no — gitignored** | All personal values: brokerage balances, strategy picks, leverage, sizing knobs. |
| `.claude/launch.json` | yes | Dashboard launch target for agent harnesses. |
| `.claude/settings.local.json` | **no — gitignored** | One machine's permission grants. Not needed to work here. |

```bash
cp user_config.example.json user_config.json     # then edit
```

Without `user_config.json` the loader falls back to the documented defaults in `main.py`; a
**malformed** file exits rather than guessing. Precedence for strategy selection:
CLI `--strategy` > `user_config.json` `STRATEGIES` > the `STRATEGIES_TO_RUN` catalog.

> ### ⚠️ `user_config.json` is why you must not run `main.py` bare
>
> On a machine configured for live use it sets `EXECUTION_MODE=True`, so `python main.py` runs in **live mode
> and prints real brokerage account names and dollar balances**. Use the backtest-only driver in
> `.claude/skills/safe-backtest/SKILL.md` for every measurement. Never commit this file, and
> never echo its values into a report, a transcript or a commit.

## 3. Data

No credentials and no API keys. Market data comes from Yahoo Finance through `yfinance`, cached
as daily bars in `data/cache/daily_*.csv` (gitignored). The first run downloads; afterwards the
cache re-checks Yahoo at most every `CACHE_REFRESH_HOURS` (default 6), and a skipped refresh is
printed in the report header rather than being silent. Force it with `--refresh` or
`CACHE_REFRESH_HOURS=0`.

The test suite is **deterministic and network-free** — it never touches Yahoo, so it works
offline on a fresh clone with no cache at all.

## 4. External services

**None.** There is no `.mcp.json`, no MCP server dependency, no environment variable to set, no
account to create. If tooling prompts you to authenticate a connector, it is unrelated to this
project.

`tools/vendor_crosscheck.py` reaches a second market-data vendor, and that is still true of it:
it needs no key and no account. It is also the only code here that talks to anyone but Yahoo, it
is never imported by the engine or by the test suite. Its default vendor is Nasdaq's public
historical quotes (Stooq has gated automated access since 2026-09-01); an unreachable ticker
reports `unavailable`, never agreement. Read its module header before trusting a clean run.

## 5. Verify the install

```bash
venv/Scripts/python.exe -m unittest discover -s tests    # expect: Ran 762 tests ... OK
venv/Scripts/python.exe main.py --list                   # safe: prints the 35 strategy keys
```

`--list` is the only `main.py` invocation that cannot reach the live path. If the test count is
not 762, a dependency is missing — re-read §1 before trusting any number the engine prints.
