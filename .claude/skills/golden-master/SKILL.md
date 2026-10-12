---
name: golden-master
description: Decide whether a moved number is a regression or an intended change, and regenerate the pinned golden-master metrics legitimately. Use when tests/test_golden_master.py fails.
---

# When the golden master fails

`tests/test_golden_master.py` pins 8 strategies × 6 metrics over a frozen daily fixture. **It
fails on purpose when a number moves.** The failure is information, not an obstacle, and the one
forbidden response is regenerating it to make the suite green.

## 1. Decide which kind of change this is

Ask what in the pipeline could have moved the number, and confirm it against the change you just
made:

- **Intended** — you changed an execution convention, a cost, the leverage handling, a defensive
  rule, a data splice, or a paper rule. The metrics *should* move, and by roughly the amount you
  can account for.
- **Regression** — you changed reporting, refactored, touched the analysis layer, or edited docs.
  Those must not move engine metrics at all. The audit-fix work of 2026-08-02 rewrote three
  published PBO figures and left the golden master **unmoved**, which is exactly the expected
  signature of a change confined to the analysis layer.

If you cannot explain the direction *and* the rough magnitude, treat it as a regression and find
the cause. "The test was stale" is not a diagnosis.

## 2. Check what else should have moved

A genuine engine change usually shows up in more than one place. Run a real backtest through
`.claude/skills/safe-backtest/SKILL.md` and read the coverage line, the traded table and the
regime panel — not only the CAGR column.

## 3. Regenerate, if and only if the change is intended

```bash
venv/Scripts/python.exe -m tests.test_golden_master --record
```

Then:

- **Commit the regenerated JSON in the same commit as the change that moved it.** A golden master
  updated in its own commit is a golden master nobody can audit.
- **Append an entry to the JSON's `history` array** saying what moved and why. That array is the
  record of why a pinned number is what it is that travels with the number itself.
- Re-run the full suite: `venv/Scripts/python.exe -m unittest discover -s tests` and compare the
  count with the one `AGENTS.md` states.

## 4. What the golden master cannot tell you

It says a number moved; it cannot say which rule is right. That is the job of
`tests/test_paper_rules.py` (each family against its published rule) and `tests/test_anchors.py`
(against hand arithmetic and closed forms computed in the test file). If a paper rule is in
question, the golden master is the wrong instrument — go to the spec in `strategy_specs/` and see
`.claude/skills/audit-response/SKILL.md`.
