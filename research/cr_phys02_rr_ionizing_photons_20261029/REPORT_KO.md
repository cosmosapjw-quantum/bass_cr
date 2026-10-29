# BASS-CR 물리 광자 source 생성: PR110 frozen-Coulomb/RR 파생 관측량

**Unit:** `CR_PHYS02_RR_IONIZING_PHOTON_V1`. **Parent:** Draft PR124 `a6b49b352fed31587955d55b1cad30c0b55a81eb`. Source branch: PR110 actual scientific data and original `5,421,103`-byte immutable ZIP (SHA256 `5392bc1bf159d0b23d7530a541f894e201231c3df874d6c547474b7517654c58`). This is an independent add-only branch, not a merge or modification of PR110/124/main.

## Summary of actual physical-data output

Use original source-qualified 100 K H1/He4 direct 0.1–10 eV electron cohort, proper t∈[0,10^10]s, actual 3200-atom RR capture event weights for H II→H I(1s) and He II→He I(1s² singlet). Convert original finite events to explicit channel- and time-resolved retained photon energy and frequency source. This calculates **new derived physical emission products** from original physics; it does not perform a new RR solve or invent new cross sections or a physical exclusive-He double-event kernel.

Total Nγ=2.7294411246106446e-25 m⁻³, total retained Uγ=7.591430348411315e-43 J m⁻³. H: Nγ=2.4949449643820725e-25m⁻³, Uγ=6.550324148959684e-43Jm⁻³; He: Nγ=2.3449616022857224e-26m⁻³, Uγ=1.0411061994516318e-43Jm⁻³. Energy-eligibility counts: above H I threshold all 2.7294411246106446e-25/m³; above He I threshold 2.3449616022857227e-26/m³ (8.591361730215857%); above He II threshold 0. These are potential photoionizing photons *if* suitable absorber/optical depth is supplied; actual ionizations are unknown.

Discrete four proper-time bins [0,2.5e9], [2.5e9,5e9], [5e9,7.5e9], [7.5e9,1e10] seconds have H event number densities 4.6363591070009445e-27, 2.991076865408379e-26, 7.576943431724697e-26, 1.3917793435987553e-25 /m³; He 4.311855551774776e-28, 2.7977571477112684e-27, 7.115262892656268e-27, 1.310541042731221e-26 /m³. Exported `PHOTON_SPECTRUM.csv` has 368 rows = 46 energy bins×4 time bins×2 channels with eV/frequency edges, event N, photon U, bin-mean rate and density. `PHOTON_ATOMWISE.npz` holds original 3200×4×2 event weights plus emitted energy/frequency positions, avoiding loss of original spectral resolution.

As separate signed first-order formal slab diagnostic, the monotone cumulative-capture bracket is δτ_T ∈ [−2.1760852212695975e−35, −8.152152542331533e−36] over the same proper T, baseline frozen τ0=3.022299437152936e−10. **Not** a cosmological visibility/Thomson-τ completion or a self-consistent plasma perturbation. No full-source native25, photon transfer, on-the-spot Case B, thermal feedback, radiation force or CMB likelihood is activated.

## Derivation, input authority, and validation

Mathematical definitions and limitations are in `THEORY_KO.md`, machine-readable `CONTRACT.json` and raw `results/PHOTON_RESULT.json`. Original PR110 source array and outcome SHA are checked, alongside source JSON and its *different* parent NPZ lineage SHA. The original 5.42MB ZIP is preserved unchanged inside this new package. Original stored source physics is not rerun. Full event-energy identities and 4 disjoint bins checked against original RESULT/ARRAYS.

New Python `unittest` 12/12 normal, 12/12 `python -O` PASS; independent self-contained Decimal80 original-atom sums 8/8 passed against original saved RESULT, and Wolfram symbolic residuals 0 for energy identity, time-average/units. Python plotting uses only saved derived outputs and visual QA, not inferred observational data. Original solver/reference prior validations remain inherited claims. Initial source JSON vs distinct NPZ lineage SHA comparison failed and was corrected without modifying source. Initial missing time-grid guard exposed by `test_reject_wrong_clock` failed, then repaired and targeted tests passed. These are distinct implementation failures, not source physics failures. Current whole aggregate CPU cap is not certified; do not recycle PR110's used/unused budget.

## DAG, review and publication scope

- Central original **28/88** delta0 (88 nodes/17 edges). Extension **0/3**. New scoped physical data auxiliary **1/1 implementation tested, reviewer HOLD**. This node supplies a useful photon-source export but **does not** qualify any existing original node as COMPLETE without owner/contract review.
- Selected new R/C workflow **18/20**: genuine distinct-author R06 and C09 both NOT_RUN because native subagent delegation unavailable. Same-context assertions, independent-algorithm Decimal80 and Wolfram are distinct methods, not a distinct-author reviewer.
- Physical exclusive He pair kernel/K, outside partner/donor energy, source total/full native25, photon absorption/deposition and production/L4 HOLD. Historical PR118 resource FAIL, aggregate CPU not certified, original PR124 draft, source & parent unchanged.

Source materials: BASS-CR PR109/PR110/PR112/PR124 fixed source and return receipts; Nebrin (2023) DOI 10.3847/2515-5172/acd37a; NIST CODATA 2022 constants. Related proton–He double-ionization primary research Ciappina et al. (2008) DOI 10.1103/PhysRevA.77.062706 is **6MeV**, not source-matched 1–4MeV exclusive joint K. This distinction prevents accidental promotion of a new physical kernel from incomplete literature.
