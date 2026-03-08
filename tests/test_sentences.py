"""Tests for sentence splitting (imports main app)."""

from pocket_tts_api import split_into_sentences


def test_split_into_sentences_single():
    assert split_into_sentences("Hello.") == ["Hello."]


def test_split_into_sentences_multiple():
    text = "First. Second! Third?"
    assert split_into_sentences(text) == ["First.", "Second!", "Third?"]


def test_split_into_sentences_empty():
    assert split_into_sentences("") == []
    assert split_into_sentences("   ") == []


def test_split_into_sentences_keeps_punctuation():
    assert split_into_sentences("Yes. No.") == ["Yes.", "No."]


def test_split_into_sentences_strips():
    assert split_into_sentences("  Hi.  Bye.  ") == ["Hi.", "Bye."]
