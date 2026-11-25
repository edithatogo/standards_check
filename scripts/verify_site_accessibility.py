"""Check minimal keyboard-navigation and heading contracts in generated HTML."""

import sys
from html.parser import HTMLParser
from pathlib import Path


class _Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.headings = 0
        self.skip_links = 0
        self.main_targets = 0
        self.unlabelled_progress = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "h1":
            self.headings += 1
        if tag == "a" and attributes.get("href") == "#main-content":
            self.skip_links += 1
        if tag == "main" and attributes.get("id") == "main-content":
            self.main_targets += 1
        if attributes.get("role") == "progressbar" and not (
            attributes.get("aria-label") or attributes.get("aria-labelledby")
        ):
            self.unlabelled_progress += 1


def problems(html: str) -> list[str]:
    """Return concrete contract failures without claiming WCAG certification."""
    page = _Page()
    page.feed(html)
    errors = []
    if page.headings != 1:
        errors.append(f"expected exactly one h1, found {page.headings}")
    if page.skip_links != 1:
        errors.append("expected one skip-to-main link")
    if page.main_targets != 1:
        errors.append("expected one main-content landmark")
    if page.unlabelled_progress:
        errors.append("progress bars must have accessible names")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_site_accessibility.py <site-directory>", file=sys.stderr)
        return 2
    pages = sorted(Path(sys.argv[1]).rglob("*.html"))
    if not pages:
        print("no generated HTML pages to validate", file=sys.stderr)
        return 1
    failed = 0
    for path in pages:
        for error in problems(path.read_text(encoding="utf-8")):
            print(f"{path}: {error}", file=sys.stderr)
            failed += 1
    if not failed:
        print(
            f"Checked {len(pages)} generated HTML pages (heading, skip-link, landmark, progress-name)"
        )
    return int(bool(failed))


if __name__ == "__main__":
    raise SystemExit(main())
