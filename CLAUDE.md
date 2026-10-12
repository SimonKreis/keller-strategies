# CLAUDE.md

**Read [`AGENTS.md`](AGENTS.md).** It is the master guide for this repository — conventions,
invariants, commands, architecture and known traps. This file holds only the parts that are
specific to Claude Code, so that nothing is duplicated and nothing can drift out of sync.

## Claude Code specifics

- **Skills** live in `.claude/skills/` and are committed (mirrored in `.agents/skills/`; edit
  both). Load one before doing the thing it describes:
  - `safe-backtest` — measure anything without reaching the live path. **Read it before your
    first run**; a bare `main.py` prints real brokerage balances.
  - `audit-response` — how to handle an external audit report. `audit-prompt.md` beside it is
    the prompt that commissions one, and names the blind spot every audit so far shared.
  - `golden-master` — how to legitimately regenerate the pinned metrics.
  The same procedures are mirrored in `.agents/skills/` for other harnesses.
- **`.claude/launch.json`** is committed. It defines the
  `dashboard` target (`venv/Scripts/python.exe app.py --browser`, port 8080) for harnesses
  that drive a browser preview. When verifying the dashboard, stay on the **Backtest** tab:
  the Live tab renders real account balances and must not be screenshotted or read into a
  transcript.
- **`.claude/settings.local.json`** is personal and stays gitignored. It is not needed to work
  on this project; the permissions it grants are conveniences, and two entries in it are stale
  (a `pytest` invocation — this project uses `unittest` — and a `scipy` import check — scipy is
  not a dependency).
- **No MCP servers are required.** There is no `.mcp.json` and the project depends on none.
  If a tool asks you to authenticate a connector, it is unrelated to this repository.
- **Memory.** Durable project knowledge belongs in `memory/PROJECT.md` **inside the repo**, not
  in the harness's private memory directory. It is keyed by the project's path, so every move
  orphans it. `memory/PROJECT.md` is public: keep it free of personal data.
