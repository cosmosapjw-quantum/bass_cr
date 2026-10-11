# PHYS02F publication assembly helper

This helper performs local preparation only. It has not frozen the unit, prepared Git payloads, built the final handoff, or made remote writes.

Run from the scratch root after root finishes science reports, NCP code and independent review:

```sh
python phys02f_publish_work/assemble.py freeze-unit-manifest
python phys02f_publish_work/assemble.py prepare-git
python phys02f_publish_work/assemble.py bundle SCIENCE_COMMIT_40 SCIENCE_TREE_40 --science-receipt ROOT_RECEIPT_PATH --readme ROOT_README_PATH
```

Global `--repo` and `--output` precede the subcommand if overriding defaults. `bundle --recovery PATH` overrides the actual PR35 family source directory. The root receipt must contain `science_commit` and `science_tree` (or `commit` and `tree`). No API call occurs here; root creates Git API blobs/tree/commit separately after review.

`freeze-unit-manifest` writes repository-relative path → bytes/SHA256 entries to the unit's FILE_MANIFEST.json. It omits itself, Python caches and publication files except READBACK_PLAN.json. Neither preparation nor bundling refreshes the manifest: changed bytes or membership fail. Freeze is a root action to be invoked only when the unit is final.

`prepare-git` writes under `phys02f_publish_work/git/`, refusing a nonempty output directory. UTF-8 groups contain no more than approximately 95000 encoded JSON bytes. Larger or binary files have separate base64 JSON payloads. GIT_TREE_ENTRIES.json maps every new-unit path to mode/type/Git blob SHA and payload file; it includes FILE_MANIFEST itself. It never emits edits for the 538 dependencies.

`bundle` verifies final unit membership and hashes, exactly 538 dependency identities (including existing Git blob SHA), two canonical harness archives, and the root science commit/tree receipt. The actual PR35 family envelope is deduplicated if the same size/SHA already occurs in the dependencies; BUNDLE_MANIFEST records its exact placement. Repository layout is preserved at archive root. README_NCP_KO.md and SCIENCE_COMMIT_RECEIPT.json are root-provided. The unused complete prior D failure archive is omitted. The bundle schema is `cr-phys02f-self-contained-bundle.v1`; the launcher must accept this F schema and reject inherited E bundle schemas.

The output is CR_PHYS02F_20261011_<science8>_HANDOFF.zip, deflate level 6, sorted entries and current timestamps. Every archived payload is verified against its manifest after writing; the entry list is checked exactly and duplicates fail. BUNDLE_MANIFEST hashes every payload except itself. BUNDLE_ASSEMBLY_RECEIPT.json stays outside the ZIP and records its size/SHA and verification result. Root performs the one clean archive restore/--plan gate afterward.

Path validation rejects absolute paths, traversal, backslashes, noncanonical path strings and repository source symlinks. Archive membership comes from the two manifests plus named extras, rather than recursively packaging the whole repository or current configuration.
