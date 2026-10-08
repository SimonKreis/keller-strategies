# The prompt that commissions an external audit

Paste this into a *different* model, in a fresh session with the repository attached. Four
audits have been run this way; between them they found the four critical defects that 55
self-consistent tests had all passed against, and two of them also produced findings that
were later refuted on the primary source.

Read `SKILL.md` beside this file **before applying anything the returned report says**.

What makes this prompt work, and is worth preserving if you rewrite it:

- It assigns an adversarial prior ("your default assumption: the code contains bugs"), so a
  clean verdict costs the auditor something.
- It demands one decision cycle traced by hand with the arithmetic shown. Every audit that
  skipped this step returned findings that were reasoning-from-reading, and those are the
  ones that were refuted.
- It requires "checked, clean" to name what was checked — the same rule this repository
  applies to its own guards, where an `ok` that means "I verified nothing" is a defect.
- It forbids assuming a deviation is intentional, which is what surfaced the undocumented
  design choices now recorded in `KNOWN_GAPS.md`.

It has one known blind spot, demonstrated on 2026-09-01: **every audit run from this prompt
reproduced the repository's numbers from the repository's own price cache.** A fixture cannot
disagree with a vendor, so the adjustment-vintage splice survived all four. If you commission
another, add an instruction to check the price panel against something outside the repository
— see `tools/vendor_crosscheck.py`.

---

# Codebase Audit: Keller Quantitative Strategies

## Role
You are auditing a codebase implementing Keller's tactical asset allocation
strategies (e.g. HAA, DAA, BAA family). Act as a skeptical senior quant
reviewer, not a helpful assistant. Your default assumption: the code contains
bugs and the methodology contains silent deviations from the source papers.
Your job is to find them and prove they matter, or prove the implementation
correct.

## Scope: three layers, audit all three
1. **Correctness vs. specification.** Compare the implementation against the
   original Keller papers' rules: momentum formulas (e.g. 13612W weighting),
   canary/protective asset logic, breadth rules, top-N selection, cash
   fraction computation, rebalance timing. Flag every deviation, even ones
   that look intentional, and classify: bug / undocumented design choice /
   documented design choice.
2. **Code quality and hidden bugs.** Look specifically for the classic quant
   pitfalls: look-ahead bias (using data not available at decision time),
   off-by-one in return windows, survivorship bias in the universe,
   dividend/total-return vs price-return confusion, timezone or month-end
   date handling, NaN propagation, silent reindexing/joins that misalign
   dates, float comparison in ranking ties, transaction cost and slippage
   assumptions.
3. **Design and methodology.** Critique architecture choices: data pipeline
   robustness, testability, parameter hardcoding, whether backtest and live
   paths share the same signal code (they must), reproducibility (seeds,
   data snapshots), and whether the backtest results are even trustworthy
   given the above.

## Method (follow in order)
1. Map the repo: entry points, data flow from raw data to orders/weights.
   Produce a short architecture summary first.
2. Trace ONE full decision cycle end-to-end by hand for a specific
   historical date: pull the actual intermediate values (momentum scores,
   rankings, canary state, final weights) and verify each step against the
   paper's rules. Show your arithmetic.
3. Systematically hunt each pitfall from layer 2 above; for each, state
   where you looked and what you found (including "checked, clean").
4. Where feasible, write and run small verification scripts/tests rather
   than reasoning from reading alone. Prefer executed evidence.

## Output format
For each finding:
- **ID + Severity**: Critical (wrong results) / Major (fragile, likely to
  break) / Minor (quality) / Info (design opinion).
- **Evidence**: file, line, and the concrete demonstration (trace, test
  output, or paper citation).
- **Impact**: what results are wrong and by roughly how much, if estimable.
- **Fix**: exact instructions, with code where the change is small; a
  step-by-step plan where it is structural. Do not apply fixes yet.
Finish with: (a) a verdict on whether current backtest results can be
trusted, (b) a prioritized fix order, (c) the 2-3 highest-leverage
structural improvements.

## Rules
- Never assume a deviation is intentional; ask or flag it.
- "Looks fine" requires stating what you checked.
- If you cannot verify something (missing data, ambiguous paper rule), say
  so explicitly instead of guessing.
- Quantify confidence on each non-trivial judgment.
