"""Back-test on last year: the catalogue must reproduce last year's published section E,
and last year's mapping is checked against its own workbook and report."""

import re
import tomllib
from pathlib import Path

from .compose import published
from .locate import STATUS
from .money import fmt, fmt_count, fmt_pct, mil
from .pipeline import InputError, analyse, input_name


def token_count(text: str, number: str) -> int:
    """Occurrences of a number as a whole token: '12,4' is not counted inside '412,4'."""
    return len(re.findall(rf"(?<![\d.,]){re.escape(number)}(?![\d]|[.,]\d)", text))


def _as_text(number, factor, format_: str, total=None) -> str:
    if total is not None:
        return fmt_pct(number / total)[:-2]
    if format_ == "count":
        return fmt_count(number)
    if format_ == "pct_1":
        return fmt_pct(number)[:-2]
    lei = number * factor
    return mil(abs(lei) if format_.endswith("_abs") else lei)


def validate_mapping(path: Path, wb, report: str) -> list[dict]:
    with open(path, "rb") as fh:
        entries = tomllib.load(fh).get("figure", [])
    rows = []
    for e in entries:
        row = {"text": e["text"], "occurrence": e["occurrence"], "cell": f"{e['sheet']}!{e['cell']}", "ok": False}
        sh = next((s for s in wb.sheets if s.name == e["sheet"]), None)
        if sh is None:
            rows.append(row | {"detail": f"foaia «{e['sheet']}» nu există sau nu e vizibilă"})
            continue
        v = sh.value_at(e["cell"])
        total = sh.value_at(e["total_cell"]).number if e.get("derived") == "share" else None
        if v.number is None or (e.get("derived") == "share" and not total):
            rows.append(row | {"detail": v.problem or f"celula totalului {e.get('total_cell')} nu are valoare"})
            continue
        if e["format"].startswith("mil_lei") and sh.factor is None:
            rows.append(row | {"detail": f"{sh.name}: {sh.unit_problem}"})
            continue
        got = _as_text(v.number, sh.factor, e["format"], total)
        tokens, subs = token_count(report, e["text"]), report.count(e["text"])
        notes = []
        if subs > tokens:
            notes.append(f"«{e['text']}» apare de {subs} ori ca subșir, dar de {tokens} ori ca număr întreg; "
                         f"o căutare pe subșir ar nimeri în interiorul altui număr")
        if got != e["text"]:
            col = sh.columns.get("current", (0,))[0]
            label = next((r.label for r in sh.rows if col and sh.coord(r.row, col) == e["cell"]), "?")
            better = [f"{s.name}!{s.coord(r.row, s.columns['current'][0])} «{r.label}»"
                      for s in wb.sheets if "current" in s.columns and s.factor is not None
                      for r in s.rows
                      if (n := s.value(r.row, s.columns["current"][0]).number) is not None
                      and _as_text(n, s.factor, e["format"]) == e["text"]]
            notes.insert(0, f"celula {row['cell']} («{label}») dă «{got}», nu «{e['text']}»"
                         + (f"; celula care dă «{e['text']}»: {', '.join(better)}" if better else ""))
        elif e["occurrence"] > tokens:
            notes.insert(0, f"apariția {e['occurrence']} nu există: «{e['text']}» apare de {tokens} ori în raport")
        else:
            row["ok"] = True
        rows.append(row | {"detail": "; ".join(notes) or f"reproduce «{got}»"})
    return rows


def run(cfg: dict, folder: Path) -> tuple[str, dict]:
    year = cfg["run"]["reporting_year"] - 1
    run_cfg, template, decisions = cfg["run"], cfg["template"], cfg["decisions"]
    out = [f"# Back-test pe {year}", ""]
    summary = {"year": year}

    report_path = folder / input_name(cfg, "prior_report", year + 1)
    if not report_path.is_file():
        return "\n".join(out + [f"Lipsește {report_path.name}; back-test-ul nu a rulat.", ""]), summary | {"ran": False}
    report = report_path.read_text(encoding="utf-8")
    try:
        a = analyse(year, folder, cfg)
    except InputError as e:
        return "\n".join(out + [f"Back-test-ul nu a rulat: {e}.", ""]), summary | {"ran": False}
    kinds = {k: f.kind for k, f in a.facts.items()}

    out += [f"## 1. Catalogul pe {a.wb.path.name} față de secțiunea E din {report_path.name}", "",
            f"Programul rulează pe registrul {year} și compară fiecare cifră pe care ar scrie-o cu cifra publicată.",
            "", "| Slot | Publicat | Calculat de program | Rezultat |", "|---|---|---|---|"]
    # A figure that a sum check allows to be absent (tier 3) may have had no row last year,
    # while last year's text said "none": expected, since this year the program wants an explicit row.
    optional = {fid for c in cfg["catalogue"]["check"] for fid in c.get("optional", [])}
    ok = bad = expected = 0
    for spec, groups in published(template, decisions, kinds, report, year, run_cfg["company"]):
        name = spec.get("topic") or spec.get("fixed") or spec.get("variant") or spec["text"][:50]
        if groups is None:
            out.append(f"| {name} | — | — | **propoziția nu se regăsește în raport** |")
            bad += 1
            continue
        if "variant" in spec:
            f = a.facts[spec["variant"]]
            pub = "nul" if groups.get(spec["variant"]) is None else groups[spec["variant"]]
            got = ("nul" if f.value == 0 else fmt(f.value, f.kind)) if f.usable else f"gap ({STATUS[f.status]})"
            if pub != got and pub == "nul" and f.status == "missing" and f.id in optional:
                expected += 1
                out.append(f"| {name} | {pub} | {got} | așteptat: în {a.wb.path.name} rândul nu există, iar textul "
                           f"publicat se sprijinea pe lipsa lui; în {year + 1} programul cere un rând explicit, "
                           f"altfel lasă loc de completat |")
                continue
            good = pub == got
            ok, bad = ok + good, bad + (not good)
            out.append(f"| {name} | {pub} | {got} | {'ok' if good else '**diferă**: ' + '; '.join(f.problems)} |")
            continue
        if not any(groups.values()):
            out.append(f"| {name} | text identic | — | ok |")
            ok += 1
            continue
        for g, val in groups.items():
            if val is None:
                continue
            parts = g.split("__")
            if parts[0] in ("clause", "coverage") or parts[-1] == "cause":
                out.append(f"| {g} | «{val}» | — | text, nu cifră (se verifică prin dovezi) |")
                continue
            if parts[0] == "evidence":
                out.append(f"| {g} | {val} | — | sursă documentară, nu din registru: nu se compară |")
                continue
            if parts[0] == "comparison":
                fid, spec_c = parts[1], template["comparison"][parts[1]]
                cur, pc = a.facts[fid], a.facts.get(spec_c["prior_column_figure"])
                if pc is None or pc.value is None or cur.value is None:
                    out.append(f"| {g} | {val} | — | **nu se poate calcula** |")
                    bad += 1
                    continue
                got = (fmt(pc.value, "money") if parts[-1] == "prior"
                       else spec_c["up"] if cur.value > pc.value else spec_c["down"])
            else:
                f = a.facts.get(g)
                value = None if f is None else (f.value if f.value is not None else f.computed)
                got = fmt(value, f.kind) if value is not None else "—"
            good = got == val
            ok, bad = ok + good, bad + (not good)
            out.append(f"| {g} | {val} | {got} | {'ok' if good else '**diferă**'} |")
    summary |= {"ran": True, "slots_ok": ok, "slots_bad": bad, "slots_expected": expected}

    out += ["", f"## 2. {input_name(cfg, 'prior_mapping', year + 1)} pe propriul an", "",
            f"Fiecare intrare e citită din {a.wb.path.name} (cu unitatea foii) și comparată cu textul din "
            f"{report_path.name}, pe număr întreg, nu pe subșir.", "",
            "| Text | Apariția | Celula | Rezultat | Detaliu |", "|---|---|---|---|---|"]
    mapping_path = folder / input_name(cfg, "prior_mapping", year + 1)
    rows = validate_mapping(mapping_path, a.wb, report) if mapping_path.is_file() else []
    summary["files"] = [p.name for p in a.files] + [report_path.name] + ([mapping_path.name] if rows else [])
    for r in rows:
        out.append(f"| {r['text']} | {r['occurrence']} | {r['cell']} | {'ok' if r['ok'] else '**greșit**'} | {r['detail']} |")
    warned = [r for r in rows if r["ok"] and "subșir" in r["detail"]]
    summary |= {"mapping_total": len(rows), "mapping_wrong": [r for r in rows if not r["ok"]], "mapping_warned": warned}
    out += ["", f"Rezultat: {len(rows) - len(summary['mapping_wrong'])} din {len(rows)} intrări reproduc textul; "
                f"{len(summary['mapping_wrong'])} greșite; {len(warned)} corecte doar dacă se caută pe număr întreg.", ""]
    return "\n".join(out), summary
