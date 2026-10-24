"""Catalogue entry -> exactly one cell, and the reason it is the right one.

A figure that matches no row, or more than one, is not chosen: it becomes a gap with the reason.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from .money import plain
from .workbook import Workbook, label_keys, normalize

OK = ("ok", "decided")
STATUS = {"ok": "ok", "decided": "decis", "conflict": "conflict", "missing": "lipsă", "uncertain": "nesigur"}


@dataclass
class Fact:
    id: str
    description: str
    kind: str
    status: str  # ok | decided | conflict | missing | uncertain
    value: Decimal | None = None  # lei, or a fraction for ratios
    source: str = ""  # file!sheet!cell, document, or calculation
    reason: str = ""  # why this source is the right one
    problems: list = field(default_factory=list)  # why the figure is not ok, or what was noted
    notes: list = field(default_factory=list)  # remarks that do not lower the status
    checks: list = field(default_factory=list)  # "check id: result"
    sheet: str | None = None
    cell: str | None = None
    computed: Decimal | None = None  # derived figures: the calculation, kept even in conflict
    column: str = "current"
    name: str = ""  # short name, for the reasons written in the draft

    def flag(self, status: str, problem: str):
        """Lower the status (never raise it) and record why."""
        order = ["ok", "decided", "uncertain", "conflict", "missing"]
        if order.index(status) > order.index(self.status):
            self.status = status
        self.problems.append(problem)

    @property
    def usable(self) -> bool:
        return self.status in OK and self.value is not None


def _pick_sheets(spec: dict, wb: Workbook):
    names = {normalize(n) for n in spec.get("names", [])}
    titles = {normalize(t) for t in spec.get("titles", [])}
    chosen = [s for s in wb.sheets if normalize(s.name) in names or normalize(s.title) in titles]
    if chosen:
        how = {s.name: ("numele foii" if normalize(s.name) in names else f"titlul «{s.title}»") for s in chosen}
        return chosen, how, None
    wanted = ", ".join(f"«{n}»" for n in spec.get("names", []))
    return wb.sheets, {}, f"foaia {wanted} nu a fost găsită după nume sau titlu; s-a căutat în toate foile vizibile"


def locate(fig: dict, wb: Workbook, sheet_specs: dict) -> Fact:
    column = fig.get("column", "current")
    f = Fact(fig["id"], fig["description"], fig["kind"], "ok", column=column, name=fig.get("name", ""))
    aliases = set().union(*(label_keys(lbl) for lbl in fig["labels"]))
    sheets, how, fallback = _pick_sheets(sheet_specs[fig["sheet"]], wb)
    candidates = [(s, r) for s in sheets for r in s.rows if r.keys & aliases]
    file = wb.path.name

    if not candidates:
        f.status = "missing"
        where = ", ".join(f"«{s.name}»" for s in sheets) or "niciuna"
        f.problems.append(f"nu există niciun rând cu eticheta «{fig['labels'][0]}» (sau variantele din catalog) "
                          f"în foile vizibile {where}" + (f"; {fallback}" if fallback else ""))
        return f
    if len(candidates) > 1:
        f.status = "uncertain"
        f.problems.append("eticheta se potrivește cu mai multe rânduri, deci nu se alege: " + ", ".join(
            f"foaia «{s.name}», rândul {r.row} «{r.label}»" for s, r in candidates))
        return f

    sh, row = candidates[0]
    if column not in sh.columns:
        f.status = "missing"
        f.problems.append(f"foaia «{sh.name}» nu are coloana «{'an curent' if column == 'current' else 'an anterior'}»")
        return f
    col, header = sh.columns[column]
    coord = sh.coord(row.row, col)
    f.sheet, f.cell, f.source = sh.name, coord, f"{file}!{sh.name}!{coord}"
    found_by = how.get(sh.name, "căutare în toate foile")
    f.reason = (f"eticheta «{row.label}» (rândul {row.row}), foaia vizibilă «{sh.name}» (găsită după {found_by}), "
                f"coloana {coord.rstrip('0123456789')} («{header}»)")
    if fallback:
        f.notes.append(fallback)

    v = sh.value(row.row, col)
    notes = ("; pe rând scrie " + ", ".join(row.notes)) if row.notes else ""
    if v.number is None:
        f.status = "missing" if v.empty else "uncertain"
        f.problems.append(v.problem + notes)
        return f
    if v.conflict:
        f.flag("conflict", v.conflict)

    if f.kind == "money":
        if sh.factor is None:
            f.flag("uncertain", f"{sh.unit_problem} (foaia «{sh.name}»); valoarea din {coord} nu poate fi convertită în lei")
            return f
        f.value = v.number * sh.factor
        f.reason += f", unitate «{sh.unit_text}», {v.how} → {plain(f.value)} lei"
    elif f.kind == "ratio":
        if "%" in v.number_format or "%" in row.label:
            f.value = v.number if "%" in v.number_format else v.number / 100
            f.reason += f", {v.how}, format procent → {plain(f.value)}"
        else:
            f.flag("uncertain", f"{sh.name}!{coord}: celula nu e formatată ca procent, deci nu se știe dacă "
                                f"{plain(v.number)} e o fracție sau un procent")
            return f
    else:
        f.value = v.number
        f.reason += f", {v.how}"
    if notes:
        f.notes.append(notes.lstrip("; "))
    return f
