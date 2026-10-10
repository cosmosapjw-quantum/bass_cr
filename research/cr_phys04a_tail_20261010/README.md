# CR-PHYS04a: 4–10 MeV neutral-ionization tail ledger

This separately executed diagnostic reuses the CR-PHYS01 source and exact
constant-background Bianchi characteristics at 100 K, xi=.01, nH=140/m³,
Y=.248, z_source=8 and age 10¹⁰ s. It extends the *diagnosed Rudd neutral H/He
ionization channel* to 4–10 MeV; production `build_packet` retains its 1–4 MeV
domain. The production receiver is untouched.

For each target and proton band, the ledger records primary event rate,
primary binding cost, secondary kinetic energy, and their summed proton
ionization loss. It splits secondary energy at the existing FS10 maximum,
9937.21 eV. Both secondary partitions remain unallocated: no cascade, heat,
secondary ionization, or photon reinjection is computed here.

The final-proton edges are exactly 4e6, 4567804.2094395505,
4572846.425549054 and 1e7 eV. The two interior boundaries solve the H and He
Rudd endpoint crossing of 9937.21 eV. Each interval is passed separately to
`transport_population`, which maps its edges to birth energy before quadrature.
Full-source normalization is retained; the collision band is never renormalized.

## Observed validation

Run commands, with BLAS/OpenMP threads set to one:

```sh
python3 -B -m unittest discover -s research/cr_phys04a_tail_20261010/tests -p 'test_tail_ledger.py' -v
python3 -B research/cr_phys04a_tail_20261010/tail_ledger.py --validation --output research/cr_phys04a_tail_20261010/evidence/VALIDATION.json
```

The generated evidence path must be new; the CLI refuses to overwrite an
existing result. Choose another output path for reproduction.

Six focused tests pass: domain/positivity, partition and binding additivity,
zero-age/OFF, analytic moments versus direct SDCS integration, the frozen
48/8/8 → 64/12/12 refinement, and the unchanged production 1–4 MeV guard.

The raw unsplit failure is preserved alongside the repaired result in
`evidence/VALIDATION.json`. Its combined above-table secondary-energy change
is **3.295126107250752e-5**; the maximum over all target/band/moment channels is
**4.654547582321343e-5** (He above-table primary binding). The split result has
maximum relative change **4.975509450101899e-14**, passing the fixed **2e-6**
criterion. These are finite quadrature comparisons, not certified continuum
or physical-model uncertainty bounds.

The refined combined 4–10 MeV ionization loss is
6.857785204200995e-43 J m⁻³ s⁻¹. Its primary binding and secondary kinetic
parts are 1.5094806067500958e-43 and 5.348304597450901e-43 J m⁻³ s⁻¹.
Above-table secondary kinetic power is 2.124419913044426e-44 J m⁻³ s⁻¹,
or 0.039721371031428594 of the tail secondary kinetic power.

The final-node sampled loss-rate-times-age estimate is
2.6515820741121155e-7. This is neither a trajectory supremum nor a certified
thin-target bound. Coulomb losses, primary excitation, HeII collisions,
other proton energies, secondary time delay, and collision feedback remain
unmodelled. Solver intervals executed: **0**. Full CR history remains HOLD.

Independent review and publication are delegated to the parent worker after
this implementation handoff; neither is claimed by these local tests.
