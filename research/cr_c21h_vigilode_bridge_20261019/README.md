# C21H: 원본 광학깊이 IVP를 쓰는 VigilODE·Diffsol 비교 경로

> 현재 게시 중단: 새 명시적 push 지시 후의 create_tree594개 재시도도 user rejected MCP tool call을 반환했고 tree SHA가 없었다. commit·branch·PR 생성은 실행하지 않았다. 최신 상태는 `PUBLICATION_RECEIPT.json`을 따른다. 원래 8개 runtime source는 변경하지 않았다. 현재 환경의 locked 실제 재컴파일과 복원 근거는 새 영수증에 보존하며 native chemistry/NCP는 NOT_RUN이다.

> 역사 기록 — 재지시 이전의 2026-10-20 게시 요청: 새 create_tree도 `user rejected MCP tool call`을 반환했다. 원격 tree SHA·commit·branch·PR은 확인되지 않았고 현재 게시 상태는 `PUBLICATION_RECEIPT.json`을 따른다. 원 과학 source·검증은 유지되며 최신 실행/복구 증거는 별도 create-only 백업에 보존한다.
> 역사 기록 — 2026-10-20 이전 이관: 다른 대화로 이관하기 위해 C21H 게시 요청이 중단됐다. 마지막 create_tree 응답은 aborted by user였고 SHA가 없으며, 실제 branch/commit/PR 생성은 확인되지 않았다. 프로그램과 검증 raw는 세 저장처에 보존된 원 과학 ZIP에서 바이트 동일하게 복원했다. 현재 영수증을 읽고 게시를 재개한다. Native chemistry/NCP는 NOT_RUN이다.

이 단위는 `bass_cr` PR84의 연속방정식과 기존 native provider를 그대로 호출하면서, 적분 방법을 **VigilODE Rodas5P fast** 또는 **Diffsol 0.17.1 BDF**로 선택할 수 있게 한다. C21G의 reference 민감도 연구에 서로 다른 stiff 적분 방법을 연결한다. 새 물리 closure나 native kernel을 만들지 않는다.

현재 배포·검증 상태는 `PUBLICATION_RECEIPT.json`, `BACKUP_RECEIPT.json`, `VALIDATION_SUMMARY.json`, `DAG_C21H.json`에서 각각 확인한다. 이 파일들이 생성되기 전의 작업 snapshot은 게시 완료를 뜻하지 않는다. 실제 C21H native chemistry/NCP 실행은 **NOT_RUN**이며 `global_error_bound=null`이다.

## 1. 고정 입력과 사전 조사

| 항목 | Identity |
|---|---|
| C21G parent | PR84, `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5` |
| C21G 실행 내용 | `e742d44f605c51c06615451774ba90af8f41f622` |
| 원래 광학깊이 RHS | `../cr_c21e_event_native_20261018/src/reference_tau.py`, SHA256 `714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0` |
| 미시물리 native owner | `cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4` |
| VigilODE 실행 source | `cosmosapjw-quantum/vigilode@8a8bd409b1d96c7b7421f496d229e119fd3d284e` |
| 새 의존성 | Diffsol `=0.17.1`, 두 backend의 Faer 선형대수, 고정 `Cargo.lock` |
| 확인한 도구체인 | Rust 1.94.1; Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0 |

현재 연결된 세 repository의 모든 branch·모든 상태 PR·tag ref·release 목록을 페이지 끝까지 읽고, 관련 Drive/Dropbox/Library의 폴더와 제목 목록을 조사했다. 초기 목록은 각각 branch 161/247/147, PR 84/205/71개다. NCP의 비게시 파일이나 모든 역사 branch의 모든 blob에 대한 부재 증명은 아니다. 자세한 조회 범위와 실제 connector 제한은 `evidence/intake/`에 있다.

새 VigilODE 원시 CSV 154행과 2700행은 실제 GitHub 바이트·Git blob·SHA256을 검사했다. 작업 도중 PR71에 추가된 run `39257390707`도 다시 확인했다. 새 보고서는 756개 실행 완료와 solver별 목표 정확도 통과 수를 구별한다. 측정 source commit에 적용된 두 campaign repair도 함께 기록했다. 이 별도 벤치마크를 C21H native 결과로 바꾸지 않는다.

C21F 복구·게시·기존 native 결과와 C21G 게시/백업을 재사용한다. 과거 과학 ZIP의 역사적인 `NOT_PUBLISHED` 문구, 중간 branch, `APPLY_C21F_FULL.py`를 다시 적용하지 않는다. C21G의 두 fixture × L1/L2/L3/L3M 8개 reference 및 조건부 native refinement 4개 실행 계약은 독립적으로 유지한다.

## 2. 방정식에서 구현까지

원래 독립변수는 \(x=\ln a\)이고, 각 활성 cohort는

\[
\tau_i'=\lambda_i/H,\qquad N_i=A_i\exp(-\tau_i)
\]

를 따른다. 상태는 광학깊이 \(M\)개, gas 변수 4개, 누적 장부 15개다. `Y=0`이면 두 He unknown을 원래와 동일하게 제거한다.

`optical_adapter.py`는 SHA가 고정된 `reference_tau.py`를 별도 module instance로 읽고, **그 instance의 `solve_ivp` binding만** `RustIVP`로 교체한다. 원래 RHS closure, birth/breakpoint 순서, 상태 축소, ledger 적분, accepted tau 검사, endpoint 계산이 같은 함수 안에서 수행된다. 원본 파일과 공개 module binding은 바꾸지 않는다.

### 고정 대각 scaling

기존 C21G의 양의 척도 \(D_i\)를 쓰고 \(u=Dz\)로 둔다. 그러면

\[
F_z(x,z)=D^{-1}F_u(x,Dz),\quad
J_z=D^{-1}J_uD,\quad
\partial_xF_z=D^{-1}\partial_xF_u.
\]

물리 좌표의 `atol_i=alpha*D_i`가 scaled 좌표의 scalar `atol=alpha`로 정확하게 대응한다. 각 backend가 쓰는 같은 상태·오차벡터에서 weighted norm을 보존한다는 항등식이다. VigilODE의 old/new 최대값 분모와 Diffsol의 current-state 분모, 각 적분기의 오차추정기·controller는 서로 다르다.

### Jacobian과 시간 편미분

- \(\partial N_i/\partial\tau_j=-\delta_{ij}N_i\)로 광학깊이 열의 species·heat·photon-work 성분을 계산한다.
- 장부는 RHS에 되먹임하지 않으므로 15개 passive 열은 정확히 0이다.
- gas 열은 원래 provider를 호출하는 3점 차분이다. 물리 정의역 안의 실제 표현 가능한 중심/편측 노드를 사용한다. clipping이나 미분값 0 fallback을 쓰지 않는다.
- 원래 cell clamp의 평탄 branch와 corner convention에서는 시간 편미분 0, 내부에서는 clamp를 넘지 않는 3점 차분을 쓴다. 작은 inset이 endpoint로 반올림되는 원래 연산도 보존한다.
- 기본 gas probe는 `eps**(1/3)*max(abs(u_j),D_j)`, time probe는 `1e-4*cell_width`다. 실제 노드와 한쪽 차분 횟수를 저장한다. 필요한 표현 가능한 노드가 없으면 명시 실패한다.

수식, 단위, 정의역, 차분 truncation 항, 가능한 gas-block Schur 소거는 `theory/C21H_THEORY_KO.md`에 유도했다. Schur 소거는 수학적 구성 단계이며 이번 실행기의 별도 선형 solver로 구현·성능 채택하지 않았다. Wolfram 검산과 원전/공식 패키지 source 대조는 같은 폴더에 있다.

## 3. 실제 Rust 연결과 출력 계약

`rust_bridge/src/main.rs`는 한 segment마다 새 프로세스에서 `C21H_V1` JSONL protocol을 사용한다. Python은 원 RHS, Jacobian, 시간 편미분 요청에 응답한다. 순서·dimension·finite·version·오류 응답을 검사하고 양방향 메시지를 보존한다. 이 구현은 물리 식을 두 언어로 다시 작성하지 않으므로 입력 차이를 좁힐 수 있다. RPC 비용을 포함하며 기존 native-only benchmark의 속도비를 이 연결에 적용하지 않는다.

VigilODE는 fresh Jacobian의 실제 accepted base를 관측하고 마지막 endpoint를 붙여 전체 수락 grid를 반환한다. Diffsol은 실제 수락 step의 상태를 직접 저장한다. `internal_steps+1`, 시작/끝 시각과 상태, 전체 trace의 유한성·엄격 증가를 검사한다. 선형 work counter는 VigilODE의 `direct_factorizations`와 Diffsol의 `number_of_linear_solver_setups`를 각각 기록하며 같은 의미의 비용으로 간주하지 않는다.

Diffsol의 초기 자동 step 추정이 짧은 음수 epoch 구간 밖을 조회하는 실제 실패를 발견하여, 공개 `BdfState::new_without_initialise`와 `bdf_solver`로 지정한 초기 상태와 `h0`를 사용한다. 이후 통합 검증에서 관측한 roundoff stop 처리 및 실제 교정 결과는 Rust README와 검증 영수증에 기록한다.

## 4. 준비된 실행과 판별량

```bash
python3 research/cr_c21h_vigilode_bridge_20261019/run_pilot.py plan --out NEW_PLAN_DIRECTORY
```

`plan`은 C21H runtime 8개와 기존 C21G의 source/baseline identity를 확인한다. 실제 실행은 `smoke` 또는 `native`다. Native는 실제로 할당한 CPU, 기존 pinned native binary 또는 기록된 동일 owner build, 현재 bridge build receipt가 필요하다. 경로·명령의 완성된 예는 `handoff/CODEX_HANDOFF_KO.md`에 있다.

| 실행 | 수 | 입력/계약 |
|---|---:|---|
| C21H base | 4 | 두 기존 fixture × 두 Rust 방법, `rtol=2e-11`, `alpha=2e-14`, cell step divisor 8 |
| C21H FD followup | 조건부 4 | 해당 base가 실제 COMPLETE이고 같은 source·fixture·native·bridge인 경우 두 probe scale을 절반으로 |
| C21G 기존 reference ladder | 기존 8 | 기존 PR84의 실행 계약 사용, 완료된 동일 job 재실행 금지 |
| C21G discrete refinement | 기존 조건부 4 | 기존 reference readiness gate 뒤에만 실행 |

한 job의 계산 deadline은 300초, 원 RHS/native 호출 상한은 200000, 동시 실행은 1개다. NumPy import 이전에 BLAS/OpenMP/Rayon worker를 1개로 고정한다. Native provider 호출마다 남은 deadline 안으로 timeout을 줄인다. 종료 정리는 native 최대 약 2초, Rust 약 0.5초의 별도 정리 구간을 가질 수 있다. CPU55 보호와 현재 campaign의 자원 배정은 별도 실제 inventory가 필요하다. Affinity membership만으로 독점 할당을 추정하지 않는다.

각 output은 새 디렉터리만 허용하고 raw, 실제 입력·바이너리·source identity, derivative nodes, process exit, job receipt를 저장한다. 완료 뒤 identity를 다시 검사한다. FD followup은 base receipt와 payload를 전후 비교하여 실행 중 바뀐 parent도 거절한다.

`INDEPENDENT_BALANCES.json`은 기존 독립 진단으로 number/species/energy 수지를 다시 계산한다. Native endpoint는 `COMPARE_TO_PINNED_L0.json`, FD followup은 `COMPARE_FD_HALF_TO_BASE.json`에 차이를 기록한다. 이들은 수지와 관측된 민감도이며 전역 궤적 오차 상계가 아니다.

## 5. 상태와 재개

실제 성공·실패·교정 로그, 검사한 source SHA, 제조 IVP와 mock 계약 검사의 구분은 `VALIDATION_SUMMARY.json`과 `evidence/`가 담당한다. 기존 C21F 56개/C21G 35개 및 원래 native matrix를 다시 실행하지 않았다. 새 검사를 전부 red-first라고 표시하지 않는다.

현재 NCP 원격 호출 잔여량은 새 조회에서도 0%였고 live CPU/RAM/campaign 상태는 확인되지 않았다. 이곳에서 가능한 코드·컴파일·가벼운 검증을 완료한 뒤, NCP에는 현재 자원 확인·고정 build·실제 실행을 인계한다.

Full48, source-age/spectral/angular, Case B, signed Bianchi, full EoR, standalone Grackle driver parity는 해당 독립 검증 전까지 HOLD다. `DAG_C21H.json`은 각 완료 단계의 실제 게시·백업 영수증과 실행되지 않은 의무를 따로 연결한다.

## 마감 전 추가 결과 확인

17:09:32–17:12:05 UTC delta에서도 bass_cr PR84 head는 그대로였다. VigilODE production head는 `b56bb19ce85bc28a021138ee29689701a81bc4f0`로 변경됐으며 `604a91e703da062cd2445bc2cd9468f991a3ab43`의 core patch는 같은 shifted matrix 연산에서 panic을 typed NonFinite로 전파한다. 정상 Ok 연산의 값·순서는 그대로다. C21H의 finite callback/원시 실패 보존 계약은 유지되므로 검증한 `8a8bd409...` pin을 자동 교체하지 않는다. 새 patch를 채택할 때 해당 실패 경로를 따로 검증한다.

VigilODE PR71의 matched benchmark/readback과 REI PR198 native Radau 19설정(신규18+재사용1), PR199 고정 age transport도 추가로 확인했다. 서로 다른 fixture·owner·lane의 결과이며 C21G/C21H native 실행으로 채택하지 않는다. 최신 범위·source/runtime 변경과 문서 변경의 구분은 `evidence/intake/FINAL_17UTC_GITHUB_DELTA_KO.md`에 있다.
