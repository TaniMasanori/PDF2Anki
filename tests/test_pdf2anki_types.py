import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from pdf2anki_types import Card


def test_basic_tsv_row():
    card = Card(question="Q1", answer="A1", tags=["t1", "t2"], note_type="basic")
    row = card.to_tsv_row()
    assert row.split("\t")[:2] == ["Q1", "A1"]
    assert row.endswith("t1;t2")


def test_cloze_tsv_row_uses_extra():
    card = Card(question="The capital is {{c1::Paris}}.", answer="", extra="Europe", tags=["geo"], note_type="cloze")
    row = card.to_tsv_row()
    fields = row.split("\t")
    assert fields[0].startswith("The capital is")
    assert fields[1] == "Europe"
    assert fields[2] == "geo"












