//! Candidate parser/weighted-transducer qualification only; not a maintained dependency.

use std::ops::Range;
use typst_syntax::{LinkedNode, SyntaxKind};

fn checked_replace(input: &str, range: Range<usize>, old: &str, new: &str) -> Option<String> {
    if input.get(range.clone())? != old {
        return None;
    }
    let mut output = input.to_owned();
    output.replace_range(range, new);
    Some(output)
}

/// Normalize one uniquely identified Typst label; conserve all other bytes.
pub fn typst_label(input: &str, old: &str, new: &str) -> Option<String> {
    if input.len() > 100_000 || !old.starts_with('<') || !new.starts_with('<') {
        return None;
    }
    let root = typst_syntax::parse(input);
    if root.diagnosis().either() || root.full_text().as_str() != input {
        return None;
    }
    let mut stack = vec![LinkedNode::new(&root)];
    let mut spans = Vec::new();
    while let Some(node) = stack.pop() {
        if node.get().kind() == SyntaxKind::Label && input.get(node.range()) == Some(old) {
            spans.push(node.range());
        }
        stack.extend(node.children());
    }
    let [range] = spans.as_slice() else { return None; };
    let replacement = typst_syntax::parse(new);
    if replacement.diagnosis().either()
        || replacement.children().count() != 1
        || replacement.children().next()?.kind() != SyntaxKind::Label
    {
        return None;
    }
    let output = checked_replace(input, range.clone(), old, new)?;
    let parsed = typst_syntax::parse(&output);
    (!parsed.diagnosis().either() && parsed.full_text().as_str() == output).then_some(output)
}

/// Normalize one exact parsed LaTeX label-definition node. Never expand macros.
pub fn latex_label(input: &str, old: &str, new: &str) -> Option<String> {
    if input.len() > 100_000 || !old.starts_with("\\label{") || !new.starts_with("\\label{") {
        return None;
    }
    let mut parser = tree_sitter::Parser::new();
    parser.set_language(&codebook_tree_sitter_latex::LANGUAGE.into()).ok()?;
    let replacement = parser.parse(new, None)?;
    if replacement.root_node().has_error() || replacement.root_node().named_child_count() != 1 {
        return None;
    }
    let child = replacement.root_node().named_child(0)?;
    if child.kind() != "label_definition" || child.byte_range() != (0..new.len()) {
        return None;
    }
    let tree = parser.parse(input, None)?;
    if tree.root_node().has_error() {
        return None;
    }
    let mut stack = vec![tree.root_node()];
    let mut spans = Vec::new();
    while let Some(node) = stack.pop() {
        if node.kind() == "label_definition" && input.get(node.byte_range()) == Some(old) {
            spans.push(node.byte_range());
        }
        let mut cursor = node.walk();
        stack.extend(node.children(&mut cursor));
    }
    let [range] = spans.as_slice() else { return None; };
    let output = checked_replace(input, range.clone(), old, new)?;
    let parsed = parser.parse(&output, None)?;
    (!parsed.root_node().has_error()).then_some(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rustfst::algorithms::{compose, shortest_path};
    use rustfst::fst;
    use rustfst::prelude::*;

    #[test]
    fn native_cst_exact_span_edits_and_ambiguity() {
        assert_eq!(
            typst_label("= Heading <old>\n// keep\n", "<old>", "<new>"),
            Some("= Heading <new>\n// keep\n".into())
        );
        assert!(typst_label("<old> <old>", "<old>", "<new>").is_none());
        assert_eq!(
            latex_label("\\section{A}\\label{old}\n% keep\n", "\\label{old}", "\\label{new}"),
            Some("\\section{A}\\label{new}\n% keep\n".into())
        );
        assert!(latex_label("\\label{old}\\label{old}", "\\label{old}", "\\label{new}").is_none());
    }

    #[test]
    fn weighted_competing_paths_and_epsilon() -> Result<(), Box<dyn std::error::Error>> {
        let mut transducer = VectorFst::<TropicalWeight>::new();
        let start = transducer.add_state();
        let via = transducer.add_state();
        let end = transducer.add_state();
        transducer.set_start(start)?;
        transducer.set_final(end, TropicalWeight::new(0.0))?;
        transducer.add_tr(start, Tr::new(1, 2, TropicalWeight::new(5.0), end))?;
        transducer.add_tr(start, Tr::new(1, 3, TropicalWeight::new(1.0), via))?;
        transducer.add_tr(via, Tr::new(0, 4, TropicalWeight::new(1.0), end))?;
        let accepted: VectorFst<TropicalWeight> = fst![1];
        let composed: VectorFst<TropicalWeight> = compose(accepted, transducer.clone())?;
        let best: VectorFst<TropicalWeight> = shortest_path(&composed)?;
        let paths: Vec<_> = best.paths_iter().collect();
        assert_eq!(paths.len(), 1);
        assert_eq!(paths[0].olabels, vec![3, 4]);
        assert_eq!(paths[0].weight, TropicalWeight::new(2.0));
        let rejected: VectorFst<TropicalWeight> = fst![9];
        let no_match: VectorFst<TropicalWeight> = compose(rejected, transducer)?;
        assert_eq!(no_match.paths_iter().count(), 0);
        Ok(())
    }
}
