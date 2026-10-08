# G03: B0 정적 rate의 점근 구조와 최소 판별 계산

**판정: RESOLVED_WITH_LIMITATION.** 실제 B0 표현에 맞는 점근 구조와 M1–M4의 오프라인 판별 코드를 완성했다. 그러나 `G03_EMPIRICAL_ASYMPTOTIC_MODEL_IDENTIFIED`는 OPEN이다. 네 반경에서 얻은 값만으로 고유한 점근 모형을 선택할 수 없다. 다음 계산은 **z=−48,+48 a0 두 점**이다. 이번 연구에서 신규 native 호출·전파·권한 소비는 모두 0이다.

`REPORT_GAP_03` 원문은 sparse samples에 의한 R^-2 추정의 공백이다. 원래 상태 `REPORTED_RECOMMENDATION_NOT_VALIDATED`를 검증된 주장으로 사용하지 않았다. 출처와 파일 SHA256은 `SOURCE_EVIDENCE.json`, 정확한 수치와 개별 signed fitting 결과는 `ASYMPTOTIC_MODELS.json`에 있다.

## 1. 문헌이 실제로 뒷받침하는 범위

선택한 v3 DB fulltext를 열어 페이지를 읽었고, 모든 PDF의 SHA256을 DB와 비교했다. PDF 원문은 이 연구 디렉터리에 복제하지 않는다.

| source_id / 버전 | 읽은 위치 | 이 연구에서 사용하는 내용 / 제한 |
|---|---|---|
| RungeMicha1996 / user-upload publisher-formatted cited article, DOI 10.1103/PhysRevA.53.1388 | PDF 2쪽=인쇄 1389쪽 식(2),(3); PDF 3쪽=1390쪽 식(22),(23) | traveling atomic orbitals와 위치·속도 의존 ETF. 이 논문의 Mulliken/Loewdin population 및 W 기호는 여기의 Gram selected-projector Q와 rate W와 다르다. 논문의 식을 BASS W의 감쇠 정리로 읽지 않는다. |
| Toshima1999 / user-upload publisher-formatted cited article, DOI 10.1103/PhysRevA.59.1981 | PDF 1–2쪽=1981–1982쪽, 식(1),(2); PDF 7쪽=1987쪽 결론 | 양 중심의 bound/pseudostate 전개와 GTO radial representation, basis convergence 문제. 논문의 수렴 결과는 현재 18-channel FEM B0의 완전성 또는 rho power를 인증하지 않는다. |
| ThorsonDelos1978 / institutional copy of cited article, DOI 10.1103/PhysRevA.18.117 | PDF 1쪽=117쪽; PDF 4–5쪽=120–121쪽, §II.C 및 식(2.14) 주변 | ETF가 coupling과 asymptotic channel boundary condition에 관여한다. 이를 빼고 H의 원소만 읽어 W를 해석하면 안 된다는 배경. BASS finite-space rate bound는 제공하지 않는다. |
| Dollard1964 / user-upload publisher-formatted cited article, DOI 10.1063/1.1704171 | PDF 2–3쪽=인쇄 729–730쪽; PDF 1쪽은 표지 | Coulomb long range에서는 scattering asymptotic comparison을 수정해야 한다는 범위. 무한 Hilbert-space scattering theorem을 finite-basis selected population에 자동 이식하지 않는다. |

문헌의 역할은 표현과 물리적 주의점의 근거다. 아래 matrix cancellation과 counterexample은 현재 코드·정의에 대해 직접 유도했다. 획득된 본문만으로 필요한 근거가 충분하여 추가 광범위 검색은 하지 않았다.

## 2. 실제 B0는 무한지지 Slater/Gaussian 기저가 아니다

현재 `full_operator.py::_basis`는 동일한 radial mesh의 `FEMRadial`을 요구한다. `FEMRadial.evaluate`는 `r < edges[-1]`에서만 piecewise polynomial을 평가하고 밖에서는 함수와 코드상의 도함수를 모두 0으로 반환한다. B0 registry의 radius는 **64 a0**, lmax는 1이다. `exact_cross.py::...`의 `R >= 2*L` 분기는 cross S/H/D를 `DISJOINT_SUPPORTS`로 0 반환한다. 따라서 이 구현에서 **R≥128 a0이면 cross blocks가 정확한 코드 분기로 0**이다. z 임계는 sqrt(128²−2²)≈127.984374 a0이다. 조건부 exact conforming finite-element 모형에서도 경계항이 적절히 소거되면 같은 지지 집합 논리가 성립한다.

반면 무한지지의 국소화 원자궤도를 가정하면, 단순 예 `|phi_A|≤C_A exp(−alpha r_A)`, `|phi_B|≤C_B exp(−beta r_B)`에서 임의의 0<gamma<min(alpha,beta)에 대해

`alpha r_A+beta r_B ≥ gamma R +(alpha−gamma)r_A+(beta−gamma)r_B`.

따라서 적분의 나머지를 유계로 억제할 수 있는 polynomial-weight/derivative 가정 아래 cross overlap은 `O(exp(−gamma R))`이다. ETF의 절댓값 1은 이 envelope를 바꾸지 않지만 derivative에는 velocity와 phase factor가 추가된다. 이것은 가정하의 직접 envelope 유도이며 현재 positive-energy FEM pseudostate가 무한공간에서 그러한 지수감쇠 상태라는 주장이 아니다. 특히 현재 표본 R≤32.1는 128보다 훨씬 안쪽이므로 관측된 cross-block 비단조성도 지지절단 이후의 영값과 모순되지 않는다.

**결과:** 문헌의 exponential AO overlap과 Coulomb algebraic multipoles는 같은 이상화에서 공존할 수 있다. 그러나 현재 B0의 실제 최외곽 cross-tail은 compact-support 절단이며, 이를 지수함수 fitting으로 대체하지 않는다.

## 3. S,H,D에서 W까지의 cancellation

한 중심 블록에서 S는 시간에 무관하다. 코드의 `A_j=<phi_a|partial_j phi_b>`, `vA=sum_j v_j A_j`, 속도 v에 대해

`H = H0 + V_other +(i/2)((vA)†−vA)+(v²/2)S`,

`D = −vA −(i v²/2)S`.

따라서 직접 대입하면

`H−iD = H0+V_other +(i/2)((vA)†+vA)`.

정확한 conforming basis의 integration by parts로 `(vA)†=−vA`이면 ETF transport 항과 v² 항이 소거된다. 이 조건의 구현 독립검증은 G02에 속한다. 단순히 H와 D의 원소 norm이 크다는 이유만으로 W가 큰 것으로 읽을 수 없다.

R>128로 cross blocks가 사라지고 S가 block diagonal 상수일 때, S-whitened 좌표의 선택 projector를 P, effective Hermitian Hamiltonian을 h라 하면 `W_hat=i[h,P]`이다. 다음 두 조건을 추가로 요구한다.

1. isolated Hamiltonian h0가 선택 부분공간을 보존한다: `[h0,P]=0`.
2. moving-basis compatibility가 정확하다; 또는 정확한 호환 reference model과의 차이를 별도로 통제한다.

그러면 monopole `−Z/R`는 각 중심의 S에 비례하므로 선택 projector와 commute하여 selected rate에서 소거된다. **Hamiltonian에는 R^-1이 있어도 W의 주항이 R^-1일 필요는 없다.** 그러나 h0의 비영 off-block 또는 compatibility defect는 R과 무관한 잔여항을 만들 수 있다. 이 항을 fitting 잔차나 roundoff라는 이유만으로 삭제하면 무한 적분 가능성을 잘못 주장하게 된다.

G04 Route A의 저장된 coefficient 감사는 literal binary polynomial의 작은 비적합/isolated-generator 잔여항을 발견했다. 따라서 이 보고서는 실제 저장된 표현에 대해 `[h0,P]=0`를 인증하지 않는다. 그 판단과 수치는 `../majorant_analytic_20261001/ARCHIVED_RADIAL_AUDIT.json`과 `CONTINUOUS_MAJORANT_ROUTE_A.md`가 SSOT다. 이 제한은 이미 승인된 ±12 finite-window temporal 결과를 취소하는 주장이 아니다.

## 4. 어떤 거듭제곱이 가능한가

R>radial radius에서는 각 중심의 Coulomb potential에 대해

`1/|R−r| = sum_L r^L P_L(n·r_hat)/R^(L+1)`.

이 식을 l≤1 원자각함수의 곱에 적분하면 해당 행렬원소에서 L≤2만 남는다. 이는 `same_center_blocks`가 사용하는 finite angular projection이며, 공간 전체 potential을 L=2에서 근사 절단한다는 뜻과 구별된다. R>128에서 지지분리와 정확한 h0/ETF 소거까지 가정하면 whitened rate matrix는

`W_hat(R,n) = R^-2 W2(n) + R^-3 W3(n)`

꼴의 dipole/quadrupole 잔여항으로 표현된다. 행렬원소에 대한 statement이며 rho는 그 operator norm이다. 정해진 b=2 직선에서 `n=(b/R,0,±sqrt(1−b²/R²))` 역시 R에 의존한다. 일반적인 비회전불변 선택에서는 이 방향 변화도 scalar correction에 관여한다. 다만 아래의 완전 multiplet B0 이상화에서는 회전에 의한 unitary covariance가 방향 의존성을 scalar norm에서 제거한다. 고유값/특이값의 norm 연산 자체는 여전히 R^-4 등의 scalar correction을 만들 수 있다.

- **M1의 p=2:** dipole selected-to-complement coupling이 비영이고 지배적이면 자연스러운 후보다. 현재 source alone은 비영 leading coefficient의 인증이 아니다.
- **M3의 R^-3:** 일반적으로 quadrupole, 비회전불변 선택의 방향 correction, 비매끄러운 dominant branch에서 허용되는 항이다. 아래 smooth parity 조건에서는 소거되지만, 현재 overlapping-support 표본이나 literal stored model에 그 조건이 입증된 것은 아니다.
- **M4의 R^-4:** scalar norm expansion에 허용된다. R^-4가 fit에 들어간다고 실제 lmax=1 operator에 octupole을 추가한 것은 아니다.
- **M2의 자유 p:** 제한된 범위의 effective slope다. 비정수 p가 fitting된다는 사실은 새로운 물리적 asymptotic power 정리가 아니다.
- leading dipole가 선택 규칙으로 완전히 0이면 더 빠른 leading power가 가능하다. B0에는 선택된 s,p bound modes와 제외된 positive s,p pseudostates가 함께 있어 parity alone으로 모든 dipole selected-complement 원소의 소거를 주장할 수 없다. radial moments까지 확인해야 한다.
- parity에 의해 특정 `(l_a,l_b,L)` 원소는 0일 수 있지만, 전체 norm의 C3=0과 같은 statement는 훨씬 강하다. 현재 ±z의 수치대칭도 `rho(|z|)=C2/R²+C3/R³+...`의 C3를 금지하지 않는다.

R>128의 conditional far-field 식은 현재 16–32 표본의 유한구간 분석을 대체하지 않는다. 64 부근의 radial-support geometry와 128 부근의 disjoint-support regime을 한 fitting curve로 무비판적으로 합치지 않는다.

## 4.1 완전 multiplet에서 조건부 C3 소거

정확한 far-field ideal B0에서 각 retained radial mode는 완전한 m multiplet을 갖고 selected J도 bound multiplet 전체를 선택한다. 그러면 parity U와 회전은 P와 commute한다. 지지분리·정확한 ETF cancellation 이후 dipole block B2는 parity-odd, quadrupole B3는 parity-even이다. 따라서 선택/보완 공간에서 유도되는 parity를 사용하면

`f(epsilon)=||B2+epsilon B3|| = ||−B2+epsilon B3|| = f(−epsilon)`.

즉 f는 짝함수다. **leading singular value가 simple하여 f가 0 근방에서 매끄러운 branch이면** 1차 항이 0이고 `rho=C2/R²+O(R^-4)`이다. 이 조건하에서는 M3의 C3=0이 이론적으로 예측된다. 완전 multiplet의 회전 covariance 때문에 scalar norm은 n 방향에도 무관하다. 이는 유한 z에서 ± 부호가 수치적으로 맞는다는 사실보다 훨씬 많은 가정을 사용한다.

그러나 짝함수만으로 C3=0은 아니다. B2=[[0,1],[1,0]], B3=I이면 두 행렬은 위 parity 조건을 만족하지만 `||B2+epsilon B3||=1+|epsilon|`이다. epsilon=1/R>0에서는 R^-3 correction이 남는다. 따라서 degeneracy/cusp를 배제하거나 실제 asymptotic dominant singular pair의 simplicity를 검증해야 한다. 현재 sampled spectrum gap은 유한 반경의 gap이며 infinity limit의 그 조건을 대신하지 않는다.

`PARITY_SYMBOLIC_CHECK.json`은 B2=[[0,2],[1,0]], B3=diag(3/10,7/10)에 대해 exact rational polynomial algebra로 characteristic discriminant와 norm의 짝수 전개를 확인한다. 외부 CAS 사용 주장이 아니라 stdlib Fraction의 정확연산이며, 독립 NumPy spotcheck 세 개와 smooth/degenerate 사례 unit test를 함께 보존했다. 위 조건부 lemma는 실제 저장 계수의 잔여항이나 overlapping-support 표본을 없애지 않는다.

## 5. spectral branch switching

매끄러운 W에서도 `rho=max_j |lambda_j|`는 branch switch를 겪을 수 있다. 직접 만든 반례는 S=I,

`W=[[0,B],[B,0]], B=diag(R^-2,3R^-3)`.

고유값은 ±R^-2, ±3R^-3이고 `rho=max(R^-2,3R^-3)`이다. R=3에서 지배하는 branch가 바뀐다. `test_branch_switch_is_possible_despite_smooth_matrix`가 이 값을 확인한다. 이는 B0에서 실제 switching이 있었다는 주장이 아니라, scalar rho fit만으로 switching 부재를 증명할 수 없다는 반례다.

G07의 동일 저장 행렬 postprocessing 결과 `numerical_methods_20261001/E_RHO_SOLVER_RESULTS.json`에는 전체 spectrum이 있다. 양의 z에서 첫 |lambda| pair와 다음 pair는 다음과 같다.

| z | dominant eigenvalue magnitude pair | 다음 eigenvalue magnitude pair |
|---:|---:|---:|
| 16 | 1.8407204763249943e−3 | 7.688327753908880e−4 |
| 20 | 1.0737749206106931e−3 | 3.243568548798180e−4 |
| 24 | 7.506799347299690e−4 | 2.151627258150323e−4 |
| 32 | 4.2250541593842215e−4 | 1.219648811504561e−4 |

첫 pair의 ± 고유값은 절댓값에서 roundoff 범위로 중복된다. 따라서 첫째·둘째 |lambda| 차이가 작다는 사실은 서로 다른 dominant singular branch의 교차 증거가 아니다. 추적하려면 ± pair의 2차원 invariant subspace와 다음 pair와의 간격을 기록한다. 표본 사이의 crossing 부재는 이 네 표본으로 인증할 수 없다.

## 6. 정확한 네 반경에 대한 fitting

입력은 signed 8행의 원래 CSV이며 user message의 반올림 수치는 사용하지 않았다. 각 부호를 따로 fitting했다. 부호 간 rho의 최대 상대차는 1.4443e−15이나, 이를 8개의 독립 반경으로 취급하지 않는다.

모든 모형의 목적함수는 `sum((rho_fit−rho)/rho)^2`이다. 선형 M1/M3/M4는 column-scaled least squares, M2는 amplitude를 정확히 profile-out한 뒤 p∈[0,8]에서 scalar minimization한다. reference radius 24 a0는 conditioning을 위한 좌표선택이다. 오차분포가 없으므로 confidence interval, 통계적 유의성, AIC에 의한 확정 순위를 만들지 않았다.

| outgoing fit | coefficients (a0와 atomic time 사용) | 최대 training 상대잔차 | 반경 하나씩 제외한 최대 예측잔차 |
|---|---|---:|---:|
| M1 | C2=0.4440101441 | 7.225% | 9.210% |
| M2 | C=0.6491927571, p=2.1218080512 | 3.834% | 9.274% |
| M3 | C2=0.3852790090, C3=1.2937889436 | 3.652% | 9.313% |
| M4 | C2=0.5781351832, C3=−7.5172825271, C4=94.9250342510 | 1.317% | 10.689% |

Ck의 단위는 a0^k/atomic_time, M2 C의 단위는 a0^p/atomic_time다. M4는 3 parameters와 4 radii이므로 training residual 자유도는 1에 불과하다. leave-one-out에서는 3점을 3 parameters로 보간하며 바깥으로 extrapolate하므로 더 강한 validation을 제공하지 못한다.

현재 outgoing `rho R²`는 0.4785873238, 0.4338050679, 0.4353943621, 0.4343355672이다. 인접 effective slopes는 2.4458180, 1.9797744, 2.0085081이다. **|z|16을 제외하면 M2 p=1.99838745**이고 최외곽 두 점에서는 p=2.00850808이다. 이는 |z|20–32가 near-R^-2인 경험적 class와 양립함을 보여주지만, 16을 임의로 버린 뒤 확정 정리로 보고할 근거는 아니다. 16 데이터는 모두 보존한다.

## 7. 가장 작은 다음 판별 단계

먼저 **z=−48,+48 a0**를 각각 독립 계산한다. 기존 최외곽 z의 1.5배에서 두 부호를 평가하여 regime 혼합을 줄이고 signed consistency도 확인한다. all-four 모델이 예측하는 outgoing rho는 다음과 같다.

| M1 | M2 | M3 | M4 |
|---:|---:|---:|---:|
| 1.9237874529e−4 | 1.75507e−4 | 1.7860033717e−4 | 2.0051542360e−4 |

정확한 부호별 예측은 contract JSON에 고정했다. range/median은 13.48%이고 |z|40에서는 8.23%다. 큰 반경일수록 이 단순 지표가 커지지만, 64와128의 표현상 regime 변화 및 비용 자료가 없어 무조건 가장 먼 192를 택하는 것은 최적화가 아니다. ±48은 최소 batch 제안이지 비용 최적성 정리가 아니다.

또한 |z|20,24,32의 outer-three fits는 48에서 대체로 1.86–1.89e−4 범위에 모인다. 따라서 첫 signed pair가 모든 모형을 고유하게 구별해 준다고 약속하지 않는다. 첫 목표는 **16의 pre-asymptotic correction과 outer near-R^-2 predictive class를 구별하는 것**이다.

사전 규칙은 다음과 같다.

1. 현재 20–32 fitting과 전체 16–32 fitting의 holdout residual을 각각 먼저 기록한다. 48을 fitting에 넣기 전에 예측을 채점한다.
2. 경험적 screen은 상대잔차 ≤ max(2%, 10×새 resolution-pair rho 상대차)다. 이것은 operator error bound나 통계 confidence interval이 아니다. 부호별로 적용한다.
3. outer exponent가 2에서 0.05 이내이고 48을 넣었을 때 변화가 0.05 이내인지 보고한다. 실패하면 source/qualification/branch 구조를 우선 진단한다.
4. 성공하면 refit을 고정한 뒤 **off-grid −44,+44**를 새로운 holdout으로 별도 제안한다. 실패하거나 경향이 달라지면 진단 이후 **−64,+64**를 다른 regime 판별용으로 별도 제안한다. 어느 경우든 자동으로 다음 pair를 실행하지 않는다.
5. 최소 두 추가 signed pairs의 holdout과 fitting-window sensitivity가 통과해도, 여러 모형이 구별되지 않으면 `near-R^-2 empirical predictive class`로만 보고한다. M1의 exact law나 고유 coefficients는 닫지 않는다. G04/G05는 별개다.

`MINIMUM_STATIC_DISCRIMINATOR_CONTRACT.json`은 exact time hex, input/native/basis hashes, 기존 11-resolution ladder, query당 최대11·전체22 raw attempts, 최대2 workers/900초의 제안, stop/return schema를 포함한다. 모든 resource 값은 새 authorization에 명시적으로 결합해야 한다. 이전 8-query executor는 그대로 보존하고, 별도 `../static_validation_20261001/executor/g03_executor.py`에 strict two-query/budget22/context/nonce admission을 구현했다. `prepare_g03_authority.py`는 최종 clean source/input/resource를 결합하고 `supervise_g03.py`는 범위와 중단을 관리한다. 실행기가 고정한 `G03_SCIENCE_CONTRACT.json`은 초기 과학 규격의 immutable 사본이며 이 문서의 readiness 갱신으로 수정하지 않았다. 분석 코드는 `--return-json externally_verified_signed48.json --output G03_RETURN_ANALYSIS.json`으로 검증된 두 점 반환을 소비하고, 고정 예측의 오차를 먼저 채점한 뒤 refit과 다음 pair 예측을 출력한다. 반환 JSON은 `samples` 아래 각 점의 `z_a0`, `R_a0`, `rho_per_atomic_time`, `qualified:true`, `adjacent_relative_rho_discrepancy`를 요구한다. source/권한 receipt는 별도 검증을 거쳐야 하며 이 분석기가 대신 인증하지 않는다. 분석기와 native producer 구현이 모두 완료되었다. `g03_rate_postprocess.py`는 저장된 각 resolution의 cross block과 동일한 order20 same-center block에서 S/H/D를 복원하고 W, generalized eigensystem, dominant absolute-rate cluster의 S-projector와 다음 cluster gap, Hermiticity/SPD/residual, adjacent-rho 차이를 create-only로 반환한다. 이 agent가 실행한 후처리3 tests가 통과했고 executor owner가 synthetic 두 점/네 raw attempts부터 frozen holdout 분석까지 포함한 G02/G03 통합17 tests 통과를 보고했다. 통합검증의 정확한 명령·결과·환경은 `../static_validation_20261001/EXECUTOR_VALIDATION.json`에 있으며 이 결과 파일을 직접 읽었다. 실제 native 실행은 없었다. 남은 경계는 최종 source/resource binding과 fresh authorization이다.

## 8. 검증·상태·한계

실행한 명령:

```
python -m unittest discover -s research/gap_closure_20261001/asymptotics_20261001 -p test_asymptotic_models.py -v
python research/gap_closure_20261001/asymptotics_20261001/asymptotic_models.py
python research/gap_closure_20261001/asymptotics_20261001/parity_symbolic_checks.py
```

첫 TDD 실행은 구현 파일이 없어서 실패했고 `TDD_RED.log`에 남겼다. 구현 후 **7 tests PASS**: 네 정확한 synthetic 모델의 복원, 비양수·rank 부족 입력 거부, signed grouping/outer sensitivity 회귀, smooth-matrix branch-switch 반례, frozen holdout 채점 후 refit 순서, scope/qualification 위반 반환 거부, smooth parity 소거와 degenerate cusp의 구별. `G03_RUNTIME.json`은 실제 실행 환경 Python3.12.14 / NumPy2.3.5 / SciPy1.17.0을 기록한다. 생산 native operator·현재 propagator는 수정하거나 실행하지 않았다. offline code가 current SciPy production eigensolver를 검증한다고 주장하지 않는다.

닫은 범위는 실제 표현에 맞는 conditional power 구조, source/notation 분리, fitting 민감도 진단, 최소 판별 설계다. **NUMERICAL_METHOD_BLOCKER**는 sparse radii의 model nonidentifiability이며, G03 별도 two-query/22-attempt executor가 완성되어 IMPLEMENTATION_BLOCKER는 제거했다. 새 source/input/resource proposal과 명시적인 fresh authorization이 아직 없으므로 실행 경계는 **RESOURCE_POLICY_BLOCKER**다. 기존 G02 66/726 범위나 이전 static 권한은 재사용하지 않는다. unconditional asymptotic rho law, 연속 majorant, 무한적분, tail 시점의 P/Pdot는 여전히 미확보다.

`capture=false`, `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `original_capture_gap_resolved=false`, `continuous_global_supremum_bound=false`, `continuous_trajectory_error_bound=false`를 유지한다.
