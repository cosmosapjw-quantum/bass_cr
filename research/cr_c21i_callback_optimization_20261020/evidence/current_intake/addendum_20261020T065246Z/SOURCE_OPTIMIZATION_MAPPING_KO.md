# 최신 source 최적화와 C21I의 대응

관측 기준은 외부 GitHub 2026-10-20 06:03–06:06 UTC와 현재 보존된 C21I component/block 근거다. 목적은 이미 구현한 경로의 의존성·비용·후속 연결을 비교하는 것이다. 외부 배속은 BASS native 성능으로 채택하지 않는다. 입력 문서·source SHA는 이 별첨의 `SOURCE_INPUT_IDENTITIES.json`에 고정한다.

## 1. 저장하는 계산과 유효 범위

| 경로 | 실제 저장 대상과 의존성 | 계속 수행하는 작업 |
|---|---|---|
| REI PR198 `cell-cache` | 하나의 Jacobian 동안 각 photon cell의 `PreparedCell`. 같은 immutable transport·geometry/ray scale·support가 전제다. 가스 차분은 photon state가 같아 모든 cell을 재사용하고, photon 차분은 명시한 한 cell만 다시 준비한다. `prepare`는 모든 support와 나머지 cell의 number/energy_ref가 base와 같은지 검사한다. | 현재 absorber·gas에서 native rate와 원 node 순서의 합산을 다시 계산한다. RHS budget과 node visit은 생략하지 않는다. 비교가 수치 `!=`이므로 이 구현의 finite exact equality를 IEEE signed-zero bit identity라고 부르지 않는다. |
| C21I `vectorized_exact` | 성공한 원 RHS 전체 `F_u(t,u)`. cell-owned LRU16에 **실제 t와 physical u 전체의 binary64 bits**를 key로 사용한다. source/provider owner·fixture·birth·cell/clamp·D·dynamic map은 고정된 scope다. | domain·deadline·provider 상태·소유권 guard와 반환 copy는 hit에서도 실행한다. Miss는 원 RHS와 원 gas/time FD를 실행한다. 실제 RHS/native 호출과 logical request/hit를 분리한다. |
| C21I Schur companion | `S=I−σC−σ²BA`의 작은 LU factor. key는 M/G/L 및 σ/A/B/C 전체 bits다. P/Q와 현재 RHS는 S의 의존성이 아니다. | 현재 P/Q·RHS로 tau와 ledger15를 복원하고 full-space residual을 계산한다. RHS 또는 전체 Jacobian의 cache와 다르다. 현재 C21H backend에는 미연결이다. |
| REI PR199 A/B/C | 고정 입력 선형 age-transport의 정확 exponential interval·같은 age·같은 group oracle. cache는 `(rate_id,later_bits,earlier_bits)`, immutable rate 및 입력에 묶인다. 다른 thread의 모든 prefix endpoint bits를 canonical 결과와 대조해 동일 검산을 재사용한다. | 원 directed 산술, 원 node/group 순서 및 interval/prefix 계약을 유지한다. 이 모델에는 현재 C21H의 nonlinear gas/native RHS와 adaptive cell trajectory가 없다. |

REI198의 native cell preparation API는 별도 LRS owner/source에 추가된 것이다. C21H의 고정 owner `6ea2b1b4…`와 `C21H_V1` JSONL API에 그 메서드가 있다고 가정하지 않는다. C21I의 RHS-value cache를 그 cell cache로 바꾸는 작업은 새 native API·source identity·동등성 계약이 필요하다. [REI198 source](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/native_additions/axbi_native_rhs.rs), [REI198 admission](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/33ae18c31bf61bcc99d6d05edb6c2e7a5cb272a1/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/optimization_20261020/ROOT_ADMISSION.json).

## 2. 실제 비용을 먼저 대조한다

REI198의 새 15개 AB/BA pair에서 두 mode의 실제 RHS attempt와 node visit은 같았다. fixed 첫 pair는 각각 2,992회와 1,914,880회이며 cell preparation만 119,680→14,720회다. 같은 fixed 5쌍의 native wall 중앙값은 0.550993→0.122657s, **process 전체** 중앙값은 0.666076→0.214912s다. Preparation 감소율을 전체 배속으로 대입하지 않는다. 이 intake는 새 pair와 summary만 대조했고 기존19 history 전체를 재분석하지 않았다. 이번 REI198 최적화의 NCP 실행은 NOT_RUN이다. [실제 pair와 source 대조](../20261020T060305Z/SCOPED_RAW_READBACK.json).

C21I의 완료된 component 측정은 원 RHS closure와 제조 microphysics를 사용했다. 같은 입력의 timed 출력3,888개가 원 callback 출력과 bitwise 일치했으며 native/Rust/ODE 실행은 모두0이다. 지정된 `jacobian→rhs→partial_t` 순서에서 원 RHS는 triplet당 `2G+5→2G+3`회로 줄었다. 빈 cache의 cold serial batch에서 M64/128 벡터화는 약1.13–1.22배, exact reuse 포함은 약1.25–1.49배였지만 M9/G4 벡터화-only 배속은0.855로 느렸다. Warm 동일점4.82–11.19배는 의도적으로 같은 FD 점까지 반복한 조건이고 실제 solver hit율이 아니다. 두-task thread 정책도36묶음 중31묶음에서 serial보다 느렸다. [C21I component 보고서](../../../bass_cr/research/cr_c21i_callback_optimization_20261020/evidence/component_analysis_01/CALLBACK_COMPONENTS_REPORT_KO.md).

현재 native admission helper는 source·class·운용 identity 및 파일 lease를 추가로 검사한다. 그 guard의 JSON 비교/stat 비용은 위 제조-provider benchmark로 측정되지 않았다. 실제 native 총비용은 그 helper를 연결한 runner에서 판단해야 한다. [Native admission 범위](../../../bass_cr/research/cr_c21i_callback_optimization_20261020/NATIVE_CACHE_ADMISSION_KO.md).

## 3. 수학 연결과 다음 판정

C21I는 `J=[[0,A,0],[B,C,0],[P,Q,0]]`의 구조화 JVP와 Schur 식을 실제 Rust companion으로 구현했다. 제조312 solve/240 JVP 및 독립 raw 검토 근거는 존재하지만, dense comparator는 scalar reference이고 C21H VigilODE/Diffsol 선형해법은 교체하지 않았다. 따라서 큰 제조 행렬의 factorization 차이를 native solver 배속으로 사용하지 않는다. Ledger15의 출력·full residual·기존 WRMS는 계속 남는다. [Block companion과 적용 경계](../../../bass_cr/research/cr_c21i_callback_optimization_20261020/block_solver/README_KO.md).

REI199의 원문과 받은 C2_rep3 study는 57,344개 고정 node의 endpoint 모델이며 `no nonlinear ODE or cosmological history solve`를 명시한다. 대표 run3.531863s/threads2와 새 exact-arithmetic source의 identity는 확인했지만 새 age32 native 결과가 아니다. 이 사례에서 재사용할 원칙은 완전히 동일한 계산의 중복 제거와 **요청한 최적화 mode의 실제 활성화 검사**다. 그 exponential/affine 알고리즘이나 배속을 C21H 비선형 RHS에 그대로 연결하지 않는다. [REI199 구현·실측](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/cf00684741eb612e35f987713c28937513d44d57/research/rei_age_exposure_envelope_20261018/optimization_20261020/README.md), [mode activation 독립 검토](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/cf00684741eb612e35f987713c28937513d44d57/research/rei_age_exposure_envelope_20261018/optimization_20261020/reviews/c9/C9_RECEIPT.json).

다음 runner의 판정 대상은 동일 fixture·rtol·alpha·binary·worker에서 실제 callback 순서, original/native 실제 호출 수, accepted 전체 상태·ledger 수지, RPC bytes, 준비·guard·실패·거절·fallback을 포함한 wall 비용이다. 구조화 API가 실제로 연결되기 전까지 block companion은 별도 완료 노드다. `global_error_bound=null`을 유지한다.

| 실행 | 게시 | 백업 | DAG |
|---|---|---|---|
| 이 별첨은 새 실행 없이 보존 source·실측을 비교 | GitHub write0; 마지막 C21H create_tree는 SHA 미반환, 이후 ref/PR[] | 기존 intake immutable; 이 별첨은 create-only, 상위 provider ACK를 따름 | source/비용 대응 완료; native runner 통합·실제 trajectory/NCP는 별도 노드 |
