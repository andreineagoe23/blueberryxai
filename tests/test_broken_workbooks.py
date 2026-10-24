"""Broken copies of registru_2025.xlsx: each must give the right value, or a visible gap or conflict."""

import re
from decimal import Decimal

from sfcr.compose import GAP_RE

GAP = "[de completat:"
STALE_2024 = ["284,6", "251,3", "33,3", "187,4 %", "45,6"]


def para(a, start: str) -> str:
    return next(line for line in a.draft.text.splitlines() if line.startswith(start))


def outside_gaps(a) -> str:
    return re.sub(GAP_RE, "", a.draft.text)


def scr_para(a) -> str:
    return next(line for line in a.draft.text.splitlines() if "Rata de solvabilitate a fost de" in line)


def assert_no_2024_figures(a):
    for figure in STALE_2024:
        assert figure not in a.draft.text, figure


def test_real_workbook(run):
    a = run()
    f = a.facts
    assert f["own_funds_total"].value == Decimal("293699300") and f["own_funds_total"].status == "ok"
    assert f["scr"].value == Decimal("148763200")
    assert f["mcr"].status == "missing"
    assert f["solvency_ratio"].status == "decided"
    assert "293,7 mil. lei" in a.draft.text and "197,4 %" in a.draft.text
    assert "în scădere față de 151,9 mil. lei la sfârșitul anului 2024, în principal ca urmare a scăderii " \
           "riscului de piață" in a.draft.text
    assert para(a, "[de completat: Cerința de capital minim")
    assert "acoperită integral" not in a.draft.text.replace("«a fost acoperită integral»", "")
    assert ("Capital_vechi", "foaie ascunsă (titlu «NU SE FOLOSEȘTE (copie 2024)»)") in a.wb.ignored
    assert_no_2024_figures(a)


def test_rows_moved(run):
    def change(wb):
        ws = wb["Capital"]
        ws.move_range("A5:E12", rows=3, translate=True)
        ws["B5"] = "Notă: rânduri inserate de un coleg"
    a = run(change)
    assert a.facts["own_funds_total"].value == Decimal("293699300")
    assert a.facts["own_funds_total"].cell == "C11"
    assert a.facts["scr"].cell == "C13"
    assert "293,7 mil. lei" in a.draft.text and "148,8 mil. lei" in a.draft.text


def test_formula_without_stored_value_is_recalculated(run):
    a = run(lambda wb: None)  # saving with openpyxl drops every stored formula result
    total = a.facts["own_funds_total"]
    assert total.value == Decimal("293699300")
    assert "fără valoare salvată" in total.reason


def test_unit_back_to_lei(run):
    def change(wb):
        ws = wb["Capital"]
        ws["A2"] = "Valori în lei"
        for row in ws.iter_rows(min_row=5, min_col=3, max_col=4):
            for c in row:
                if isinstance(c.value, (int, float)) and c.row != 12:
                    c.value = round(c.value * 1000)
    a = run(change)
    assert a.facts["own_funds_t1"].value == Decimal("262449600")
    assert a.facts["scr"].value == Decimal("148763200")
    assert "148,8 mil. lei" in a.draft.text


def test_unit_missing(run):
    a = run(lambda wb: wb["Capital"].__setitem__("A2", None))
    assert a.facts["own_funds_total"].status == "uncertain"
    assert "nu indică unitatea" in " ".join(a.facts["own_funds_total"].problems)
    assert "fondurile proprii eligibile" in para(a, "La 31 decembrie 2025, fondurile")
    assert GAP in para(a, "La 31 decembrie 2025, fondurile")
    assert_no_2024_figures(a)


def test_unit_label_wrong_is_caught_by_magnitude(run):
    # Header says lei, values still in thousands: 293.699 lei against 284,6 mil. lei last year.
    a = run(lambda wb: wb["Capital"].__setitem__("A2", "Valori în lei"))
    assert a.facts["own_funds_total"].status == "uncertain"
    assert "eroare de unitate" in " ".join(a.facts["own_funds_total"].problems)
    assert "0,3 mil. lei" not in a.draft.text


def test_unknown_unit(run):
    a = run(lambda wb: wb["Capital"].__setitem__("A2", "Valori în mii euro"))
    assert a.facts["scr"].status == "uncertain"
    assert "nu e recunoscută" in " ".join(a.facts["scr"].problems)


def test_hidden_sheet_made_visible_and_renamed(run):
    def change(wb):
        ws = wb["Capital_vechi"]
        ws.sheet_state = "visible"
        ws.title = "Capital 2"
    a = run(change)
    assert any(name == "Capital 2" for name, _ in a.wb.ignored)
    assert a.facts["own_funds_total"].value == Decimal("293699300")
    assert_no_2024_figures(a)


def test_old_copy_disguised_as_capital_is_ambiguous(run):
    def change(wb):
        ws = wb["Capital_vechi"]
        ws.sheet_state = "visible"
        ws.title = "Capital 2"
        ws["A1"] = "Fonduri proprii și cerințe de capital"
    a = run(change)
    # Two visible sheets claim to be "Capital": a label found on both is not chosen.
    assert a.facts["scr"].status == "uncertain"
    assert "Capital 2" in " ".join(a.facts["scr"].problems)
    assert GAP in scr_para(a)
    assert_no_2024_figures(a)


def test_renamed_capital_sheet_found_by_title(run):
    a = run(lambda wb: setattr(wb["Capital"], "title", "Fonduri proprii"))
    assert a.facts["own_funds_total"].sheet == "Fonduri proprii"
    assert "titlul" in a.facts["own_funds_total"].reason


def test_duplicate_label_is_not_chosen(run):
    def change(wb):
        ws = wb["Capital"]
        ws["B14"], ws["C14"] = "SCR", 150000
    a = run(change)
    assert a.facts["scr"].status == "uncertain"
    assert "mai multe rânduri" in " ".join(a.facts["scr"].problems)
    assert GAP in scr_para(a)
    assert GAP in scr_para(a).split("Rata de solvabilitate")[1]


def test_label_variants(run):
    def change(wb):
        ws = wb["Capital"]
        ws["B5"] = "  fonduri proprii eligibile SCR ,  NIVEL 1 "
        ws["B10"] = "Cerinţa de capital de solvabilitate (SCR)"  # cedilla ţ
    a = run(change)
    assert a.facts["own_funds_t1"].status == "ok"
    assert a.facts["scr"].value == Decimal("148763200")


def test_mcr_filled_and_covered_by_tier_1(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C11", 44628.96))
    assert a.facts["mcr"].status == "ok"
    assert "Cerința de capital minim (MCR) a fost de 44,6 mil. lei și a fost acoperită integral." in a.draft.text


def test_mcr_not_covered_by_tier_1_alone(run):
    def change(wb):
        ws = wb["Capital"]
        ws["C5"], ws["C6"], ws["C11"] = 40000, 253699.3, 44628.96
    a = run(change)
    line = para(a, "Cerința de capital minim (MCR) a fost de 44,6 mil. lei")
    assert "acoperită integral" not in line and GAP in line


def test_mcr_outside_corridor(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C11", 148763.2))
    assert a.facts["mcr"].status == "conflict"
    assert para(a, "[de completat: Cerința de capital minim")


def test_mcr_copied_from_last_year(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C11", 45570))
    assert a.facts["mcr"].status == "conflict"
    assert "45,6" not in a.draft.text


def test_ratio_corrected_needs_no_decision(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C12", 1.974))
    assert a.facts["solvency_ratio"].status == "ok"
    assert "197,4 %" in a.draft.text
    assert any("nu e necesară" in o.detail for o in a.outcomes)


def test_ratio_wrong_otherwise_reopens_the_conflict(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C12", 1.9))
    assert a.facts["solvency_ratio"].status == "conflict"
    assert any(not o.applied and "s-au schimbat" in o.detail for o in a.outcomes)
    line = scr_para(a)
    assert "Rata de solvabilitate a fost de [de completat:" in line
    assert "190,0 %" in line and "197,4 %" in line  # both values named in the gap


def test_decision_not_carried_to_changed_own_funds(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C7", 1000))  # tier 3 > 0 changes the total
    assert "Societatea a deținut fonduri proprii de nivel 3 de 1,0 mil. lei." in a.draft.text
    assert "294,7 mil. lei" in a.draft.text
    assert a.facts["solvency_ratio"].status == "conflict"
    assert "Rata de solvabilitate a fost de [de completat:" in a.draft.text


def test_scr_differs_between_sheets(run):
    a = run(lambda wb: wb["SCR_module"].__setitem__("C11", 150000))
    assert a.facts["scr"].status == "conflict"
    assert GAP in scr_para(a)
    assert "148,8 mil. lei" not in outside_gaps(a)


def test_number_stored_as_text(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C10", "148.763,2"))
    assert a.facts["scr"].status == "uncertain"
    assert "conține text" in " ".join(a.facts["scr"].problems)
    assert "148,8" not in scr_para(a)


def test_tier_sum_broken(run):
    def change(wb):
        ws = wb["Capital"]
        ws["C8"] = 300000  # typed over the formula
    a = run(change)
    assert a.facts["own_funds_total"].status == "conflict"
    assert any(r.id == "fonduri-proprii-niveluri" and r.result == "eșuat" for r in a.results)
    assert "300,0 mil. lei" not in outside_gaps(a)


def test_tier_2_missing(run):
    def change(wb):
        ws = wb["Capital"]
        ws["B6"], ws["C6"] = None, None
    a = run(change)
    assert a.facts["own_funds_t2"].status == "missing"
    assert a.facts["own_funds_total"].status != "ok"


def test_capital_sheet_renamed_and_retitled(run):
    def change(wb):
        ws = wb["Capital"]
        ws.title, ws["A1"] = "Foaie1", "Situație"
    a = run(change)
    # Unique labels are still found on any visible sheet; "SCR" is now on two sheets and is not chosen.
    assert a.facts["own_funds_total"].value == Decimal("293699300")
    assert a.facts["own_funds_total"].notes
    assert a.facts["scr"].status == "uncertain"
    assert GAP in scr_para(a)


def test_sheets_reordered(run):
    def change(wb):
        wb.move_sheet("Capital", offset=-5)
        wb.move_sheet("Prime", offset=3)
    a = run(change)
    assert a.facts["solvency_ratio"].status == "decided"
    assert "197,4 %" in a.draft.text


def test_ratio_as_formula(run):
    def change(wb):
        ws = wb["Capital"]
        ws["C12"] = "=C8/C10"
    a = run(change)
    assert a.facts["solvency_ratio_reported"].value is not None
    assert a.facts["solvency_ratio"].status == "ok"


def test_mcr_filled_while_note_says_pending(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C11", 44628.96))
    assert any("de confirmat" in n for n in a.facts["mcr"].notes)


def test_scr_rose_so_the_falling_cause_is_dropped(run):
    def change(wb):
        wb["Capital"]["C10"] = wb["SCR_module"]["C11"] = 160000
        wb["SCR_module"]["C10"] = 24507  # operational risk, so that the SCR_module checks still pass
    a = run(change)
    line = scr_para(a)
    assert "160,0 mil. lei, în creștere față de 151,9 mil. lei" in line
    assert "riscului de piață" not in line
    assert "[de completat: cauza variației" in line and "«în scădere»" in line


def test_scr_change_below_threshold_is_not_called_a_fall(run):
    def change(wb):
        wb["Capital"]["C10"] = wb["SCR_module"]["C11"] = 151500
        wb["SCR_module"]["C10"] = 16007
    a = run(change)
    line = scr_para(a)
    assert "în scădere" not in line and "în creștere" not in line
    assert "(-0,26 %) e sub pragul de 0,50 %" in line


def test_unit_in_millions(run):
    def change(wb):
        for name in ("Capital", "SCR_module"):
            ws = wb[name]
            ws["A2"] = "Valori în milioane lei"
            for row in ws.iter_rows(min_row=5, min_col=3, max_col=4):
                for c in row:
                    if isinstance(c.value, (int, float)) and not (name == "Capital" and c.row == 12):
                        c.value = c.value / 1000
    a = run(change)
    assert a.facts["own_funds_total"].value == Decimal("293699300")
    assert a.facts["solvency_ratio"].status == "decided"
    assert "293,7 mil. lei" in a.draft.text and "197,4 %" in a.draft.text


def test_column_headers_with_the_year(run):
    def change(wb):
        for name in ("Capital", "SCR_module"):
            wb[name]["C3"], wb[name]["D3"] = "31.12.2025", "31.12.2024"
    a = run(change)
    assert a.facts["scr"].value == Decimal("148763200")
    assert a.facts["scr_prior_col"].value == Decimal("151900000")


def test_labels_moved_to_column_a(run):
    def change(wb):
        ws = wb["Capital"]
        for r in range(3, 13):
            ws.cell(r, 1).value, ws.cell(r, 2).value = ws.cell(r, 2).value, None
    a = run(change)
    assert a.facts["own_funds_total"].value == Decimal("293699300")
    assert "197,4 %" in a.draft.text


def test_mcr_typed_as_text(run):
    a = run(lambda wb: wb["Capital"].__setitem__("C11", "44.629,0"))
    assert a.facts["mcr"].status == "uncertain"
    assert "44,6" not in a.draft.text
    assert para(a, "[de completat: Cerința de capital minim")


def test_diversification_typed_negative(run):
    def change(wb):
        ws = wb["SCR_module"]
        ws["B8"], ws["C8"] = "Diversificare (valoare negativă)", -22431.9
    a = run(change)
    assert any(r.id == "scr-baza-din-module" and r.result == "trecut" for r in a.results)
    assert "148,8 mil. lei" in scr_para(a)
