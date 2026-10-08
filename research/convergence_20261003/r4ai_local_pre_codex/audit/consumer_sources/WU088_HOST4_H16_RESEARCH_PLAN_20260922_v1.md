# BASS / WU088 / HOST4: 결과 종결을 위한 연구계획서

버전: H16_CONVERGENCE_v1. 작성일: 2026-09-22.
부모: H15 FINAL, SHA-256 `6773bb886c8ea13662db0a7c18b1c84fa2ad92e52367541ed1044cf4c67804cd`.
이번 산출물은 연구목적 재정렬, 새 해석 명제, 검산, 단계별 실행계약이다. 전체 프로젝트 또는 physical rate가 완료되었다는 보고가 아니다.

## 1. 최종 목적과 범위

### 1.1 이 스레드의 직접 완료 대상

H5의 immutable state/target/source/frame/time에 맞는 `H0_CR_1s_FORMATION_COUNT__NOT_TOTAL_GAS_HII`를 계산하고, 해당 관측량에 적합한 source/수치/모델 오차를 분리하여 실제 소비자와 실행 가능한 host에 전달한다. 최종 패키지는 수식이나 handoff만이 아니라 다음을 함께 포함해야 한다.

- 지정 상태에서의 rate 계수 및 부피당 생성률, 단위, source signature, 적용 에너지 범위.
- 선택한 continuum에 대한 수치오차 certificate와 물리/source 불확실성의 별도 기록.
- warm-target support 밖의 누락 기여, 조건과 상한. 극소 확률을 0으로 대체하지 않는다.
- source/state/target/grid/operator/quad/frame/time/host/runtime의 신원과 실제 실행 증거.
- 독립 재실행 결과와 parent WU088의 반응별 수락 또는 구체적인 거절 사유.

여기서 H5 state는 **새로 정의한 물리 모델 초기조건**이다. 잃어버린 observational/actual snapshot의 복구본이 아니며 그렇게 바꾸지 않는다. 실행된 모델 상태는 `origin=model_defined`인 새 runtime 산출물로 등록할 수 있지만, 기존 `ACTUAL_DECLARED` status를 복사해 승인된 것으로 만들 수 없다.

### 1.2 온전한 종료와 제한적 결과를 구분

`COUNT_MODEL_RESULT`: 정해진 continuum·kinematics·state 모델을 수치적으로 검증한 생성률. 이것은 지금 가장 빨리 완결할 수 있는 중간 과학 결과이다.

`COUNT_EVALUATED_SOURCE_RESULT`: 원전 평가와 검증된 모델 선택에 근거한 물리 추정치. 보수적 estimated accuracy를 confidence interval 또는 hard truth bound로 부르지 않는다.

`COUNT_STRICT_CERTIFIED_RESULT`: 필요한 전체 domain의 인증된 source/모델 discrepancy/수치/꼬리 상한을 갖춘 결과. 기존 physical-rate strict gate를 여는 것은 이 profile의 독립 승인 후이다.

`HOST4_THREAD_COMPLETE`: 약속한 count profile의 결과, 실제 host/state 결합, 재실행 증거, parent 반응별 수락까지 완료한 상태. 기존 가장 강한 strict gate를 유지하는 기본 계획에서, 모델 결과나 evaluated 결과만으로 이 상태를 선언하지 않는다.

전체 BASS의 transport/deposition, joint physical UQ, H–H 반응군 종결은 아래 확장 DAG의 별도 완료 대상이다. 이들을 HOST4 단일 count에 불필요하게 직렬로 달지는 않지만, 전체 BASS 완료로 혼동하지 않는다.

### 1.3 이번에 바로잡은 critical path

H11–H15는 total-CX tail을 크게 정리했지만, H10에 남은 **중심 1–100 keV/u의 state-selective 1s continuum authority**와 **production host pin**은 그 결과로 닫히지 않았다. 앞으로는 중심 kernel, state/host, endpoints를 병렬로 진행한다. Low-energy P0의 transport table을 high-energy 1s continuum으로 대체하지 않는다.

또한 whole-domain sup-norm proof는 weighted count의 필요조건이 아니다. 실제 관측량의 positive weight로 전파된 error를 인증하면 된다. 유한 부분파 구간 전체를 새로 고정밀 계산하는 것 역시 필요조건이 아니다. Unitarity의 느슨한 bound만으로 해당 구간이 error budget 아래라면 그 분기는 끝낸다.

## 2. 회수한 기준 문서와 fresh 상태

### 2.1 바이트로 재검증한 자료

H15 FINAL: 2,130,037 bytes, ZIP CRC 정상, manifest 35/35 일치.

H15 안의 P0 R25 FINAL: 2,199,160 bytes, SHA-256 `db5889700b09f110fe7b83742beff55d3163263728874373c05e57b14cdd95ee`, ZIP CRC 정상, manifest 1200/1200 일치. 이는 바이트 검사이지 192개 solver run의 재실행이 아니다. R25의 873 nodes와 targeted midpoint gate는 모델계열 수치 근거로만 유지한다.

H5 및 H10 원 보고서의 현재 Library bytes를 별도 intake에 보존했다. H5 state 자체의 SHA는 보고서에 기록되어 있으나, 이번 작업은 H5 state builder를 실행하거나 state JSON 전체를 새로 회수한 작업이 아니다.

### 2.2 sibling 의존성만 갱신한 자료

CR R3M14 v2 preflight: Dropbox 정본 `id:BSpOijBcT10AAAAAADtAig`의 추출 내용을 읽었다. Canonical parent `d04124e8a1b83f29fd26baa13f11cd68a8f33c15`, restart ancestry `02546302a3d6958ea9fa97488a670672e07be178`는 해당 자료의 기록이다. 이번에 GitHub HEAD를 직접 감사한 것은 아니다. Status는 `PREFLIGHT_ONLY_PRODUCTION_NOT_RUN`, b-grid `NO_GO`, isolated fixture 6 PASS이며 production pair/collision 결과가 아니다. 따라서 1s kernel의 새 중앙값으로 import하지 않고, preparation → 실제 propagated initial state의 typed-byte/config/environment 결합 요구사항만 C1/C4에 반영한다. Raw ZIP 전송은 download tool routing 및 DNS 문제로 완료하지 못했다.

H–H R9B: Google Drive report `1rR7VYBhOhqmfco393giLOp6XLP_kDzAt`를 읽었다. ch23 weak-H control 종결과 R10 raw-matrix gate 허용까지만 확인했다. 전체 행렬·propagation·physical-channel admission은 아직 not executed이다. H+ + H capture data로 import하지 않는다.

Google Drive와 Dropbox의 좁은 R26/R27 refresh 결과는 `SIBLING_SYNC.json`에 기록한다. 특정 검색의 무결과는 전체 provider에 그러한 연구가 존재하지 않는다는 증명이 아니다.

### 2.3 되풀이하지 않을 역사적 복구

WU087 원 evidence archive loss 및 actual co-bound snapshot의 과거 생성 미확립은 H3의 종료 판정으로 보존한다. 새 exact object ID/hash라는 반증 증거가 나오지 않는 한 전역 provider tree를 다시 훑지 않는다. H4 reference host를 production host로 바꾸어 읽지 않는다.

## 3. 이번 루프의 실제 연구 산출

P1: 공통 외부 Jost 로그미분 \(z=\alpha+i\beta\)와 임의 정규화된 내부 regular 해의 로그미분 \(m_i\)만으로

\[
\sin^2\Delta\delta_\ell=
\frac{\beta^2(m_g-m_u)^2}{[(m_g-\alpha)^2+\beta^2][(m_u-\alpha)^2+\beta^2]}
\]

라는 정확한 경계식을 유도했다. 내부 해의 절대 normalization을 구해야 한다는 H15 작업을 경계 invariant 문제로 바꾼다. 외부 tail의 물리 효과는 z에 남는다.

P2: 인증된 원심 장벽 조건 아래 \(m_i\ge\nu/r\) 및 \(|m_g-m_u|\le\int|\Delta U|(r/R_c)^{2\nu}dr\)를 유도했다. 따라서 source-tail 인증에는 cellwise potential bound, 외부 z enclosure 및 합가능한 all-ℓ majorant가 필요하다. 실제 B,z,L*,ρ 수치를 아직 얻지 않았으므로 source-model infinite-ℓ gate는 OPEN이다.

P3: finite omitted band는 unitarity로 묶고, weighted error가 예산 미만이면 그 부분파들의 direct solver replay를 생략하는 종료 규칙을 도입했다. k→0, physical potential discrepancy 및 genuine infinite tail을 생략하는 규칙은 아니다.

P4: positive functional의 integrated error를 직접 인증하며, 상대오차 분모에는 중앙값이 아니라 인증된 양의 core 하한을 요구한다. 독립 kernel/spread/convergence 진단을 physical covariance로 합치지 않는다.

P5: 유한 표본만으로 continuous kernel bound를 인증할 수 없음을 smooth bump 반례로 명시했다. 따라서 추가 자료가 필요할 때에는 '더 많은 보간법'이 아니라 실제로 빠진 regularity/Hamiltonian/source uncertainty 가정을 요구한다.

증명과 부호·차원·영점 chart·유효범위는 `proofs/H16_BOUNDARY_CERTIFICATE_AND_GOAL_ORIENTED_CLOSURE_KO.md`에 있다.

## 4. 공통 성공조건과 오차 계약

### 4.1 고정 상태와 단위

기본 H5 benchmark: z=8, nHI=138.4520191201626 m⁻³, T=10⁴ K, target drift=0, isotropic neutral Maxwellian, gas tetrad, proper-time rate. Projectile G(p)=Cp⁻² on 4–81 keV/u, nCR=1.3845201912016257×10⁻⁴ m⁻³. Bianchi-I H_i/H=(1.01,0.995,0.995) at a_i=1. 모두 model-defined 값이다.

Metric signature (-,+,+,+); c, ħ, k_B는 보존한다. eV/u, keV/u, E_CM, E_lab는 서로 다른 필드로 저장하고 반응 질량·단위를 함께 pin한다. 계수 K [m³/s]와 R=nHI nCR K [m⁻³/s]를 구분한다.

`fast`가 단순 projectile-population label인지, 별도 outgoing energy threshold인지 C1에서 exact observable signature로 확인한다. 후자라면 differential capture kernel이 필요하므로 현재 scalar total-1s 적분의 완료조건을 그대로 쓰지 않는다.

### 4.2 수치 목표와 물리 uncertainty

선택된 모델의 numerical integration 상대 목표 10⁻⁸은 이번 계획의 새 engineering target이다. 기존 tail screening 목표 10⁻¹²는 인증된 positive core lower bound에 대해 적용한다. 이 값들은 source의 실제 물리 정확도가 10⁻⁸ 또는 10⁻¹²라는 뜻이 아니다.

Source error에는 임의 1% 목표를 '이미 가능한 정확도'로 부여하지 않는다. 필요한 연속 오차 계급을 닫고, 달성한 범위와 해석을 보고한다. 불확실성 자체가 넓으면 숫자를 숨기거나 post-hoc threshold를 완화하지 않고 그 범위를 결과로 낸다. 엄밀한 source bound가 없으면 strict profile은 미승인으로 남긴다.

Deterministic enclosure들이 같은 quantity와 normalization을 지배할 때에만 삼각부등식으로 합산한다. Nodal estimate, interpolation-family spread, quantum-method discrepancy, numerical quadrature residual을 RSS로 합해 CI를 만들지 않는다. 통계적 joint uncertainty를 주장할 때에는 별도의 확률모형과 cross-energy dependence가 필요하다.

### 4.3 state-validity domain

H5 한 event의 certificate는 모든 Bianchi state에 대한 certificate가 아니다. 이후 evolution에 쓰려면 \(\mathcal S=\{T,n,v_{drift},G,\ldots\}\) 유효영역을 명시하고 parameter-cell certificate를 만든다. 런타임이 \(\mathcal S\)를 벗어나면 fail-closed 재승인한다. 배경 anisotropy가 있어도 국소 scalar count의 angular reduction이 성립하는 조건과, drift/anisotropic-target에서 깨지는 조건을 구별한다.

## 5. 앞으로의 단계별 실행계획

아래는 **현재 종결한 C0 뒤에 남은 여섯 작업 묶음**이다. C1,C2,C3는 가능한 범위에서 병렬이다. 모든 대안 방법을 동시에 필수로 요구하지 않는다.

### C0. 목적·근거·종료 profile 고정: 이번 루프에서 수행

입력: H5/H10/H15, R25, 현재 sibling 상태. 출력: 이 계획, claim contract, 논리 DAG, 새 증명, 검산 기록. 완료조건: 원래 1s count와 total-CX/transport/UQ의 관측량 분리, old physical gate 보존, 현재 실행된 것과 미래 작업 구분. 미완료: actual host 및 physical rate 자체.

### C1. 실제 consumer-state와 실행 host를 함께 고정

**담당:** HOST4 + actual consumer/host owner. **선행:** C0. **병렬 가능:** C2,C3.

1. H5 benchmark 원 state bytes를 exact hash로 회수한다. 실제 host가 받아들일 새 model-origin event를 export하며 spectrum, gas, tetrad, proper time, state normalization을 하나의 packet에 묶는다.
2. Host repository commit/tree, executable/entrypoint, build flags, dependency versions, units/measure/time adapter를 pin한다. Reference commit은 reference로만 보존한다.
3. Prepared state, export된 state, 실제 solver가 첫 step에 사용하는 state의 typed-array digest와 norm을 확인한다. R3M14의 의미론을 사용하되 그 fixture 성공을 HOST4 성공으로 복사하지 않는다.
4. Existing preflight가 actual-origin만 받는다면 별도 model-origin profile 변경안을 owner에게 전달한다. 기존 status string이나 attestation을 조작하지 않는다. Profile 변경은 명시적 승인된 mutation 후 별도 시험 대상이다.
5. `fast` acceptance rule, channel labeling, gas-only reservoir와 전체 species bookkeeping을 확정한다.

**반환:** STATE_HOST_BINDING.json, 원 state, source-grid/evaluation hashes, ENVIRONMENT.json, exact entrypoint, units/frame/time checklist. **PASS:** 모든 필수 필드 실제 값, 첫-step identity 일치, 원 provenance 보존. **STOP:** missing host/state/권한을 명확히 기록하고 reference-only track의 결과는 별도 산출한다. Host 부재를 원자 물리 오류로 분류하지 않는다.

### C2. 중심 1s continuum과 관측량별 source 오차

**담당:** high-energy CR/source owner + HOST4 analytic owner. **선행:** C0; H5 point model로 먼저 수행 가능, 최종 소비자 packet에는 C1 필요.

1. D102563 native 1s grid의 에너지/frame/channel 신원을 재확인한다. C102 선택 interpolant를 명시적 project model로 유지하고 source-owned continuum과 구별한다. D107338/BDSCx는 독립 reference다.
2. 두 승인 경로 중 하나를 닫는다. 경로 A는 원 source가 제공한 continuum representation 또는 interpolation-error/regularity authority의 직접 회수다. 경로 B는 독립 Schrödinger/scattering 계산을 연속 domain에 대해 검증하고, 모델 가정과 source discrepancy의 허용범위를 명시하는 것이다. 후자를 원 source의 공식 결과로 바꾸어 부르지 않는다.
3. Weight \(W_s\)로 각 energy panel의 관측량 오차 \(e_j\)를 먼저 평가한다. \(e_j\)가 큰 panel부터 off-grid 검증/interval refinement를 수행한다. R25의 low-energy transport nodes를 high-energy 1s 값으로 대입하지 않는다.
4. 검증점은 interpolation 구성용 점과 분리한다. 새 점을 삽입하면 기존 validation은 훈련 데이터가 되므로 최종 frozen model을 별도 off-grid 집합으로 검사한다.
5. source interval \(\sigma_{core,-},\sigma_{core,+}\) 또는 명시된 conditional error model을 반환한다. 단순 nodal box vertices가 nonlinear PCHIP box 내부의 extrema를 포괄한다고 가정하지 않는다. 필요하면 validated interval extension 또는 proven parameter monotonicity로 보완한다.

**반환:** CORE_1S_KERNEL.json, admissible model class, E↔g 변환, source/operator hashes, interval/error record, invalid-domain refusal. **PASS 모델 profile:** fixed continuum replay와 numerical validation. **PASS strict profile:** weighted 또는 pointwise source envelope 및 positive core lower bound 확보. **STOP:** 유한 표본만 있고 추가 regularity가 없으면 `INSUFFICIENT_CONTINUUM_CONSTRAINTS`; 같은 자료로 새 spline을 늘리는 반복은 중지한다.

### C3. 두 extreme endpoint와 물리·운동학 일관성

**담당:** HOST4 theory; 필요 수치만 외부 runtime. **선행:** C0. **C2와 병렬.**

C3E: H15의 0.12 eV/u–10 MeV/u IAEA all-state 자료를 source-evaluated lane으로 유지한다. Reported accuracy와 5.4% fit deviation으로 만든 envelope는 해당 가정을 명시한 evaluated envelope다. 가장 강한 physical truth bound로 승격하지 않는다. 입력이1s capture인지 all-state total인지 schema로 분리한다.

C3L: <0.12 eV/u. 우선 \(g\sigma_{1s}\le A/g+B\)처럼 Maxwell weight와 직접 적분되는 majorant를 찾는다. Scattering-length 유한성이나 threshold law의 존재만으로 숫자가 생기지 않으므로 상수와 적용 범위를 확보한다. Threshold resonance·hyperfine/channel convention의 필요 여부를 확인한다. 이 직접 경로가 닫히면 모든 Khoma partial wave 재계산을 count의 필수조건으로 요구하지 않는다.

C3J: 직접 low-energy physical majorant가 없고 Khoma source 경로를 사용할 때만 critical이다. H16 P1–P3로 source의 B, ΔU cell enclosure, exterior z, d0>0, all-ℓ summability를 인증한다. Finite band는 unitarity 상한이 예산 아래이면 계산 없이 닫는다. 그렇지 않은 band만 interval log-derivative/Prüfer 계산을 수행한다. 실제 L*는 certificate에서 결정하고 1764를 고정 답으로 넣지 않는다.

C3P: source-model 경로를 물리 bound로 쓰려면 실제 potential family와의 discrepancy도 필요하다. ΔV exchange tail만이 아니라 공통 mean potential 오차, short-range potential 입력, BO/nonadiabatic·mass/channel 가정을 확인한다. 물리 H2+ potential의 단순 leading asymptote를 finite-R bound로 사용하지 않는다. 이 항이 없으면 source-model theorem까지만 완료다.

C3U: >10 MeV/u. 같은 kinetic energy/frame에서 적용 가능한 state-summed bound 또는 source-evaluated extension을 확보한다. 비상대론 Maxwell 무한 support와 상대론적 speed cap을 혼용해 exact physical rate라고 부르지 않는다. NR 모델을 유지하면 kinetic-model discrepancy를 별도 남기고, 물리 relativistic profile이면 분포와 flux를 일관된 질량껍질 형식으로 다시 정의한다. 최종 H5 NR 결과와는 명시적 비교로 연결한다.

**반환:** 양 끝점의 positive integrated upper bounds, kinematics record, validity domain, 모든 상수의 authority, 사용했으면 Jost/discrepancy certificate. **PASS strict:** 전체 누락 범위의 인증된 상한. **PASS evaluated:** source 가정이 명시된 endpoint estimate만의 별도 profile. **STOP:** 확률만 극소하거나 점근식만 존재하면 rate-tail PASS가 아니다. 같은 문헌 검색을 반복하는 대신 빠진 상수/정리/데이터를 exact requirement로 전달한다.

### C4. 결정론적 적분 인증과 rate packet 조립

**담당:** external/local numerical runtime; 여기서는 수식·작업계약. **선행:** C2,C3의 선택 profile, 최종 packet은 C1.

1. 양의 분포/변환 Jacobian으로 source-panel별 integration을 한다. Core는 g 또는 E 적분, 독립 검산은 원래 p–g representation 또는 다른 수학적 quadrature로 구성한다.
2. GL refinement의 차이는 진단이다. Strict numerical certificate에는 interval quadrature, analytic panel remainder 또는 검증된 enclosure가 필요하다. Exp/erfc tails는 log-domain 또는 scaled functions로 계산하며 underflow를0으로 승인하지 않는다.
3. \(R_{core}^-\), \(R_{core}^+\), T_low,T_high, covered-domain uncertainty, epsilon_quad를 동일한 rate 단위로 조립한다. R→K 변환에 density를 한 번만 나누거나 곱한다.
4. \(R_{core}^->0\)일 때만 tail relative criterion 10⁻¹² 및 numerical target10⁻⁸을 검사한다. 양의 하한이 없으면 absolute enclosure를 산출하며 relative completion을 선언하지 않는다.
5. Count/model/evaluated/strict flag와 claim ceiling을 독립 필드로 저장한다. Parent의 physical_rate_admission flag는 해당 profile 승인 전에는 HOLD다.

**반환:** COUNT_RESULT.json, panelwise contributions/errors, exact input/output hashes, negative-control results, independent replay. **PASS:** 선택 profile의 모든 지배관계·수치 조건 충족. **STOP:** 잘못된 source는 수치오차가 아니고, runtime 실패는 이론 반례가 아니다.

### C5. 실제 host의 국소 반응 replay와 Bianchi consistency

**담당:** host runtime owner + independent reviewer. **선행:** C1,C4 및 profile별 admission AND gate.

1. 승인된 packet으로 isolated/shadow host run을 실행한다. 현재 스레드에서 production mutation 또는 collision run을 했다는 뜻이 아니다.
2. Count-only 경로에서 nHI→0, nCR→0의 영점, density bilinearity, nonnegative formation, g/u/channel mismatch 거부, wrong E_CM/E_lab 변환을 검사한다.
3. C1이 확정한 outgoing acceptance와 같은 count를 두 구현이 계산하는지 비교한다. 출사 속도 선택이 있으면 scalar1s total을 사용할 수 없다.
4. Bianchi-I collisionless \(p_i\propto a_i^{-1}\), \(n\propto(a_1a_2a_3)^{-1}\)를 검사하고, \(H_i\to H\)에서 FLRW 제한을 회복한다. Collision + geometry의 time-step splitting 오차는 독립적으로 분리한다.
5. fixed-event gas-frame rotational invariance와 spatial anisotropy evolution을 구별한다. Isotropic target 아래의 scalar count가 각도에 둔감하다는 사실로 전체 Bianchi 효과가0이라고 결론내리지 않는다.
6. 첫-step state identity, restart 반환, 저장된 response/source hash의 일치를 검증한다. 계산된 charge-exchange count를 photoionization이나 thermal heat로 자동 연결하지 않는다.

**반환:** 실행 가능한 command/config, REF_VS_HOST.json, balance ledger, accepted result. **PASS:** 실제 pinned checkout/runtime과 independent replay에서 같은 scoped quantity가 계약 안에 일치한다. **STOP:** environment/state mismatch이면 원 atomic proof를 다시 만들지 말고 경계만 복구한다.

### C6. parent 전달, 수락, 명시적 종료

**담당:** HOST4 + WU088 integration owner. **선행:** C5.

1. Final source/state/operator/result/uncertainty packet을 WU088 반응 registry에 전달한다. 어떤 profile과 observable이 승인되었는지 한 줄로 식별 가능하게 만든다.
2. Parent가 실제 consumer에서 같은 결과를 읽는 독립 intake를 수행한다. 수락 영수증에는 exact hashes, source class, frame/time/measure, output quantity와 유효영역이 있어야 한다.
3. 잔여 각 항을 '후속 연구', '별도 반응', '지원되지 않은 주장', '완료를 막는 필수 blocker' 중 하나로 분류한다. 단순 handoff 생성만으로 최종 수락을 가정하지 않는다.
4. 종료 후 동일 정의의 추가 검증은 새 반례·입력 변경·범위 변경·dependency hash 변경이 있을 때만 연다.

**종결 산출물:** 결과표와 해석, certified/estimated error ledger, executable reproduction, source/state provenance, dual-backup receipt, parent acceptance receipt. Strict profile이 끝나지 않았으면 `PARTIAL_RESULT_DELIVERED_NOT_THREAD_COMPLETE`로 정확히 남긴다.

## 6. 별도 확장: 전체 transport/deposition 및 joint uncertainty

확장 X는 이 스레드의 1s count와 다른 산출물이다. 전체 BASS 목표를 달성하려면 필요한 반응별로 X를 수행하되, 원자 count의 parent 인계를 모든 반응이 끝날 때까지 미루지 않는다.

X1: state-resolved differential/transport kernels, recoil energy와 fast/thermal membership, momentum·energy exchange. Total capture만으로 angular redistribution이나 heating을 만들 수 없다.

X2: P0의 physical multi-observable/cross-energy uncertainty와 실제 state-dependent W[state]를 결합한다. Full covariance가 없을 때 deterministic admissible-set propagation은 가능하지만, 이를 statistical covariance로 부르지 않는다.

X3: neutral H–H stripping/ionization은 HH raw matrix → propagation → asymptotic channel → source admission의 자기 DAG를 통과해야 한다. R9B element control을 collision cross section으로 import하지 않는다.

X4: thermal gas heat와 species mapping이 승인된 뒤 Grackle thermochemistry/downstream adapter와 parent deposition에 연결한다. CR heat를 RT photoheating field에 넣지 않고 energy·nuclei·charge ledger를 재확인한다.

이 확장이 닫혀야 해당 transport/deposition 결과를 주장할 수 있다. WU088 reaction registry는 count, transfer, heat, UQ의 admission flags를 분리해야 한다.

## 7. DAG와 진행 순서

논리 DAG는 `DAG.json`의 `all_of`, `any_of`, `conditional_requires`가 정본이다. `DAG.mmd`는 읽기용이다. 특히 LOW_GATE의 직접 majorant와 SOURCE_PHYS_GATE는 OR 관계이다. 반대로 SOURCE_PHYS_GATE는 SOURCE_JOST와 POTENTIAL_DISCREPANCY가 모두 필요한 AND 관계다. 모든 대안의 동시 성공을 요구하지 않는다.

현재 C0 완료 후의 실제 우선순위:

1. HOST_STATE_BIND와 CORE_1S를 즉시 병렬로 착수한다. 기존의 core/host blocker를 tail 이후로 미루지 않는다.
2. Low direct-majorant와 high endpoint/kinematics를 병렬로 진행한다. Low direct가 닫히면 Jost branch는 source-model theorem의 별도 연구로 남긴다.
3. 선택 profile에 대해 weighted quadrature/assembly를 수행한다. Model packet은 먼저 보존할 수 있지만 physical flags는 그대로 둔다.
4. 실제 host replay 및 parent acceptance에서 끝낸다. 새 H번호를 만드는 것은 종료조건이 아니다.

## 8. 반복·실패·중단·재개 규칙

각 루프는 최소 하나를 반환해야 한다: 새 usable source bytes, 증명된 불등식/반례, 실제 numerical certificate, source/host 결합, 명시적 branch 선택·종료. 같은 OPEN 항목을 다시 열거하기만 한 루프는 진전으로 집계하지 않는다.

Source transport는 동일 URL의 반복 시도가 아니라 이미 확인된 대체 provider/object ID를 최대 두 경로까지 확인한다. 그래도 실패하면 `SOURCE_KNOWN_TRANSPORT_BLOCKED`로 두고 다른 독립 작업을 수행한다. Source absence라고 바꾸지 않는다.

각 bounded numerical batch는 config/input hash, progress, completed nodes, restart cursor를 즉시 기록한다. 미완성 array를 final source로 가져오지 않는다. 수치 budget 초과 시 정확한 마지막 certificate·미해결 panel을 반환한다. 무조건 l 또는 mesh 전체를 두 배로 늘리는 규칙은 쓰지 않는다.

Mathematical obstruction이 나오면 그 조건을 다음 입력계약으로 바꾼다. 예: d0≤0이면 bound가 안 나오는 것이지 cross section이 무한이라는 결론이 아니다. Interval이 넓으면 chart/partition/majorant를 조정하되 tolerance는 결과 후 변경하지 않는다.

현재 numerical model의 source precision이 부족하면 모델 결과를 보존하고 strict result를 미승인으로 종료할 수 있다. 이것은 전체 연구목적 완료가 아니라 정확한 partial delivery다. 프로젝트의 과학적 완료와 유한한 실행 중단을 같은 status로 합치지 않는다.

## 9. 정기 import와 백업 프로토콜

CP0: parent hash와 정확한 다음 work unit을 고정하고, 관련 sibling만 fresh 검색한다.
CP1: 새 증명/데이터/계산 결과를 write-once checkpoint로 보존한다. Sibling에 새 FINAL이 보이면 manifest와 reaction/observable/units/frame/energy/UQ 계약이 맞는 부분만 가져온다.
CP2/FINAL: stage acceptance와 변경된 DAG만 확정하고 final pre-seal bounded refresh를 한다.

전역 Dropbox/Drive 전수검색을 각 수학 단계에 끼워 넣지 않는다. 정확히 필요한 sibling branch의 최신 checkpoint와 마지막 import 이후 hash 변화만 본다. Streamed text-only intake와 exact-byte intake를 다른 상태로 기록한다.

원격 backup 완료는 두 provider의 실제 성공 응답이 있어야 한다. 가능하면 size/objectID/provider hash를 대조하고 raw readback 여부를 별도로 쓴다. Receipt의 자기 자신 SHA를 archive 내부에서 재귀적으로 완성하려 하지 않는다. Receipt는 detached로 보존한다.

**현재 H16 환경:** Google Drive/Dropbox는 enabled·installed이며 읽기 성공. 그러나 현재 discovery에는 upload action이 노출되지 않았다. 따라서 새 H16 산출물의 이중 온라인 백업은 미완료이며, 로컬 경로·hash·manifest와 upload-ready handoff만 제공한다. 이를 permission revoked 또는 과거 backup 실패로 추정하지 않는다. C1 이후 다른 실행환경에서 write action이 실제로 제공되면 같은 exact files를 create-only로 업로드한다.

## 10. 이번 루프 종료 후 상태

완료: 원 목적 복구, H15/R25 바이트 검증, scope-matched sibling 상태 동기화, P1–P7 직접 유도, symbolic/독립 대수 검사, 단계별 계획·논리 DAG·acceptance contract.

미완료: 실제 B/exterior-Jost/all-ℓ 수치 certificate, physical potential discrepancy, extreme endpoints의 hard source envelope, core physical continuum error, 실제 host/state admission, physical collision rate run, parent acceptance, 새 H16 온라인 이중 백업.

가장 중요한 다음 행동은 **CORE_1S와 HOST_STATE_BIND를 동시에 진행하면서, tail은 positive-functional 예산에 필요한 만큼만 닫는 것**이다. 전체 atomic scattering 문제를 모두 해결하는 것을 H5 count의 자동 선행조건으로 삼지 않는다. 반대로 작은 확률이나 좋은 보간을 근거로 기존 strict physical gate를 몰래 완화하지 않는다.


## 근거 문서와 출처

[SRC_H5] WU088_HOST4_H5_REPORT_KO_20260921.md, §§2–4, §§6–8. Model-defined state, observable signature, state/host admission 범위. 현재 Library bytes는 intake/purpose_sources에 보존했다.

[SRC_H10] WU088_HOST4_H10_REPORT_KO_20260921.md, §§1–7, §§10–11. Central1s continuum model과 source authority의 구별, positive functional, 네 error ledgers.

[SRC_H15] WU088_HOST4_H15_REPORT_KO_20260922.md와 exact FINAL archive. Wronskian identity, IAEA evaluated envelope, endpoints 및 남은 gates. 현재 바이트 검증은 results/PARENT_BYTE_VERIFICATION.json.

[SRC_R25] H15 안의 P0 R25 FINAL archive. 현재 SHA/CRC/1200-entry manifest 검증은 results/R25_BYTE_IMPORT_VERIFICATION.json. 해당 solver run을 재실행한 것으로 표시하지 않는다.

[SRC_CR14] Dropbox R3M14 v2 preflight archive extracted text, object ID와 범위는 results/SIBLING_SYNC.json. 텍스트 수준 intake만 수행했다.

[SRC_HH9B] Google Drive R9B report, 같은 sync record. 다른 반응의 full-H element control이며 scalar CX source로 채택하지 않는다.

[EXT_IAEA] R. K. Janev & J. J. Smith, Atomic and Plasma-Material Interaction Data for Fusion, Vol.4 (IAEA,1993), Introduction 및 §2.3.1/printed p.78. 이번 web parsed text에서 all-final-state definition와 reported fit/accuracy를 재확인했다. Web screenshot 요청은 cache-miss로 실패했으므로 이번에는 원 수치표를 새로 시각 검증하거나 재추출하지 않았다. Parent H15의 materialization과 이번 원문 텍스트 확인을 구별한다.

[EXT_PHASE] K. Chadan, R. Kobayashi, T. Kobayashi, The absolute definition of the phase-shift in potential scattering, arXiv:math-ph/0103044. Variable-phase/phase-branch 맥락만 참고한다. H16 경계 비교식과 수치상수의 권위로 인용하지 않는다.

H16의 새 P1–P7는 위 parent 및 방정식 정의에서 직접 유도했으며, 문헌의 알려진 수치 결과로 포장하지 않았다.
