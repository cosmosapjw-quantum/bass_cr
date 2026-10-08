# R3M26 수치 전략: 인증과 실용 수렴을 분리하고 B3로 전진

## 판단

다음 실험은 **같은 h=.20 family의 B3 전체 충돌 한 번**이다. R3M25의 국소 CF4 reference를 추가로 더 엄격하게 인증하는 루프를 선행조건으로 붙이지 않는다. R3M25는 실제 생산 H/CAP/state 부근에서 full-H 구현과 국소 시간 정확도를 독립적으로 뒷받침했고, 미해결 질문은 이제 전체 trajectory의 최종 P1/P2/P3 시간 민감도다. B3의 목적은 B0/B1/B2로 미리 고정한 예측을 새 데이터 한 점으로 시험하고 **모델에 근거한 시간오차 추정**을 확정 또는 기각하는 것이다.

사용자의 새 목표는 내부적으로 일관된 물리모델의 검증된 수치해다. 엄밀한 global certificate, 원저자 코드의 byte reproduction, 원저자 관측값과의 강제 일치는 이 목표의 필수조건이 아니다. Numerical verification, physical-model validity, literature/experiment agreement는 별도 ledger다. 다만 temporal gate가 통과해도 현재 약3% 공간 gap과 all-bound/b 적분은 남으므로 전체 production은 아직 HOLD다.

## 읽은 authority와 직접 검사

- repo HEAD `90d6cbad25e4bc49e9563f8721fdc408761b31c7`; R3M25 report/research plan, roadmap ERROR_BUDGET/DAG, 과거 B0/B1/B2 temporal models.
- upload RESULT SHA `a51828e724c6636c3522aee7c4ecdb02435d9031947bf39d9ccde1fe195239ff`는 repo ATTEMPT_2 원본과 byte-identical이다.
- RESULT/PREFLIGHT/WARMUP→MANIFEST, MANIFEST→COMPLETED, MANIFEST→CONTRACT_2 연결 여섯 검사가 모두 맞다. 이는 scalar-file identity/seal 검사다. 큰 endpoint 배열이나 GPU 실행은 다시 검증하지 않았다.
- raw distances에서 CF4 관측차수 4.20202063593422, 4.045839749892995를 재계산했다. R3M25의 `GLOBAL_TIME_ERROR=NOT_EVALUATED`는 정확하다.
- B3는 실제 dt `0.00624946176119497 = B2 actual dt/2`, nstep **7172**, 128-step chunk **57개**, 마지막 **4 steps**다. requested dt=.00625가 기존 runner에서 이 값을 준다.
- 검산 기록: `results/R3M26/foundation/SCALAR_INPUT_AUDIT.json`. 첨부 scalar/seal을 읽어 재계산했으며 큰 endpoint 배열이나 GPU 실행은 하지 않았다. 최종 시간 규칙에는 별도 D_hold cap이 없고 아래 U_time에 포함된다.

## R3M26 계약에 적용하는 조항

1. ERROR_BUDGET의 `Conservative sum of justified bounds only`를 production용 empirical estimate ledger와 optional certified-bound ledger로 나눈다. 기존 1% 목표와 .10% 시간 배분은 그대로 둔다. 검증된 경험적 불확실성의 보수적 합은 사용할 수 있지만 이를 확률적 신뢰구간이나 엄밀한 상한으로 명명하지 않는다.
2. `not certified`를 empirical-budget closure의 자동 거절 사유에서 제거한다. 대신 `held-out prediction tested`, `assumptions/regime stated`, `estimator calibrated`, `cross-effects checked`를 요구한다.
3. p∈[1.5,2.5]는 diagnostic flag로 둔다. dt²+dt⁴ crossover가 새로운 B3를 설명하면 p>2.5만으로 거절하지 않는다. 기존 R3M18 판정은 소급 수정하지 않고 R3M26부터 새 prospective rule을 적용한다.
4. 보존된 R3M25 local reference는 이미 충족된 algorithm evidence다. 새 local reference를 mandatory gate로 다시 열지 않는다. B3가 예측과 크게 충돌하거나 구조적 failure가 있을 때만 원인이 특정된 진단을 수행한다.
5. roadmap/DAG의 현재 frontier는 R3M19에 멈춰 있으므로 R3M20–25 완료 요약과 B3 node로 갱신한다. 과거 계약의 `새 collision 0`을 현재의 영구 금지조건처럼 상속하지 않는다.

## 엄밀한 충분조건과 그 역할

단위가 있는 식에서

    i ħ ∂t ψ = (H(t) − i W) ψ,  H=H†, W=W†≥0,
    A(t)=−iH/ħ−W/ħ.

현재 구현은 atomic units에서 ħ=1이다. 같은 격자 weighted norm에 대해

    d||ψ||²/dt = −(2/ħ)<ψ,Wψ> ≤ 0,
    ||U(t,s)|| ≤ 1.

연속 재구성된 근사 ψ~의 defect를 r=∂tψ~−Aψ~라 하면, e=ψ−ψ~는

    e(T)=U(T,0)e(0)−∫_0^T U(T,s)r(s) ds,
    ||e(T)|| ≤ ||e(0)||+∫_0^T||r(s)||ds =: δ.

piecewise reconstruction에 jump가 있으면 jump norm 합을 추가한다. 또는 각 numerical state에서 exact one-step와 numerical one-step의 defect를 전 구간에 걸쳐 지배하면 contraction에 의해 그 norm 합으로 global state error를 지배한다. 국소 CF4 repeat 몇 개만으로 전체 integral/합을 지배할 수는 없다.

고정 orthogonal projector Q에 대해 p~=||Qψ~||²이면

    |p−p~| ≤ 2 sqrt(p~) δ + δ²,
    [max(0,sqrt(p~)−δ)]² ≤ p ≤ [sqrt(p~)+δ]².

따라서 relative-to-p~ 목표 ε의 충분조건은

    δ ≤ sqrt(p~) ε/(sqrt(1+ε)+1).

현재 ε=.001일 때 threshold는 P1 약3.8994e−5, P2 약4.3526e−5, P3 약4.4945e−5다. 이 조건을 못 닫는 것은 observable failure가 아니라 INCONCLUSIVE다. Q 자체를 바꾸면 projector discrepancy 항도 별도로 필요하다. 초기 준비 차이/격자 차이/모델 차이를 동일한 fixed-H same-Q certificate로 섞지 않는다.

현재 finite-grid Gram observable에는 실제로 이 projector 구조가 있다. grid mass matrix M=dv I, sampled channel 열행렬 B, G=B†MB가 full rank라면 Q=B G⁻¹ B†M이다. Q²=Q이고 Q†M=MQ이므로 weighted norm에서 ||Q||=1이다. c=B†Mψ일 때 p=c†G⁻¹c=||Qψ||²이며, raw overlap sum c†c와 구별된다. `cr_repro/r3m11.py:gram_projection`은 이 full-rank solve를 구현하고 ill-conditioned Gram을 거절한다. 이것은 선택한 finite sampled span에 대한 orthogonal projector이며 exact Coulomb spectral projector나 all-bound projector라는 뜻은 아니다.

다른 Q와 R을 같은 Hilbert space에서 비교하고 η=||Q−R||를 안다면 |p_Q(ψ)−p_R(ψ~)|≤2√p_R(ψ~)δ+δ²+η||ψ||²이다. 그리드가 달라지면 먼저 공통 Hilbert space의 norm-consistent embedding을 정해야 이 식을 사용할 수 있다. CAP 후의 p/||ψ||²는 survival-conditioned fraction으로 observable 자체가 달라지므로 physical capture p를 대신하지 않는다. δ는 같은 gauge의 raw state norm으로 충분하며, 임의 phase alignment로 얻은 ray distance를 residual theorem에 조용히 대입하지 않는다.

이 theorem route는 필요할 때 엄밀한 결과를 주는 선택지다. global residual quadrature, roundoff, 전 trajectory reference를 새로 증명해야만 모델 검증형 production을 허용한다는 규칙으로 바꾸지 않는다.

## B3 사전 등록 empirical rule

아래 숫자는 기존 판정 변경이 아니라 **B3 값을 보기 전에 고정하는 새 운영 규칙**이다. 안전계수2는 검증 관행을 참고한 보수적 설계 선택이며 theorem이나 95% confidence를 뜻하지 않는다.

### 입력 불변조건

동일 energy/b/grid/box/CAP rate/target potential/초기 배열 bytes/관측량 Q와 source family를 유지한다. B3 config의 real dt만 .00625로 변경하고 fresh receipt와 v2 internal binding을 만든다. 총시간은 44.821139751290325 au다. 결과·norm·Gram·nested probabilities·checkpoint가 유효해야 한다. 구조적 failure와 수치 수렴 failure를 분리한다.

### 아직 보지 않은 B3의 예측을 먼저 봉인

각 Pk에서 다음 세 forecast를 B0/B1/B2만으로 고정한다.

- F_power: B0/B1/B2의 actual-dt single-power fit.
- F_even: B0/B1/B2의 P∞+c2 dt²+c4 dt⁴ interpolation.
- F_p2: B1/B2만으로 leading second-order를 가정한 한 단계 앞 예측.

예측 범위:

| channel | F_power | F_even | F_p2 |
|---|---:|---:|---:|
| P1 | .006087425905056484 | .006088483581395872 | .006089481091543652 |
| P2 | .007584574562317878 | .007585789738104656 | .007586849802025597 |
| P3 | .008087011530294713 | .008088288894064294 | .008089375422685228 |

이 값 자체를 정답이나 acceptance target으로 만들지 않는다. 예측오차와 model spread가 새 관측값 대비 목표 배분 내에서 충분히 작았는지를 검사한다.

### B3 후 계산

actual time step을 τ0>τ1>τ2>τ3, 결과를 y0..y3라 하자. 최소 조건은:

- finest signed increments Δ12=y2−y1, Δ23=y3−y2가 같은 부호이고 |Δ23|<|Δ12|이다.
- |Δ23|/|y3|≤.001. 이 B family에는 별도 absolute 승인 기준이 등록되지 않았다. y3=0은 입력 거절, unresolved-small 차분은 OPEN이며 자동 PASS하지 않는다.
- 다음 네 가지 zero-step estimate를 산출한다: (i) finest-p2, (ii) B1/B2/B3 even2+4, (iii) four-point even2+4 least squares, (iv) finest-triplet single power. 계수 solve는 해당 fit의 max(dt)로 dt를 scale하여 수행한다. p fit은 actual ratios를 사용하며 부호 변화나 계산 불능을 감추지 않는다.

정의:

    E_model = max_M |P∞_M − y3|,
    D_hold  = max_{F_power,F_even,F_p2} |y3 − F|,
    U_time  = 2 max(E_model, D_hold).

**P1/P2/P3 모두** 위 구조·pair·contraction 조건과 U_time/|y3|≤.001을 만족하면

    TEMPORAL_ESTIMATE_VALIDATED_FOR_FIXED_H_SELECTED_SPANS

로 종료한다. `estimate_kind=CONSERVATIVE_EMPIRICAL_MODEL_ENVELOPE`, `certified=false`, `model_conditional=true`, global physical production은 HOLD로 둔다. 더 엄격한 global certificate나 새 국소 benchmark를 요구하지 않는다.

이 규칙은 `.10% pair PASS`만으로 끝내지 않으면서도, 세 점 interpolation은 theorem이 아니라는 이유로 모든 경험적 수렴을 영구 거절하지 않는다. 예를 들어 기존 F_even에 가까운 B3가 나오면 predicted pair는 .0507–.0533%이고 모델 잔여/forecast discrepancy를 두 배 감싼 추정도 .10% 안에 들 가능성이 있다. 이는 계획상의 전망이지 미실행 PASS가 아니다.

구체적인 운영성 검산은 `results/R3M26/foundation/HYPOTHETICAL_B3_ILLUSTRATION.json`에 있다. **PREDICTION_NOT_OBSERVATION**: 아래는 B3를 아직 측정하지 않은 상태에서 가상 y3=F_even으로 둔 예다. 실제 B3가 이 값에 맞도록 조정해야 한다는 뜻이 아니다.

| channel | 가상 pair 변화 | 가상 U_time / abs(y3) | 가상 empirical gate |
|---|---:|---:|---|
| P1 | .0532525% | .0355017% | PASS |
| P2 | .0507755% | .0338504% | PASS |
| P3 | .0506751% | .0337834% | PASS |

따라서 현재 예측과 일관된 새 관측이 나올 경우 이 gate는 시간오차 배분을 유한하게 닫는다. 위 표는 새 full collision 결과·검증·승인이 아니다. 실제 signed asymmetrical dt의 power fit은 Δ01/Δ12=(τ0ᵖ−τ1ᵖ)/(τ1ᵖ−τ2ᵖ)를 풀고 P∞=y2+Δ12/[(τ1/τ2)ᵖ−1]를 쓴다. 절댓값으로 sign change를 숨기거나 requested dt의 정확한2배 비율을 가정하지 않는다.

### 4-point/LOO 해석

B3는 미리 고정한 예측에 대해 새로운 datum 한 개다. 이후 all-four leave-one-out은 estimator sensitivity diagnostic이며 독립 실험 네 개가 아니다. coarse B0를 finer triplet로 역외삽한 오차가 크다는 이유만으로 finest temporal gate를 다시 막지 않는다. coarse point를 포함/제외한 limit 민감도는 E_model에 이미 나타난다.

4-point even degree-six polynomial은 네 점을 정확히 보간할 수 있지만 error estimate를 검증하지 않는다. λ∏_j(dt²−τ_j²)를 더하면 관측점을 보존하고 dt=0 limit를 바꿀 수 있다. 이것은 finite-data inference의 이론적 한계다. 모델 검증 route에서는 그 한계를 공개하고, formal order·같은 H의 독립 algorithm check·held-out prediction·보수적 model envelope를 근거로 결정하면 된다.

## finite 종료와 escalation

- 통과: 시간 budget을 **경험적 검증 수준에서 닫고 spatial/boundary 단계로 이동**한다. 더 많은 temporal points/국소 certificates를 자동 요구하지 않는다.
- 구조/자원 failure: 정확한 구현/환경 blocker 하나를 수리한다. 기존 failure 보존, 동일 실패의 무근거 재시도 금지.
- pair/estimate만 약간 초과하면서 contraction/model forecast가 잘 맞음: 실제 새 값에서 다음 dt 비용 대비 예상 오차를 계산해 **최대 한 번**의 추가 temporal refinement를 후속 bounded 계획으로 택할 수 있다. 목표 배분은 유지하고 무한 ladder로 가지 않는다.
- sign change, prediction disagreement, model spread domination: 맹목적 B4 대신 어떤 차원이 틀렸는지 지정한 strategy decision. 후보는 같은-H CF4 full-run의 work-precision 평가 또는 좁은 원인 검증이다. 정상 데이터를 버리고 새 tolerance에 맞추지 않는다.
- coarse-to-fine extrapolation이 실패해도 model-based result를 포기하는 것이 아니라, 한계를 지정한 unresolved uncertainty와 실제 observable을 보존한다.

## 최종 산출물과 범위 유지

원 목표는 50/100/225 keV/u의 모델 기반 bound capture, 최종 b 적분 및 source release다. 중간 finite-n 데이터셋은 별도 명시된 산출물로 유용하지만 **all-bound endpoint를 대체하지 않는다**.

- `P1/P2/P3 scoped release`: 시간/공간/준비/box-CAP/final-time 검증을 마친 finite selected-channel 결과. n≤3라는 정의에 대한 수치 uncertainty를 붙인다. b=2 한 점은 단면적이 아니다.
- `all-bound release`: supported n-ladder, 고준위 support, tail model의 held-out 검사/독립 비교에 근거한 **실용 truncation estimate**가 필요하다. 엄밀 tail theorem만 허용할 필요는 없지만 n=4 한 increment를 tail bound로 쓰지 않는다. current box가 high-n support를 못 담으면 box/basis 표현을 실제로 바꾸어 해결해야 한다.
- `cross-section/source release`: adaptive b panels와 tail extension, 수치 error의 적분 전파, energy/state/channel contract. HOST 쪽 admission과 원자 수치 결과는 분리한다.

물리모델 discrepancy는 수치 1% ledger와 분리한다. 직선 궤적/전자-핵 근사/질량/전자상태/상대론적 효과 등의 모델 가정 및 외부 비교 discrepancy를 별도로 표시한다. 원저자 수치와 다르다는 이유로 수치 tolerance 또는 모델을 사후 조정하지 않는다. AOCC는 독립 representation 검증을 제공하지만, 현재 단일 TDL 수치 결과의 모든 진전에 AOCC 미구현을 허위 선행조건으로 붙이지 않는다. 원 계획의 두-lane 비교는 explicit comparison deliverable로 유지할 수 있다.

## 출처와 적용 한계

1. Auzinger, Koch, Thalhammer, *Defect-based local error estimators ... Part I: The linear case*, JCAM 236 (2012) 2643–2659, DOI 10.1016/j.cam.2012.01.001. Publisher abstract 및 검색 결과에서 defect/variation-of-constants와 asymptotically correct estimator의 commutator 가정을 확인했다. 전역 CAP 식은 위에서 직접 유도했으며 논문이 현재 Coulomb/FFT/CAP 구현의 전역 bound를 준다고 주장하지 않는다. Primary URL: https://www.sciencedirect.com/science/article/pii/S0377042712000027 (direct open 403; search-indexed publisher abstract checked).
2. Rumsey & Thomas, NASA/TM–2008–215537, §2 pp.2–3: https://fun3d.larc.nasa.gov/papers/NASA-tm-2008-215537.pdf. 실제 원문 pp.5–6의 discretization-uncertainty 절에서 safety factor를 둔 error estimation, oscillatory/divergent sequence 및 지나치게 높은 apparent order의 경고를 확인했다. 이것은 practical uncertainty reporting의 1차 문헌 사례이며 CFD 규칙을 현재 TDSE에 theorem처럼 그대로 이식하지 않는다.
3. Eça & Hoekstra, JCP 262 (2014) 104–130, *A procedure ... grid refinement studies*, publisher-indexed abstract에서 fitting·safety factor 기반 solution verification을 확인했다. https://www.sciencedirect.com/science/article/pii/S0021999114000278 (direct open 403). 이 문헌으로 본 과제의 safety factor2를 정당화한 것은 아니다; factor2와 above gate는 새 사전 등록 설계 선택이다.


## 작은 행렬에서 실행한 유도식 검산

`scripts/r3m26_foundation.py`와 `tests/test_r3m26_foundation.py`는 2×2 비정규 소산계 및 4차원 가중 Gram 예제만 사용한다. production wavefunction·collision 입력은 사용하지 않는다. 비정규 소산행렬의 SciPy exponential과 독립적인 삼각행렬 closed-form exponential을 비교하고, 알려진 강제항을 갖는 y(t)에서 Duhamel identity를 직접 계산한다.

추가로 inner product의 adjoint를 A*라 할 때 z′=−A*z, z(T)=Qy(T)를 두면

    Δq = 2 Re〈z(0),e(0)〉 − 2 Re∫〈z,r〉dt + ||Qe(T)||²

이다. 여기서 e=ψ−y, r=y′−Ay이며 Q는 같은 inner product에 대한 orthogonal projector다. Euclidean 예제에는 A*=A†를 사용하고, 일반 mass matrix M이면 A*=M⁻¹A†M이다. 잔차 적분과 adjoint 적분은 각각 알려진 강제항의 endpoint 표현과 독립 비교했다. 이 goal identity는 큰 전역 state bound가 필요 이상 보수적일 수 있는 이유를 보여 주지만, 이번 empirical route의 필수 adjoint 실행 요구는 아니다.

가중 Gram projector는 mass-weighted QR이라는 독립 표현과 비교했고, invertible basis mixing 및 channel phase의 불변성을 확인했다. 정규화된 비직교 두 basis가 동일 성분을 중복 계산하는 반례에서 raw overlap sum은 1.5, 올바른 projected probability는 1이다. 다른 반례는 모든 eigenvalue가 −1이어도 비소산 비정규계에서 propagator norm이 1.3084가 될 수 있음을 보인다. 가중 projector의 Euclidean norm 1.1662와 weighted norm 1의 차이는 norm convention의 필요성을 확인한다.

최종 결과는 `results/R3M26/foundation/RESULT_FINAL.json`에 있으며 Duhamel identity 잔차 최대 5.31e−17, adjoint goal 잔차 최대 5.60e−17, Gram/QR projector 차이 6.80e−16이다. 해당 시험은 9 passed다. 유도식·작은 행렬 구현의 수치 검산이며 production의 시간오차 검증이나 엄밀 residual quadrature 인증이 아니다. 최초 runtime 및 JSON 직렬화 실패, 수정과 최종 실행 결과는 같은 디렉터리의 raw logs 및 `VALIDATION.json`에 보존한다.
