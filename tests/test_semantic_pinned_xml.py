import hashlib

import pytest

from scripts.blind_adjudication import read_pinned_article_xml


def test_pinned_xml_uses_shared_utf8_entity_boundary(tmp_path):
    path = tmp_path / "article.xml"
    good = b"<article><body/></article>"
    path.write_bytes(good)
    pin = hashlib.sha256(good).hexdigest()
    root, raw = read_pinned_article_xml(path, pin)
    assert root.tag == "article" and raw == good
    with pytest.raises(ValueError, match="not pinned"):
        read_pinned_article_xml(path, "0" * 64)
    for bad in (b'<!DOCTYPE article [<!ENTITY x "expansion">]><article>&x;</article>',
                "<article/>".encode("utf-16"), b"<article>", b"x" * 8_000_001):
        path.write_bytes(bad)
        with pytest.raises(ValueError):
            read_pinned_article_xml(path, hashlib.sha256(bad).hexdigest())
