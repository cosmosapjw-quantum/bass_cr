# C23B: 실제 PW19 공개 스펙트럼에서 primary 전자 공급으로

## 결과와 채택 범위

Taira, Kopenhafer, O’Shea의 2025년 공개 릴리스에 포함된 PW19 spectrum 세 개를 새 외부 공급원으로 구현했다. 원 Cloudy 형식과 CSV가 함께 있는 **z=2.316, 2.479, 2.649**에서 H I, He I, He II의 primary 광이온화 전자 분포를 계산했다. 새 실행은 9 cases와 양의 구적 원자 32,592개를 생성했다. gas ODE와 기존 campaign 재실행은 각각 0이다.

실행은 `runs/c23b_pw19_spectral_source_20261023_v1`에 있다. `photoelectron_atoms.csv`의 각 행은 `(redshift, channel, kinetic_eV, number_weight_per_target_s)`이고 **정지 target의 bath frame, 흡수 target 하나당 proper second** 정규화다. 실제 gas source에서는 각 absorber의 population 또는 proper number density를 곱한다. 비열적 electron의 thermal 편입, secondary cascade 또는 cosmological ODE는 이 표의 계산에 포함하지 않았다.

`spectral_photo_source.py`가 source identity와 원자 입력을 검사한다. 3개 redshift 사이의 보간, 범위 밖 extrapolation, 다른 isotope·분자에 대한 묵시적 재사용은 허용하지 않는다. `global_error_bound=null`이다. 새 결과는 C23A의 arXiv1801.04931v1 D1 moment table과 **별도 identity**를 가진다.

## 원자료와 재사용

원 데이터 릴리스는 [DOI10.5281/zenodo.15367103](https://doi.org/10.5281/zenodo.15367103), v1.0.0이다. [원 저장소](https://github.com/tairaeli/Metagalactic_Ultraviolet_Background_Data_Tables/tree/863c3b7fa73a8510fbf57ee7b75ad1e8c34086de)의 commit은 `863c3b7fa73a8510fbf57ee7b75ad1e8c34086de`다. 원 논문은 [arXiv2505.23544v1](https://arxiv.org/html/2505.23544v1), DOI10.3847/2515-5172/adddae다. 이 릴리스 자체를 source로 사용하며 원 Puchwein/CUBA 내부 출력과 byte-identical이라는 주장은 하지 않는다.

실제 ZIP은 8,388,585 bytes, SHA256 `afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55`이며 Zenodo가 광고한 MD5 `2c8790767866ca446d13660043224d67`와 일치했다. ZIP 824 members의 CRC를 모두 검사했다. PW19의 51 CSV, paired original-format 3개, README·변환 코드 등 선택 57개를 추출해 실제 Git blob SHA1/size와 모두 대조했다. 이 검사는 데이터 배송의 identity 근거다. 물리적 정확도의 보편적 인증으로 쓰지 않는다. Zenodo 메타데이터는 이 릴리스에 CC0를 명시한다.

원자 단면적은 [Verner 공식 원자료](https://www.pa.uky.edu/~verner/photo.html)의 [photo.dat](https://www.pa.uky.edu/~verner/dima/photo/photo.dat)를 실제 회수했다. 17,760 bytes, SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`다. 논문의 식(1)은 [Verner et al.1996](https://arxiv.org/pdf/astro-ph/9601009)에 있다.

| Channel | Z,N | 채택 threshold χ/eV | 채택 photon upper/eV |
|---|---:|---:|---:|
| H I | 1,1 | 13.60 | 50,000 |
| He I | 2,2 | 24.59 | 50,000 |
| He II | 2,1 | 54.42 | 50,000 |

이 값은 Verner 표에서 읽은 **이번 모형의 atomic convention**이다. C23A D1 표의 미확인 수치 threshold를 복원한 것으로 쓰지 않는다. ground-state 원자/이온 fit이며 isotope shift, molecular final states, target thermal velocity 및 recoil은 별도 의무다. 작은 recoil을 버리는 이번 근사에서는 photon 초과에너지 전부를 한 primary electron에 준다.

## 1. 데이터 열의 의미와 에너지 장부

릴리스의 `I (erg/s/cm**2)`라는 열 이름만 보면 bin integral로 읽기 쉽다. 실제 `make_UVB_data_table.py`는

\[
 S(\epsilon)=4\pi\nu J_\nu,\qquad \epsilon=h\nu
\]

를 생성한다. 따라서 이는 **d ln ε당 spectral energy intensity**이고 bin별 에너지 적분값이 아니다. 등방장의 angle-integrated scalar intensity로서 순방향의 net energy flux와도 구별한다. photon 에너지를 eV 수치 ε로 쓰고 ε₀=1.602176634×10⁻¹² erg/eV라 하면

\[
 \frac{d\Phi_\gamma}{d\epsilon}=\frac{S(\epsilon)}{\epsilon_0\epsilon^2}
 \quad[\mathrm{cm^{-2}\,s^{-1}\,eV^{-1}}].
\]

그 결과 absorber i 하나당 전자 source는

\[
 q_i(K)=\frac{S(K+\chi_i)\sigma_i(K+\chi_i)}
                 {\epsilon_0(K+\chi_i)^2},\qquad K\ge0.
\]

이 식은 isotropic radiation, atom at rest in the bath frame, single ground-state ionization, zero-recoil excess-energy mapping에 대한 식이다. c는 intensity와 photon number density 관계 nν=4πJν/(chν)에서 충돌률 cnνσ와 곱해져 소거된다. h=2πℏ와 eV의 변환은 위 ε₀와 source 정의에 추적된다.

하나의 동일 finite atomic domain에서

\[
 \Gamma_i=\int q_i(K)dK,\quad
 H_{e,i}=\int Kq_i(K)dK,\quad
 B_i=\chi_i\Gamma_i,\quad
 A_i=\int(K+\chi_i)q_i(K)dK=B_i+H_{e,i}.
\]

Hₑ는 **primary electron kinetic supply**다. 이를 gas heat에 먼저 더하고 cascade의 heat를 다시 더하지 않는다. prescribed external radiation 모형은 Aᵢ를 외부 imported energy로 기록하고, transported internal photon 모형은 같은 absorption을 photon reservoir에서 차감한다. 두 소유권을 동시에 적용하지 않는다. target i→i⁺와 electron+1의 charge/nucleus bookkeeping은 이 사건수를 공통으로 사용한다. 실제 반응 network의 charge-state mapping은 상위 구현에서 명시해야 한다.

원형 3×626개 행의 재형식화 대조에서는 릴리스 변환 코드가 사용한 Ryd-to-eV=13.605703976, legacy unyt eV-to-erg=1.602176562×10⁻¹², h=6.62606957×10⁻²⁷ erg s를 그대로 사용했다. 이 숫자로 CSV를 재구성한 최대 상대차는 4.45×10⁻¹⁶이다. 현재 SI 상수를 과거 변환에 덮어쓰지 않았다. source의 E,S 수치는 릴리스 그대로 고정하고, 새 event/energy 단위 변환은 코드의 ε₀로 명시했다.

이 수치 재구성은 사용된 단위 변환 계수와의 일치 근거다. 원 릴리스를 생성한 unyt의 정확한 설치 버전은 알려지지 않았다.

## 2. 양의 유한 구적 표현과 경계

626개의 양의 source nodes 사이에서 log S를 log ε에 대해 선형으로 보간한다. 이것은 이번에 선언한 연속 표현이며 source 원 저자의 미공개 보간기를 복원한 것이 아니다. 원 atomic threshold, 원 spectrum nodes, 전자 K=10 및 9937.21 eV 경계에서 모두 구간을 나눈다.

각 구간의 x=ln ε에서

\[
 d\Gamma_i=\frac{S(\epsilon)\sigma_i(\epsilon)}{\epsilon_0\epsilon}dx
\]

를 양의 Gauss–Legendre16 weights로 적분한다. 저장된 atoms는 이 유한 구적 측도다. 구적 count와 first energy moment를 독립적으로 합산하며, 저장 후 임의 정규화를 적용하지 않는다. 이산 source의 소비자는 그 weights를 원 분포의 정확한 delta spectrum과 구별하고 source quadrature identity를 유지한다.

상위 source spectrum은 약0.0107349eV–49.9735MeV를 덮지만, 현재 atomic fit은 photon50keV까지 채택했다. 50keV 위의 **radiation photon scalar flux와 energy flux**는 source에서 따로 적분해 저장했고, 그 구간의 absorption event rate와 electron yield는 null이다. atomic range 밖을 0으로 대신하지 않았다. 반대로 지원 atomic domain 안에서 K<10eV, 10≤K≤9937.21eV, K>9937.21eV의 electron count와 energy는 모두 실제로 계산해 별도 장부에 남겼다.

## 3. 실제 새 실행 결과

`c23b_pw19_spectral_source_20261023_v1`은 CPU3 worker, CPU6 coordinator, native thread1, 현재 quota/memory 관찰 및 cooperative lease를 사용했다. worker wall2.4517s, CPU2.3984s, peak RSS74,336KiB이고 own lease를 해제했다. source identity는 `277d49a9d48c94f6abf4f28fdef9e3be1d352fbb737a2edaed8ad46f1c260955`다. 정확한 명령은 `python3 run_spectral_source.py --run-id <fresh-id>`다. 동일 완료 결과를 복원할 때 재실행하지 않는다.

| 검사 | 실제 최대차 | 사전 기준 | 결과 |
|---|---:|---:|---|
| 3 original-format spectra→CSV | 4.45×10⁻¹⁶ 상대 | 2×10⁻¹³ | PASS_SCOPED |
| Verner 식(1), mpmath80 | 5.68×10⁻¹⁵ 상대 | 2×10⁻¹⁴ | PASS_SCOPED |
| Gauss8→16 | 5.24×10⁻¹⁶ 상대 | 2×10⁻¹¹ | PASS_SCOPED |
| Gauss16 vs independent photon-E adaptive quad | 3.17×10⁻¹⁵ 상대 | 2×10⁻¹¹ | PASS_SCOPED |
| B+Hₑ=A | 1.72×10⁻¹⁶ 상대 | 2×10⁻¹⁴ | PASS_SCOPED |
| 양의 electron atoms | 32,592개 | 모두 K≥0,w>0 | PASS_SCOPED |
| invalid/unsupported inputs | 15개 거부 | 최소10개 | PASS_SCOPED |

이 차이는 지정된 finite representation의 계산 비교다. spectral sampling error, atomic fit 물리 오차, isotope/recoil 오차 또는 실제 우주의 공급 불확실성을 합친 전역 오차상계가 아니다.

독립 C9 검토에서 `Verner96`의 공개 dataclass 생성자로 임의 계수를 넣거나 `replace`로 바꾸면 type 검사만 통과할 수 있는 입력 경계 문제가 발견됐다. 실제9cases는 모두 hash 검증을 거친 `from_table`을 사용해 영향이 없다. 실행된13개 source/input files를 `history/v1`에 원 bytes로 고정한 뒤, 생성자와 sigma/source/quadrature 소비 경로에서 모든 coefficients가 공식3rows와 정확히 같은지 검사하도록 교정했다. 원 수식·구적·저장 atom bytes는 바꾸지 않았다.

교정 후 `c23b_atomic_provider_guard_20261023_v2`는 새51개의 targeted checks만 수행해 PASS했다. 수동 생성·replace·NaN/bool 계수 및 object-level 변조 뒤 소비 모두 거부했다. worker CPU0.00663s, wall0.00663s, CPU3/native1이며9개 완료 spectral cases는 재실행하지 않았다. guarded code SHA256은 `71b7e3a6b6f1c68ec15bcb19b98014bc025ef595f53df29703f11e25f36f4a8d`, 새 guard execution identity는 `bed0b482329d34397e1709c34b155533a353d1f418c979e538bc1baac4ecc0bc`다. 기존 v1의 `below_threshold_physical_zero` 검사명은 역사로 보존하고 새 기록은 **source_fit_threshold_zero**로 표기한다. 채택된 반올림 fit threshold 아래의 zero와 정확한 isotope의 물리 threshold를 구별한다.

대표 z=2.479의 결과는 다음과 같다. 수치는 target 하나당 rate이며 전체 gas에 대한 합산 전이다.

| Channel | Γ/s⁻¹ | 평균 primary K/eV | K<10eV kinetic fraction | 10..9937.21eV fraction | 그 위, atomic 범위내 |
|---|---:|---:|---:|---:|---:|
| H I | 1.1871043741×10⁻¹² | 3.73701137 | 0.669184174 | 0.330815825 | 9.55×10⁻¹⁰ |
| He I | 5.9179469512×10⁻¹³ | 7.07386341 | 0.406654309 | 0.593345659 | 3.18×10⁻⁸ |
| He II | 7.1300911290×10⁻¹⁵ | 19.96943547 | 0.094289610 | 0.905709531 | 8.59×10⁻⁷ |

특히 H I primary electron의 kinetic energy 약66.9%가 FS 표의10eV 아래에 있다. 이 부분을 표 밖이라고 지우면 source energy의 큰 부분을 잃는다. 현재 공급 단계는 그 에너지를 unresolved nonthermal electron 장부에 보존한다. 실제 thermalization 시간과 다른 채널을 채택한 뒤 gas heat로 이동시킨다.

## 4. 별도 identity 비교와 실제 외부 데이터 이상

C23A D1의 59-node rate table을 원 bytes로 읽어 기존 log(rate)–log(1+z) convention으로 비교했다. 이번 spectral Γ/D1 Γ는 H I에서1.003–1.032, He I에서1.028–1.059, He II에서1.211–1.643이다. 특히 He II 차이가 커서 같은 ensemble 또는 교환 가능한 source로 합치지 않는다. `D1_SEPARATE_IDENTITY_COMPARISON.json`은 model·release·threshold·보간 차이가 함께 있는 진단값이며 원인을 하나로 단정하지 않는다. C23A 결과를 변경하지 않았다.

원 릴리스 z=0 CSV의626 intensity 값은 약3.7656×10¹⁹–3.7689×10¹⁹에 밀집해 있다. H threshold 부근에서 z=0.04912의 동일 에너지 값에 대한 비는4.15869×10²⁵다. 해당 z0 original-format 파일은 이 릴리스에 포함되지 않아 변환 원인을 확인할 수 없다. `SOURCE_ANOMALY.json`은 이를 **QUARANTINED_UNRESOLVED_CAUSE**로 기록하고 원 bytes를 보존한다. smoothing, normalization, 이웃 redshift 복사 또는 제거를 수행하지 않았다. 세 admitted nodes만 사용하는 provider는 이 행을 읽지 않는다.

## 5. FS2010 조성 및 채택 의무

[FS2010 원 논문](https://arxiv.org/abs/0910.4410)의 §3과 원 `elec_interp.c`는 xᵢ=n_HII/n_H, 동일한 HeII fraction, HeIII=0이라는 표의 조성 조건을 준다. §2의 neutral-fraction 표기와 §3의 정의가 혼동될 수 있지만 실제 interpolation argument `xHII_call`, 표의 배경 header 및 §3의 정의를 함께 연결했다. **숫자 He/H abundance는 현재 읽은 원 논문과 배포 interpolation code에 명시되지 않았다.** 다른 연구가 사용한Y=0.24 또는 임의 primordial number ratio를 이 표의 실제 생성 입력으로 대체하지 않았다. C23A에서 기록한 low-xᵢ header/C-axis 충돌과 closure defects는 그대로 유지한다.

따라서 이번 새 source의 in-FS-energy-domain 부분은 source 지원 구간을 뜻한다. FS cascade를 실제21-population gas에 적용하기 위해서는 He/H와 ionized fractions, zero-HeIII 조건, 밀도/Coulomb logarithm, finite stopping, photon reabsorption 및 isotope mapping을 별도로 충족해야 한다. FS의 sub10.2eV heat 규칙을 즉시 시간0 gas heating으로 채택한 실행은 하지 않았다.

## 다음 합류점과 네 축

- **EXECUTION**: 새 spectral9 cases, 원형/단위/구적/원자식검사 완료. ODE0, 역사계산 재실행0. 양의 저장 atoms와 finite-domain ledger 제공.
- **PUBLICATION**: parent C23B integration으로 이관. 이 agent의 remote write0.
- **BACKUP**: local packet 준비; 실제 archive/provider ACK는 parent delivery 기록이 권위다.
- **DAG**: source-spectrum·threshold·정규화의 세 노드 scoped완료 → independent C9 → source-frame/response consumer → 조성·시간·원자 반응 coverage 계약 → 실제 coupled thermal/radiation. FS helium ratio, P19D1 threshold identity, isotope/molecular final state 및 >50keV absorption inputs는 각각 OPEN.

전체 Non-tilted LRS stress convention과 별도 nonbaryonic Vlasov matter stress는 바뀌지 않는다. 이 packet이 general tilted/triaxial/polarized CMB 또는 full nuclear/thermal/stellar network를 구현한 것으로 쓰지 않는다.
