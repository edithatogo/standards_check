#!/usr/bin/env python3
"""Verify, extract, and patch the staged Track 01 implementation overlay."""
from __future__ import annotations

import base64
import hashlib
import io
from pathlib import Path
import shutil
import tarfile

ROOT = Path.cwd()
STAGING = ROOT / ".track01-bootstrap"
ARCHIVE_SHA256 = "baa0c61f32db4699e97df9a29e3a9f5d22a2f4ea8509f8f73557d54e255df315"
PARTS = (
    ("overlay.b64.part00", "158487e66a8c3df16dc2790d58d4ebd837d7c187c79ac4f0d8be546906c502e2"),
    ("overlay.b64.part01", "3f6f24bed20f40a02fda53e4ecf218db233ce78a3e018a58e6c50993ccee6697"),
    ("overlay.b64.part02a", "fa75a03f7ed1e3cc94bd9cf69762627edf32ca5471117cc1d40e682aced1a37d"),
    ("overlay.b64.part02b", "4f3a838f47fdc75b76202cf7fcac430ff0f7cf90338591c4bd8bcadada3241dd"),
    ("overlay.b64.part03", "6bdb94015466c1ea95163633fb08ccde18b0dea4235cc2b79568c82855283e50"),
    ("overlay.b64.part04", "78e8e2da2fe412ba66c5a5dff25a15377ad539ffcd6313df3802f90f4b9bb033"),
    ("overlay.b64.part05", "788e2eff2d6d1b0652210e66ea8718c828526b40ed48c6556f5ec80fa5cbb574"),
    ("overlay.b64.part06", "8bbbd4190623c75ebd661f9abff293db38bfe723418f26a2204f7828a5100eed"),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace(path: str, old: str, new: str) -> None:
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"expected source fragment not found in {path}")
    file.write_text(text.replace(old, new), encoding="utf-8")


def verify_and_extract() -> None:
    part_zero = STAGING / "overlay.b64.part00"
    text = part_zero.read_text(encoding="ascii")
    if len(text) == 6999:
        text = text[:1367] + "J" + text[1367:]
        part_zero.write_text(text, encoding="ascii")

    encoded = bytearray()
    for name, expected in PARTS:
        data = (STAGING / name).read_bytes()
        observed = digest(data)
        if observed != expected:
            raise SystemExit(f"segment integrity failure: {name}: {observed}")
        encoded.extend(data)

    archive_bytes = base64.b64decode(bytes(encoded), validate=True)
    observed_archive = digest(archive_bytes)
    if observed_archive != ARCHIVE_SHA256:
        raise SystemExit(f"archive integrity failure: {observed_archive}")

    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        archive.extractall(ROOT, filter="data")

    shutil.rmtree(ROOT / "scripts/__pycache__", ignore_errors=True)


def apply_core_fixes() -> None:
    canonical = "crates/standardflow-core/src/canonical.rs"
    replace(
        canonical,
        "/// Error produced while creating StandardFlow canonical JSON.",
        "/// Error produced while creating `StandardFlow` canonical JSON.",
    )
    replace(
        canonical,
        "/// Floating-point values are excluded from canonical StandardFlow contracts.",
        "/// Floating-point values are excluded from canonical `StandardFlow` contracts.",
    )
    replace(
        canonical,
        "/// Serializes a value using the StandardFlow canonical JSON profile.",
        "/// Serializes a value using the `StandardFlow` canonical JSON profile.",
    )
    replace(
        canonical,
        '''    let digest = Sha256::digest(bytes);
    let mut output = String::with_capacity(digest.len() * 2);
    const HEX: &[u8; 16] = b"0123456789abcdef";
    for byte in digest {
        output.push(char::from(HEX[usize::from(byte >> 4)]));
        output.push(char::from(HEX[usize::from(byte & 0x0f)]));
    }
    output
}
''',
        '''    let digest = Sha256::digest(bytes);
    let mut output = String::with_capacity(digest.len() * 2);
    for byte in digest {
        output.push(hex_digit(byte >> 4));
        output.push(hex_digit(byte & 0x0f));
    }
    output
}

const fn hex_digit(nibble: u8) -> char {
    match nibble {
        0 => '0',
        1 => '1',
        2 => '2',
        3 => '3',
        4 => '4',
        5 => '5',
        6 => '6',
        7 => '7',
        8 => '8',
        9 => '9',
        10 => 'a',
        11 => 'b',
        12 => 'c',
        13 => 'd',
        14 => 'e',
        15 => 'f',
        _ => '?',
    }
}
''',
    )

    evidence = "crates/standardflow-core/src/evidence.rs"
    replace(
        evidence,
        "//! Evidence and authority types shared across StandardFlow boundaries.",
        "//! Evidence and authority types shared across `StandardFlow` boundaries.",
    )

    lock = "crates/standardflow-core/src/lock.rs"
    replace(lock, "use std::fs::{self, File, OpenOptions};", "use std::fs::{self, OpenOptions};")
    replace(
        lock,
        '''fn manifest_digest(files: &[LockedFile]) -> String {
    let mut digest = Sha256::new();
    for file in files {
        digest.update(file.path.as_bytes());
        digest.update([0]);
        digest.update(file.sha256.as_bytes());
        digest.update([0]);
        digest.update(file.bytes.to_string().as_bytes());
        digest.update([b'\\n']);
    }
    let bytes = digest.finalize();
    let mut output = String::with_capacity(bytes.len() * 2);
    const HEX: &[u8; 16] = b"0123456789abcdef";
    for byte in bytes {
        output.push(char::from(HEX[usize::from(byte >> 4)]));
        output.push(char::from(HEX[usize::from(byte & 0x0f)]));
    }
    output
}
''',
        '''fn manifest_digest(files: &[LockedFile]) -> String {
    let mut digest = Sha256::new();
    for file in files {
        digest.update(file.path.as_bytes());
        digest.update(b"\\0");
        digest.update(file.sha256.as_bytes());
        digest.update(b"\\0");
        digest.update(file.bytes.to_string().as_bytes());
        digest.update(b"\\n");
    }
    sha256_hex(&digest.finalize())
}
''',
    )

    pack = "crates/standardflow-core/src/pack.rs"
    replace(
        pack,
        '''        if let Some(number) = requirement.display_number.as_deref() {
            if let Some(previous) = display_numbers.insert(number, index) {
                report.push(Diagnostic::warning(
                    "SF-REQ-009",
                    format!("{path}/display_number"),
                    format!("display number duplicates requirement index {previous}"),
                ));
            }
        }
''',
        '''        if let Some(number) = requirement.display_number.as_deref()
            && let Some(previous) = display_numbers.insert(number, index)
        {
            report.push(Diagnostic::warning(
                "SF-REQ-009",
                format!("{path}/display_number"),
                format!("display number duplicates requirement index {previous}"),
            ));
        }
''',
    )
    replace(
        pack,
        '''fn is_iso_date(value: &str) -> bool {
    let bytes = value.as_bytes();
    if bytes.len() != 10 || bytes[4] != b'-' || bytes[7] != b'-' {
        return false;
    }
    let Some(year) = parse_decimal(&bytes[0..4]) else {
        return false;
    };
    let Some(month) = parse_decimal(&bytes[5..7]) else {
        return false;
    };
    let Some(day) = parse_decimal(&bytes[8..10]) else {
        return false;
    };
    let max_day = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if is_leap_year(year) => 29,
        2 => 28,
        _ => return false,
    };
    (1..=max_day).contains(&day)
}
''',
        '''fn is_iso_date(value: &str) -> bool {
    let mut parts = value.split('-');
    let Some(year_text) = parts.next() else {
        return false;
    };
    let Some(month_text) = parts.next() else {
        return false;
    };
    let Some(day_text) = parts.next() else {
        return false;
    };
    if parts.next().is_some()
        || year_text.len() != 4
        || month_text.len() != 2
        || day_text.len() != 2
    {
        return false;
    }
    let Some(year) = parse_decimal(year_text.as_bytes()) else {
        return false;
    };
    let Some(month) = parse_decimal(month_text.as_bytes()) else {
        return false;
    };
    let Some(day) = parse_decimal(day_text.as_bytes()) else {
        return false;
    };
    let max_day = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if is_leap_year(year) => 29,
        2 => 28,
        _ => return false,
    };
    (1..=max_day).contains(&day)
}
''',
    )
    replace(pack, "fn is_leap_year(year: u32) -> bool {", "const fn is_leap_year(year: u32) -> bool {")


def apply_cli_fixes() -> None:
    main = "crates/standardflow-cli/src/main.rs"
    replace(main, "struct SuccessEnvelope<T: Serialize> {", "struct SuccessEnvelope<T> {")
    replace(
        main,
        '''            let text = value
                .as_object()
                .map(|object| {
                    object
                        .iter()
                        .map(|(key, value)| format!("{key}: {}", display_json_value(value)))
                        .collect::<Vec<_>>()
                        .join("\\n")
                })
                .unwrap_or_else(|| value.to_string());
''',
        '''            let text = value.as_object().map_or_else(
                || value.to_string(),
                |object| {
                    object
                        .iter()
                        .map(|(key, value)| format!("{key}: {}", display_json_value(value)))
                        .collect::<Vec<_>>()
                        .join("\\n")
                },
            );
''',
    )

    test_file = ROOT / "crates/standardflow-cli/tests/cli.rs"
    test_text = test_file.read_text(encoding="utf-8")
    crate_docs = "//! CLI integration tests for the `StandardFlow` pack commands.\n\n"
    if not test_text.startswith("//!"):
        test_file.write_text(crate_docs + test_text, encoding="utf-8")


if __name__ == "__main__":
    verify_and_extract()
    apply_core_fixes()
    apply_cli_fixes()
    print("Track 01 overlay verified, extracted, and patched")
