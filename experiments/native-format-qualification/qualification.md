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
