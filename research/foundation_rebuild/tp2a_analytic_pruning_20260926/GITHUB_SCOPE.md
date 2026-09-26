# GitHub sidecar scope

This branch carries the exact validated analytic-pruning source, tests, symbolic
derivations, reports, and the original source manifest.

The heavy z=0 binary fixtures are intentionally **not committed through the
connector** because this delivery surface has no direct binary-file upload seam.
Do not replace them with re-encoded approximations.

To run the heavy 18-channel z=0 qualifier from a checkout, restore
`inputs/z0/` from the durable handoff package:

- package: `BASS_TP2A_ANALYTIC_PRUNING_20260926.zip`
- package SHA-256: `c732f809ba0edd6d5104e47723147941737d3386802dd90d347bb5dd19b28aa0`
- basis NPZ SHA-256: `172303585e254e6ad3ea7543fe0c1e695bd9364dc60040fad49c99b06ee84abe`

The original `SOURCE_MANIFEST.json` remains unchanged and therefore fails
closed until those exact fixtures are restored. This is intentional.

User-local confirmation of the standalone package on 2026-09-27:

- status: `ANALYTIC_Z0_QUALIFICATION_PASS`
- RETURN_REPORT SHA-256:
  `5fc2277f088971afe3e13d279c39e23bed428ecfc7b524869c2013801ee72393`
- RETURN ZIP SHA-256:
  `d5fb784dabf0366f83fe8b745058daf202b5cf70f0b553a938a62a88339393bd`

This sidecar is not yet integrated into the HP/full-geometry qualification
pipeline. It does not authorize capture, production, all-bound, or b-grid work.
