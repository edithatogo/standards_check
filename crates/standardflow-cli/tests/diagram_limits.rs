//! End-to-end bounded-input regression tests for the diagram CLI.

use std::fs;
use std::path::PathBuf;
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::Value;

static COUNTER: AtomicU64 = AtomicU64::new(0);

fn temporary_path(name: &str) -> PathBuf {
    let counter = COUNTER.fetch_add(1, Ordering::Relaxed);
    std::env::temp_dir().join(format!(
        "standardflow-diagram-limit-{}-{counter}-{name}",
        std::process::id()
    ))
}

#[test]
fn cli_rejects_oversized_diagram_input_before_json_parsing()
-> Result<(), Box<dyn std::error::Error>> {
    let input = temporary_path("oversized.json");
    let output = temporary_path("output.svg");
    fs::write(&input, vec![b' '; 1_048_577])?;
    let response = Command::new(env!("CARGO_BIN_EXE_standardflow"))
        .args(["--json", "diagram", "prisma"])
        .arg(&input)
        .args(["--format", "svg", "--output"])
        .arg(&output)
        .output()?;
    let _ignored = fs::remove_file(&input);
    let _ignored = fs::remove_file(&output);
    assert_eq!(response.status.code(), Some(1));
    let error: Value = serde_json::from_slice(&response.stderr)?;
    assert_eq!(
        error.pointer("/error/kind"),
        Some(&Value::String(String::from("io")))
    );
    assert!(
        error
            .pointer("/error/message")
            .and_then(Value::as_str)
            .is_some_and(|message| message.contains("1048576-byte input limit"))
    );
    Ok(())
}
