# Analytical projection reconciliation (#151)

This branch supersedes the alternative PyArrow exporter with the existing Polars
canonical and directory projections from main. The previous branch commits and
review findings remain in history. Keep the pinned test dependency and lock
closure; do not add a second Parquet runtime or overwrite the established schemas.

The useful additional safeguard from #151 is now enforced in the existing
projector: pack-level and effective item rights must both be cleared and the
pack must be source-reconciled or externally validated before section text,
verbatim text, normalized requirements, guidance or evidence expectations are
exported. Held rows retain their identities, source anchors and hashes. The
table validator rejects attempted prose injection even after projection.

The former numeric source-index release-label failure was specific to the
removed duplicate Arrow source-index projection; this change does not claim
to have added that table. If a curated-index projection is required by a
consumer, normalize schema-valid numeric edition labels to text in the
existing projection lane, with a dedicated regression. Canonical pack edition
labels remain schema-validated strings. Preserve #149 open for remaining
consumer qualification, byte-level receipt and output-path safeguards.
No new rights admission, source repin, semantic qualification or schema
migration follows from this change.
