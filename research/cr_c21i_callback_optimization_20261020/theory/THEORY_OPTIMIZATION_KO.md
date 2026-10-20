# C21I: 광학깊이–가스–장부 구조의 비용 축소와 구현 계약

기준일: 2026-10-20 UTC. 대상은 `bass_cr`의 C21H 광학 어댑터이며, 여기서 채택하는 물리식·event cell·오차 척도는 C21H와 같다. 이 보고서의 실행은 복원된 제조 JSONL의 구조 판독, Wolfram 대수 검산 및 독립 유리수 검산이다. 새 ODE 적분·native chemistry 실행·성능 benchmark는 이 문서의 결과에 포함하지 않는다.

## 1. 확보한 결과와 구현 우선순위

**현재 어댑터에서 먼저 줄일 수 있는 것은 광자 cohort별 Python 반복과 같은 평가점의 중복 원 RHS 호출이다.** `CellCallbacks.jacobian`은 전체 `(M+19)²` 영행렬을 만들고, cohort마다 `event_fractions`와 heat reduction을 호출한 뒤 Y=0 축소와 좌표 scaling을 한다. 같은 산술을 cohort 축에 대해 배열 연산으로 수행하고 처음부터 실제 적분 차원의 행렬을 채울 수 있다. 가스 열의 물리 영역 내 차분, 15개 장부, 원 RHS 함수와 event 순서는 유지한다.

보존된 제조 JSONL에서는 세 cell 각각에서 VigilODE의 모든 accepted base가 `jacobian → rhs → partial_t`의 같은 binary64 `(t,y)`를 사용했다. 같은 operation 자체의 반복 요청은 없었다. 그러므로 새 cache의 우선 대상은 cross-operation **원 RHS base 값**이다. Diffsol의 같은 `(t,y)` dense Jacobian cache는 이미 C21H Rust에 구현되어 있다. 이를 새 개선으로 세지 않는다.

Schur 소거는 C21H 이론 식 (5)를 재사용한다. 이번에는 그 식을 전체 error norm·장부 복원·구조화 JVP·비자율 clock 확장·실제 통신/행렬 구조에 연결했다. Schur의 직접 연산량은 G와 장부 수가 고정될 때 M에 선형이다. 실제 backend의 dense solve 교체 여부는 해당 API와 새 residual/benchmark 증거에 따라 판정한다.

## 2. 정의·가정·차원

독립변수는 `x=ln(a)`, 상태는 `u=(tau,g,ell)`이다. Tau M개는 무차원, 가스 g는 H/He 분율과 열에너지 w [eV/H], 장부 ell 15개는 사건 수/H 또는 에너지 eV/H다. Y=0에서는 두 He unknown을 정확히 제거하여 G=2, 일반 Y>0에서는 G=4다. 미분은 x에 관한 것이므로 적분기의 선형계 shift `sigma`는 무차원이다. `sigma`는 광속 c와 관계없는 수치 계수다.

한 cell에서 활성 cohort, fixture·source identity, native owner, 척도 D, dynamic index, clamp 규약을 고정한다. `N_i=A_i exp(-tau_i)`와 log survivor를 유지한다. 비활성·구조적 zero와 실제 underflow는 원 source의 규칙을 따른다. 원 가스/provider는 장부의 현재 값에 의존하지 않는다. 가스 차분이 성공한 노드에서만 그 열을 채택하며, 유효한 stencil이 없으면 명시적인 입력 실패다.

순서 `(tau,g,ell)`에서 구현이 제공하는 혼합 Jacobian은

\[
J=\begin{pmatrix}0&A&0\\ B&C&0\\ P&Q&0\end{pmatrix},
\quad A\in\mathbb R^{M\times G},\quad B\in\mathbb R^{G\times M},
\quad P\in\mathbb R^{15\times M}.
\]

Tau 열과 장부 영 열은 해석 구조이고, A/C/Q 중 가스 미분은 C21H의 represented-node 차분으로 얻는다. 아래 선형대수는 **제공된 이 행렬**에 대해 정확하다. 가스 차분의 truncation error가 사라진다는 주장은 하지 않는다.

## 3. Cohort 벡터화의 정확한 연결

`species[i,:]=-N_i k_i alpha`, `heat[i]=sum_s species[i,s](E_i-B_s)`로 둔다. Tau 열의 비영 행은

\[
J_{g_{\rm frac},\tau_i}=\mathcal S_Y(\mathrm{species}_i)/H,
\quad J_{w,\tau_i}=J_{\ell_{\rm photo\ heat},\tau_i}=\mathrm{heat}_i/H,
\]
\[
J_{\ell_{\rm photo},\tau_i}=\mathrm{species}_i/H,
\quad J_{\ell_{\rm photon\ work},\tau_i}=-N_iE_i.
\]

Y>0의 사건 사상은 `(s_H,(s_HeI-s_HeII)/Y,s_HeII/Y)`이다. Y=0에서는 H 행만 동적으로 남기고 두 He 사건의 구조적 0을 유지한다. 따라서 `(M,3)` rate 배열과 길이 M heat 배열로 모든 cohort 열을 채울 수 있다. 원래 `event_fractions`의 Y/domain 계약을 확인한 뒤 이 명시적 사상을 적용한다.

구현에서는 source-pinned RHS를 계속 호출하고, tau 부분의 행렬 조립만 바꾼다. `dynamic`으로 full-index→reduced-index 사상을 한 번 준비하면 `(M+19)²`의 full 임시행렬과 `np.ix_` 복사 하나를 줄일 수 있다. Matrix scratch를 재사용할 때는 매 요청에서 영 열과 비활성 열까지 완전히 초기화해야 한다. 반환 배열을 다음 요청이 덮어쓰지 않도록 소유권을 분리하거나 소비 완료가 보장된 경로로만 재사용한다.

NumPy 공식 문서는 broadcasting이 Python loop를 C의 array loop로 옮기는 근거와, 큰 중간 배열이 메모리 비용을 늘리는 반대 경우를 함께 설명한다. `out=`은 결과 배열 재사용을 허용하지만 overlap 판정에 따라 내부 temporary가 생길 수 있다. 이 연결에서는 cohort×cohort temporary를 만들지 않고 `(M,3)` 또는 `(G,M)` 크기를 사용한다. [NumPy broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html), [NumPy 2.3 ufuncs](https://numpy.org/doc/2.3/reference/ufuncs.html).

부동소수점 acceptance는 두 층으로 기록한다. 원소별 곱셈·나눗셈·3종 합산 순서를 유지하면 먼저 bitwise 일치를 검사한다. BLAS dot, FMA 또는 reduction 순서가 달라지면 binary64 차이를 수치로 남기고 기존 물리 tolerance에서 별도 비교한다. 단순히 수학식이 같다는 이유로 bitwise 동일을 선언하지 않는다.

## 4. Exact cache의 소유권과 의존성

한 `CellCallbacks` 객체는 하나의 고정 cell과 원 RHS closure를 소유한다. 다음 항목이 객체 생성 시 고정되고 실행 전후 source/fixture/native identity로 검증된다면, 성공한 원 RHS 값의 cache key는 `(t의 float64 bytes, physical u 전체의 float64 bytes)`로 둘 수 있다.

| 고정되는 의존성 | 이유 |
|---|---|
| source·reference SHA와 provider/native owner | 함수 자체와 가스 rates의 정체성 |
| fixture·birth/amount/energy 배열·Y | 광자와 가스 문제 정의 |
| cell lo/hi·활성집합·clamp corner 규약 | 같은 t의 실제 RHS 해석 |
| dynamic index와 양의 고정 D | physical state 복원과 반환 척도 |
| provider configuration·epoch 규약 | 같은 입력의 결정성 |

이 의존성을 매 hit마다 긴 문자열로 반복 hashing할 필요는 없다. cache를 해당 객체 수명에만 두고 frozen contract가 바뀌면 새 객체를 만들면 된다. 객체가 다른 cell·fixture·provider에 재사용되면 위 항목을 모두 key/invalidation에 넣어야 한다. t 대신 clamped epoch만 key에 넣는 축약이나 장부를 key에서 제거하는 축약은 별도 함수 의존성 증거가 있어야 하므로 첫 구현에서는 전체 physical u와 actual t를 유지한다.

Cache는 성공한 finite 결과만 보관한다. 예외·timeout·부분 반환을 cache하지 않으며, 실패를 재시도 성공으로 바꾸지 않는다. 출력은 caller의 mutation으로 오염되지 않게 보호한다. `np.array_equal`는 signed-zero의 byte 차이를 구별하지 않으므로 byte identity를 요구하는 cache에서는 `tobytes`/`to_bits`를 사용한다. Bounded LRU 또는 명시적인 base slot으로 메모리 상한을 정한다.

원 함수가 stateful/stochastic provider를 사용하면 같은 `(t,u)`의 결과 동일성이 자동으로 성립하지 않는다. 이번 채택 범위는 source/fixture가 고정된 결정적 RHS/provider이다. Call budget·raw counter는 `request`, `cache_hit`, `actual original RHS evaluation`, `actual native call`을 분리해야 한다. 비용 감소는 실제 호출 수가 줄어든 사실로 기록하고, cache hit를 native 실행 증거로 세지 않는다.

Jacobian cache에는 위 항목과 FD 제어값/실제 미분 규약이 추가된다. LU cache는 더 엄격하게 **제공된 Jacobian 전체 bytes와 shift sigma bits**, 행렬 차원·ordering·numeric backend identity가 모두 일치해야 한다. 동일 fixture라는 이유만으로 다른 accepted state의 Jacobian을 재사용하는 것은 approximate method 변경이다.

## 5. JVP와 Schur 소거: 장부와 error norm을 유지한 선형 비용

임의 `v=(v_tau,v_g,v_ell)`에 대해

\[
Jv=\begin{pmatrix}Av_g\\Bv_\tau+Cv_g\\Pv_\tau+Qv_g\end{pmatrix}.
\]

따라서 `v_ell`은 곱에 기여하지 않지만 결과의 장부 성분은 남는다. Dense n² 형식을 만들지 않고 A/B/C/P/Q를 전달하는 protocol 또는 같은 프로세스의 구조화 저장을 사용하면, 고정 G≤4,L=15에서 저장과 matvec은 O(M)이다. 현재 `C21H_V1`는 dense JSON 행렬을 주고받으므로 이 통신 절감에는 protocol/backend의 명시적인 새 구현이 필요하다. 현재 Rust Diffsol은 dense J를 exact `(t,y)` cache에 저장한 후 row dot을 수행한다.

선형계 `Wk=b`, `W=I-sigma J`의 첫 블록행은

\[
k_\tau=b_\tau+\sigma A k_g.
\]

이를 둘째 블록행에 대입하면

\[
S k_g=b_g+\sigma B b_\tau,
\quad S=I_G-\sigma C-\sigma^2BA.
\]

마지막 블록행으로

\[
k_\ell=b_\ell+\sigma P k_\tau+\sigma Q k_g
\]

를 복원한다. 이 세 식을 W에 역대입하면 첫/셋째 잔차는 0이고, 둘째 잔차는 `S k_g-b_g-sigma B b_tau`이므로 0이다. 블록 Gaussian elimination의 단위 삼각인자를 사용하면 `det W=det S`도 성립한다. 따라서 S가 가역일 때 유일해가 일치하며, 그 조건은 W의 가역성과 동치다. S가 특이하거나 허용 residual을 만족하지 않으면 명시적으로 실패한다.

| 연산 | 구조화 비용, G/L 고정 전 |
|---|---|
| BA 및 S 조립 | O(MG²+G²) |
| S factorization | O(G³) |
| 한 right-hand side의 gas/tau solve | O(MG+G²) |
| 장부 복원 | O(LM+LG) |
| 구조화 저장 | O(MG+LM+LG+G²) |

Dense W의 factorization O((M+G+L)³)와 대비되는 직접 연산량이다. 현재 n=26에서 library call/allocation/protocol overhead가 이론 FLOP 감소보다 클 수 있으므로 속도 향상은 benchmark로 결정한다. Schur solve에는 full-space backward residual

\[
\eta=\frac{\|W\widehat k-b\|_\infty}{\|W\|_\infty\|\widehat k\|_\infty+\|b\|_\infty}
\]

를 기록한다. 분모가 0이면 잔차도 0인 영문제만 η=0으로 정의한다. 작은 η는 해당 선형계의 backward accuracy를 지지하며, ill-conditioning이 있을 때 작은 forward error를 보장하지 않는다. Norm/condition estimate·실패를 기록하고 silent fallback을 피한다.

고정 대각 `u=Dz`에서 `J_z=D^{-1}J_u D`, `b_z=D^{-1}b_u`, `k_z=D^{-1}k_u`이고

\[
(I-\sigma J_z)k_z=D^{-1}(I-\sigma J_u)k_u.
\]

물리 행과 열을 맞추어 저장하면 구조화 solve도 이 변환을 따른다. 장부를 선형 factorization에서 소거하는 것과 적분 state/error estimator에서 제거하는 것은 서로 다른 조작이다. 모든 accepted output, 장부 수지, 원래 n차원 WRMS는 유지한다. D>0와 `atol_i=alpha D_i`에서 각 성분 비율의 D가 약분되므로 C21H의 scalar-scaled norm 계약을 그대로 쓴다.

## 6. 보존된 실제 Jacobian과 통신비 구조

아래 값은 최종 C21H 제조 base들의 기존 `rpc.jsonl` bytes를 읽어 집계한 것이다. 입력은 Y=0,M=9,G=2,L=15,n=26이고 새 ODE 실행은 0회다.

| Backend / cell | RHS / J / F_x RPC | J 비영원소 | half-bandwidth | 한 행 최대 비영수 | 양방향 기록 bytes |
|---|---:|---:|---:|---:|---:|
| VigilODE / 000 | 72 / 9 / 9 | 33 | 25 | 5 | 119115 |
| VigilODE / 001 | 72 / 9 / 9 | 51 | 25 | 8 | 132314 |
| VigilODE / 002 | 72 / 9 / 9 | 69 | 25 | 11 | 144402 |
| Diffsol / 000 | 19 / 1 / 0 | 33 | 25 | 5 | 31165 |
| Diffsol / 001 | 22 / 1 / 0 | 51 | 25 | 8 | 38479 |
| Diffsol / 002 | 18 / 1 / 0 | 69 | 25 | 11 | 37225 |

총 30개 J에서 passive15 열과 tau–tau 블록은 정확한 0이었다. 세 cell에 걸쳐 cohort가 활성화되면서 nnz가 증가했다. 현재 ordering의 half-bandwidth25는 full dimension26에 근접하므로 PR73의 FixedWidth2 표현은 이 J를 직접 표현하지 못한다. 뒤쪽 장부와 앞쪽 cohort의 결합이 원거리 비영항을 만든다. 구조적 소거/JVP 쪽을 먼저 연결하는 근거가 된다.

양방향 기록 bytes는 JSONL 파일의 log wrapper를 포함하며 실제 pipe wire bytes와 다르다. 별도의 송수신 serialization/parse 시간 측정이 필요하다. 이 표는 protocol bandwidth를 추산하기 위한 원자료이고 solver wall-time 분해는 아니다.

VigilODE의 27개 accepted base에서 세 operation의 t/y bytes가 같았고, Diffsol은 cell당 하나의 RHS/J 공유점을 가졌다. 원 source의 `partial_t` 3개 초기 plateau를 제외하면, base 값을 충분히 유지하는 exact cache는 이 **보존된 trace와 동일한 callback 순서**에서 원 RHS 51회(423회 중)와 Diffsol 3회(74회 중)를 줄일 기회가 있다. 이는 예상 호출 감소이며 새 실행에서 확인해야 한다. 동일-operation 반복 요청은 0이어서 J cache hit율이나 LU cache 이득을 미리 기대할 근거로 쓰지 않는다.

원 raw identity와 matrix별 집계는 `raw/STORED_JACOBIAN_SUPPORT.json`, cross-op 목록은 `raw/CROSS_OP_REUSE_OPPORTUNITY.json`에 있다.

## 7. Nonautonomous RHS와 PR74/75 연결

Steinebach의 Rodas5P 원전 식 (1.2)에는 `h² gamma_i F_x` 항이 있으며, 현재 C21H는 explicit partial-time callback을 전달한다. 이를 없애고 현재 문제를 autonomous로 표기하면 다른 stage식을 계산한다. [Steinebach 2023](https://doi.org/10.1007/s10543-023-00967-x).

보조 독립변수 s를 두고 clock ξ를 상태에 추가하면

\[
\frac{d\xi}{ds}=1,\qquad \frac{dz}{ds}=F(\xi,z),\qquad
\widetilde J=\begin{pmatrix}0&0\\F_x&J\end{pmatrix}
\]

라는 autonomous identity-mass 시스템을 만들 수 있다. 초기 ξ=x_0를 두면 연속해에서 ξ=x_0+s다. 구조화 JVP는 `(0,F_x v_x+Jv_z)`이며, shifted solve는 `k_x=b_x`, `(I-sigma J)k_z=b_z+sigma F_x b_x`다. 이것이 PR74/75의 autonomous interface로 가는 대수적 사상이다.

그러나 그 API에 clock state를 추가하는 것만으로 adaptive trajectory·event landing·dense output·global bound 계약이 완성되지는 않는다. 각 stage의 ξ가 frozen cell 안에 있어야 하고, 원 clamp와 corner 규약을 유지해야 한다. 물리 error norm을 n에서 n+1로 평균하면 clock error가 0이어도 기존 norm을 `sqrt(n/(n+1))`배로 바꾸므로, clock을 물리 error norm에서 제외하거나 정확히 동일한 원 n차원 norm을 명시적으로 계산해야 한다. 현재 user tolerance를 그대로 유지하는 구현 의무다.

`residual-first`는 **유지한 같은 stage/state와 같은 방정식**의 현재 residual이 이미 종료 기준을 만족할 때 JVP를 생략하는 국소 결정이다. 새로운 stage, 다른 shift 또는 변경된 background에서 이전 residual을 읽어 생략하면 다른 알고리즘이다. C21H의 JSONL `SharedChannel`은 mutex 한 개를 통해 요청하므로 stage worker를 늘리기만 하면 Python/native 요청은 직렬화될 수 있다. 실제 병렬화를 위해서는 thread-owned callback scratch, 독립 provider 채널·raw·예산 및 단일 full-space residual 조합을 구현해야 한다.

Rosenbrock–Krylov 문헌은 Krylov/Jacobian approximation과 시간 적분의 order conditions를 함께 다룬다. 따라서 일반 JVP를 공급한다는 사실만으로 임의의 basis truncation이 기존 Rodas5P의 accuracy를 유지한다고 채택하지 않는다. [Tranquilli–Sandu, SIAM J. Sci. Comput. 36 (2014), A1313–A1338; arXiv:1305.5481](https://arxiv.org/abs/1305.5481). SciSpace의 repository 메타데이터에는 2022 중복 항목이 있었으며 원 arXiv의 2013 제출/2015 개정과 2014 journal 출판을 우선한다.

## 8. Vectorization과 병렬 실행의 선택

Curtis–Niemeyer–Sung은 화학 RHS/Jacobian에서 SIMD/SIMT의 data layout과 vector width를 실제 비교했다. 재사용할 점은 어느 축에 독립 상태/종을 연속 배치하는지와 lane당 작업을 명시해 벤치마크하는 방법이다. 그들의 압력/부피 고정 combustion mechanism, pyJac 생성코드와 C21H의 외부 native RPC는 다른 입력 계약이다. 여기서는 해당 speedup 숫자를 C21H에 전이하지 않는다. [원 논문](https://arxiv.org/abs/1809.01029), [저자 공개 코드](https://github.com/SLACKHA/pyJac).

NumPy 2.3은 많은 연산에서 GIL을 해제하지만, worker가 독립 배열을 소유하는 경우를 권장한다. BLAS thread는 별도 설정이고 NumPy ufunc 자체의 기본 thread 수와 구분된다. SciPy 1.17.0 BDF 문서는 vectorized 함수가 FD Jacobian을 빠르게 만들 수 있지만 작은 상태 차원에서는 전체 실행을 느리게 만들 수 있음을 명시한다. 따라서 G=2의 네 FD 평가를 naive thread pool에 보내는 방식은 실제 overhead/IPC/native thread-safety를 먼저 측정해야 한다. [NumPy 2.3 thread safety](https://numpy.org/doc/2.3/reference/thread_safety.html), [global configuration](https://numpy.org/doc/2.3/reference/global_state.html), [SciPy 1.17.0 BDF](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.BDF.html).

선택 순서는 cohort 배열 조립 → 정확히 같은 RHS base 재사용 → 실제 structured JVP/Schur API 연결 → batch/stage/job 병렬의 worker 손익 측정이다. Native pilot의 기본 동시 job1/worker1 계약은 유지한다. 병렬 실험은 새 bounded contract가 생긴 경우에 그 입력 범위에서 실행한다.

## 9. 실제 검산과 근거 상태

| 항목 | 상태 | 범위 |
|---|---|---|
| C21H Schur 식 | derived, reused | S 가역 조건 아래 일반 블록 역대입 증명 |
| 구조화 JVP·clock augmentation·scaling | derived | 위 직접 유도, 같은 차원/norm 계약 |
| Wolfram context | SERVICE_ERROR | `Internal error`, 다른 tool 능력으로 확대하지 않음 |
| Wolfram evaluator | PASS_SCOPED with warnings | 8×8 Schur residual8개=0, determinant 차=0, JVP8개=0, clock9개=0, scalar ratio 차=0; `FullSimplify::cas` 경고 원문 보존 |
| 선택적 SymPy import | PACKAGE_MISSING | 현재 환경의 `ModuleNotFoundError`만 기록 |
| 독립 Python fractions | implementation-verified, PASS_SCOPED | G=2/4의 8개 유리수 shift 사례, full solve/Schur/JVP/clock 일치; scale3사례와 singular rejection |
| 기존 raw의 sparsity/요청 판독 | numerically checked | 보존된 제조 base6개 cell, J30개; 새 solver/native 실행0 |
| C21I 실제 최적화 속도 | unresolved | 구현 담당의 같은 입력·tolerance·worker benchmark로 판정 |

Wolfram에 보낸 원 코드는 `WOLFRAM_CHECK.wl`, 실제 응답은 `raw/wolfram_schur_scaling.json`에 있다. Fraction 검산은 `python3 verify_block_identities.py`로 재현하며 `raw/FRACTION_INDEPENDENT_CHECK.json`에 실제 결과가 있다. 기존 raw 파싱 중 JSON tuple-key 출력 실패 1회는 분석 스크립트의 serialization 문제로 보존하고 string-key 출력으로 교정했다. 과학 source나 기존 raw는 변경하지 않았다.

일반 블록 명제의 근거는 행렬 역대입 증명이며, 유한 유리수 예제는 그 구현·부호·ordering의 독립 검사다. 새 no-go나 새 stiff method를 주장하지 않으므로 NG1–NG7을 새 불가능성 채택에 사용하지 않는다. `global_error_bound=null`이다.

## 10. R1–R10 판정과 코딩 인계

| 단계 | 이번 작업 |
|---|---|
| R1 | C21H 동일 physics와 C21I 비용 축소 범위를 고정 |
| R2 | source-pinned adapter/theory/Rust와 기존 raw·SciSpace·Exa 원전 재사용 |
| R3 | exact block algebra와 FD Jacobian/숫자 성능 주장을 구별 |
| R4 | cohort vectorization, base cache, Schur/JVP, clock augmentation 후보 비교 |
| R5 | Schur/JVP/scaling/clock·norm 대응 유도 |
| R6 | Wolfram 역대입과 독립 Fraction row elimination, 부호·차원 확인 |
| R7 | 실제 저장된 J30개·cross-op 요청 판독; 새 native 실행 없음 |
| R8 | vectorization/base cache 우선 구현, FixedWidth2 직접 적용 보류; solver 교체에는 residual/API gate |
| R9 | 3–8절의 함수·key·소유권·norm·benchmark 계약을 구현자에게 전달 |
| R10 | 이 파일·원전/raw·reproducer·manifest로 보존; 최적화 diff 검토·benchmark는 후속 C단계 |

코딩 acceptance는 다음 결과를 실제 source/diff/raw로 확인한다: 원 RHS byte identity 유지, Y=0/일반Y 및 event/domain/underflow 경계, tau/passive/gas 열의 같은 입력 비교, cache off/on의 exception과 최종 출력/trace 동일성, counters의 실제 의미, full-space Schur/JVP residual, 같은 입력·허용오차·worker의 cold/warm 원시 시간과 메모리. native 실행과 성능 판정은 C21H의 제조 기록과 별도 상태로 유지한다.
