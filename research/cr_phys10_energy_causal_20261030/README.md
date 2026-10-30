# CR PHYS10 | Causal initial photoelectron energy (100 K frozen H/He RR source)

Physical data: 2,231 source-derived rows, exact original PHYS09 full source SHA-256 guard.

## Reproduce

The Git-only checkout does **not** include the original binary archive. Download the complete exact `BASS_CR_PHYS10...SOURCE.zip` from the separately verified backup. In an extracted complete source package run:

```bash
bash REPRODUCE.sh
```

A Git-only run requires the pristine 6,671,808-byte `BASS_CR_PHYS09_NEUTRAL_RESPONSE_SOURCE_20261030.zip` and:

```bash
python phys10_energy.py --source-zip /absolute/path/to/BASS_CR_PHYS09_NEUTRAL_RESPONSE_SOURCE_20261030.zip --out /tmp/phys10_outputs
```

`phys10_energy.py` verifies PHYS09 and nested PHYS08/PHYS07 byte identities before reading original spectrum/opacity; no fabricated or spliced physical input. `test_phys10.py` checks 20 original-source and physics cases, `compare_parent.py` checks original PHYS09 numeric response identity.

## Claim gate

Central DAG **28/88**, extension **0/3**, PHYS10 auxiliary science-data **1/1 REVIEW_HOLD**. Real independent-author R06/C09 absent, native subagent NOT_RUN, physical K/exclusive He double-event/common evolving neutral history/source-common radiation-owner unbound; no L4, native25, merge or production.
