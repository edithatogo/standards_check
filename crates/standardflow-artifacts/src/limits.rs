//! Shared resource and text-safety limits for untrusted artefact inputs.

/// Maximum bytes accepted for one recipe or PRISMA flow JSON document.
pub const MAX_INPUT_BYTES: usize = 1_048_576;
/// Maximum nodes in one recipe or generated scene.
pub const MAX_NODES: usize = 512;
/// Maximum edges in one recipe or generated scene.
pub const MAX_EDGES: usize = 2_048;
/// Maximum zero-based row index in the deterministic grid.
pub const MAX_ROW_INDEX: u32 = 1_000;
/// Maximum columns in a recipe grid.
pub const MAX_COLUMNS: u32 = 12;
/// Maximum bytes in an identifier used by a node, edge or binding.
pub const MAX_IDENTIFIER_BYTES: usize = 256;
/// Maximum bytes in a recipe identifier or source-standard path.
pub const MAX_PATH_IDENTIFIER_BYTES: usize = 512;
/// Maximum bytes in one template, label, reason or accessible text component.
pub const MAX_TEMPLATE_BYTES: usize = 16_384;
/// Maximum bindings supplied to a recipe.
pub const MAX_BINDINGS: usize = 256;
/// Maximum bytes in one resolved binding value.
pub const MAX_BINDING_BYTES: usize = 16_384;
/// Maximum bytes in a rendered title, description, node label or edge label.
pub const MAX_RENDERED_COMPONENT_BYTES: usize = 65_536;
/// Maximum bytes in the complete non-visual equivalent.
pub const MAX_TEXT_EQUIVALENT_BYTES: usize = 262_144;
/// Maximum wrapped lines in one scene node.
pub const MAX_WRAPPED_LINES: usize = 4_096;
/// Maximum canvas width or height in CSS pixels.
pub const MAX_CANVAS_DIMENSION: u32 = 100_000;
/// Maximum count that round-trips exactly through common JSON number implementations.
pub const MAX_SAFE_JSON_INTEGER: u64 = 9_007_199_254_740_991;
/// Maximum structured report-exclusion reasons in one PRISMA stream.
pub const MAX_EXCLUSION_REASONS: usize = 20;
/// Maximum Unicode scalar values in one exclusion reason.
pub const MAX_EXCLUSION_REASON_CHARS: usize = 240;

/// Returns whether every scalar value is legal in XML 1.0 text.
pub fn is_xml_10_text(value: &str) -> bool {
    value.chars().all(is_xml_10_char)
}

#[allow(
    clippy::manual_range_contains,
    reason = "explicit scalar boundaries remain const and mirror the XML 1.0 production"
)]
const fn is_xml_10_char(value: char) -> bool {
    matches!(value, '\u{9}' | '\u{A}' | '\u{D}')
        || (value >= '\u{20}' && value <= '\u{D7FF}')
        || (value >= '\u{E000}' && value <= '\u{FFFD}')
        || (value >= '\u{10000}' && value <= '\u{10FFFF}')
}
