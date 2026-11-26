//! Candidate non-PRISMA consumer contract and partition mutations.

use standardflow_artifacts::{RenderFormat, build_trial_scene, render};

const INPUT: &[u8] =
    include_bytes!("../../../contracts/examples/trial-flow/synthetic-two-arm.json");

#[test]
fn trial_scene_is_deterministic_and_preserves_denominators()
-> Result<(), Box<dyn std::error::Error>> {
    let scene = build_trial_scene(INPUT)?;
    assert_eq!(scene.nodes.len(), 3);
    assert_eq!(scene.edges.len(), 2);
    for format in [
        RenderFormat::Svg,
        RenderFormat::Text,
        RenderFormat::SceneJson,
    ] {
        assert_eq!(
            render(&scene, format)?,
            render(&build_trial_scene(INPUT)?, format)?
        );
    }
    assert!(scene.text_equivalent.contains("Analysed (n = 48)"));
    assert!(scene.text_equivalent.contains("Lost") || scene.text_equivalent.contains("lost"));
    Ok(())
}

#[test]
fn invalid_trial_counts_fail_closed() -> Result<(), Box<dyn std::error::Error>> {
    for path in [
        "/assessed",
        "/randomized",
        "/arm_a/allocated",
        "/arm_a/not_received",
        "/arm_a/lost_to_follow_up",
        "/arm_b/excluded_from_analysis",
    ] {
        let mut trial: serde_json::Value = serde_json::from_slice(INPUT)?;
        *trial
            .pointer_mut(path)
            .ok_or_else(|| std::io::Error::other("missing fixture field"))? =
            serde_json::Value::from(999_u64);
        assert!(build_trial_scene(&serde_json::to_vec(&trial)?).is_err());
    }
    assert!(build_trial_scene(b"{}").is_err());
    Ok(())
}

#[test]
fn trial_rejects_oversize_and_unsupported_scope() -> Result<(), Box<dyn std::error::Error>> {
    use standardflow_artifacts::{TrialFlowError, limits::MAX_INPUT_BYTES};

    assert!(matches!(
        build_trial_scene(&vec![b' '; MAX_INPUT_BYTES + 1]),
        Err(TrialFlowError::Invalid)
    ));
    for (path, value) in [
        ("/schema_version", serde_json::Value::from("unknown")),
        (
            "/analysis_population",
            serde_json::Value::from("per_protocol"),
        ),
        ("/arm_a/discontinued", serde_json::Value::from(46_u64)),
        ("/arm_b/received", serde_json::Value::from(u64::MAX)),
        ("/assessed", serde_json::Value::from(u64::MAX)),
    ] {
        let mut trial: serde_json::Value = serde_json::from_slice(INPUT)?;
        *trial
            .pointer_mut(path)
            .ok_or_else(|| std::io::Error::other("missing fixture field"))? = value;
        assert!(matches!(
            build_trial_scene(&serde_json::to_vec(&trial)?),
            Err(TrialFlowError::Invalid)
        ));
    }
    Ok(())
}
