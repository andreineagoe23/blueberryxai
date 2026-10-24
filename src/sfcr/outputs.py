"""Every file in output/, deterministic: no timestamps, fixed order, LF line endings."""

import csv
import hashlib
import io
import json
import platform
import re
from importlib import metadata
from pathlib import Path

from .backtest import token_count
from .checks import FAILED, NOT_RUN
from .locate import STATUS
from .money import fmt, plain


def _csv(rows: list[list]) -> str:
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(rows)
    return buf.getvalue()


def _toml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def figures_csv(a) -> str:
    rows = [["figura", "descriere", "stare", "valoare_exacta", "valoare_in_text", "sursa", "motiv", "probleme",
             "note", "verificari"]]
    for f in a.facts.values():
        value = f.value if f.value is not None else f.computed
        rows.append([f.id, f.description, STATUS[f.status], plain(value) if value is not None else "",
                     fmt(f.value, f.kind) if f.usable else "", f.source, f.reason, " | ".join(f.problems),
                     " | ".join(f.notes), " | ".join(f.checks)])
    return _csv(rows)


def checks_csv(a) -> str:
    rows = [["verificare", "descriere", "figuri", "rezultat", "detaliu"]]
    rows += [[r.id, r.description, " ".join(r.figures), r.result, r.detail] for r in a.results]
    return _csv(rows)


def mapping_toml(a, cfg) -> str:
    """Next year's mapping, generated: figure id -> cell or document, with the reason."""
    text = a.draft.text
    out = [f"# Mapping generat de program pentru raportul {a.year}, secțiunea E. Nu se editează de mână.",
           "# id: figura din config/catalogue.toml; text și occurrence: cum apare în raport (număr întreg, nu subșir);",
           "# unit: unitatea foii, citită din registru; status: ok / decis / conflict / lipsă / nesigur.", ""]
    cursor = 0
    placed = {fid for fid, _ in a.draft.placements}
    for fid, shown in a.draft.placements:
        number = re.sub(r" (mil\. lei|%)$", "", shown)
        m = re.compile(rf"(?<![\d.,]){re.escape(shown)}").search(text, cursor)
        occurrence = token_count(text[:m.start()], number) + 1
        cursor = m.end()
        f = a.facts[fid]
        sh = next((s for s in a.wb.sheets if s.name == f.sheet), None)
        out += ["[[figure]]", f"id = {_toml_str(fid)}", f"text = {_toml_str(number)}",
                f"occurrence = {occurrence}"]
        if f.cell:
            out += [f"workbook = {_toml_str(a.wb.path.name)}", f"sheet = {_toml_str(f.sheet)}",
                    f"cell = {_toml_str(f.cell)}"]
            if sh is not None and sh.unit_text and f.kind == "money":
                out.append(f"unit = {_toml_str(sh.unit_text)}")
        out += [f"format = {_toml_str({'money': 'mil_lei_1', 'ratio': 'pct_1'}[f.kind])}",
                f"value = {_toml_str(plain(f.value))}", f"status = {_toml_str(STATUS[f.status])}",
                f"source = {_toml_str(f.source)}", f"reason = {_toml_str(f.reason)}", ""]
    for f in a.facts.values():
        if f.id not in placed and f.cell and f.column == "current":
            out += ["[[figure]]", f"id = {_toml_str(f.id)}", "# nu apare în text", f"sheet = {_toml_str(f.sheet)}",
                    f"cell = {_toml_str(f.cell)}", f"status = {_toml_str(STATUS[f.status])}",
                    f"reason = {_toml_str(f.reason or '; '.join(f.problems))}", ""]
    return "\n".join(out)


def issues_md(a, cfg, bt_summary) -> str:
    d = cfg["decisions"]
    y = a.year
    out = [f"# Probleme: secțiunea E, {y}", ""]
    open_conf = [f for f in a.facts.values() if f.status in ("conflict", "uncertain", "missing")]
    decided = [f for f in a.facts.values() if f.status == "decided"]
    failed = [r for r in a.results if r.result == FAILED]
    out += [f"- **{len(a.draft.gaps)}** locuri de completat în text înainte de publicare",
            f"- **{len(decided)}** figuri rezolvate prin decizie, **{len(open_conf)}** figuri care nu sunt ok",
            f"- **{len(failed)}** verificări eșuate din {len(a.results)}", ""]

    out += ["## Locuri de completat în text", ""]
    out += [f"- **{topic}**: {reason}" for topic, reason in a.draft.gaps] or ["Niciunul."]
    out += ["", "## Figuri care nu sunt ok", ""]
    out += [f"- **{f.id}** ({STATUS[f.status]}), {f.description}: {'; '.join(f.problems)}" for f in open_conf] or ["Niciuna."]
    out += ["", "## Decizii din config/decisions.toml", ""]
    out += [f"- **{o.id}** ({o.figure}): {o.detail}" for o in a.outcomes] or ["Niciuna."]
    for f in decided:
        out.append(f"  - {f.id}: problema inițială: {'; '.join(f.problems)}")
    out += ["", "## Verificări eșuate sau care nu au putut rula", ""]
    out += [f"- **{r.id}** ({r.result}): {r.detail}" for r in a.results if r.result in (FAILED, NOT_RUN)] or ["Niciuna."]
    out += ["", "## Foi ignorate", ""]
    out += [f"- {a.wb.path.name}, foaia «{n}»: {why}" for n, why in a.wb.ignored] or ["Niciuna."]
    out += ["", "## Unitatea fiecărei foi", "", f"| Foaie | {a.wb.path.name} | "
            + (f"{a.prior_wb.path.name} |" if a.prior_wb else "anul anterior |"), "|---|---|---|"]
    prior_units = {s.name: s.unit_text or s.unit_problem for s in a.prior_wb.sheets} if a.prior_wb else {}
    for s in a.wb.sheets:
        now, before = s.unit_text or f"**{s.unit_problem}**", prior_units.get(s.name, "—")
        mark = " (schimbată)" if before != "—" and before.split(" (")[0] != now.split(" (")[0] else ""
        out.append(f"| {s.name} | {now}{mark} | {before} |")
    out += ["", "## Dovezi din documente", ""]
    for item in d["evidence"]:
        v = a.verified.get(item["id"])
        out.append(f"- **{item['id']}** ({'verificată' if v and v.ok else 'NEVERIFICATĂ'}): {item['claim']} "
                   f"{v.detail if v else ''}" + (f". Motiv: {item['reason']}" if item.get("reason") else ""))
    out += ["", "## Text fix aprobat (fără sursă în documentele anului)", ""]
    out += [f"- **{t['id']}** (aprobat de {t['approved_by']}; sursa textului: {t.get('source', '—')}): {t['reason']}"
            for t in d["fixed_text"]] or ["Niciunul."]
    out += ["", "## Cereri neacceptate", ""]
    for c in d["rejected_claim"]:
        v = a.verified.get(c["id"])
        contra = f" Contrazis de: {v.detail}." if v and v.ok else ""
        out.append(f"- **{c['claim']}** (cerut în {c['requested_by']}): {c['reason']}{contra}")
    out += ["", "## Reguli aplicate", ""]
    out += [f"- **{p['id']}**: {p['rule']} ({p['source']})" for p in d["policy"]]
    notes = [(f.id, n) for f in a.facts.values() for n in f.notes]
    out += ["", "## Observații", ""]
    out += [f"- {fid}: {n}" for fid, n in notes] or ["Niciuna."]
    out += ["", f"## Back-test pe {bt_summary.get('year')}", ""]
    if not bt_summary.get("ran"):
        out.append(f"Nu a rulat; motivul e în backtest_{bt_summary.get('year')}.md.")
    else:
        out.append(f"- secțiunea E {bt_summary['year']}: {bt_summary['slots_ok']} sloturi reproduse, "
                   f"{bt_summary['slots_expected']} cu diferență așteptată, {bt_summary['slots_bad']} diferite "
                   f"(detalii în backtest_{bt_summary['year']}.md)")
        for r in bt_summary["mapping_wrong"]:
            out.append(f"- mapping {bt_summary['year']}, «{r['text']}» → {r['cell']}: **greșit**: {r['detail']}")
        for r in bt_summary["mapping_warned"]:
            out.append(f"- mapping {bt_summary['year']}, «{r['text']}» → {r['cell']}: {r['detail']}")
    return "\n".join(out) + "\n"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(a, input_dir: Path, read: set, config_dir: Path, written: dict) -> str:
    inputs = sorted(p for p in input_dir.iterdir() if p.is_file() and not p.name.startswith("."))
    libs = {}
    for lib in ("openpyxl", "pypdf", "python-docx"):
        try:
            libs[lib] = metadata.version(lib)
        except metadata.PackageNotFoundError:
            libs[lib] = "?"
    data = {
        "reporting_year": a.year,
        "inputs": {p.name: {"sha256": _sha(p), "read_by_program": p.name in read} for p in inputs},
        "config": {p.name: _sha(p) for p in sorted(config_dir.glob("*.toml"))},
        "outputs": {name: hashlib.sha256(text.encode("utf-8")).hexdigest() for name, text in sorted(written.items())},
        "python": platform.python_version(),
        "libraries": libs,
    }
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write_all(a, cfg, input_dir: Path, config_dir: Path, out_dir: Path, backtest_md: str,
              bt_summary: dict) -> list[str]:
    y = a.year
    files = {
        f"raport_{y}_sectiunea_E.txt": a.draft.text,
        f"cifre_E_{y}.csv": figures_csv(a),
        f"verificari_E_{y}.csv": checks_csv(a),
        f"probleme_E_{y}.md": issues_md(a, cfg, bt_summary),
        f"mapping_{y}.toml": mapping_toml(a, cfg),
        f"backtest_{y - 1}.md": backtest_md,
    }
    read = {p.name for p in a.files} | set(bt_summary.get("files", []))
    files["manifest.json"] = manifest(a, input_dir, read, config_dir, files)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (out_dir / name).write_text(text, encoding="utf-8", newline="\n")
    return list(files)
