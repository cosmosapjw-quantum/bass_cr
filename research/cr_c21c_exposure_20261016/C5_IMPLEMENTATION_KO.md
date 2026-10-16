# C21C C5 구현 완료: exposure-aware native-rate dual seam

- 원본 parent PR76 `172ca4c814b0b5bb05a03b509086e85f9cdd6138`의 photo-only `exact_pair`를 **수정하지 않고** 독립적인 `exact_pair_exposure`를 구현했다.
- `src/exposure_contract.py`는 공통 minority branch, `expm1/log1p` 안정화, 정확한 photon·absorber exposure 및 native 두 rate 표현을 반환한다. 실제 native Rust는 호출하지 않았다.
- `NativeRateBridge`의 `gamma_exposure_s/heat_exposure_erg_abs_s`는 **physical-time** 통합 exposure를 입력받는 반면, `gamma_endpoint_s/heat_endpoint_erg_abs_s`는 원본 C19처럼 endpoint-BE 사건 수지를 강제한다. 이들은 반드시 독립된 이름으로 유지한다.
- 종료 absorber=0 이면서 사건>0이면 `HOLD_ENDPOINT_RATE_UNREPRESENTABLE`, 조건수 exposure/(dt*endpoint)>1e6은 `HOLD_ENDPOINT_ILL_CONDITIONED`로 출력한다. 이는 구현 진단 임계일 뿐 사용자 locked 과학 정확도 tolerance 변경이 아니다.
- photon/heat input은 사건/H와 erg/(absorber s), event/cm³/s를 총 H 핵 밀도로 연결한다. 환원되지 않은 physical exposure 없이 Strang operator pseudo-time exposure를 임의로 합산하지 않는다.
- `src/radau_exposure_oracle.py`는 독립 SciPy Radau에서 원본 Verner 계수, total-H density, FLRW clock, MD14 emission clock, 두 source-birth 시각과 3개 스펙트럼 양의 manufactured support에 대해 실제 absorber exposure ∫A dt를 계산한다. 원본 50k stellar spectrum 전체가 아닌 지정한 3-energy conditional source다. 원본 RR/CI/DR/CMB/Case-A native 소스는 미구현.
- `src/compare_c21b.py`는 저장된 C21B PR76 원본과 independently solved Radau를 시간 구간/threshold로 정렬해서 비교한다. 원본 C21B 소스가 저장소 내 sibling으로 존재하면 그대로 불러온다. ZIP standalone의 경우 `vendor/pr76`에 SHA256 `8cca6193747287c5fae84ce58f9249684ba258a8e38869e4626ff402336a29f4`인 정확한 기존 소스를 포함하여 복구·재검산한다.
- 구현 단위의 한계: photo-only evolving gas, 고정 처방 FLRW 및 positive impulse births; 실제 동적 native Grackle EOS/cooling, recombination/escape, full EoR, angular anisotropy에는 적용하지 않는다.

다음: C6/C7의 다양한 stiffness·zero absorber·source-birth·true-Verner threshold tests 및 C8의 2→128 step independent convergence를 실시한다.
