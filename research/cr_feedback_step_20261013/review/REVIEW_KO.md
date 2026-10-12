# BASS_CR 온도·조성 피드백 연구 단위의 독립 통합 심사

연구 단위: **CR-THEORY-FEEDBACK-20261013**  
검토자: **/root/feedback_literature_review**  
판정: **PROMOTE_SCOPED / PASS**  
승인 대상: **FB1–FB7의 명시된 가정 아래 직접 유도된 결과와 두 reference 구현**  
열린 차단 지적: **0개**

사건별 공통 extent의 재고 상계, 온도·조성 계수 피드백의 존재·수렴 조건,
잔차에서 온도로 이어지는 오차식, 공변 투영 및 주어진 Bianchi I 기하 부분 흐름을
하나의 조건부 이론 결과로 승인한다. 이 판정은 `CANDIDATE_MANIFEST.json`의
정확한 파일에 결속된다. 최종 기계 판정과 파일별 SHA-256은 `DECISION.json`에 있다.

## 1. 독립성, 읽은 범위와 판정 방법

검토자는 사건 map, feedback 정리, angular lift, reference 코드, 작성자 검산과
Wolfram/xAct 검산의 생성·설계에 참여하지 않았다. 완성된 후보를 읽고 최소 교정을 요청한
뒤 교정 내용을 다시 대조했다. 이번 독립 검토에서 과학 검산을 새로 실행한 횟수는 **0**이다.
파일 digest 및 실행 입력과 현재 파일의 일치 여부 확인은 과학 실행과 구분했다.

읽은 대상은 세 유도 문서 전체, 두 feedback 가정·오차 JSON, H/He 사건 JSON,
`event_capacity_step.py`, `feedback_solver.py`, 두 Python 검산 프로그램,
세 Wolfram 검산 프로그램과 xAct body, 실행 결과 전체, xAct 설정 관측,
최종 후보 `CONTRACT.json` 및 `CLAIMS.json`이다. SciSpace와 Exa로 확인한
4개 원전의 실제 읽은 절과 조건은 `../LITERATURE_KO.md`, `../SOURCES.json`에 따로 기록했다.

독립 방법은 다음과 같다.

1. 공유 재고의 전체 소모량을 사건별 분모의 공통 항으로 직접 상계했다.
2. 사건 열의 원소·전하·에너지를 대입하고 EOS의 유한 차를 역대입했다.
3. compact convex domain, Brouwer 적용 조건, 분수 차의 Lipschitz 상계,
   contraction 잔차, 실제 경로의 첫 이탈 논증 및 Gronwall 적분을 확인했다.
4. 공변 에너지·입자수 투영의 부호와 c의 위치, 물리 운동량의 에너지 미분,
   기하 일 장부 및 동일 상태 공간 위의 Lie 합성을 확인했다.
5. 코드가 반환한 상태·extent·잔차·종료 상태의 의미를 정리와 대조하고,
   실제 결과를 프로그램 및 입력 파일 identity와 연결했다.

## 2. 승인한 과학적 주장

| 주장 | 승인 내용 | 적용 조건과 확인 근거 |
|---|---|---|
| FB1 | 공통 extent map의 비음성, 양의 초기 소모 재고의 명시적 하한, 모든 LS=0 불변량 보존 | 유한 고정 S, 유한 비음수 proposal, h≥0, 초기 zero donor의 사건별 비활성화. 직접 상계와 사건 검산. |
| FB2 | 12상태·10사건 H/He family의 원자핵·전하·active/thermal/chemical/radiative 에너지 회계 및 EOS | 고정 현재 에너지 channel, 핵 recoil 생략, 양의 capture-energy quadrature, 이상 thermal bath. 사건별 직접 대입과 40개 영잔차. |
| FB3 | 양의 온도 compact domain의 고정점 존재, 계산한 q<1에서 유일성과 Picard 수렴, step 선택식 | domain 전체의 연속·비음수 계수, self-map, U 하한과 필요시 밀도 하한. 일반 q는 정의역에서 검증해야 한다. |
| FB4 | 이산 잔차와 계수 오차의 온도 증명서, 실제 ODE endpoint defect의 별도 온도 증명서 | 같은 norm·양의 count 하한·Lipschitz 상수·실제 경로의 domain 유지. 실제 ODE 오차에는 physical G를 사용한다. |
| FB5 | frozen-donor capacity map의 일차 정합성과 명시적 local O(h²) 상계 | 초기 propensity 일치, 정칙 support, 시간·상태 Lipschitz. 초기 zero donor branch의 vanishing 조건 및 경계 근처 균일 상계의 추가 조건을 유지한다. |
| FB6 | 공변 energy/current 투영, 정확 Bianchi momentum·thermal subflow, signed stress-work 장부, 일차 Lie 결합 | prescribed diagonal metric, even active packets, 동일 angular chart/연속 collision closure, 양의 scale factor, 정확도에는 H_i의 시간 Lipschitz. |
| FB7 | 중성 한 사건 비선형 예제의 정확 endpoint와 독립적인 실제 rate defect | 선언한 scalar segment 및 η=4/17. x*=1/4, c_vT/E0=7/10, q=170/841, E=6E0, Q=0, defect=−17κ0/128. |

FB1의 `CLAIMS.json` 위치 표기는 사건 문서의 ES-A/ES-B와 feedback 문서의
FP.7–FP.9를 함께 가리키는 것으로 읽었다. 실제 증명 경로는 두 문서에서 확인했다.

### 공유 재고 상계가 닫히는 이유

`C=(-S)_+`, `c_i=Σ_r C_ir f_r`라 쓰면, 초기 재고 `y_i^n>0`를 소모하는
모든 사건의 분모에는 같은 `c_i/y_i^n` 항이 있다. 따라서

$$
\sum_r C_{ir}\xi_r
\le \frac{h c_i}{1+h c_i/y_i^n},
\qquad
\Phi_i\ge \frac{y_i^n}{1+h c_i/y_i^n}>0.
$$

초기 0인 donor의 관련 사건을 loads 계산 전에 비활성화하므로 그 행에는 생산만 남는다.
동일 extent를 모든 행에 적용하면 `LΦ=Ly^n`은 대수적으로 성립한다.
이 성질은 여러 흡열 채널이 같은 U를 소모할 때도 유지된다.
유한 h 전체에서의 이 map 성질과, 주어진 계수 정의역을 보존하고 고정점을 구하는
추가 step 조건을 각각 적용했다. 세부 검토는 `EVENT_REVIEW_KO.md`에 있다.

### 피드백과 연속 오차를 구분하는 이유

온도는 `T=U/(c_v N_th)`이고 `N_th=N_nuc+N_e`다. 재고의 유한 갱신 뒤
이 EOS를 계산하면 ionization이 늘린 입자수에 따른 온도 변화까지 포함한다.
양의 thermal floor를 갖는 compact domain에서 직접 구한 map Lipschitz 상수가
q<1이면, 실제 잔차 ρ와 map 근사 상계 ε는

$$
\|z-y_*\|_{\infty,a}\le\frac{\rho+\varepsilon}{1-q}
$$

를 준다. 온도 오차에는
`a_U/(c_v N_min)+T(z)a_N/N_min`을 곱한다.
이 증명서는 선언한 capacity map의 정확 고정점을 대상으로 한다.

실제 donor와 실제 physical vector field를 쓰는 endpoint defect에는
`(z-y_n)/h−G(z,t_n+h)`가 들어간다. 선형 재구성 경로와 Gronwall을 적용하면

$$
A(L,h)=\frac{e^{Lh}-1}{L},\qquad
B(L,h)=\frac{(Lh-1)e^{Lh}+1}{L^2},
$$

및 `A(0,h)=h`, `B(0,h)=h²/2`가 나타난다. 실제 ODE 경로의 동일 domain 유지와
G의 시간·상태 Lipschitz 조건이 함께 필요하다. 두 종류의 증명서가 각각 무엇을
제한하는지 코드·가정·오차 JSON에 일관되게 나타난다. 세부 검토는
`FEEDBACK_REVIEW_KO.md`에 있다.

## 3. 기하 단계의 직접 심사와 교정 완료

서명 `(-+++)`, `n·n=−1`에서

$$
-n_b\nabla_aT^{ab}
=D_n\rho+(\rho+p)\Theta+\pi^{ab}\nabla_a n_b
$$

가 곱의 미분과 정규화로 나온다. proper time 변환 `dot=cD_n`,
`θ=cΘ`, `σ=c\barσ`를 적용하면 energy source는 `Q=−c n_bF^b`이고,
current `J_s=c n_s n`의 발산은 `dot n_s+θ n_s`다. 문서의 c 배치는
두 source를 같은 초 단위 고유시간에 연결한다.

Diagonal Bianchi I의 공간 Killing momentum `P_i`가 일정하므로
`p_i^+=a_i^n p_i^n/a_i^+`는 정확한 부분 흐름이다. 상대론적 kinetic energy의
도함수 `∂W/∂p_i=v_i`를 대입하면 `dot W=−Σ H_i p_i v_i`다.
Packet 합은 `dot U_A=−V K:Π_A`이며, isotropic thermal closure에는
`U_th^+=U_th^n(V^+/V^n)^(-2/3)`가 적용된다. 두 실제 energy 차이를 합친
기하 work 장부는 연속 stress work 적분과 일치한다. 수축 축이 있는 경우의
signed work는 비음수 material 재고와 별도로 유지된다.

기하 문서에는 두 가지 최소 교정을 요청했고 최종 파일에서 모두 확인했다.

| 지적 | 최종 교정 | 상태 |
|---|---|---|
| CG-R1 | 정확 subflow에는 양의 C¹ scale factor면 충분하지만 local O(h²) 전개에는 H_i의 시간 Lipschitz를 추가했다. 시간 의존 반응계수의 정칙성도 함께 명시했다. | CLOSED |
| CG-R2 | CG.L1에 실제 kinetic energy에서 ±p packet을 만드는 양의 angular lift를 명시했다. 입력은 같은 chart에 있고, C0=Id이며, 연속 collision에도 같은 angular rule을 사용한다. 다음 chart는 실제 운반된 방향을 그대로 담는다. | CLOSED |

CG.L1의 momentum 크기 `sqrt(W(W+2m_ec²))/c`를 상대론적 W에 대입하면
원래 W를 회복한다. 반대 방향의 가중치 `A_j β_jα/2`를 합하면 bin count,
energy와 0 net momentum을 보존한다. `L C_h L^-1`는 해당 chart 위에서
정의되고, h=0에서 입력의 angular stress까지 유지한다.
이로써 collision의 bin 표현과 geometry의 momentum 표현이 한 상태 공간에 놓인다.
이 lift에 대한 증명은 직접 대입으로 심사했으며 추가 Wolfram 실행을 주장하지 않는다.

기하 변화 뒤의 실제 parent energy에 맞춘 다음 event columns 또는 양의 보존 remap은
다음 atomic-kernel adapter의 입력 의무다. 이번 정칙 branch의 일차 Lie 정리를
적용하려면 단계별로 같은 연속 collision closure와 정칙성을 유지해야 한다.
Cutoff crossing의 시간 정확도에는 이전 TH1의 crossing 분할 또는 검증된 boundary flux가
필요하다는 조건도 보존했다.

## 4. 새 반복 드라이버의 독립 인터페이스 심사

`feedback_solver.py`의 `solve_feedback`는 고정 초기 state로 매번 capacity map을
평가하고, 후보 endpoint에서 계수 피드백을 평가한다. 방문한 state와 다음 map image의
비음성·domain membership·thermal count 하한을 확인한다. q의 수치 범위는 검사하지만,
domain 전체의 contraction 및 self-map 증명은 호출자가 제공하는 계약이다.
양의 state scales와 count-scale bound도 같은 norm과 domain에 대응해야 한다.

반환 `state`와 `event_extents`는 마지막으로 받아들인 map에 함께 속한다.
별도 `certifying_map_image`는 반환 state의 잔차를 측정한 다음 map image다.
따라서 반복 중단 시 저장한 extent가 반환 state를 정확히 재구성한다.
`max_iterations`는 받아들인 갱신 횟수이며, 마지막 state의 실제 잔차를 위해
map을 한 번 더 평가한다. `MAX_ITERATIONS`는 feasible state와 실제 증명서를 반환하면서
수렴을 선언하지 않는다. h=0은 identity를 직접 반환한다.

작성자의 새 연결 검산 두 개는 최종 코드·정리 해시와 일치했고 모두 PASS다.

| 실행 입력 | 실제 반환 | 직접 확인한 의미 |
|---|---|---|
| FP7, 온도 허용오차 10^-12 K, 최대 30회 갱신 | CONVERGED, 15회 갱신·16회 map 평가 | 실제 온도 오차 6.2903244740×10^-14 K ≤ 증명서 2.3115767176×10^-13 K ≤ 허용오차. 상태·extent·불변량 일치. |
| 같은 문제, 허용오차 10^-30 K, 최대 1회 갱신 | MAX_ITERATIONS, extent 6/29, 2회 map 평가 | 실제 온도 오차 1/35 K, 증명서 449616/4513817 K. 비음수·보존 상태를 반환하고 미수렴을 표시. |

첫 사례의 실제 physical endpoint rate defect norm은 약 0.13281250000059
(scaled state)/s로 반환됐다. 이는 이산 고정점 오차가 작아도 physical rate defect가
별도로 남음을 확인하는 입력이다. 드라이버는 physical defect를 출력하고,
추가 Lipschitz·path 조건으로 그 값을 ODE 오차로 바꾸는 FP6 정리를 제공한다.
이번 실행에서 실제 ODE 적분은 수행하지 않았다.

## 5. 실제 실행 근거와 한계

| 실행 주체와 종류 | 성공 수 | 심사에서 읽은 근거 |
|---|---:|---|
| 사건 작성자, 정확 유리수 검산 | 9/9 | EVENT_CHECKS.json, 검산 코드, 입력 3개 digest |
| 피드백 작성자, 새 반복 연결 검산 | 2/2 | FEEDBACK_DRIVER_CHECKS.json, 코드, 입력 4개 digest |
| Root, Wolfram+xAct tensor 항등식 | 4/4 groups | canonical script, raw output, 공식 package hash, normalized record |
| Root, Wolfram FP6–FP7 정확식 | 14/14 groups | canonical script와 raw exact zero residual |
| Root, Wolfram 기하 항등식 | 5/5 groups | momentum 3성분을 포함한 7개 scalar zero residual |

Wolfram 합계는 **23개 명명된 검산 group, 25개 scalar residual**이다.
xAct tensor 검산은 orthogonality, trace, energy projection, number current의
4개 항등식이다. Brouwer·contraction 정리 전체의 자동 증명으로 해석하지 않았다.
Python의 exact-rational 사례들도 명시된 유도와 인터페이스를 판별하는 실행이다.

실제 kernel은 Wolfram 15.0.1 Linux x86 64-bit이며 xTensor 1.3.0,
xPerm 1.2.4를 사용했다. xCore·xPerm·xTensor는 공식 URL에서 받은 source의
SHA-256을 확인한 뒤 로드했다. canonical script의 embedded xAct body는 별도
`xact_tensor_body.wl`과 일치한다. 세 canonical script와 세 raw result의 digest도
`SYMBOLIC_CHECKS.json`에 기록한 값과 일치했다.

초기 xAct 미설치와 native permutation 경로의
`TranslatePerm::invalid`, `DefTensor::invalid`, `Dagger::unknown` 관측은
`XACT_SETUP_OBSERVATIONS.json`에 보존됐다. 지원되는 `$xpermQ=False` 경로에서
metric derivative 정의가 완료됐고 canonical 네 항등식은 모두 0이었다.
초기 version-symbol context의 혼동은 canonical code에서 `System` 및 package의
완전한 context를 사용해 교정했다. 이는 해당 환경의 실행 경로 관측이다.

FP6–FP7 raw output에는 `Power::infy`, `Infinity::indet` 등의 중간 CAS 메시지도
보존돼 있다. 최종 14개 residual은 모두 0이며 제거 가능한 두 극한은 문서의 연속 정의와
검토자의 직접 적분·극한 확인에 일치한다. 이 메시지들을 숨기거나 추가 성공 횟수로 세지 않았다.
기존 science suite, full atomic kernel, 새 ODE 적분, NCP 실행은 모두 0회다.

## 6. 원전과 이번 구성의 관계

| 원전 | 실제 읽은 내용 | 이번 판정에서의 역할 |
|---|---|---|
| Pan–Chen–Fan, JCP 441, 110477 (2021), [DOI](https://doi.org/10.1016/j.jcp.2021.110477) | 저자 원고 §§2–5의 process 공통 가중치, 보존, 에너지와 Theorems 1–2/Conjecture 1 | 공유 사건 가중치의 배경. 읽은 원고의 일반 multi-reactant 존재·유일성 추측을 이번 증명에 도입하지 않았다. |
| Kopecz–Meister, [arXiv:1702.04589](https://arxiv.org/abs/1702.04589) | 생산·소멸의 짝보존, positive denominator, M-matrix 보조정리 및 별도 order 조건 | 고정 선형 positive map과의 비교. 이번 nonlinear event map은 직접 상계로 승인했다. |
| Ziegler, A&A 586 A82 (2016), [DOI](https://doi.org/10.1051/0004-6361/201527262) | §§2.1–2.2의 반응열과 입자수 변화가 포함된 온도식, §3의 적분법 | 고정 γ 이상 EOS와 thermo-chemical 연결의 원전 확인. Active split과 이번 positivity는 별도 직접 결과다. |
| Reynolds 외, JCP (2009), [DOI](https://doi.org/10.1016/j.jcp.2009.06.006) | §§3.2–3.2.4의 joint chemistry/energy residual, scaling, local block | 비선형 물리 coupling의 방법론적 맥락. 해당 모델·허용오차·Newton 수렴을 이번 map의 증거로 사용하지 않았다. |

SciSpace 1개 자연어 질문과 Exa의 제한된 검색·본문 조회로 비교에 필요한 원문을 읽었다.
일부 generic web 조회 실패와 관련 없는 검색 결과는 기록하고 제외했다.
원전의 조건과 우리 구성의 조건을 구분했으며 문헌 전수조사나 전역 신규성 판정을 주장하지 않는다.

## 7. 최종 결속과 다음 단계

FP-R1의 실제 사건 파일 참조, CG-R1의 시간 정칙성, CG-R2의 packet 상태 인터페이스는
모두 교정 완료다. 밀도 log 계수의 `0<n_lo≤n≤n_hi<C²` 조건은 정리·가정·오차 문서에서
일관되게 명시됐다. 열린 차단 지적은 없다.

이 판정은 현재 stage의 명시된 positive conservative map, 그 nonlinear feedback,
조건부 오류 증명서와 prescribed geometry 결합을 승인한다. 다음 atomic 적용에는
실제 단면적·재분배·parent/daughter energy의 현재 상태 결속, 그 domain에서의
q 및 physical Lipschitz 상계, 움직인 packet/grid의 보존 연결을 제공해야 한다.
그 입력 의무는 이번 부분 정리의 승인과 함께 유지한다.

Root가 후속 보고서·LaTeX/PDF·DAG를 만들 때는 이 frozen science와 같은 식·가정·결과를
사용하고 `POST_REVIEW_BINDING.json`에 최종 문서 및 상태 변경을 결속한다.
기존 후보의 identity를 보존한 상태 metadata 교정과 문서 편집은 새 과학 검산 없이
연결할 수 있다. 수식·가정·과학 코드·결과의 변경은 그 변경 부분을 다시 심사해야 한다.
PDF 시각 검수와 최종 배포 기록은 root integrator의 후속 작업이다.
