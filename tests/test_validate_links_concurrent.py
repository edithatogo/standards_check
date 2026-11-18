"""Exercise the real executor without network access."""

from threading import Barrier
from types import SimpleNamespace

import pytest

from scripts import validate_links


def test_requests_overlap_and_summary_preserves_input_order(tmp_path, monkeypatch, capsys):
    paths = []
    for name in ("first", "second"):
        path = tmp_path / f"{name}.yml"
        path.write_text(f"source_url: https://example.com/{name}\n", encoding="utf-8")
        paths.append(str(path))
    monkeypatch.setattr(validate_links, "glob", lambda *args, **kwargs: paths)
    barrier = Barrier(2)
    requested = []

    def head(url, **kwargs):
        requested.append(url)
        barrier.wait(timeout=5)
        return SimpleNamespace(status_code=403)

    def forbid_network(*args, **kwargs):
        pytest.fail("Validation bypassed the isolated request boundary")

    monkeypatch.setattr(validate_links.requests.sessions.Session, "request", forbid_network)
    monkeypatch.setattr(validate_links.requests, "head", head)
    with pytest.raises(SystemExit) as exit_info:
        validate_links.main()

    assert exit_info.value.code == 0
    assert set(requested) == {
        "https://example.com/first", "https://example.com/second"
    }
    summary = capsys.readouterr().out.split("--- Validation Summary ---")[1]
    assert summary.index("https://example.com/first") < summary.index("https://example.com/second")
