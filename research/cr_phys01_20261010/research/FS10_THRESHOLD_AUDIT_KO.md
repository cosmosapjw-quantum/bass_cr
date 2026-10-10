> 후속 선택 반영: 이 문서는 원자료/후보 단계의 기록이다. 최종 provider는 `DEPOSITION_PROVIDER_SELECTION_KO.md`와 `src/fs10.py`의 FS10 xi=.01, E≤9937.21 eV를 채택했다. MEDEA 3000 eV 제한은 채택 모델이 아니며, raw-data 무보정 감사와 최종 명시적 bounded numerical heat-closure projection을 구별한다.

# FS2010 이온화 문턱·에너지 회계 및 He 풍부도 추가 감사

2026-10-10 UTC. Loader와 원자료를 수정하지 않았다. 재현 스크립트 `FS10_THRESHOLD_AUDIT.py`, 전체 결과 `FS10_THRESHOLD_AUDIT.json`.

## 즉시 필요한 결정

현재 `.01` 표에서 보고된 count 기반 에너지 closure `9.525291×10^-5`는 재현된다. `13.6,24.6,54.4 eV`라는 반올림 문턱을 사용하면 표의 내부 에너지 회계와 차이가 난다. 더 정밀한 현대 원자값을 넣는 것만으로 원자료의 문턱을 복원했다고 할 수 없다. **원표 f_ion 에너지와 종별 ionization counts를 서로 다른 검증량으로 유지**하고 그 차이를 provenance가 있는 잔차로 기록한다. 임의 renormalization이나 heat 보정으로 잔차를 제거하지 않는다.

| 사용한 χ_HI, χ_HeI, χ_HeII (eV) | xi=.01 count 기반 총 에너지 closure 최대 잔차 | 증거 수준 |
|---|---:|---|
| 13.6, 24.6, 54.4 | 9.5252912304×10^-5 | 통상 반올림 비교값 |
| 13.5984, 24.5874, 54.4178 | 4.2690254280×10^-5 | 현대값 비교 후보; FS 원 생성 코드의 값으로 확인되지 않음 |
| 13.58, 24.586, 54.398 | 3.4866222766×10^-4 | 공식 `xray_interp.c`의 Eion 배열 |
| 13.598, 24.586, 54.392 | 3.2305152565×10^-5 | 표로부터 추론한 후보; 원 생성 상수의 직접 증거 아님 |

원표의 `fion+fheat+fexc−1` 최대 잔차는 3.2×10^-5이다. 마지막 후보에서 count-derived fion과 원 fion 차이의 최대는 1.541469×10^-6이다. 이를 validation 진단으로 쓸 수 있지만, 원 threshold의 정확한 복원 선언에는 쓰지 않는다.

## 실제 출판 코드에서 확인된 상수

공식 tar: https://cosmicdawn.astro.ucla.edu/elec_interp.tar . `xray_interp.c`는 `Eion={13.58,24.586,54.398}`를 선언한다. 같은 파일의 광이온화 차단조건은 `13.6,24.586,54.4`이다. `elec_interp.c/.h` 자체는 이온화 수를 반환하며 전체 species energy 변환 상수를 정의하지 않는다. 따라서 예제의 서로 다른 숫자를 원래 Monte Carlo 표 생성 상수로 간주할 수 없다. tar에는 Monte Carlo 생성 코드가 없다.

3612개 행에서 `fion = Σ n_ion,s χ_s / E`를 최소제곱으로 맞추면 `13.598000995,24.585996731,54.392404348 eV`가 나온다. HeII 문턱은 이온화율이 높은 표가 더 잘 제약하며 `.9` 표만 사용하면 약54.392004 eV이다. 이 결과는 **13.598,24.586,4×13.598**을 사용하는 내부 회계의 강한 수치적 단서다. 이는 자료 기반 역추론이며 상수의 직접 인용이 아니다.

## 표시 정밀도만으로 완전한 복원이 가능한가

각 양수 token에 마지막 표기 자릿수의 ±1/2 단위를 허용하고 zero 채널은 정확한 zero로 둔 뒤, E·fion·counts를 모두 구간으로 처리했다. 이 구간에 공통 χ 세 개가 들어갈 수 있는지 양의 χ에 대한 선형부등식으로 검사했다. **전체 14개 표의 모든 행을 엄격하게 동시에 만족하는 해는 발견되지 않았다.** 다만 추가해야 하는 최소 fion slack은 **2.268233×10^-8**에 불과하므로 거의 양립한다. 이 결과를 큰 물리적 불일치로 확대 해석하지 않는다. 계산 feasibility tolerance는 10^-9이며, slack은 통계적 신뢰구간이 아니다. 정확한 생성 상수 인증과 수치적 근접성을 구분한다.

정확한 상수를 확인하려면 저자 Monte Carlo 생성 코드 또는 원본 정밀 출력이 필요하다. 오늘 사용하려면 원표 에너지 closure와 count-energy compatibility를 독립 gate로 두고, 사용하는 thresholds 및 residual을 결과에 함께 보존하는 것이 적절하다.

## He 풍부도: 확인된 것과 미확인인 것

원 논문은 primordial composition 및 Dunkley et al. 2009 cosmological parameters를 언급하지만, 검사한 공개 표/보간기에는 원 Monte Carlo 생성용 Y_He 숫자가 없다. `xray_interp.c`의 spectrum 예제에는 **HI_den=0.92, He_den=0.08**이라는 상대 number weight가 있다. 이로부터 He/H=0.08695652, 질량비4를 쓰면 Y_He=0.25806452를 계산할 수 있다. 그러나 이는 예제 광흡수 weighting이며 **표 생성 당시 abundance라는 보증은 없다**. 이 값을 .24 또는 .248로 치환하거나, 21cmFAST 현재 cosmology 값을 과거 FS 표에 소급 적용하지 않는다.

따라서 machine-readable 원표 abundance는 `null / NOT_EXPLICIT_IN_ARCHIVE_OR_INSPECTED_PAPER`로 유지한다. 주어진 composition manifold `xHII=xHeII`, `xHeIII=0`와 절대 helium abundance의 미확인은 별개의 조건이다. 정확한 Y_He를 요구하는 전체 IGM production gate에는 아직 증거 공백이 있다.
