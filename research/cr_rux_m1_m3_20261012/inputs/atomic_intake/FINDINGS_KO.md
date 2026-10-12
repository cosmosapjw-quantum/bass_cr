# bass_cr 원자물리 재사용: 선택적 source intake

기준은 `cosmosapjw-quantum/bass_cr@767273fec673ac0877dc4833da4bef147ae04c40`이다. 이 문서는 DAG 설계 협력의 source intake이며 독립 승격 심사 결과가 아니다. 저장소 파일을 변경하지 않았고 기존 scientific 계산·suite를 실행하지 않았다. 원문·blob ID·파일 SHA256·source URL은 `SOURCE_INVENTORY.json`, 기계판독 결과는 `CR_ATOMIC_REUSE_FINDINGS.json`에 있다. 기존 보고서의 PASS는 당시의 고유 범위에서 보존하며 새 검증으로 표기하지 않는다.

## 바로 사용할 수 있는 baseline 흡수·가열

`docs/fastest_track_resume_20261007_v1/CR_F0_IGM_PHOTON_BRIDGE_KO.md`와 `research/fastest_rejoin_20261007/cr_off_igm_bridge.rs`는 실제 함수의 단위와 사건 소유권을 제공한다. gas-rest frame에서 proper nH,nHe[cm^-3], 에너지[eV], 이미 에너지·각도 적분된 p_j[photons/H]를 받는다.

- Gamma_a = c nH sum_j p_j sigma_aj [s^-1].
- heat_a = c nH (eV→erg) sum_j p_j sigma_aj (E_j-chi_a) [erg/absorber/s].
- R_a = n_abs,a Gamma_a [cm^-3/s].
- dp_j/dt = -c p_j sum_a n_abs,a sigma_aj [photons/H/s].

추가 4pi,dE,a^-3,dt를 곱하지 않는다. AtomicProvider는 cross section의 fit domain을, 기존 상수 owner는 binding threshold를 제공한다. 광자 손실과 이온화·열은 동일 사건으로 결속된다. `igm_point_rhs`가 chemistry, variable-particle EOS, CMB 및 photoheat를 처리하므로 소비자가 열을 다시 더하지 않는다. Source injection, redshift, stage 및 dt는 caller 소유다. 코드 61–64,75–87,97–125행에서 정의가 직접 확인된다.

기존 보고서는 scoped native photon-IGM CR-OFF bridge PASS를 기록한다. 이것은 point 함수와 별도 실행 capsule의 검증이며, 현재 전체 REI에 대한 owner adoption이나 physical history 완료를 뜻하지 않는다. CR OFF에서는 해당 provider load/callback을 호출하지 않지만 AtomicProvider 함수까지 무호출인 것은 아니다. CR ON을 zero fill로 대신하지 않는다.

## Point·시간 오차·물리 성분의 서로 다른 범위

| 원문 | 재사용할 결과 | claim ceiling |
|---|---|---|
| fastest_rejoin_20261008/full_point_source/RETURN.json | 실제 native full RHS의 24 matched pairs, photo/nonphoto 분해 | continuous flow와 propagated error OPEN; future temperature sign 아님 |
| cr_r16b_20261009/R16B_REPORT_KO.md | FT03 fixed-birth variant0, 32cell/6birth, proper [0,1.25e9]s의 조건부 signed tau 시간오차 | 기존 FT03 원 모형만; 새로운 Grackle-subset IGM 또는 physical EoR에 이전하지 않음 |
| cr_r17b2_20261010/BASS_CR_NCP_R17B2_RETURN_KO.md | full-coupled backend와 공통 value tube | NO_CERTIFIED_SOURCE_SHARPENING; 높은 birth derivative/jump tube 부재 |
| cr_phys01_20261010/REPORT_KO.md 및 CR_PACKET.json | 실제 SN proton→H/He ionization→FS10 cascade→native derivative의 비영 성분 | 고정 상태의 조건부 terminal component; delay 미승인, coupled solver interval=0 |

첨부 S15의 182panel/5824point 원본은 이번 선택적 Git intake에서 열지 않았다. 그러므로 그 payload의 새 identity 확인이나 wide error PASS를 주장하지 않는다. 이미 확보된 위 point operator와 좁은 FT03 시간 인증은 서로 독립적으로 소비할 수 있다.

## 실제 hard-particle provider는 존재한다

PHYS01은 `CONDITIONAL_PHYSICAL_COMPONENT_AVAILABLE`이다. nH=140m^-3,nHe=11.542553191489361m^-3, xHII=xHeII=.01,xHeIII=0,T=100K,H=3.3e-17s^-1,s=3.3e-18s^-1, age=1e10s에서 1–4MeV proton ionization-loss 성분을 계산했다. 전체 proton injection은 10keV–1PeV에서 정규화했으며 active window로 재정규화하지 않는다.

사건율 단위는 m^-3s^-1, power는 Jm^-3s^-1이다. `modelled_ionization_loss_power`=3.2670019626760045e-42와 `full_injection_power`=5.315371751092545e-34는 서로 다른 양이다. receiver external_power에는 전자가 포함된 모델 손실 성분만 들어간다. heat=1.2093044641845817e-42, ionization=1.3963750685843803e-42, excitation_escape=6.613224299070425e-43은 저장된 packet 값이다. 이번에 재계산한 값이 아니다.

Primary binding은 한 번만 기록하고 cascade에는 secondary electron kinetic energy만 넣는다. FS10 내부에서 처리한 helium excitation photon을 다시 ionizing source로 넣지 않는다. 원 table의 정확한 helium abundance 및 z8←z10 transplantation 근사가 남아 있으며, heat closure projection은 물리적 오차 상계가 아니다. 물리 source가 아예 없다는 HOLD로 되돌아갈 이유는 없지만, 이 고정 terminal packet을 변화하는 가스·임의 xi·인과적 EoR history에 바로 쓸 수 있다는 결론도 아니다.

## PHYS01과 PHYS02/M0의 연결 경계

PHYS01/PHYS02A/PHYS02B manifest는 다음 동일한 source 파일 SHA를 기록한다.

- injection.py: `c5eda0e60302339af1bbdd0603ae1cd8a8921d9e6489c22d954e0bc92968c27d`.
- rudd.py: `757e4c8b33618ad6ef88f422919fe813654454c836f0942cf9792be133e8eac2`.

Source 계보는 공유하지만 반응 연산자는 다르다. PHYS02A는 Np≈t qp의 선두국소 근사를 사용하여 Qe(W,t)=t A(W), 전자0.1–10eV의 causal Coulomb stopping을 계산한다. PHYS02B는 동일 prescribed bath에서 전자0.1–900eV와 두 birth tag로 확장하고 반복 HI/HeI 충돌·n2..4 excitation·Coulomb drift를 추적한다. HeII electron-impact, gas feedback 및 photon branching/reabsorption은 제외한다. PHYS02A 계약은 one-point terminal REI packet의 delayed receiver 재사용을 명시적으로 금지한다.

M0 직접 입력은 cached response SHA `60747f9d...f3b7b`, 원 F 기록 SHA `dfdca59c...f6f5`이다. 원래 H0 normalization과 selected_record/birth_defined 구분을 유지하는 고정 causal kernel의 endpoint response다. PHYS01의 FS10 terminal heat에 M0의 p를 곱해 delayed heating이라고 하는 것은 입력 에너지 창·electron spectrum·atomic operator·source history·normalization의 동일성을 확보하지 못한 변환이다. 현재 필요한 작업은 새로운 원자정밀 campaign이 아니라 이 소비 계약의 명시적 결속이다.

## overlay에 반영할 결정

RUX03에는 기존 baseline photon-IGM 모듈의 단위·사건 계약을 바로 공급한다. RUX13의 준비 입력에는 실제 PHYS01 provider와 조건부 packet을 추가한다. Native provider 부재라고 쓰지 않는다. CR hard-process 필요성은 source/domain 선정 시 판정하고, 실제 ON/OFF history sensitivity는 compatible physical history가 생긴 뒤 수행한다. 기존 FT03 인증과 M0 완료를 재개방하지 않는다. 이 intake 자체가 global RUX00/RUX03/RUX13 등을 실행하거나 PASS시킨 것은 아니다.
