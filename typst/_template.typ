# Title of Checklist

#let heading(level: int, text) = {
  if level == 1 { set text(size: 20pt, weight: "bold") };
  if level == 2 { set text(size: 14pt, weight: "bold") };
  text(text)
}

// Scope and Reference
heading(1, "Title of Checklist")
heading(2, "Instructions")
"Use checkboxes and free-text fields; keep numbering consistent."

heading(2, "Items")
- [ ] First requirement clearly stated.
- [ ] Second requirement with some detail.

heading(3, "Notes")
// Free-text area placeholder
"Notes: _______________________________"

heading(2, "Provenance")
"Source: <URL>; Version: <year>; License: <terms>"

