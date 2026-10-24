# N5 mechanical publication preparation

These stdlib helpers perform no scientific calculation or remote mutation. Actual status is root-owned. Requested worker model: `gpt-6.1-sol`; observed runtime model: `UNOBSERVED`.

## Actual central patch

Supply a complete resolved return JSON, either directly or as `{ "return": { ... } }`. The required science commit/tree, GitHub PR, run/results/raw identities, measured result/check/review fields, three measured budget fields and execution/DAG axes must be actual. Set `draft:false`, `publishable:true` and remove `draft_reason`. `documents_commit:null` is permitted with an explicitly pending PUBLICATION axis; null backup receipts require an explicitly pending BACKUP axis. The helper does not derive numerical results or budget values.

Fresh exact DAG and handoff bytes and the expected central SHA must come from the same root-observed publication base. The expected SHA is recorded, not independently queried by this filesystem-only helper. The output directory must not exist.

```bash
python publication_prep/prepare_central.py \
  --status ACTUAL_STATUS_INITIAL.json \
  --dag FRESH_DAG.json \
  --handoff FRESH_HANDOFF_bass_cr_KO.md \
  --expected-sha ACTUAL_40_HEX_CENTRAL_SHA \
  --variant initial --variant-id n5_initial_20261024_v1 \
  --out publication_prep/central_initial_20261024_v1 \
  > publication_prep/PRESERVATION_INITIAL_20261024_v1.json
```

It emits only `DAG.json`, `HANDOFF_bass_cr_KO.md`, and `returns/CR_N5_PROVIDER_RATE_SEMANTICS_AND_CE_ENVELOPE_20261024.json`. Stdout is the minimal preservation receipt. Use unique receipt paths and shell noclobber (`set -C`) when redirecting stdout.

An initial invocation deduplicates an existing exact same-child entry only when the full entry matches. A final invocation requires the existing owned return and matching science identity in the current DAG. It permits changes only to `documents_commit`, `publication`, `backup`, `delivery_receipts`, and the PUBLICATION/BACKUP axes. `central_base` naturally follows the fresh root-supplied expected SHA. Budget values remain unchanged. Other owner progress, all 40 contracts, all 39 other wrappers, 7 authorities, and integration including 17 edges are preserved. Each handoff variant appends a section to the complete supplied handoff prefix.

```bash
python publication_prep/prepare_central.py \
  --status ACTUAL_STATUS_FINAL.json \
  --existing-return ACTUAL_EXISTING_CHILD_RETURN.json \
  --dag FRESH_FINAL_DAG.json \
  --handoff FRESH_FINAL_HANDOFF_bass_cr_KO.md \
  --expected-sha ACTUAL_40_HEX_CENTRAL_SHA \
  --variant final --variant-id n5_final_20261024_v1 \
  --out publication_prep/central_final_20261024_v1 \
  > publication_prep/PRESERVATION_FINAL_20261024_v1.json
```

## Canonical recovery ZIP and independent readback

Use distinct explicit initial/final variants. Payload files are read from the specified unit plus each explicit receipt mapping. Archive names are POSIX paths. Omit the archive's own build/readback receipt from its payload: those receipts are produced after bytes are fixed and should stay separate. The source unit must be stable during a build. Output ZIP is create-only; excluded path components are `__pycache__` and `mpl_cache`, and excluded suffix is `.pyc`. ZIP timestamps/modes and ordering are deterministic. Every payload has bytes/SHA256 in `MANIFEST.json`.

```bash
python publication_prep/canonical_zip.py build \
  --unit work/bass_cr/research/cr_n5_rate_semantics_20261024 \
  --variant initial --variant-id n5_initial_20261024_v1 \
  --receipt receipts/SCIENCE_PUBLICATION.json=ACTUAL_SCIENCE_PUBLICATION.json \
  --receipt receipts/CENTRAL_PUBLICATION.json=ACTUAL_CENTRAL_PUBLICATION.json \
  --out publication_prep/N5_CANONICAL_INITIAL_20261024_v1.zip \
  > publication_prep/ZIP_BUILD_INITIAL_20261024_v1.json
```

After root downloads that same archive independently from the delivery provider:

```bash
python publication_prep/canonical_zip.py verify \
  --zip ACTUAL_INDEPENDENTLY_DOWNLOADED.zip \
  --expected-json publication_prep/ZIP_BUILD_INITIAL_20261024_v1.json \
  > publication_prep/ZIP_READBACK_INITIAL_20261024_v1.json
```

Verification requires exact archive size and SHA256, checks all ZIP CRCs, exact manifest/payload set equality, every payload size/SHA256 and exclusion rules. The helper cannot establish remote provenance; root owns the independent-download attribution. `verify` produces stdout only. Use `--variant final`, a distinct variant ID/output path, and explicit final receipts for the final archive.

## Observed format-only verification

`SYNTHETIC_FORMAT_CHECK_v2/SELFCHECK_RECEIPT.json` records synthetic initial/final preservation, wrong-science rejection, a two-payload ZIP roundtrip, cache exclusions and corrupted-ZIP rejection. This is not science evidence or a remote-download receipt. All synthetic fixture and proposal paths are explicitly tagged.

`SELFCHECK_V2_PROCESS_TIME.json` records actual additive preparation cost: 0.203897 user CPU s + 0.041927 system CPU s = 0.245824 CPU s; wall 0.245527951 s. Inside that total, spawned helper CPU was 0.213982 s. Do not sum the nested helper subtotal twice. A first fixture attempt rejected a synthetic-tagged required identity; its cost is unmeasured. A subsequent `/usr/bin/time` attempt found that binary absent and launched no helper. Both events remain recorded. Existing scientific budgets were not edited or reset.
