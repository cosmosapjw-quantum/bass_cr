# Project readback policy

Owner instruction, effective 2026-09-22. Machine-readable policy:
[../.codex/readback-policy.json](../.codex/readback-policy.json).

| Tier | Evidence | Use |
| --- | --- | --- |
| R0 | Provider success | Explicitly temporary / low-risk operations |
| R1 | Provider success, remote ID/ref, available size/hash metadata | Ordinary default |
| R2 | API/remote metadata and manifest cross-check | Canonical checkpoint |
| R3 | Actual content download/readback and byte/hash verification | Release, recovery, audit |

Select the tier before mutation. R3 triggers override the default: canonical
release; destructive/overwrite mutation; restore/recovery; runtime interruption
recovery; provider checksum/size mismatch; provenance conflict; authority change;
external/untrusted import; or explicit user request. Crossing a trust boundary
also requires R3. Record the trigger. A normal fast-forward branch push by itself
is an ordinary R1 operation, not a destructive overwrite. A sealed checkpoint
requires R2 unless a separate R3 trigger applies. Audits explicitly requesting
content verification use R3. Scope readback to affected objects.

`manual_override.enable_readback: true` means an explicit per-operation opt-in is
available; it does not enable downloads for every operation. Large-artifact
`download_for_verification: false` is a default, not an exemption from R3.

## GitHub

Retain the push success/exit receipt, expected local commit SHA, destination ref,
and `git ls-remote` result for that exact ref. Require the expected and observed
commit SHA to match. Tree SHA is optional. Stop at R1 on agreement; do not fetch
raw files or clone merely to confirm a normal push. A mismatch is unresolved
provenance and escalates to investigation/R3, never an automatic force push.

## Drive / Dropbox and other artifacts

Retain local source, local SHA256/size, provider success receipt and remote object
ID. Obtain remote size/hash from provider metadata when available. Compare only
like algorithms: DropboxHash and MD5 are not SHA256. An absent provider SHA256 is
`UNAVAILABLE`, not a locally computed value attributed to the provider. Missing
remote identity or provider success leaves the operation unverified; resolve
metadata first. Report available size/hash mismatches and escalate to R3; a
successful readback does not erase an inconsistent provider receipt.

For existing authorized raw rclone remotes, the R1 workflow is immutable upload
(`rclone copyto --immutable SOURCE REMOTE_OBJECT`) followed by metadata only
(`rclone lsjson --stat --hash REMOTE_OBJECT`). Retain exit codes and JSON, require
a non-directory object with a provider ID, compare available size and matching
hash algorithms. Use provider API metadata if rclone omits the object ID. Never
substitute a synchronized local path for a remote object. No default `rclone cat`,
download, or `rclone check --download`. For R2 additionally compare the manifest's
object membership, identities, sizes and available hashes with remote metadata;
do not download the payload to do that comparison.

A dual backup succeeds only when both independent providers satisfy the selected
tier. Record per-provider success/failure separately. Receipts include the actual
tier, reason, provider receipt, remote ID/ref, available integrity metadata, and
whether content readback occurred. R1/R2 success is not R3 byte-readback success.
Do not delete the local source before receipts are secured; retention beyond that
point follows the existing task's archival requirements, not automatic cleanup.

## Existing entrypoints and historical evidence

`scripts/r3m11_dual_backup.py` is a legacy R3-only entrypoint: it always streams
both remote objects and does not consume the JSON policy. Invoke it only when a
recorded R3 trigger or explicit readback override applies. All agent-driven R1/R2
uploads must use the metadata workflow above. No automatic process-wide command
interceptor is installed by this policy.

Older instructions in `docs/r3m11/START_CODEX_HANDOFF_PROMPT.md` and
`docs/r3m11/REPORT_KO.md` describe the previous mandatory-readback workflow. This
policy governs future operations; retain those historical documents and receipts
unchanged. It does not resolve the previously pending Drive archive backup or
alter scientific NO_GO, checkpoint source binding, or archived checksums.
