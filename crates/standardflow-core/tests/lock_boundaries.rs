//! Native filesystem boundaries exercised through the public lock API.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};

use standardflow_core::{
    LockError, LockLimits, build_pack_lock, verify_pack_lock, write_pack_lock,
};

static NEXT_DIRECTORY: AtomicU64 = AtomicU64::new(0);
const PACK: &str = include_str!("../../../contracts/examples/minimal-standard-pack.v1.json");

struct Directory(PathBuf);

impl Directory {
    fn new() -> io::Result<Self> {
        let counter = NEXT_DIRECTORY.fetch_add(1, Ordering::Relaxed);
        let path = std::env::temp_dir().join(format!(
            "standardflow-lock-boundary-{}-{counter}",
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

#[test]
fn traversal_limits_fail_before_returning_a_partial_manifest()
-> Result<(), Box<dyn std::error::Error>> {
    let directory = Directory::new()?;
    fs::create_dir(directory.path().join("nested"))?;
    fs::write(directory.path().join("nested/evidence.txt"), b"evidence")?;
    for limits in [
        LockLimits {
            max_files: 1,
            ..LockLimits::default()
        },
        LockLimits {
            max_depth: 0,
            ..LockLimits::default()
        },
        LockLimits {
            max_total_bytes: 1,
            ..LockLimits::default()
        },
    ] {
        assert!(matches!(
            build_pack_lock(directory.path(), limits),
            Err(LockError::Limit(_))
        ));
        assert!(!directory.path().join("standardflow.lock.json").exists());
    }
    Ok(())
}

#[test]
fn lock_read_rejects_nonregular_and_overflowing_inputs() -> Result<(), Box<dyn std::error::Error>> {
    let directory = Directory::new()?;
    let lock = directory.path().join("standardflow.lock.json");
    fs::write(&lock, b"")?;
    let unbounded = LockLimits {
        max_total_bytes: u64::MAX,
        max_file_bytes: u64::MAX,
        ..LockLimits::default()
    };
    assert!(matches!(verify_pack_lock(directory.path(), unbounded),
        Err(LockError::Limit(message)) if message.contains("overflow")));
    fs::remove_file(&lock)?;
    fs::create_dir(&lock)?;
    let preserved = lock.join("preserved.txt");
    fs::write(&preserved, b"approved")?;
    let result = verify_pack_lock(directory.path(), LockLimits::default());
    // Windows refuses an ordinary read-only open of a directory. Unix opens it,
    // then the metadata check rejects it before any lock JSON can be decoded.
    #[cfg(windows)]
    assert!(matches!(
        result,
        Err(LockError::Io { operation: "open pack file", path, source })
            if Path::new(&path) == lock && source.kind() == io::ErrorKind::PermissionDenied
    ));
    #[cfg(not(windows))]
    assert!(matches!(
        result,
        Err(LockError::NonPortablePath(path)) if Path::new(&path) == lock
    ));
    assert!(lock.is_dir());
    assert_eq!(fs::read(preserved)?, b"approved");
    Ok(())
}

#[test]
fn invalid_roots_and_malformed_locks_cannot_report_verification()
-> Result<(), Box<dyn std::error::Error>> {
    let directory = Directory::new()?;
    let pack = directory.path().join("pack.json");
    assert!(matches!(
        build_pack_lock(&pack, LockLimits::default()),
        Err(LockError::UnsafeRoot(_))
    ));
    assert!(matches!(
        build_pack_lock(&pack.with_extension("missing"), LockLimits::default()),
        Err(LockError::Io { .. })
    ));
    let lock = directory.path().join("standardflow.lock.json");
    assert!(matches!(
        verify_pack_lock(directory.path(), LockLimits::default()),
        Err(LockError::Io { .. })
    ));
    fs::write(&lock, b"{not-json}")?;
    assert!(matches!(
        verify_pack_lock(directory.path(), LockLimits::default()),
        Err(LockError::Json(_))
    ));
    fs::remove_file(&lock)?;
    fs::create_dir(&lock)?;
    assert!(matches!(
        write_pack_lock(directory.path(), LockLimits::default()),
        Err(LockError::Io { .. })
    ));
    let entries = fs::read_dir(directory.path())?.collect::<Result<Vec<_>, _>>()?;
    assert!(
        !entries
            .iter()
            .any(|entry| entry.file_name().to_string_lossy().ends_with(".tmp"))
    );
    Ok(())
}

#[cfg(unix)]
#[test]
fn native_symlink_boundaries_preserve_the_target() -> Result<(), Box<dyn std::error::Error>> {
    use std::os::unix::fs::symlink;

    let directory = Directory::new()?;
    let victim = directory.path().join("approved.txt");
    fs::write(&victim, b"approved")?;
    let lock = directory.path().join("standardflow.lock.json");
    symlink(&victim, &lock)?;
    assert!(matches!(
        verify_pack_lock(directory.path(), LockLimits::default()),
        Err(LockError::SymlinkLock(_))
    ));
    assert_eq!(fs::read(&victim)?, b"approved");
    fs::remove_file(&lock)?;
    let root_link = directory.path().join("root-link");
    symlink(directory.path(), &root_link)?;
    assert!(matches!(
        build_pack_lock(&root_link, LockLimits::default()),
        Err(LockError::UnsafeRoot(_))
    ));
    fs::remove_file(root_link)?;
    assert_eq!(fs::read(victim)?, b"approved");
    Ok(())
}

// The Linux CI filesystem admits this fixture; macOS rejects these filename
// bytes during creation, before the pack API can inspect them.
#[cfg(target_os = "linux")]
#[test]
fn non_utf8_filename_cannot_enter_a_pack_manifest() -> Result<(), Box<dyn std::error::Error>> {
    use std::os::unix::ffi::OsStrExt;

    let directory = Directory::new()?;
    let invalid = directory
        .path()
        .join(std::ffi::OsStr::from_bytes(b"invalid-\xff"));
    fs::write(&invalid, b"data")?;
    assert!(matches!(
        build_pack_lock(directory.path(), LockLimits::default()),
        Err(LockError::NonPortablePath(_))
    ));
    assert_eq!(fs::read(invalid)?, b"data");
    assert!(!directory.path().join("standardflow.lock.json").exists());
    Ok(())
}
