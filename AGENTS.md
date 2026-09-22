# BASS_CR project harness

## Selective remote verification (owner policy, 2026-09-22)

Apply [.codex/readback-policy.json](.codex/readback-policy.json) and
[docs/READBACK_POLICY.md](docs/READBACK_POLICY.md) to all future project work,
including GitHub publication, Drive/Dropbox backup, handoffs and large artifacts.
These are project instructions for every agent and worktree, not global CUH-G
routing settings. Default: selective / R1. Do not fetch remote file bodies after
ordinary writes when provider success, remote identity and available integrity
metadata establish the mutation. Record the tier actually achieved.

R3 is required for the listed release, overwrite, recovery, trust/authority change,
inconsistent provenance and explicit-user-request conditions. Missing optional
provider SHA256 alone is not a reason to download. Do not label metadata-only
verification as raw readback. Keep local artifact sources until receipts exist.

This policy supersedes blanket post-write raw-readback requirements in older
project handoff documents for future operations. Preserve archived results,
receipts, manifests and their historical meanings; do not retrospectively promote
an incomplete backup. A changed source digest does not migrate old checkpoints.

The legacy `scripts/r3m11_dual_backup.py` always performs raw readback and does not
load this configuration: use it only for R3 with a recorded trigger/explicit
opt-in. For R1/R2 use the metadata workflow in docs/READBACK_POLICY.md. Do not invoke
the legacy script as the default upload path. These rules are agent-harness
instructions, not a shell-wide interception of manually executed commands.

Keep b-grid NO_GO and existing scientific claim ceilings. Verification policy
changes do not authorize new physics runs, 50/225 keV/u, integrated cross sections,
physical rates, main-branch merges or changes to global runtime policy.
