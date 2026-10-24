# How I worked with AI

I used Claude Code for the whole assessment, in three sessions: the trap audit and DESIGN.md; the plan
and the code for section E; an audit against the brief, the README, the DESIGN.md cuts and this page. The raw transcripts are in `conversations/`, unedited. I set the direction, made the decisions and checked the
results; the AI read the materials, wrote the code and tests, and ran them.

## A suggestion I rejected

After a first round of cuts, Claude reported that DESIGN.md fitted four pages at a line height of 1.25 but
not at 1.4, and left it to me, since cutting more meant removing ideas. I rejected that framing: *at most*
four pages must hold under any reasonable rendering, not the most favourable one. I asked for options
instead. Claude measured each candidate cut by its rendered height. Its first measurement was misleading,
because page-break slack absorbed the early cuts. I then chose seven of fourteen, and the memo now fits
four pages at 1.4. I also turned down shipping my working notes in the zip; the brief lists what goes in.

## Where the AI was wrong, and how I caught it

The approved plan said to run `python ../src/main.py`. I ran it on my Mac and got
`zsh: command not found: python`. macOS ships only `python3`, and Homebrew's Python refuses a global
`pip install`, so the command had never worked on the machine it was written for. The README now sets
up a virtual environment, and the code is tested on Python 3.11 as well as 3.14.

A second error was caught by asking for an audit of every claim in DESIGN.md against the code. The memo
said "we broke the workbook 40 ways", but 40 was the total number of tests, and only 27 of them broke the
workbook. The sentence now gives the real number, 34.

## A decision I kept for myself

This was what the draft may say about the MCR once a workbook contains one. "A fost acoperită integral"
(covered in full) is a statement the CFO signs before the supervisor. Only part of tier 2 counts towards
the MCR, and the workbook does not give that limit. Claude laid out the options; I decided that the sentence
appears only if tier 1 alone covers the MCR, and otherwise the text shows a gap. How conservative to be is
the call of whoever answers for the report.

## What I would never let an AI do on its own here

Change `config/decisions.toml`. Any failing check can be made to pass from that file: by updating a
decision's `observed` values, adding an evidence quote, or approving a fixed text. Each of these is a
statement in the company's name. An AI may propose one, and it is good at finding the quote; a named person
makes it, and it stays in the history. The same goes for choosing between two figures, writing a cause, and
anything that leaves the building: filing with ASF or, here, publishing to a repository, which happened
only on my explicit instruction.
