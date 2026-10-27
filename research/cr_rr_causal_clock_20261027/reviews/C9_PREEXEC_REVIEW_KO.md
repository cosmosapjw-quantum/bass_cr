# C9 사전 독립 코드·산술 검토

## 판정과 범위

**PASS_STATIC_AFTER_TARGETED_REPAIR — 실제 실행·참조 결과 판정은 대기.** 생산 native/Python certificate, finite-bin exporter 및 새 실행 pipeline을 실제로 읽었다. 실행 전에 확인한 두 지적의 소스 수정이 반영됐다. 이 판정은 아래 exact source를 C6 실행과 독립 참조 검증에 넘길 수 있다는 뜻이며, 아직 numerical PASS 또는 최종 C9 완료를 뜻하지 않는다.

| 대상 | 검토한 현재 SHA256 |
|---|---|
| `implementation/clock_kernel.cpp` | `0629567c34be30c4ade93755a1c77d62e5737cfbe5c45c185636b01dda4721a9` |
| `implementation/clock_engine.py` | `8285c73f0d0e38df2d23d95e259cc94e53aeac531e936da45e1fdd88c51f046a` |
| `implementation/export_adapter.py` | `9c29468f0b0adbefc891c1df00d5757148f9cdbcf00ba1aa830fd026e25d13d1` |
| `implementation/runner_common.py` | `660fc3af3a786b7a1727892b90499f2a3f219c704c50bb7521adebacc1ba4db1` |
| `implementation/primary_runner.py` | `cffc760e37634cf1c5066bfcf586d8b1fd0b3230745f82717efd5ff83e4b1a73` |
| `implementation/controls.py` | `38b04da6c7c25f890a8a54d0bcdc8fab2bff4a94c735e8319a90820f79ae4a9d` |
| `implementation/reference_runner.py` | `ee4693cc9619c8afc2160c04206e5933ed98246f2ada1625508ba54e9cbf298a` |

모든 경로의 unit root는 `research/cr_rr_causal_clock_20261027`이다. Python engine은 `6cb9625a…`를 본문 전체 검토한 뒤 현재 `8285c73f…`와 실제 diff를 비교했다. 차이는 `-llapack/-lblas`에서 설치된 versioned library 이름 `-l:liblapack.so.3/-l:libblas.so.3`로 바뀐 link flags뿐이며 strict FP flags와 수식은 유지됐다. 실제 library의 ABI와 수치 동작은 C6의 scalar/finite-matrix control로 확인해야 한다.

## 지적과 소스 교정

### C9-F01 — 양수 error bound의 long-double underflow

원 native SHA `ec8999265aead913369b05bb9130349f15b4de6c1a764357bddebd8d4037faf8`에서 `umul`과 `udiv`는 양의 exact 곱·몫이 rounded 0이 되어도 `up(0)=0`을 반환했다. 이 값은 양의 참값의 상한이 아니다. normal short-dot 연산의 상대오차 분석으로 이 문제가 해결되지는 않는다. 반복되는 epsilon은 short residual의 binary64 operand product보다 훨씬 작아질 수 있다.

실행 없이 구성한 구체적 예는 n=1, d=2¹⁰²³, r=γ=2⁻¹⁰⁷⁴, h=w=1, m=8이다. exact K는 nonsingular M-matrix이고 기존 입력 guard를 통과하는 finite binary64 값들이다. FP64 recurrence 중심은 0으로 underflow하지만 마지막 exact reward는 `γ⁷ r/(d+γ)⁸>0`, 약 2⁻¹⁶⁷⁷⁶이다. epsilon의 extended 나눗셈도 0으로 underflow하면 해당 step의 capture radius가 0이 되는 반례다. 이는 **실제 frozen research grid에서 관측한 실패가 아니라 허용된 산술 입력에 대한 명시적 코드 반례**다.

수정된 두 helper는 exact-zero 입력의 0을 유지하고, positive operands의 rounded result가 0인 경우 `nextafterl(0,+∞)`를 반환한다. nearest/gradual-underflow 전제에서 이 양의 최소 표현값은 exact 양수 결과의 상한이다. nonzero rounded result에는 기존 `up`를 적용한다. 수정된 source를 실제로 읽었고 unit에도 같은 `0629567c…` bytes가 복사됐음을 확인했다. 설계의 모든 certificate intermediate가 normal 범위에 남는다는 이전 단정도 철회됐다.

**상태:** `STATIC_REPAIR_VERIFIED; C6_TARGETED_RUNTIME_CONTROL_PENDING`. Root가 위 n=1,m=8 example에 대해 exact Fraction 마지막 값의 capture-radius 포함을 확인하는 control을 추가한 것도 실제 코드에서 읽었다. 그 control의 실행 PASS를 아직 주장하지 않는다.

### C9-F02 — minimum nominal metadata의 초기값

원 primary SHA `2e619dd9…`는 `minimum_nominal=0.`으로 시작했다. 모든 nominal vector가 양수일 때 실제 최소 대신 0을 `minimum_nominal_solution`에 기록했다. 음수 검출 gate는 유지됐지만 기록 이름과 값이 달랐다.

현재 `cffc760e…`는 `float("inf")`로 초기화한다. 모든 실제 clock의 최소를 기록하면서 기존 음수 검출 기준을 바꾸지 않는다. 이 변경을 실제 파일에서 확인했다.

**상태:** `CLOSED_STATIC`. 수식·허용오차·실행 범위 변경은 없다.

## Native certificate의 코드 대조

### 산술 환경과 short residual

entry마다 binary64 double, 64-significand-bit extended long double, 충분한 exponent 범위, nearest rounding, x87 extended precision, SSE FTZ/DAZ off를 확인한다. 각 LAPACK factor/solve 뒤에도 환경을 확인한다. compile flags는 fast-math와 contraction을 막고 rounding-sensitive arithmetic을 보존한다. 이 조건은 환경을 임의 변경해서 통과시키는 절차가 아니다.

`LEPS=2⁻⁶³`, unit roundoff u=LEPS/2다. recurrent row residual에는 최대 5개의 product와 4개의 signed addition, 총 9개 연산이 있다. 같은 rounded products의 absolute sum을 Ŝ라 하면, product·sum 양쪽의 오차를 반영한 `gamma9/(1−gamma9)` 계수는 코드의 `6*LEPS`보다 작다. 구현의 `G=64*LEPS`는 그보다 넓다. `(|rho_hat|+G*Ŝ)*(1/h)_up*(1+G)`의 양의 마지막 연산들에 대한 하향 rounding도 `(1−u)^4(1+G)>1`의 여유로 덮인다. row bound의 finite/normal 조건을 검사하며, binary64 operands의 nonzero product는 이 extended exponent 범위 안에서 표현 가능하다.

앞서 발견한 F01은 이 short-dot 분석의 부호나 연산 수 문제가 아니라 이후 반복 error-bound 연산의 underflow 문제였다. 수정된 helper는 normal·subnormal upper arithmetic을 분리하여 그 공백을 닫는다.

### Exact shifted target와 양의 witness

LAPACK factorization은 rounded binary64 diagonal `d+gamma`를 사용할 수 있다. 인증 residual은 이를 재사용하지 않고 `rhs − d*x − gamma*x − lower*xprev − upper*xnext`를 separate long-double products로 계산한다. j>0 RHS도 `gamma*previous`를 정확한 target product로 평가하므로 FP64 RHS formation 손실과 diagonal-addition 손실을 포함한다.

`witness_beta`는 `Kh`의 signed row sum에 explicit short-dot error를 빼고 아래로 나눠 β를 만든다. beta의 binary64 하향 변환이 0이면 실패한다. `cr_clock`은 전달된 β와 Cw upper를 다시 검증한다. alpha의 `max(gamma,down(beta+gamma))`는 exact beta+gamma 이하이면서 양수인 유효한 lower bound다.

오차 recurrence는 gamma*epsilon, eta와의 합, alpha로 나눗셈을 각각 상향 연산으로 처리하고 epssum도 상향 누적한다. 마지막 step의 residual만 사용하는 경로는 없다. all-time cap도 기존 approximate solution의 actual residual과 beta로 둘러싸며 새 all-time solve나 저장값의 exact 가정을 사용하지 않는다.

### 누적·source contraction·capture

n-term dot에는 `4(n+1)*LEPS`, m-term vector accumulation에는 `4(m+1)*LEPS`를 사용한다. 지원된 n,m에서 이 계수는 product/sum 및 computed absolute sum의 오차를 포함하는 표준 gamma 계수보다 크다. source weights가 비음수이므로 accumulated-vector error를 source에 곱하는 방향이 맞다.

scalar radius에는 `Cw*sum(epsilon)`, vector accumulation error, source-dot error와 binary64 중심 변환 차이가 포함된다. 최종 lower/upper는 LD 다음 표현값과 directed binary64 conversion으로 만든다. capture의 step radius 및 cumulative radius도 같은 오차를 성분별로 포함하며 `(m,2,n)` native 배치에서 `(m,n,2)` reference 배치로의 transpose가 맞다.

## Python tail과 최종 endpoint

Gamma는 exact Fraction `m(1±delta)/T`를 binary64로 한 번 변환한 뒤, 실제 `gamma.hex()`와 encoded T로 a=gamma*T/m을 다시 구성한다. minus a>1, plus 0<a<1 검사를 한다. ideal δ tail을 rounded gamma에 그대로 적용하지 않는다.

Decimal80의 a lower/upper에서 `ln(a_upper)`를 correctly rounded 값의 next-plus로 올리고, `1−a_lower`와 합·곱을 ceiling으로 계산한다. 이어 exp의 next-plus를 구하고 binary64 upper로 변환한다. ln 증가성과 각각의 outward 방향 때문에 exponent와 q는 모두 upper다. q의 underflow를 0으로 승인하지 않고 0<q<1을 요구한다.

검토한 실제 runtime metadata는 Python **3.12.14**, decimal **1.70**, libmpdec **4.0.0**이다. runtime method docstrings와 [Python 공식 decimal 문서](https://docs.python.org/3/library/decimal.html#decimal.Decimal.exp)에서 ln/exp의 ROUND_HALF_EVEN correct-rounding 보장 및 next-plus 의미를 확인했다. 이 확인은 문서·환경 read-only 조사이며 함수의 과학 수치 실행이 아니다.

마지막 horizon bracket은 exported A/P/q를 exact Fraction으로 읽고 R6 식을 계산한 뒤 바깥쪽으로 반올림한다. all-time upper와 A upper의 교차도 A≤P에 근거한다. T=0은 solve 없이 exact zero RR로 처리한다. 이 검토에서 닫힌 R6 정리를 반복 검토하지 않았다.

## Exporter와 새 pipeline

Exporter는 공통 N,E를 exact encoded binary64 interval로 유지하고 exact rational map으로 fast `−E`, internal `−54.42N`, retained photon `E+54.42N` 및 species count를 생성한다. 계수 부호에 따라 interval 끝점을 바꾸는 코드와 SI 변환 한 번의 경로가 맞다. common-basis correlation을 저장하고 independent interval corners의 에너지 합이 0이라고 주장하지 않는다. explicit nb control만 native25를 만들며 actual nb=null에서 native25·instantaneous RHS·actual source history는 null이다.

동일 pulse window의 canonical event ID는 clock order·bound 값·nb 선택을 제외한다. `PulseReturnBook`은 source/case/operator/bath를 묶고 같은 window의 중복을 막으며, 겹치는 cumulative 진단들을 자동 합산하지 않는다. source bytes와 upstream certificate 자체를 exporter가 검증했다고 주장하지도 않는다.

새 `runner_common`은 source-pinned 같은 bytes를 relocated 경로에서 읽고 saved HeIII RHS10:12·all-time10:12·t witness와 original projection[1:]만 가져온다. 실제 NPZ member read에서 t의 길이 2479와 해당 operator/source E-grid bytes의 동일성을 확인했다. source[0] boundary와 raw atom·bath pin은 provenance에 남는다.

primary는 raw levels를 보존하고 같은 horizon의 유효 intervals를 교차한 뒤 monotonic lower/upper를 각각 안전한 방향으로 tightening한다. bins는 exact Fraction으로 endpoint 차이를 계산한다. 한 source/case book에 여섯 개 disjoint bin만 export하며 cumulative views를 같이 합산하지 않는다. grid/domain endpoint 비교는 동결된 별도 수용 기준으로 남겨 실패 시 보존한다. 실제 interval 폭·격자 gate가 통과했는지는 아직 확인하지 않았다.

controls의 m4 qualification output은 합의한 NPZ와 JSON metadata 형식이다. reference wrapper는 stdlib만 import하고 runpy로 별도 checker를 호출한다. `runner_common` 또는 production engine을 reference process에 import하는 경로는 없다. copied reference SHA는 `4d1bbb8cbb9f12cbc25fd4847f48239d793ac70e96196c09f2c10eab33c5f7e1`로 준비한 독립 코드와 동일하다.

## 후속 판정과 보존

다음은 이미 C 계약에 속한 실제 실행 의무다: versioned LAPACK library의 scalar/2×2 control, F01 targeted underflow control, zero reward 및 input rejection, 실제 stored witness, frozen primary footprint·width/grid/domain gates, 32-RHS Decimal70+directed-Decimal100 reference, 실제 export·budget/attempt receipts. 이 사전 검토는 이 실행들의 결과를 만들어내지 않는다.

본 검토자의 과학 실행·기존 과학 replay·원격 mutation은 각각 0이다. metadata CPU는 미측정이며 0으로 기록하지 않는다. Root의 linker 실패·재빌드 receipt는 별도 실제 자료이며 이 검토가 그 비용을 초기화하지 않는다. 최종 C9는 실제 실행 코드/binary pins, 결과와 해당 비용 ledger를 읽고 판정한다.

shared 진행 **27/88**, count effect **0**. N4/N5 partial, N6/N7 predecessor gate, 과거 UNKNOWN_NO_ACK·예산과 isotope/provider 범위를 보존한다. caloric partition이나 retained photon ledger를 physical heating으로 승격하지 않는다.
