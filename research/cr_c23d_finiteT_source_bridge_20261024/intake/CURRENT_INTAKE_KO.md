# 다음 stopping 연구를 위한 현재 intake

## 판정

**현재 scope의 읽기 전용 intake: COMPLETE_SCOPED.** 다음 연구는 기존 Maxwell-bath/비선형 Landau 결과를 재사용하는 **C23B source → 명시한 bath/기존 EE operator 결속**으로 진행할 수 있다. PR59에는 유한 온도 diffusion과 moving-interface 에너지 장부가 이미 구현돼 있다. 이를 새로운 최초 유도로 세지 않는다.

이번 조사에서는 과학 실행·ODE·기존 계산 replay·archive 다운로드·원격 변경을 수행하지 않았다. 최신 ref/PR와 선택 원문을 조사했다.

## 최신 authority 및 조사 범위

- bass_cr PR98: `research/cr-c23c-cutoff-binding-20261023` → `ec0c2cb8cc9feae64fe028ca2a4ea0eb7d79c8f8`.
- 중앙 rei_bianchi PR222: `research/orchestration-sandbox-20261022` → `68420637a9ab54ada92afd786c5733bc0764b8c9`.
- 고정 사용자 인계 `0f9d9df825be1dac9ca9bdf73cdc2e8908bcba17`는 역사적 원 계약이다. 현재 중앙 handoff에는 named C23C 소비자 수신 완료 overlay가 있다.
- 관측 구간: 2026-10-23T21:57:23.122Z — 2026-10-23T21:57:27.747Z.
- 이전 완전한 7-repo inventory는 2026-10-23T14:41:49.568Z의 1294 heads. 이번 1301: **+7 added / 4 changed / 0 removed**. 별도로 더 늦은 narrow intake의 bass_cr E→F와 중앙 0f9→M은 이미 완료된 게시의 차이다.
- Git wire `git ls-remote`는 browser-proxy 연결 실패(exit 128)였다. 지원되는 GitHub REST `branches`를 repo별 per_page=100으로 끝까지 페이지 처리했다. 따라서 이번 결과는 **REST 전체 visible branch refs**, 성공한 git-wire advertisement라는 주장이 아니다.
- 모든 열린 PR metadata도 repo별 페이지 처리했다. 전 페이지에서 branch name / PR number 중복이 없는지 로컬로 확인했다. 계정 전체의 미지정 저장소나 닫힌 모든 PR, 모든 commit/body를 조사했다는 주장은 하지 않는다.

| Repo | Branch refs | Branch pages | Open PRs | PR pages |
|---|---:|---:|---:|---:|
| bass_cr | 176 | 2 | 97 | 1 |
| bass | 269 | 3 | 154 | 2 |
| rei_bianchi | 263 | 3 | 207 | 3 |
| BASS_HE | 97 | 1 | 92 | 1 |
| WU088_HH | 150 | 2 | 141 | 2 |
| rec_bianchi | 148 | 2 | 96 | 1 |
| vigilode | 198 | 2 | 51 | 1 |
| 합계 | 1301 | 15 | 838 | 11 |

모든 마지막 페이지는 100개 미만이었다. `raw/ALL_BRANCH_PAGES.json`에는 15개 branch 응답 본문이 있고, `OPEN_PR_INVENTORY.json`은 11개 PR 페이지의 URL/시각과 원 응답에서 선택한 metadata 필드를 보존한다. PR API의 사용하지 않은 전체 transport envelope를 저장했다는 주장은 하지 않는다. 중요한 변경 PR 11개와 기존 Coulomb PR58–64의 실제 본문은 `selected_prs/`에 따로 보존했다.

## 이번 delta와 병렬 소유권

| Repo | 중요한 새/변경 ref 및 근거 | 현재 stopping 작업에 대한 의미 |
|---|---|---|
| bass_cr | PR98/F가 14:41의 7-repo baseline 이후 추가. 다른 bass_cr ref 변경 0 | 기존 PR59–64 완료 결과가 현재 F의 역사에도 존재한다. 새 warm-operator 최초 구현을 반복할 필요가 없다. |
| bass | PR184 G1B → `28b7705cbb236c26e1b273335f6da7e9da4d1aaf` | smooth collisionless FD/Planck 및 massless radial reduction 결과. collision/heat closure에 자동 이식하지 않는다. |
| rei_bianchi | PR222/M; PR221 → `8d10231b1f0f788164d5eadbe1bcee0b802cceca` | 중앙 N4 수신 완료와 prescribed-background angular thermochemistry. source/model/oracle tolerance의 소유권을 분리한다. |
| BASS_HE | PR92 HE-ANG → `0a11bf9e1f6ffcc696625de0caf1c581c27cf7f0` | 계약/controls COMPLETE_SCOPED, 실제 empirical source는 SOURCE_INPUT_PENDING. EE stopping rate 공급자로 승격하지 않는다. |
| WU088_HH | PR140 completion → `6a2fc5aacb6182a916b9434c316e99e750e8273c`; PR141 source adapter → `3c04b6eecd6d1f425e8b6aa5d54b81ec56ffe173` | PHYS83 완료와 PHYS84 소유자가 존재한다. N5의 excitation/radiation 공급은 이 소유자 결과를 채택해야 하며 재구현하지 않는다. PR141 본문은 S0 이후 implementation 완료를 아직 주장하지 않으므로 더 강한 판정은 해당 최신 산출물을 읽은 owner에게 맡긴다. |
| rec_bianchi | PR130 REC-HISTORY → `93e1bdc8298db9a7c16f77d4bf64985a0c3f25aa` | causal history/경계 adapter의 복구. physical/production HOLD와 완전한 thermal Jacobian 잔여 의무를 보존한다. |
| vigilode | PR80 V1 readiness, PR81 portable norm; 별도 general-ode-selection ref `14171ed0c4f7dc453f47870cf6c1399f41afc4f2` | portable norm과 native owner/solver 통합은 별개. general-ode-selection은 현재 열린 PR 목록과 연결되지 않았으며 본문 미조사. 기존 P02 C6FAIL과 native 소유권을 유지한다. |

위 외부 결과의 설명은 관측한 PR 본문/metadata 범위다. 외부 raw science를 다시 검증하거나 실행하지 않았다. root 요청에 따라 material next-node source 외 본문 확장은 여기서 종료한다.

## 핵심 재사용 발견: PR59–64

모든 아래 브랜치의 현재 head는 해당 과거 완료 head와 동일했다. 현재 F에서 가져온 공개 파일도 Git blob/size가 검증됐다.

| PR / 실제 head | 현재 F 안의 파일 | 재사용 내용과 범위 |
|---|---|---|
| [59](https://github.com/cosmosapjw-quantum/bass_cr/pull/59), `029b2122db4f76f5a639e8ae4d58cf552e71b91d` | `research/cr_coulomb_partition_20261014/RESULT_AND_DELIVERY_KO.md`, `coulomb_partition.py` | Maxwell bath A/D/angular coefficients, reversible finite-band reference, moving-interface count/energy, opposite bath moment, eliminated-core memory |
| [60](https://github.com/cosmosapjw-quantum/bass_cr/pull/60), `2c404479469cb0e1bf1dd073a50c1e2123809606` | `research/cr_core_tail_pilot_20261014/RESULT_AND_DELIVERY_KO.md` | fixed-V Coulomb-only four-origin-label Gaussian moment pilot, reciprocal pair heat, shape defect |
| [61](https://github.com/cosmosapjw-quantum/bass_cr/pull/61), `8a2bb3d8220ecc871ae786d9fa67a9f94465202f` | `research/cr_kinetic_defect_20261014/RESULT_AND_DELIVERY_KO.md` | symmetric nonlinear radial Landau kernel, 128–2048-cell saved histories, separate moment/kinetic/continuum claims |
| [62](https://github.com/cosmosapjw-quantum/bass_cr/pull/62), `aa2705dc3e35a03920e2cd5e7efc32ef9fe43c77` | `research/cr_tail_stability_20261014/RESULT_AND_DELIVERY_KO.md` | coarse continuum temperature/tail bound; fine shape correction remains open |
| [63](https://github.com/cosmosapjw-quantum/bass_cr/pull/63), `6da1d99643660974a48da3677658a4a37b6f5392` | `research/cr_weak_front_rei_20261014/RESULT_AND_DELIVERY_KO.md` | same saved nonlinear history의 weak cutoff residual, separate REI threshold diagnostic |
| [64](https://github.com/cosmosapjw-quantum/bass_cr/pull/64), `26ac3b4eb6cbe792101c09ab48b3562dab8c5249` | `research/cr_r5_trace_threshold_20261014/RESULT_AND_HANDOFF_KO.md` | signed continuum tail trace/affine flux lifting; smooth constitutive residual and fine adjoint remain open |

PR59 code Git blob **27923abcaef06527011eb916acf7a414dd43c128**, 3984 bytes. Its report blob **56a3dd2a678873fc1e7805880f62f4c0b6c94aca**, 11636 bytes. The report distinguishes published tested code commit `7900d17dcf4f13c07cdd144b1abc85e53811e3e4`, PR59 final and present containing commit F; F is not retroactively its execution-time commit.

### Existing Maxwell-bath implementation

Let theta=kB T/epsilon_eV, x=W/theta and Phi=erf(sqrt(x))−2sqrt(x)exp(−x)/sqrt(pi). Existing code implements:

- `D=theta*b0(W)*Phi`, variance 2D dt;
- `j=-D[N'+(1/theta-1/(2W))*N]`, stationary count weight proportional to sqrt(W) exp(−W/theta);
- Ito drift `a=D'+D*(1/(2W)-1/theta)`;
- angular Laplacian coefficient, with electron-ion scattering explicitly separate;
- an explicitly separate running-log extension retaining the logarithm derivative;
- `MaxwellianCoulomb.coefficients`, `energy_flux`, `reversible_generator`, `bath_energy_rate`, `moving_interface`.

The reused local assumptions are nonrelativistic, nondegenerate, weakly coupled Maxwell electron background, declared common leading Coulomb logarithm and bath-rest proper time. It is not the nonlinear production operator or an automatically qualified bath for C23B.

### Existing moving-interface equation

With positive energy current toward increasing W, old PR59 already gives

```text
Jrel = integral_Omega[j_C + g_W F - qdot F]_(W=q)
I_C  = integral_tail j_C dW dOmega
Ntail' =  Jrel ; Ncore' = -Jrel
Utail' =  q Jrel + I_C + Work_tail
Ubath' = -q Jrel - I_C + Work_core
```

The same interface transfers count/energy. Bulk collisional exchange I_C also contributes before crossing. Adding the old stopping-heat term to the opposite kinetic moment duplicates that interaction. A full Maxwell pivot is not an extra physical population, and a truncated core has different potentials and mean energy. The original source had nonthermal/core count ratio 2, so that source did not automatically justify dilute test particles.

## Cold-source result that must remain separate

The restored Oct12 `CONTRACT.json`, `CLAIMS.json`, `COLLISION_CLOCK_KO.md` and actual `causal_cascade.py` identify

```text
G(d) = d G(1) - (d log(d)/2) C0
```

under fixed temperature/composition/grid/redistribution, common scaling of all target densities, and positive shifted Coulomb logs. This identity corrects the source-pinned cold downward drift; it is not an arbitrary finite-T Landau density law.

The Oct13 `KERNEL_EVENT_ADAPTER_KO.md` explicitly owns `n_e=N_e,thermal/V`, distinct from all-free electrons and total thermal particles. Existing fixed-energy coefficients have no explicit T dependence at fixed density. The cold-target domain requires W≫kBT, positive log, dilute targets, and original 0.1–900 eV source/excitation closure. The cutoff existence condition chi≥3/2 does not certify cold-target accuracy. It explicitly leaves finite-T diffusion/all-free screening/thermal cross-section averaging as separate closure.

Thus a new source-to-warm-operator connector must bind current bath/distribution/density, coefficient normalization, Coulomb-log prescription, source clocks/volumes, electron ownership and actual validity. Old source anchor numbers, fixed-V four-label histories or cold density residuals cannot be copied as a new C23B physical run.

## Current DAG and minimal next action

Current N4 cutoff admission is COMPLETE_SCOPED/CONSUMER_ADMITTED only for `C23C_FROZEN_FIVE_LABEL_CALORIC_V1` and its stored 18 requests. Central stopping, empirical N5 and N6 remain OPEN.

The root can now freeze a distinct C23B-to-existing-EE-operator binding unit. Reuse PR59 equations/code and PR60–64 scope/evidence. New work should evaluate only a genuinely new bound source/bath input and its relevant checks, with physical time ratios and omitted-channel conditions stated. No old operator reconstruction, 2048-grid replay, or repeated theorem novelty claim is needed. Neutral/inelastic/electron-ion and empirical N5 coverage remain explicit dependencies; full stopping admission is separate from one EE component.

Frozen inherited campaign spend/remaining/currency stay null. Existing measured costs are owned by their execution receipts and `research/cr_n4_admission_20261024/BUDGET_CONTINUITY.json`; this intake neither remeasures nor resets them.

## Policy and four axes

Current bass_cr AGENTS and the three execution/readback policy blobs equal the earlier verified versions. Current rei_bianchi AGENTS also equals its prior version. The current root/research trees and selected units contain no applicable lower AGENTS; donor/intake AGENTS copies are not ancestor policies.

- **EXECUTION:** COMPLETE_SCOPED read-only intake. New science, ODE, prior suite replay and archive downloads 0; external runtime/lease UNOBSERVED.
- **PUBLICATION:** no mutation. Current ref identity observed; root owns any new expected-SHA publication and exact-ref check.
- **BACKUP:** no upload/download. Latest PR98/222 backup state is reported evidence only; separate backup agent owns reconciliation. Drive UNKNOWN_NO_ACK is not promoted.
- **DAG:** N4 cutoff remains admitted in its exact named scope. Next stopping source binding can proceed using existing EE evidence. N5/N6/full physical closure stay separately open; global_error_bound and overall percentage null.

Other conversations are UNAVAILABLE in this child task. The report does not infer private discussion contents or live external campaign state.

## Local evidence

- `ADVERTISED_HEADS_20261024.json`, `REF_DELTA.json`
- `OPEN_PR_INVENTORY.json`, `OPEN_PR_DELTA.json`
- `raw/ALL_BRANCH_PAGES.json`, `raw/SELECTED_REF_TREE_RESPONSES.json`, `raw/BASS_SELECTED_UNIT_TREES.json`
- `selected_prs/PARALLEL_CHANGE_BODIES.json`, `selected_prs/bass_cr_PR58_PR64.json`
- `SELECTED_BLOB_VERIFICATION.json`: 24 files, 277398 bytes, all current-tree Git blob/size PASS. Nine bodies reused from existing verified local bytes after current blob equality, avoiding redundant download.
