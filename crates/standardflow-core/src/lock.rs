//! Deterministic, symlink-safe Standard Pack lockfiles.

use std::fs::{self, OpenOptions};
use std::io::{Read, Write};
use std::path::{Component, Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use thiserror::Error;

use crate::canonical::{CanonicalError, canonical_json, sha256_hex};
use crate::pack::{PackError, PackId, load_pack};

const LOCK_FILE_NAME: &str = "standardflow.lock.json";
const PACK_FILE_NAME: &str = "pack.json";
static TEMP_COUNTER: AtomicU64 = AtomicU64::new(0);

/// Defensive limits for recursive lock generation.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub struct LockLimits {
    /// Maximum number of files in one pack.
    pub max_files: usize,
    /// Maximum size of one file.
    pub max_file_bytes: u64,
    /// Maximum aggregate bytes read.
    pub max_total_bytes: u64,
    /// Maximum directory nesting depth.
    pub max_depth: usize,
}

impl Default for LockLimits {
    fn default() -> Self {
        Self {
            max_files: 10_000,
            max_file_bytes: 256 * 1024 * 1024,
            max_total_bytes: 2 * 1024 * 1024 * 1024,
            max_depth: 32,
        }
    }
}

/// One content-addressed file entry.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct LockedFile {
    /// Portable path relative to the pack root.
    pub path: String,
    /// Raw file byte length.
    pub bytes: u64,
    /// SHA-256 of raw file bytes.
    pub sha256: String,
}

/// Deterministic Standard Pack lockfile.
#[derive(Clone, Debug, Deserialize, Eq, PartialEq, Serialize)]
#[serde(deny_unknown_fields)]
pub struct PackLock {
    /// Lock contract version.
    pub schema_version: String,
    /// Digest algorithm.
    pub algorithm: String,
    /// Stable pack identifier.
    pub pack_id: PackId,
    /// Pack release version.
    pub pack_version: String,
    /// SHA-256 of canonical `pack.json` semantics.
    pub canonical_pack_sha256: String,
    /// Sorted raw-file entries, excluding this lockfile.
    pub files: Vec<LockedFile>,
    /// SHA-256 over the sorted file manifest.
    pub tree_sha256: String,
}

/// Successful lock verification summary.
#[derive(Clone, Debug, Eq, PartialEq, Serialize)]
pub struct LockVerification {
    /// Pack identifier.
    pub pack_id: PackId,
    /// Pack version.
    pub pack_version: String,
    /// Verified tree digest.
    pub tree_sha256: String,
    /// Number of locked files.
    pub file_count: usize,
}

/// Lock generation or verification failure.
#[derive(Debug, Error)]
pub enum LockError {
    /// Pack parsing or validation failed.
    #[error(transparent)]
    Pack(#[from] PackError),
    /// Canonical lock serialization failed.
    #[error(transparent)]
    Canonical(#[from] CanonicalError),
    /// JSON lock decoding failed.
    #[error("invalid lock JSON: {0}")]
    Json(#[from] serde_json::Error),
    /// File-system operation failed.
    #[error("{operation} failed for {path}: {source}")]
    Io {
        /// Operation being attempted.
        operation: &'static str,
        /// Affected path.
        path: String,
        /// Underlying error.
        #[source]
        source: std::io::Error,
    },
    /// Pack root is not a real directory.
    #[error("pack root {0} must be a real directory, not a symlink")]
    UnsafeRoot(String),
    /// A symbolic link was encountered in the pack.
    #[error("symbolic links are prohibited in packs: {0}")]
    Symlink(String),
    /// A path cannot be represented portably.
    #[error("pack path is not portable UTF-8: {0}")]
    NonPortablePath(String),
    /// A configured defensive limit was exceeded.
    #[error("pack limit exceeded: {0}")]
    Limit(String),
    /// Existing lockfile does not match current contents.
    #[error("pack lock does not match current contents")]
    Mismatch {
        /// Digest recorded by the existing lock.
        recorded_tree_sha256: String,
        /// Digest computed from current files.
        computed_tree_sha256: String,
    },
    /// An existing lockfile is a symlink.
    #[error("lockfile must not be a symbolic link: {0}")]
    SymlinkLock(String),
}

/// Builds a deterministic lock from a pack directory.
///
/// # Errors
///
/// Returns [`LockError`] for unsafe paths, exceeded limits, invalid `pack.json`,
/// file-system failures or canonicalization failures.
pub fn build_pack_lock(root: &Path, limits: LockLimits) -> Result<PackLock, LockError> {
    validate_root(root)?;
    let validated = load_pack(&root.join(PACK_FILE_NAME))?;
    let canonical_pack_sha256 = validated.pack().canonical_sha256()?;
    let mut files = Vec::new();
    let mut total_bytes = 0_u64;
    collect_files(root, Path::new(""), 0, limits, &mut files, &mut total_bytes)?;
    files.sort_unstable_by(|left, right| left.path.cmp(&right.path));
    let tree_sha256 = manifest_digest(&files);
    Ok(PackLock {
        schema_version: String::from("dev.standardflow.lock.v1"),
        algorithm: String::from("sha256"),
        pack_id: validated.pack().pack_id.clone(),
        pack_version: validated.pack().version.clone(),
        canonical_pack_sha256,
        files,
        tree_sha256,
    })
}

/// Writes a deterministic lock atomically in the pack directory.
///
/// # Errors
///
/// Returns [`LockError`] when lock generation or an atomic file operation fails.
pub fn write_pack_lock(root: &Path, limits: LockLimits) -> Result<PackLock, LockError> {
    let lock = build_pack_lock(root, limits)?;
    let mut bytes = canonical_json(&lock)?;
    bytes.push(b'\n');
    let destination = root.join(LOCK_FILE_NAME);
    reject_symlink_lock(&destination)?;
    let temp = temporary_lock_path(root);
    let result = write_new_file(&temp, &bytes).and_then(|()| {
        fs::rename(&temp, &destination).map_err(|source| LockError::Io {
            operation: "rename temporary lockfile",
            path: destination.display().to_string(),
            source,
        })
    });
    if result.is_err() {
        let _ignored = fs::remove_file(&temp);
    }
    result?;
    Ok(lock)
}

/// Verifies the existing lock against current pack contents.
///
/// # Errors
///
/// Returns [`LockError::Mismatch`] for stale contents and other variants for unsafe
/// paths, invalid data or file-system failures.
pub fn verify_pack_lock(root: &Path, limits: LockLimits) -> Result<LockVerification, LockError> {
    validate_root(root)?;
    let path = root.join(LOCK_FILE_NAME);
    reject_symlink_lock(&path)?;
    let bytes = fs::read(&path).map_err(|source| LockError::Io {
        operation: "read lockfile",
        path: path.display().to_string(),
        source,
    })?;
    let recorded: PackLock = serde_json::from_slice(&bytes)?;
    let computed = build_pack_lock(root, limits)?;
    if recorded != computed {
        return Err(LockError::Mismatch {
            recorded_tree_sha256: recorded.tree_sha256,
            computed_tree_sha256: computed.tree_sha256,
        });
    }
    Ok(LockVerification {
        pack_id: computed.pack_id,
        pack_version: computed.pack_version,
        tree_sha256: computed.tree_sha256,
        file_count: computed.files.len(),
    })
}

fn validate_root(root: &Path) -> Result<(), LockError> {
    let metadata = fs::symlink_metadata(root).map_err(|source| LockError::Io {
        operation: "inspect pack root",
        path: root.display().to_string(),
        source,
    })?;
    if metadata.file_type().is_symlink() || !metadata.is_dir() {
        return Err(LockError::UnsafeRoot(root.display().to_string()));
    }
    Ok(())
}

#[allow(
    clippy::too_many_arguments,
    reason = "All traversal limits and counters are explicit security controls"
)]
fn collect_files(
    root: &Path,
    relative: &Path,
    depth: usize,
    limits: LockLimits,
    files: &mut Vec<LockedFile>,
    total_bytes: &mut u64,
) -> Result<(), LockError> {
    if depth > limits.max_depth {
        return Err(LockError::Limit(format!(
            "directory depth exceeds {}",
            limits.max_depth
        )));
    }
    let directory = root.join(relative);
    let entries = fs::read_dir(&directory).map_err(|source| LockError::Io {
        operation: "read pack directory",
        path: directory.display().to_string(),
        source,
    })?;
    for entry in entries {
        let entry = entry.map_err(|source| LockError::Io {
            operation: "read pack directory entry",
            path: directory.display().to_string(),
            source,
        })?;
        let path = entry.path();
        let name = entry.file_name();
        let child_relative = relative.join(name);
        let metadata = fs::symlink_metadata(&path).map_err(|source| LockError::Io {
            operation: "inspect pack entry",
            path: path.display().to_string(),
            source,
        })?;
        if metadata.file_type().is_symlink() {
            return Err(LockError::Symlink(path.display().to_string()));
        }
        if metadata.is_dir() {
            collect_files(root, &child_relative, depth + 1, limits, files, total_bytes)?;
            continue;
        }
        if !metadata.is_file() {
            return Err(LockError::NonPortablePath(path.display().to_string()));
        }
        let portable = portable_path(&child_relative)?;
        if portable == LOCK_FILE_NAME {
            continue;
        }
        if files.len() >= limits.max_files {
            return Err(LockError::Limit(format!(
                "file count exceeds {}",
                limits.max_files
            )));
        }
        let bytes = read_bounded_file(&path, &portable, limits, *total_bytes)?;
        let observed_bytes = u64::try_from(bytes.len())
            .map_err(|_| LockError::Limit(String::from("file length does not fit u64")))?;
        let next_total = (*total_bytes)
            .checked_add(observed_bytes)
            .ok_or_else(|| LockError::Limit(String::from("aggregate byte count overflow")))?;
        *total_bytes = next_total;
        files.push(LockedFile {
            path: portable,
            bytes: observed_bytes,
            sha256: sha256_hex(&bytes),
        });
    }
    Ok(())
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
    let mut segments = Vec::new();
    for component in path.components() {
        match component {
            Component::Normal(segment) => {
                let text = segment
                    .to_str()
                    .ok_or_else(|| LockError::NonPortablePath(path.display().to_string()))?;
                if text.is_empty() || text == "." || text == ".." {
                    return Err(LockError::NonPortablePath(path.display().to_string()));
                }
                segments.push(text);
            }
            _ => return Err(LockError::NonPortablePath(path.display().to_string())),
        }
    }
    if segments.is_empty() {
        return Err(LockError::NonPortablePath(path.display().to_string()));
    }
    Ok(segments.join("/"))
}

fn manifest_digest(files: &[LockedFile]) -> String {
    let mut digest = Sha256::new();
    for file in files {
        digest.update(file.path.as_bytes());
        digest.update(b"\0");
        digest.update(file.sha256.as_bytes());
        digest.update(b"\0");
        digest.update(file.bytes.to_string().as_bytes());
        digest.update(b"\n");
    }
    sha256_hex(&digest.finalize())
}

fn reject_symlink_lock(path: &Path) -> Result<(), LockError> {
    match fs::symlink_metadata(path) {
        Ok(metadata) if metadata.file_type().is_symlink() => {
            Err(LockError::SymlinkLock(path.display().to_string()))
        }
        Ok(_) => Ok(()),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
        Err(source) => Err(LockError::Io {
            operation: "inspect lockfile",
            path: path.display().to_string(),
            source,
        }),
    }
}

fn temporary_lock_path(root: &Path) -> PathBuf {
    let counter = TEMP_COUNTER.fetch_add(1, Ordering::Relaxed);
    root.join(format!(
        ".{LOCK_FILE_NAME}.{}.{}.tmp",
        std::process::id(),
        counter
    ))
}

fn write_new_file(path: &Path, bytes: &[u8]) -> Result<(), LockError> {
    let mut file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .map_err(|source| LockError::Io {
            operation: "create temporary lockfile",
            path: path.display().to_string(),
            source,
        })?;
    file.write_all(bytes).map_err(|source| LockError::Io {
        operation: "write temporary lockfile",
        path: path.display().to_string(),
        source,
    })?;
    file.sync_all().map_err(|source| LockError::Io {
        operation: "sync temporary lockfile",
        path: path.display().to_string(),
        source,
    })
}

#[cfg(test)]
mod tests {
    use std::fs;
    use std::path::{Path, PathBuf};
    use std::sync::atomic::{AtomicU64, Ordering};

    use super::{
        LockError, LockLimits, build_pack_lock, read_bounded_file, verify_pack_lock,
        write_pack_lock,
    };

    static TEST_COUNTER: AtomicU64 = AtomicU64::new(0);

    struct TestDirectory(PathBuf);

    impl TestDirectory {
        fn create() -> Result<Self, std::io::Error> {
            let counter = TEST_COUNTER.fetch_add(1, Ordering::Relaxed);
            let path = std::env::temp_dir().join(format!(
                "standardflow-lock-test-{}-{counter}",
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

    fn minimal_pack() -> &'static str {
        include_str!("../../../contracts/examples/minimal-standard-pack.v1.json")
    }

    #[test]
    fn lock_is_deterministic_and_detects_changes() -> Result<(), Box<dyn std::error::Error>> {
        let directory = TestDirectory::create()?;
        fs::write(directory.path().join("pack.json"), minimal_pack())?;
        fs::create_dir(directory.path().join("sources"))?;
        fs::write(
            directory.path().join("sources/note.txt"),
            b"source evidence\n",
        )?;

        let first = build_pack_lock(directory.path(), LockLimits::default())?;
        let second = build_pack_lock(directory.path(), LockLimits::default())?;
        assert_eq!(first, second);

        write_pack_lock(directory.path(), LockLimits::default())?;
        let verified = verify_pack_lock(directory.path(), LockLimits::default())?;
        assert_eq!(verified.file_count, 2);

        fs::write(directory.path().join("sources/note.txt"), b"changed\n")?;
        assert!(matches!(
            verify_pack_lock(directory.path(), LockLimits::default()),
            Err(LockError::Mismatch { .. })
        ));
        Ok(())
    }

    #[test]
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
        use std::os::unix::fs::symlink;

        let directory = TestDirectory::create()?;
        fs::write(directory.path().join("pack.json"), minimal_pack())?;
        fs::write(directory.path().join("target.txt"), b"target")?;
        symlink("target.txt", directory.path().join("link.txt"))?;
        assert!(matches!(
            build_pack_lock(directory.path(), LockLimits::default()),
            Err(LockError::Symlink(_))
        ));
        Ok(())
    }
}
