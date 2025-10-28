import sys
from pathlib import Path

# Ensure src is on path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from anki_core import build_output_instructions, build_prompt, parse_cards_from_output
from pdf2anki_types import Card


def test_build_output_instructions_basic():
    txt = build_output_instructions("basic", 3)
    assert "Question:" in txt and "Answer:" in txt
    assert "cloze" not in txt.lower()


def test_build_output_instructions_cloze():
    txt = build_output_instructions("cloze", 2)
    assert "Cloze:" in txt and "Extra:" in txt
    assert "Question:" not in txt


def test_build_prompt_contains_focus_and_content_truncation():
    content = "X" * 10000
    prompt = build_prompt("basic", 5, "mixed", content)
    assert "key concepts" in prompt
    # truncated
    assert len(prompt) < 6000


def test_parse_basic_cards_from_output():
    output = (
        "1. Question: What is Python?\n   Answer: A programming language.\n\n"
        "2. Question: Year?\n   Answer: 1991"
    )
    cards = parse_cards_from_output(output, note_type="basic")
    assert len(cards) == 2
    assert cards[0].question == "What is Python?"
    assert cards[0].answer.startswith("A programming language")
    assert cards[0].note_type == "basic"


def test_parse_cloze_cards_from_output():
    output = (
        "1. Cloze: The capital of France is {{c1::Paris}}.\n   Extra: City in Europe\n\n"
        "2. Cloze: Water boils at {{c1::100}} °C.\n   Extra: At sea level"
    )
    cards = parse_cards_from_output(output, note_type="cloze")
    assert len(cards) == 2
    assert "{{c1::Paris}}" in cards[0].question
    assert cards[0].note_type == "cloze"

