"""Human decisions from config/decisions.toml, bound to the values they were taken on."""

import tomllib
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from .money import plain


@dataclass
class Outcome:
    id: str
    figure: str
    applied: bool
    detail: str


def load(path: Path) -> dict:
    with open(path, "rb") as fh:
        d = tomllib.load(fh)
    for key in ("policy", "decision", "evidence", "rejected_claim", "fixed_text"):
        d.setdefault(key, [])
    return d


def year_ok(decisions: dict, year: int) -> bool:
    return decisions.get("meta", {}).get("reporting_year") == year


def apply(decisions: dict, facts: dict, year: int) -> list[Outcome]:
    """A decision applies only if the figure is in conflict and every observed value is still exactly the same."""
    out = []
    for d in decisions["decision"]:
        fig = facts.get(d["figure"])
        if not year_ok(decisions, year):
            out.append(Outcome(d["id"], d["figure"], False,
                               f"decizia e pentru anul {decisions.get('meta', {}).get('reporting_year')}, nu pentru {year}"))
            continue
        if fig is None:
            out.append(Outcome(d["id"], d["figure"], False, f"figura «{d['figure']}» nu există în catalog"))
            continue
        if fig.status not in ("conflict", "uncertain"):
            out.append(Outcome(d["id"], d["figure"], False, f"nu e necesară: figura are starea «{fig.status}»"))
            continue
        changed = []
        for fid, seen in d.get("observed", {}).items():
            now = facts.get(fid)
            now_v = now.value if now is not None else None
            if fid == d["figure"] and now is not None and now.value is None:
                now_v = now.computed
            if now_v is None or now_v != Decimal(seen):
                changed.append(f"{fid}: decizia a fost luată pe {seen}, acum {plain(now_v) if now_v is not None else 'lipsă'}")
        if changed or not d.get("observed"):
            why = "; ".join(changed) or "decizia nu indică valorile pe care a fost luată"
            out.append(Outcome(d["id"], d["figure"], False, f"nu se aplică, valorile s-au schimbat: {why}"))
            continue
        if d["choice"] == "computed":
            value = fig.computed
        else:
            src = facts.get(d["choice"])
            value = src.value if src is not None else None
        if value is None:
            out.append(Outcome(d["id"], d["figure"], False, f"alegerea «{d['choice']}» nu are valoare"))
            continue
        fig.status, fig.value = "decided", value
        fig.source += f" (decizia «{d['id']}», {d['decided_by']}, {d['decided_on']})"
        fig.notes.append(f"conflict rezolvat prin decizia «{d['id']}»: {' '.join(d['reason'].split())}")
        out.append(Outcome(d["id"], d["figure"], True,
                           f"aplicată: valorile observate sunt identice ({', '.join(f'{k} = {v}' for k, v in d['observed'].items())})"))
    return out
