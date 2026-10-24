from decimal import Decimal

from sfcr.money import fmt_count, fmt_mil, fmt_pct, mil, to_decimal


def test_half_up_on_x5():
    # 412.350.000 lei is the 2024 premiums total: half-even or float could give 412,3.
    assert fmt_mil(Decimal(412_350_000)) == "412,4 mil. lei"
    assert mil(Decimal(250_000)) == "0,3"
    assert fmt_pct(Decimal("1.87350")) == "187,4 %"
    assert fmt_pct(Decimal("0.00049")) == "0,0 %"


def test_thousands_separator_and_count():
    assert fmt_mil(Decimal("1234567890")) == "1.234,6 mil. lei"
    assert fmt_count(Decimal(18420)) == "18.420"
    assert fmt_count(Decimal(437)) == "437"


def test_total_is_not_the_sum_of_rounded_parts():
    t1, t2 = Decimal("262449600"), Decimal("31249700")
    assert (mil(t1), mil(t2)) == ("262,4", "31,2")
    assert mil(t1 + t2) == "293,7"  # 262,4 + 31,2 would be 293,6


def test_round_once_on_the_unrounded_quotient():
    own_funds, scr = Decimal("293699300"), Decimal("148763200")
    assert fmt_pct(own_funds / scr) == "197,4 %"


def test_decimal_from_float_keeps_what_was_typed():
    assert to_decimal(262449.6) == Decimal("262449.6")
    assert to_decimal(0.1) + to_decimal(0.2) == Decimal("0.3")
