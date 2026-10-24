"""Exact amounts and the report's number format (README §4 rule 5).

Amounts are Decimal lei; ratios are Decimal fractions. Rounding happens once, half up,
on the unrounded value, only when a number is written as text.
"""

from decimal import ROUND_HALF_UP, Decimal

MILLION = Decimal(1_000_000)
TENTH = Decimal("0.1")


def to_decimal(value) -> Decimal:
    """A number read from a workbook, as the Decimal it was typed as (repr, not binary float)."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"not a number: {value!r}")
    return Decimal(value) if isinstance(value, int) else Decimal(repr(value))


def _group(digits: str) -> str:
    """'293699' -> '293.699'."""
    out = []
    while len(digits) > 3:
        out.insert(0, digits[-3:])
        digits = digits[:-3]
    out.insert(0, digits)
    return ".".join(out)


def _one_decimal(x: Decimal) -> str:
    q = abs(x).quantize(TENTH, rounding=ROUND_HALF_UP)
    whole, frac = f"{q:f}".split(".")
    sign = "-" if x < 0 and q != 0 else ""
    return f"{sign}{_group(whole)},{frac}"


def mil(lei: Decimal) -> str:
    """'293,7' for 293.699.300 lei."""
    return _one_decimal(lei / MILLION)


def fmt_mil(lei: Decimal) -> str:
    return f"{mil(lei)} mil. lei"


def fmt_pct(fraction: Decimal) -> str:
    """'197,4 %' for 1.97427..."""
    return f"{_one_decimal(fraction * 100)} %"


def fmt_count(n: Decimal) -> str:
    """'18.420'."""
    q = n.quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return ("-" if q < 0 else "") + _group(str(abs(int(q))))


def fmt(value: Decimal, kind: str) -> str:
    return {"money": fmt_mil, "ratio": fmt_pct, "count": fmt_count}[kind](value)


def plain(value: Decimal) -> str:
    """Exact value for tables and decisions: no exponent, no trailing zeros."""
    s = f"{value:f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def parse_ro_amount(text: str) -> Decimal:
    """'(15.000.000)' or '15.000.000' or '1.234,5' -> Decimal (absolute value)."""
    t = text.strip().strip("()").replace(".", "").replace(",", ".")
    return Decimal(t)
