#!/usr/bin/env python3
"""Apply reviewed strict-Clippy corrections from GitHub compiler receipts."""
from pathlib import Path

root = Path('crates/standardflow-artifacts/src')

def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly one match, found {count}: {old!r}')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')

prisma = root / 'prisma.rs'
replace_once(prisma, "    fn recipe_json(self) -> &'static str {", "    const fn recipe_json(self) -> &'static str {")
replace_once(
    prisma,
    "    fn bindings(&self) -> Result<BTreeMap<String, String>, PrismaError> {",
    "    #[allow(\n        clippy::too_many_lines,\n        reason = \"bindings intentionally enumerate the complete versioned PRISMA contract in one auditable mapping\"\n    )]\n    fn bindings(&self) -> Result<BTreeMap<String, String>, PrismaError> {",
)
replace_once(
    prisma,
    '''    if let Some(identified) = identified {
        if stream.reports_sought != identified {
            report.push(Diagnostic::error(
                "SF-PRISMA-020",
                "/other_methods/reports_sought",
                format!(
                    "reports sought must equal reports identified by other methods ({identified}) in the official reference recipe"
                ),
            ));
        }
    }
''',
    '''    if let Some(identified) = identified
        && stream.reports_sought != identified
    {
        report.push(Diagnostic::error(
            "SF-PRISMA-020",
            "/other_methods/reports_sought",
            format!(
                "reports sought must equal reports identified by other methods ({identified}) in the official reference recipe"
            ),
        ));
    }
''',
)

recipe = root / 'recipe.rs'
replace_once(recipe, 'use std::collections::{BTreeMap, BTreeSet};\n', 'use std::collections::{BTreeMap, BTreeSet};\nuse std::fmt::Write as _;\n')
replace_once(
    recipe,
    "    #[must_use]\n    pub fn validate(&self) -> ValidationReport {",
    "    #[must_use]\n    #[allow(\n        clippy::too_many_lines,\n        reason = \"validation is a linear catalogue of stable recipe diagnostics kept together for auditability\"\n    )]\n    pub fn validate(&self) -> ValidationReport {",
)
replace_once(
    recipe,
    '''    pub fn build_scene(
        &self,
        bindings: &BTreeMap<String, String>,
    ) -> Result<Scene, RecipeError> {''',
    '''    #[allow(
        clippy::too_many_lines,
        reason = "scene construction keeps the deterministic prepare-layout-materialise pipeline visible in one auditable function"
    )]
    pub fn build_scene(
        &self,
        bindings: &BTreeMap<String, String>,
    ) -> Result<Scene, RecipeError> {''',
)
replace_once(
    recipe,
    '''    /// Template delimiters are malformed.
    #[error("template contains malformed binding delimiters")]
    MalformedTemplate,
''',
    '''    /// Template delimiters are malformed.
    #[error("template contains malformed binding delimiters")]
    MalformedTemplate,
    /// Formatting into an in-memory text equivalent failed.
    #[error("formatting generated text equivalent failed")]
    Formatting,
''',
)
replace_once(recipe, "fn nodes_overlap(left: &RecipeNode, right: &RecipeNode) -> bool {", "const fn nodes_overlap(left: &RecipeNode, right: &RecipeNode) -> bool {")
replace_once(
    recipe,
    '        text.push_str(&format!("\\n{}. {}", index + 1, node.label));',
    r'''        write!(&mut text, "\n{}. {}", index + 1, node.label)
            .map_err(|_| RecipeError::Formatting)?;''',
)

render = root / 'render.rs'
replace_once(
    render,
    "pub fn render_svg(scene: &Scene) -> Result<String, RenderError> {",
    "#[allow(\n    clippy::too_many_lines,\n    reason = \"the standalone SVG writer is a linear, deterministic serialization pass with no hidden renderer state\"\n)]\npub fn render_svg(scene: &Scene) -> Result<String, RenderError> {",
)
replace_once(
    render,
    '''fn midpoint(left: u32, right: u32) -> u32 {
    u32::try_from((u64::from(left) + u64::from(right)) / 2).unwrap_or(u32::MAX)
}''',
    '''fn midpoint(left: u32, right: u32) -> u32 {
    left.midpoint(right)
}''',
)

scene = root / 'scene.rs'
replace_once(scene, "    fn right(self) -> Option<u32> {", "    const fn right(self) -> Option<u32> {")
replace_once(scene, "    fn bottom(self) -> Option<u32> {", "    const fn bottom(self) -> Option<u32> {")
replace_once(
    scene,
    "    #[must_use]\n    pub fn validate(&self) -> ValidationReport {",
    "    #[must_use]\n    #[allow(\n        clippy::too_many_lines,\n        reason = \"scene validation keeps the complete stable diagnostic catalogue together for auditability\"\n    )]\n    pub fn validate(&self) -> ValidationReport {",
)

replace_once(
    render,
    "fn midpoint(left: u32, right: u32) -> u32 {",
    "const fn midpoint(left: u32, right: u32) -> u32 {",
)
replace_once(
    scene,
    "fn rectangles_overlap(left: Rect, right: Rect) -> bool {",
    "const fn rectangles_overlap(left: Rect, right: Rect) -> bool {",
)

cli_test = Path('crates/standardflow-cli/tests/diagram.rs')
replace_once(
    cli_test,
    'use std::fs;\n',
    '//! End-to-end CLI tests for deterministic PRISMA diagram generation.\n\nuse std::fs;\n',
)

print("Applied reviewed strict-Clippy corrections to Track 02 source")
