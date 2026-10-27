# R6 독립 검토 — CR RR causal Erlang clock

## 판정

**PASS_SCOPED_CONDITIONAL_ON_STATED_PREMISES.** 검토 대상의 exact finite-matrix 정리와 반올림 인증 설계는 명시된 전제 아래 유효하다. 수정이 필요한 실제 finding은 **0개**다. 수치 구현, 저장 NPZ에서의 M-matrix witness, 실제 arithmetic enclosure의 실행 통과를 이 판정에 포함하지 않는다. 이들은 동결된 C 단계의 의무다.

검토한 exact 후보는 다음과 같다.

| 파일 | bytes | SHA256 |
|---|---:|---|
| `theory_candidate/THEORY_KO.md` | 21,837 | `c736e9ab4377bc3bbbdcacd7c7a86c3a3a65dfd7c0c6700d60eb298025d07c6a` |
| `theory_candidate/FORMULA_CONTRACT.json` | 13,315 | `73d06e1d244768490afa9df4a2a9c78246e3ed06bfd499f0a168a83e8d82ec07` |

이 판정은 이 두 파일의 hash에 결속된다. 후속 문서의 검토 상태 label 또는 링크 정리만 바뀌면 해당 비수학 delta를 확인할 수 있다. 전제·식·정규화·rounding 목표가 바뀌면 영향을 받는 부분을 다시 검토한다.

## 독립성·현재 권한·실제 수행

검토자는 `/root/latest_repo_survey`이며 이전 R1 read-only 조사에 참여했다. R5 후보의 작성, 새 solver 구현 또는 science 실행에는 참여하지 않았다. 제안된 문제와 식을 받은 뒤 **후보 본문을 읽기 전에** positivity, expectation, 양쪽 tail, 결정론적 bracket, M-matrix witness와 잔차 전파를 별도로 유도했다. 그 기록은 2026-10-27 **06:10:55.688 UTC**에 고정한 `INDEPENDENT_DERIVATION.md`, SHA256 `138c6030dafcd166181a1a3c043a2c8a6eacdbfd8036f7effb8039dc01f14e2c`다. 후보 작성자에게 이 독립 유도의 검토 항목을 전달했고, 이후 최종 후보의 식·증명을 대조했다.

R6 시작에 06:08:52–53 UTC의 원격 ref와 AGENTS를 실제 읽었다. CR 기준 branch의 HEAD는 D `ec463db0c7e5c7fb5070796071c926caa4db6445`, 중앙 HEAD는 M `5abe0d19df95db730e3e33bae0373c81ba37ce89`로 유지됐다. CR AGENTS SHA256 `8d62d9758fe173263eb3820c7b00ca569193bb7f912fc3d95d145e73d4a40970`, 중앙 AGENTS SHA256 `ab29a05cac922bd393dc04f7f280a0d4e1d7289ae6ea24291f48fd7cf7b2e8eb`도 R1 snapshot과 exact bytes가 일치했다. 관련 parallel branch는 R1의 06:02:31 UTC cutoff를 재사용한다. 게시 branch와 다음 노드의 새 HEAD 확인은 root의 각 단계 preflight가 맡는다.

`physmath-research-loop`의 R6 지침에 따라 핵심 전이, 부호, 차원, 극한, 경계, source 의미를 검토했다. 새로운 과학 수치 실행·기존 과학 replay·원격 변경은 각각 **0**이다. 스칼라 및 비대칭 2×2 예제는 종이 위의 닫힌식 검산이며 solver 실행으로 기록하지 않는다. metadata CPU는 미측정이므로 0이라고 기입하지 않는다.

## 핵심 수학 대조

### 1. Nonsingular M-matrix에서 필요한 성질

후보는 K를 저장 binary64 entries가 표현하는 exact finite matrix로 정의한다. continuum operator나 저장 전 HeI+HeIII exact diagonal sum과 구분한다. Z-matrix와 `h>0, Kh≥βh, β>0`를 확보하면 diagonal scaling 뒤 strict diagonal dominance와 Gershgorin으로 안정성이 나오고, `−K`의 Metzler 성질로 `exp(−Kt)≥0`가 나온다. 후보 식 (2)의 variation-of-constants identity도 부호가 맞다.

따라서 `K⁻¹≥0`, `0≤F_r(T)≤P_r`, `F′_r(T)≥0`를 얻는다. row substochasticity, 행합 0, `P_r≤1`은 필요하지 않으며 후보도 사용하지 않는다. 독립 예제 `K=[[1,−2],[0,1]], w=e1, r=e2`에서는 `P_r=2`이므로 unit probability cap이 일반적으로 부당함을 별도로 확인했다. 후보의 count density·energy reward 언어와 `P_r` cap이 맞다.

positive exact Thomas pivot 대안도 유효하다. 양의 pivot과 비양 off-diagonal이면 triangular inverse가 비음수다. 후보는 nominal floating pivot만으로 인증하지 않으며, 정량 오차에는 witness 또는 검토된 inverse bound를 추가로 요구한다.

### 2. Erlang resolvent와 recurrence

nonnegative integrand에 Tonelli를 적용하면

`E F(H) = ∫ wᵀexp(−Kt)r Pr(H>t) dt`

가 된다. Erlang survival polynomial과 matrix Laplace integral을 결합하면 factorial이 상쇄되어 정확히

`A_m = Σ[j=0,…,m−1] γ^j wᵀ(K+γI)^(−j−1)r`

를 얻는다. 후보의 `z0=B⁻¹r`, `zj=γB⁻¹z(j−1)`는 지수·합의 항 수·γ factor가 맞다. scalar `K=k>0`일 때 양쪽 유도 모두 `A_m=P_r[1−(γ/(k+γ))^m]`로 줄어든다. symmetry나 diagonalizability를 요구하지 않는다.

### 3. 양쪽 tail과 deterministic horizon

작은 평균 `T/(1+δ)`의 clock에는 `Pr(H−>T)` 상한을, 큰 평균 `T/(1−δ)`에는 `Pr(H+<T)` 상한을 써야 한다. 후보는 이 방향과 Chernoff tilt를 정확히 구분했다. 일반 encoded rate에서도 실제 `a=γT/m`를 사용하도록 명시했다.

단조성으로 `A−≤(1−q−)F(T)+q−P_r` 및 `A+≥(1−q+)F(T)`가 나오므로 최종 bracket

`max(0,(A−−P_r Q−)/(1−Q−)) ≤ F(T) ≤ min(P_r,A+/(1−Q+))`

이 성립한다. lower의 denominator와 tail correction, upper의 denominator 모두 맞다. tail upper bound로의 치환은 `P_r−F(T)≥0`를 사용하므로 signed reward에 직접 적용하면 안 된다. 후보는 count/kinetic의 nonnegative response를 먼저 구한 뒤 signed ledger로 옮겨 이 조건을 지킨다.

### 4. 극한·수렴

`T=0`을 exact endpoint로 처리하고 `γ=m/T`를 평가하지 않는다. 고정 m,δ에서 `T→0+` 및 `T→∞`의 bracket 극한은 각각 0과 P_r다. 후보는 exact arithmetic 극한과 실제 certificate 폭을 구분했다.

고정 δ에서 m만 증가시키면 두 clock은 서로 다른 시간에 집중하므로 bracket이 일반적으로 F(T)로 닫히지 않는다. 후보는 이 점과 충분조건 `δ_m→0, mδ_m²→∞`를 올바르게 명시하고, tail exponent 부등식으로 q→0을 증명했다. 이 분석은 수치 실행의 정확도나 생산 order를 미리 통과시키지 않는다.

## 반올림 인증 설계

후보 식 (15)–(20), 계약 F11–F15 및 numerical obligations는 다음 필수 항목을 모두 포함한다.

| 항목 | 확인한 설계 |
|---|---|
| exact target | 저장 K와 선언한 exact γ로 B를 정의하며 factorization의 rounded diagonal과 구분한다. |
| 양의 witness | h>0와 β>0에 대한 `Kh≥βh`를 exact 또는 rigorously enclosed arithmetic으로 확인한다. |
| 개별 solve 잔차 | `r−B zhat0`, `γ zhat(j−1)−B zhatj`를 exact target에 대해 제한한다. |
| 이전 오차 전파 | `εj=(γ ε(j−1)+ηj)/(β+γ)`로 이전 solve 오차를 누적한다. |
| scalar contraction | `wᵀh`, dot products, sum, error accumulation의 반올림을 포함한다. |
| all-time 값 재사용 | 저장된 근사해에 새 residual certificate를 붙이며 저장값을 exact 해로 가정하지 않는다. |
| tail 상한 | nominal log/exp나 underflow zero로 rigorous upper bound를 주장하지 않는다. |
| 최종 방향 | A− lower, A+ upper, P upper, q upper를 사용하고 L은 아래로·U는 위로 반올림한다. |
| 실패 처리 | interval 역전이나 음의 bin upper를 0으로 덮어 PASS시키지 않는다. |

이 설계는 구현 가능하고 수학적으로 충분하다. 아직 실제 배열에서 witness를 확인하거나 solver residual·tail 상한을 계산한 것은 아니다. C6에서 그 산출물과 arithmetic mode를 확인해야 numerical certificate를 승인할 수 있다. 이러한 미실행 의무는 theorem의 조건부 증명과 구분한다.

## Source, transpose, 에너지와 기존 경계

기존 frozen contract를 필요한 범위에서 실제로 읽었다. RR의 부호는 fast kinetic `−E`, internal `−I N`, retained photon `E+I N`이며, HeIII의 I=54.42 eV, native He4III12→He4II11 mapping과 조건부 elemental-to-He4 mapping을 유지해야 한다.

후보는 세 RR channel의 저장 count/kinetic RHS를 그대로 exact represented input으로 채택한다. kinetic RHS를 새 `λE` product로 바꾼 뒤 기존 all-time 해를 같은 문제로 취급하지 않는다. `projection[1:]`와 초기 `projection[0]` boundary mass를 구분하고 후자는 기존 pulse ledger에 남겨 RR reward를 0으로 둔다. 따라서 이전 source projection과 경계 해석을 변경하지 않는다.

time bin 차이의 lower `max(0,L2−U1)`와 upper `min(P^U,U2−L1)`는 같은 exact 입력의 endpoint bounds에서 바로 따른다. 공통 N,E에 대한 signed energy mapping은 올바르다. 특히 후보 본문은 interval 끝점을 독립 선택한 조합이 모두 에너지를 보존한다는 뜻이 아니며, exporter가 공통 N,E의 correlation을 유지해야 한다고 명시한다. SI count factor10⁶ 및 energy factor10⁶×1.602176634e−19를 한 번만 적용하는 단위도 맞다.

forward population은 `n′=−Kᵀn+b`이고 backward reward는 K를 사용한다. 후보의 convolution 식은 이 transpose와 부합한다. 일반 vector history와 고정 shape `b(t)=w q(t)`를 구분하고, scalar saved-pulse kernel만으로 arbitrary energy-time source가 이미 계산됐다고 주장하지 않는다.

본 결과의 time-bin 평균은 **선언한 pulse의 조건부 반환률**이다. 실제 연속 injection history·exposure·donor/recipient nb·pointwise instantaneous RHS를 공급하지 않는다. z snapshots는 history가 아니고 다른 100 K source를 현재 10000 K bath에 이식하지 않는다. retained photon ledger는 photon cascade, escape 또는 physical heating 완료가 아니다. 이 구분은 원래 source-qualified 공급 범위와 일치한다.

## 남은 의무와 진행 수치

이 R6의 미수행 수치 의무는 이미 후보에 명시돼 있으며 새 검토 finding으로 부풀리지 않는다. C 단계는 선택 case/horizon/order·예산을 고정한 뒤 실제 K의 sign/shape와 양의 witness, recurrence 및 all-time residual enclosure, actual γ와 q의 일치, outward arithmetic, 실제 interval 폭과 export 의미를 확인해야 한다. nominal high-precision agreement만 얻으면 numerical certificate는 diagnostic 또는 unresolved로 남긴다.

새 물리 공급자, 전체 cascade, 실제 history, 물리 heating 또는 전역 error bound는 승인하지 않는다. 원래 N4/N5 partial, N6/N7 predecessor gate, `UNKNOWN_NO_ACK`, 별도 예산, global completion/error null과 L4 false를 보존한다. 이 단위의 중앙 완료 수 증가는 **0**이며 현재 shared 표시는 **27/88**이다.

검토 산출물은 root가 해당 단계의 source ZIP·이중 백업·게시 receipt에 결속한다. 검토자가 원격 변경을 수행하지 않았다.
