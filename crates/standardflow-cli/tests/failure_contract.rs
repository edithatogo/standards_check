//! CLI contracts exercise failure status, output isolation and file preservation.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::{Value, json};

static NEXT_DIRECTORY: AtomicU64 = AtomicU64::new(0);
const PACK: &str = include_str!("../../../contracts/examples/minimal-standard-pack.v1.json");

struct Directory(PathBuf);

impl Directory {
    fn new() -> io::Result<Self> {
        let counter = NEXT_DIRECTORY.fetch_add(1, Ordering::Relaxed);
        let path = std::env::temp_dir().join(format!(
            "standardflow-cli-contract-{}-{counter}",
            std::process::id()
        ));
        fs::create_dir(&path)?;
        fs::write(path.join("pack.json"), PACK)?;
        Ok(Self(path))
    }

    fn path(&self) -> &Path {
        &self.0
    }
}

impl Drop for Directory {
    fn drop(&mut self) {
        let _ignored = fs::remove_dir_all(self.path());
    }
}

fn cli() -> Command {
    Command::new(env!("CARGO_BIN_EXE_standardflow"))
}

fn json_error(output: &Output, status: i32, kind: &str) -> Result<(), Box<dyn std::error::Error>> {
    assert_eq!(output.status.code(), Some(status));
    assert!(
        output.stdout.is_empty(),
        "failures must not produce success output"
    );
    let value: Value = serde_json::from_slice(&output.stderr)?;
    assert_eq!(value.get("ok"), Some(&json!(false)));
    assert_eq!(value.pointer("/error/kind"), Some(&json!(kind)));
    Ok(())
}

#[test]
fn incomplete_or_ambiguous_commands_return_usage_errors() -> Result<(), Box<dyn std::error::Error>>
{
    for arguments in [
        vec![],
        vec!["pack"],
        vec!["pack", "unknown"],
        vec!["pack", "validate"],
        vec!["pack", "digest"],
        vec!["pack", "canonicalize"],
        vec!["pack", "lock", ".", "--erase"],
        vec!["diagram"],
        vec!["diagram", "wrong", "x", "--format", "svg", "--output", "x"],
        vec!["diagram", "prisma", "x", "--format", "png", "--output", "x"],
        vec!["diagram", "prisma", "x", "--format", "svg", "--output", "-"],
    ] {
        json_error(&cli().arg("--json").args(arguments).output()?, 2, "usage")?;
    }
    Ok(())
}

#[test]
fn invalid_pack_has_no_canonical_output_and_preserves_existing_destination()
-> Result<(), Box<dyn std::error::Error>> {
    let directory = Directory::new()?;
    let input = directory.path().join("pack.json");
    let destination = directory.path().join("canonical.json");
    fs::write(&destination, b"existing approved output")?;
    let mut value: Value = serde_json::from_str(PACK)?;
    *value
        .get_mut("title")
        .ok_or_else(|| io::Error::other("no title"))? = json!(" ");
    fs::write(&input, serde_json::to_vec(&value)?)?;
    let output = cli()
        .args(["--json", "pack", "canonicalize"])
        .arg(&input)
        .arg(&destination)
        .output()?;
    json_error(&output, 1, "validation")?;
    let response: Value = serde_json::from_slice(&output.stderr)?;
    assert!(response.pointer("/error/diagnostics/diagnostics").is_some());
    assert_eq!(fs::read(&destination)?, b"existing approved output");
    let text = cli().args(["pack", "validate"]).arg(&input).output()?;
    assert_eq!(text.status.code(), Some(1));
    assert!(String::from_utf8(text.stderr)?.contains("SF-PACK-002 /title"));
    Ok(())
}

#[test]
fn unreadable_and_malformed_inputs_are_operation_failures() -> Result<(), Box<dyn std::error::Error>>
{
    let directory = Directory::new()?;
    for bytes in [b"{".as_slice(), b"null".as_slice()] {
        let input = directory.path().join("bad.json");
        fs::write(&input, bytes)?;
        json_error(
            &cli()
                .args(["--json", "pack", "validate"])
                .arg(input)
                .output()?,
            1,
            "pack",
        )?;
    }
    json_error(
        &cli()
            .args(["--json", "pack", "digest"])
            .arg(directory.path().join("absent.json"))
            .output()?,
        1,
        "pack",
    )?;
    json_error(
        &cli()
            .args(["--json", "diagram", "prisma"])
            .arg(directory.path().join("absent.json"))
            .args(["--format", "text", "--output", "output.txt"])
            .output()?,
        1,
        "io",
    )?;
    Ok(())
}

#[test]
fn canonical_bytes_and_digest_agree_across_file_and_stdout_modes()
-> Result<(), Box<dyn std::error::Error>> {
    let directory = Directory::new()?;
    let input = directory.path().join("pack.json");
    let destination = directory.path().join("canonical.json");
    let file = cli()
        .args(["--json", "pack", "canonicalize"])
        .arg(&input)
        .arg(&destination)
        .output()?;
    assert!(file.status.success());
    let written: Value = serde_json::from_slice(&file.stdout)?;
    let digest = cli()
        .args(["--json", "pack", "digest"])
        .arg(&input)
        .output()?;
    assert!(digest.status.success());
    let summary: Value = serde_json::from_slice(&digest.stdout)?;
    assert_eq!(written.get("result"), summary.get("result"));
    let stdout = cli()
        .args(["pack", "canonicalize"])
        .arg(&input)
        .arg("-")
        .output()?;
    assert!(stdout.status.success());
    assert_eq!(stdout.stdout, fs::read(&destination)?);
    let text = cli()
        .args(["pack", "validate"])
        .arg(&destination)
        .output()?;
    assert!(text.status.success());
    assert!(String::from_utf8(text.stdout)?.contains("requirements: 1"));
    json_error(
        &cli()
            .args(["--json", "pack", "canonicalize"])
            .arg(&input)
            .arg("-")
            .output()?,
        2,
        "usage",
    )?;
    Ok(())
}

#[test]
fn lock_write_check_and_tamper_are_distinct_observable_results()
-> Result<(), Box<dyn std::error::Error>> {
    let directory = Directory::new()?;
    for (flag, expected) in [("--write", "written"), ("--check", "verified")] {
        let result = cli()
            .args(["--json", "pack", "lock"])
            .arg(directory.path())
            .arg(flag)
            .output()?;
        assert!(result.status.success());
        let value: Value = serde_json::from_slice(&result.stdout)?;
        assert_eq!(value.pointer("/result/mode"), Some(&json!(expected)));
    }
    fs::write(
        directory.path().join("new-evidence.txt"),
        b"unreviewed addition",
    )?;
    json_error(
        &cli()
            .args(["--json", "pack", "lock"])
            .arg(directory.path())
            .arg("--check")
            .output()?,
        1,
        "lock",
    )?;
    Ok(())
}

#[test]
fn failed_output_rename_cleans_up_only_its_temporary_file() -> Result<(), Box<dyn std::error::Error>>
{
    let directory = Directory::new()?;
    let destination = directory.path().join("output");
    fs::create_dir(&destination)?;
    fs::write(destination.join("preserved.txt"), b"preserve")?;
    json_error(
        &cli()
            .args(["--json", "pack", "canonicalize"])
            .arg(directory.path().join("pack.json"))
            .arg(&destination)
            .output()?,
        1,
        "io",
    )?;
    assert_eq!(fs::read(destination.join("preserved.txt"))?, b"preserve");
    let names = fs::read_dir(directory.path())?
        .map(|entry| entry.map(|value| value.file_name()))
        .collect::<Result<Vec<_>, _>>()?;
    assert!(
        !names
            .iter()
            .any(|name| name.to_string_lossy().ends_with(".tmp"))
    );
    Ok(())
}
