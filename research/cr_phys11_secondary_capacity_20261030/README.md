# BASS-CR PHYS11 | Energy-only upper capacity for secondary H I ionization

**Physics scope:** original frozen 100 K H/He RR source, 6,400 original photon-energy atoms, four original proper-time birth bins, original Verner photoionization fits. Primary first absorption source and proper-time convention preserved from PHYS10/PR135 exact SHA-256 `faf883bec9aa8852792856c170bcf4974b7b95c40c611790e23d6afb11197033`.

New source-dependent physics: initial photoelectron energy eligibility for an **additional** e+H I -> H II+2e^- event; exact energy-only capacity bound, not actual secondary ionization probability, cross section, or rate. Within the **cold-target/source-frame single-primary isolated energy-budget approximation**, direct helium double photoionization and additional He I ionization are impossible on this original photon support; at most one additional H I ionization is energetically allowed for a subset of He-origin photons first absorbed by H I. Ambient target motion, stochastic thermal tails, and non-source external field work are not included in the strict energy-only bound.

## Data
- 12,800 source-energy atom × first-target support records, 2,389 H-eligible He-origin -> H I energy atoms
- 108 time/source/absorber physical capacities
- 27 time/source-birth totals
- 1,728 windowed causal derivatives of the energy-selected capacity
- 184 final source-energy-bin contrasts
- 14,847 total new data rows (not 14,847 independent experiments).

## Reproduce
Use the complete source-inclusive ZIP; Git text-only checkout does not contain the original parent binary ZIP.

```bash
bash REPRODUCE.sh
```

Python 3 with numpy; current tests also use the standard-library `unittest`. No cosmological integration or heating. Source archive hierarchy is byte-locked; no recombination/source-owner files are rewritten.

## Gate
Central DAG **28/88 +0**, extension **0/3 +0**, PHYS11 auxiliary **1/1 CONDITIONAL/HOLD**. Distinct-author R06/C09 NOT_RUN. Existing PHYS08 PR133 remains partial Git 11/43; PR134/PR135 and main unchanged. Production, merger, native25/L4 all HOLD. `AUTO_NEXT_NODE=false`.
