# 다음 단위 R1 범위 제안 — 실제 source 부모 표적 귀속과 native25 사건 장부

상태: root가 R1을 고정하기 위한 과학 intake 제안이다. R1/R2 완료나 새 수치 계산의 승인을 자체 선언하지 않는다.
제안 단위: CR_PHYS02_PARENT_EVENT_NATIVE25_V1
제안 경로: research/cr_parent_event_native25_20261028
새 예산: root가 제안한 별도 40 CPU-s(준비·worker·coordinator·tail 포함). 과거 잔여 이월 0.
작성 역할: 이론/입력 식별 제안자. production 코드 작성·새 과학 실행·CAS 실행·옛 solver/quadrature 재실행 모두 0.

## 1. 새로 만들 결과와 재사용 경계

실제 PHYS02 low-birth source의 H/He **전자 생산량**을 원 생성식의 3계수 모델 안에서 새로 식별한다.
원 저장 source의 byte·합산 spectrum·proper history·3201개 atom은 변경하지 않는다.
PR110의 저장된 3200-state response, 네 prefix/네 observation bin, cutoff·Coulomb·H/He RR 및 retained-photon 결과를 그대로 재사용한다.
이 결과에 새로운 이름의 동일 100 K native25 **부분/조건부 사건 소비자**를 붙인다.
실제 He 독점 분기, 선택 구간 밖 partner, excitation, 실제 외부 CR 에너지 차감이 없으면 실제 전체 native25 point는 null이다.

원 source recipe의 nH=140과 nHe=nH·0.248/[4(1−0.248)]는 **전체 핵 수 밀도**다.
이온화 source의 실제 neutral target은 각각 0.99배이며 이 인자는 source 계수에 이미 포함되어 있다.
새 조건부 H1/He4 inventory의 nb=140+4·1085/94=8750/47 m^-3를 재사용한다.
PR109의 nb=null, 별도 REI/BASS/PW19 상태는 바꾸거나 가져오지 않는다.
고정 clock은 proper time 0≤t≤T=1e10 s, source q(t,W)=t A(W), scalar gas-rest frame, fixed proper-volume density이다.
절대 worldtube 부피와 이후 history는 null이다.

## 2. 알려진 생성식으로 제한한 계수 식별

I_H^src=13.605693122994 eV, I_He^src=24.59 eV.
f1(I,W)=(1+W/I)^(-3), f2(I,W)=(W/I)(1+W/I)^(-3).
원 H Williams-limit에서 c1_H=(7/3)c2_H이므로

A(W)=theta_H[(7/3)f1(I_H,W)+f2(I_H,W)]
     +theta_He1 f1(I_He,W)+theta_He2 f2(I_He,W).

이는 새로운 자유 spectrum 가정이 아니다. 실제 causal_subthreshold.py, causal_cascade.py, rudd.py에 있는 생성식이다.
이 식의 모든 항은 원 1–4 MeV proton quadrature의 모든 node에서 W endpoint보다 작은 공통 영역에서만 사용한다.
실제 저장 source-coverage의 최소 endpoint는 2154.927725… eV이므로 아래 0–1000 eV anchor는 공통 support 안이다.
0–1000 eV anchor 사용은 현재 .1–10 eV birth cohort의 support 확장이 아니라 원 계수의 식별 근거다.

실제 PHYS02A NUMERICAL_RESULT.json에 [0,.1], [.1,1], [1,3], [3,10], [10,100], [100,1000]의 합산 energy coefficient가 저장돼 있다.
제안 고정 recovery anchors는 [0,.1], [3,10], [100,1000]; 나머지 3개는 fitting에 쓰지 않는 holdout이다.
각 행 M_bj=∫_band W f_j(W)dW, b_b=저장된 energy coefficient로 3×3 선형식을 푼다.
필요한 적분은 유리함수와 log의 닫힌식이며 원 64-node proton quadrature를 다시 계산하지 않는다.
세 계수는 ORIGINAL_SAVED_COEFFICIENT_BYTES가 아니라 **MODEL_IDENTIFIED_FROM_PINNED_MOMENTS**이다.

문헌/코드의 H 비율은 실수 식에서 정확하지만 원 binary64의 서로 다른 dot accumulation에는 반올림 차이가 있을 수 있다.
그 차이를 허용치 안에서 검증해야 하며, 실패하면 4계수 fit·새 source 생성·허용치 완화를 몰래 대체하지 않는다.
독립 reference는 별도 analytic moments/선형해와 미사용 atom/holdout을 사용하고 production module을 import하지 않는다.

### 허용치 제안: R1에서 root의 명시적 채택 필요

- dimensionless row/column scaling을 문서로 고정한 recovery matrix의 rcond_inf ≥ 1e-6.
- 저장 anchor의 수치 일관성 perturbation envelope eta=2e-12(물리 모델 오차 인증이 아님)를 고정.
- componentwise sensitivity |M^-1|·(eta|b|)/|theta|의 최대값 ≤ 1e-8, 그 envelope 안에서 계수 양수.
- 미사용 저장 band moments: 각 양수 값 자신의 scale에서 상대차 ≤ 2e-12.
- 실제 canonical source atoms의 재구성 일관성: atom 자신의 scale에서 ≤ 2e-11; 정확한 0은 절대 0 규칙.
- target-resolved N/E의 독립 계산 일치: 각 양수 target quantity 자신의 scale에서 ≤ 1e-9.
- 새 split의 total N/E와 canonical 저장 aggregate의 합치: ≤ 2e-11.
- native stoichiometry/charge/baryon/energy algebra 및 conditional finite-caloric 장부: ≤ 1e-11, tiny increments를 baseline 크기로 숨기지 않음.
- interval/roundoff 엄밀 인증 또는 physical accuracy로 위 ordinary arithmetic checks를 승격하지 않음.

조건을 못 맞추면 MODEL_IDENTIFICATION_UNRESOLVED를 남긴다. 원 source/G/RR 재실행이나 spectrum renormalization을 자동 개시하지 않는다.

## 3. 원 projection의 정확한 의미

원 low source는 W∈[.1,10]에서 8-point cell quadrature 후 number-linear barycentric projection을 하고 E_j·N_j 좌표로 저장했다.
첫 cell은 E=.1 ghost와 첫 active node로 나뉜다. 직접 cutoff atom은 W<.1 source가 아니다.
각 target extent는 원 projector P를 공유해야 한다:

a_(s,j)=P_j[A_s],   a_j=P_j[A_H+A_He].

P_j가 cell integral이므로 a_j·A_s(E_j)/A_total(E_j)는 일반적으로 a_(s,j)가 아니다.
원 canonical a_j를 새 계산값으로 대체하지 않는다.
새 attribution에 필요한 고정 basis projection만 계산하고, 저장 aggregate와의 잔차를 별도 기록한다.
부모 species extent만 필요하면 전체 source array의 재생성 없이 target별 low N/E와 미사용 atom anchors로 검증할 수 있다.
표적 density, proper factor729, angle integration, nb 변환, finite-time t²/2를 각각 한 번만 적용한다.

N_s[a,b]=(b²−a²)/2 ·∫_.1^10 A_s(W)dW.
U_s[a,b]=(b²−a²)/2 ·∫_.1^10 W A_s(W)dW.
단, 원 projection의 retained discrete N/E를 authoritative로 두고 이 연속 생성식의 평가와 차이를 검사한다.
원 source는 전자별 marginal이며 target attribution 자체가 parent-event pairing을 복구하지는 않는다.

## 4. 실제 식별 가능성과 He의 일반 family

Rudd 1992 §II 원문은 방출 전자의 수를 세는 inclusive SDCS로 정의한다.
H는 한 bound electron인 원자 표적이므로 조건부 H→H1 mapping 안에서 선택된 H-electron count J_H가 direct H1I→H1II parent extent다.
He의 선택 전자 수 N_He는 exclusive HeI→HeII/HeIII 사건 수가 아니다.

선택 low cohort와 교차하는 He 사건을 다음과 같이 둔다.

- s: single ionization, 그 한 전자가 선택됨.
- p: double ionization, 두 전자 중 하나만 선택됨.
- d: double ionization, 두 전자 모두 선택됨.

s+p+2d=N_He, s,p,d≥0.
따라서 source-parent contribution은
Δn_HeI=−(N_He−d), Δn_HeII=N_He−p−2d, Δn_HeIII=p+d.
그 parent가 낳은 전체 free-electron charge는 N_He+p이다.
p개의 선택 밖 partner의 energy·proper history·후속 response는 필요한 별도 port이며 실제 값은 null이다.
He+ residual excitation도 source에서 제공되지 않으므로 별도 hidden atomic-energy port가 필요하다.
p=0 closed selected family, d=0 one-electron effective channel, ground residual은 명시적 conditional fixtures만 가능하다.
실제 p,d,s 개별 point·branch spectrum·partner history를 임의로 채우지 않는다.

저장 selected-cohort RR C_H,C_He를 합성한 식별 성분은
Δn_HII=J_H−C_H,
Δn_HeII=N_He−p−2d−C_He,
Δn_HeIII=p+d,
중성 species는 핵 수 보존으로 정한다.
이는 **selected response + parent family**다. 미식별 partner의 후속 RR/escape/thermal response까지 계산한 실제 전체 endpoint가 아니다.

## 5. 에너지 convention bridge와 외부 donor의 한계

원 H binding13.605693122994와 저장 RR H13.60을 같은 값으로 덮어쓰지 않는다.
선택 전자에 대해 원 source recipe가 정의하는 computable loss functional은
L_Rudd,selected=U_inj+I_H^src·J_H+I_1^src·N_He.
CRIPTIC 2022 §2.3.3 Eq23은 바로 (W+I) weighted loss를 사용한다.
그러나 이것을 실제 exclusive-He 사건의 proton debit로 승격할 수 없다.

일반 He parent family의 필요한 ground-state donor work에는
U_partner + I_2^src·p + (I_2^src−I_1^src)·d
가 더해지고, residual excitation/recoil 등 선택한 물리 모형의 별도 항이 있으면 그것도 필요하다.
I_2^src나 partner 값을 기존 HeIII RR 데이터에서 몰래 채우지 않는다.

공통 recipient chemical convention I*에 대해(먼저 closed selected one-electron fixture)
ΔB*=Σ_s I*_s(J_s−C_s),
U_gamma=Σ_s(K_Cs+I_s^RR C_s),
U_inj=U_active+Q_C+U_cut+Σ_s K_Cs.
따라서
L_Rudd,selected−[U_active+Q_C+U_cut+U_gamma+ΔB*]
=Σ_s(I_s^src−I*_s)J_s + Σ_s(I*_s−I_s^RR)C_s.

우변은 **명시적 convention residual sidecar**다. physical heat 또는 w_ext로 이동시키지 않는다.
I_H*=13.60이면 H source 차이는 0.005693122994·J_H eV/m³이다.
일반 s,p,d family에는 chemical basis의 p,d 계수, actual branch work와 partner port를 추가해 같은 방식으로 잔차를 보존한다.
retained gamma의 w_ext 기여는 0이나, **실제 total external-work/w_ext point는 null**이다.
실제 CR proton population의 depletion/history 또는 signed native w_ext ownership 계약은 아직 없기 때문이다.

## 6. cutoff retention과 조건부 finite-caloric endpoint

기본은 cutoff retention: selected unresolved electrons N_cut,U_cut를 별도 retained port로 유지한다.
명시적으로 nonthermal subset으로 보관하는 새 consumer에서는 selected Δζ=(N_active+N_cut)/nb,
selected Δw_nt=(U_active+U_cut)·eV_J/nb이다.
상태의 모든 자유전자를 thermal이라고 놓는 old FS10 consumer에 그대로 넣지 않는다.

선택 밖 partner closure를 명시한 conditional fixture에서만 cutoff의 즉시 thermal assimilation을 선택할 수 있다.
그때 selected Δζ=N_active/nb, selected thermal-electron increment=N_cut이고 Q=Q_C+U_cut이다.
nb는 일정하고 총 핵 수는 보존된다. 원 100 K response의 rate를 바뀐 T로 다시 계산하지 않는다.

n_part,0=n_H+n_He+n_e,0, T0=100 K일 때
T1=[n_part,0 T0 + 2Q/(3kB)]/[n_part,0+N_cut],
δT/T0=[Q/(1.5 kB T0)−N_cut]/[n_part,0+N_cut],
ΔlogT=log1p(δT/T0).

Q는 J/m³로 변환을 한 번 적용한다. 고정 heat capacity로 ΔT만 더하는 방식과 달리 새 thermal electron의 particle count를 포함한다.
baseline+increment를 authoritative로 저장한다. tiny ΔY/ΔlogT를 binary64 baseline에 더해 사라진 값을 '0 변화'로 보고하지 않는다.
partner가 thermal population/energy에 줄 실제 기여가 미식별이면 실제 T1/전체 native25는 null이고, 위 결과는 conditional component/fixture다.
이 새 caloric closure는 PR110을 소급하여 physical-heating 완료로 바꾸지 않는다.

## 7. 최소 입력과 소유권

필수 pin:
PR110 S/D/M, canonical source record hash, 실제 PHYS02A/B/Rudd/injection source inventory,
recovery/holdout moments와 정확한 raw JSON bytes, 원 grid/projector 및 source atom bytes,
PR110 저장 prefix/bin RESULT와 capture/photon atoms, native25 order/energy basis를 제공하는 실제 consumer revision,
동일 conditional inventory와 clock/frame/support, source family 및 birth partition, 새 source-parent attribution ID.

source consumption은 source family+native birth partition+proper interval에 한 번만 claim한다.
RR/cutoff/photons의 observation bins는 저장된 absolute history를 그대로 쓴다. prefix 차이를 새로운 source birth로 claim하지 않는다.
새 native25 composition은 기존 RR-only claim을 포함하는 하나의 새 aggregate claim이어야 하며 두 출력을 같은 recipient에 중복 적용하지 않는다.
부모 출생 target과 RR 포획 target을 동일한 label로 가정하지 않는다.
He parent p,d와 partner 입력은 별도 event identity를 가져야 하며 branch/event pair를 marginal에서 만들어 내지 않는다.

## 8. 완료로 주장할 수 있는 범위

가능한 새 결과: pinned generated-model H/He attribution, H의 식별 가능한 parent contribution,
He의 일반 selected-support affine constraints, 조건부 native25/event-energy consumer와 finite-caloric 함수,
실제 provenance 및 실패를 포함한 독립 검토.

유지할 null: actual exclusive He branch point/잔류 상태, partner source·energy/history/response,
actual full low-source physical native25 point, full9600/full-source native25, actual proton depletion/debit,
absolute worldtube totals, photon reabsorption/escape activation, full physical heating, global physical completion/error/budget/currency.
N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4=false, 현재 관찰 중앙28/88 및 이 CR 집계효과0를 보존한다.

