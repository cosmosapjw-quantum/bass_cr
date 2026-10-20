# C21J: 저장된 native 호출열에서 exact RHS cache를 판정하는 범위

작성일: 2026-10-20 UTC  
연구 단위: PR87의 새 native 반환을 입력으로 하는 고정 trace 진단과 callback 재현  
기존 실행 source: `fe6bbaec2de5032b938aed0713623b9618ba70e6`  
반환 문서 snapshot: `d3eaf596e46be4f994723fb742237a7399c290ed`  
native archive SHA256: `2722e479b6205015a68f1393b8c537d21e63201bb57efd3cf850fe74e4668de3`

## 1. 확보한 결과와 연구 위치

새 native 자료의 I 실행은 `vectorized`, cache capacity 0이었다. 저장된 RPC, 실제 FD nodes, native EVAL 요청·응답을 고정 source와 대응시켜 복원한 original-RHS 요청은 작업당 823회다. 기존 exact 경로와 같은 **셀별 full \((t,u)\) binary64 key, LRU16**을 적용하면 세 작업 각각 69회 적중, 754회 miss다. 7개 native 입력만 비교할 때의 100회 적중과 구분해야 한다. 이 수치는 고정된 유한 요청열에 관한 정확한 조합적 결과다. [근거 A]

Root가 수행한 callback replay attempt 01과 gate 보완 후 attempt 02에서는 I base trace에 H 원형, I vectorized, I vectorized_exact callback을 각각 적용했고, FD-half trace에 exact callback을 적용했다. 각 경우 저장된 callback 응답 472개, binary64 값 40,432개가 모두 일치했다. exact의 table-provider 조회는 823회에서 754회로 줄었다. 이 계산은 저장된 native 응답표를 읽고 기존 RHS와 callback을 계산했으며 새 native 프로세스와 새 IVP 적분은 각각 0회였다. 저장된 accepted states를 소비하여 재구성한 종단 물리량의 일치도 새 trajectory 적분을 뜻하지 않는다. [근거 B]

이 보고서는 기존 C21I의 일반 Schur 유도, vectorized Jacobian 유도, exact cache 구현과 제조 검증을 재사용한다. 새로운 내용은 native trace의 full-key 적중 집합, native-key 투영과의 관계, 완전한 callback 재현의 전제, 조건부 adaptive 동일성, 그리고 새 native 시간 자료를 사용한 비용 해석이다. 기존 비용식의 직접 재사용 위치는 `C21HI_CLOSEOUT_REPORT_KO_20261020.md`의 보존 본문 §4 “비용 구조와 새 cache가 줄이는 것”이다.

| 항목 | 현재 근거와 상태 |
|---|---|
| 기존 exact 구현 및 제조 focused 검증 | C21I의 고정 source·기존 증거 재사용 |
| PR87 native 실행 | H base, I vectorized base, I vectorized FD-half의 기존 실행 raw 재사용 |
| 실제 native exact 모드 실행 | `NOT_RUN` |
| full-key LRU16 기회 수 | 세 저장 trace에서 각각 69/823 |
| callback replay | 원 attempt 01 보존; gate 보완 후 attempt 02도 `PASS_SCOPED` |
| 재사용 가능한 evidence gate | attempt 02 완료; source 24개·return 60개 고정 pin 및 raw manifest admission, 독립 focused 16+6개 PASS |
| native exact 성능 | `NOT_EVALUATED`; replay timer는 native benchmark가 아님 |
| 전체 시간 가속 | `NOT_ESTABLISHED` |
| 과학적 trajectory 오차 상한 | `global_error_bound=null` 유지 |
| 이번 이론 단위의 native / IVP 호출 | 0 / 0 |

독립 검토 V1은 reusable gate의 pin authority 및 terminal 검사 두 결함을 찾았다. 신뢰된 기본 입력의 원 성공 결과는 보존했고, root가 gate를 보완한 뒤 attempt 02에서도 같은 수치 결과와 69회 적중을 얻었다. analyzer도 고정 archive의 payload manifest SHA256 `40d61253fb5535435373c07150ff554ff708796902076168e171fb1f9301125a`에 읽는 각 raw 파일을 연결하는 admission을 추가했다. 최신 analysis attempt 02는 세 job의 69/754 결과를 유지했다. 독립 검토 V2에서 replay 계약 16개와 analyzer admission 6개가 모두 PASS이고 C9-J1, C9-J2, C9-J3이 해당 source 버전에서 닫혔다. 최초 analyzer privacy 테스트가 manifest에 하나의 inventory entry만 있다고 가정해 실패한 기록도 보존했다. 실제 항목 3개를 모두 읽기 전에 거절하는지 검사하도록 테스트만 교정했으며 구현 결함으로 재분류하지 않았다. 현재 유효 결과와 V1의 역사적 finding을 구분한다. [근거 A–C]

## 2. source와 상태의 정의

현재 공통 IC 대조는 \(\Delta\ln a=10^{-4}\), 3개 event cell의 `FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT` 범위다. 입력의 producer source identity는 `PINNED_PR79_MD14_RATE_MANUFACTURED_3_ENERGY_GAS`이며 native 미시물리 호출 자체는 실제 기록된 Rust EVAL이다. 이 진단을 별도 MD14 native 12-cell fixture 실행으로 확장하지 않는다. 현재 양의 helium fixture에서는 \(M=9\)이고, 적분되는 물리 상태는 28차원이다. \(x=\ln a\)를 독립변수로 쓰고 다음처럼 나타낸다.

\[
u=(\tau_1,\ldots,\tau_M,\;g,\;L),\qquad
g=(x_{\mathrm{HII}},x_{\mathrm{HeII}},x_{\mathrm{HeIII}},w),\quad L\in\mathbb R^{15}.
\]

\(\tau_i\)는 광학깊이, \(w\)는 수소핵당 열에너지, \(L\)은 누적 photo/ci/rr/dr/escape/cmb/work/heat 장부다. native fixture의 \(Y=n_{\mathrm{He},0}/n_{\mathrm{H},0}=0.08130135170951498\)이다. 이 note는 다른 fixture나 \(Y=0\) 축약 상태의 실행 결과를 새로 주장하지 않는다. 현재 full key에서 “full”은 original RHS에 전달되는 전체 물리 적분 상태를 뜻한다. [근거 A; source S1–S4]

서로 다른 역할을 하는 세 표현을 구분한다.

| 표현 | 구성 | 용도 |
|---|---|---|
| RPC 입력 | \((t,z)\) | solver가 고정 diagonal scale을 적용한 좌표로 보낸 입력 |
| full RHS key | \((\operatorname{bits}_{64}(t),\operatorname{bytes}_{64,\mathrm{LE}}(u))\) | 셀 소유 exact cache; \(u=z\odot s\), 내부 FD 호출은 실제 물리 perturbed state |
| native EVAL key | \((a,n_{\mathrm H,0},n_{\mathrm H,0}Y,g_1,g_2,g_3,w)\)의 실제 ASCII 요청 | 비광자 native 미시물리의 입력; \(a=\exp(\operatorname{clamp}_c(t))\) |

C21I source는 `struct.pack("<d", float(t))`와 `np.ascontiguousarray(u, dtype="<f8").tobytes()`로 key를 만든다. 원 time을 clamp하기 전의 bits와 모든 물리 좌표를 포함한다. signed zero를 합치거나 허용오차로 rounding하지 않는다. nonfinite 값은 원 admission/domain 계약에서 거절된다. fixture, active cohort, 셀 경계, scale, dynamic index, reference source와 provider admission은 key 바깥의 **동결된 cache scope**다. 새 셀에는 새 cache가 생긴다. [S1, S2]

native key의 문자열은 동일한 고정 source가 일곱 float에 `.17e` 형식을 적용하여 만든 실제 요청과 비교한다. 단순히 사람이 읽을 자릿수로 반올림한 7-tuple 비교가 아니다. cache의 \((t,u)\) key와 native 입력의 더 작은 key는 목적과 정의역이 다르다. [S4]

## 3. 유한 요청열의 정확한 LRU 판정

셀 \(c\)에서 성공한 original-RHS 요청열을

\[
Q_c=(K_{c,1},\ldots,K_{c,n_c})
\]

라 하자. 각 셀 시작 시 cache는 비어 있고 capacity는 16이다. 적중 시 해당 key의 recency를 갱신한다. miss의 결과가 성공적으로 finite/shape 검증과 후행 guard를 통과했을 때만 저장한다. 실패 결과, 기한이 지난 결과, 다른 scope의 결과는 저장 대상이 아니다. 이는 기존 C21I 구현의 동작을 그대로 재사용한 정의다. [S1]

어떤 요청 \(K_j\)의 같은 셀 내 직전 동일 key 위치가 \(i<j\)라고 하자. \(i\)와 \(j\) 사이의 **서로 다른 key 수**를 reuse distance \(d_j\)라 하면,

\[
K_j\text{가 LRU16 hit}\quad\Longleftrightarrow\quad i\text{가 존재하고 }d_j<16.
\]

증명은 LRU가 최근 사용한 서로 다른 16개 key를 유지한다는 불변식이다. 직전 \(K_i\) 접근 직후 \(K_i\)는 가장 최근 항목이다. 이후 서로 다른 key가 16개 미만 등장하면 남아 있고, 16개째가 등장하면 퇴출된다. 같은 중간 key의 반복은 서로 다른 key 수를 추가하지 않는다. 이 불변식은 요청열 길이에 대한 귀납으로 성립한다. 새 ODE 적분이나 native 함수를 실행할 필요가 없다.

전체 요청열은 RPC의 `rhs` 요청 400개만 세어 얻을 수 없다. 각 Jacobian의 base와 gas FD 양쪽 node, 각 \(\partial_t\) callback의 base와 실제 time FD node까지 포함해야 한다. 저장된 derivative nodes의 표현 가능한 offset과 원 연산 순서를 재사용한다. 현재 trace의 확장 계수는 다음과 같다. [A; S1, S2]

| 셀 | original RHS 요청 | full-key hit | full-key miss | native-key hit | full hit의 역할 |
|---|---:|---:|---:|---:|---|
| 0 | 272 | 23 | 249 | 36 | rhs 12, partial_t base 11 |
| 1 | 279 | 23 | 256 | 28 | rhs 12, partial_t base 11 |
| 2 | 272 | 23 | 249 | 36 | rhs 12, partial_t base 11 |
| 합계 | 823 | 69 | 754 | 100 | rhs 36, partial_t base 33 |

H base, I base, I FD-half에서 각각 위 계수가 확보되었다.

전체 호출 계수도 원 callback 구조로 닫힌다. gas 변수 4개의 양쪽 FD를 쓰는 Jacobian 36개는 각각 base 1회와 node 8회를 호출한다. time callback 36개 중 셀 경계의 flat branch 3개는 RHS를 호출하지 않고, 나머지 33개는 base와 time node 2개를 호출한다. 따라서 현재 trace에서

\[
N_F=400+36(1+2\cdot4)+(36-3)\cdot3=823.
\]

적중 역할의 합도 \(36+33=69\)다. 이 계수 항등식은 이번 기록된 callback 순서를 설명하며 다른 adaptive 경로나 다른 FD branch의 보편적 적중률로 사용하지 않는다. 이번 finite-trace 적중률은

\[
h_{\mathrm{full}}={69\over823}=0.0838396111786148\ldots
\]

이다. “새 실제 native 호출을 69회 줄였다”가 아니라, baseline의 같은 요청열에 기존 exact cache를 적용할 때 **원 RHS 평가 69회가 생략되며 replay가 이를 실현했다**는 결과다.

## 4. native 입력 투영은 full cache hit의 상한을 준다

같은 셀 안에서 full key에서 native 요청 key로 가는 결정적 사상을 \(P_c\)라 하자. 여기서는 각 성공한 original-RHS 평가가 정확히 하나의 성공한 native EVAL과 대응하고, 그 순서가 모두 맞는다. 실제 비교는 작업당 823개의 native 요청 문자열에서 mismatch 0을 확인했다. [A]

**보조정리.** 위 조건에서 full-key 셀별 LRU16 hit가 일어난 baseline 인덱스는 동일한 baseline 호출열의 native-key LRU16에서도 hit다. native cache가 셀 경계에서 reset되지 않아도 이 포함 관계는 성립한다.

**증명.** full key가 위치 \(j\)에서 hit면 같은 셀의 이전 \(i\)에서 같은 key를 보았고, 사이의 full key 종류는 16개 미만이다. 같은 셀의 결정적 투영은 종류 수를 늘릴 수 없으므로 투영된 native key의 사이 종류 수도 16개 미만이다. 투영된 같은 key가 \(i\)보다 더 최근에 나타났다면 reuse distance는 더 줄어든다. 셀 밖 기록을 유지하는 native cache에서도 \(i\) 이후 이 최근 접근 관계는 유지된다. 따라서 native LRU16에도 해당 key가 남는다. □

그 결과 baseline 인덱스 집합에 대해

\[
\mathcal H_{\mathrm{full}}\subseteq\mathcal H_{\mathrm{native}},\qquad
69\le100
\]

이다. 현재 실제 결과에서는 native cache를 셀별로 reset해도, 작업 전체에서 유지해도 100회다. native-key-only 31회 중 4회는 광학깊이가 다르고, 27회는 광학깊이와 passive ledger가 함께 다르다. [A]

이 포함은 원래 baseline 요청열에 대한 관계다. 이미 full cache로 어떤 요청을 생략한 뒤 남은 native 호출열에 또 다른 native cache를 붙이는 이중 cache의 hit 수를 뜻하지 않는다. 또한 서로 다른 fixture·provider·scope를 허용하면 \(P_c\)의 전제가 달라지므로 해당 로그를 무조건 합칠 수 없다.

## 5. 7-input EVAL 일치가 full RHS 일치를 보장하지 않는 이유

동일 native 입력은 비광자 미시물리 결과를 재사용할 근거가 될 수 있다. full optical RHS에는 native 입력에 없는 광자 생존량이 들어간다. 현재 source에서 active cohort \(i\)의 생존량은

\[
N_i=A_i e^{-\tau_i}
\]

이며, \(A_i>0\)인 active cohort에 대해서만 이 표현을 쓴다. 구현은 \(\exp(\log A_i-\tau_i)\)를 계산하고, 구조적으로 비활성이거나 양이 0인 cohort는 정확히 0으로 둔다. underflow 보고를 유지하고 임의의 양의 floor를 넣지 않는다. 다음 식은 해당 source의 의존성을 밝히는 수학적 식이며 replay에서는 원 부동소수점 연산 순서를 그대로 사용한다. [S3]

\[
\begin{aligned}
E_i(x)&=q_i e^{-x},\\
k_{is}(x)&=\kappa\,c\,n_{\mathrm H,0}e^{-3x}\sigma_s(E_i),\\
r_{is}(x,u)&=N_i\,k_{is}(x)\alpha_s(g,Y),\\
L'_{\mathrm{photo},s}&={1\over H(x)}\sum_i r_{is},\\
L'_{\mathrm{heat}}&={1\over H(x)}\sum_{i,s}r_{is}(E_i-B_s),\\
L'_{\mathrm{photonwork}}&=\sum_i N_iE_i.
\end{aligned}
\]

고정된 \(x,g,n_{\mathrm H,0},Y\)와 같은 cell/fixture에서 active cohort \(j\)의 \(\tau_j\)만 \(\tau_j+\delta\)로 바꾸자. \(\delta>0\)이고 \(N_j,k_{js},\alpha_s,H>0\)인 허용된 채널을 고르면 native EVAL key는 그대로인데,

\[
\begin{aligned}
\Delta N_j&=N_j(e^{-\delta}-1)\ne0,\\
\Delta L'_{\mathrm{photo},s}
 &= {N_jk_{js}\alpha_s\over H}(e^{-\delta}-1)<0,\\
\Delta L'_{\mathrm{heat}}
 &=\sum_s(E_j-B_s)\Delta L'_{\mathrm{photo},s},\\
\Delta L'_{\mathrm{photonwork}}
 &=N_jE_j(e^{-\delta}-1)\ne0.
\end{aligned}
\]

gas photo-ionization와 thermal RHS도 이 광자율에 의존한다. 예를 들어 \(\delta=\log2\)이면 해당 cohort의 생존량과 이 cohort가 기여한 rate가 절반이 된다. 따라서 7-input key만으로 전체 RHS를 반환하는 대체 구현은 일반적으로 잘못된 함수가 된다. 이 반례는 현재 source에 대한 구체적 key 의존성 진단이며 새로운 strong no-go 성과로 채택하지 않는다.

**Passive ledger 값에 관한 교정.** 이 source에서 누적 \(L\)의 현재 값 자체는 RHS에 되먹임되지 않으므로 그 15개 Jacobian 열은 정확히 0이다. “장부값을 바꾸면 RHS가 달라진다”는 설명은 이 구현에서는 틀리다. 정확한 설명은 **광학깊이가 photon-dependent 장부의 도함수까지 바꾼다**는 것이다. 기존 full cache는 passive ledger까지 포함한 보수적인 key를 사용한다. 이 note는 key 축소나 새로운 native-level cache를 구현하지 않는다. [S1, S3]

차원도 원 물리 단위를 유지한다. \(c\)는 cm/s, \(n_{\mathrm H,0}\)는 cm\(^{-3}\), \(\sigma\)는 cm\(^2\)라서 \(k\)는 s\(^{-1}\)이다. \(\alpha,\tau,x,Y\)는 무차원, \(N\)은 수소핵당 광자수다. \(H\)는 s\(^{-1}\)이므로 \(r/H\)는 수소핵당 수의 \(d/d\ln a\) 도함수이고, \((E-B)r/H\)는 eV/H의 도함수다. \(k_B\)는 EOS의 eV/K 단위로 유지되며 natural-unit convention을 새로 도입하지 않았다. Wolfram의 단위 계산은 각각 Hz, 1, eV로 돌아왔다. [S3; 검산 W3]

## 6. 정확한 table replay의 계약

Python 공식 문서는 memoization을 같은 함수 인수에 대해 이전 계산값을 재사용하는 기능으로 설명하며, 부작용이나 시각처럼 호출마다 달라지는 결과를 가진 함수에는 부적절하다고 설명한다. 이는 일반적 동기를 제공한다. 본 프로젝트의 full binary64 key, frozen scope, live guard, copy 규칙은 Python 문서에서 따라오는 것이 아니라 고정 C21I source의 별도 계약이다. [P1; S1]

이번 replay의 비교 대상은 **저장된 callback의 모든 solver-relevant 수치 응답**이다. 다음 조건을 함께 요구한다.

1. **입력과 source identity.** source 파일, fixture, tolerance/scaling, native table, cell config, RPC, FD nodes, terminal result를 권위 있는 고정 snapshot에 연결한다. 임의의 빈 pin 목록으로 성공할 수 없어야 한다.
2. **완전한 성공 trace.** hello/config, 연속된 request/response ID, 성공 응답, 성공 terminal, EOF의 순서를 확인한다. 저장된 prefix를 완전한 성공 실행처럼 취급하지 않는다.
3. **native table 일관성.** 같은 실제 native 요청 문자열의 성공 응답이 모두 같아야 한다. 누락된 key, 충돌한 응답, 실패 protocol, nonfinite 값은 hard failure다. interpolation이나 새 native 호출로 빈칸을 채우지 않는다.
4. **원 response 해석.** 원 NativeMicro의 parser, field 수, density/EOS 및 ownership 검증을 재사용한다. 저장된 table provider와 실행 중인 native process의 admission은 별도 종류로 기록한다.
5. **실제 callback 경로.** 원 cell activation, clamp, physical scaling과 순서, analytic tau 열, 실제 gas/time FD node, 수치 배열 shape와 signed zero를 보존한다. 완성된 Jacobian이나 \(\partial_t\) reply를 원 값에서 복사해 정답으로 돌려주는 방식이 아니다.
6. **cache 의미.** cache scope가 고정되어야 하고, 성공값만 저장하며, 호출자에게는 별도 copy를 반환한다. readonly 저장본이 호출자 변형으로 바뀌지 않아야 한다.
7. **출력 비교.** rhs/Jacobian/\(\partial_t\)의 모든 수치값을 shape와 binary64 bytes로 비교한다. wire envelope를 별도로 검증하되 JSON의 공백 등 수치적으로 무관한 직렬화 모양까지 동일하다고 주장하지 않는다.

현재 duplicate native response disagreement는 0이고, 작업별 unique native request는 723개다. attempt 01 및 gate 보완 후 attempt 02는 원 RHS와 callback을 실제로 계산해 수치 reply가 같은 것을 보였다. immutable table에 대한 exact admission은 성공했지만 살아 있는 native process의 liveness, deadline, binary 검증을 이번 replay가 다시 입증한 것은 아니다. [A–C; S4]

## 7. 고정 replay와 adaptive 경로에 관한 조건부 정리

고정 replay는 solver가 다음 query를 선택하게 두지 않고 이미 저장된 query를 차례로 공급한다. 따라서 “replay가 성공했으니 모든 미래 adaptive 실행도 같고 빨라진다”는 무조건적 결론은 성립하지 않는다. 다만 아래의 조건부 동일성은 직접 증명할 수 있다.

solver의 완전한 수치 상태 \(S_j\)에 현재 상태, controller/history, method flags, 누적 수치량과 다음 event 결정에 필요한 상태를 포함하자. 다음 query와 전이는

\[
q_j=Q(S_j),\qquad S_{j+1}=\Phi(S_j,r_j)
\]

로 표현한다. 비교하는 두 실행에 다음을 가정한다.

- 같은 IVP, fixture, source, event 정책, tolerance/scaling, solver binary와 초기 수치 상태를 사용한다.
- 부동소수점 환경, library 구현과 계산 순서가 같고, \(\Phi,Q\)가 그 상태와 응답에 관해 결정적이다.
- cache가 대체한 응답의 모든 solver-relevant bits가 원 함수 응답과 같다.
- provider의 numerical 성공 결과는 admitted key와 고정 scope로 결정된다.
- 한쪽만 timeout, call-cap, process-liveness, resource failure 또는 다른 외부 분기로 빠지지 않는다.

**정리.** 이 조건 아래 동일한 초기 상태에서 시작한 cache-off와 cache-on 실행의 모든 수치 query, adaptive step 결정, accepted numerical trajectory와 종료 수치 결과는 같다.

**증명.** \(S_0\)가 같으므로 \(q_0=Q(S_0)\)가 같다. reply bits가 같으므로 같은 결정적 \(\Phi\)를 적용한 \(S_1\)도 같다. 이 논리를 귀납하면 모든 유한 \(j\)에서 \(S_j\), \(q_j\), 수치 결과가 같다. 저장된 성공 trace를 끝까지 포함하는 경우 종료 분기도 같다. □

기록된 모든 query에서 응답 동일성을 확인한 replay는 이 귀납 논증의 수치 응답 전제를 해당 trace에서 구체화한다. 그러나 live guard와 시간에 관련된 외부 분기는 table replay의 검증 범위 밖이다. 새 fixture, 새로운 입력 state, 다른 build나 library, nondeterministic provider와 다른 scheduling 조건으로 일반화하려면 그 변경된 전제를 다시 확인해야 한다.

native call counter, log 길이, wall time과 cache 통계는 정상적으로 달라질 수 있다. 여기서의 동일성은 **수치 solver 계약의 동일성**이며 프로그램의 모든 외부 상태가 byte 단위로 같다는 뜻이 아니다. 또한 같은 approximate numerical trajectory가 재현되어도 참해에 대한 오차를 증명한 것은 아니므로 `global_error_bound=null`은 그대로다.

## 8. ISAT와 이번 exact memoization의 관계

Pope의 1997년 원 논문은 reaction mapping을 이용한 in situ adaptive tabulation을 제안한다. 그 방법은 저장 composition 근처의 query에 대해 저장 mapping 값과 Jacobian으로 국소 선형 근사를 만들고, 정해진 scaled retrieval error를 다루는 accuracy region으로 그 근사의 사용을 판정한다. 이는 근처의 다른 입력에도 근사를 반환하는 방법이다. 논문의 §4, 특히 식 (49)의 local linear approximation과 accuracy-region 설명을 실제로 읽어 확인했다. [P2]

현재 C21I exact cache는 가까운 입력을 묶지 않고 같은 full binary64 입력과 frozen scope에 저장된 동일 결과만 반환한다. 이번 table replay 역시 실제로 존재하는 동일 native 요청의 응답만 주입한다. 따라서 ISAT의 국소 근사 오차나 보고된 combustion benchmark 가속률을 이번 exact cache의 오차 또는 성능 수치로 가져오지 않는다. ISAT의 retrieval error 계약도 BASS의 전체 adaptive ODE 오차 상한으로 변환하지 않는다.

이 구분을 위해 SciSpace에서 원 논문을 식별하고 Exa로 저자 소속 Cornell의 원 PDF와 Python 3.12 공식 문서를 읽었다. 최초 SciSpace 검색의 광범위하거나 비관련인 결과는 채택하지 않았으며, `/3/` 최신 Python 문서 fetch는 버전 고정 근거에서 제외하고 `/3.12/` fetch를 사용했다. 검색 범위와 실제 tool 응답은 문헌 ledger에 남겼다.

## 9. native interval, full RHS와 end-to-end 시간

기존 C21I 비용식 자체를 재사용하되 새 raw에 맞춰 각 timer의 포함 관계를 분명히 한다. [A; S1, S4]

native log의 `seconds`는 request write/flush부터 response read까지의 monotonic interval이다. response 해석/validation과 응답 뒤 log JSON 쓰기/flush, Python optical RHS 구성은 그 timer 밖이다. I의 `original_rhs_execution_ns`는 그보다 큰 `super().original` 구간의 합이다. segment, reference result, job receipt, outer process wall은 시작·종료 위치가 다른 더 큰 관측 범위다. **이 timer들을 서로 독립적인 단계처럼 더하면 중복 계산한다.**

| 관측 범위 | H base (s) | I vectorized base (s) |
|---|---:|---:|
| outer process elapsed | 1.91 | 2.12 |
| job receipt wall | 1.2116977100085933 | 1.4319355220068246 |
| reference result wall | 0.8852872390125412 | 0.9776933779940009 |
| segment wall 합 | 0.8100929029751569 | 0.894694751012139 |
| instrumented original RHS 합 | 미계측 | 0.581804697 |
| logged native request interval 합 | 0.05604552090517245 | 0.05898441682802513 |
| full-key hit 인덱스의 native interval 합 | 0.004690387926530093 | 0.00497811014065519 |
| native-key hit 인덱스의 native interval 합 | 0.006793982960516587 | 0.007200388237833977 |

I의 original RHS 823회와 그 안의 native 823회는 같은 큰 비용의 서로 다른 부분이다. 마지막 두 행도 baseline에서 선택한 인덱스의 기록을 합한 것이므로 실제 cache-on 실행의 측정 절약량이 아니다.

full RHS 호출 \(j\)의 제거 가능한 전체 비용을 \(C_j\)라 하고, baseline 벽시계를 \(T_I\)라 하자. 같은 수치 trace에서 cache lookup, copy, insert/eviction 등 추가 비용을 \(C_{\rm cache}\), 그 외 실행 환경 및 다른 단계의 차이를 \(\Delta T_{\rm other}\)로 묶으면 비용 accounting은

\[
T_{\rm exact}^{\rm acct}
  = T_I-\sum_{j\in\mathcal H_{\rm full}}C_j
       +C_{\rm cache}+\Delta T_{\rm other}
\]

이다. 이 식에서 \(C_j\)를 native 로그 interval만으로 대체할 수 없다. 전체 RHS의 Python 연산, response parsing, validation, logging 비용도 생략될 수 있기 때문이다. 반대로 새로운 cache 비용을 0이라고 두는 것은 실제 구현의 측정이 아닌 이상화다.

주어진 H 작업의 wall보다 작은 값을 얻기 위한 조건은

\[
\boxed{\quad
\sum_{j\in\mathcal H_{\rm full}}C_j
  > (T_I-T_H)+C_{\rm cache}+\Delta T_{\rm other}
\quad}
\]

이다. 현재 한 쌍의 trial에서

\[
T_I-T_H=0.2202378119982313\ {\rm s},\qquad
T_I/T_H=1.181759699782439\ldots.
\]

동일한 다른 비용을 가정하면 I wall의 15.380428% 이상을 순수하게 줄여야 이 H wall에 도달한다. 이 비율은 한 쌍의 기록에 대한 산술이며 통계적으로 일반적인 성능 차이의 추정이 아니다. [A; W1]

### 실제 full-key 집합을 사용한 추가 판별

69개 full-key hit 인덱스의 I native interval 합은 4.97811014065519 ms다. 이는 I wall의 **0.347649%**, H–I gap의 **2.260334%**, 전체 native interval의 **8.439704%**다. 이 interval만 회계상 제외하면 1.42695741186616941 s가 남으며, H와의 차이는 0.21525970185757611 s다. native-key 100회의 7.200388 ms를 여기에 대신 사용하면 다른 cache 정책의 호출까지 절약했다고 잘못 셈하게 된다. [A; W3]

I의 전체 original-RHS 합은 0.581804697 s이고 개별 요청별 전체 RHS 시간은 저장되어 있지 않다. cache 비용과 다른 시간 변화가 0이라는 단순 조건에서도 H wall을 넘으려면 69개 hit가 전체 RHS 시간의 **37.854251% 초과**를 차지해야 한다. 동일한 사실을 요청 평균으로 쓰면,

\[
\overline C_{\rm hit}> {0.2202378119982313\over69}
 =3.19185235\ {\rm ms},
\]

반면 전체 823회의 관측 평균은

\[
\overline C_{\rm all}
 ={0.581804697\over823}
 =0.706931588\ {\rm ms}.
\]

따라서 그 단순 조건에서 필요한 hit 평균은 전체 평균의 **4.515080배 초과**다. 이는 hit별 전체 RHS 비용을 아직 모르기 때문에 유용한 **break-even 조건**이다. hit가 평균과 같은 비용이라고 가정한 성능 예측은 하지 않는다. cache-on 실제 실행을 하더라도 scheduling, native admission/guard, logging과 프로세스 비용을 포함하는 같은 timer 범위에서 판단해야 한다. [A; W3]

native wait를 전부 0으로 둔 회계값도 1.37295110517879947 s로 H보다 크지만, 이 사실을 “exact cache의 전체 가속은 불가능하다”는 no-go로 사용하지 않는다. full RHS의 나머지 제거 가능한 시간과 실행 변동을 native wait 상한이 제한하지 않기 때문이다. 확보한 결론은 현재 기록만으로 전체 시간 가속이 확립되지 않았다는 것이다.

## 10. 독립 검산, 실제 수행과 남은 의무

Wolfram context를 먼저 호출한 뒤 evaluator를 사용했다. 전체 determinant나 기존 Schur 유도는 반복하지 않았다.

| 검산 | 실제 결과 | 범위 |
|---|---|---|
| W1: 광학깊이 변화 및 시간 산술 | heat 항등식 residual 0; native input의 tau 미분 7개 0; exact decimal rational 시간 계산 |
| W1의 첫 부호 단순화 | `True`로 닫히지 않고 동등한 부등식으로 남음 | 이를 성공한 부호 증명이라고 기록하지 않음 |
| W2: 부호와 작은 사례 refinement | \(d>0\land1-e^{-d}>0\)의 Reduce 결과 \(d>0\); 인수분해 residual 0; \(d=\log2\)에서 \(-1/2\) |
| W3: full-key 수치와 차원 | opacity Hz, tau 도함수 무차원, thermal 도함수 eV; 69-hit break-even 산술 | 실제 full-key 결과 도착 후 변경된 수치만 검산 |

유한 LRU 불변식과 투영 보조정리는 직접 귀납으로 증명했고, adaptive 동일성은 필요한 numerical 및 runtime 전제를 열거한 조건부 귀납 정리로 보존했다. 작은 optical counterexample는 key 의존성을 분리하는 구성이다. 새로운 strong no-go는 주장하거나 채택하지 않았다.

| 축 | 이번 단위 상태 |
|---|---|
| 유도·검산 실행 | 새 구성과 proof, source 확인, SciSpace/Exa 원전 확인, Wolfram 경량 검산 완료 |
| callback/trace 계산 | 최신 analysis/replay attempt 02 재사용; 원 attempt 01 보존; 새 native·IVP 0 |
| 게시 | 이 child가 remote를 변경하지 않음; root의 C21J source/report 게시 단계와 분리 |
| 백업 | 이 child는 업로드하지 않음; 원 raw를 scratch에 보존하여 root의 create-only 마감 대상으로 전달 |
| DAG | C21I 고정 source + PR87 고정 native 반환 → full trace/LRU와 immutable reply table → callback replay; timer raw → 별도 비용 해석 |

재개 시 기존 일반 C21I 이론·제조 검증이나 이번 성공 기본 replay를 전면 재실행할 필요는 없다. gate 수정 후 성공한 attempt 02를 현재 결과로 사용하고, 원 attempt 01 및 V1 finding을 별도 identity로 보존한다. 독립 focused 검증 22개 PASS와 root의 변경된 gate 실행 exit 0 기록을 연결했다. 게시·백업 영수증은 root의 별도 마감 축이다. native exact의 실제 성능은 이 자료로 완료 처리하지 않는다. live exact 실행이 후속 목표가 되면 현재 source/binary/fixture/table identity, resource/admission/timeout 계약을 실제 실행 시점에 확인한 bounded 입력이 필요하다.

## 근거 및 원전

### 프로젝트의 직접 근거

- **A**: 현재 `../evidence/analysis_attempt_02/ANALYSIS.json`; 역사적 최초 분석 `../evidence/analysis_attempt_01/ANALYSIS.json`. 세 raw job의 full-key 복원·823개 native string 대응·LRU·timer scope·input SHA. 최신 분석은 읽는 return 파일을 고정 payload manifest에 연결한다. 원 source와 raw 파일의 SHA는 그 JSON과 이 디렉터리의 `SOURCE_IDENTITY.json`에 있다.
- **B**: 현재 `../evidence/replay_attempt_02/REPLAY_REPORT.json`; 역사적 최초 replay `../evidence/replay_attempt_01/REPLAY_REPORT.json`. 원 source에 저장된 native response를 주입한 실제 네 case의 callback 재현. 최신 보고서는 input pin SHA, source 24개·return 60개와 source/return commit, 각 segment reply hash, 새 호출 0을 구분한다.
- **C**: 현재 `../evidence/independent_review/REPLAY_REVIEW_V2.json`, `../evidence/independent_review/RUN_FOCUSED_GATE_TESTS.md` 및 `../evidence/ROOT_FOCUSED_EXECUTIONS.json`. 독립 focused 16+6개 PASS, C9-J1/J2/J3 해결, root의 새 gate가 포함된 analysis/replay attempt 02 exit 0. 역사적 `../evidence/independent_review/REPLAY_REVIEW_V1.json`, `../evidence/independent_review/REPLAY_CONTRACT_PROBES_V1.json`, `../evidence/independent_review/TRACE_ADMISSION_TEST_ATTEMPT01.json`은 그대로 보존한다.
- **S1**: [고정 C21I optimized_adapter.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21i_callback_optimization_20261020/optimized_adapter.py).
- **S2**: [고정 C21H optical_adapter.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21h_vigilode_bridge_20261019/optical_adapter.py).
- **S3**: [고정 reference_tau.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21e_event_native_20261018/src/reference_tau.py), [run_experiment.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21e_event_native_20261018/src/run_experiment.py).
- **S4**: [고정 native_micro.py](https://github.com/cosmosapjw-quantum/bass_cr/blob/fe6bbaec2de5032b938aed0713623b9618ba70e6/research/cr_c21e_event_native_20261018/src/native_micro.py).
- **W1–W3**: `raw/wolfram_evaluator_trace.json`, `raw/wolfram_sign_refinement.json`, `raw/wolfram_full_key_timing_dimensions.json`. 실제 code, 요청시각과 원 tool 응답 포함.

### 실제 읽은 외부 원전

- **P1**: Python 3.12 공식 문서, [functools — Higher-order functions and operations on callable objects](https://docs.python.org/3.12/library/functools.html), `lru_cache` 절. 개념적 memoization 및 purity 주의의 근거로만 사용.
- **P2**: S. B. Pope, “Computationally efficient implementation of combustion chemistry using in situ adaptive tabulation,” *Combustion Theory and Modelling* **1** (1997), 41–63. [Cornell 저자 원 PDF](https://tcg.mae.cornell.edu/pubs/Pope_CTM_97.pdf), [DOI 10.1080/713665229](https://doi.org/10.1080/713665229). §4 및 식 (49)를 사용; paper의 가속률을 본 프로젝트에 이전하지 않음.

원 tool 결과와 검색의 채택·제외 이유는 `LITERATURE_LEDGER.json`, R1–R10의 새 작업/재사용 구분은 `R_LOOP_STATUS.json`에 있다.

