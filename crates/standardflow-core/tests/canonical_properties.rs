//! Bounded generated contracts for canonical bytes and portable identifiers.
//!
//! Values are synthetic; source reconciliation and rights gates are unaffected.

use proptest::prelude::*;
use proptest::test_runner::FileFailurePersistence;
use serde_json::{Map, Value};
use standardflow_core::{CanonicalError, PackId, canonical_json, parse_pack, sha256_hex};

fn integer_json() -> BoxedStrategy<Value> {
    let leaf = prop_oneof![
        Just(Value::Null),
        any::<bool>().prop_map(Value::Bool),
        any::<i64>().prop_map(|value| Value::Number(value.into())),
        any::<u64>().prop_map(|value| Value::Number(value.into())),
        ".{0,32}".prop_map(Value::String),
    ];
    leaf.prop_recursive(4, 64, 8, |child| {
        prop_oneof![
            prop::collection::vec(child.clone(), 0..8).prop_map(Value::Array),
            prop::collection::btree_map(".{0,16}", child, 0..8)
                .prop_map(|entries| Value::Object(entries.into_iter().collect())),
        ]
    })
    .boxed()
}

proptest! {
    #![proptest_config(ProptestConfig {
        cases: 256,
        max_shrink_iters: 4096,
        failure_persistence: Some(Box::new(FileFailurePersistence::WithSource("proptest-regressions"))),
        ..ProptestConfig::default()
    })]

    #[test]
    fn integer_json_preserves_values_and_is_canonically_idempotent(value in integer_json()) {
        let encoded = canonical_json(&value)?;
        let decoded: Value = serde_json::from_slice(&encoded)?;
        prop_assert_eq!(&decoded, &value);
        let recoded = canonical_json(&decoded)?;
        prop_assert_eq!(&encoded, &recoded);
        prop_assert_eq!(sha256_hex(&encoded), sha256_hex(&recoded));
        prop_assert!(!encoded.ends_with(b"\n"));
    }

    #[test]
    fn object_wire_order_and_whitespace_do_not_change_canonical_bytes(
        entries in prop::collection::btree_map(".{0,16}", integer_json(), 1..8),
    ) {
        // Construct reverse-order wire bytes directly: serde_json::Map normally
        // sorts keys, so collecting a reversed map would not test input order.
        let mut fields = Vec::new();
        for (key, value) in entries.iter().rev() {
            fields.push(format!("{} : {}", serde_json::to_string(key)?, serde_json::to_string(value)?));
        }
        let reverse_wire = format!("{{\n {}\n}}", fields.join(",\n "));
        let decoded: Value = serde_json::from_str(&reverse_wire)?;
        let original = Value::Object(entries.into_iter().collect());
        prop_assert_eq!(canonical_json(&decoded)?, canonical_json(&original)?);
    }

    #[test]
    fn rejected_float_paths_preserve_escaped_keys_and_array_indices(
        prefix in "[a-z0-9]{0,12}",
        suffix in "[a-z0-9]{0,12}",
        index in 0_usize..8,
    ) {
        let key = format!("{prefix}~/{suffix}");
        let mut values = vec![Value::Null; index];
        values.push(serde_json::json!(0.25));
        let mut object = Map::new();
        object.insert(key, Value::Array(values));
        let result = canonical_json(&Value::Object(object));
        let expected = format!("/{prefix}~0~1{suffix}/{index}");
        prop_assert!(matches!(result, Err(CanonicalError::FloatingPoint { path }) if path == expected), "float diagnostic path must match the generated position");
    }

    #[test]
    fn untrusted_or_mutated_pack_bytes_never_panic(
        bytes in prop::collection::vec(any::<u8>(), 0..4096),
        mutation_position in any::<usize>(),
        replacement in any::<u8>(),
    ) {
        // Bounded arbitrary bytes plus one-byte mutations of an actual valid
        // pack exercise both the JSON boundary and deeper semantic validation.
        // This is property-based input mutation, not an OpenSSF-recognised fuzzer.
        let _ = parse_pack(&bytes);
        let mut known = include_bytes!("../../../packs/org.prisma/prisma/2020/pack.json").to_vec();
        let index = mutation_position % known.len();
        known[index] = replacement;
        let _ = parse_pack(&known);
    }

    #[test]
    fn valid_pack_ids_round_trip_and_separator_mutations_fail_closed(
        segments in prop::collection::vec("[a-z0-9][a-z0-9._-]{0,16}", 2..6),
    ) {
        let text = segments.join("/");
        let parsed = PackId::parse(&text)?;
        let wire = serde_json::to_string(&parsed)?;
        let decoded: PackId = serde_json::from_str(&wire)?;
        prop_assert_eq!(decoded.as_str(), text.as_str());
        for invalid in [
            format!("/{text}"),
            format!("{text}/"),
            format!("{text}//extra"),
            format!("{text}/../extra"),
            format!("{text}/./extra"),
            format!("{text}\\extra"),
            format!("{text}/Upper"),
        ] {
            prop_assert!(PackId::parse(&invalid).is_err(), "accepted {invalid}");
            let invalid_wire = serde_json::to_string(&invalid)?;
            prop_assert!(serde_json::from_str::<PackId>(&invalid_wire).is_err());
        }
    }
}
