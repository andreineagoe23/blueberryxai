"""One year's analysis: extract, locate, check, decide, verify evidence, write the draft."""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from . import decisions as dec
from .checks import FAILED, PASSED, record, compare_prior, derive, run_checks
from .compose import GAP_RE, NUM, Context, compose, published, resolve_comparison
from .evidence import Documents, shared_ngrams, verify_all
from .locate import Fact, locate
from .workbook import load, normalize


class InputError(Exception):
    pass


@dataclass
class Analysis:
    year: int
    files: list  # input files read
    wb: object
    prior_wb: object
    facts: dict
    prior_facts: dict | None
    results: list
    outcomes: list
    verified: dict
    draft: object
    prior_published: list


def load_config(config_dir: Path) -> dict:
    cfg = {}
    for key, name in (("run", "run.toml"), ("catalogue", "catalogue.toml"), ("template", "template_E.toml")):
        with open(config_dir / name, "rb") as fh:
            cfg[key] = tomllib.load(fh)
    cfg["decisions"] = dec.load(config_dir / "decisions.toml")
    cfg["catalogue"].setdefault("derived", [])
    cfg["catalogue"].setdefault("check", [])
    return cfg


def input_name(cfg: dict, key: str, year: int) -> str:
    return cfg["run"]["inputs"][key].format(year=year, prior=year - 1)


def locate_all(wb, catalogue) -> dict:
    return {fig["id"]: locate(fig, wb, catalogue["sheets"]) for fig in catalogue["figure"]}


def analyse(year: int, folder: Path, cfg: dict) -> Analysis:
    run, cat, template, decisions = cfg["run"], cfg["catalogue"], cfg["template"], cfg["decisions"]
    tol = run["tolerances"]
    files = []

    wb_path = folder / input_name(cfg, "workbook", year)
    if not wb_path.is_file():
        raise InputError(f"lipsește registrul {wb_path}")
    wb = load(wb_path, run, year)
    files.append(wb_path)
    prior_path = folder / input_name(cfg, "prior_workbook", year)
    prior_wb = load(prior_path, run, year - 1) if prior_path.is_file() else None
    if prior_wb:
        files.append(prior_path)

    facts = locate_all(wb, cat)
    prior_facts = locate_all(prior_wb, cat) if prior_wb else None
    results = []
    compare_prior(facts, prior_facts, tol, prior_path.name, results)
    run_checks(facts, cat["check"], tol, results)
    derive(facts, cat["derived"], tol, results)
    outcomes = dec.apply(decisions, facts, year)

    docs = Documents(folder)
    verified = verify_all(decisions, docs, dec.year_ok(decisions, year), year)
    for item in decisions["evidence"]:
        files.append(folder / item["document"])
        if "corroborated_by" in item:
            files.append(folder / item["corroborated_by"]["document"])
        if "figure" in item:
            v = verified[item["id"]]
            facts[item["figure"]] = Fact(item["figure"], item["claim"], "money", "ok" if v.ok else "missing",
                                         value=v.value if v.ok else None, source=v.source,
                                         reason=f"dovada «{item['id']}», {v.detail}",
                                         problems=[] if v.ok else [f"dovada «{item['id']}»: {v.detail}"])

    for item in decisions["evidence"]:
        fact = facts.get(item.get("explains_gap", ""))
        if fact is not None and fact.usable and verified[item["id"]].ok:
            fact.notes.append(f"registrul are acum o valoare, dar {verified[item['id']].source} spune: "
                              f"„{item['quote']}”; de confirmat că valoarea e cea finală")

    kinds = {k: f.kind for k, f in facts.items()} | {d["id"]: "ratio" for d in cat["derived"]}
    report_path = folder / input_name(cfg, "prior_report", year)
    prior_published = []
    if report_path.is_file():
        files.append(report_path)
        prior_published = published(template, decisions, kinds, report_path.read_text(encoding="utf-8"),
                                    year - 1, run["company"])

    comparisons = {}
    for fid, spec in template.get("comparison", {}).items():
        pub = next(((report_path.name, g[fid]) for _, g in prior_published
                    if g and g.get(fid) and not g[fid].startswith("[")), None)
        slot, prior_fact = resolve_comparison(fid, spec, year, facts, prior_facts, pub, decisions, verified, tol,
                                              results)
        comparisons[fid] = slot
        facts[prior_fact.id] = prior_fact

    ctx = Context(year=year, company=run["company"], facts=facts, template=template, decisions=decisions,
                  verified=verified, comparisons=comparisons)
    draft = compose(ctx)
    _check_draft(draft, decisions, folder, cfg, year, results, files)
    return Analysis(year, files, wb, prior_wb, facts, prior_facts, results, outcomes, verified, draft, prior_published)


def _check_draft(draft, decisions, folder, cfg, year, results, files):
    """The written text itself: every amount traced, no rejected claim, no other company's wording."""
    shown = re.findall(rf"{NUM} (?:mil\. lei|%)", re.sub(GAP_RE, "", draft.text))
    placed = [t for _, t in draft.placements]
    untraced = [t for t in shown if t not in placed]
    record(results, {}, "text:fiecare-suma-are-sursa", "fiecare sumă și procent din text vine dintr-o figură",
            [], FAILED if untraced or len(shown) != len(placed) else PASSED,
            f"{len(shown)} în text, {len(placed)} cu sursă" + (f"; fără sursă: {', '.join(untraced)}" if untraced else ""))
    text_n = normalize(draft.text)
    for claim in decisions["rejected_claim"]:
        hits = [t for t in claim.get("forbidden_terms", []) if normalize(t) in text_n]
        record(results, {}, f"text:fara-{claim['id']}", f"textul nu conține afirmația respinsă «{claim['claim']}»",
                [], FAILED if hits else PASSED, f"găsit: {', '.join(hits)}" if hits else "niciun termen interzis")
    n = cfg["run"]["similarity"]["ngram_words"]
    for name in cfg["run"]["inputs"].get("other_company_texts", []):
        path = folder / name.format(year=year, prior=year - 1)
        if not path.is_file():
            record(results, {}, f"text:formulari-straine:{path.name}", "fără formulări din textul altei companii",
                    [], "nu s-a putut rula", f"{path.name} lipsește")
            continue
        files.append(path)
        shared = shared_ngrams(draft.body, path.read_text(encoding="utf-8"), n)
        record(results, {}, f"text:formulari-straine:{path.name}", "fără formulări din textul altei companii", [],
                FAILED if shared else PASSED,
                f"{len(shared)} secvențe comune de {n} cuvinte" + (f": {'; '.join(shared[:5])}" if shared else ""))
