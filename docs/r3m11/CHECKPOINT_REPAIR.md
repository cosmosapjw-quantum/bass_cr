# Completed checkpoint strides survive later interruptions

The controlled runner previously sealed state files only when an entire call
returned. Interrupting a later step left a completed checkpoint pair with a
missing or stale seal, so the next call rejected a usable restart.

Each completed checkpoint now invokes a save hook and records its seal before
the next step. The underlying TDL save order, propagation, config identity and
scientific thresholds are unchanged. Hash/source mismatches still fail closed.
An interruption *during* the state/metadata/seal write sequence can still leave
an incomplete checkpoint that must be rejected; this is not a transactional
multi-file storage format.

The regression interrupts a tiny CPU fixture after one saved stride, resumes
one step, and requires bit-identical state to two uninterrupted steps. This is
software restart validation, not a new physical convergence result. Existing
archived runs and the current active runner are not migrated by this patch.
