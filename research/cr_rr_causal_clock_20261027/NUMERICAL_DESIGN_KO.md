# C2/C3/C5 candidate — HeIII causal clock engine

## 1. 실행 전 범위

생산 과학 실행은 아직 하지 않는다. 부모가 C4 resource/attempt 계약을 동결한 뒤 runner가 호출한다. 이 후보는 `clock_engine.py`, `clock_kernel.cpp`, 이 문서만 구성한다. source loading/pins, resource lease, process termination, correlated event export, stage/backup/publication은 부모와 별도 exporter 담당이다.

새 연구 계약의 60 aggregate CPU-second envelope와 primary30/independent15 등 예약을 읽었다. 시작 시 로컬 git HEAD는 이전 D `ec463db0...`이고 stage 파일은 부모가 작성 중이었다. 원격 새 branch를 조회한 HEAD는 R02 `08186920c58cea4cc01969710152bdf608a3ed77`이며 그 AGENTS 본문은 이전 14,446-byte source와 동일했다. R02 preflight의 WU `f949c21...`, REC synthesis `d6dbe39...`, 중앙 `5abe0d19...` 및 병렬 변경 없음 기록도 읽었다. 로컬/원격 HEAD 차이는 부모의 staged publication 절차이며 이 후보가 git 상태를 변경하지 않는다.

실제 primary reward는 기존 `rhs_physical18[:,10:12]`와 matching `solution_physical18[:,10:12]`의 HeIII count/kinetic 두 열이다. H1/HeI 결과는 재계산하지 않는다. K는 saved binary64 K의 exact represented real matrix다. source는 matching PR104 `source_z[1:]`, witness 후보는 기존 `t`다. 원 source의 `[0]` boundary mass는 runner/exporter가 보존한다.

## 2. 호출자와 자료 배치

`ClockEngine(library_path).prepare(diag,lower,upper,rewards,weights,witness,all_time,source_ids)`는 새 K나 hazard를 생성하지 않는다. 입력은 finite native binary64다.

- K arrays: (n), (n-1), (n-1).
- rewards/all_time: (n,2), native에서는 Fortran column-major.
- weights: (nsource,n), C row-major.
- witness: (n), 모든 원소 >0.
- 출력: source별 all-time count/kinetic intervals, witness beta lower와 Cw upper, immutable copied inputs.

`.horizon(problem,T,m,delta,capture=False)`는 실제 binary64 gamma 두 개를 명시하고 한 clock당 하나의 FP64 LAPACK DGTTRF factorization과 m회의 2-RHS DGTTRS를 수행한다. `source_rows`는 count_cm3/kinetic_eV_cm3의 두 endpoint 배열을 반환한다. gamma_hex와 exact Fraction \(a=\gamma T/m\)를 기록한다. `.clock(...)`은 C9 qualification 및 작은 controls를 위해 개별 shifted clock을 노출한다.

생산 primary는 capture=False다. qualification capture는 m<=16에서만 허용하며 `z_steps(m,n,2)`, `epsilon_steps(m,2)`, `step_radius(m,n,2)`, `cumulative(n,2)`, `cumulative_radius(n,2)`를 반환한다. epsilon/radius는 upward binary64이므로 C9는 `Decimal.from_float` 또는 float.hex→float.fromhex→Decimal.from_float로 정확히 복원한다. 문자열의 짧은 십진 표시를 exact upper로 해석하지 않는다.

## 3. 실제 native arithmetic 전제

확인된 host metadata는 GCC13.3, system liblapack.so.3/libblas.so.3다. link/ABI와 실제 결과 검사는 C4 이후다. 필요한 build command는 엔진이 순수 문자열 목록으로 제공하며 자동 실행하지 않는다.

- GNU/Linux x86_64, LP64 Fortran LAPACK int32 ABI.
- binary64 double, radix2의 64-significand-bit extended long double, 넓은 exponent.
- FE_TONEAREST, x87 precision control=extended, x87/SSE rounding nearest.
- MXCSR FTZ/DAZ off; `-fno-fast-math -ffp-contract=off -frounding-math`.
- `CR_STRICT_BUILD=1`, `CR_LAPACK_LP64=1`을 명시하지 않으면 compile fail.
- 환경 검사는 각 entry와 각 LAPACK solve 뒤에 반복한다. 플랫폼이 다르면 certificate를 조용히 약화하지 않고 fail한다.

LAPACK은 FP64 근사해만 생산한다. 인증은 실제 반환된 finite vector와 exact saved K/actual gamma의 잔차에 결속하므로 LAPACK 내부 연산의 backward-stability 상수나 완벽한 해를 가정하지 않는다. Native source에는 고정된 큰 science workload나 자동 재시도가 없다.

## 4. 빠른 잔차 bound의 직접 근거

\(\varepsilon=\mathrm{LDBL\_EPSILON}=2^{-63}\), unit roundoff \(u=\varepsilon/2\)다. short residual dot은 최대 5 products와 4 additions, 총 9 operations이다. long-double 값으로 정확히 확장한 binary64 operands를 사용한다. standard \(\gamma_9=9u/(1-9u)\)로 exact residual과 nominal residual \(\widehat\rho\)의 차를 bound한다.

동일한 rounded products의 absolute sum \(\widehat S\)에도 같은 종류의 bound를 적용하면 \(|\rho-\widehat\rho|<6\varepsilon\widehat S\)다. 구현은 더 넓은 **G=64ε**를 사용한다. \(h_i^{-1}\)는 처음에 nextafterl로 위쪽 bound를 만든다. row norm은

\[
 \widehat b_i=
 \operatorname{fl}\!\left[
   \operatorname{fl}\{(|\widehat\rho_i|+G\widehat S_i)\,
                     (1/h_i)_{\rm up}\}\,(1+G)\right]
\]

로 계산한다. 양의 최종 연산은 최대 4회이며
\((1-u)^4(1+G)>1\)이므로 마지막 inflation은 그 연산이 아래로 반올림한 경우까지 덮는다. 따라서 \(\widehat b_i\ge|\rho_i|/h_i\). row마다 nextafterl을 여러 번 호출하지 않아도 되는 이유다. G는 경험적 tolerance가 아니라 위 roundoff inequality에 여유를 둔 상수다.

0<S인 short residual row bound는 normal long double이어야 한다. 그 primitive의 binary64 operand products와 reciprocal-witness scaling은 넓은 extended exponent 범위에서 평가하며 실제 비정상 range는 fail한다. 그러나 반복되는 epsilon error certificate는 m이 커지면 LD underflow에 이를 수 있다. 따라서 positive operands의 umul/udiv 결과가 rounded0이면 nextafterl(0,+infinity)를 upper로 반환한다. 정확히 0인 입력의 분기만 0을 유지한다. 0이 아닌 subnormal 결과에도 다음 representable upper를 취한다. FP64 solver의 underflow 효과는 exact-target residual에 포함되며 양의 small tail을 0으로 인증하지 않는다.

Witness \(Kh\)와 generic dot products에는 nominal sum ± explicit error를 만든 뒤 scalar nextafterl을 적용한다. n-term dot의 absolute bound 계수는 \(4(n+1)\varepsilon\), m-term accumulated vector의 계수는 \(4(m+1)\varepsilon\)다. 이 계수들은 \(\gamma_{2n}/(1-\gamma_{2n})\), \(\gamma_m/(1-\gamma_m)\)보다 크며 이 workload에서 \(n\varepsilon,m\varepsilon\ll1\)이다. 이 두 계수와 short-dot G의 구별을 코드에 유지한다.

## 5. 정확한 shifted target와 오차 전파

FP64 factorization diagonal은 \(\operatorname{fl}(K_{ii}+\gamma)\)일 수 있다. residual은 반드시

\[
 \gamma\widehat z_{j-1}
 -K\widehat z_j-\gamma\widehat z_j
\]

를 별도 products로 평가한다. 첫 step의 RHS는 정확한 saved reward다. RHS gamma multiplication과 shifted diagonal 형성 손실도 이 잔차에 포함된다.

validated \(Kh\ge\beta h\)에서 \(\alpha_{\rm lower}\le\beta+\gamma\)를 사용한다. 안전한 lower가 rounding으로 gamma 이하로 접근할 때 \(\max(\gamma,\operatorname{down}(\beta+\gamma))\)를 사용해 여전히 유효한 양의 bound를 유지한다.

\[
 \epsilon_0=\eta_0/\alpha_{\rm lower},\quad
 \epsilon_j=(\gamma\epsilon_{j-1}+\eta_j)/\alpha_{\rm lower}.
\]

이 scalar recurrence의 곱·합·나눗셈은 upward nextafterl 연산으로 수행한다. 따라서 앞 step의 오차를 누락하지 않는다. all-time은 새 solve 없이 saved solution의 residual과 \(\beta\)로 인증한다.

벡터 \(\sum_j\widehat z_j\)는 long double로 누적하고 source contraction은 clock 마지막에 한 번 수행한다. 결과의 error는 **Cw·Σε + vector accumulation error + source-dot error + binary64 serialization error**를 포함한다. capture radius는 같은 오차를 성분별로 제공한다. 생산 primary에는 모든 recurrence vector를 저장하지 않는다.

## 6. Tail과 최종 endpoints

실제 gamma는 정확한 Fraction \(m(1\pm\delta)/T\)를 binary64로 한 번 반올림한 값이다. \(a=\gamma T/m\)는 그 encoded gamma와 encoded T로 다시 exact Fraction을 만든다.

Decimal80에서 Fraction a를 floor/ceiling으로 둘러싼다. correctly-rounded Decimal.ln/exp의 결과에 next_plus를 적용하고 나머지 양의/부호 민감 연산은 ROUND_CEILING으로 수행한다. 최종 q는 Decimal upper에서 binary64 upper로 변환한다. Python 공식 문서는 ln/exp의 ROUND_HALF_EVEN correct rounding과 next_plus의 next representable semantics를 명시한다: https://docs.python.org/3/library/decimal.html#decimal.Decimal.ln 및 #decimal.Decimal.exp. 이 경로는 exp/ln의 nominal 값을 그대로 인증값으로 쓰지 않는다. tail upper가 1 이상이면 fail한다.

horizon lower/upper는 native A/P bounds와 q_upper binary64를 **exact Fraction**으로 읽어 이론식을 계산한 뒤 각각 아래/위 binary64로 반올림한다. final scalar operations의 rounding을 숨기지 않는다. \(T=0\)과 infinity는 직접 zero/all-time endpoints로 제공할 수 있지만 finite clock API의 T는 엄밀히 양수·유한이다.

## 7. 작업량과 남은 검증

부모 제안 schedule은 2 finest cases의 3 levels 및 4 other cases의 finest-only, 6 horizons, 각 2 clocks다. 총 shifted solve 단계 수는

\[
 [2(64+256+1024)+4(1024)]\times6\times2=81408
\]

이며 각 단계는 2 RHS다. 모든 행 수를 2479로 잡은 단순 upper planning estimate는 약 \(4.04\times10^8\) row/RHS residual evaluations다. 실제 case 행 수는 C4 input metadata로 확인해야 한다. 이 수치는 성능 측정이 아니며 primary30 CPU-second 적합성은 아직 입증하지 않았다. native loop, inverse-witness precompute, clock 끝 source contraction은 이 비용을 줄이기 위한 실제 설계다. Parent runner가 reservation·wall guard를 적용하며 workload 변경은 실행 전 계약에서만 한다.

C4 이후 필요한 검증은 LP64 scalar solve control, native arithmetic guard, invalid signs/shape, zero reward, exact scalar Erlang identity, finite matrix controls, saved witness 실제 통과, 선택 m4 Decimal70 recurrence 비교다. 실제 primary certified width가 넓으면 넓은 결과를 남긴다. H1/HeI replay, new source history, physical heating/cascade 완료 또는 전역 오차는 주장하지 않는다.

## 8. 동결 계약과 준비 검증

부모의 R9 CODING_CONTRACT.json을 실제로 읽었다. finest clock width/all-time upper <=0.30, arithmetic scalar radius/all-time upper <=1e-4, grid endpoint difference <=0.005, domain endpoint difference <=1e-5, independent own-column relative <=5e-10 및 exact reference inclusion 기준은 그대로다. 엔진이 임의 tolerance로 결과를 좁히거나 기준을 바꾸지 않는다. 여러 level interval의 교차와 시간 monotonic tightening은 raw source_rows를 받아 부모 runner가 수행한다.

후보 생성 뒤 C++를 strict flags의 -fsyntax-only로 검사했고 exit0, build CPU 1.11162 s, wall 1.117081884 s, compiler max RSS 70,260 KiB를 관측했다. Python은 AST parse만 수행했고 metadata CPU 0.018992557 s, 문법 검사가 통과했다. Python import/native load/link/수치 검사 또는 실제 NPZ 입력 실행을 수행한 것은 아니다. 이 준비 CPU를 과학 실행 0회와 혼동하지 않는다. 생산 library build와 ABI control은 C4 이후의 별도 실제 영수증을 필요로 한다.

Exporter 호환 clock metadata는 time_units=proper_s, gamma_units=s^-1 및 records를 사용한다. a_numerator/a_denominator는 Python 정수이며, exact a_fraction 문자열도 보존한다. C9 metadata는 root가 case/T_s/clock_label/delta를 붙이고 source_id를 z로 대응한다. qualification arrays는 이미 합의한 축 순서로 반환한다.

C5 전 static 검토에 따라 scalar 입력은 Python/NumPy 정수·실수만 받으며 bool/np.bool_, 문자열, 일반 변환 가능 객체를 거부한다. 정수는 변환 뒤 exact Fraction 동등성을 확인해 binary64 표현에서 시간·rate 값이 조용히 바뀌지 않도록 한다. 표준 변환 오류도 ClockError로 통일한다. 수식·허용오차·native kernel에는 변화가 없다.

C9 static finding F1은 positive epsilon 곱·나눗셈의 LD rounded0을 exact0처럼 처리하던 경우다. umul/udiv만 위와 같이 보강했고 threshold는 유지했다. C6의 새 표적 control은 n=1, d=2^1023, r=gamma=2^-1074, h=w=1, m=8이며 마지막 epsilon/radius가 양의 upper로 남는지 확인한다. 이 문서 수정 시점에는 해당 control 또는 다른 과학 입력을 실행하지 않았다. 앞 scalar 입력 hardening과 구분되는 native 범위 수정이다.

