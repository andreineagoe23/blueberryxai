# SFCR roll-forward: section E, Asigurări Carpați 2025

A small working slice of the design in [DESIGN.md](DESIGN.md). From the 2025 workbook, last year's report
and the company's documents, it writes a draft of section E (own funds, SCR, MCR and the solvency ratio)
for 2025. Every figure comes with its source and the reason that cell was chosen. Anything that cannot be
filled correctly is left as a visible `[de completat: …]`.

## Install

Python 3.11 or newer (the code uses `tomllib`). Tested on 3.11 and 3.14.

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

A virtual environment is the simplest route on macOS, where Homebrew's Python refuses a global `pip install`.

## Run: the one command

The zip does not include the assessment materials. Put the `date/` folder from the assessment next to `src/`
(`<project>/date/registru_2025.xlsx`, and so on), then run from it:

```
cd date
../.venv/bin/python ../src/main.py
```

With the venv activated (`source .venv/bin/activate`), the command is `python ../src/main.py`.

The inputs are read from the current folder (`date/`), the configuration from `config/`, and everything is
written to `output/` at the project root, next to `src/`. Exit code 0 means the files were written, and gaps
and conflicts are reported inside them. Exit code 2 means `registru_2025.xlsx` was not found in the current
folder (for example because the command was run from the project root).

To run on another version of the workbook, replace `date/registru_2025.xlsx` and run the same command. No
code or config change is needed. Options `--input`, `--config` and `--out` override the three folders.

Tests: `.venv/bin/python -m pytest tests` (from the project root).

## What it writes (`output/`)

| File | Content |
|---|---|
| `raport_2025_sectiunea_E.txt` | the draft of section E |
| `cifre_E_2025.csv` | every figure: exact value in lei, value as written, status, source cell or document, why that source, checks |
| `verificari_E_2025.csv` | every check that ran, its inputs and result, including the ones that passed |
| `probleme_E_2025.md` | what a person must close before filing: gaps, conflicts, decisions applied or not, ignored sheets, units, evidence, refused requests |
| `mapping_2025.toml` | next year's mapping, generated: figure → cell or document, with the reason |
| `backtest_2024.md` | the same catalogue run on the 2024 workbook against the published 2024 section E, plus a check of every entry in `mapping_2024.toml` |
| `manifest.json` | SHA-256 of every input, config and output file; library versions |

The same inputs and config give byte-identical files.

## Where things are

```
config/run.toml         reporting year, file name templates, column headers, units, tolerances
config/catalogue.toml   the figures of section E (what each one is, not where it is) and the checks
config/template_E.toml  last year's section E as sentences with slots
config/decisions.toml   human decisions: conflict resolutions, evidence quotes, refused requests, fixed text
src/main.py             the command
src/sfcr/               workbook → locate → checks → decisions → evidence → compose → outputs; backtest
tests/                  broken copies of the real workbook, rounding and format, decisions and evidence
```

Next year: set `reporting_year` in `config/run.toml`, review `config/decisions.toml` (its decisions apply
only to the year and the values they were taken on), and put the new files in `date/`.

## Assumptions

Where the brief or the materials left a choice open, the program does this.

**Reading the workbook**
- "31.12 an curent" means 31 December of `reporting_year` in `config/run.toml`; the workbook does not state
  the year.
- Figures are found by their label, never by their coordinates. A label matching no row, or several rows, is
  a gap, never a choice.
- Hidden sheets, and sheets titled "nu se folosește" or "copie", are not sources. They are listed as ignored.
- The unit is read from each sheet's header ("Valori în mii lei"). A sheet with no recognised unit gives no
  amounts.
- A formula without a stored result is recalculated, but only for simple arithmetic on the same sheet;
  anything else makes the figure uncertain.
- A tier 3 row that is absent is not read as zero. The sentence "nu a deținut fonduri proprii de nivel 3"
  needs a row showing 0.

**Checks and conflicts**
- A non-zero current value identical to last year's is treated as not updated, so it is a conflict. A value
  that really did not change needs a decision in `config/decisions.toml`.
- A value 0,5× to 2× last year's passes the order-of-magnitude check; outside that range it is a probable
  unit error.
- The solvency ratio is eligible own funds / SCR. A typed ratio that differs from the calculation is a
  conflict. If the typed ratio is missing or unreadable, the calculation is used, and an issue is recorded.
- The MCR must lie between 25 % and 45 % of the SCR (the Solvency II corridor).

**Decisions**
- A decision applies only while the inputs show exactly the values it was taken on (`observed`). This
  year's decision uses the computed ratio (197,4 %) because the typed cell (187,4 %) equals 2024's.
  **On another version of `registru_2025.xlsx`, that decision will usually not apply**: the ratio is then
  a gap naming both values, until someone records a new decision. This is intended, not a failure.
- No source wins by default. Audited accounts are used for accounting figures (dividends, as the CFO's
  email asks) and the workbook for Solvency II figures, but a disagreement is still a conflict.

**Text**
- A direction ("în creștere", "în scădere") is computed against last year's SCR, which must come from at
  least two agreeing sources: the 2024 workbook, the "an anterior" column, and the published 2024 report.
  A change below 0,5 % is left to a person.
- A cause ("ca urmare a …") appears only as a verbatim quote from a company document. The program re-finds
  the quote in the file, and the quote must explain the direction actually computed. The actuarial
  function's note is accepted as a source for explanations.
- "MCR … a fost acoperită integral" is written only if tier 1 own funds alone cover the MCR. Tier 2 counts
  towards the MCR only up to a limit that the workbook does not give.
- The legal-basis sentence in E.1 has no source in this year's documents. It is carried forward as fixed text
  approved in `config/decisions.toml`, and should be reconfirmed by compliance each year.
- A gap in the draft gives a short, concrete reason (the figure, the cell, what is wrong). The full
  reason, with file names and whole quotes, is in `probleme_E_2025.md`.
- The draft is checked automatically: every amount in it comes from a figure, none of the refused claims
  appears, and it shares no six-word sequence with the Asigurări Dunărea report.

**Not read by the program**
- The CFO's email is not read. Its requests are recorded and answered in `config/decisions.toml`.
- The scanned board minutes have no text layer and are not read either (board composition is section B, not E).
- The 2024 summary is outside section E.

`manifest.json` lists which input files were read.
