# C21C native cohort owner 재실행

## 범위

이 자료는 C21C의 세 번째 비교 lane인 `PreparedAbsorption` + native H/He
chemistry owner가 실제 NCP에서 실행 가능한지를 확인한 **재실행 영수증**이다.
실행 원본은 `rei_bianchi` PR #166 head
`553ce556d9f8662290c000ec675c7e6007c9d895`의
`research/rei_source_age_native_owner_bind_20261016/native_owner.rs`이다.
원본과 NCP materialization의 SHA-256은 모두
`086f99c3e8b51980bced16a4fb925216f0b5302dceddd6ff8b99998b635adf4a`로
byte-identical이다.

이 owner는 cohort 별 `PreparedAbsorption`을 같은 trial gas에 대해 평가하고,
그 Gamma/heat를 합산해 **한 번** native `igm_point_rhs(..., h=0, Tcmb=2.7255/a)`
로 전달한다. Newton residual <= 1e-11, absorption ledger 및 candidate-wide
number/energy gate <= 1e-10을 함께 만족해야 commit한다. geometry가 photon
redshift work와 gas adiabatic work를 단일 소유한다.

## 실행

`taskset -c 57 timeout 180s source_age_campaign OUT`을 실행했다. CPU 55는
사용하지 않았고, output은 create-only
`/root/BASS_CR_C21C_NATIVE_20261016_001/run_pr166_byte_matched`이다.
`checks.txt`의 11개 native regression은 PASS였다. elapsed 28.99 s, peak RSS
11,724 KiB, exit 0이다. `history.csv`에서 max absolute photon residual은
`8.131516293641283e-20 / H`, max absolute energy residual은
`7.396083745447868e-12 eV / H`이다.

## C21C 판정 경계

이 재실행은 PR77 exposure lane과의 공통-IC three-lane comparison이 아니다.
PR77은 `a=1/12`, nine-cohort manufactured three-energy photo-only FLRW Radau
reference이고, 이 replay는 PR166 MD14/signed-Bianchi native source run이다.
따라서 endpoint BE, physical-exposure integrated chemistry, PreparedAbsorption의
같은 입력 정량 비교와 exposure-integrated native chemistry는 **HOLD**이다.
특히 `Gamma_exposure=L/I_A`를 endpoint BE `igm_point_rhs`에 그대로 전달하지
않았고, endpoint absorber depletion에는 epsilon clipping이 허용되지 않는다.

PR166 자신의 source-matched DOP853 path도 internal negative photon trial로
HOLD이며 age refinement가 비단조적이다. 이 replay는 full EoR, global source-age
convergence, independent Radau equivalence를 주장하지 않는다.

## 다음 DAG

1. PR77 nine-cohort FLRW IC/source/GL2/Verner spectrum을 PR166 tagged-owner
   input adapter로 정확히 materialize한다.
2. 같은 proper-time mesh에서 endpoint BE와 `PreparedAbsorption`을 비교한다.
3. exposure event integral은 endpoint rate adapter와 분리한 integrated chemistry
   owner로 구현하고, endpoint depleted case는 explicit HOLD로 유지한다.
4. 각 accepted step에서 native Newton residual, photon/species/charge 및
   physical-reservoir energy ledger를 동시에 gate하고 rollback을 시험한다.
