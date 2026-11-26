"""Shared Unicode-aware lexical normalization (not fidelity normalization)."""

import math
import re
import unicodedata
from collections import Counter


def normalise(text: str) -> str:
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def term_counts(text, method):
    if method not in ("word", "char"):
        raise ValueError("unknown statistical retrieval method")
    normalized = normalise(text)
    if not normalized:
        return Counter()
    if method == "word":
        words = normalized.split()
        terms = Counter(words)
        terms.update(" ".join(pair) for pair in zip(words, words[1:], strict=False))
        return terms
    padded = f" {normalized} "
    return Counter(padded[i : i + 3] for i in range(len(padded) - 2))


def tfidf_vectors(documents):
    documents = {key: terms for key, terms in documents.items() if terms}
    frequencies = Counter(term for terms in documents.values() for term in terms)
    vectors = {}
    for key, terms in documents.items():
        weights = {
            term: count * (1 + math.log((1 + len(documents)) / (1 + frequencies[term])))
            for term, count in terms.items()
        }
        norm = math.sqrt(math.fsum(value * value for value in weights.values()))
        vectors[key] = {term: weight / norm for term, weight in weights.items()}
    return vectors


def cosine(left, right):
    return round(min(1.0, math.fsum(v * right.get(t, 0) for t, v in left.items())), 6)
