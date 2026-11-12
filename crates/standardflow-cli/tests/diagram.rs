//! End-to-end CLI tests for deterministic PRISMA diagram generation.

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::Value;

static COUNTER: AtomicU64 = AtomicU64::new(0);

struct TestDirectory(PathBuf);

impl TestDirectory {
    fn create() -> Result<Self, std::io::Error> {
        let counter = COUNTER.fetch_add(1, Ordering::Relaxed);
        let path = std::env::temp_dir().join(format!(
            "standardflow-diagram-cli-{}-{counter}",
            std::process::id()
        ));
        if path.exists() {
            fs::remove_dir_all(&path)?;
        }
        fs::create_dir_all(&path)?;
        Ok(Self(path))
    }

    fn path(&self) -> &Path {
        &self.0
    }
}

impl Drop for TestDirectory {
    fn drop(&mut self) {
        let _ignored = fs::remove_dir_all(&self.0);
    }
}

fn repository_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn cli() -> Command {
    Command::new(env!("CARGO_BIN_EXE_standardflow"))
}

#[test]
fn cli_renders_accessible_svg_and_reports_its_digest() -> Result<(), Box<dyn std::error::Error>> {
    let directory = TestDirectory::create()?;
    let input = repository_root()
        .join("contracts/examples/prisma-flow/new-databases-registers-other-sources.json");
    let output_path = directory.path().join("diagram.svg");
    let output = cli()
        .args(["--json", "diagram", "prisma"])
        .arg(input)
        .args(["--format", "svg", "--output"])
        .arg(&output_path)
        .output()?;
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    let summary: Value = serde_json::from_slice(&output.stdout)?;
    assert_eq!(summary.pointer("/ok"), Some(&Value::Bool(true)));
    assert_eq!(
        summary.pointer("/result/format"),
        Some(&Value::String(String::from("svg")))
    );
    let svg = fs::read_to_string(output_path)?;
    assert!(svg.contains("role=\"img\""));
    assert!(svg.contains("standardflow-text-equivalent"));
    Ok(())
}

#[test]
fn cli_rejects_invalid_prisma_arithmetic() -> Result<(), Box<dyn std::error::Error>> {
    let directory = TestDirectory::create()?;
    let source =
        repository_root().join("contracts/examples/prisma-flow/new-databases-registers.json");
    let mut value: Value = serde_json::from_slice(&fs::read(source)?)?;
    let screened = value
        .pointer_mut("/databases_registers/records_screened")
        .ok_or_else(|| std::io::Error::other("fixture field is missing"))?;
    *screened = Value::from(1_u64);
    let invalid = directory.path().join("invalid.json");
    fs::write(&invalid, serde_json::to_vec_pretty(&value)?)?;
    let output_path = directory.path().join("diagram.svg");
    let output = cli()
        .args(["--json", "diagram", "prisma"])
        .arg(invalid)
        .args(["--format", "svg", "--output"])
        .arg(output_path)
        .output()?;
    assert_eq!(output.status.code(), Some(1));
    let response: Value = serde_json::from_slice(&output.stderr)?;
    assert_eq!(
        response.pointer("/error/kind"),
        Some(&Value::String(String::from("validation")))
    );
    assert!(response.pointer("/error/diagnostics/diagnostics").is_some());
    Ok(())
}

#[test]
fn scene_json_can_be_streamed_to_stdout() -> Result<(), Box<dyn std::error::Error>> {
    let input =
        repository_root().join("contracts/examples/prisma-flow/updated-databases-registers.json");
    let output = cli()
        .args(["diagram", "prisma"])
        .arg(input)
        .args(["--format", "scene-json", "--output", "-"])
        .output()?;
    assert!(output.status.success());
    let scene: Value = serde_json::from_slice(&output.stdout)?;
    assert_eq!(
        scene.pointer("/schema_version"),
        Some(&Value::String(String::from(
            "dev.standardflow.scene-graph.v1"
        )))
    );
    Ok(())
}
