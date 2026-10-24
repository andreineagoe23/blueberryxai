"""Check figures against each other and against last year before they reach the text.

A failed check never picks a winner: the figures involved become conflicts, with both values.
"""

from dataclasses import dataclass
from decimal import Decimal

from .locate import STATUS, Fact
from .money import fmt, plain

PASSED, FAILED, NOT_RUN = "trecut", "eșuat", "nu s-a putut rula"


@dataclass
class CheckResult:
    id: str
    description: str
    figures: list
    result: str
    detail: str


def _cited(f: Fact) -> str:
    return f"{fmt(f.value, f.kind)} ({f.sheet}!{f.cell})" if f.cell else fmt(f.value, f.kind)


def _show(f: Fact) -> str:
    return f"{f.id} = {plain(f.value)} ({fmt(f.value, f.kind)})" if f.value is not None else f"{f.id} = —"


def record(results, facts, check_id, description, figure_ids, result, detail):
    results.append(CheckResult(check_id, description, figure_ids, result, detail))
    for fid in figure_ids:
        if fid in facts:
            facts[fid].checks.append(f"{check_id}: {result}")


def compare_prior(facts: dict, prior: dict | None, tol: dict, prior_file: str, results: list):
    """Identical to last year (not updated) or a different order of magnitude (unit error)."""
    lo, hi = Decimal(tol["magnitude_min"]), Decimal(tol["magnitude_max"])
    for f in facts.values():
        if f.value is None or f.value == 0 or f.cell is None or f.column != "current":
            continue
        p = prior.get(f.id) if prior else None
        if p is None or p.value is None or p.value == 0:
            continue
        figs = [f.id]
        if f.value == p.value:
            msg = (f"{f.source} = {plain(f.value)} este identică cu valoarea din {prior_file} ({p.source}); "
                   f"probabil nu a fost actualizată")
            f.flag("conflict", msg)
            record(results, facts, f"diferit-de-N-1:{f.id}", "valoarea diferă de anul anterior", figs, FAILED, msg)
        else:
            record(results, facts, f"diferit-de-N-1:{f.id}", "valoarea diferă de anul anterior", figs, PASSED,
                    f"{plain(f.value)} față de {plain(p.value)}")
        ratio = f.value / p.value
        if not lo <= abs(ratio) <= hi:
            msg = (f"{f.source} = {plain(f.value)} lei este de {ratio:.4f} ori valoarea din {prior_file} "
                   f"({plain(p.value)}); posibilă eroare de unitate")
            f.flag("uncertain", msg)
            record(results, facts, f"ordin-de-marime:{f.id}", "ordinul de mărime față de anul anterior", figs,
                    FAILED, msg)
        else:
            record(results, facts, f"ordin-de-marime:{f.id}", "ordinul de mărime față de anul anterior", figs,
                    PASSED, f"raport {ratio:.4f}")


def _term(t: str):
    sign, use_abs = 1, False
    if t.startswith("-"):
        sign, t = -1, t[1:]
    if t.startswith("abs:"):
        use_abs, t = True, t[4:]
    return sign, use_abs, t


def run_checks(facts: dict, checks: list, tol: dict, results: list):
    money_tol = Decimal(tol["money_lei"])
    for c in checks:
        if c["type"] == "sum":
            terms = [_term(t) for t in c["terms"]]
            ids = [t[2] for t in terms] + [c["equals"]]
            total, missing, skipped = Decimal(0), [], []
            for sign, use_abs, fid in terms:
                f = facts[fid]
                if f.value is None:
                    if fid in c.get("optional", []) and f.status == "missing":
                        skipped.append(fid)
                    else:
                        missing.append(f"{fid}: {'; '.join(f.problems)}")
                    continue
                total += sign * (abs(f.value) if use_abs else f.value)
            target = facts[c["equals"]]
            cells = [facts[i].source for i in ids if facts[i].cell]
            if len(cells) != len(set(cells)):
                record(results, facts, c["id"], c["description"], ids, NOT_RUN,
                       "două figuri au fost găsite în aceeași celulă, deci verificarea nu dovedește nimic")
                for fid in ids:
                    facts[fid].flag("uncertain", f"verificarea «{c['description']}» nu poate rula: aceeași celulă")
                continue
            if c.get("taint_total"):
                bad = [fid for _, _, fid in terms if fid not in skipped and facts[fid].status not in ("ok", "decided")]
                if bad and target.value is not None:
                    target.flag("uncertain", f"totalul depinde de {', '.join(bad)}, care nu sunt de încredere")
            if missing or target.value is None:
                why = missing + ([f"{target.id}: {'; '.join(target.problems)}"] if target.value is None else [])
                record(results, facts, c["id"], c["description"], ids, NOT_RUN, " | ".join(why))
                continue
            shown = ", ".join(_show(facts[i]) for i in ids if i not in skipped)
            note = f" ({', '.join(skipped)} lipsește, tratat ca absent)" if skipped else ""
            diff = total - target.value
            if abs(diff) <= money_tol:
                record(results, facts, c["id"], c["description"], ids, PASSED, f"{shown}{note}")
            else:
                parts = " + ".join(_cited(facts[t[2]]) for t in terms if t[2] not in skipped)
                msg = (f"verificarea «{c['description']}» nu trece: {parts}"
                       + (f" = {fmt(total, 'money')}" if len(terms) > 1 else "")
                       + f" față de {_cited(target)}, diferență {plain(diff)} lei")
                for fid in ids:
                    if fid not in skipped:
                        facts[fid].flag("conflict", msg)
                record(results, facts, c["id"], c["description"], ids, FAILED, f"{shown}{note}; diferență {plain(diff)}")
        elif c["type"] == "range":
            f, of = facts[c["figure"]], facts[c["of"]]
            ids = [f.id, of.id]
            if f.value is None or of.value is None:
                why = [f"{x.id}: {'; '.join(x.problems)}" for x in (f, of) if x.value is None]
                record(results, facts, c["id"], c["description"], ids, NOT_RUN, " | ".join(why))
                continue
            share = f.value / of.value
            if Decimal(c["min"]) <= share <= Decimal(c["max"]):
                record(results, facts, c["id"], c["description"], ids, PASSED, f"{_show(f)}, {_show(of)}, raport {share:.4f}")
            else:
                msg = f"{f.id} este {share:.4f} din {of.id}, în afara intervalului {c['min']}–{c['max']}"
                f.flag("conflict", msg)
                record(results, facts, c["id"], c["description"], ids, FAILED, msg)


def derive(facts: dict, derived: list, tol: dict, results: list):
    """Ratios computed from verified figures, compared with the value typed in the workbook."""
    for d in derived:
        num, den = facts[d["numerator"]], facts[d["denominator"]]
        rep = facts.get(d.get("reported"))
        f = Fact(d["id"], d["description"], "ratio", "ok", source=f"{num.source} / {den.source}",
                 reason=f"calculat: {num.id} / {den.id}, rotunjit o singură dată la scriere")
        facts[d["id"]] = f
        ids = [num.id, den.id] + ([rep.id] if rep else [])
        blocked = [x for x in (num, den) if not x.usable]
        if not blocked and den.value == 0:
            den.flag("uncertain", f"{den.source} este 0; raportul nu se poate calcula")
            blocked = [den]
        if blocked:
            f.status = "missing" if any(x.status == "missing" for x in blocked) else "uncertain"
            f.problems.append("nu se poate calcula, pentru că " + " și ".join(
                f"{x.description} nu e disponibil ({STATUS[x.status]})" for x in blocked))
            record(results, facts, f"calcul:{f.id}", "valoarea raportată = calculul", ids, NOT_RUN, f.problems[-1])
            continue
        f.computed = num.value / den.value
        if rep is None or rep.value is None:
            f.value = f.computed
            f.notes.append("valoarea din registru lipsește sau nu poate fi citită ("
                           + ("; ".join(rep.problems) if rep else "nu e în catalog") + "); s-a folosit calculul")
            record(results, facts, f"calcul:{f.id}", "valoarea raportată = calculul", ids, NOT_RUN, f.notes[-1])
            continue
        both = f"raportat {fmt(rep.value, 'ratio')} ({rep.source}), calculat {fmt(f.computed, 'ratio')} ({f.source})"
        if abs(rep.value - f.computed) > Decimal(tol[d["tolerance"]]):
            f.flag("conflict", f"{both}: valorile diferă")
            record(results, facts, f"calcul:{f.id}", "valoarea raportată = calculul", ids, FAILED, both)
        elif rep.status not in ("ok", "decided"):
            f.flag("conflict", f"{both}; valoarea raportată nu e de încredere: {'; '.join(rep.problems)}")
            record(results, facts, f"calcul:{f.id}", "valoarea raportată = calculul", ids, FAILED, f.problems[-1])
        else:
            f.value = f.computed
            record(results, facts, f"calcul:{f.id}", "valoarea raportată = calculul", ids, PASSED, both)
