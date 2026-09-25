# START: BASS_CR foundation rebuild return

ROLE=LOCAL_CODEX_TWO_CENTER_FOUNDATION_IMPLEMENTER
PROJECT=cosmosapjw-quantum/bass_cr
BASE_AUDITED_COMMIT=8e1d49e5ef6af70bb47d9238e64cda68ea0f5c4f
BASE_AUDITED_REF=cr/r3m29-spatial-discretization-discriminator-20260924
NEXT_PROPOSED_NODE=FND_R2_TWO_CENTER_OPERATOR_PARITY_AND_BOUND_SPECTRUM
MODE=BOUNDED_PHYSICS_FIRST_REBUILD

## 목표
기존 cell-average same-h4-step sensitivity node만 반복하지 않는다. 이번 패키지에서 실제 검증한 true-H 준비, Coulomb Fourier-Galerkin, radial FEM, moving-frame exact benchmark를 읽고 두 중심 S/H/D kernel의 첫 독립 구현으로 전진한다. 원래3% capture gap을 이미 해결했다고 주장하지 않는다.

## 먼저 읽기
REPORT_KO.md, docs/MATHEMATICAL_FOUNDATIONS_KO.md, docs/REBUILD_ARCHITECTURE_KO.md,
results/SYNTHESIS_SCALARS.json, results/CP3_FINAL_TESTS.txt, results/FAILURE_LEDGER.json,
src/bass_foundations/kernels.py, tests/test_foundations.py.
Repo에서는 docs/r3m26/MODEL_CONTRACT.json, MODEL_FOUNDATION_KO.md,
docs/roadmap/ERROR_BUDGET.json, docs/r3m27/REPORT_KO.md, docs/r3m28/REPORT_KO.md,
docs/r3m29/REPORT_KO.md, cr_repro/aocc.py, scripts/r3m17_aocc_metric.py를 exact source로 읽는다.

## Intake와 보존
remote ref/HEAD를 실제 확인한다. 다른 최신 작업이 있으면 diff/identity를 먼저 읽고 destructive reset하지 않는다. 원래 작업 checkout, 사용자 untracked files, R3M10–29 raw failures, source digest, scientific claim ceilings를 보존한다. 해당 사용자의 로컬 workspace 정책이 금지하면 새 git worktree를 만들지 않는다. 새 결과는 별도 output root에 쓴다. GitHub push/merge는 별도 사용자 요청 범위에 따라 처리하고 자동 main merge하지 않는다.

이 package의42 tests는 원 repo의 full-suite PASS가 아니다. 현재 환경을 출력한 다음 위 README의 tests를 fresh 실행한다. local model은 필수 dependency가 아니며 실패해도 coding을 막는 gate로 만들지 않는다. 예산 절약이 physics/coding 목표를 대체하게 하지 않는다.

## 이번에 닫힌/남은 질문
- finite-τ split eigenstate가 true H_h eigenstate가 아니라는 구조와 residual floor가 실제3D probe로 강하게 확인됨.
- true-H preconditioned eigen preparation은 CPU 독립 oracle와 검증됨. production preparation budget은 아직 OPEN.
- point/cell의 E1s error 및 translation dependence가 직접 측정됨.
- nonalias Galerkin은 static spectrum에서 큰 개선, exact translation identity와 Toeplitz/dense parity 확인. 구면 cutoff/periodic 모형이므로 full original Coulomb production으로 곧바로 바꾸면 안 됨.
- radial239DOF/l, R128,n<=3 spectrum은 정확하지만 two-center collision engine은 미구현.
- R3M17은 metric derivative를 이미 검사한다. 새로 필요한 것은 D의 skew part를 직접 검증하는 basis-derivative/physical transport benchmark다.
- actual capture gap, all-bound, b-grid, CAP/finite-time/interactions는 unresolved.

## 한정된 다음 실행
1. 독립 패키지/추가 모듈로 two-center radial basis specification을 만든다. 초기 작은 lmax=0,1,2,3 경로와 negative/positive pseudostates를 구분한다. s+p-only를 n<=3 complete basis라고 부르지 않는다.
2. 작은 separated and overlapping centers에서 S,H,D를 조립한다. v=0 1s overlap의 exp(-R)(1+R+R²/3)를 독립 기준으로 사용한다. v≠0의 ETF overlap은 별도 quadrature로 검사한다.
3. 직접 basis derivative로 D를 검증한다. Sdot, Cholesky derivative, G skew test만으로 끝내지 않는다. 순수 anti-Hermitian perturbation에 반응하는 negative control과 exact moving-Coulomb benchmark를 요구한다.
4. 작은 frozen H의 dense exponential, weighted norm, analytic atom spectrum, angular degeneracy, quadrature/box/basis refinement를 검증한다. H/S/D source bytes 및 derived operator identity를 묶는다. 실수 floor나 symmetrization으로 결함을 감추지 않는다.
5. 한 번의 bounded common-capture pilot 설계를 만들되 실제 run 전 geometry/basis/time/reference/output/resource contract를 고정한다. 이전4-step cell-average 실험을 그 설계의 mandatory 선행조건으로 만들지 않는다.

## stop conditions
실패한 primitive/connection/domain/reference가 있으면 해당 실패를 그대로 봉인하고, parameter를 무작정 줄이거나 이미 resolved한 scalar audit을 반복하지 않는다. Two-center kernel이 독립 기준을 통과하면 다음 실제 small-capture experiment로 나아간다. Production status는 common typed observable의 모든 component 근거가 생기기 전까지 HOLD다. 새관측량에 예전 fixed-h time PASS를 복사하지 않는다. Exact paper/private raw 재현이나 rigorous global certificate를 필수조건으로 재도입하지 않는다.

## 반환 형식
수학 식과 수치 form의 대응표, 변경한 코드, exact source/commit identities, 실제 command/test output, S/H/D residuals와 first failures, scope별 claim status, measured CPU/GPU/memory 비용, 다음 하나의 실험을 반환한다. 새로운 체크포인트는 Google Drive+Dropbox에 create-only 저장하고 두 provider의 실제 응답 및 가능한 size/checksum을 receipt로 보존한다. UPLOAD_VERIFIED와 RESTORE_VERIFIED를 구분한다. 큰 endpoint를 복원하지 않았으면 full state restore를 주장하지 않는다.
