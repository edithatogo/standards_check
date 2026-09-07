//! Deterministic JSON encoding and content digests.

use serde::Serialize;
use serde_json::Value;
use sha2::{Digest, Sha256};
use thiserror::Error;

/// Error produced while creating `StandardFlow` canonical JSON.
#[derive(Debug, Error)]
pub enum CanonicalError {
    /// Serialization into an intermediate JSON value failed.
    #[error("JSON serialization failed: {0}")]
    Serialize(#[from] serde_json::Error),
    /// Floating-point values are excluded from canonical `StandardFlow` contracts.
    #[error("floating-point JSON numbers are not supported at {path}")]
    FloatingPoint {
        /// JSON-pointer-like location.
        path: String,
    },
}

/// Serializes a value using the `StandardFlow` canonical JSON profile.
///
/// Object keys are ordered lexicographically, whitespace is omitted, strings use
/// `serde_json` escaping, and floating-point numbers are rejected. The result has no
/// trailing newline.
pub fn canonical_json<T: Serialize>(value: &T) -> Result<Vec<u8>, CanonicalError> {
    let value = serde_json::to_value(value)?;
    let mut output = Vec::new();
    write_value(&value, "", &mut output)?;
    Ok(output)
}

/// Returns a lowercase SHA-256 digest.
#[must_use]
pub fn sha256_hex(bytes: &[u8]) -> String {
    let digest = Sha256::digest(bytes);
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

fn write_value(value: &Value, path: &str, output: &mut Vec<u8>) -> Result<(), CanonicalError> {
    match value {
        Value::Null => output.extend_from_slice(b"null"),
        Value::Bool(boolean) => {
            output.extend_from_slice(if *boolean { b"true" } else { b"false" });
        }
        Value::Number(number) => {
            if number.is_i64() || number.is_u64() {
                output.extend_from_slice(number.to_string().as_bytes());
            } else {
                return Err(CanonicalError::FloatingPoint {
                    path: display_path(path),
                });
            }
        }
        Value::String(text) => {
            output.extend_from_slice(serde_json::to_string(text)?.as_bytes());
        }
        Value::Array(values) => {
            output.push(b'[');
            for (index, child) in values.iter().enumerate() {
                if index > 0 {
                    output.push(b',');
                }
                let child_path = format!("{path}/{index}");
                write_value(child, &child_path, output)?;
            }
            output.push(b']');
        }
        Value::Object(object) => {
            output.push(b'{');
            let mut keys = object.keys().collect::<Vec<_>>();
            keys.sort_unstable();
            for (index, key) in keys.into_iter().enumerate() {
                if index > 0 {
                    output.push(b',');
                }
                output.extend_from_slice(serde_json::to_string(key)?.as_bytes());
                output.push(b':');
                let escaped_key = key.replace('~', "~0").replace('/', "~1");
                let child_path = format!("{path}/{escaped_key}");
                if let Some(child) = object.get(key) {
                    write_value(child, &child_path, output)?;
                }
            }
            output.push(b'}');
        }
    }
    Ok(())
}

fn display_path(path: &str) -> String {
    if path.is_empty() {
        String::from("/")
    } else {
        path.to_owned()
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::{CanonicalError, canonical_json, sha256_hex};

    #[test]
    fn object_keys_are_sorted() -> Result<(), CanonicalError> {
        let value = json!({"z": 1, "a": {"d": 4, "b": 2}});
        let encoded = canonical_json(&value)?;
        assert_eq!(encoded, br#"{"a":{"b":2,"d":4},"z":1}"#);
        Ok(())
    }

    #[test]
    fn floating_point_values_are_rejected() {
        let value = json!({"measurement": 0.25});
        let result = canonical_json(&value);
        assert!(matches!(
            result,
            Err(CanonicalError::FloatingPoint { path }) if path == "/measurement"
        ));
    }

    #[test]
    fn sha256_matches_a_known_vector() {
        assert_eq!(
            sha256_hex(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        );
    }
}
