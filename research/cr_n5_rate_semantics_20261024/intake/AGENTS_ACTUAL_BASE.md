# BASS_CR project harness

## 현재 이론 연구 루프 — 실제 kernel과 온도 의존 cutoff, 2026-10-13

[현재 보고서](research/cr_kernel_cutoff_20261013/latex/manuscript.md), [전체 PDF](research/cr_kernel_cutoff_20261013/latex/report.pdf), [계획](research/cr_kernel_cutoff_20261013/PLAN_KO.md), [DAG](research/cr_kernel_cutoff_20261013/NEXT_DAG.json), [handoff](research/cr_kernel_cutoff_20261013/HANDOFF.json)를 먼저 읽는다. 실제 saved 9600-grid의 HI/HeI kernel 양의 사건 adapter와 같은 parent–target family sharing 보존, 온도 의존 cutoff의 유한 count·energy 분할, 연속 root·오차 certificate, 원자 branch의 유한 구성, 공변 경계 source와 fixed-reconstruction coupled feedback KC1–KC7이 독립 PROMOTE_SCOPED / PASS를 받았다. 가정과 적용 범위는 CONTRACT.json과 CLAIMS.json에 결속한다. 다음 이론 작업은 실제 coupled branch solver의 self-map·오차·crossing 선택 구성과 prescribed geometry 이후 현재 에너지에 대한 kernel 재결속이다. 선택 scenario/source·관측량 오차 예산은 기존 응용 node에서 결속한다. 이전 근거의 identity를 재사용하며, 조건 변화가 없는 과학 suite를 반복하지 않는다. 아래 이전 정책과 물리 채택 경계는 원문 그대로 보존한다.

## 현재 이론 연구 루프 — 온도·H/He 자기일관적 사건 step, 2026-10-13

[현재 보고서](research/cr_feedback_step_20261013/latex/manuscript.md), [전체 PDF](research/cr_feedback_step_20261013/latex/report.pdf), [계획](research/cr_feedback_step_20261013/PLAN_KO.md), [DAG](research/cr_feedback_step_20261013/NEXT_DAG.json), [handoff](research/cr_feedback_step_20261013/HANDOFF.json)를 먼저 읽는다. 공통 사건 extent의 비음성·선형 보존, 12-state/10-event H/He 구성, 양의 온도 domain과 고정점 존재·수축, 반복 및 물리 endpoint defect의 온도 오차, 공변 xAct 투영과 prescribed Bianchi 합성, 정확한 비선형 사례 FB1–FB7 및 두 reference 구현이 독립 PROMOTE_SCOPED / PASS를 받았다. 모든 주장은 명시된 유한 사건·rate-domain·angular closure·정칙 시간 조건에 결속된다. 다음 이론 작업은 실제 atomic kernel의 현재 parent/daughter 에너지에 대한 양의 사건 adapter와 온도 의존 cutoff의 implicit 경계 응답이다. 선택 scenario/source와 관측량 오차 예산은 해당 응용 node에서 결속한다. 기존 과학 실행과 원 근거의 identity를 재사용하고 조건 변화 없는 실행을 반복하지 않는다. 아래는 보존한 이전 단계다.

## 현재 이론 연구 루프 — 열적 진화와 충돌 시계, 2026-10-12

[현재 보고서](research/cr_thermal_evolution_20261012/REPORT_KO.md), [전체 PDF](research/cr_thermal_evolution_20261012/latex/report.pdf), [계획](research/cr_thermal_evolution_20261012/PLAN_KO.md), [DAG](research/cr_thermal_evolution_20261012/NEXT_DAG.json), [handoff](research/cr_thermal_evolution_20261012/HANDOFF.json)를 먼저 읽는다. 이동 cutoff, thermal/all-free 초과에너지의 정확한 동치, 공통 충돌 시계, 실제 Coulomb 밀도 잔차와 온도 오차 연결 TH1–TH7이 독립 PROMOTE_SCOPED를 받았다. 명시된 가정 아래 이론을 완결했다. 다음 이론 작업은 T·H/He 조성 피드백을 포함하는 양의 보존적 한 step 구성이다. 사용자의 명시적 이론 요청은 일반 유도·구성의 근거이며 실제 scenario 선택과 수치 오차 예산은 해당 응용 경로에서 결속한다. 검산과 원 근거의 identity를 재사용하고 조건 변화가 없는 이전 실행을 반복하지 않는다. 아래는 보존한 이전 단계다.

## 현재 연구 루프 — 실제 전자 주입원과 cutoff 열적 편입, 2026-10-12

[현재 보고서](research/cr_source_binding_20261012/REPORT_KO.md), [계획](research/cr_source_binding_20261012/PLAN_KO.md), [DAG](research/cr_source_binding_20261012/NEXT_DAG.json), [handoff](research/cr_source_binding_20261012/HANDOFF.json)를 먼저 읽는다. 실제 Qe=tA의 SI source binding, cutoff 에너지·입자수의 열적 편입 후보 및 누적 에너지 예산이 독립 PROMOTE_SCOPED를 받았다. 다음은 실제 선택 scenario/source, total/active/thermal 전자수 및 관측량 허용오차의 결속이다. 전역 REI 채택은 별도이며 새 NCP 작업은 없다. 아래는 보존한 이전 단계다.

## 이전 연구 루프 — CR 재사용 DAG와 M1–M3, 2026-10-12

[현재 보고서](research/cr_rux_m1_m3_20261012/REPORT_KO.md), [재편 계획](research/cr_rux_m1_m3_20261012/PLAN_KO.md), [DAG](research/cr_rux_m1_m3_20261012/NEXT_DAG.json), [handoff](research/cr_rux_m1_m3_20261012/HANDOFF.json)를 먼저 읽는다. M0와 이차 응답은 재사용했고, M1의 실제 소비자 snapshot 조사·M2의 양수성 보존 finite-age 오차 지도·M3의 국소 OFF 근거 재사용을 완료했다. 다음 here 작업은 `M1_ELECTRON_SOURCE_BINDING`과 실제 소비자의 오차 예산 연결이다. 전역 RUX 상태는 승격하지 않았고 새 NCP dispatch는 0이다. 아래 M0/plan-reset 항목은 보존한 이전 단계다.

## M0 후속 결과 — 2026-10-12

현재 완료 결과는 [이차 주입 이력의 가열 응답](research/cr_m0_quadratic_20261012/README_KO.md)이다. [현재 handoff](research/cr_m0_quadratic_20261012/HANDOFF.json)와 [다음 DAG](research/cr_m0_quadratic_20261012/NEXT_DAG.json)를 먼저 읽는다. 원 M0 COMPLETE와 감사 반영 계획을 유지하며, 다음 here 작업은 M1/M2/M3다. 이번 M0를 위한 NCP 작업은 없고 완료된 계산을 재실행하지 않는다.


## 현재 개발계획 — 2026-10-12

[CR 과학 산출물 우선 계획](research/cr_plan_reset_20261012/PLAN_AND_RESULTS_KO.md), [현재 DAG](research/cr_plan_reset_20261012/NEXT_DAG.json), [현재 handoff](research/cr_plan_reset_20261012/HANDOFF.json)를 먼저 읽는다. 아직 시작하지 않은 PHYS02H 전체9600 NCP qualification의 자동 실행은 보류됐다. 기존 cached response 해석과 관측량별 오차·domain을 우선하며, CR-off 기준 응용은 full CR 원자 연구의 완료를 기다리지 않는다. 이미 진행·완료한 NCP run은 원래 예산과 결과를 수집한다. 이 변경은 frozen H evidence/contract와 inherited physical gates를 바꾸지 않는다.


## Selective remote verification (owner policy, 2026-09-22)

Apply [.codex/readback-policy.json](.codex/readback-policy.json) and
[docs/READBACK_POLICY.md](docs/READBACK_POLICY.md) to all future project work,
including GitHub publication, Drive/Dropbox backup, handoffs and large artifacts.
These are project instructions for every agent and worktree, not global CUH-G
routing settings. Default: selective / R1. Do not fetch remote file bodies after
ordinary writes when provider success, remote identity and available integrity
metadata establish the mutation. Record the tier actually achieved.

R3 is required for the listed release, overwrite, recovery, trust/authority change,
inconsistent provenance and explicit-user-request conditions. Missing optional
provider SHA256 alone is not a reason to download. Do not label metadata-only
verification as raw readback. Keep local artifact sources until receipts exist.

This policy supersedes blanket post-write raw-readback requirements in older
project handoff documents for future operations. Preserve archived results,
receipts, manifests and their historical meanings; do not retrospectively promote
an incomplete backup. A changed source digest does not migrate old checkpoints.

The legacy `scripts/r3m11_dual_backup.py` always performs raw readback and does not
load this configuration: use it only for R3 with a recorded trigger/explicit
opt-in. For R1/R2 use the metadata workflow in docs/READBACK_POLICY.md. Do not invoke
the legacy script as the default upload path. These rules are agent-harness
instructions, not a shell-wide interception of manually executed commands.

Keep b-grid NO_GO and existing scientific claim ceilings. Verification policy
changes do not authorize new physics runs, 50/225 keV/u, integrated cross sections,
physical rates, main-branch merges or changes to global runtime policy.

## Code ownership and cloud handoff (owner instruction, 2026-09-28)

Follow [docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md](docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md).
ChatGPT is the primary implementation/repair/test/packaging worker. Deliver tested
code and exact source identity before handing work to cloud Codex. Cloud Codex
performs focused review, necessary in-scope repairs, approved execution and evidence
return; do not make it reimplement delivered features or restart completed work.
Unchanged prior suites are not rerun. Changed code/environment receives targeted
checks. Preserve separate scientific, runtime, publication and authority gates.

## Accuracy-preserving HPC development (owner instruction, 2026-10-01)

Apply [docs/HPC_ACCURACY_POLICY_KO.md](docs/HPC_ACCURACY_POLICY_KO.md) to future
research code. Target the actual admitted topology/RAM of the64-CPU128GB NCP:
OpenMPI for independent complete query ladders, Fortran/OpenMP and SIMD for
validated hot kernels, Python for orchestration. Preserve FP64, quadrature,
tolerances, per-entry accumulation order and source/context identity. No fast
math, uncontrolled floating reductions, nested BLAS oversubscription or silent
reuse of old native approval. Measure same-input correctness and performance;
do not claim64-core scaling from a smaller-host benchmark. Include rank0 and
memory reserve in resource admission. See the additive R4S HPC implementation.

The R4U integration in `research/gap_closure_20261001/production_solver_20261001/`
connects the physical qualified provider to the HPC queue and a cache-only,
checkpointed midpoint solver. Use its fresh source/native/input/resource manifest
and exact cache/time identities for this archived B0 lane. Operational acceptance
and restart checks do not close the independent scientific production gates.

R4V `research/gap_closure_20261001/production_validation_20261001/` adds
bounded local process partitions when no admitted MPI launcher is available.
The single coordinator allocates disjoint, nontransferable raw-attempt blocks
before launching any lane. Aggregate CPU/RAM admission and exact manifest pins
remain mandatory; failed lanes cancel all owned work, including orphaned children.
This local path is not evidence of MPI execution or NCP64 scaling. Its fresh-context
G02/G03 analyzers preserve the original scientific thresholds. The Richardson
supplement never replaces the raw FD gate, and the short same-IVP DOP853 pilot
does not certify the full scattering window or a continuous error bound.

R4W `research/gap_closure_20261001/g02_stable_derivative_20261001/` separates
same-center derivative residuals into stored FEM interface defects and numerical
arithmetic, with an exact-coefficient/high-precision reference. The continuity
candidate is a separate mathematical representation, not an adopted bank.
Keep the original G02 failure and basis identity; tiny-h reruns or projecting
raw D cannot substitute for independently validating a changed representation.

R4X `research/gap_closure_20261001/g02_continuous_basis_20261002/` implements
an explicitly separate shared-endpoint/bubble radial representation. Original
nodal eigensolve bytes are not recovered. Exact trace/norm checks and bounded
paired static S/H/D diagnostics preserve the original bank and raw operators.
The strict Fortran/OpenMP evaluator has local bitwise parity and timing evidence;
the static comparison itself uses the fixed C++ moment backend and Python radial
evaluator. This does not establish full solver or NCP64 speedup. At z=0 the
order32/40 spatial comparison remains unresolved for both representations.
Before derivative/production adoption, bind the new representation separately
and qualify spatial quadrature. Keep G02 UNRESOLVED and all prior claim ceilings.

R4Y `research/gap_closure_20261001/g02_central_quadrature_20261002/` qualifies
only the separate R4X candidate's central z=0, b=2, 100keV/u spatial operator.
Fresh C++/Python and Fortran/Fortran raw/full parity is bitwise exact. The
original 1e-9 six-raw-block criterion passes at legacy (56,2)->(64,2), with
independent (48,4), and at inner-phase beta24 order40->48, with independent
beta12/order40. Both full screens and unprojected identical-s central exact-zero
controls pass for the selected comparisons. The phase rule preserves the basis,
outer FEM/triangle panels and radial Gauss measure; it is a separately identified
quadrature rule, not a certified error bound. Lower-resolution failures remain.
Thirteen actual static calls used local admitted process/OpenMP parallelism;
no MPI or NCP64 scaling is claimed. Preserve the immutable run context and
distinguish the subsequently added read-only analyzer from executed sources.
Next qualify every derivative-stencil geometry under a fresh context before
testing the full dS/dt=D+D-dagger identity. G02 remains UNRESOLVED, production
HOLD, capture false, all_bound OPEN and b_grid NO_GO.

R4Z `research/gap_closure_20261001/g02_derivative_validation_20261002/`
checks the separate candidate's central full metric derivative using S-only
fixed Richardson weights. All13 shifted geometries pass the original six-block
spatial criterion with order40/48 beta24 and independent order48 beta12.
The two preselected fine windows pass all three absolute residual norms at1e-12,
window agreement and cross-rule agreement. The coarse window and original R2
failures remain recorded; this does not establish physical C9 regularity, a
certified order8 bound, the original eight-center gate or full G02 closure.
RUNTIME_INTERRUPTION_RECOVERY retains25 completed payloads and three interrupted
attempts; a distinct context adds15 missing payloads, for40 completed results
and43 charged attempts. Do not resume the old started batch in place or fabricate
its terminal marker. The source-pinned recovery adapter changes collection and
reporting only; original numerical functions, inputs and native binaries remain.
Use FINAL_STATE.json and the report for current state; RUN_STATE.json preserves
the original pre-execution record. G02 remains UNRESOLVED, production HOLD,
capture false, all_bound OPEN and b_grid NO_GO; no MPI/NCP64 scaling is claimed.

