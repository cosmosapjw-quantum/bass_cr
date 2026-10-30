# BASS_CR PHYS16 | conditional 2p-emitter recoil and one HI resonant scatter

**Research only.** Original source-owned H/He RR 6400 atoms -> first H photoionization -> source-qualified primary electron H 1s->2p excitation -> Lyα spontaneous photons -> spectrally integrated **first** HI resonant scattering, with an explicitly conditional plane-wave Born DCS / E1 angular closure. A separate static-HI one-scattering redistribution kernel is calculated but **not yet fed back into a multiple-scattering or cosmological radiation equation**.

Status: source parent immutable; `central DAG 28/88 (+0)`, `extension DAG 0/3 (+0)`, scoped PHYS16 auxiliary `1/1 CONDITIONAL_REVIEW_HOLD`, `R06/C09 true distinct-author NOT_RUN`, no full physical K, no source-owner evolving gas-radiation geometry, no global He exclusive kernel. Production/NATIVE25/L4 HOLD. Draft only; no merge or force push.

`bash REPRODUCE.sh` reruns actual 6,400-source-photon and 2,066-qualified-event spectral work in a separate temporary directory; two 35-test suites; 3 science figures; numerical output SHA-256 comparisons. Use `python verify_archive.py FULL_SOURCE.zip` to inspect source-inclusive manifest. This package intentionally includes original PHYS15 source binary: checking out Git alone without the archive is insufficient to reproduce native historical dependencies.

Key files: `THEORY_KO.md` formalism; `REPORT_KO.md` physical outcomes; `LITERATURE.md` primary papers and next missing DCS; `BLIND_REFEREE_EVIDENCE.json` same-author adversarial findings; `HANDOFF_NEXT_THREAD_KO.md` exact next-step state; `stages/R01..R10.json` and `stages/C01..C10.json` stage evidence. These 20 stage records describe **one** physical computation and one review pass, not 20 independent computations.
