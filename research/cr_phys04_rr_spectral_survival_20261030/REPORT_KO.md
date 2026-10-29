# BASS-CR PHYS04 | Source-locked surviving photon spectra (2026-10-30)

## 목표 및 현황

실제 PR125의 H/He ground-state radiative recombination photon event measure(3200 energies × 4 source birth-time bins × 2 photon channels)를 PR127의 원래 Verner1996 H I/He I photionization opacity로 조건부 전파한다. PR128의 누적 9-time photon/electron 결과와 일치시키고, **아직 생성되지 않았던 1 eV 광자 에너지별 생존 광자 스펙트럼과 target별 첫 흡수 스펙트럼**을 생성한다. 외부 BASS21/REI photon bath와 혼합하지 않는다.

## 고정 상태

- Parent PR128: `df3324b1319293a25a26e22f69b9b0eccd23b6dd`; `OPEN/DRAFT/UNMERGED` at intake.
- Parent SOURCE ZIP 5,920,585 bytes, SHA256 `a6062e5fa54c51983439e256ffd521f7b25d151952293e0fad7c2b3064ff4819`.
- Nested PR125 SOURCE SHA256 `8e9b58236819146f4929aa4647dafdb1dc21b97b2f129ec4035291bb73a1ed2e` and original photon NPZ SHA256 `e171824cf5fc3ba232fbbd4def6fc8cf6c855ca9e7d05506e4e4426c9416688f`.
- Original PR127 Verner module SHA256 `2db17652571465cd2e5f5fde51f60be01fd6d3ae2b11b193addc98dd047f9594`, original Table 1 SHA256 `a9ae2f7e7393de6f9ad89376cf5dd4be84da60cb3dadde3be37a4d3bd5989492`.
- Frozen 100 K gas: n_HI=138.6 m^-3, n_HeI=11.427127659574467 m^-3. Proper time t in 0..1e10 s. Event-weight [m^-3], E [eV], photon energy density [J/m^3]. Photon speed physical c=299792458 m/s. No cosmic redshift, no scattering, no secondary electrons, no heat deposition or chemistry feedback.

## 새 연구 결과

Fixed 23 photon-energy bins `[13,14),...,[35,36)` eV, 9 observation times and both original source channels. Every time-energy row is derived from **every original atom** without bin-centre approximation in opacity evaluation. Source bin birth-time uncertainty is kept as a sharp *pointwise* envelope.

- `SURVIVING_PHOTON_ENERGY.csv`: 414 rows (9 times × 2 birth-photon source channels × 23 photon-energy bins), number and photon-energy lower/upper; unborn and absorbed complements.
- `ABSORBED_PHOTON_ENERGY.csv`: 828 rows (× HI and HeI first-absorber), energy partition between target ionization threshold and primary electron excess kinetic energy. No thermalization assumed.
- `TIME_TOTAL.csv`: 9 rows, exact comparison to PR128's total absorption and survival bounds.
- `JOINT_WITNESS_LEDGERS.csv`: 54 rows (9 times × 2 source channels × 3 explicitly realizable birth-time witnesses), each with photon-number/energy conservation. Do not confuse independent pointwise extrema with one joint physical history.

At T=10^10 s:

| quantity | lower | upper | units |
|---|---:|---:|---|
| surviving photon count | 2.5575019879501597e-25 | 2.664075525362283e-25 | m^-3 |
| surviving photon energy | 7.1509468195262445e-43 | 7.424411457346008e-43 | J m^-3 |
| first photon absorption count | 6.536559924836173e-27 | 1.719391366604854e-26 | m^-3 |
| H I target count | 6.462553503537656e-27 | 1.6996986246313593e-26 | m^-3 |
| He I target count | 7.400642129851676e-29 | 1.9692741973494655e-28 | m^-3 |
| absorbed photon energy | 1.6701889106530612e-44 | 4.4048352888507267e-44 | J m^-3 |

Initial source photon number = `2.7294411246106446e-25 m^-3`, source photon energy = `7.591430348411317e-43 J m^-3`. Final source count and energy are preserved by the opposite bound pairing: `N_survive^-(T)+N_absorb^+(T)=N_source` and `N_survive^+(T)+N_absorb^-(T)=N_source`, similarly for photon energy. This complement is guaranteed **only after all four birth bins have ended**.

The source-H photon channel to HeI absorber is strictly zero by source energy threshold, not a fitted numerical cutoff. At an observation time strictly inside a birth bin, survivor upper requires a witness birth at `s=T`; using only bin endpoint births would be wrong. It is an internally valid sharp envelope under unresolved birth-time freedom, not an actual resolved emission history.

## 재현과 출처 검산

`bash REPRODUCE.sh` (source ZIP included) returned exit 0 in authoring worktree. Python unittest 13/13 normal and 13/13 `-O` PASS; compileall PASS; 64 original atom/source-bin MP80 controls, worst relative sigma `2.574185945666324e-15`, survival `4.521742341987451e-16`, absorber `2.592719913672951e-15`. Frozen PR128 original 9 cumulative bounds separately matched within 6e-13 relative; negative SHA corruption test rejects modified source. Wolfram symbolic derivative and conditional unity evaluated (positive survivor ds, negative target first absorption ds, partition unity). **All tests performed within the same authoring context**, so R6 independent theory and C9 different-author code review remain `NOT_RUN`.

## 문헌 근거

- Verner et al., 1996, ApJ 465:487, DOI 10.1086/177435. Original Table source: https://www.pa.uky.edu/~verner/photo.html; original fit and coefficients kept byte exact.
- Switzer & Hirata, PRD 77:083006 (2008), DOI 10.1103/PhysRevD.77.083006, demonstrates cosmological He I transfer needs time-varying H I continuum opacity and line transfer. We do **not** claim to reproduce that full calculation.
- Chluba, Fung & Switzer, 2012, DOI 10.1111/j.1365-2966.2012.21110.x, illustrates additional time-dependent transfer requirements, absent here.

## Cross-repo intake (read-only)

Latest observed: `bass` PR262 CE1-S bolometric Bianchi-I sky; `rei_bianchi` PR274 off-manifold Li forcing (its separate CI/compatibility not promoted); `vigilode` PR121 original 193 epoch; `BASS_HE` PR116; `rec_bianchi` PR162; `WU088_HH` PR166. These are independent source contracts, not a unified photon history. In particular PR125 finite-time 100 K RR source is not a replacement for BASS21 native photons, Puchwein2019 UVB or Bianchi-I anisotropic transfer. No actual cross-repo physics was silently stitched.

## DAG 및 다음 단계

CENTRAL DAG **28/88 unchanged**, EXTENSION **0/3 unchanged**, new scoped auxiliary **1/1 physical data generated / R6+C9 REVIEW HOLD**. Source-owner physical K, exclusive He double-event kernel, source-consistent evolving neutral H/He, true photon angular field and cosmological redshift/transport, donor/partner bookkeeping and stopping are missing. `native25=L4=production=HOLD`; PR128 and other existing PRs remain Draft/unmerged and unchanged.

Next science candidate only after owner contracts: bind evolving HI/HeI density histories and a common clock + directional photon redshift to solve real radiative transfer. A different-author review of the new theorem's birth-time admissibility and implementation/output round-trip is still required before formal merge.

Publishing records for stages are retrospective checkpoints, not per-stage contemporaneous science executions. Separate `R06/C09` NOT_RUN and preserve failed historical PR118 resource run, unknown aggregate CPU billing and no production claims.
