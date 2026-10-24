# C23E: 실제 PW19 광원과 D43K 화학 퍼텐셜의 조건부 연결

## 결과의 위치

이 연구의 새 대상은 이미 완성된 H/D 전하교환 적분이 아니라, 저장된 C23B 광원에서 D의 문턱에 맞는 세 모멘트를 만들고 그 모멘트를 같은 결합에너지의 PI/RR/CX 장부에 연결하는 것이다. 시간 적분은 수행하지 않는다. 실제 수치 결과는 별도 RESULTS_KO.md와 create-only runs/ 아래에 결속된다. 이 문서는 계산 전 확정한 식·가정·판정 범위를 제공한다.

최근 조사에서 REI ISO-COUPLE-P1/P2와 WU PHYS79가 H/D 전하교환의 진행량 환원, 열용량, 원본 Savin 두 fit의 상세평형 차이, D43K 보존적 연산자를 이미 갖고 있음을 확인했다. 따라서 처음 준비한 열적 CX 재실행 계약은 실행 전에 폐기하고 기록만 history/에 남겼다. 새 발견·새 ODE로 세지 않는다. 중앙 WU_D_PI_RR_MATCHED의 Milne 관계·동위원소 원전 gate도 이번 조건부 연결만으로 닫히지 않는다.

## 1. 원전과 재사용 대응

| 근거 | 실제 재사용 | 이번에 추가하지 않는 주장 |
|---|---|---|
| C23B, bass_cr4a0bbc0e의 source_providers | PW19 공개 release의3개 z 스펙트럼, Verner H 단면적, 이미 계산된 H 모멘트와 양의 quadrature atom | 새 H 광원 재적분, z 연속 이력 |
| REI PR180 c4a148a8, PR181 b6551164 | threshold-gated H-equality D 모델과 명시적 isotope 상태라는 설계 | 기존13상태·manufactured70/30eV 검증을 새21상태 PW19 검증과 동일시 |
| WU PHYS79 PR134 science338fb772/final3304d16d | delta=43 kB 및 kr 고정, kf=kr exp(-43/T), 공통 화학 퍼텐셜 | 원본 Savin forward fit 보존이라고 주장하거나 새 CX 발견으로 명명 |
| C22A rr_energy_moment.py | VF rate fit에 조건부로 대응하는 포획 전자 에너지 모멘트 | rate fit 정확도로 derivative 또는 실제 D recombination 정확도 인증 |
| C23C atomic_contract.py | 이름으로 식별되는21population,8핵종 및 전하 incidence | spectator 반응률을 물리적0으로 채우기 |

외부 원전은 Savin(2002), ApJ566,599, DOI[10.1086/324218](https://doi.org/10.1086/324218), Verner et al.(1996), ApJ465,487, DOI[10.1086/177435](https://doi.org/10.1086/177435), Verner & Ferland(1996), ApJS103,467 및 [저자 recombination data](https://www.pa.uky.edu/~verner/rec.html), Taira et al.(2025), [arXiv2505.23544](https://arxiv.org/abs/2505.23544), 공개 release DOI10.5281/zenodo.15367103이다. SciSpace에서 Savin 논문을 검색했고 원문 PDF의 식과 표를 확인했다. 현재 Grackle master의 k50/k51도 pinned commit6d57fe2c3eb07c34dadb0b0e568cdc12f975146d에서 대조했다. Grackle의 온도외 처리나 기존 REI의 별도 operational T 범위를 이번 VF/CX 교집합으로 자동 이식하지 않는다.

## 2. 물리 모형과 단위

정상 관측자 bath frame의 정지 표적, 등방성 기체, 고유시간을 쓴다. 반응 기체는 등방성 stress closure이고 비등방 matter stress는 별도 비바리온 Vlasov 부문이다. Non-tilted LRS, full Frobenius norm, 부호 있는 진폭과 norm·상쇄 구별은 그대로 유지된다.

광원 열은 S(E)=4*pi*nu*J_nu 이며 단위 erg cm^-2 s^-1이다. 에너지 bin 적분값으로 읽지 않는다. photon energy E를 eV로 쓰면 표적 하나당 흡수 사건 밀도는

q(E) = S(E) sigma_H(E) / (eV_erg E^2),

단위 s^-1 eV^-1이다. eV_erg=1.602176634e-12이다. 기존 H 모형의 chi_H=13.6eV와 상한 M=50000eV를 유지한다. 공개 자료의 분광학적 문턱값으로 몰래 바꾸지 않는다.

PHYS79가 선택한 delta=43 kB=0.0037054533027224263eV를 쓰고 chi_D=chi_H+delta로 둔다. 43K는 이 연구 계열의 명시적 모형값이다. 기존 REI 제조 입력0.0037eV와는 별도 identity다. D 단면적은 E>=chi_D에서 H 단면적과 같고 문턱 아래에서는0이라는 조건부 근사를 택한다. 실제 finite-mass isotope 단면적을 새로 공급한 것은 아니다.

온도는 RR 원전의3..1e9K와 CX 원전의2.7..2e5K가 겹치는3..200000K이다. 광원은 z=2.316,2.479,2.649의 원 release 노드만 쓴다. 각 노드 내부 positive log-log interpolation은 기존 C23B의 유한 표현이다. 이산화 오차, 원전 fit 오차, 동위원소 근사 오차와 천체 광원 불확실성은 서로 다른 항이다.

## 3. 전체 광원을 반복하지 않는 문턱 이동 항등식

기존 저장값을 Gamma_H=integral_chiH^M q(E)dE, K_H=integral_chiH^M(E-chi_H)q(E)dE, A_H=integral_chiH^M E q(E)dE라 하자. 양의 q와0<delta<M-chi_H에 대해 새 구간의 세 값을

G_l=integral_chiH^chiD q(E)dE,
A_l=integral_chiH^chiD E q(E)dE,
B_l=integral_chiH^chiD(chi_D-E)q(E)dE

로 정의하면, 선택한 D 모형에서 정확히

Gamma_D=Gamma_H-G_l,
K_D=K_H-delta*Gamma_H+B_l,
A_D=A_H-A_l

이다. 두 번째 식은 D 구간에서 E-chi_D=(E-chi_H)-delta를 대입하고 빠진 저에너지 구간을 분리하면 얻어진다. 따라서

chi_D*Gamma_D+K_D-A_D
=chi_H*Gamma_H+K_H-A_H

이고, 원 H 장부의 잔차만 상속한다. B_l=chi_D G_l-A_l를 큰 두 항의 차로 구현하지 않고 양의 integrand로 직접 계산한다. delta->0이면 새 band가 사라지고 H 값으로 연속 복귀한다. q>0인 band에서 Gamma_D<Gamma_H, A_D<A_H이다. K_D는 원 정의의 비음성 integrand로도 양수임을 확인한다.

새 정리의 강한 불가능성 주장이나 novelty 우선권은 없다. 저장된 같은 공급자의 모멘트를 다른 문턱에 재사용하는 구성적 항등식과 그 실데이터 구현이다. 계산량의 대수적 축소를 wall-time speedup으로 부르지 않는다.

### 기존 양의 atom을 단순 필터하면 무엇이 달라지는가

원 H Gauss atom은 기존 spectral cell을 적분하는 유한 측도다. 새 delta가 cell 내부를 자르면 K<delta인 atom 전체를 제거하는 이산 연산과 연속 구간[chi_H,chi_D]의 실제 사건률은 일반적으로 같지 않다. 기존 H atom에 대한 필터 자체는 정의대로 정확하다. 그러나 그것을 연속 D source의 정밀 문턱 보정이라고 해석하려면 새로운 경계 정렬 검증이 필요하다.

이번에는 저장 atom을 읽어 그 차이만 측정한다. production 계산은 새 좁은 band를 GL16으로 평가하며 GL8/32를 비교한다. 독립 검산은 새 D 전체 구간에 대해서만 scipy.quad를 호출한다. 완료된 H source 적분은 재실행하지 않는다. 이 판별은 D의 cutoff bin이나 secondary stopping 열전달을 공급하지 않는다.

## 4. 하나의 결합에너지와 전자 pool

21개 핵종·전하 population을 이름으로 입력하고 n_e,all=sum q_i n_i를 계산한다. 호출자는 열적·fast 전자 수를 따로 공급하여 n_e,all=n_e,thermal+n_e,fast를 만족해야 한다. n/T의 명시적 초기0은 이 검증 inventory의 선언이며 다른 species 누락을 대신하는 값이 아니다.

광이온화 X0+gamma -> X+ +e의 rate는 n_X0 Gamma_X다. 같은 사건에서 binding은 chi_X, fast electron kinetic은 E-chi_X, 흡수 광자는 E다. 이번 operator에서 primary electron은 fast source로 기록하며 즉시 열화하지 않는다. thermal heat에 같은 초과에너지를 더하지 않는다.

RR X+ +e_thermal -> X0+gamma는 alpha(T)n_X+ n_e,thermal로 평가한다. VF fit이 온도에 무관한 단면적의 Maxwellian 평균을 나타낸다는 조건 아래 포획 kinetic moment는

K_capture = kB*T*(3/2 + d ln(alpha)/d ln(T)).

이 fit family에서는 기존 C22A가 유도한 양의 형태

K_capture/(kB*T) = (1-b)/(2(1+sqrt(T/T0))) + (1+b)/(2(1+sqrt(T/T1)))

를 그대로 쓴다. binding 감소chi_X, thermal kinetic 감소K_capture, escaping photon 증가chi_X+K_capture가 한 사건에서 닫힌다. alpha_D=alpha_H와 capture_D=capture_H는 조건부 근사다. 실제 D PI와 RR이 모든 bound level을 포함한 Milne 관계를 만족한다는 별도 물리 주장은 없다.

CX의 순진행률 J=kf n_D0 n_H+ - kr n_D+ n_H0에 대해 chemical 증가delta*J, thermal 변화-delta*J다. 총 자유전자수와 두 pool 수는 이 사건에서 변하지 않는다. WU의 kr 고정 상세평형 근사 kf/kr=exp(-43/T)를 재사용한다.

그 결과 선택된 모든 사건에 대해

dU_binding+dU_thermal+dU_fast+L_escape-P_absorbed=0

이다. 21species 중 나머지 원자는 기여 전자 수를 포함하지만 reaction incidence는 spectator다. 그 실제 CI/RR/DR/CX rate coverage가 완성되었다고 해석하지 않는다.

### 서로 다른 퍼텐셜을 섞으면 발생하는 구체적 결함

H ionization, D0+H+ charge exchange, D recombination의 닫힌 화학 경로에서 퍼텐셜 합은 chi_H+delta-chi_D=0이다. 기존 equal-H/D 문턱을 PI/RR에 남긴 채 D43K CX 열항만 넣으면 합이delta가 된다. 따라서 새 API는 각 활성 과정의 potential descriptor를 일치시키고 이러한 혼합을 거부한다. 원본 C21O 모형은 소급 수정하지 않는다.

Wolfram 실제 평가에서 boundary 모멘트 항등식, PI/RR/CX 및 위 경로의 에너지 잔차는 각각0이었다. 의도적으로 섞은 equal-threshold 경로는delta를 돌려주었다. 원 코드와 실제 응답은 theory/D43_BOUNDARY_DERIVATION.wl 및 D43_WOLFRAM_RESULT.json에 있다.

## 5. 동위원소 quotient와 후속 오차 예산

H/D를 단순 elemental charge state로 합치는 exact quotient는 두 동위원소의 동일 생성자가 필요하다. 이 선택 모형에서는 Gamma_D=Gamma_H-G_l이므로 양의 광원 band가 있으면 PI rate가 다르다. 상태별 binding도delta만큼 다르다. 따라서 기존 동일-rate21->9 quotient를 이 모형에 무조건 적용할 수 없다. 적어도 D의 독립 charge state와delta*n_D+ binding 기여를 유지하면 선택 연산자는 재사용된다.

H-equality를 천체 관측량 차원에서 근사해도 되는가는 D abundance, 열상태, 광원과 목표 오차에 달려 있다. 이번18상태는 제조된 순간 검증으로, 그런 관측량 허용오차를 정하지 않는다. 유효한 local moment 일치가 전역 시간적분 오차 bound가 되지 않으므로 global_error_bound=null을 유지한다.

## 6. 판정 범위와 다음 실행점

새 국소 source adapter는 frozen tolerance, 입력 identity,18개 상태, 실패경로 및 fresh Astra 검토를 통과한 경우에만 NUMERICALLY_CHECKED_SCOPED로 승격한다. 광원 문턱에 결속된 새로운 모멘트와 에너지 owner가 그 산출물이다. WU_D_PI_RR_MATCHED의 empirical/Milne gate, full21 원자 coverage와 CR_N5 부모는 OPEN/PARTIAL이다.

다음 연구는 선택 D 원자 공급자의 finite-mass/level-resolved PI–RR 대응을 확보하거나, 목표 정확도를 정한 조건부 모형 사용을 명시적으로 선택하는 것이다. 동시에 full stopping의 neutral/ion/inelastic channels, 위10eV source, finite bath·escape는 별도 노드로 남는다. 그 이후 N6 보존적 coupling과 새 입력/N7 parcel을 진행한다. 기존 source,cutoff,ISO-COUPLE,PHYS79 및 NCP51을 복원 명목으로 다시 실행하지 않는다.
