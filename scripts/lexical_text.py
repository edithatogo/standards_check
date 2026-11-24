"""Shared Unicode-aware lexical normalization (not fidelity normalization)."""
import re
import unicodedata


def normalise(text: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))
