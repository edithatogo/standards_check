# E18 native-format dependency qualification

The candidate sources are copied byte-for-byte from PR #180 for independent
development qualification. The production workspace and its lockfile are unchanged.
This path-filtered, read-only workflow resolves the four exact direct pins in an
isolated workspace and retains the registry-only, checksum-bound candidate lock.
It checks the existing repository dependency policy before any compilation.
Only a passing policy allows the exact graph to be fetched and the synthetic
probe to execute offline. A failed resolution, security/rights check, compilation
or assertion is a retained negative result; it is not permission to relax policy.

This first hosted run may generate a candidate lock. A later replay must use the
reviewed exact lockfile committed in the isolated candidate scope. No production
normalization, official standard or scientific claim follows from a development
probe. The publication and Conductor remain under T02.060 and T05.060-062 (#158).
The pinned parser handles structure only, not TeX expansion or Typst evaluation;
the weighted path fixture is not general-purpose transduction qualification.
No document execution, secret, restricted source, or external upload.

## First hosted resolution

Run [45785147370](https://github.com/edithatogo/standards_check/actions/runs/45785147370)
resolved all four pins to 87 registry packages plus the local probe. The policy
step failed at an invalid placement of the cargo-deny --config argument; no
candidate code executed. The [retained archive 15100431282](https://github.com/edithatogo/standards_check/actions/runs/45785147370/artifacts/15100431282)
was downloaded and SHA-256 verified as dcc2010535ea870cb274ed83dc4aea23363f65f6e872f9d07ac09936abb0dfd7.
The exact generated lock digest is 20f995abbc9e34022e94d4dbd8f85183df6dcb29ad301feaece676a63b52ed92.
Retain that byte-identical candidate lock, explicitly copy the existing deny
policy alongside the scratch manifest, and run the same pinned policy action
with its common locked arguments. The probe's own licence follows the workspace
licence. No change to the root graph or policy. Still held pending policy and
actual offline compilation/tests.

## Import repair and receiving-main reconciliation

Original run 45785734826 passed candidate cargo-deny advisories, bans, licences and sources; Rust test compilation failed with two E0425 missing acceptor and two E0423 compose module/function errors. Use the pinned 1.3.1 API imports [compose](https://docs.rs/rustfst/1.3.1/rustfst/algorithms/compose/fn.compose.html) and [acceptor](https://docs.rs/rustfst/1.3.1/rustfst/utils/fn.acceptor.html). Preserve original tests and exact candidate lock; no new dependencies or change to policy. Reconcile E9/E11 receiving main 776ed1db, with disjoint changes. No successful parser/WFST test claim until actual fresh hosted compilation and execution. #180's source candidate copy requires later reconciliation.
