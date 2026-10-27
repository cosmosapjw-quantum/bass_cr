# PHYS02 actual finite proper-time source — 선택 근거

## 선택과 물리적 의미

PHYS02의 실제 실행된 `Q_e(W,t)=t A(W)`를 **독립적인 density-space 주입 moment port**로 선택한다. 원 source revision은 `4ca5a90de79c8fb82a25fd9e83615bec0dfa870b`이며 현재 `D=ec463db0c7e5c7fb5070796071c926caa4db6445`에도 같은 원문과 기록이 있다. `NUMERICAL_RESULT.json`의 실제 bytes를 읽어 SHA256 `0b33ad9af1be50297e54fa8b38570471c35b5e342ce771d834bb576458a91500`, 75490 bytes를 확인했다. 동결 source 이력과 저장된 적분량을 사용하며 spectrum을 moments로 복원하지 않는다.

시계는 proper seconds, 부피는 proper m³, 유효 시간은 0≤t≤10¹⁰ s이다. 이력은 초기 nonthermal stock0에서 시작하는 leading-local `Np=t qp` 근사다. 10¹⁰ s 이후의 continuation 또는 shutoff는 주어지지 않았다. 기존 Bianchi 비교의 유한 표본 residual은 연속 오차 certificate가 아니다.

배경은 T=100 K, nH=140 m⁻³, YHe=.248, xHII=xHeII=.01, xHeIII=0이다. H/He source는 원래 elemental neutral atom이며 원 자료가 isotope-resolved이지 않다. H→H1, He→He4를 쓰려면 조건부 귀속을 명시한다. D/T/He3/Li나 여기상태로의 확대는 없다. 상대속도와 원자 target을 쓰는 local prescribed gas rest-frame scalar source이며 tilt/전자 각분포/반동 분포는 공급되지 않았다.

## 기존 실제 적분량

fullBED와 legacy의 source moments는 같은 값이다. 두 모형을 두 source로 합산하지 않는다.

| birth tag | Ekin 지원 [eV] | N(10¹⁰s) [m⁻³] | U(10¹⁰s) [J m⁻³] |
|---|---|---:|---:|
| direct_0p1_10 | .1–10 | 8.583703187582436e-16 | 5.47033142884169e-34 |
| direct_10_900 | 10–900 | 8.304211765519884e-16 | 8.459279749254517e-33 |
| selected_total | .1–900 | 1.6887914953102317e-15 | 9.006312892138684e-33 |

선형 이력이 독립적으로 알려져 있으므로 구간 [a,b]⊂[0,T]에는 `N_[a,b]=N_T(b²−a²)/T²`, `U_[a,b]=U_T(b²−a²)/T²`, 순간 주입에는 `dN/dt=2N_T t/T²`, `dU/dt=2U_T t/T²`를 쓸 수 있다. 이는 실제 history 법칙으로 저장 moments를 재표현한 식이다. 이 조사자는 새 수치 평가를 실행하지 않았다. 사용자 요청의 새 bounded 구현 단계에서 변경 계산만 수행하면 된다.

selected_total은 기존 FP64 합산 순서의 기록이므로 두 decimal band sum과 마지막 자리 차이를 보존한다. 원 source를 맞추려고 rescale하지 않는다. exact decimal 산술이 원 quadrature나 물리적 정확도를 높여주는 것은 아니다.

## 한 번만 적용할 인자

`q_p`는 전체 10 keV–1 PeV에서 정규화한 angle-integrated proper-volume rate다. 충돌에 사용한 1–4 MeV 구간을 전체 source power로 다시 정규화하지 않는다. 원 Rudd provider의 허용 proton 범위는 1–10 MeV이며 실제 소비 구간은 그 부분이다.

`z=8`의 proper-volume 변환729는 `q_p`에 이미 포함되어 있다. 각도는 이미 적분되어 추가4π를 붙이지 않는다. `.99*nH`와 `.99*nHe`도 `A(W)`에 이미 한 번 들어 있다. 저장된 `injected_energy_J_m3`는 이미 J이므로 다시 eV→J 변환하지 않는다. `A`의 단위는 m⁻³s⁻²eV⁻¹, `t A`의 단위는 m⁻³s⁻¹eV⁻¹이다. 두 birth 열은 같은 전체 selected-energy 분모를 사용한다.

## PR107/108과 연결하는 경계

PR107의 RR operator는 T=10000 K, nHeIII=.01 cm⁻³의 다른 frozen bath다. PHYS02 actual history를 그 operator에 직접 넣을 same-state/transport 증거가 없으므로 연결은 `GATED_SOURCE_RECIPIENT_STATE_MISMATCH`다. 실제 time history가 있다는 사실만으로 저장된 all-time RR reward에 유한시간 clock을 붙일 수 없다.

명시적 same-state donor/recipient `nb`는 현재 자료에 없으므로 `nb_m3/native25=null`을 유지한다. nH·YHe에서 수를 만들어 기존 CR bath의 nb로 공급하지 않는다. retained photon은 별도 port이며 공급되지 않은 photon 반환을 0 또는 heating으로 채우지 않는다.

새로 관찰된 PR108 `research/cr-rr-causal-clock-20261027`, HEAD `2776752de6952f60d8d690a128f33fec4df2c57b`는 C08/18of20에서 finite-age/bin RR를 수행 중이다. 그 범위는 declared pulse와 관측 clock이며 actual continuous injection history/nb는 null이다. 해당 작업과 예산을 보존하고 같은 solver를 실행하지 않는다.

## 원 배열 복원

원 NPZ는 pinned D Git tree에 있다. 재생성할 이유가 없다.

- `research/cr_phys02c_paired_9600_closeout_20261011/raw/THIRD_GRID_LOCAL_20261011_EXEC01/SPECTRUM_fullBED_9600.npz`: 217754 bytes, SHA256 `7ee8c1eff7f58cd7175a9bcd3968a27ef065f0e983f05e609dc875f5f06112cc`.
- 같은 디렉터리 `SPECTRUM_legacy_9600.npz`: 217716 bytes, SHA256 `a3f81dbbd86c1d0521f962db8a2ee2ed158f613f3f7a069caccbda9c964acda6`.

과거 raw array 근거는 source_vectors shape(9611,2), SHA256 `07dd0fa81154f5aecaf262b00c2adfada21ebc9b2a2dba59703e03e3f5dab609`; energy(9600,) SHA256 `6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292`이다. 부모가 pinned Git에서 NPZ를 복원한 뒤 이 조사자가 현재 실제 NPZ bytes·array metadata/hash를 읽어 위 값과 일치함을 확인했다. 배열의 물리적 합산·새 projection·solver 실행은 없었다. canonical HeIII ZIP에는 PHYS02 원 배열이 없다. 실제 복원은 새 파일에 pinned `git show`로 하고 size/SHA256을 확인하면 된다. 기본 shell lazy Git fetch는 browser-proxy 연결 실패였으며 이는 과학 runtime 실패가 아니다.

## 수행 범위

원문·실제 저장 JSON·실행 계보·현재 PR108를 읽었다. 과거 science replay0, source quadrature0, projection0, provider run0, 새 native simulation0이다. 중앙27/88, child count effect0, global physical completion/error/budget remaining null을 유지한다. 개인 대화 전체 검색 unavailable 및 Drive partial inventory 한계도 그대로다. 새 논문의 결과를 주장하는 조사가 아니므로 기존 원문 모델을 정규화 계약의 근거로 재사용하며, 새 근거가 필요한 수학·물리 주장은 부모 루프에서 SciSpace·Exa·primary source로 대조한다.

## 복원 뒤 확인한 discrete source 좌표

원 배열의 첫9600행은 number가 아니라 **energy 좌표**다. `b_i=source_vectors[i,tag]`, `E_i=energy_eV[i]`, `U*=physical_energy_scale_eV_m3`, `T=10¹⁰s`이면 number 주입계수는 `A_Ni=(U*/T²)b_i/E_i`, energy 주입계수는 `A_Ei=(U*/T²)b_i`다. 실제 순간 주입은 여기에 proper time t를 한 번 곱한다. 저장 source는 이미 finite count/energy-preserving projection을 거친 이산 근거이며 원 연속 spectrum과 구별한다. 그 이산 근거를 직접 소비하는 것은 moments에서 spectrum을 만드는 작업이 아니다.

추가11행의 순서는 heat9600, binding_HI9601, binding_HeI9602, excitation_HI9603, excitation_HeI9604, cutoff_energy9605, ionizations_HI9606, ionizations_HeI9607, cutoff_number9608, low_cross_energy9609, low_cross_number9610이다. 실제 source의 heat/binding/excitation/ionization 행은 모두0이다.

cutoff에는 low-tag `b_energy=4.579701473759296e-7`, `b_number=4.579701473759296e-6`가 별도 보존된다. 이 수와 에너지를 직접 읽는다. 원 cutoff는.1eV, active grid 첫점은.10309375000000001eV다.

**low_cross 행을 주입량에 더하면 중복이다.** high-tag low_cross_energy=2.785842106789342e-5, low_cross_number=2.785842106789342e-6은 high-born source가10eV 경계 active node로 projection된 부분의 진단 기록이다. 원 energy functional은 active energy와 첫6개 energy ledger만 합하며 cross ledger를 제외한다. 원 number functional은 active b/E+cutoff_number−ionization counters다. 부모의 새 코드도 이 소유권을 유지해야 한다.
