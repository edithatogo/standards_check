//! Bounded synthetic parallel-trial participant accounting.

use std::collections::BTreeMap;

use serde::Deserialize;
use thiserror::Error;

use crate::limits::{MAX_INPUT_BYTES, MAX_SAFE_JSON_INTEGER};
use crate::{DiagramRecipe, RecipeError, Scene};

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct TrialArm {
    allocated: u64,
    received: u64,
    not_received: u64,
    followed_up: u64,
    lost_to_follow_up: u64,
    discontinued: u64,
    analysed: u64,
    excluded_from_analysis: u64,
}

impl TrialArm {
    fn valid(&self) -> bool {
        [
            self.allocated,
            self.received,
            self.not_received,
            self.followed_up,
            self.lost_to_follow_up,
            self.discontinued,
            self.analysed,
            self.excluded_from_analysis,
        ]
        .iter()
        .all(|&n| n <= MAX_SAFE_JSON_INTEGER)
            && self.received + self.not_received == self.allocated
            && self.followed_up + self.lost_to_follow_up == self.allocated
            && self.discontinued <= self.received
            && self.analysed + self.excluded_from_analysis == self.allocated
    }

    fn bindings(&self, arm: &str, bindings: &mut BTreeMap<String, String>) {
        for (field, count) in [
            ("allocated", self.allocated),
            ("received", self.received),
            ("not_received", self.not_received),
            ("followed_up", self.followed_up),
            ("lost_to_follow_up", self.lost_to_follow_up),
            ("discontinued", self.discontinued),
            ("analysed", self.analysed),
            ("excluded_from_analysis", self.excluded_from_analysis),
        ] {
            bindings.insert(format!("{arm}_{field}"), count.to_string());
        }
    }
}

#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct TrialFlow {
    schema_version: String,
    analysis_population: String,
    assessed: u64,
    excluded: u64,
    randomized: u64,
    arm_a: TrialArm,
    arm_b: TrialArm,
}

/// Errors from the synthetic trial-flow consumer boundary.
#[derive(Debug, Error)]
pub enum TrialFlowError {
    /// Invalid JSON or unexpected fields.
    #[error("invalid trial-flow JSON: {0}")]
    Json(#[from] serde_json::Error),
    /// Unsupported scope, resource limit or inconsistent participant partition.
    #[error("invalid trial-flow scope or participant accounting")]
    Invalid,
    /// Existing recipe or scene validation failure.
    #[error(transparent)]
    Recipe(#[from] RecipeError),
}

/// Build a candidate two-arm scene using the existing validated recipe engine.
///
/// This contract requires all receipt, follow-up and analysis partitions to
/// use allocated participants as their denominator. Discontinuation is a
/// subset of receipt; its overlap with follow-up and analysis is unspecified.
/// It does not implement or certify the official CONSORT flow diagram.
///
/// # Errors
/// Returns an error for an unsupported contract, inconsistent counts or recipe failure.
pub fn build_trial_scene(input: &[u8]) -> Result<Scene, TrialFlowError> {
    if input.len() > MAX_INPUT_BYTES {
        return Err(TrialFlowError::Invalid);
    }
    let trial: TrialFlow = serde_json::from_slice(input)?;
    if trial.schema_version != "dev.standardflow.trial-flow.v1"
        || trial.analysis_population != "allocated_partition"
        || [trial.assessed, trial.excluded, trial.randomized]
            .iter()
            .any(|&n| n > MAX_SAFE_JSON_INTEGER)
        || !trial.arm_a.valid()
        || !trial.arm_b.valid()
        || trial.assessed != trial.excluded + trial.randomized
        || trial.randomized != trial.arm_a.allocated + trial.arm_b.allocated
    {
        return Err(TrialFlowError::Invalid);
    }
    let mut bindings = BTreeMap::from([
        (String::from("assessed"), trial.assessed.to_string()),
        (String::from("excluded"), trial.excluded.to_string()),
        (String::from("randomized"), trial.randomized.to_string()),
    ]);
    trial.arm_a.bindings("a", &mut bindings);
    trial.arm_b.bindings("b", &mut bindings);
    let recipe = DiagramRecipe::from_json(include_bytes!(
        "../../../recipes/trial-flow/synthetic-two-arm.json"
    ))?;
    Ok(recipe.build_scene(&bindings)?)
}
