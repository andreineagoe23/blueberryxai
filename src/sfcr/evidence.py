"""Statements from the company's documents, used only if their quote is found verbatim."""

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import docx
import pypdf

from .money import parse_ro_amount, plain

AMOUNT = re.compile(r"\(?\d{1,3}(?:\.\d{3})+(?:,\d+)?\)?")


def _clean(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


class Documents:
    """Text of each input document, by page (a .txt or .docx is one page)."""

    def __init__(self, folder: Path):
        self.folder, self._pages = folder, {}

    def pages(self, name: str) -> list[str] | None:
        if name not in self._pages:
            path = self.folder / name
            if not path.is_file():
                self._pages[name] = None
            elif path.suffix == ".pdf":
                self._pages[name] = [_clean(p.extract_text() or "") for p in pypdf.PdfReader(path).pages]
            elif path.suffix == ".docx":
                self._pages[name] = [_clean("\n".join(p.text for p in docx.Document(path).paragraphs))]
            else:
                self._pages[name] = [_clean(path.read_text(encoding="utf-8"))]
        return self._pages[name]

    def find(self, name: str, quote: str) -> int | None:
        """1-based page where the quote occurs verbatim (whitespace aside), or None."""
        for i, text in enumerate(self.pages(name) or [], 1):
            if _clean(quote) in text:
                return i
        return None


@dataclass
class Verified:
    id: str
    ok: bool
    detail: str  # where it was found, or why it was rejected
    source: str = ""
    value: Decimal | None = None


def _where(docs: Documents, name: str, page: int) -> str:
    return f"{name}, p. {page}" if len(docs.pages(name)) > 1 or name.endswith(".pdf") else name


def verify(item: dict, docs: Documents) -> Verified:
    name, quote = item["document"], item["quote"]
    if docs.pages(name) is None:
        return Verified(item["id"], False, f"documentul {name} lipsește din folderul de intrare")
    page = docs.find(name, quote)
    if page is None:
        return Verified(item["id"], False, f"citatul «{quote}» nu se regăsește cuvânt cu cuvânt în {name}")
    source = f"{_where(docs, name, page)} ({item.get('location', '')})"
    clause = item.get("clause")
    if clause and _clean(clause) not in _clean(quote):
        return Verified(item["id"], False, f"clauza «{clause}» nu face parte din citat", source)
    value = None
    if "value_lei" in item:
        value = Decimal(item["value_lei"])
        if parse_ro_amount(quote) != value:
            return Verified(item["id"], False, f"citatul «{quote}» nu dă suma {plain(value)}", source)
        text = docs.pages(name)[page - 1]
        at = text.find(_clean(item["label"])) if item.get("label") else -1
        first = AMOUNT.search(text, at) if at >= 0 else None
        if item.get("label") and (first is None or first.group(0) != quote):
            got = first.group(0) if first else "nimic"
            return Verified(item["id"], False, f"prima sumă după eticheta «{item['label']}» în {name} este {got}, "
                                               f"nu {quote}", source)
        corr = item.get("corroborated_by")
        if corr:
            cpage = docs.find(corr["document"], corr["quote"]) if docs.pages(corr["document"]) else None
            amounts = [parse_ro_amount(a) for a in AMOUNT.findall(corr["quote"])]
            if cpage is None:
                return Verified(item["id"], False, f"coroborarea «{corr['quote']}» nu se regăsește în {corr['document']}",
                                source)
            if value not in amounts:
                return Verified(item["id"], False, f"coroborarea din {corr['document']} nu conține suma {plain(value)}",
                                source)
            source += f"; confirmat de {_where(docs, corr['document'], cpage)} ({corr.get('location', '')})"
    return Verified(item["id"], True, f"găsit cuvânt cu cuvânt: {source}", source, value)


def verify_all(decisions: dict, docs: Documents, year_ok: bool, year: int) -> dict[str, Verified]:
    out = {}
    for item in decisions["evidence"]:
        if not year_ok:
            out[item["id"]] = Verified(item["id"], False, f"dovezile din config/decisions.toml nu sunt pentru anul {year}")
        else:
            out[item["id"]] = verify(item, docs)
    for item in decisions["rejected_claim"]:
        c = item.get("contradicted_by")
        if c:
            out[item["id"]] = verify({"id": item["id"], **c}, docs)
    return out


def shared_ngrams(text: str, other: str, n: int) -> list[str]:
    """Word sequences of length n present in both texts (report rule 4)."""
    def grams(t):
        w = re.findall(r"\w+", unicodedata.normalize("NFC", t).lower())
        return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
    return sorted(grams(text) & grams(other))
