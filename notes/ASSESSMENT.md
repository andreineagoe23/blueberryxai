# BlueberryX Engineering Assessment

Thank you for taking the time. This is a take-home assessment. We care less about how much you build and more about how you think.

## Before you start

- **AI tools are expected.** Use whatever you use every day: Claude Code, Cursor, Copilot, ChatGPT, Claude, Gemini, or several. We want to see how you use them, so you will send us your full AI conversations (see deliverable 3).
- **We don't answer questions about the assessment.** If something is unclear, make a reasonable assumption and write it down.
- **All data is fictional.** Asigurări Carpați S.A. and Asigurări Dunărea S.A. do not exist, and the people are invented.
- **The materials are in Romanian**, as a real client's would be. Using AI to read or translate them is fine.

## 1. The problem

Every insurer in the EU publishes a yearly **Solvency and Financial Condition Report (SFCR)**. It has a fixed structure (sections A to E plus a summary), and most of it is last year's text with this year's figures. Today people update it by hand: it takes weeks, and mistakes are easy.

BlueberryX builds software that does the **roll-forward**: it starts from last year's published report and this year's data, and produces a draft of this year's report, which the company's people review and approve. It must run again next year, on new data, without its authors.

Your client is **Asigurări Carpați S.A.**

**The rule of the domain:** in a report sent to the supervisor (ASF), a wrong figure, or a sentence the company's documents do not support, is far worse than a gap left visibly empty. A gap is filled before publication.

## 2. A few terms

You need no insurance knowledge beyond these.

- **SCR** (Solvency Capital Requirement): the capital the insurer must hold. Built from risk modules, minus a diversification effect, plus operational risk.
- **MCR** (Minimum Capital Requirement): the minimum capital floor, lower than the SCR.
- **Eligible own funds**: the capital available, split into quality tiers (tier 1, 2 and 3). The total is the sum of the tiers.
- **Solvency ratio**: eligible own funds divided by the SCR, as a percentage.
- **Technical provisions**: obligations to policyholders. Under Solvency II they are a "best estimate" plus a "risk margin"; the statutory accounts compute them differently, so the numbers normally differ.
- **Mapping**: the link between each figure in the report's text and the workbook cell it comes from.

## 3. The materials (folder `date/`)

| File | What it is |
|---|---|
| `raport_2024.txt` | Sections A to E of the published 2024 report. |
| `raport_2024_sinteza.txt` | The 2024 summary. |
| `mapping_2024.toml` | Last year's mapping: for each figure in `raport_2024.txt`, its sheet and cell in the 2024 workbook. The format is explained in the file's comments. |
| `registru_2024.xlsx` | The 2024 workbook. |
| `registru_2025.xlsx` | The 2025 workbook, received from the client. |
| `situatii_financiare_2025_extras.pdf` | An extract of the audited 2025 financial statements. |
| `nota_functia_actuariala_2026-02-02.docx` | A note from the actuarial function about 2025. |
| `proces_verbal_CA_2025-02-18_scanat.pdf` | A scanned extract of board minutes. |
| `proces_verbal_AGA_2025-04-24.txt` | An extract of the shareholders' meeting minutes. |
| `email_director_financiar.txt` | An email from the client's finance director. |
| `raport_Asigurari_Dunarea_2024_extras.txt` | An extract of another insurer's public report. |

Work on copies of the workbooks: opening and saving them in Excel or LibreOffice can change what is stored.

## 4. The report's rules

These apply to everything you build.

1. **Traceability.** Every figure in the 2025 report has a source you can show: a workbook cell, a document (with its page), or a calculation from those. Last year's figure is never used in place of this year's.
2. **No unsupported statements.** No sentence states something the sources do not support. This covers facts, the direction of a change ("increased"), and explanations ("as a result of", "because").
3. **Visible gaps.** Where something cannot be filled correctly, the text says `[de completat: reason]`, with a short, concrete reason.
4. **No copied text.** Never reuse wording from another company's report.
5. **Number format**, as in the 2024 report: amounts in millions of lei with one decimal (`284,6 mil. lei`); percentages with one decimal, a space and `%` (`187,4 %`); whole numbers with a dot for thousands (`18.420`); rounding half up, once, on the unrounded value; a total is taken from its source, never by adding rounded values.

## 5. What we ask for

### Deliverable 1. The case (`DESIGN.md`, at most 4 pages, at least one diagram)

**The situation.** Asigurări Carpați's CFO spends six weeks every spring on the SFCR, with three people and a lot of copy-paste. Last year the report went to ASF with a wrong figure in it, found by the auditor after filing. The CFO has asked BlueberryX to take this over. The Board's question is simple: *"Can we trust a machine with a regulatory report, and what does it take?"*

You are the engineer leading the answer. Write a memo for the CFO and our CTO at the same time: plain enough for the first, precise enough for the second. Lead with your answer, then support it.

1. **The answer first.** In at most five lines: can this be automated safely, which part should not be, and what must be true for the CFO to sign the result?
2. **Structure the problem.** Break "produce next year's SFCR correctly, every year, without its authors" into its parts. A short tree is enough. For each branch, name the main way it can go wrong. Which branch carries the most risk, and why?
3. **Design the system.** One diagram, then a short walk through it:
   - the parts, and how data flows from the client's files to the draft;
   - what stops a wrong number reaching the text when next year's workbook is built by someone else (rows move, a sheet is added, units change);
   - what the system does when two sources disagree on a figure;
   - how it knows that last year's "increased" is still true;
   - where people decide things, and where their decisions are kept.
4. **The role of AI.** Where would you let a language model write text, and where never? Give the rule you would defend in front of the supervisor, and the one example that would make you change it.
5. **Size it.** Estimate, with your assumptions shown:
   - how many figures and sentences in this report change from one year to the next (use the materials);
   - the hours your system saves the CFO's team in a year, and the hours it still needs from them;
   - what one wrong figure in a filed report costs the client, in money, time or reputation, and how that should shape your design.

   Rough numbers with clear logic beat precise numbers without it.
6. **Prioritise.** You have four weeks before the CFO's deadline, not six months. What do you build first, what do you leave as a manual step, and what do you refuse to ship? Why that order?
7. **Prove it.** How do you test it, so the team trusts next year's run without you? What evidence would you show the CFO before he signs?
8. **Scale it.** BlueberryX sells this to 25 insurers. What stays the same, what changes per client, and what becomes the bottleneck? One paragraph on what that means for us as a business.
9. **Risks.** The three things most likely to go wrong after launch, each with its early warning sign and what you would do.

There is no single right answer.

### Deliverable 2. A small working slice (code)

Prove the heart of your design on the real materials, for **section E only** (own funds, SCR, MCR and the solvency ratio):

- one command, run from the `date/` folder, writes everything to `output/` (put the command in your README);
- for each figure in section E, it finds this year's value and says **why** that cell is the right one, or that the value is missing or uncertain;
- it checks the figures against each other before they reach the text, and never chooses silently between two values that disagree;
- it writes section E for 2025, following the rules above, with visible gaps where needed;
- human decisions live in a configuration file the program reads, each with its source and reason; money is computed exactly (for example `Decimal`); nothing that changes from year to year is hardcoded.

**We will run your program, unchanged, on another version of `registru_2025.xlsx`.** Every file in `output/` must be produced by the program. Keep it small.

### Deliverable 3. How you worked with AI (`ai/`)

1. **The raw conversations.** Export every AI conversation you used for this assessment, complete and unedited: for example Claude Code's `/export`, ChatGPT or Claude share links in a text file, or a copy of your Copilot or Cursor chats. Put them in `ai/conversations/`. If you used no AI for part of the work, say so.
2. **`ai/AI.md`, one page:**
   - one suggestion from an AI that you rejected or rewrote, and why;
   - one place where an AI was wrong and you caught it, and how you caught it;
   - one decision you deliberately kept for yourself, and why;
   - in a system like this, what you would never let an AI do on its own.

Please don't tidy them up.

## 6. What you send, once, at the end

One zip named `firstname_lastname.zip`, uploaded to the Google Drive folder we shared with you (where you found this assessment), before the deadline:

```
README.md            how to install and run, the one command
DESIGN.md            the case
ai/
    AI.md
    conversations/   the raw exports
config/              your decisions, read by the program
output/              generated by the program
src/                 the code
tests/               optional: a few tests for the logic that matters
```

Python is preferred; another language is fine if you tell us why. If you use git, include the history.

Good luck, and enjoy it.
