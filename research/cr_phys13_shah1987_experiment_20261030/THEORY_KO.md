# PHYS13: Shah 1987 원측정 H 원자 전자충돌과 원래 H/He RR source

## 정의와 source authority

시공간 metric signature (-,+,+,+); 첫 광흡수 확률은 원래 PHYS09/PHYS12 source 모듈의 정상 proper-time kinematics로 고정. 원래 H I n_H = 138.6 m^-3, He I n_He=11.427127659574467 m^-3, 100 K 고정 상태, photon source 원자 6400개 및 출생구간 4개를 변경하지 않는다.

Shah, Elliott and Gilbody (1987), *J Phys B 20*, p3508 Table 1의 실측 H(1s) 전자충돌 총 이온화 단면적 26점 E_e=14.6...21.4eV를 수동 전사. 단위 10^-17 cm^2=10^-21 m^2. 67% 재현성·통계 오차는 측정점마다 제시; p3509의 **추가 공통 절대 정규화 오차 6.8%**는 별도. 기호 '*'의 의미를 추정하지 않고 원문에서 본 위치만 기록. Kim (1992) Eq.(2)/Table1은 *Shah 데이터를 근사한 경험식*, Bray et al (2018) PRL121 203401의 Wannier 지수 1.127은 근임계 법칙이며 Shah 원 측정점이 아니다.

## 측정 지원영역의 구간별 수치 형태

측정 매듭점 {E_i,σ_i} 사이에서만 σ_interp(E)=σ_i+(E−E_i)(σ_(i+1)−σ_i)/(E_(i+1)−E_i), E∈[14.6,21.4]eV. 20.99 eV 최대 원래 광전자도 20.9와 21.4 eV 실측점 사이에 존재한다. 이 밖 E<14.6 eV는 **unmeasured**, 0이라는 물리 판정은 하지 않는다. electron 초기 운동에너지 E_e=E_γ−I_H(source) (I_H=13.60eV), 표적 상대 운동에너지의 100K 열적 분포는 미적용.

조건부 collision hazard ν=n_H σ_interp(E_e) sqrt(2 e_J E_e/m_e) [s^-1]. 원래 He/H competing photon hazards k_γH, k_γtotal와 생년 s, 관측 T에서 첫 광자 H 흡수 뒤 H 원자 전자충돌이 일어날 수 있는 모형상 최대 노출:

P_2(T|s,E_e) = ∫_0^(T−s) k_γH exp(−k_γtotal u)[1−exp(−ν(T−s−u))] du.

초기 전자의 에너지 증가나 외부 가속이 없고 실제 시간별 충돌 hazard ≤ν(initial)인 경우에 한해 노출 상한이다. 실제 stopping, 산란, 확산, 100K 운동 표적, 공간/기하 이력 없이 확정된 사건율은 아니다.

 공통 실험 정규화 η에 대한 미분은

∂P_2/∂ln η = ∫_0^(T−s) k_γH exp(−k_γtotal u) ν(T−s−u) exp(−ν(T−s−u))du ≥0.

26 측정점 개별 67%-level 오차 δ_i와 추가 공통 ±6.8% 정규화를 동시 선택한 σ_i^±=(σ_i±δ_i)(1±0.068)은 *stress-scenario endpoints*, **신뢰구간/엄밀한 경계가 아니다**. 실제 측정 불확실도 공분산은 별도 제공되지 않았다. 모델 외삽 없음.

## 실제 데이터, T=10^10 proper s

- PHYS11 source 원래 에너지상 허용 첫 이벤트 1.28863125860899684e-28 m^-3.
- Shah 실측 지원영역 비중 0.70037795, 미측정 기여의 *kinematic capacity* 3.86102336573753815e-29m^-3.
- Shah 선형보간 조건부 사건상한 1.23437461610498315e-31m^-3, 양끝 스트레스 시나리오 [1.11744008417127528e-31,1.35610902897027718e-31] m^-3.
- Kim 경험식을 **동일 지원영역으로 제한**한 결과 1.25356210324239099e-31m^-3, 비율 Shah/Kim 0.9846936286. 이는 원래 전체 Kim 상한과 직접 비교하면 안 된다.
- 측정 14.6 eV에서 Kim 근사식은 Shah 원데이터보다 7.821446% 높다.
- Shah 실측 지원영역 아래의 H 2차 이온화를 0으로 둔 것이 아니므로, 전체 사건 상한/관측 이온화율이라고 주장 불가.

## Scope/claim gate

derived / numerically checked / implementation-verified (conditional model); independent-author R06/C09 NOT_RUN. CENTRAL 28/88 (+0), EXTENSION 0/3 (+0), PHYS13 auxiliary 1/1 REVIEW_HOLD; PHYSICAL_K/HE_EXCLUSIVE/COMMON_EVOLVING_NEUTRAL_AND_RADIATION/STopping UNBOUND, production HOLD. No merge, no force-push, no automatic next node.
