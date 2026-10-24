# Rolling the SFCR forward: can a machine be trusted with it?

**To:** CFO, Asigurări Carpați · CTO, BlueberryX  **From:** Andrei Neagoe  **Date:** October 2026

## 1. The answer

**Yes, for the figures and the routine text, provided the system may say "I don't know".** Two things stay with people: choosing between sources that disagree, and saying *why* something changed. The CFO can sign when three things hold. Every figure links to a cell or page his team can open. Every gap and conflict was closed by a named person. And the system has been shown, on last year's report and on deliberately broken workbooks, to stop rather than guess.

## 2. The problem, broken down

```
SFCR year N, correct, without its authors
├─ 1 Read sources     fails: wrong unit, hidden sheet read, OCR misread
├─ 2 Locate figures   fails: rows moved, last year's mapping wrong,       ◄ most
│                            "12,4" matched inside "412,4"                   risk
├─ 3 Check, reconcile fails: silent choice between sources, stale value   ◄ most
│                            that looks plausible                            risk
├─ 4 Write text
│   ├─ figures        fails: wrong year; a total built from rounded parts
│   ├─ directions     fails: last year's "increased" kept, figure fell
│   ├─ causes         fails: unsupported "as a result of"
│   └─ fixed text     fails: "five Board members" no longer true
├─ 5 Review, sign-off fails: rubber-stamping under deadline pressure
└─ 6 Next year        fails: hardcoded rules; a mapping only its author knows
```

**Branches 2 and 3 carry the most risk, because their errors are silent and plausible.** A wrong sentence reads wrong to an expert; a wrong number in the right cell and format does not, which is how last year's error reached ASF. This year's materials hold four: a ratio cell still showing 2024's 187,4 % (the same sheet gives 197,4 %), RCA premiums of 142,0 mil. lei against the audited 124,0, a hidden sheet copying 2024, and last year's own mapping pointing "12,6" at the wrong cell.

## 3. The system

```
 CLIENT FILES (read-only): workbooks N and N-1 · audited accounts,
                           minutes, notes · report N-1 and its mapping
                               ▼
       ┌───────────────────────────────────────────────┐
       │ 1 EXTRACT every cell with its label, unit,    │
       │   visibility, formula; document text + page   │
       └───────────────────────┬───────────────────────┘
       ┌───────────────────────▼───────────────────────┐ none or several
       │ 2 LOCATE catalogue entry → exactly one cell,  ├─────────────┐
       │   and the reason for it                       │             ▼
       └───────────────────────┬───────────────────────┘     ┌───────────────┐
       ┌───────────────────────▼───────────────────────┐fail │ ISSUES        │
       │ 3 CHECK totals, cross-sheet, cross-source,    ├────►│ gap/conflict, │
       │   magnitude, "same as N-1?"                   │     │ with reason   │
       └───────────────────────┬───────────────────────┘     └───────┬───────┘
       ┌───────────────────────▼ ok ───────────────────┐     ┌───────▼───────┐ CFO team,
       │ 4 FACTS exact Decimal value, source,          │◄────┤ decisions.toml│ actuary
       │   status ok · decided · conflict · gap        │     │ in git:       │ decide
       └───────────────────────┬───────────────────────┘     │ decisions     │
       ┌───────────────────────▼───────────────────────┐     │ bound to the  │
       │ 5 WRITE last year's text as slots; direction  │◄────┤ values seen;  │
       │   computed; cause only from evidence;         │     │ evidence      │
       │   otherwise [de completat]                    │     │ quotes; fixed │
       └───────────────────────┬───────────────────────┘     │ text          │
                               ▼                             └───────────────┘
 output/  draft section · evidence table · issues list · next year's mapping
```

**When someone else builds the workbook.** A **figure catalogue** says *what* each figure is, not *where*: the locator matches labels, never coordinates, and reads each sheet's unit from its header (in 2025 Capital moved to *thousands* of lei; Prime stayed in lei). A figure needs exactly one candidate on a visible sheet, or it is a gap with the reason. Then the figures are checked: tiers sum to the total; modules minus diversification give the basic SCR; the SCR matches across sheets; the MCR lies at 25–45 % of the SCR; the ratio equals own funds / SCR; the magnitude matches last year (×1000 is a unit error); and the raw value differs from last year's (raw, because RC generală shows 7,1 % in both years although its share changed). Formulas with no stored result are re-evaluated.

**When two sources disagree,** none wins by default. The figure becomes a *conflict*, and the draft shows a gap naming both values. A person resolves it in `config/decisions.toml` with the chosen and rejected source, the reason, their name and the values seen. The decision is **bound to those values**: if a corrected workbook arrives, the conflict reopens. This year the ratio uses own funds / SCR (197,4 %), because the reported cell equals 2024's.

**How it knows "increased" is still true.** The word is never copied. The direction is recomputed against last year's published figure; a change near zero goes to a person. A cause needs an **evidence item**: a verbatim quote from a current-year company document, with its location, which the program re-finds in the file. In 2024 the SCR "rose as a result of higher premiums"; in 2025 it fell "în principal ca urmare a scăderii riscului de piață", per the actuarial note. The CFO's "thanks to the new reinsurance programme" is contradicted by the same note, so it is left out and the issues list says why.

**Where people decide.** In one version-controlled file: conflict decisions, approved evidence, and fixed text that no document confirms, reconfirmed yearly. Sign-off is a tagged version of that file plus a hash of the inputs.

## 4. The role of AI

**A model may propose; it never asserts.**

**Allowed, always checked:** finding passages in scans, matching new labels to old ones, rewording a sentence whose structure must change (numbers inserted by code), a second reader for unsupported words. **Never:** producing or choosing a figure, resolving a conflict, a direction or cause without evidence, anything sent to ASF without a named approver.

**The rule I would defend before ASF:** *every figure is computed by deterministic code from a cell or page we can show; every statement of direction or cause is tied to a passage in the company's own documents and approved by a named person; the model only proposes wording.*

**The example that would make me tighten it:** a model that drops "*în principal*" ("mainly") when rewording the actuarial note, or adds "and the reinsurance programme" because the CFO's email was in its context. It reads fluently and gets past a tired reviewer. If our tests catch it once, cause sentences become verbatim quotes only.

## 5. Size

**What changes.** The 2024 extract has **37 figures** (33 mapped, plus dividends, statutory provisions, headcount, Board size). In 2025, 36 change; the 37th only *looks* unchanged (7,1 %). Three cannot be filled from the sources (MCR, year-end headcount, Board size) and the ratio is in conflict. Of its **33 sentences**, 6 carry no figure (3 need yearly reconfirmation), 17 change only their figures, 2 make a direction or ranking claim that still holds after re-checking, and **8 must be rewritten or left as a gap** (SCR direction and cause, market-risk source, listed shares, Board, headcount, MCR ×2, non-compliance). So a quarter of the text needs judgement each year. A full SFCR, ten times this extract, has ~400 figures and ~350 sentences, ~80 needing judgement.

**Hours (assumed).** Three people for six weeks at half time: 3 × 6 × 20 = **360 h**. Copying, formatting and cross-checking go from 200 h to 10 h; chasing sources from 90 h to 40 h (conflicts arrive located); narrative and review from 70 h to 60 h. Total **110 h**. That saves **~250 h a year** (year one costs ~40 h more for onboarding and a parallel run). The 110 h left are decisions and explanations, on purpose.

**Cost of one wrong figure (assumed).** Refiling, the auditor's follow-up, answering ASF, the Board's time: 100+ hours, roughly 50–100k lei, and a possible sanction under Law 237/2015. The bigger cost is trust: brokers, reinsurers and rating agencies read the SFCR, and a restated ratio casts doubt on every other figure. A gap costs an hour before filing. That asymmetry, 100× or more, shapes the design: **precision over recall**, checks that fail closed, and two independent confirmations for the key capital figures.

## 6. Prioritise: four weeks

**Week 1:** section E end to end: catalogue, locator, checks, evidence table, gaps, back-test on 2024 *(the slice delivered here)*. **Week 2:** figures for sections A–D; quotes from the accounts and minutes, each checked in its file. **Week 3:** text for all sections; walk the team through the decisions file. **Week 4:** parallel run with the CFO's team on real data, every difference explained; sign-off pack.

**The order follows the cost of an error.** Section E is what ASF reads first, and its errors are invisible; text errors are easier for reviewers to see.

**Left manual:** explanations of change, OCR'd scans, legal and governance text, the MCR. **Refused:** last year's figure for a missing one, automatic conflict resolution, model-made numbers or causes, another insurer's wording, a "final" draft without sign-off.

## 7. Prove it

- **Back-test.** On 2024's inputs, the system must reproduce last year's published figures. The slice reproduces section E and re-checks all 33 entries of last year's mapping, which exposed the mapping fault above.
- **Fault injection, on every change.** Broken copies of the real workbook (rows moved, units switched, hidden sheet shown, formula without stored value, stale value, a broken total, duplicate labels, numbers as text) pass only with the right value or a visible gap or conflict. Unit tests cover rounding and format.

**What the CFO sees before signing:** (1) an evidence table (value, source, checks passed); (2) an issues list: how each gap and conflict was closed, and by whom; (3) the test report ("we broke the workbook 34 ways; each time it gave the right figure or a visible gap"); (4) proof that the same inputs and decisions give byte-identical output.

**Trust without me:** one command, a one-page runbook, failing checks that explain themselves in Romanian, one file to edit.

## 8. Scale it: 25 insurers

**Stays the same:** the engine, checks, formats, the decisions model, tests, the workflow, the A–E skeleton; section E's figures can anchor to the standard templates (S.23.01, S.25.01, S.28.01). **Changes per client:** workbook layouts, last year's text, document sources, deployment, reviewer roles. **The bottleneck** is onboarding (first back-test, catalogue) and scarce expert review, all in the same weeks: every client's deadline is 14 weeks after year-end, in early April.

**What this means for us as a business:** revenue recurs, but delivery stays people-heavy unless onboarding becomes configuration. So we invest early in the standard templates and a shared catalogue, so client 25 costs a fraction of client 1; we staff for a February–April peak; and we sell an **audit-ready evidence pack**, not "AI writes your report".

## 9. Risks after launch

| Risk | Early warning | Response |
|---|---|---|
| **Client files drift** beyond the locator (merged sheets, new labels) | More "not found" or "ambiguous" figures per run | Update labels with the client before the season; ask for a fixed input template |
| **Review becomes a rubber stamp** under deadline pressure (as in this year's email) | Decisions closed in seconds; reasons like "as last year"; gaps closed in the last 48 h | Source and reason required; planted test errors; four-eyes on capital figures; open gaps escalated, never filled for a date |
| **The report's structure changes** (Solvency II review, new sections) | Regulatory consultations; template sentences without a slot | Version catalogue and templates per year; re-run the back-test after every change |

**Assumptions** are listed in the README.
