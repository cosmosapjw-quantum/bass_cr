# C21I 값 캐시·벡터화·실행 통합의 독립 검토 계획

2026-10-20. 이 문서는 실제 C21H/C21F/C21G source와 pinned native owner를 읽고 작성한 **설계 검토**다. 새 C21I candidate source의 최종 검토, 새 callback benchmark, 새 ODE/native 실행의 성공 기록은 아니다. 구현 담당자와 독립적으로 작성했으며 해당 source를 수정하지 않았다. 이론 유도·Wolfram/유리수 검산과 저장 raw 분석은 THEORY_OPTIMIZATION_KO.md 및 기존 raw를 재사용한다.

## 1. 채택 가능한 구현 범위

현재 source에는 두 가지 구체적인 최적화 여지가 있다. 첫째, cohort별 Python loop와 전체 M+19 정방행렬을 만든 뒤 Y=0 축소하는 임시 할당을 줄일 수 있다. 둘째, 한 event cell에서 정확히 같은 시간·물리 상태로 요청된 RHS/Jacobian/time partial의 **성공한 base RHS 값**을 공유할 수 있다. 원 RHS closure 자체, gas/time의 정의역 안 실제 3점 차분, birth/corner 순서, 전체 accepted state와 ledger는 유지한다.

값 캐시는 순수한 수학값과 provider의 운용 상태를 구별해야 한다. 동일 입력에서 같은 값을 내는 kernel이라는 사실은 만료된 시간 예산, 종료된 native process, 바뀐 source/fixture를 허용하는 근거가 아니다. 아래 guard와 identity가 구현된 경우에만 exact cache를 admissible로 평가한다. 알 수 없는 사용자 provider는 cache를 끄거나 명시적인 purity contract를 요구한다. kind 문자열이나 duck typing만으로 admission하지 않는다.

새 Rust block solver가 standalone으로만 제조 검증되면 선형대수 companion의 결과로 기록한다. 그것이 C21H bridge의 실제 backend linear solver를 대체했다는 주장은 실제 wiring과 동일 binary의 end-to-end 실행으로 별도 입증한다.

## 2. 읽은 실제 source와 새 native purity 근거

검토한 repository source는 다음과 같다. 파일 identity는 REVIEW_SOURCE_IDENTITY.json에 기록한다.

| 원 단위 | 실제 파일 | 이번 검토에서 사용한 계약 |
|---|---|---|
| C21H | optical_adapter.py | physical guard, original callback count, 3점 차분, cell scope, Rust RPC·accepted trace |
| C21H | run_pilot.py | BudgetedNativeMicro, source/build identity, base-parent 검증, 300초/200000회, native call equality |
| C21F | src/reference_tau.py | 원 reduced_rhs closure, 실제 callback count, min_internal_tau, birth event와 exact Y=0 축소 |
| C21F | src/native_micro.py | process lifecycle, 실제 native call budget, timeout, raw 요청·응답, strict owner protocol |
| C21F | src/run_experiment.py | Fixture, opacity, breakpoints, initial state |
| C21F | src/event_coupler.py | state domain, ManufacturedMicro, MicroRates validation |
| C21F | native/native_point.rs | EVAL 입력이 fresh state와 immutable point kernel로 연결되는 경로 |
| C21G | campaign_contract.py | frozen source/baseline/fixture identity, owner binary 검증, scale 계약 |
| C21G | run_campaign.py | terminal payload·call count·process exit·source closure 검증 의미 |

Native EVAL의 값 의존성을 확인하기 위해 owner 6ea2b1b4b3875c9163cafc45efe720afded43fc4의 다음 5개 파일을 GitHub에서 새로 읽었다. 수신 바이트의 Git blob이 provider의 blob과 **5/5 일치**했다. 원본·fetch response·비교 결과는 raw/owner_purity/에 있다. 이는 이미 고정된 owner의 source 검토이며 새 native 결과 회수나 실행이 아니다.

| 파일 | 실제 Git blob |
|---|---|
| igm_thermal.rs | 0648618d9822e169e9672ac3c556f86595c3b0b6 |
| igm_state.rs | 437365fbe329a10afe292f9dd7eebf549fef804c |
| igm_rates.rs | dc3cc028a41ac852d94835372ce13545389d1c3a |
| hhe_events.rs | 57a63eee1e9d8c4aa2b5ed663dbea15619359f71 |
| lib.rs | 1dfdc11b6af391ceaf5a92713b10b8c89d7db6b1 |

native_point.rs의 EVAL은 요청마다 새 IgmGasState를 만들고, 명시적인 nh/nhe/temperature/photo/expansion 입력으로 igm_point_rhs를 부른다. igm_point_rhs → igm_rates, IgmGasState EOS → HHeModel의 관련 함수는 입력·상수·지역 값으로 계산하며 이 경로에 시계/RNG/가변 전역값을 읽는 연산이 없다. 이 exact owner·binary·동일 실행 환경에서 EVAL 결과값을 재사용할 수 있다는 source 근거다. wrapper의 calls/closed/process/timeout/log는 여전히 가변 상태다. 원 native package의 문서화된 coefficient floor/cap은 이 source의 기존 과학 계약이며 C21I가 새 projection이나 floor를 도입하는 근거가 아니다.

원전 링크: [igm_thermal.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6ea2b1b4b3875c9163cafc45efe720afded43fc4/rust/rei_microphysics/src/igm_thermal.rs), [igm_state.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6ea2b1b4b3875c9163cafc45efe720afded43fc4/rust/rei_microphysics/src/igm_state.rs), [igm_rates.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6ea2b1b4b3875c9163cafc45efe720afded43fc4/rust/rei_microphysics/src/igm_rates.rs), [hhe_events.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6ea2b1b4b3875c9163cafc45efe720afded43fc4/rust/rei_microphysics/src/hhe_events.rs), [lib.rs](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/6ea2b1b4b3875c9163cafc45efe720afded43fc4/rust/rei_microphysics/src/lib.rs).

## 3. Exact cache contract

### 3.1 값과 부수 상태의 분리

수학값은 F(x,u; θ)이고 θ는 한 cell의 고정된 source·fixture·provider·coordinate map이다. 실제 evaluator는 추가로 상태 s를 (s', F)로 바꾼다. cache는 F만 저장한다. Hit 경로에서 보존해야 할 guard를 evaluator 호출 안에 남겨 놓은 채 호출 전체를 생략하면 운용 계약이 변한다.

따라서 callback은 순서대로 (1) 현재 t/z의 physical validation, (2) 현재 job deadline와 provider lifecycle 확인, (3) immutable cell lease와 exact key 확인, (4) hit의 방어적 값 복사 또는 원 evaluator 호출, (5) 성공·finite shape 확인 및 deadline 재확인을 수행한다. 오류·부분 결과·nonfinite 값은 삽입하지 않는다. 원 source의 예외와 실패 raw를 같은 실패로 전달하며 stale 값으로 덮지 않는다.

원 reference_tau의 calls는 실제 원 RHS 호출 때만 증가한다. NativeMicro.calls 역시 실제 EVAL 전송 시도 수다. cache hit가 둘을 함께 줄이는 것은 실제 계산을 제거한 결과다. 이 hit를 실행한 native call로 보고하면 안 된다. 200000의 실제 호출 상한은 유지하며 논리적 Rust RPC 요청 상한도 유지한다. native call budget에 도달한 뒤 hit를 반환하는 것은 새로운 EVAL을 수행하지 않는다는 의미에서 actual-call cap 위반은 아니지만, 다음 miss는 원 상한으로 실패해야 한다. 현재 job deadline가 지난 hit는 허용하지 않는다.

원 RHS는 min_internal_tau도 갱신한다. 성공한 동일 물리 상태를 같은 active mask에서 이미 평가했다면 min 연산은 idempotent다. 다른 cell/active mask, 또는 일부 값만 같은 state에 이 주장을 확장하면 안 된다. 새로운 상태는 반드시 원 closure를 호출한다. accepted tau와 underflow/log-survivor의 원 검사를 유지한다.

### 3.2 Key와 cell lease

key는 원 evaluator에 실제 전달되는 float64 t bit pattern과 모든 reduced physical u의 bit pattern, shape를 포함한다. Python float tuple의 ==는 +0/-0을 구별하지 않으므로 bit-key를 사용한다. 현재 physical scaling 뒤의 u가 원 callback 입력이므로 scaled z 대신 physical u를 비교하는 것은 가능하다. 요청 시간 t 대신 clamp된 xx만 비교하면 callback convention과 진단을 합치게 되므로 이번 좁은 cache는 실제 t를 사용한다. NaN은 key에 넣기 전에 거절한다.

한 cell 객체가 다음 θ를 소유하고 외부 변경을 허용하지 않는 경우 해당 정보를 key마다 직렬화할 필요는 없다. 대신 새로운 cell/job/provider/구성마다 빈 cache를 만들고, setter나 변경 가능한 입력이 있다면 명시적으로 invalidate하거나 mutation을 거절해야 한다.

| 고정 의존성 | 확인·무효화 경계 |
|---|---|
| 원 reference source SHA 및 실제 fun closure | source hash 확인 후 private load, closure 교체 시 새 객체 |
| fixture 전체, nh0/Y/q/amounts/birth, source_identity | fixture canonical identity와 cell 소유 사본; 깊은 가변 list/array를 무조건 frozen으로 간주하지 않음 |
| lo/hi/active mask, clamp convention | event cell마다 새 객체; birth 전후 상태를 공유하지 않음 |
| dynamic indices, scale D, FD 정책 | 초기 고정 map/값을 소유; 변경 시 새 객체 |
| provider exact class, instance, owner/binary/config | 알려진 deterministic value 경로만 admission; instance 교체·설정 변경·process 종료 후 재사용하지 않음 |
| 프로세스·시간 제한 | key가 아닌 매 요청 guard; 현재 deadline/closed/poll 상태 확인 |

현재 RHS는 passive ledger 값에 의존하지 않지만 좁고 검토하기 쉬운 구현은 ledger 15개도 key에 포함한다. ledger를 key에서 제외하는 별도 최적화는 physical validation과 의미적 무의존성의 추가 증명 및 검사 범위가 생긴다. 이번 구현에 필요하지 않다. cache 값이나 key용 배열을 caller가 나중에 in-place 수정해도 저장 값이 바뀌지 않도록 소유 copy 또는 읽기 전용 소유 버퍼를 사용한다.

### 3.3 Provider admission

ManufacturedMicro의 현재 source는 입력값으로 계산하며 성공값 재사용이 가능하다. NativeMicro를 감싼 BudgetedNativeMicro도 위 pinned EVAL value 경로 및 기존 build/owner/binary 검증이 맞으면 후보가 된다. exact class/source와 known wrapper 조합을 확인하고, provider.kind 문자열만 같은 임의 객체·subclass·monkeypatch를 자동 승인하지 않는다. 사용자가 다른 callable을 넘길 수 있는 public API라면 기본 cache-off 또는 명시적인 purity token이 필요하다. token은 단지 문자열 선언으로 source 검증을 대체하지 않는다.

NativeMicro의 closed 또는 이미 종료된 process를 hit가 가리는 것을 막는다. cache가 제거한 EVAL마다 가짜 native log row를 만들지 않는다. 별도 callback cache counter와 원 RPC raw로 감소를 설명한다. 실패 후 같은 key를 다시 요청해도 새 성공으로 바꾸지 않고 원 실패 lifecycle을 따른다.

## 4. 실제 시간·counter 통합 문제

H run_segment.receive의 timeout 검사는 newline이 아직 없어 기다리는 동안에 수행된다. buffer에 이미 완전한 line이 있는 경우의 처리와 callback CPU 작업 전체에 대한 공통 deadline guard로 쓰기에는 부족하다. C21I는 각 logical callback의 시작/끝 및 solver 최종 반환 전에 한 job deadline를 검사하는 작은 명시적 강화를 둘 수 있다. cache hit도 이 경로를 지난다. native miss는 원 BudgetedNativeMicro의 timeout=min(15초, 남은 job 예산)을 계속 사용한다. 이 변경은 예산을 완화하지 않는다.

최소 보고 counter는 Rust rhs/jacobian/partial_t 요청 수, Python base-cache lookup/hit/miss, 실제 원 RHS 호출 수, 실제 provider/native 전송 시도 수, gas/time FD 평가 수, bytes, accepted/rejected step과 backend 고유 linear work다. H run_pilot의 native 성공 검사 provider.calls == result.rhs_evaluations를 유지한다. 줄어든 실제 호출은 세그먼트 합과도 같아야 한다. nfev를 원 RHS/native 호출 수로 다시 이름 붙이지 않는다.

## 5. Private runner injection과 provenance

H run_pilot은 import 시 NUMPY_ALREADY_IMPORTED를 먼저 기록하고 thread 환경변수를 모두 1로 설정한 뒤 optical_adapter/NumPy를 import한다. C21I wrapper가 먼저 optimized_adapter 또는 NumPy를 import하면 native path가 원 정책에 따라 거절된다. **fresh process에서 pinned private H runner를 먼저 load**하여 원 guard와 thread 설정을 실행하고, 그 다음 C21I callable을 주입해야 한다. flag를 False로 덮어써서 해결하지 않는다.

private load 뒤 H runner의 run_rust_reference binding 등 필요한 좁은 binding만 바꾼다. 원 canonical H module, reference_tau source, 이미 다른 작업에 사용 중인 sys.modules를 전역 교체하지 않는다. scope를 벗어나거나 예외가 발생하면 restore하는 것이 검토하기 쉽다. 병렬 job이 1이라는 원 계약을 유지한다.

H verify_own_source의 실제 runtime 8개 검사는 계속 실행한다. C21I runner/optimized adapter/보조 runtime/설정 manifest의 before/after identity를 더하고 그 전체 실행 closure를 JOB_RECEIPT.source_identity에 포함한다. C21I entrypoint를 실행하면서 H source만 확인한 receipt는 불충분하다. H bridge build를 그대로 사용한다면 build source 3개는 실제 H Cargo/lock/main.rs와 일치해야 한다. 새 block companion compile receipt는 그 별도 source·binary를 가리켜야 한다. 실행하지 않은 companion을 주 bridge 실행 identity에 합쳐 성공으로 표시하지 않는다.

base와 fd_half parent는 동일한 C21I runtime/source, fixture, method, native owner/binary, bridge build/binary, scales와 최적화 옵션을 확인한다. fd_relative/time_fd_fraction의 지정된 1/2 변화만 variant로 허용하고 다른 구성을 섞지 않는다. 실행 전후 parent receipt와 payload를 다시 확인한다. cache on/off 비교도 비교할 옵션을 실제 receipt에 기록한다. 완료 status를 옵션 없는 H receipt에서 복사하지 않는다.

NCP 전달은 최신 publication receipt의 실제 published content commit으로 시작하는 기존 guard를 보존한다. 현재 publication 차단을 해제하려고 status=PUBLISHED guard를 제거하지 않는다. local 제조 validation은 명시적으로 local 제조 scope로 기록한다. 현재 NCP 자원 조회·할당·locked compile·native 실행은 다른 상태 항목이며 이 검토가 대신하지 않는다.

## 6. 변경 의존성에 맞춘 acceptance 검사

아래는 **필요한 의미적 scenario**다. 행 수를 새 test 통과 수로 주장하지 않는다. 기존 C21H 유효 검사와 중복하는 내용은 source identity가 유지되는 한 재사용하고, 새 cache/vector/private-injection 경로에 걸리는 assertion만 새 focused test로 둔다.

| Scenario | 좁은 확인 내용 |
|---|---|
| reduced vector Jacobian | Y=0의 G=2와 Y>0의 G=4, 여러 active/inactive cohort에서 원 callback과 모든 성분 비교; passive 열/tau-tau exact zero와 full ledger 행 유지 |
| 연산 순서 | bitwise 동등성을 먼저 검사하고, 다르면 max absolute/relative/ULP와 성분 위치 기록; tolerance 비교를 bitwise PASS로 쓰지 않음 |
| domain/corner | 이미 cached인 상태 뒤 잘못된 t, nonfinite/shape/state, endpoint clamp, 짧은 cell 경계를 요청해 원 guard가 여전히 거절/허용하는지 확인 |
| exact key | 같은 값 복사본은 hit, t 또는 한 physical 성분의 1 ULP/부호 bit 변화와 ledger 변화는 miss; 다른 cell/provider/closure에서는 이전 값이 나오지 않음 |
| cache ownership | caller가 입력/반환 배열을 수정해도 저장 key/value가 오염되지 않음; 실패와 nonfinite 반환은 저장되지 않음 |
| provider budget/lifecycle | 고정 deterministic counter stub에서 실제 calls만 줄어듦; miss는 원 actual-call cap, expired-hit는 deadline, closed/dead-process hit는 lifecycle로 실패; unknown/stateful provider admission 거절 또는 명시적 off |
| callback 순서 replay | 같은 저장 RPC request sequence를 baseline/vector-only/vector+cache에 replay하고 응답값·FD node·원 callback count·hit 위치를 비교 |
| original diagnostics | cache on/off의 min_internal_tau, accepted tau/log-survivor, final full state/ledger와 물리 수지 의미 유지; 실제 calls와 result counter 일치 |
| runner import/source | 원 NumPy early-import guard, thread=1, H+I before/after source drift, 실제 build source, variant identity, create-only output, 실패 receipt 유지 |
| FD parent | 다른 I source/config/method/fixture/binary 또는 변조된 raw는 parent로 거절; 올바른 COMPLETE base만 사용 |
| 짧은 full trajectory | 같은 새 bridge binary·같은 제조 입력·controls·환경에서 H baseline과 I를 backend별로 비교; callback-only replay를 solver 실행으로 표시하지 않음 |

Rust block solver는 이론 보고서의 Schur와 full-space residual 검증을 사용한다. G=2/G=4, σ=0, 여러 finite positive/negative shift, singular/invalid 구조의 명시적 오류를 focused로 확인한다. 행렬 RHS·full residual의 크기를 스케일해 서로 비교하고, singular를 작은 pivot floor로 통과시키지 않는다. 실제 검증되지 않은 대역폭 또는 adaptive API를 가정하지 않는다.

기존 H gas/time FD source가 unchanged이고 새 assembly의 원 callback 응답이 bitwise 동일한 범위는 그 기존 검증을 재사용할 수 있다. 새 rounding 차이 또는 FD 경로 변화가 발견되면 영향받은 base/fd-half만 추가한다. C21F 56/C21G 35/과거 native 행렬의 전체 재실행을 이번 변경의 필수 gate로 만들지 않는다.

## 7. 성능 측정과 판정

### 7.1 세 층을 분리한다

첫 층은 assembly kernel이다. baseline과 vector-only를 동일한 이미 검증된 intermediate 입력으로 비교하면 cohort loop/임시 배열 제거 비용을 분리할 수 있다. 이 값은 RHS 또는 native 가속률이 아니다. 실제 제조 M=9,G=2를 먼저 사용하고 더 큰 M 또는 G=4는 별도 synthetic scale-up label을 둔다. 현재 reference max_cohorts=128 등의 원 지원 범위를 넘긴 성능 주장을 하지 않는다.

둘째 층은 callback replay다. 기존 raw의 정확한 request 순서를 source-pinned 원 RHS closure와 같은 제조 provider에 재생한다. baseline, vector-only, vector+cache를 구별한다. request order 자체가 고정되어 있으므로 controller 비용을 포함하지 않으며 새 과학 궤적이 아니다. 실제 원 RHS 호출, 원응답 동등성, FD node, Python CPU/elapsed time, allocation peak 및 trace size를 측정한다. JSONL log wrapper bytes와 실제 wire bytes를 구별한다. profile hook과 tracemalloc은 비용을 바꾸므로 primary timing에 섞지 않고 별도 진단 row로 기록한다.

셋째 층은 full 제조 solver 실행이다. 같은 새 binary SHA와 toolchain/build receipt, 같은 fixture/scales/rtol=2e-11/alpha=2e-14/max_step_divisor=8, worker=1을 사용한다. H baseline과 I를 각각 새 create-only output에 실행하고 accepted/rejected·fallback·실패·RPC·원 RHS·wall 전체를 포함한다. 새 환경/새 binary의 I 시간을 옛 환경 H 기록과 나눠 성능비로 쓰지 않는다.

### 7.2 Cold/warm과 실제 반복값

새 process+import+handshake+output 시작의 cold 비용은 전체 job의 구성 요소로 남긴다. callback의 warm 반복은 setup을 이미 한 조건이라는 것을 적고 setup bytes/time을 버리지 않는다. H run_segment는 cell마다 Rust process를 새로 만들므로 한 native persistent process와 세 Rust cell process의 비용을 혼동하지 않는다. paired 순서를 미리 정해 번갈아 실행하고 원시 반복값을 모두 보존한다. 반복 수·pre-warm·batch 길이는 timing을 본 뒤 유리하게 고르지 않는다. 실패나 timeout은 제거하지 않고 총비용과 실패 row에 포함한다.

소규모 비교에서 median/IQR/min/max와 paired ratio를 보고할 수 있다. 너무 짧은 함수는 여러 호출을 한 batch로 묶되 실제 호출 수와 total duration을 기록한다. hit cache를 무조건 warm-hit만 반복하면 저장 request sequence에서 나타나는 miss/FD 비용을 감추므로 replay와 별도로 label한다. CPU affinity는 독점 할당 증거가 아니며 현재 환경/부하/사용 worker를 실제 기록한다. 작은 n=26에서 stage/job thread 가속을 가정하지 않는다. NumPy 2.3 thread safety 및 SciPy 1.17 BDF 공식 문서와 기존 vectorization 원전은 앞 보고서에서 회수한 근거를 재사용한다.

### 7.3 기존 raw의 예측과 새 측정의 구별

저장 H 제조 base raw에서 동일-op request 반복은 없고, 교차 op base 재사용 여지가 관측됐다. 이전 분석의 예측은 VigilODE 원 RHS 423 중 51개, Diffsol 74 중 3개의 제거다. 실제 구현의 cache 크기·교체정책·guard 및 controller 응답이 같을 때 새 counter로 확인할 항목이다. 예상 제거율은 속도비가 아니다. Diffsol의 기존 Rust exact dense-J cache는 이미 있으므로 이번 Python cache의 이익과 중복해서 세지 않는다.

벡터화가 rounding을 바꾸면 controller trajectory와 call count도 바뀔 수 있다. 그러면 원래 정확도 설정에서의 출력·수지·accepted trace 차이를 먼저 평가하고 동일 tolerance 의미의 wall 비교를 보고한다. cache-only가 정확한 동일 값 재사용인데도 deterministic 같은 binary의 궤적이 바뀐다면 값/입력 오염이나 숨은 provider state를 조사한다. 실패를 tolerance 완화로 성공 처리하지 않는다.

## 8. 현재 상태와 다음 독립 검토

| 축 | 이 문서에서 완료한 것 | 남은 것 |
|---|---|---|
| 실행 | source 기반 purity·운용 계약 검토, owner source Git blob 5/5 | candidate final diff, focused 결과/raw, 새 binary full 제조 비교, native NOT_RUN |
| 게시 | 게시 상태를 새로 만들지 않음 | parent의 실제 GitHub ref/PR/provider ACK 확인 |
| 백업 | 이 작업의 새 파일을 독립 scratch 산출물로 작성 | parent의 create-only GitHub/세 저장처 전달·영수증 |
| DAG | 기존 근거 → 값/guard/key 계약 → 구현 → focused/replay/full 제조 → 성능 판정의 의존성 정의 | 실제 PASS/FAIL과 source SHA에 따라만 노드 승격 |

최종 independent review는 이 계획 자체를 PASS 근거로 세지 않는다. 구현된 최종 source/diff, 실제 test/benchmark raw, identity closure를 읽어 미충족 항목을 구체적으로 지적한다. native 수렴·전역 오차·Full48 등 기존 HOLD는 유지한다. global_error_bound=null.
