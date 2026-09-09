#!/usr/bin/env python3
"""Refine the staged hardening patch before compiler verification."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {old[:100]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


recipe = "crates/standardflow-artifacts/src/recipe.rs"
replace_once(
    recipe,
    "use std::fmt::Write as _;\n",
    "",
)
replace_once(
    recipe,
    "            let lines = wrap_label(&label, self.layout, width);",
    "            let lines = wrap_label(&label, self.layout, width)?;",
)
replace_once(
    recipe,
    "fn wrap_label(label: &str, layout: GridLayout, width: u32) -> Vec<String> {",
    "fn wrap_label(\n    label: &str,\n    layout: GridLayout,\n    width: u32,\n) -> Result<Vec<String>, RecipeError> {",
)
replace_once(
    recipe,
    '''    if lines.is_empty() {
        lines.push(String::from(" "));
    }
    if lines.len() > MAX_WRAPPED_LINES {
        lines.truncate(MAX_WRAPPED_LINES);
    }
    lines
}
''',
    '''    if lines.is_empty() {
        lines.push(String::from(" "));
    }
    if lines.len() > MAX_WRAPPED_LINES {
        return Err(RecipeError::ResourceLimit {
            resource: "wrapped label lines",
            limit: MAX_WRAPPED_LINES,
        });
    }
    Ok(lines)
}
''',
)
replace_once(
    recipe,
    '''        let label = edge
            .label
            .as_deref()
            .map_or(String::new(), |value| format!("; label: {value}"));
''',
    '''        let label = edge
            .label
            .as_deref()
            .map_or_else(String::new, |value| format!("; label: {value}"));
''',
)
replace_once(
    recipe,
    "    text.push('\n');",
    "    text.push('\\n');",
)

limits = "crates/standardflow-artifacts/src/limits.rs"
replace_once(
    limits,
    "const fn is_xml_10_char(value: char) -> bool {",
    "#[allow(\n    clippy::manual_range_contains,\n    reason = \"explicit scalar boundaries remain const and mirror the XML 1.0 production\"\n)]\nconst fn is_xml_10_char(value: char) -> bool {",
)

# Resource budgets are part of the caller-facing contract: clients should be able to
# reject oversized work before serialising or submitting it. Expose the documented
# catalogue deliberately rather than fighting `unreachable_pub` and
# `redundant_pub_crate` with conflicting restricted visibilities.
replace_once(
    "crates/standardflow-artifacts/src/lib.rs",
    "mod limits;\n",
    "pub mod limits;\n",
)
limits_path = ROOT / limits
limits_text = limits_path.read_text(encoding="utf-8")
visibility_count = limits_text.count("pub(crate) ")
if visibility_count != 18:
    raise SystemExit(
        f"{limits}: expected 18 visibility markers, found {visibility_count}"
    )
limits_path.write_text(
    limits_text.replace("pub(crate) ", "pub "),
    encoding="utf-8",
)

cli = "crates/standardflow-cli/src/main.rs"
replace_once(
    cli,
    '''    let observed = match u64::try_from(bytes.len()) {
        Ok(value) => value,
        Err(_) => u64::MAX,
    };
''',
    '''    let observed = u64::try_from(bytes.len()).unwrap_or(u64::MAX);
''',
)

print("Refined hardening patch: bounded labels remain complete, resource budgets are public and bounded reads satisfy strict Clippy")
