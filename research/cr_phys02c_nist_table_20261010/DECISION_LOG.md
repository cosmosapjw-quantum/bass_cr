# Decisions

- Freeze a new source-table component before execution, rather than change old
  EMAX or import unpinned upstream HDF5 data. Both would exceed this unit.
- Use the literal NIST excitation energies (HI 10.204 eV, HeI 21.218 eV).
  Neither the old effective 23s energy nor a different Rydberg convention is
  silently substituted. Transition IDs remain explicit in every result.
- Linear E/sigma interpolation is declared numerical behavior; its agreement
  with the underlying continuous physics remains unmeasured.
- First validation PASS_SCOPED does not imply independent review, physical-model
  adoption, kernel permission, recovery or publication. Those remain separate.
- Next action: one parent-owned independent review; no second validation campaign
  without a substantive changed-code finding.
