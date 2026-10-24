"""Section E from the template: figures in slots, direction computed, cause only from evidence.

Anything that cannot be filled correctly is written as [de completat: reason].
The same template, read as a pattern, extracts last year's published figures (see sentence_regex).
"""

import re
from dataclasses import dataclass, field
from decimal import Decimal

from .checks import FAILED, PASSED, record
from .locate import STATUS, Fact
from .money import fmt, fmt_mil, plain

SLOT = re.compile(r"\{([a-z0-9_]+)(?:\.([a-z0-9_-]+))?\}")
NUM = r"\d{1,3}(?:\.\d{3})*,\d"
GAP_RE = r"\[de completat:[^\]]*\]"


def gap(reason: str) -> str:
    return f"[de completat: {reason}]"


@dataclass
class Slot:
    text: str | None = None
    reason: str | None = None  # set when the slot is a gap
    placements: list = field(default_factory=list)  # (fact id, number text as in the draft)


@dataclass
class Draft:
    text: str
    body: str  # the section without the title lines
    gaps: list  # (topic, reason)
    placements: list  # (fact id, number text), in order of appearance


def reason_of(f: Fact, ctx) -> str:
    why = "; ".join(f.problems) or f"starea «{STATUS[f.status]}»"
    for item in ctx.decisions["evidence"]:
        v = ctx.verified.get(item["id"])
        if item.get("explains_gap") == f.id and v and v.ok:
            why += f"; {v.source}: „{item['quote']}”"
    return f"{f.description}: {why}"


class Context:
    def __init__(self, *, year, company, facts, template, decisions, verified, comparisons):
        self.year, self.company, self.facts, self.template = year, company, facts, template
        self.decisions, self.verified, self.comparisons = decisions, verified, comparisons
        self.fixed = {t["id"]: t for t in decisions["fixed_text"]}

    def slot(self, name: str, arg: str | None) -> Slot:
        if name == "year":
            return Slot(str(self.year))
        if name == "prior_year":
            return Slot(str(self.year - 1))
        if name == "company":
            return Slot(self.company)
        if name == "comparison":
            return self.comparisons[arg]
        if name == "evidence":
            f = self.facts.get(arg)
            if f is None:
                return Slot(reason=f"nicio dovadă pentru «{arg}» în config/decisions.toml")
            if not f.usable:
                return Slot(reason=reason_of(f, self))
            t = fmt(f.value, f.kind)
            return Slot(t, placements=[(f.id, t)])
        if name == "clause":
            v = self.verified.get(arg)
            if v is None or not v.ok:
                return Slot(reason=f"dovada «{arg}»: {v.detail if v else 'lipsește din config/decisions.toml'}")
            return Slot(self.template["clauses"][arg])
        if name == "coverage":
            return self._coverage(arg)
        f = self.facts.get(name)
        if f is None:
            return Slot(reason=f"slotul «{name}» nu există în catalog")
        if not f.usable:
            return Slot(reason=reason_of(f, self))
        t = fmt(f.value, f.kind)
        return Slot(t, placements=[(f.id, t)])

    def _coverage(self, fid: str) -> Slot:
        rule = self.template["coverage"][fid]
        req, by = self.facts[fid], self.facts[rule["covered_by"]]
        if not req.usable:
            return Slot(reason=f"«{rule['text']}» nu se poate afirma fără {req.id.upper()}")
        if not by.usable:
            return Slot(reason=f"acoperirea nu se poate verifica: {reason_of(by, self)}")
        if by.value >= req.value:
            return Slot(rule["text"])
        return Slot(reason=f"{by.description} ({fmt_mil(by.value)}) nu acoperă singur {req.description} "
                           f"({fmt_mil(req.value)}); partea eligibilă din nivelul 2 nu se poate stabili din registru")

    def render_text(self, text: str, whole_gap_on=()) -> Slot:
        out, pos, reasons, placements, whole = [], 0, [], [], []
        for m in SLOT.finditer(text):
            out.append(text[pos:m.start()])
            s = self.slot(m.group(1), m.group(2))
            if s.text is None:
                lead = ", " if m.group(1) == "clause" else ""
                out.append(lead + gap(s.reason))
                reasons.append(s.reason)
                key = m.group(1) + (f".{m.group(2)}" if m.group(2) else "")
                if key in whole_gap_on:
                    whole.append(s.reason)
            else:
                out.append(s.text)
                placements += s.placements
                if s.reason:
                    reasons.append(s.reason)
            pos = m.end()
        out.append(text[pos:])
        if whole:
            r = "; ".join(reasons)
            return Slot(gap(r), r, [])
        return Slot("".join(out), "; ".join(reasons) or None, placements)

    def sentence(self, spec: dict) -> Slot:
        if "fixed" in spec:
            t = self.fixed.get(spec["fixed"])
            if t is None:
                r = f"textul fix «{spec['fixed']}» nu e aprobat în config/decisions.toml"
                return Slot(gap(r), r)
            return Slot(t["text"])
        if "variant" in spec:
            f = self.facts[spec["variant"]]
            if not f.usable:
                r = reason_of(f, self)
                return Slot(gap(r), r)
            return self.render_text(spec["zero"] if f.value == 0 else spec["positive"])
        for ev in spec.get("requires", []):
            v = self.verified.get(ev)
            if v is None or not v.ok:
                r = f"{spec['topic']}; dovada «{ev}»: {v.detail if v else 'lipsește din config/decisions.toml'}"
                return Slot(gap(r), r)
        return self.render_text(spec["text"], spec.get("whole_gap_on", []))


def compose(ctx: Context) -> Draft:
    t = ctx.template
    lines = [ctx.render_text(h).text for h in t["header"]] + [""]
    start = len(lines)
    gaps, placements = [], []
    for block in t["block"]:
        if "heading" in block:
            lines += [block["heading"], ""]
            continue
        parts = []
        for spec in block["sentences"]:
            s = ctx.sentence(spec)
            parts.append(s.text)
            placements += s.placements
            if s.reason:
                gaps.append((spec.get("topic") or spec.get("fixed") or spec.get("variant") or spec["text"][:60], s.reason))
        lines += [" ".join(parts), ""]
    return Draft("\n".join(lines).rstrip() + "\n", "\n".join(lines[start:]).strip() + "\n", gaps, placements)


# ---------------------------------------------------------------------------
# Last year's value and the direction of change
# ---------------------------------------------------------------------------

def _pct2(fraction: Decimal) -> str:
    """'-0,26 %': a relative change in a gap's reason, two decimals so small changes stay visible."""
    return f"{fraction * 100:.2f} %".replace(".", ",")


def resolve_comparison(fid, spec, year, facts, prior_facts, published, decisions, verified, tol,
                       results) -> tuple[Slot, Fact]:
    """Direction against last year's value, confirmed by at least two agreeing sources."""
    cur = facts[fid]
    prior_fact = Fact(f"{fid}_prior_year", f"{cur.description}, anul anterior", cur.kind, "ok", column="prior")
    sources = []
    pf = prior_facts.get(fid) if prior_facts else None
    if pf is not None and pf.usable:
        sources.append((pf.source, pf.value))
    pc = facts.get(spec.get("prior_column_figure"))
    if pc is not None and pc.usable:
        sources.append((pc.source, pc.value))
    listed = [f"{s} = {plain(v)}" for s, v in sources] + ([f"{published[0]}: «{published[1]}»"] if published else [])
    prior_fact.source = "; ".join(listed)

    problem = None
    if not sources:
        problem = "valoarea exactă din anul anterior nu e disponibilă în registre"
    elif len(sources) + (1 if published else 0) < 2:
        problem = f"o singură sursă pentru valoarea din anul anterior ({listed[0]}); sunt necesare cel puțin două"
    elif any(abs(v - sources[0][1]) > Decimal(tol["money_lei"]) for _, v in sources):
        problem = "sursele pentru anul anterior nu concordă: " + "; ".join(listed)
    elif published and published[1] != fmt_mil(sources[0][1]):
        problem = f"raportul publicat spune «{published[1]}», registrul dă {fmt_mil(sources[0][1])}"
    if problem:
        prior_fact.flag("conflict" if sources else "missing", problem)
        record(results, facts, f"an-anterior:{fid}", "valoarea din anul anterior, din cel puțin două surse",
                [fid], FAILED, problem)
        return Slot(reason=f"comparația cu anul anterior: {problem}"), prior_fact
    prior = sources[0][1]
    prior_fact.value = prior
    prior_fact.reason = "aceeași valoare în toate sursele: " + "; ".join(listed)
    record(results, facts, f"an-anterior:{fid}", "valoarea din anul anterior, din cel puțin două surse",
            [fid], PASSED, "; ".join(listed))
    if not cur.usable:
        return Slot(reason=f"comparația cu anul anterior nu se poate face fără {cur.id.upper()}"), prior_fact

    change = (cur.value - prior) / prior
    threshold = Decimal(tol["direction_min_relative"])
    if abs(change) < threshold:
        return Slot(reason=f"variația față de anul anterior ({_pct2(change)}) e sub pragul de {_pct2(threshold)} "
                           f"din config; formularea se decide de om"), prior_fact
    direction = "up" if change > 0 else "down"
    prior_text = fmt_mil(prior)
    cause, why = None, None
    for item in decisions["evidence"]:
        if item.get("explains") != fid:
            continue
        v = verified.get(item["id"])
        if item.get("direction") != direction:
            said = spec.get(item.get("direction"), item.get("direction"))
            why = why or (f"cauza variației: dovada «{item['id']}» explică o variație «{said}», "
                          f"dar valoarea calculată este «{spec[direction]}»")
        elif v is None or not v.ok:
            why = f"cauza variației: dovada «{item['id']}»: {v.detail if v else 'neverificată'}"
        else:
            cause, why = item["clause"], None
            break
    if cause is None:
        why = why or "cauza variației nu are nicio dovadă aprobată în config/decisions.toml"
        cause = gap(why)
    text = spec["text"].format(direction=spec[direction], prior=prior_text, prior_year=year - 1, cause=cause)
    return Slot(text, why, [(prior_fact.id, prior_text)]), prior_fact


# ---------------------------------------------------------------------------
# The template read as a pattern (back-test, last year's published figures)
# ---------------------------------------------------------------------------

def _group(name: str) -> str:
    return re.sub(r"[^0-9a-zA-Z_]", "_", name.replace(".", "__"))


def sentence_regex(spec: dict, template: dict, decisions: dict, kinds: dict, year: int, company: str) -> str:
    def money(g):
        return rf"(?P<{g}>{NUM} mil\. lei|{GAP_RE})"

    def text_regex(text):
        out, pos = [], 0
        for m in SLOT.finditer(text):
            out.append(re.escape(text[pos:m.start()]))
            name, arg = m.group(1), m.group(2)
            g = _group(name + (f".{arg}" if arg else ""))
            if name in ("year", "prior_year"):
                out.append(str(year if name == "year" else year - 1))
            elif name == "company":
                out.append(re.escape(company))
            elif name == "clause":
                out.append(rf"(?P<{g}>{re.escape(template['clauses'][arg])}|, {GAP_RE})?")
            elif name == "coverage":
                out.append(rf"(?P<{g}>.*?)")
            elif name == "comparison":
                c = template["comparison"][arg]
                direction = rf"(?P<{g}__direction>{re.escape(c['up'])}|{re.escape(c['down'])})"
                inner = (re.escape(c["text"])
                         .replace(r"\{direction\}", direction)
                         .replace(r"\{prior\}", money(f"{g}__prior"))
                         .replace(r"\{prior_year\}", str(year - 1))
                         .replace(r"\{cause\}", rf"(?P<{g}__cause>.*?)"))
                out.append(rf"(?:{inner}|{GAP_RE})")
            elif kinds.get(name) == "ratio":
                out.append(rf"(?P<{g}>{NUM} %|{GAP_RE})")
            else:
                out.append(money(g))
            pos = m.end()
        out.append(re.escape(text[pos:]))
        return "".join(out)

    # A sentence that is wholly a gap is not matched: it would match any other gap in the report.
    if "fixed" in spec:
        t = next((x["text"] for x in decisions["fixed_text"] if x["id"] == spec["fixed"]), None)
        return re.escape(t) if t else r"(?!)"
    if "variant" in spec:
        return rf"(?:{text_regex(spec['zero'])}|{text_regex(spec['positive'])})"
    return text_regex(spec["text"])


def published(template, decisions, kinds, text, year, company) -> list:
    """Each template sentence, filled with `year`, matched against a report: (spec, groups or None)."""
    body = " ".join(text.split())
    out = []
    for block in template["block"]:
        for spec in block.get("sentences", []):
            m = re.search(sentence_regex(spec, template, decisions, kinds, year, company), body)
            out.append((spec, m.groupdict() if m else None))
    return out
