#![no_main]

use libfuzzer_sys::fuzz_target;
use standardflow_core::parse_pack;

fuzz_target!(|data: &[u8]| {
    // Rejection is normal; panic, memory errors and timeouts are failures.
    if let Ok(validated) = parse_pack(data) {
        assert!(validated.report().is_valid());
    }
});
