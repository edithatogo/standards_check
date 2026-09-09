//! Command-line access to Canonical Standard Pack and artefact operations.
#![forbid(unsafe_code)]

use std::env;
use std::ffi::{OsStr, OsString};
use std::fs;
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use serde::Serialize;
use standardflow_artifacts::{PrismaError, RenderFormat, parse_prisma_flow, render};
use standardflow_core::{
    LockLimits, PackError, ValidationReport, load_pack, sha256_hex, verify_pack_lock,
    write_pack_lock,
};

const USAGE: &str = "Usage:\n  standardflow [--json] pack validate <pack.json>\n  standardflow [--json] pack canonicalize <pack.json> <output.json|->\n  standardflow [--json] pack digest <pack.json>\n  standardflow [--json] pack lock <pack-directory> --write\n  standardflow [--json] pack lock <pack-directory> --check\n  standardflow [--json] diagram prisma <input.json> --format <svg|text|scene-json> --output <path|->\n";

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum OutputMode {
    Text,
    Json,
}

#[derive(Debug)]
struct CliError {
    exit_code: u8,
    kind: &'static str,
    message: String,
    validation: Option<ValidationReport>,
}

impl CliError {
    fn usage(message: impl Into<String>) -> Self {
        Self {
            exit_code: 2,
            kind: "usage",
            message: message.into(),
            validation: None,
        }
    }

    fn operation(kind: &'static str, message: impl Into<String>) -> Self {
        Self {
            exit_code: 1,
            kind,
            message: message.into(),
            validation: None,
        }
    }

    fn from_pack(error: PackError) -> Self {
        match error {
            PackError::Validation(report) => Self::validation("pack validation", report),
            other => Self::operation("pack", other.to_string()),
        }
    }

    fn from_prisma(error: PrismaError) -> Self {
        match error {
            PrismaError::Validation(report) => Self::validation("PRISMA validation", report),
            other => Self::operation("diagram", other.to_string()),
        }
    }

    fn validation(context: &'static str, report: ValidationReport) -> Self {
        Self {
            exit_code: 1,
            kind: "validation",
            message: format!("{context} failed with {} error(s)", report.error_count()),
            validation: Some(report),
        }
    }
}

#[derive(Serialize)]
struct SuccessEnvelope<T> {
    ok: bool,
    operation: &'static str,
    result: T,
}

#[derive(Serialize)]
struct ErrorEnvelope<'a> {
    ok: bool,
    error: ErrorBody<'a>,
}

#[derive(Serialize)]
struct ErrorBody<'a> {
    kind: &'static str,
    message: &'a str,
    diagnostics: Option<&'a ValidationReport>,
}

#[derive(Serialize)]
struct PackSummary<'a> {
    pack_id: &'a str,
    version: &'a str,
    canonical_sha256: String,
    requirements: usize,
    warnings: usize,
}

#[derive(Serialize)]
struct DigestSummary<'a> {
    pack_id: &'a str,
    version: &'a str,
    canonical_sha256: String,
}

#[derive(Serialize)]
struct LockSummary<'a> {
    pack_id: &'a str,
    version: &'a str,
    tree_sha256: &'a str,
    files: usize,
    mode: &'static str,
}

#[derive(Serialize)]
struct DiagramSummary {
    recipe_id: String,
    format: &'static str,
    output: String,
    bytes: usize,
    sha256: String,
}

fn main() -> ExitCode {
    let arguments = env::args_os().skip(1).collect::<Vec<_>>();
    let (mode, arguments) = extract_output_mode(arguments);
    match run(mode, &arguments) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            let _ignored = emit_error(mode, &error);
            ExitCode::from(error.exit_code)
        }
    }
}

fn extract_output_mode(mut arguments: Vec<OsString>) -> (OutputMode, Vec<OsString>) {
    if arguments.first().is_some_and(|value| value == "--json") {
        arguments.remove(0);
        (OutputMode::Json, arguments)
    } else {
        (OutputMode::Text, arguments)
    }
}

fn run(mode: OutputMode, arguments: &[OsString]) -> Result<(), CliError> {
    let Some(command) = arguments.first() else {
        return Err(CliError::usage(USAGE));
    };
    match command.to_str() {
        Some("pack") => pack_command(mode, arguments),
        Some("diagram") => diagram_command(mode, arguments),
        _ => Err(CliError::usage(format!("unknown command\n\n{USAGE}"))),
    }
}

fn pack_command(mode: OutputMode, arguments: &[OsString]) -> Result<(), CliError> {
    let Some(operation) = arguments.get(1) else {
        return Err(CliError::usage(USAGE));
    };
    match operation.to_str() {
        Some("validate") => validate_command(mode, arguments),
        Some("canonicalize") => canonicalize_command(mode, arguments),
        Some("digest") => digest_command(mode, arguments),
        Some("lock") => lock_command(mode, arguments),
        _ => Err(CliError::usage(format!(
            "unknown pack operation\n\n{USAGE}"
        ))),
    }
}

fn diagram_command(mode: OutputMode, arguments: &[OsString]) -> Result<(), CliError> {
    ensure_argument_count(arguments, 7)?;
    if argument(arguments, 1)? != OsStr::new("prisma")
        || argument(arguments, 3)? != OsStr::new("--format")
        || argument(arguments, 5)? != OsStr::new("--output")
    {
        return Err(CliError::usage(USAGE));
    }
    let input_path = PathBuf::from(argument(arguments, 2)?);
    let format_text = argument(arguments, 4)?
        .to_str()
        .ok_or_else(|| CliError::usage("diagram format must be UTF-8"))?;
    let format = RenderFormat::parse(format_text)
        .ok_or_else(|| CliError::usage("diagram format must be svg, text or scene-json"))?;
    let output_argument = argument(arguments, 6)?;
    if output_argument == OsStr::new("-") && mode == OutputMode::Json {
        return Err(CliError::usage(
            "--json cannot be combined with diagram output to stdout",
        ));
    }
    let input = fs::read(&input_path).map_err(|error| {
        CliError::operation(
            "io",
            format!("cannot read {}: {error}", input_path.display()),
        )
    })?;
    let flow = parse_prisma_flow(&input).map_err(CliError::from_prisma)?;
    let scene = flow.build_scene().map_err(CliError::from_prisma)?;
    let bytes =
        render(&scene, format).map_err(|error| CliError::operation("render", error.to_string()))?;
    if output_argument == OsStr::new("-") {
        io::stdout()
            .lock()
            .write_all(&bytes)
            .map_err(|error| CliError::operation("io", error.to_string()))?;
        return Ok(());
    }
    let output_path = PathBuf::from(output_argument);
    write_atomic(&output_path, &bytes)?;
    let result = DiagramSummary {
        recipe_id: scene.recipe_id,
        format: format.as_str(),
        output: output_path.display().to_string(),
        bytes: bytes.len(),
        sha256: sha256_hex(&bytes),
    };
    emit_success(mode, "diagram.prisma", &result)
}

fn validate_command(mode: OutputMode, arguments: &[OsString]) -> Result<(), CliError> {
    ensure_argument_count(arguments, 3)?;
    let path = PathBuf::from(argument(arguments, 2)?);
    let validated = load_pack(&path).map_err(CliError::from_pack)?;
    let digest = validated
        .pack()
        .canonical_sha256()
        .map_err(CliError::from_pack)?;
    let result = PackSummary {
        pack_id: validated.pack().pack_id.as_str(),
        version: &validated.pack().version,
        canonical_sha256: digest,
        requirements: validated.pack().requirements.len(),
        warnings: validated.report().warning_count(),
    };
    emit_success(mode, "pack.validate", &result)
}

fn canonicalize_command(mode: OutputMode, arguments: &[OsString]) -> Result<(), CliError> {
    ensure_argument_count(arguments, 4)?;
    let input = PathBuf::from(argument(arguments, 2)?);
    let output = argument(arguments, 3)?;
    let validated = load_pack(&input).map_err(CliError::from_pack)?;
    let mut bytes = validated
        .pack()
        .canonical_bytes()
        .map_err(CliError::from_pack)?;
    bytes.push(b'\n');
    if output == OsStr::new("-") {
        if mode == OutputMode::Json {
            return Err(CliError::usage(
                "--json cannot be combined with canonical output to stdout",
            ));
        }
        io::stdout()
            .lock()
            .write_all(&bytes)
            .map_err(|error| CliError::operation("io", error.to_string()))?;
        return Ok(());
    }
    let output_path = PathBuf::from(output);
    write_atomic(&output_path, &bytes)?;
    let digest = validated
        .pack()
        .canonical_sha256()
        .map_err(CliError::from_pack)?;
    let result = DigestSummary {
        pack_id: validated.pack().pack_id.as_str(),
        version: &validated.pack().version,
        canonical_sha256: digest,
    };
    emit_success(mode, "pack.canonicalize", &result)
}

fn digest_command(mode: OutputMode, arguments: &[OsString]) -> Result<(), CliError> {
    ensure_argument_count(arguments, 3)?;
    let path = PathBuf::from(argument(arguments, 2)?);
    let validated = load_pack(&path).map_err(CliError::from_pack)?;
    let result = DigestSummary {
        pack_id: validated.pack().pack_id.as_str(),
        version: &validated.pack().version,
        canonical_sha256: validated
            .pack()
            .canonical_sha256()
            .map_err(CliError::from_pack)?,
    };
    emit_success(mode, "pack.digest", &result)
}

fn lock_command(mode: OutputMode, arguments: &[OsString]) -> Result<(), CliError> {
    ensure_argument_count(arguments, 4)?;
    let root = PathBuf::from(argument(arguments, 2)?);
    let action = argument(arguments, 3)?;
    if action == OsStr::new("--write") {
        let lock = write_pack_lock(&root, LockLimits::default())
            .map_err(|error| CliError::operation("lock", error.to_string()))?;
        let result = LockSummary {
            pack_id: lock.pack_id.as_str(),
            version: &lock.pack_version,
            tree_sha256: &lock.tree_sha256,
            files: lock.files.len(),
            mode: "written",
        };
        emit_success(mode, "pack.lock", &result)
    } else if action == OsStr::new("--check") {
        let verified = verify_pack_lock(&root, LockLimits::default())
            .map_err(|error| CliError::operation("lock", error.to_string()))?;
        let result = LockSummary {
            pack_id: verified.pack_id.as_str(),
            version: &verified.pack_version,
            tree_sha256: &verified.tree_sha256,
            files: verified.file_count,
            mode: "verified",
        };
        emit_success(mode, "pack.lock", &result)
    } else {
        Err(CliError::usage(format!(
            "lock requires --write or --check\n\n{USAGE}"
        )))
    }
}

fn argument(arguments: &[OsString], index: usize) -> Result<&OsStr, CliError> {
    arguments
        .get(index)
        .map(OsString::as_os_str)
        .ok_or_else(|| CliError::usage(USAGE))
}

fn ensure_argument_count(arguments: &[OsString], expected: usize) -> Result<(), CliError> {
    if arguments.len() == expected {
        Ok(())
    } else {
        Err(CliError::usage(USAGE))
    }
}

fn emit_success<T: Serialize>(
    mode: OutputMode,
    operation: &'static str,
    result: &T,
) -> Result<(), CliError> {
    match mode {
        OutputMode::Json => write_json(
            &mut io::stdout().lock(),
            &SuccessEnvelope {
                ok: true,
                operation,
                result,
            },
        ),
        OutputMode::Text => {
            let value = serde_json::to_value(result)
                .map_err(|error| CliError::operation("json", error.to_string()))?;
            let text = value.as_object().map_or_else(
                || value.to_string(),
                |object| {
                    object
                        .iter()
                        .map(|(key, value)| format!("{key}: {}", display_json_value(value)))
                        .collect::<Vec<_>>()
                        .join("\n")
                },
            );
            let mut stdout = io::stdout().lock();
            stdout
                .write_all(text.as_bytes())
                .and_then(|()| stdout.write_all(b"\n"))
                .map_err(|error| CliError::operation("io", error.to_string()))
        }
    }
}

fn emit_error(mode: OutputMode, error: &CliError) -> Result<(), CliError> {
    match mode {
        OutputMode::Json => write_json(
            &mut io::stderr().lock(),
            &ErrorEnvelope {
                ok: false,
                error: ErrorBody {
                    kind: error.kind,
                    message: &error.message,
                    diagnostics: error.validation.as_ref(),
                },
            },
        ),
        OutputMode::Text => {
            let mut stderr = io::stderr().lock();
            stderr
                .write_all(error.message.as_bytes())
                .and_then(|()| stderr.write_all(b"\n"))
                .map_err(|write_error| CliError::operation("io", write_error.to_string()))?;
            if let Some(report) = &error.validation {
                for diagnostic in &report.diagnostics {
                    let line = format!(
                        "{:?} {} {}: {}\n",
                        diagnostic.severity, diagnostic.code, diagnostic.path, diagnostic.message
                    );
                    stderr.write_all(line.as_bytes()).map_err(|write_error| {
                        CliError::operation("io", write_error.to_string())
                    })?;
                }
            }
            Ok(())
        }
    }
}

fn write_json<T: Serialize>(writer: &mut impl Write, value: &T) -> Result<(), CliError> {
    serde_json::to_writer(&mut *writer, value)
        .map_err(|error| CliError::operation("json", error.to_string()))?;
    writer
        .write_all(b"\n")
        .map_err(|error| CliError::operation("io", error.to_string()))
}

fn display_json_value(value: &serde_json::Value) -> String {
    value
        .as_str()
        .map_or_else(|| value.to_string(), str::to_owned)
}

fn write_atomic(path: &Path, bytes: &[u8]) -> Result<(), CliError> {
    let parent = path
        .parent()
        .filter(|candidate| !candidate.as_os_str().is_empty())
        .unwrap_or_else(|| Path::new("."));
    let file_name = path
        .file_name()
        .ok_or_else(|| CliError::operation("io", "output path has no file name"))?;
    let temporary = parent.join(format!(
        ".{}.{}.tmp",
        file_name.to_string_lossy(),
        std::process::id()
    ));
    fs::write(&temporary, bytes).map_err(|error| CliError::operation("io", error.to_string()))?;
    if let Err(error) = fs::rename(&temporary, path) {
        let _ignored = fs::remove_file(&temporary);
        return Err(CliError::operation("io", error.to_string()));
    }
    Ok(())
}
