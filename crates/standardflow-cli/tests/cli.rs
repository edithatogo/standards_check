//! CLI integration tests for the `StandardFlow` pack commands.

use std::path::PathBuf;
use std::process::Command;

use serde_json::Value;

fn repository_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn cli() -> Command {
    Command::new(env!("CARGO_BIN_EXE_standardflow"))
}

#[test]
fn validate_returns_machine_readable_summary() -> Result<(), Box<dyn std::error::Error>> {
    let pack = repository_root().join("packs/org.prisma/prisma/2020/pack.json");
    let output = cli()
        .args(["--json", "pack", "validate"])
        .arg(pack)
        .output()?;
    assert!(output.status.success());
    let response: Value = serde_json::from_slice(&output.stdout)?;
    assert_eq!(response.pointer("/ok"), Some(&Value::Bool(true)));
    assert_eq!(
        response.pointer("/result/requirements"),
        Some(&Value::from(27))
    );
    assert_eq!(response.pointer("/result/warnings"), Some(&Value::from(1)));
    Ok(())
}

#[test]
fn committed_prisma_lock_verifies() -> Result<(), Box<dyn std::error::Error>> {
    let root = repository_root().join("packs/org.prisma/prisma/2020");
    let output = cli()
        .args(["--json", "pack", "lock"])
        .arg(root)
        .arg("--check")
        .output()?;
    assert!(output.status.success());
    let response: Value = serde_json::from_slice(&output.stdout)?;
    assert_eq!(
        response.pointer("/result/mode"),
        Some(&Value::String(String::from("verified")))
    );
    Ok(())
}

#[test]
fn unknown_commands_return_usage_status() -> Result<(), Box<dyn std::error::Error>> {
    let output = cli().arg("unknown").output()?;
    assert_eq!(output.status.code(), Some(2));
    assert!(!output.stderr.is_empty());
    Ok(())
}
