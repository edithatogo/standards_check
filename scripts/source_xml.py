"""Shared bounded UTF-8 XML trust boundary for article and OAI sources."""
from xml.etree import ElementTree as ET


def parse_xml(raw: bytes, max_bytes: int) -> ET.Element:
    if not raw or len(raw) > max_bytes or b"\x00" in raw:
        raise ValueError("empty, oversized or unsupported XML encoding")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("unsupported source XML encoding") from exc
    # Check decoded text, not just an ASCII pattern in untrusted encoded bytes.
    # ElementTree does not load external DTDs; JATS documents may declare one.
    if "<!ENTITY" in text.upper():
        raise ValueError("entity-bearing source XML")
    try:
        return ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError("invalid source XML") from exc
