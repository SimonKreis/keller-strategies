---
name: audit-response
description: Handle an external audit or QA report on this repository — verify each finding against the code and the SSRN papers before applying anything, and record refutations. Use whenever someone supplies an audit, review or QA document about this codebase.
---

# Responding to an external audit

Four external audits have been run against this repository, all four commissioned with
`audit-prompt.md` beside this file. **Two contained findings that were refuted** on the
primary source. Applying an audit without verification has already come close to
introducing defects on the authority of a confident document.

## 1. Verify before applying — every finding, individually

For each finding, establish three things and write them down:

1. **Does the cited code say what the audit says it says?** Open the file at the cited line. One
   audit cited documentation lines that stated the *opposite* of its claim; another fabricated its
   environment baseline (every dependency version wrong — it claimed Python 3.11/pandas 2.2
   against the real 3.14/3.0.3).
2. **Does the primary source agree?** For anything touching a strategy rule, `fidelity` label or
   momentum convention, check the spec in `strategy_specs/` first, then download the SSRN PDF it
   links into a scratch directory **outside the repo** and quote it verbatim:

   ```bash
   venv/Scripts/python.exe -c "import pypdf,sys; r=pypdf.PdfReader(sys.argv[1]); print(r.pages[6].extract_text())" <path-to-downloaded.pdf>
   ```

   **The original paper governs the entry whose `source` cites it** — a later restatement by the
   same author does not. This exact distinction refuted a finding about PAA: its rule was derived
   from Keller's 2022 restatement in BAA rather than the 2016 original, whose recipe step 2 says
   "only the n good assets (with positive momentum)".
3. **Is the same-looking code in another family the same defect?** It often is not. An identical
   `> 0` filter was a genuine defect in DAA and is deliberately correct-to-leave in VAA
   (unreachable at VAA's registered parameters, 0% measured divergence). Decide each family on its
   own primary source.

## 2. Measure the claimed impact yourself

Use `.claude/skills/safe-backtest/SKILL.md`. Do not quote the audit's numbers — reproduce them.
Audits have both overstated impact (a "+2.09 pp CAGR" that was ~5.6× too large because it compared
a full holding period against a truncated one) and understated it (a finding predicted "single
percentage points" on PBO and the real move was 6.3 points, in the worse direction).

## 3. Apply, and pin

Each accepted fix needs a test that would fail if the defect returned. Prefer a test that compares
the code to something the code did not produce — a paper's rule, hand arithmetic, a closed form.
A test that only compares the code to itself adds coverage but no assurance; before 2026-07-28 all
55 tests did exactly that and every one passed against four critical defects.

Where a statistic is *removed*, pin its absence with a test explaining why, because an obvious
statistic will otherwise be re-added by the next contributor.

## 4. Record refutations where they will be found

A refused finding must leave a trace, or the next audit will raise it again and the next agent
will apply it. Put the reasoning in `KNOWN_GAPS.md` (for measurement limits) or
`memory/PROJECT.md` §2 (for rejected options), naming the finding ID. Refusing an audit
recommendation is welcome **when the refusal is evidenced**.

## 5. Report honestly

State which findings were confirmed, which were refuted and on what evidence, and what the
re-measurement changed. When a correction makes a published figure worse, **the worse figure is
the honest one** — say so plainly and update the docs, rather than preserving a flattering number
that a different convention produced.

## 6. Commissioning the next one

The prompt is `audit-prompt.md`, beside this file. Paste it into a **different** model than the
one that wrote the code — an audit by the author of the defect is a self-consistency check, which
is the failure mode this whole procedure exists to escape.

Its known blind spot is recorded in that file: every audit so far read the repository's own price
cache, so no audit could ever have caught the adjustment-vintage splice found on 2026-09-01. An
audit inherits the trust boundary of the data it is given.
