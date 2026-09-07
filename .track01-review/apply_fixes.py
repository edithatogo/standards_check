#!/usr/bin/env python3
"""Apply reviewed Track 01 security corrections and regression tests."""
from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()


def replace(path: str, old: str, new: str) -> None:
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"expected source fragment not found in {path}")
    file.write_text(text.replace(old, new), encoding="utf-8")


lock_path = "crates/standardflow-core/src/lock.rs"
replace(lock_path, "use std::io::Write;", "use std::io::{Read, Write};")
replace(
    lock_path,
    '''        if metadata.len() > limits.max_file_bytes {
            return Err(LockError::Limit(format!(
                "{portable} exceeds the per-file limit of {} bytes",
                limits.max_file_bytes
            )));
        }
        let next_total = total_bytes
            .checked_add(metadata.len())
            .ok_or_else(|| LockError::Limit(String::from("aggregate byte count overflow")))?;
        if next_total > limits.max_total_bytes {
            return Err(LockError::Limit(format!(
                "aggregate bytes exceed {}",
                limits.max_total_bytes
            )));
        }
        let bytes = fs::read(&path).map_err(|source| LockError::Io {
            operation: "read pack file",
            path: path.display().to_string(),
            source,
        })?;
        let observed_bytes = u64::try_from(bytes.len())
            .map_err(|_| LockError::Limit(String::from("file length does not fit u64")))?;
        if observed_bytes != metadata.len() {
            return Err(LockError::Limit(format!(
                "{portable} changed while the lock was being generated"
            )));
        }
        *total_bytes = next_total;
''',
    '''        let bytes = read_bounded_file(&path, &portable, limits, *total_bytes)?;
        let observed_bytes = u64::try_from(bytes.len())
            .map_err(|_| LockError::Limit(String::from("file length does not fit u64")))?;
        let next_total = (*total_bytes)
            .checked_add(observed_bytes)
            .ok_or_else(|| LockError::Limit(String::from("aggregate byte count overflow")))?;
        *total_bytes = next_total;
''',
)
replace(
    lock_path,
    '''    Ok(())
}

fn portable_path(path: &Path) -> Result<String, LockError> {
''',
    '''    Ok(())
}

fn read_bounded_file(
    path: &Path,
    portable: &str,
    limits: LockLimits,
    total_bytes: u64,
) -> Result<Vec<u8>, LockError> {
    let file = OpenOptions::new()
        .read(true)
        .open(path)
        .map_err(|source| LockError::Io {
            operation: "open pack file",
            path: path.display().to_string(),
            source,
        })?;
    let before = file.metadata().map_err(|source| LockError::Io {
        operation: "inspect opened pack file",
        path: path.display().to_string(),
        source,
    })?;
    if !before.is_file() {
        return Err(LockError::NonPortablePath(path.display().to_string()));
    }
    if before.len() > limits.max_file_bytes {
        return Err(LockError::Limit(format!(
            "{portable} exceeds the per-file limit of {} bytes",
            limits.max_file_bytes
        )));
    }
    let remaining_total = limits
        .max_total_bytes
        .checked_sub(total_bytes)
        .ok_or_else(|| LockError::Limit(String::from("aggregate bytes already exceed limit")))?;
    if before.len() > remaining_total {
        return Err(LockError::Limit(format!(
            "aggregate bytes exceed {}",
            limits.max_total_bytes
        )));
    }
    let read_limit = limits
        .max_file_bytes
        .min(remaining_total)
        .checked_add(1)
        .ok_or_else(|| LockError::Limit(String::from("bounded read limit overflow")))?;
    let mut reader = file.take(read_limit);
    let mut bytes = Vec::new();
    reader
        .read_to_end(&mut bytes)
        .map_err(|source| LockError::Io {
            operation: "read pack file through bounded reader",
            path: path.display().to_string(),
            source,
        })?;
    let observed_bytes = u64::try_from(bytes.len())
        .map_err(|_| LockError::Limit(String::from("file length does not fit u64")))?;
    if observed_bytes > limits.max_file_bytes {
        return Err(LockError::Limit(format!(
            "{portable} exceeds the per-file limit of {} bytes",
            limits.max_file_bytes
        )));
    }
    if observed_bytes > remaining_total {
        return Err(LockError::Limit(format!(
            "aggregate bytes exceed {}",
            limits.max_total_bytes
        )));
    }
    let file = reader.into_inner();
    let after = file.metadata().map_err(|source| LockError::Io {
        operation: "reinspect opened pack file",
        path: path.display().to_string(),
        source,
    })?;
    let path_after = fs::symlink_metadata(path).map_err(|source| LockError::Io {
        operation: "reinspect pack path",
        path: path.display().to_string(),
        source,
    })?;
    if path_after.file_type().is_symlink() {
        return Err(LockError::Symlink(path.display().to_string()));
    }
    if !path_after.is_file()
        || before.len() != observed_bytes
        || after.len() != observed_bytes
        || path_after.len() != observed_bytes
    {
        return Err(LockError::Limit(format!(
            "{portable} changed while the lock was being generated"
        )));
    }
    Ok(bytes)
}

fn portable_path(path: &Path) -> Result<String, LockError> {
''',
)
replace(
    lock_path,
    '''    use super::{LockError, LockLimits, build_pack_lock, verify_pack_lock, write_pack_lock};
''',
    '''    use super::{
        LockError, LockLimits, build_pack_lock, read_bounded_file, verify_pack_lock,
        write_pack_lock,
    };
''',
)
replace(
    lock_path,
    '''    #[cfg(unix)]
    #[test]
    fn lock_rejects_symlinks() -> Result<(), Box<dyn std::error::Error>> {
''',
    '''    #[test]
    fn bounded_reader_rejects_oversized_files() -> Result<(), Box<dyn std::error::Error>> {
        let directory = TestDirectory::create()?;
        let path = directory.path().join("payload.bin");
        fs::write(&path, [0_u8; 32])?;
        let limits = LockLimits {
            max_files: 1,
            max_file_bytes: 8,
            max_total_bytes: 16,
            max_depth: 1,
        };
        let result = read_bounded_file(&path, "payload.bin", limits, 0);
        assert!(matches!(
            result,
            Err(LockError::Limit(message)) if message.contains("per-file limit")
        ));
        Ok(())
    }

    #[cfg(unix)]
    #[test]
    fn lock_rejects_symlinks() -> Result<(), Box<dyn std::error::Error>> {
''',
)

pack_path = "crates/standardflow-core/src/pack.rs"
replace(
    pack_path,
    '''        value = value * 10 + u32::from(byte - b'0');
''',
    '''        value = value
            .checked_mul(10)?
            .checked_add(u32::from(byte - b'0'))?;
''',
)
replace(
    pack_path,
    '''impl fmt::Display for ValidationReport {
''',
    '''#[cfg(test)]
mod decimal_tests {
    use super::parse_decimal;

    #[test]
    fn decimal_parser_rejects_overflow() {
        assert_eq!(parse_decimal(b"999999999999999999999"), None);
    }
}

impl fmt::Display for ValidationReport {
''',
)

canonical_path = "crates/standardflow-core/src/canonical.rs"
replace(
    canonical_path,
    '''    #[test]
    fn sha256_matches_a_known_vector() {
''',
    '''    #[test]
    fn diagnostic_paths_use_rfc_6901_escape_order() {
        let value = json!({"~/": 0.25});
        let result = canonical_json(&value);
        assert!(matches!(
            result,
            Err(CanonicalError::FloatingPoint { path }) if path == "/~0~1"
        ));
    }

    #[test]
    fn sha256_matches_a_known_vector() {
''',
)

print("Track 01 review fixes applied")
