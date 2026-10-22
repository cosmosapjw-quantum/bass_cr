# C22D sandbox 최적화: 동일 물리·동일 FP64 순서의 최소 구현

## 결과와 채택 범위

**원 C22C의 77개 RHS 성분과 유한 CCC provider를 raw-byte 수준에서 보존하는 시제품을 완성했다.** 실제 변경은 같은 상태의 `fields()` 계산을 3회에서 1회로 줄이고, J0/J1/J2에 공통인 Taylor term을 한 번 계산하는 것이다. 저장 C22C 상태24점, provider 온도197점, moment 인자304점에서 바이트 표현이 일치했다. 부호 있는0도 비교했다. 원 소스·원 raw 불변을 전후 SHA로 확인했고, 기존 ODE 재실행0·신규 cosmological ODE0이다.

생산 후보: `optimized_kernel.py`, SHA256 `f0451a7349fa4682d17435336a3d3c413409fdbf442b44330eb008d33f7a8bf6`. 부모가 새 C22D 모델로 복사하고 그 파일을 별도 source freeze해야 한다. 이번 검증은 기존 C22C 물리에 대한 동등성이다. 부모의 새 collisional-ionization·에너지 registry 보정·새78-state 모델까지 검증한 것으로 해석하지 않는다.

측정 중앙값은 개선을 보였지만 실행시간 변동이 크다. 짧은 provider paired 실험에서는 전체시간비가0.880이므로 일관된 속도 향상을 입증하지 못했다. **이번 채택 근거는 정확히 같은 연산을 중복하지 않는 구조와 바이트 동등성이다. 안정적인 wall-time speedup은 OPEN이다.**

## 1. 물리 및 수치 계약

이 하위작업은 non-tilted LRS, full Frobenius norm, signed amplitude와 scalar norm 및 cancellation의 구분을 유지한다. 21종 population 중 n/T의 초기0은 선언된 invariant inventory다. 지원되지 않는 isotope/rate를0으로 채우지 않는다. Atomic gas의 응력 closure는 isotropic이고 anisotropic matter stress는 별도 nonbaryonic Vlasov다.

C22C의 원 물리는 두 CCC 표의 finite piecewise-linear cross section을 Maxwell 평균하고 H1 1s→2s/2p 에너지10.20435eV를 즉시 escaping-radiation ledger로 넘기는 것이다. 원래의 table endpoint, channel multiplicity, SI→cm³/s 변환, finite log rate, 실제 float64 underflow flag, unsupported-species refusal 및 conditional-tail semantics를 보존했다. Physical high-energy tail·다른 excited state·isotope·line trapping의 coverage는 추가하지 않았다.

FP64와 각 entry의 누산 순서는 고정했다. C22C의 독립 rate gate2e-10(log10 절대), moment gate2e-12(상대)를 그대로 재사용했다. 기존 trajectory acceptance gate2e-7은 변경하지 않았고 이번에는 trajectory 비교를 수행하지 않았다. `global_error_bound=null`이다.

## 2. 식에서 코드로

유한 구간 `[E_i,E_{i+1}]`에서 `t=(E-E_i)/h_i`, `y=h_i/(k_B T)`이면

\[
J_n(y)=\int_0^1 t^n e^{-yt}\,dt,
\qquad
J_n(y)\simeq\sum_{k=0}^{18}\frac{(-y)^k}{k!\,(n+k+1)}\quad(y\leq1/2).
\]

원래 C22C는 n=0,1,2마다 `term_0=1`, `term_k=term_(k-1)*(-y/k)`를 반복한다. term은 n에 의존하지 않는다. `moments_ordered`는 term sequence를 한 번 계산하고 각 n에 원래와 같은 `term/(n+k+1)`를 같은 k 오름차순으로 더한다. term의 FP64 recurrence가 같고 각 value의 초기값·나눗셈·덧셈 순서가 같으므로 entry별 연산 graph가 보존된다. 새 fitted coefficient·T-grid interpolation·rounded-temperature cache는 없다. 빈 branch만 계산을 생략한다. y>1/2의 incomplete-gamma 식도 그대로다.

Positive endpoint basis 역시 그대로다:

\[
w_L=E_i(J_0-J_1)+h_i(J_1-J_2),\qquad
w_R=E_iJ_1+h_iJ_2.
\]

Cross section을 `sigma_left*w_L + sigma_right*w_R`로 더하고, threshold exponential factor를 log-rate로 분리하는 원래 연산 순서를 유지한다. 하강하는 cross-section 구간에서 큰 polynomial 계수끼리 빼는 새 표현을 도입하지 않았다.

`c22a_rhs_from_fields`는 원 C22A `rhs`에서 `q=fields(eta,y)` 한 줄만 호출자로 옮긴 식이다. kinetic angular-moment loop, photo/RR event loop, 각 species 및 thermal/ledger update 순서를 그대로 복사했다. `c22c_rhs_from_fields`는 A 기여→Compton gas/bath 기여→C22C excitation gas/counter 기여 순서로 쌓는다. `q`는 동일한 `(eta,y)`에서 방금 계산한 dictionary여야 한다. cross-call mutable cache는 만들지 않는다.

| 식/계약 | 시제품 API | 동등성 조건 |
|---|---|---|
| J0/J1/J2 공통 Taylor term | `moments_ordered(y)` | 같은 FP64 입력·switch·k 순서·누산 |
| finite Maxwell 평균 | `OptimizedExcitation(provider, module)` | 원 표/상수/positive endpoint basis 유지 |
| atomic/kinetic prefix | `c22a_rhs_from_fields(a, eta, y, q)` | q가 같은 현재 상태에서 나온 값 |
| C22C 전체77 RHS | `c22c_rhs_from_fields(c, eta, full77, q, excitation_provider=...)` | A→B→C 기여 순서·원 ledger 유지 |
| 새 q를 계산하는 wrapper | `c22c_rhs_shared_fields(...)` | fields 실제 호출1회 |

## 3. 고려한 대안과 결정

* **공통 term + empty-branch skip:** 채택 가능. 각 entry의 연산 순서를 보존했고 strict bytes 비교가 PASS다.
* **fields 한 번 계산:** 채택 가능. 실제 instrumentation에서3→1회이며 24개 saved-state RHS의77성분이 동일하다.
* **Horner polynomial:** 소스에 비교 후보로 보존하고 생산에는 사용하지 않는다. 원 급수와 같은 degree18 및 switch이며 작은 y에서 alternating-series remainder는 `y^19/[19!(n+20)]` 이하이지만, FP64 누산 순서가 달라진다. 실제 moment 상대차이최대4.23244e-16, rate log10 차이최대1.77636e-15가 관찰되었다. 작은 차이를 근거로 잠긴 수치계약을 완화하지 않았다.
* **Passive ledger 분리:** 이번 production에서 보류한다. 물리상태 x와 ledger L은 `x'=f(x), L'=g(x)`의 block-triangular 구조지만 기존 adaptive error control에는 L도 포함된다. 단순히 L을 제거하면 solver 오차계약이 바뀐다. 후속 exact stage quadrature 또는 Jacobian block implementation은 별도 error-control 검증을 필요로 한다.
* **Isotope quotient·equilibrium elimination·rate interpolation:** 이번 변경에 도입하지 않았다. 새 CI가 isotope coupling/coverage 조건을 바꿀 수 있어 부모의 새 계약에서 결정해야 한다.

## 4. 실제 검증 및 실행량

v1 finite gate10개가 PASS했다. 일반 수치 equality가 signed-zero 차이를 놓칠 수 있어, 이 결함만 보완하는 후속검사를 실행했다. dtype·shape·C-order bytes를 직접 비교했으며 moment304점, provider197온도, saved RHS24점 전부 일치했다. 바이트 gate는 시간 성능과 독립적으로 판정했다.

기존 독립 Decimal85 moment oracle와 Decimal50 rate oracle는 저장된 값을 읽어 새 구현을 비교했다. 그 oracle를 다시 생성하지 않았다. 원자료 재감사나 기존 trajectory 재적분은 수행하지 않았다. changed adapter의 unsupported D/full-rate/boolean T/out-of-domain 거절, excitation OFF일 때20001K의 원 부모 영역 유지, 선언 invariant derivative0도 확인했다.

실행량:

| 실행 | 실제 호출/비용 | ODE |
|---|---|---|
| v1 finite RHS gate | 76 RHS calls | 0 |
| v1 matched block timing | provider5076 calls, RHS2052 calls, warm-up 포함 | 0 |
| v1 전체 | 69.042950s wall / 65.369842s CPU | 0 |
| 표현 비교 보완 | RHS72 calls, provider394 calls, moment grid304 | 0 |
| adjacent paired timing | provider168 calls, RHS336 calls, warm-up 포함 | 0 |
| 보완 전체 | 17.570030s wall / 17.022407s CPU | 0 |

v1은 7개 block round, 각 provider round240 calls/variant, RHS round96 calls/variant이며 variant 순서를 교대했다. 보완 실험은 입력별 인접 baseline/candidate2 calls씩,3회,12입력으로36쌍/variant다. 초기 finite provider/scalar validation 호출들은 위 timing 횟수와 구분되며 상세 grid는 JSON에 있다.

자원은 affinity0..8, quota8 CPU(`cpu.max=1600000 200000`), memory8GiB를 실제 확인했다. cooperative registry의 활성 JSON이 없음을 읽고 부모로부터CPU3를 배정받았다. 실행 중 affinity는{3}, 실제 native thread1이었다. CPU55는 가용 affinity에 없으며 부모 coordinator는 허용된CPU0를 사용한다. 외부 host CPU를 독점했다고 주장하지 않는다. 원 runtime·table·saved raw의 전후 SHA는 동일했다.

## 5. 측정된 성능과 한계

시간비는 항상 `baseline wall time / candidate wall time`이다. 1보다 크면 해당 표본에서 candidate가 빠르다. P10–P90은 측정분포이며 confidence interval이 아니다.

| 변경 | v1 block 중앙시간비 | 인접쌍 ratio 중앙값 | 인접쌍 P10–P90 | 인접쌍 전체시간비 | candidate가 빠른 쌍 |
|---|---:|---:|---:|---:|---:|
| ordered | 1.449406 | 1.424442 | 0.348313–5.939710 | 0.880017 | 25/36 |
| shared_fields | 1.457664 | 1.315705 | 0.466299–4.252758 | 1.878615 | 25/36 |
| shared_fields_and_ordered | 2.204020 | 1.287730 | 0.675978–3.283687 | 1.375219 | 26/36 |

CPU affinity와 단일 native thread를 맞췄지만 환경 변동이 충분히 작지 않다. 특히 provider의 paired total ratio는0.880으로 median ratio와 다른 방향이다. 따라서 `2.204× RHS speedup`을 일반 결과로 홍보하면 과장이다. 정확한 진술은 **v1 block 표본에서 결합 RHS 중앙시간비2.204를 측정했고, 인접쌍 실험에서는 median1.288/total1.375였으며 실행시간 향상의 재현성은 미확정**이다. 전체 ODE·campaign 속도, 62→33 대수축약의 speedup, 물리 coverage 향상은 측정하지 않았다. 추가 noisy microbenchmark를 반복하지 않고 이 한계를 보존한다.

그림 `OPTIMIZATION_EVIDENCE.png/.pdf`는 paired timing의 불확실성과 ordered/Horner residual 차이를 보여 준다. 오른쪽의1..1e8K는 finite provider 수치영역이고, 녹색1..20000K만 C22C active selector다. 이를 전체 물리 rate의 유효온도로 해석하지 않는다.

## 6. 부모 통합 및 출처 pin

부모의 새 모델은 `q=self.fields(eta, full)`를 한 번 계산한 뒤, **원 C22C model object와77-state prefix**를 `c22c_rhs_from_fields`에 전달할 수 있다. 그 뒤 새 CI population/thermal/event-ledger 항을 별도로 더한다. default `OptimizedExcitation`은 ordered kernel을 사용하며 Horner를 선택하지 않는다. 새 energy registry와 source support를 바꾼 새 모델은 자체 conservation·coverage·새 run validation을 통과해야 한다.

원 execution source identity: `e27e8506473833c6265343406b378bb2e8e260c2e8df6b5ab8537c5d7dfa904d`. 원 C22C excitation source SHA: `76f7a4ff3b731ac2e84e5631c07501412c5fc6f92d1759f2ce5951a4e52e3938`. 실제 비교에 사용한 모든 직접 소스·표·oracle pin은 `SOURCE_FREEZE.json`, saved history pin은 `FINITE_CHECKS.json` 및 `REPRESENTATION_AND_PAIRED_TIMING.json`에 기록했다. 이 텍스트의 근거는 같은 디렉터리의 실제 결과 파일이며 외부 rate의 추가검증을 주장하지 않는다.

## 7. EXECUTION | PUBLICATION | BACKUP | DAG

| 축 | 이 하위작업의 실제 상태 |
|---|---|
| EXECUTION | COMPLETE_SCOPED: 최소 구현, finite gate, 표현 gate, matched microbenchmark 완료. old/new cosmological ODE0. |
| PUBLICATION | 부모 통합·publication package 대기. 이 agent는 외부 PR/branch를 갱신하지 않았다. |
| BACKUP | 부모 release/backup package 대기. 자체 외부 ACK나 삼중 백업 완료를 주장하지 않는다. |
| DAG | ordered kernel 및 shared fields는 scoped integration 가능. Horner production HOLD. stable wall-time speedup OPEN. |

Full thermochemical/radiative energy closure는 OPEN, full nuclear high-energy 및 general triaxial/tilted/polarized CMB는 HOLD다. 외부 REI220/BASS180 compact33 mirror와 이 C22C source/ensemble을 합치지 않는다. 접근할 수 없는 대화 및 회수되지 않은 원 nuclear PNG를 읽었다고 주장하지 않는다. 사용자 최신 요청과 지정된 physmath workflow1.0.0/approval0.2 및 이번 명시적 하위작업 범위를 우선했다. 실제 노출 skill1.3.0과 attached historical protocols의 충돌하는 범위 지침은 자동확장 근거로 쓰지 않았다.
