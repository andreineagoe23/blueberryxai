import copy

from sfcr import backtest
from sfcr.outputs import write_all


def test_decision_for_another_year_does_not_apply(run, cfg):
    other = copy.deepcopy(cfg)
    other["decisions"]["meta"]["reporting_year"] = 2024
    a = run(config=other)
    assert a.facts["solvency_ratio"].status == "conflict"
    assert "Rata de solvabilitate a fost de [de completat:" in a.draft.text
    # Evidence is year-bound too: no cause, no dividends, no standard-formula sentence.
    assert "riscului de piață" not in a.draft.text
    assert "15,0 mil. lei" not in a.draft.text


def test_altered_quote_is_rejected(run, cfg):
    other = copy.deepcopy(cfg)
    item = next(e for e in other["decisions"]["evidence"] if e["id"] == "scr-change-cause")
    item["quote"] = item["quote"].replace("în principal ", "")
    item["clause"] = item["clause"].replace("în principal ", "")
    a = run(config=other)
    assert not a.verified["scr-change-cause"].ok
    assert "în scădere față de 151,9 mil. lei la sfârșitul anului 2024, [de completat: cauza" in a.draft.text


def test_cause_must_match_the_computed_direction(run, cfg):
    other = copy.deepcopy(cfg)
    next(e for e in other["decisions"]["evidence"] if e["id"] == "scr-change-cause")["direction"] = "up"
    a = run(config=other)
    assert "riscului de piață" not in a.draft.text
    assert "în scădere" in a.draft.text


def test_dividend_amount_must_follow_its_label(run, cfg):
    other = copy.deepcopy(cfg)
    item = next(e for e in other["decisions"]["evidence"] if e["id"] == "dividends-paid-2025")
    item["quote"], item["value_lei"] = "(12.000.000)", "12000000"  # last year's column
    a = run(config=other)
    assert not a.verified["dividends-paid-2025"].ok
    assert "12,0 mil. lei" not in a.draft.text


def test_backtest_finds_the_2024_mapping_errors(inputs, cfg):
    _, summary = backtest.run(cfg, inputs)
    wrong = {r["text"]: r for r in summary["mapping_wrong"]}
    assert list(wrong) == ["12,6"] and "Investitii!C6" in wrong["12,6"]["detail"]
    assert [r["text"] for r in summary["mapping_warned"]] == ["12,4"]
    assert summary["slots_bad"] == 0
    assert summary["slots_expected"] == 1  # tier 3: in 2024 the sentence rested on a missing row


def test_output_is_deterministic(run, inputs, cfg, tmp_path_factory):
    a = run()
    bt_md, bt = backtest.run(cfg, inputs)
    from conftest import ROOT
    outs = []
    for _ in range(2):
        out = tmp_path_factory.mktemp("out")
        write_all(a, cfg, inputs, ROOT / "config", out, bt_md, bt)
        outs.append({p.name: p.read_bytes() for p in out.iterdir()})
    assert outs[0] == outs[1] and len(outs[0]) == 7


def test_draft_rules(run):
    a = run()
    checks = {r.id: r.result for r in a.results}
    assert checks["text:fiecare-suma-are-sursa"] == "trecut"
    assert checks["text:fara-reinsurance-improved-ratio"] == "trecut"
    assert checks["text:formulari-straine:raport_Asigurari_Dunarea_2024_extras.txt"] == "trecut"
    assert "prime brute" not in a.draft.text


def test_next_year_reads_this_years_draft(run, cfg):
    from sfcr.compose import published
    a = run()
    kinds = {k: f.kind for k, f in a.facts.items()}
    groups = {}
    for spec, g in published(cfg["template"], cfg["decisions"], kinds, a.draft.text, 2025, cfg["run"]["company"]):
        groups.update(g or {})
    assert groups["scr"] == "148,8 mil. lei" and groups["comparison__scr__direction"] == "în scădere"
    assert "mcr" not in groups  # a gap is never read back as a figure
