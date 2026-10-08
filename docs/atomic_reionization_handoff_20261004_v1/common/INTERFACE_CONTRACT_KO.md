# 공통 원자 입력과 재이온화 소비자 계약 v1

상태: 정의·회계·작업 인터페이스 동결. 과학 입력의 전 영역 정확도나 실제 재이온화 결과를 인증한 문서가 아니다. 적용 범위는 비경사 물질, 국소 비상대론적 Maxwell 기체, unpolarized scalar H/He, 처방된 Bianchi I 배경이다. 원자 공급자는 국소 정지계의 단면적/반응률을 제공하고, 우주론 기하와 광자 분포의 진화는 rei_bianchi가 소유한다. metric (-,+,+,+); c, h=2πħ, k_B 유지.

## 1. 단일 인터페이스와 책임

공급자 레코드는 provider_id, process_id, species/상태, observable_kind, 원 출처·version·hash, units, frame, particle_distribution, domain, rate convention, branch/floor, uncertainty, energy/photon closure, implementation_status와consumer_admission을 포함한다. 실패는 구조화된 status로 반환하며 범위 밖 extrapolation·미정 에너지 항을 숫자 0으로 대체하지 않는다.

- `CrossSection(E_cm_eV) -> sigma_cm2`: 동일 과정·초기/최종 상태에 대한 면적. total과momentum-transfer, RCT와NRCT는 서로 다른 process_id다.
- `ThermalRate(T_K) -> k_cm3_s`: 국소 Maxwell 평균. 비열적/beam 분포에는 적분 전 단면적과 분포 계약이 필요하다.
- `PhotoRate(s, photon_field) -> Gamma_s_inv_s`: rei가 계산. 계수 공급자는 sigma_s(E)를 반환한다.
- `CoolingCoefficient(T_K, closure_id) -> coefficient`: 각 값의 단위와 밀도 prefactor를 레코드에 명시한다. 숫자만 반환하는 무단위인터페이스는 금지한다.
- `SourceTerm(state, provider_set, closure_id) -> species_dot, Q_thermal, Q_binding, Q_photon`: 소비자 소유. coefficient family와 closure_id를 결과에 남긴다.

공통 schema는 interface 요구사항이며 existing producer API를 반드시 재작성하라는 뜻이 아니다. 예를 들어 BASS_HE의 B3 export를 adapter로 매핑한다. 공개코드를 copy/FFI/기준실행 중 어느 방식으로 쓰더라도 원식·branch·밀도정규화는 보존한다.

## 2. 화학량론과 단위

종 순서 y=(HI,HII,HeI,HeII,HeIII,e,Hminus). 마지막 Hminus는 확장 설명용이고 기본 6종 network에 몰래 포함하지 않는다. H nuclei 벡터 h=(1,1,0,0,0,0,1), He nuclei a=(0,0,1,1,1,0,0), charge q=(0,1,0,1,2,-1,-1). 모든 반응의 순변화 v는 h·v=a·v=q·v=0이다. 자유전자 항 v_e는 전하중성 조건으로 파생되며 charge-conserving CX라고 해서 전자가 생성되는 것은 아니다.

- HI ionization: v=(-1,+1,0,0,0,+1,0). photon/electron/neutral-H impact는 동일 v이지만 서로 다른 rate와에너지 출처다.
- HeI ionization: v=(0,0,-1,+1,0,+1,0); HeII ionization: v=(0,0,0,-1,+1,+1,0).
- HeIII+HI RCT/NRCT: v=(-1,+1,0,+1,-1,0,0). 직접 자유전자 증분 0; 이후 방출광자 흡수는 별도 사건이다.
- resonant HII+HI CX: 단일 population의 총종 v=0. fast/thermal 분해에서는 운동량/에너지 교환이 남는다.
- 2HI -> HII+Hminus: v=(-2,+1,0,0,0,0,+1). 직접 free-electron 증분 0; Hminus망 없이이온화항으로대체하지않는다.

두 종의 event density는 k*n_A*n_B [cm^-3 s^-1]. Grackle k57의 source convention은 k57*n_HI^2이며 추가 1/2를 붙이지 않는다. 이것은 일반 identical-particle 단면적 규약을 부정하는 말이 아니라 이 coefficient의 이미 정의된 정규화다. photoevent는 Gamma_s*n_s [cm^-3 s^-1]. eV->erg 변환은 1.602176634e-12 erg/eV.

## 3. 복사·결합에너지·열

국소 photon number density N_nu(Ω)[cm^-3 Hz^-1 sr^-1]를 사용할 때 Gamma_s=c∫dΩ dnu N_nu sigma_s. primary-only photoheat는 Q_s=c*n_s∫N_nu sigma_s(hnu-chi_s)dnu dΩ, threshold work는 chi_s*n_s*Gamma_s다. 흡수광자 에너지와 threshold+photoelectron heat가 같아야 한다. Secondary deposition을 켜면 동일 초과에너지를 heating과 secondary ionization에 각각 전액 넣지 않는다.

중성원자를 화학에너지0으로 두면 U_bind=chi_H*n_HII+chi_HeI*n_HeII+(chi_HeI+chi_HeII)*n_HeIII. HeIII+HI->HeII+HII에서 ΔU_bind=chi_H-chi_HeII≈-40.8eV/event. 에너지 보존은 Q_heat+Q_emitted+ΔU_bind=0이며 정확한 photon spectrum/kinetic distribution은 scalar k(T)만으로 결정되지 않는다. 40.8eV monochromatic photon 또는 전액 heat를 자동 선택하지 않는다. RCT energy owner가 닫히지 않은 provider는 coupled thermal/radiation simulation에 물리 채택되지 않는다.

u_th=3*n_part*k_B*T/2, p_th=2*u_th/3. 비경사 팽창에서 dot(u_th)+Theta*(u_th+p_th)=Q-Lambda, Theta=3H -> expansion=-5H*u_th. specific e=u_th/rho의 팽창항과 혼동하지 않는다. Compton/CMB 교환, cosmological expansion, recombination electron cooling, binding-energy photons는 owner가 각각 하나다.

## 4. opacity·closure 충돌 해결

기존 Rust의 lowgroup_log_opacity 기반 effective opacity와 R1의 homogeneous bound-free kappa=Σn_s sigma_s는 별도의 모델이다. 기존 함수를 재정의하거나 양쪽 HI opacity를 더하지 않는다. 신규 물리계산은 명시적 `HOMOGENEOUS_BOUND_FREE_R1` closure ID를 소비하며 과거 effective-MFP 경로는 회귀/기존모형 lane으로 보존한다.

Case A+explicit/escape radiation 또는 coupled H/He OTS는 closure에 따라 선택한다. 종별 alpha_B 호출만으로 mixed-species recombination-photon ownership이 완성되지는 않는다. baselineprimary-only는 MICRO0 근사이며 UV에서도 secondary가 생길 수 있다. physical comparison은 이 근사에 조건부라고 명시한다.

## 5. uncertainty와 모델 비교

수치상계, source fit residual, 원자모형 spread, 소비자 observable sensitivity는 서로 다른 ledger다. rigorous_physical_bound가 없는 자료는 null로 두되 계산을 무조건 차단하지 않는다. 실제 허용 claim은 해당 근사와 감도 검증으로 결정한다. 같은 입력을 쓰는 두 구현의 일치는 수치 parity이지 독립적인 원자 물리 검증이 아니다.

Bianchi–FLRW 차이 ΔO(p)=O_B(p)-O_F(p)에 같은 rate choice/perturbation p를 사용한다. 개별 원자율의 불확실성이 ΔO보다 작아야 한다는 요구도, 공통오차가 항상 상쇄된다는 가정도 하지 않는다. time/angular/spectral refinement와 paired rate-family 결과로 구분한다.

## 6. 이번 갱신에서 고정한 결정

1. 새 physics baseline은 기존 Rust 함수를 유지한 별도 R1 adapter로 연결한다.
2. CR은 first baseline에서 off. HH/He 선택 채널은 source/domain/energy 검사가 닫힐 때 켠다.
3. BASS_HE existing B3 GM25/W82=1.70e-13와KF96=1e-14는 source-named alternative다. 겹치는 1000–10000K에서17배차이; 두 값을 평균하거나 confidence interval로 부르지 않는다. 범위밖 clamping 금지.
4. 기존 원자 lane은 회수 가능한 별도 연구이며 first scientific history의 선행조건이 아니다.
5. 자료 source/domain/observable가달라진 경우만 해당 task를 재개한다. 전수문헌조사/전체과거감사를 반복하지 않는다.
