# C21K: epoch opacity 재사용과 독립 작업 DAG의 정확성·비용 조건

작성일: 2026-10-20 UTC. 이 문서는 C21I의 일반 Schur 유도와 C21J의 full-RHS trace 분석을 재사용하고, 이번에 추가되는 opacity 공통 계산 분리, epoch 캐시, 작업 병렬화에 한정하여 새로운 근거를 적는다. 원 과학 source와 과거 실패/raw는 보존한다. 새로운 native chemistry 호출과 전진 IVP 실행은 이 이론 작업에서 각각 0회다. `global_error_bound=null`이며 기존 과학 HOLD는 유지한다.

## 1. 질문, 새 결과, 범위

검토할 구성은 고정 C21I callback `vectorized_exact`에 다음 두 변경을 더하는 것이다.

1. 원 `reference_tau.py`와 C21I callback의 source bytes를 그대로 사용하면서, private import binding으로 `run_experiment.opacity`를 정확한 epoch 캐시와 같은 순서의 scalar 공통 계산을 사용하는 함수에 연결한다. 기본 실행의 `H`는 원함수를 유지한다.
2. 서로 독립인, 입력·source·native identity가 입증된 작업을 현재 자원에 맞게 병렬 실행한다. 한 작업 안의 적분 cell 및 검증 단계의 선행 관계는 유지한다.

새로운 이론 결론은 조건부이고 구체적이다. 고정 fixture에서 opacity는 실제 전달된 clamped epoch에만 의존하므로 gas FD stencil의 서로 다른 상태에서도 같은 opacity 값을 재사용할 수 있다. 원 scalar 곱의 괄호와 개별 연산을 그대로 유지한 공통 부분식 분리는 허용된 유한 binary64 입력에서 같은 수치 결과를 준다. 이 두 성질은 전체 RHS를 epoch만으로 캐시할 수 있다는 뜻이 아니다. 실제 wall time 이득은 lookup·복사·검사 비용을 포함하여 별도로 측정해야 한다.

작업 병렬화에서는 단일 CPU 작업의 총 work와 critical path로 하한을 구할 수 있다. 고전적인 list scheduling 상한은 균질 CPU, 고정 작업 시간, 선행 관계 외의 admission 제약이 없는 모델에서 성립한다. 실제 memory·quota·affinity 제약을 적용한 NCP scheduler의 측정 성능에 이 근사비를 자동 부여하지 않는다.

## 2. 재사용 authority와 실제 읽은 근거

원 실행 source authority는 C21I content `fe6bbaec2de5032b938aed0713623b9618ba70e6`다. C21J content `55e6569a8f816e13babe4165f0fef3655f7299a3`와 그 고정 replay/input-pins는 입력 검증 및 저장된 callback stream의 authority로 재사용한다. PR87의 실제 native 반환과 C21J의 재생은 서로 다른 실행 종류다.

|표지|근거|이 문서의 용도|
|---|---|---|
|S1|`research/cr_c21e_event_native_20261018/src/reference_tau.py`, SHA256 `714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0`|실제 epoch clamp, RHS 의존성과 호출 순서|
|S2|같은 unit의 `src/run_experiment.py`, SHA256 `71fb34d6ae5ca843868a2b666a0e7f93ee330c5bedc6c7191220e8060f4869fc`|opacity 원식, fixture 구조|
|S3|같은 unit의 `src/event_coupler.py`, SHA256 `24386145f4337b2e01a32219a56ec2446080e4aa4a679a8f956a3eb7ff2ab819`|gas-dependent neutral fractions 및 H/cross binding|
|S4|같은 unit의 `vendor/pr79/radau_exposure_oracle.py`, SHA256 `23895d81e50791135c689db5b6a180fcb23e05ef8cb76e271c65b189cf3fe428`|고정 H, cross, 단위·threshold 분기|
|S5|`research/cr_c21i_callback_optimization_20261020/optimized_adapter.py`, SHA256 `bb73bfa9bd865f60eefeed55dbd05df076a9856544345595beb914676105396e`|기존 full-state exact cache, gas FD, fixture freeze|
|E1|`c21k_work/verification/epoch_final/replay/REPLAY_REPORT.json`|초기 opacity+H 캐시의 보존된 정확성·timing 결과. 디렉터리 이름의 `final`은 최신 source authority를 뜻하지 않음|
|E2|`c21k_work/verification/epoch_attempt_03/replay/REPLAY_REPORT.json`|H 원함수 유지+opacity CSE 후보의 보존된 정확성·timing 결과|
|E3|`C21K_EPOCH_INDEPENDENT_REVIEW.json`|이번 이론 작업자의 읽기 전용 source 검토 범위와 hash|
|P1|`c21k_work/policy/HPC_ACCURACY_POLICY_KO.md`|FP64·연산순서·thread·memory·실패 보존 정책|

각 파일의 실제 bytes와 추가 source/evidence hash는 `SOURCE_IDENTITY.json`에 적는다. 파일 bytes hash와 fixture의 canonical semantic digest는 다르다. 이번 I-base `fixture.json`의 원 파일 SHA는 `bcfb3d5a8b4d5c8153247712eb1c3d127c4410e2455f6106bf60720642d0f060`, 보고서의 fixture digest는 `befb0c8a7a113ff0efccc450af05b1157592a8d91cc7e994cfdfd2768905cc65`다. 이를 서로 대체하지 않는다.

## 3. 원 source의 함수 의존성

epoch를 \(x=\log a\), 해당 cell 내부에서 원 source가 실제 사용한 값을

\[
\chi_c(x)=\min\{\max(x,\ell+10^{-9}(r-\ell)),\,r-10^{-9}(r-\ell)\}
\]

로 쓰자. 이 식은 수학 표기이며 구현에서는 원 binary64 연산 결과를 그대로 사용한다. 캐시가 독자적으로 clamp를 다시 계산하지 않는다. 캐시 key는 원 함수에 실제 전달된 \(\chi\)의 bytes다.

고정 fixture를 \(f\), cohort index를 \(i\), species index를 \(j\)라 하면 원식은

\[
E_i(\chi)=q_i e^{-\chi},\qquad
K_{ij}(\chi)=s\,c\,n_{H,0}e^{-3\chi}\,\sigma_j(E_i(\chi)),
\]

\[
H(\chi)=H_0\sqrt{\Omega_m e^{-3\chi}+\Omega_r e^{-4\chi}+\Omega_\Lambda}.
\]

여기서 \(s\)는 `opacity_scale`이고, \(q_i,n_{H,0},s\) 및 cross-section 상수는 고정된다. 실제 `H` source는 `a=math.exp(x)`를 만든 뒤 `a**3`, `a**4`를 사용한다. 위 지수식으로 source를 다시 쓰지 않는다. 이 표기는 의존성과 미분을 설명하는 실수식이다. [S2–S4]

**명제 K1 — source-specific 독립성.** 고정되고 변하지 않는 fixture·원 함수 및 전역 상수·실행 환경을 하나의 scope \(S\)로 묶으면, 계수 \(B_S(\chi)=(E,K,H)\)는 gas state, optical depth, passive ledger의 값에 의존하지 않는다. 동일한 \(S,\chi\)에 대한 성공한 유한 결과는 이 세 종류의 상태가 달라도 재사용 가능하다.

증명은 원 source의 free variable을 직접 추적하는 것으로 충분하다. `opacity`는 fixture의 `q`, `opacity_scale`, `nh0`와 `x`, `cross`, `C_CM_S`, `math`, `np`만 읽는다. H는 x와 고정 우주론 상수만 읽는다. gas·tau·ledger는 두 함수의 입력이나 읽는 전역 변수에 없다. `Y`는 opacity/H 식에 나타나지 않지만, 구현은 보수적으로 전체 fixture identity를 scope에 묶는다. [S2–S4]

이 명제가 전체 RHS로 확장되지 않는 이유도 원식에서 보인다. neutral-fraction 벡터 \(\alpha(g)\), survival population \(N_i(\tau)\)에 대해

\[
\operatorname{hazard}_{ij}=K_{ij}\alpha_j(g),\qquad
\operatorname{rate}_{ij}=N_i(\tau)K_{ij}\alpha_j(g)
\]

이며 photon/gas/heat/ledger 도함수는 이 rate와 native micro 결과를 사용한다. gas FD에서 \(K\)가 동일하더라도 \(\alpha(g)\)와 micro는 달라진다. tau 변화에서는 survival population이 달라진다. 그러므로 epoch cache는 `E,K`만 저장하며 hazard, rate, RHS 또는 native reply를 저장하지 않는다. 기존 full \((t,u)\) exact cache는 별개의 충분히 큰 key와 admission을 유지한다. C21J의 7-input native projection과 full-RHS key 구분도 그대로 유효하다. [S1,S3,S5]

단위는 \(c\,[\mathrm{cm/s}]\), \(n_H\,[\mathrm{cm}^{-3}]\), \(\sigma\,[\mathrm{cm}^2]\)에서 \(K\,[\mathrm{s}^{-1}]\)다. H도 \(\mathrm{s}^{-1}\)이므로 \(K/H\)는 무차원이고, x에 대한 tau 도함수와 일관된다. 에너지 E는 eV이므로 rate에 E를 곱한 항을 H로 나누면 원 thermal/ledger 단위가 유지된다. Wolfram의 실제 unit 계산에서도 `Hertz`와 무차원 1이 반환되었다. [W2]

## 4. exact key, 소유권, 부동소수점 동등성

**명제 K2 — 정확한 memoization의 수치 동등성.** 다음 조건을 만족하면 이 scope에서 성공하는 opacity 호출마다 원함수와 같은 shape·dtype·binary64 value bytes를 반환할 수 있다.

- 입력 epoch는 실제 지원형인 Python `float` 또는 NumPy `float64`의 유한 값이다. key는 해당 값의 binary64 bytes이며 `+0`과 `-0`을 구분한다. 정수·bool·float32·longdouble 등을 동일 key로 축약하여 받아들이지 않는다.
- fixture의 순서 있는 `q`, `birth`, `amounts`, `gas0`는 소유한 tuple이고 scalar 값도 고정된다. `dataclass(frozen=True)`만으로 JSON list 내부가 고정되는 것은 아니므로 C21I의 freeze를 먼저 사용한다.
- 원 함수 binding, cross-section의 전역 상수, math/NumPy 의미와 FP 환경은 scope 동안 바뀌지 않는다. 함수 source bytes가 동일하다는 사실만으로 임의의 runtime monkeypatch까지 배제되지는 않는다.
- miss에서 원식 또는 아래 K3의 동일 연산 순서 kernel을 호출한다. 예외·nonfinite·shape 불일치 결과는 성공 cache로 저장하지 않는다.
- 내부 cache 배열은 immutable bytes로 뒷받침하고, miss의 반환 배열과 독립된 사본으로 보관한다. hit에서는 소비자가 수정해도 cache를 바꾸지 못하는 소유 사본을 반환한다.
- table은 한 작업/한 event cell의 소유이며 LRU capacity는 16이다. cell 시작 시 비운다. fixture 또는 source scope 변경 시 이전 table을 사용하지 않는다.

증명은 호출 순서에 대한 귀납이다. 첫 miss는 원 결과를 계산하고 그 bytes를 저장한다. 이후 miss도 같다. hit의 key와 scope는 이미 저장된 호출과 동일하므로 함수의 순수성·고정 환경 조건에서 동일 결과를 갖는다. 별도 소유 사본 때문에 앞 호출의 소비자 수정이 귀납 가정을 훼손하지 않는다. eviction은 다음 호출을 miss로 바꾸므로 값의 정확성을 바꾸지 않는다. LRU 크기는 정확성 조건이 아니라 저장 공간·hit 수의 선택이다.

이 보장은 숫자 결과와 원 호출자가 요구하는 배열 소유권에 관한 것이다. 매번 새로운 객체의 메모리 주소가 같아야 한다거나, 함수 호출 횟수·warnings 횟수·profiling event·wall time이 같아야 한다는 주장은 하지 않는다. 유한 정상 입력 밖의 예외 발생 시점도 본 명제의 범위에 포함하지 않는다. Python의 일반 `lru_cache`는 재사용 값과 hashable 인수를 다루지만 mutable 결과를 매번 별도로 소유해야 하는 요구까지 자동 해결하지 않는다. 이 때문에 이번 구현은 값 bytes와 소유권을 명시한다. [L2]

### 전체 callback과 미래 adaptive path

같은 원 상태·provider 답·FP 환경에서 `E,K,H`의 bytes가 같고 원 RHS의 나머지 연산 순서가 같으면 RHS bytes도 같다. callback 조립 순서가 같으면 Jacobian/partial-t reply도 같다. 이 부분은 C21J의 deterministic callback 논증을 재사용한다.

저장된 RPC 요청을 재생하여 reply bytes가 맞는다는 관측은 그 고정 stream의 검증이다. 새로운 native 실행에서 solver 초기 상태·모든 이전 응답·제어 흐름·종료 정책까지 같고 비수치적 deadline/process 실패가 개입하지 않는다는 조건을 추가하면 step-by-step 귀납으로 같은 다음 요청을 논할 수 있다. 실제 미래 adaptive 경로를 새로 실행했다는 뜻은 아니다. 이번 `global_error_bound`를 유한 상계로 바꾸지도 않는다.

### 실제 private binding 범위

`reference_tau.H`는 module import 시 `event_coupler`에서 바인딩되고, Jacobian도 `event_coupler.H`를 읽는다. `run_experiment.H`만 바꾸는 hook으로는 이 경로를 덮지 못한다. 최종 기본 후보는 이 문제를 피해 H 원 binding 자체를 유지한다. opacity는 reference와 callback의 `from run_experiment import opacity`에 private binding을 공급한다. 공개 `sys.modules`의 opacity/H를 바꾸지 않는다. [S1,S5,E3]

함수 pointer·fixture 범위의 실제 mutation guard와 전역 환경의 불변 가정은 구분한다. `_check_functions`는 검사된 direct bindings의 교체를 탐지하지만 `cross.__globals__`의 모든 항목을 매 hit마다 증명하는 장치가 아니다. 새로운 source/runtime context에서 이 불변 조건을 다시 입증해야 한다.

## 5. 원 연산 순서를 보존하는 opacity CSE

원 `K_ij` expression의 Python scalar 곱은 다음의 왼쪽 결합 순서다.

\[
\operatorname{mul}(\operatorname{mul}(\operatorname{mul}(\operatorname{mul}(s,c),n),e),v),
\quad e=\operatorname{exp}(-3\chi),\quad v=\operatorname{cross}(j,E_i).
\]

이때 `mul`은 대수적인 실수 곱이 아니라 해당 runtime의 한 번의 binary64 곱을 나타내는 기호다. 다음과 같이 같은 중간 결과를 재사용한다.

\[
A=\operatorname{mul}(\operatorname{mul}(s,c),n),\qquad
b=\operatorname{mul}(A,e),\qquad K_{ij}=\operatorname{mul}(b,v).
\]

**명제 K3 — 동일 중간식의 반복 계산 제거.** K2의 고정 환경 아래에서 위 중간 결과를 저장하여 사용하는 것은 원 각 entry의 연산 tree를 바꾸지 않는다. 따라서 성공한 유한 결과의 bytes를 보존한다. A는 fixture scope가 고정되는 cell 시작에 한 번, b는 opacity miss마다 한 번 계산해도 된다.

증명은 연산 tree의 치환이다. 새 식의 A와 b를 펼치면 원 `mul` tree와 문자 그대로 동일하다. 같은 피연산자에 대해 결정적인 한 번의 `mul`/`exp` 결과를 사용하므로 반복해서 얻던 동일 반올림 결과를 보관하여 읽는 것과 같다. Wolfram에서는 `Times`로 자동 재결합하지 않는 미정의 head `mul`을 사용하여 두 tree의 `SameQ=True`를 실제 확인했다. 이것은 tree 치환의 검산이며, Wolfram이 Python/NumPy/libm의 모든 IEEE 동작을 인증했다는 주장이 아니다. 실제 kernel bit parity는 독립된 focused 검사와 replay로 확인해야 한다. [W1,E3]

허용하지 않는 변경에는 `s*(c*n)`으로의 재결합, `exp(-3*x)`를 `exp(-x)**3`으로 바꾸기, H의 지수 표현 교체, FMA/fast-math, cross 계산 순서 변경, dtype 축소, threshold 주변 epoch rounding이 포함된다. 이들은 동일 연산 tree 증명에 들어가지 않는다. FP 연산은 각 연산에서 반올림될 수 있으므로 실수식의 대수적 같음만으로 byte 같음을 추론하지 않는다. [L3,P1]

`E=np.asarray(q)*math.exp(-x)`는 원식 그대로 둔다. M개 cohort의 원 opacity 한 호출은 E용 exp 1회와 K의 3M개 entry용 exp 3M회를 실행한다. CSE miss는 exp 2회다. 따라서 M=9에서 28→2, M=81에서 244→2이며, K 쪽의 27회가 1회가 되는 것과 E의 1회는 따로 센다. cross 호출은 miss당 3M회로 그대로다. [S2,W2]

성공한 유한 입력을 벗어나면 원함수와 새로운 guard의 예외 시점이 다를 수 있다. `M=1..128`의 명시적인 admission 범위, 양의 유한 energy, 유한 K 결과 및 고정 fixture 검사와 함께 사용한다. source-level 유도는 이 범위의 모든 M에서 같은 형태로 성립하지만 focused test가 실제 검사한 M·threshold·Y 값 목록과는 별도로 기록한다.

## 6. 민감도와 반례 검토

### 6.1 epoch 근사 key는 같은 계약이 아니다

고정 q에서

\[
\frac{E_i(x+\delta)}{E_i(x)}=e^{-\delta},\qquad E_i'(x)=-E_i(x).
\]

또 \(B(x)=\Omega_m e^{-3x}+\Omega_r e^{-4x}+\Omega_\Lambda\)라 놓으면

\[
H'(x)=-\frac{H_0(3\Omega_m e^{-3x}+4\Omega_r e^{-4x})}{2\sqrt{B(x)}}.
\]

cross의 미분 가능한 구간에서는

\[
K'_{ij}(x)=-3K_{ij}(x)-s c n_{H,0}e^{-3x}E_i(x)\sigma'_j(E_i(x)).
\]

이 식은 실수식의 sensitivity이며 원 source의 FP 연산을 바꾸는 식이 아니다. Wolfram 실제 미분 결과와 일치한다. [W1] cross에는 threshold 비교 분기가 있으므로 threshold를 가로지르는 구간에 이 매끄러운 미분식을 그대로 연장하지 않는다. 인접 표현 가능 epoch나 `+0/-0`을 무조건 합치지 않는다. exact cache를 approximate tabulation으로 확대하는 새 오차 계약은 이번에 채택하지 않는다.

### 6.2 fixture의 순서도 identity다

같은 epoch에서 `q=(q,2q)`와 `q=(2q,q)`는 E와 K의 row 순서를 바꾼다. q>0이면 첫 E 원소가 서로 다르다는 것을 Wolfram으로도 확인했다. [W2] 모든 cohort state까지 같은 permutation으로 함께 옮기는 별도 물리적 재표현은 가능하지만, 캐시가 다른 fixture의 row 배열을 그대로 돌려주는 것은 그 변환을 수행한 것이 아니다. 따라서 fixture permutation을 epoch key 아래에서 합치지 않는다. nh0 또는 opacity_scale 변경도 다른 scope다.

### 6.3 상태·복사·성능 반례

같은 epoch에서 gas를 perturb하면 alpha가 달라지고, tau를 perturb하면 population이 달라진다. 이 둘은 K1의 반례가 아니라 K1을 전체 RHS로 확장하면 틀린다는 구체적 예다. cache의 writable 배열을 그대로 반환하면 첫 호출자의 수정이 다음 hit를 오염시키므로 owned-copy 조건이 필요하다. 첫 7쌍 timing의 median이 1보다 작았다는 실제 결과는 hit 수가 많으면 항상 빠르다는 주장에 대한 반례다. 특정 구현·환경의 비용 결과이며 exact memoization 일반의 불가능성 정리는 아니다.

## 7. 실제 재생 계수와 비용식

### 7.1 서로 다른 층의 count를 분리한다

|고정 stream/모드|원 RHS 평가 또는 table query|추가 analytic Jacobian opacity 호출|opacity requests|opacity misses|opacity hits|
|---|---:|---:|---:|---:|---:|
|I-base, vectorized|823|36|859|329|530|
|I-base, vectorized_exact|754|36|790|329|461|
|I-FD-half, vectorized_exact|754|36|790|329|461|

위 표는 E1/E2의 실제 저장된 요청 재생 결과다. 각 경우 472개 callback reply, 40,432개 binary64 값과 derivative nodes를 비교했다. 원 accepted states를 이용해 재구성한 physical summary도 같았으나 새 trajectory를 적분한 것이 아니다. source/fixture/raw admission은 고정 C21J gate를 재사용했다.

I-base vectorized의 cell별 `(requests, misses, hits)`는 `(284,108,176)`, `(291,113,178)`, `(284,108,176)`이고, exact는 `(261,108,153)`, `(268,113,155)`, `(261,108,153)`이다. 따라서 기존 full-RHS 69 hit가 먼저 제거한 호출을 epoch hit에 다시 더하지 않는다. 실제로 `859−790=530−461=69`이고 miss 합은 양쪽 모두 329다. 이 등식은 이 관측 stream의 결과이며 모든 미래 stream의 miss 수 불변 정리는 아니다. [E1,E2,W1]

`823→754`는 기존 C21I full-state exact cache가 table query를 줄인 수치다. 이번 epoch 층은 같은 exact 모드에서 native query 수를 추가로 줄이지 않는다. C21J의 native projection 100 hit와 full-RHS 69 hit도 서로 다른 집계다. 이번 opacity 461 hit를 native chemistry 절약 횟수로 쓰지 않는다.

### 7.2 CSE와 cache를 포함하는 break-even 식

기존 full-RHS cache를 통과한 뒤 남는 opacity 요청을 기준으로 \(Q=N_m+N_h\)라 하자. 평균 원 opacity 계산 비용을 \(c_o\), 새로운 CSE miss kernel 비용을 \(c_f\), 모든 요청의 key/guard/lookup 비용을 \(c_k\), hit 반환 복사 비용을 \(c_h\), miss 저장 비용을 \(c_s\), cell별 setup 합을 \(C_0\)라 하면

\[
T_{\mathrm{original\ opacity}}=Qc_o,
\]

\[
T_{\mathrm{epoch+CSE}}=N_m c_f+Qc_k+N_hc_h+N_mc_s+C_0.
\]

따라서 opacity 층의 절약은

\[
\Delta T=N_hc_o+N_m(c_o-c_f)-Qc_k-N_hc_h-N_mc_s-C_0.
\tag{1}
\]

이 식은 Wolfram에서 전개한 비용 identity와 일치한다. [W1] 동일 비용 근사가 부적절하면 각 항을 실제 호출별 비용의 합으로 바꾼다. 단순히 `N_h>0`이라는 사실로 (1)>0을 결론내릴 수 없다. cheap H의 캐시 이득은 특히 작을 수 있으므로 최종 기본 후보는 H를 원함수 그대로 두고 opacity 경로에 집중한다.

전체 callback 또는 전체 job에서는

\[
T_{\rm new}=T_{\rm old}-\Delta T_{\rm opacity}
 +\Delta T_{\rm other},
\]

이고 `other`에는 Python allocation·protocol parsing·native 대기·solver 및 OS scheduling 변화가 포함될 수 있다. 기존 full-RHS cache와의 결합을 쓸 때에는 먼저 full-RHS hit가 제거한 비용을 빼고, 잔여 stream에 대해서만 식 (1)을 적용한다. 동일 opacity 계산을 두 번 절약으로 계산하지 않는다.

캐시 overhead를 0으로 가정하고 전체 기준 시간 중 opacity에서 제거할 수 있는 비율을 f라 하면 이상적인 최대 speedup은 `1/(1−f)`다. 이 식은 같은 workload와 나머지 비용 고정을 가정한 예산 상한이다. 실제 시간 비율의 추정치나 native 성능 결과가 아니다.

### 7.3 배열 payload와 관측 timing

opacity entry당 저장 값은 E의 M개와 K의 3M개 binary64이므로 payload는 32M bytes다. capacity16의 payload는 512M bytes: M=9에서 4,608 bytes, M=128에서 65,536 bytes다. 선택적인 H cache는 16개 float 값으로 추가 128 bytes이지만 기본 후보에서는 꺼져 있다. Python dict·key·array 객체와 반환 사본·native/solver RSS는 이 수에 포함되지 않는다. 이 작은 payload만 보고 NCP job의 peak memory를 추정하지 않는다. [W1]

|보존된 측정|epoch adapter SHA|paired ratio의 정의와 관측|판정|
|---|---|---|---|
|E1 초기 opacity+H memo|`3245d8711bf14f67b20190936fb7306a5934e919c2e5b5ac3244f9f7026b68c4`|original I-exact callback time / epoch callback time; 7쌍 median 0.9364664940909709, range 0.8827007445932692–1.180060594772746|일관된 replay 가속 `NOT_ESTABLISHED`|
|E2 opacity memo+CSE, H 원함수|`db244c0689e8473f80f90a35587edd5114fda7df9a9a3fda2baa1affac04f719`|같은 정의; 7쌍 median 1.0004085537167522, range 0.7356966366186033–1.1219821144916622|일관된 replay 가속 `NOT_ESTABLISHED`|

이는 warm-up 이후 순서를 번갈아 수행한 saved-callback component timing이다. 실제 NCP native job의 end-to-end timing이 아니다. 각 수치를 해당 실행 source hash에만 연결한다. E2 이후 typed-key·deadline 등의 수정에 이 측정치를 새 source의 결과로 붙이지 않는다. 최신 실행 및 source 권위는 별도 실행 영수증에서 읽는다. Native exact와 C21K live-native performance 및 NCP64 scaling은 아직 이 근거로 평가되지 않았다.

## 8. 독립 작업 DAG의 work·critical-path 하한

유한 DAG를 \(G=(V,E)\), 한 CPU를 독점하여 중단 없이 실행하는 job v의 고정 시간을 \(p_v>0\)라 하자. predecessor가 모두 끝난 뒤에만 v가 시작될 수 있다. 동일한 CPU P개가 실제로 허용되고 선행 관계 외에 admission 제약이 없다고 먼저 가정한다.

\[
W=\sum_{v\in V}p_v,\qquad
L=\max_{\pi\text{ path in }G}\sum_{v\in\pi}p_v.
\]

**명제 K4 — 필요 시간 하한.** 어떤 적법한 schedule도

\[
C^*\ge\max\{W/P,L\}
\tag{2}
\]

를 만족한다. 총 처리 가능한 CPU 시간은 PC이므로 PC≥W다. 한 선행 chain의 작업은 겹칠 수 없으므로 C≥그 chain 길이이고, 최대를 취하면 C≥L이다.

이 모델에서 work-conserving list scheduler는 idle CPU가 있고 ready job이 있으면 지정 순서의 첫 ready job을 즉시 시작한다. 마지막으로 끝난 job에서, 각 단계의 마지막으로 끝난 predecessor를 거슬러 올라가 chain을 잡는다. chain job 사이에 CPU가 남는 구간이 있었다면 다음 chain job은 이미 ready였으므로 바로 시작했어야 한다. 따라서 CPU가 모두 바쁘지 않은 시간은 이 chain의 실행 구간 안에 놓이며 그 총 길이는 L 이하이다.

총 시간 C 중 이러한 시간의 길이를 I≤L이라 하면 그 밖에는 P CPU가 모두 일하고, 그 안에도 적어도 chain의 한 CPU는 일한다. 따라서

\[
W\ge P(C-I)+I\ge PC-(P-1)L,
\]

\[
C_{\rm list}\le W/P+(1-1/P)L
\le (2-1/P)C^*.
\tag{3}
\]

이는 Graham의 원전에서 쓰는 chain/idle-time 논증을 현재 변수로 적용한 것이다. 원전의 모델은 동일 processor, non-preemption, partial order, ready task list다. 공식 Bell Labs 기록과 원 논문 본문의 모델·proof·일반 bound 부분을 실제 읽었다. (3)의 마지막 대수 단계는 work 우세/chain 우세 두 경우로 나눠 Wolfram에서 확인했다. [L1,W2]

작업 시간이나 task list가 달라지면 schedule과 critical path도 달라진다. 예를 들어 독립 job 시간 `(1,1,1,3)`을 CPU2에서 해당 순서로 list 배치하면 부하 `(2,4)`, 큰 job부터 `(3,1,1,1)`로 배치하면 `(3,3)`이다. W=6, L=3은 같지만 makespan은 4와 3이다. 이 작은 permutation 계산을 Wolfram에서 실제 수행했다. [W2] 각 job의 최적화 뒤에는 바뀐 \(p'_v\)로 W와 L을 다시 계산해야 한다. 특정 list policy에서 CPU 증가나 일부 job 단축이 항상 wall time을 단조 감소시킨다고 일반화하지 않는다. 이것은 고전적인 scheduling anomaly의 범위 문제이지 새 no-go 주장이 아니다. [L1]

## 9. NCP의 실제 admission과 측정 계약

광고된 64 cores/128GB는 실행 admission의 관측치가 아니다. 실제 사용할 CPU 집합을

\[
\mathcal A=(\text{online}\cap\text{affinity}\cap\text{effective cpuset}\cap\text{이번 작업에 배정된 CPU})\setminus(\{55\}\cup\text{다른 reserve})
\]

로 정한다. Linux cgroup의 `cpuset.cpus`는 요청 값이고 `cpuset.cpus.effective`가 실제 parent에게서 허용받은 online CPU를 나타낸다. `cpu.max`의 quota와 ancestor 한도도 별도로 고려해야 한다. 현재 NCP 값은 packet 실행 때 직접 읽어야 한다. `{0,…,63}` 전체가 실제 사용 가능하고 유일한 제외가 CPU55인 가정에서만 63개라는 산술이 성립한다. Wolfram의 63은 이 가정의 count이며 현재 NCP 측정치가 아니다. [L4,W2]

메모리는 bytes로 계산한다. 현재 host available memory, 유효한 cgroup/ancestor의 remaining limit, job policy reserve 중 더 제한적인 값을 적용하여 \(M_{\rm budget}\)을 정한다. `memory.current`는 해당 cgroup과 descendants의 현재 사용량이고 `memory.max`는 hard limit이다. cgroup 수치만으로 다른 ancestor 또는 OS의 실제 pressure가 사라지는 것은 아니다. 프로젝트 정책상 실제 128GiB 사용 가능 환경에서는 최소16GiB 여유를 두며, 더 작은 실제 한도에서는 비례 reserve와 최소1GiB 조건을 적용한다. GB와 GiB를 혼용하지 않는다. [L4,P1]

동시에 실행할 집합 R은 최소한

\[
\sum_{v\in R}c_v\le P_{\rm admitted},\qquad
\sum_{v\in R}m_v\le M_{\rm budget}
\]

를 만족해야 한다. c_v는 job 및 내부 threads의 CPU 예약, m_v는 보수적으로 정한 memory 예약이다. 일률적인 single-thread jobs에 대한 대략적인 동시성 상한은 CPU 한도, `floor(M_budget/m_job)`, ready jobs 수, 명시적 policy cap의 최솟값이다. 알려지지 않은 peak RSS를 0으로 놓지 않는다.

BLAS/OpenMP/NumExpr/Rayon 등의 thread 수를 process 시작 및 관련 runtime import 전에 고정하고, job children이 허용 affinity를 상속하도록 한다. 외부 job 동시성과 내부 thread 동시성을 곱한 예약을 계산한다. coordinator가 별도 CPU를 실질적으로 소비하면 그것도 예산에 넣는다. 작은 9-cohort kernel에 내부64 threads를 일괄 부여하는 것과 독립 jobs를 나누는 것은 다르다. 현재 packet의 scheduler가 subprocess 방식이면 이를 MPI를 실제 실행한 결과로 보고하지 않는다. [P1]

memory blocking, CPU quota throttling, heterogeneity, shared I/O, native contention, unknown future releases가 있으면 K4의 단순 list-scheduling 상한 (3)을 실제 구현의 보장으로 사용할 수 없다. 고정 capacity 모델에서의 work/chain 하한은 참고할 수 있으나, 현재 자원과 시간을 측정하여 남은 DAG를 다시 계획해야 한다. NCP64 speedup은 같은 입력·실행 source·build·thread 설정에서 실제 throughput과 per-job latency를 기록한 뒤 판정한다.

### 선행 관계와 실패의 의미

ready 판단은 단순 파일 존재가 아니라 요구한 source/fixture/native/table identity가 맞는 완료·성공 terminal receipt를 기반으로 한다. failed/timeout parent를 완료로 취급하지 않고 후속 scientific job을 막는다. 이전 build가 유효하면 재사용하고 변경되었거나 부재하면 locked compile node를 먼저 실행한다. job 안의 cell 순서, qualification ladder, exact-base 뒤의 조건부 비교는 해당 계약을 유지한다.

새 사용자의 전체 미실행 DAG packet 요청은 준비된 독립 작업들의 범위를 확장할 수 있다. 이전 C21J의 작은 exact pilot 계약은 역사적으로 보존하고, C21K packet이 무엇을 새로 준비했는지는 별도 DAG에 적는다. 더 많은 실행 노드를 준비했다고 해서 full48·native matrix·source-age·spectral/angular·CaseB·signed-Bianchi·full-EoR·Grackle parity 등 기존 HOLD가 해제되지는 않는다. global error certificate도 생기지 않는다.

## 10. 문헌의 역할과 서비스 상태

이번 변화는 memoization, 공통 부분식 제거, list scheduling이라는 기존 원리를 특정 source와 보존된 trace에 맞춰 적용한다. 일반 원리의 신규성을 주장하지 않는다. 구체적 새 부분은 이 프로젝트의 exact scope, private binding, owned-copy, opacity 의존성, residual hit 집계, 원 scalar 연산 순서, 실행/백업/DAG의 분리된 증거 계약이다.

SciSpace에서 memoization 및 precedence scheduling을 자연어 질문으로 실제 검색했다. Michie 원 논문의 publisher 페이지는 abstract와 bibliographic metadata를 읽었다. full text를 읽었다고 적지 않는다. Graham 검색은 SciSpace가 1966 원전을 직접 주지 않아 Exa로 원문과 공식 Bell Labs record를 확보했다. SciSpace의 현대 OR-precedence 또는 resource-constrained 결과를 현재 단순 AND-precedence 모델의 정리로 대체하지 않았다. 추가 발견한 compile-time memoization 원전의 HAL fetch는 `SOURCE_NOT_AVAILABLE`이어서 그 본문 결과는 채택하지 않았다.

Wolfram context 첫 호출은 내부 오류였고 짧게 정리한 context 재시도는 성공했다. 그 뒤 evaluator 두 번이 성공하여 식·operation-tree·단위·작은 schedule을 검산했다. context의 검색 결과 중 `No Results Found`는 문헌 근거로 사용하지 않았다. 첫 evaluator의 permutation 벡터 부등식은 symbolic 상태로 남았으므로 두 번째 evaluator에서 q>0 조건하의 첫 원소 부등식을 실제 `True`로 확인했다. 실패와 후속 수정 모두 raw에 보존한다.

원문·논문 abstract가 들어 있는 service response는 분석용 private raw로 보존한다. 공개 unit/ZIP에는 논문 전체, 대량 abstract, private raw를 복제하지 않는다. `LITERATURE_LEDGER.json`에는 query, 실제 UTC, URL, 읽은 범위, 채택 여부, raw response hash와 짧은 자체 요약만 둔다. 우리 Wolfram query와 수학 결과는 별도로 재현 가능한 raw로 제공한다.

### 원전 및 공식 문서

- **L1.** R. L. Graham, *Bounds for Certain Multiprocessing Anomalies*, Bell System Technical Journal 45 (1966), 1563–1581. [DOI](https://doi.org/10.1002/j.1538-7305.1966.tb01709.x), [공식 Bell Labs 기록](https://www.nokia.com/bell-labs/publications-and-media/publications/bounds-for-certain-multiprocessing-anomalies/), [원 논문 스캔](https://ia801900.us.archive.org/27/items/bstj45-9-1563/bstj45-9-1563_text.pdf). 채택 범위: 원 모델, chain/idle proof, 고전적인 scheduling bound와 anomaly 존재. 실제 NCP 성능 근거로 사용하지 않음.
- **L2.** Python 3.12 공식 [functools 문서](https://docs.python.org/3.12/library/functools.html). 채택 범위: memoization의 인수/key 및 mutable result/purity 주의. 일반 decorator를 이번 exact scope와 동일한 구현으로 취급하지 않음.
- **L3.** Python 3.12 공식 [Floating-Point Arithmetic: Issues and Limitations](https://docs.python.org/3.12/tutorial/floatingpoint.html). 채택 범위: binary floating-point 표현과 연산별 반올림의 일반 배경. source-specific bit 증명은 K2–K3 및 focused evidence에 의존.
- **L4.** Linux kernel 공식 [Control Group v2](https://docs.kernel.org/admin-guide/cgroup-v2.html). 채택 범위: effective cpuset, memory.current/max 및 자원 admission 의미. 현재 NCP 값은 문서로 추정하지 않음.
- **L5.** Donald Michie, *“Memo” Functions and Machine Learning*, Nature 218 (1968), 19–22. [Publisher](https://www.nature.com/articles/218019a0), [DOI](https://doi.org/10.1038/218019a0). 읽은 범위는 publisher abstract/metadata. memoization의 역사적 선행 근거로만 채택.
- **W1.** `raw_wolfram/wolfram_epoch_cse_cost_check.json`: 실제 query와 결과. **W2.** `raw_wolfram/wolfram_schedule_dimension_check.json`: 실제 query와 결과. 수학 검산의 모델·한계는 위 각 절에 명시.

## 11. R1–R10 판정과 다음 실행 연결

|단계|이번 실제 작업|재사용/새 근거 및 판정|
|---|---|---|
|R1 질문 계약|원 RHS source bytes 보존, epoch-only 계수와 독립 DAG 최적화 분리|새 계약. native/IVP 실행 0, global null, HOLD 유지|
|R2 evidence/문헌|세 저장처 좁은 delta intake, source 읽기, SciSpace/Exa/공식 web 원전 확인|기존 C21J evidence 재사용; 검색 실패·범위 명시|
|R3 가정·단위|immutable fixture/source/global FP 환경, typed binary64, cgroup/CPU55/memory|K1–K3·단위의 새 구체화|
|R4 표현·반례|source free-variable 표기, ordered `mul` tree, epoch sensitivity, fixture permutation|새 도출; 근사 key·gas/tau 확장 배제|
|R5 실제 유도|K1–K4, 비용식 (1), work/chain (2), list bound (3)|source-specific proof와 고전 정리의 현재 적용|
|R6 독립 검산|Wolfram context 후 evaluator2회, source 읽기 검토|CAS 성공 및 초기 context 실패 보존; IEEE 전체 인증으로 과장하지 않음|
|R7 판별 계산|859/790 residual count, 329 misses, 530/461 hits, source-matched paired timing|root의 실제 replay 결과 읽음; 과거 부정적 timing 보존|
|R8 주장 상태|pointwise 수치 동등성 조건 충족 범위, trace PASS와 future native 분리|replay speedup NOT_ESTABLISHED; native/NCP scaling NOT_EVALUATED|
|R9 구현 계약|strict type guard 지적·수용, source-binding·ownership·deadline 독립 검토|source review PASS_SCOPED, 새 동적 시험은 root의 focused 영수증에 의존|
|R10 closeout|이 문서·source identity·literature/service ledger·CAS raw·allowlist|문서 준비 완료. 실행·게시·백업·DAG 완료 여부는 root의 별도 영수증|

새로운 강한 no-go 또는 세계적인 불가능성 정리는 제안하지 않는다. 실패한 service call, 낮은 timing ratio, 특정 schedule의 비효율은 해당 범위의 관측/반례로 남긴다. 완료한 C21I/C21J 연구를 미구현으로 되돌리지 않으며, 이후 검증은 변경된 C21K 의존성 및 실제 NCP admission/실행 결과에만 연결한다.
