# H/He CR 전자 에너지 침적 provider 선정

작성일 2026-10-10. 실행 모델 식별은 `UNKNOWN`; 사용자 지정 GPT-6 Astra research v4.0.0의 START_HERE, PROJECT_INSTRUCTIONS, 상태 템플릿을 실제 읽었다. 이 문서는 source/data 선택 및 물리 계약이며 전체 IGM 계산의 성공 판정이 아니다. 실제로 확보한 수치표, 코드, hash와 원전의 적용범위를 연결한다.

## 결정

**일차 선택은 Furlanetto–Stoever 2010(FS10)의 실제 공개 전자 침적표다.** 연구팀 공식 사이트의 `elec_interp.tar`를 확보했고, 같은 수치가 MIT 21cmFAST 저장소에도 배포됨을 파일 단위로 대조했다. 14개 이온화 상태마다 258개 에너지 값, 10–9937.21 eV 범위를 제공한다. H I, He I, He II 이온화의 사건 수와 Lyα photon 수가 각각 있어, MEDEA의 단일 He 에너지채널보다 현재 H/He 이온망 연결에 적합하다. 파일 첫 열의 이름은 `Photon Energy`지만 공식 배포 설명·C API·논문의 계산 대상은 **주입 전자의 운동에너지**다. X-ray 예제는 이 전자 kernel의 한 사용 예다.[S1,S2,D1]

오늘 허용할 가장 작은 과학 계산은 **자료표와 일치하는 고정 조성에서 proton→secondary-electron SDCS와 이 kernel을 합성하는 조건부 선형 응답**이다. CR proton source 자체, 전자 생성 단면적, proton 정지/수송 연산자는 별도의 입력이다. 이 표를 확보했다는 이유만으로 Leite proton source의 10 keV–1 PeV 전 영역이 처리되었다고 선언하지 않는다.

우선 `xHII=xHeII=0.001, 0.01, 0.1`, `xHeIII=0`의 원본 조성 knot를 사용한다. 여기서 xHeII는 `nHeII/nHe`이다. 세 상태 모두 header와 C 입력이 일치하고 전자분율은 `ne/nH=xHII+(nHe/nH)xHeII`다. 이는 HM12 등에서 실제로 독립 진화하는 H/He 상태를 같은 상태로 덮어쓰라는 뜻이 아니다. 현재 상태가 manifold 밖이면 명시적으로 거부하고, 별도 frozen-composition 비교 시나리오로만 산출한다.

## 취득한 바이트와 권리 범위

| 자료 | 실제 상태 | 재사용·배포 근거 | 선정 |
|---|---|---|---|
| FS10 공식 tar | 310,272 bytes, SHA256 `e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101` | 공식 공개 다운로드이나 tar 자체 LICENSE 없음 | 원저자 provenance |
| FS10 표의 21cmFAST 배포본 | commit `c01373543fb83a721c48cdcbcd0a08ea53afe78c`; 14개 table 및 관련 C, MIT notice 확보 | 저장소 MIT 배포, 원 tar와 terminal newline를 제외한 동일성 대조 | 재사용 패키지의 pinned 배포본 |
| DarkHistory MEDEA 8표 | commit `7a09f1991b0028cf00ec386bdea81b963f78794f`; 8표+Python+LICENSE 합계 19,723 bytes, 모든 Git blob 확인 | DarkHistory MIT, 별도 원 MEDEA dataset license는 발견하지 못함 | 독립 비교 및 대체 후보 |
| DarkHistory electron upgrade | branch `lowengelec_upgrade`, commit `b556d0f0418a0665719fd6da26dcc303466b9659`; 관련 Python 실제 읽음 | MIT repo의 코드; 외부 h5는 별도 취득 필요 | 조성 확장 후속 lane |
| CRIME | 원 논문 실제 읽음 | 공개 web interface라는 사실은 source-code license가 아님 | 현재 atomic H/He kernel로 미선정 |

공개 접근과 재배포 license를 동일시하지 않는다. FS10 원 tar에 license가 없다는 사실은 보존하며, 구현 배포에는 MIT 21cmFAST snapshot의 notice와 FS10 인용을 함께 유지한다. MIT mirror가 원저자의 독립적인 data license 문서를 대신 제공한다고 주장하지 않는다. exact hash는 `FS10_ACQUISITION.json`, `DARKHISTORY_ACQUISITION.json`을 따른다. 이것은 코드·자료의 identity 근거이며 과학적 검증을 대신하지 않는다.

## FS10의 구체적 loader 계약

표 열은 `E_eV, f_ion, f_heat, f_exc, n_Lya, n_ion_HI, n_ion_HeI, n_ion_HeII, legacy_Shull_heat`다. 첫 3개 f는 에너지분율이고 n 열은 **주입전자 1개당 평균 사건 수**다. n 합을 1로 정규화하지 않는다. `legacy_Shull_heat`는 비교용이며 실측표 f_heat와 혼합하지 않는다. Lyα는 excitation의 부분집합이므로 `f_exc + 10.2 n_Lya/E`를 더하면 중복이다. 전체 excitation을 모두 열로 넣지 않는다.

FS10 원전의 입력 manifold는 H/He의 동일한 1차 이온화분율과 초기 HeIII=0이다. 정적 가스에서 전자 cascade와 helium 재방출 광자의 흡수를 이미 처리한 terminal yield다. 따라서 초기 proton impact에 따른 이온화는 따로 세되, 이 표 안에서 재흡수된 helium photons를 전체 radiation equation에 새 source로 다시 넣지 않는다. 표 header의 z=10, T=100 K를 보존하되 이를 임의 T/z 격자로 해석하지 않는다. 저밀도 근사, electron cooling 시간, inverse-Compton 상대손실은 사용하려는 배경에서 별도로 확인해야 한다.[S2]

실제 배포에서 발견한 차이는 수정해 숨기지 않는다.

1. C의 xi=2.318×10^(-4,-3,-2)와 table header가 가리키는 2.138×10^(-4,-3,-2)가 불일치한다. 세 knot의 물리적 좌표를 임의로 고르지 않고 quarantine한다.
2. xi=10^-4 파일의 HeII header=0.001은 HeI=0.9999와 합이 1이 아니므로 이 metadata도 quarantine한다. 위 세 clean fixed-knot 시나리오는 이 행을 쓰지 않는다.
3. 원 C의 upper-end clipping과 범위 밖 보정은 새 물리 API에 자동 승계하지 않는다. 에너지/조성 밖에서는 `OUT_OF_DOMAIN`을 반환한다. 유한 에너지 구간 밖의 양전자·전자 tail은 0으로 치환하지 않고 별도 미해결 에너지로 기록한다.
4. 수치 kernel은 source 행들을 보존한다. E 보간이 필요하면 우선 인접 에너지의 **yield-energy vector** `(E f_heat, E f_ion, E f_exc, n_Lya, n_HI, n_HeI, n_HeII)`를 linear-E convex 보간한다. 두 끝점의 에너지 원장이 보존되며 positivity도 보존된다. 이는 새 adapter의 명시적 근사이지 원 Monte Carlo 재실행이 아니다.
5. HI/HeI/HeII 문턱을 가로지르는 interval에서는 positive endpoint를 하위 문턱 아래로 퍼뜨리지 않는다. 가장 작은 구현은 그 interval을 거부하고 실제 source knot 계산을 허용하는 것이다. 문턱 anchor를 새로 넣는다면 별도 근사·오차 항으로 기록한다.
6. xi 보간을 나중에 추가할 때 clean knot들만 사용하고 어떤 원 knot를 제외했는지 출력한다. 오늘의 fixed-knot 계산은 xi 보간의 provenance 모호성을 피한다.

## Proton bridge에 들어가는 물리량

다음 식은 이 문서의 결합 유도이며, FS10이 proton을 수송했다는 주장이 아니다. 국소 정지계에서 `G_p(K,Ω,t)`를 단위 물리부피·운동에너지·입체각당 proton 수, `dσ_pj/dE`를 target j에서 생기는 전자의 에너지 미분단면적이라 두면

\[
 S_e(E,t)=\sum_j n_j\int dK\,d\Omega\,v_p(K)G_p(K,\Omega,t)
 {d\sigma_{pj}(K,E)\over dE}.
\]

`S_e`의 단위는 volume^-1 time^-1 energy^-1이다. FS10 사건 yield `Y_j(E,xi)`와 heat fraction h를 통해

\[
 R_j^{sec}=\int_{D_e}dE\,S_eY_j,
 \quad Q_{heat}^{sec}=\int_{D_e}dE\,S_e E h,
 \quad \dot n_\alpha^{sec}=\int_{D_e}dE\,S_eY_\alpha.
\]

따라서 HII 수 변화에는 `R_HI`, HeII 변화에는 `R_HeI-R_HeII`, HeIII 변화에는 `R_HeII`가 들어간다. free-electron source는 세 이온화 사건 수의 합이다. 이 secondary 계산은 **primary proton collision의 최초 결합에너지 비용**을 포함하지 않는다. 단일이온화 원장에서는

\[
 Q_{p,ion}=\sum_j n_j\int dK\,d\Omega\,v_pG_p
 \int dE\,(I_j+E){d\sigma_{pj}\over dE}
\]

의 `I_j`는 primary event, `E`만 electron kernel에 넘긴다. proton Coulomb heat, excitation, charge exchange, nuclear inelastic channel을 이 식에 섞어 동일 손실을 두 번 빼지 않는다. SDCS convention에 leading electron/secondary electron 수의 중복이 없는지도 공급자가 보증해야 한다.

FS10 하한보다 낮은 secondary 에너지는 별도 `subthreshold_heat` 원장에 기록할 수 있지만, 이는 원전의 Coulomb-only terminal closure와 냉각시간 조건을 채택했을 때만 유효하다. 상한 초과 tail에 대해서는 `Q_unresolved=∫outside E S_e dE`를 남긴다. 전자가 모두 admitted domain 안에 있거나 이 tail의 외부 cooling provider가 연결될 때만 전체 에너지 완료 판정을 한다.

## Axisymmetric Bianchi I 적용

metric은 `ds²=-c²dt²+a_perp²(dx²+dy²)+a_parallel²dz²`; 정상관측자의 국소 tetrad에서 충돌 kernel을 정의한다. gas 자체가 isotropic이고 target이 unpolarized인 가정 아래 scalar deposition fraction에 별도 shear 곱을 도입하지 않는다. 비등방성은 `G_p`, secondary source의 에너지·각도 분포, density history, 전자의 수송/냉각 경쟁에 들어간다.

조건부 local-terminal approximation에는 `max(|H_perp|,|H_parallel|) t_cool <<1`, 조성 변화시간보다 짧은 냉각, 공간 cell을 쓸 경우 충분히 짧은 정지거리, 포함하지 않은 ICS 손실의 작은 비중이 필요하다. scalar heat/ionization 총량은 등방 target에 대한 angle-integrated kernel로 얻을 수 있지만, 방향별 radiation field나 escape에는 이 scalar table만으로 충분하지 않다. FS10의 fixed composition에서 얻은 결과는 Bianchi I의 전체 nonlinear H/He evolution 성공이 아니라, 해당 closure의 CR 응답 측정이다.

## 대안 비교에서 얻은 실질적 수정

DarkHistory MEDEA 8표는 26개 xHII knot와 5개 에너지분율을 갖는다. 실제 header는 heat, Lyα, H ionization, He ionization, continuum 순서다. `compute_fs`의 반환 permutation은 continuum-first이며 첫 설명과 일치하나 Returns 절의 heat-first 설명과는 불일치한다. 새 loader는 열 이름으로 읽어 이 모호성을 없앤다. 1e-4 floor는 exact-zero channel을 양수로 만들므로 승계하지 않는다. 실제 표의 positivity와 208행 에너지합은 검사했고 최대 합잔차는 2×10^-6이다.[D2]

2019 DarkHistory 설명은 sub-3 keV MEDEA interpolation과 H/He 비슷한 이온화 상태의 한계를 명시한다. 2023 upgrade는 Monte Carlo He channel noise와 14 eV 결과의 차이, 6개의 원 에너지 knot라는 제약을 논의한다. 이 정보는 MEDEA 독립비교의 이유이지 자료가 모두 쓸모없다는 결론이 아니다. `yp024` 파일명의 정확한 조성 metadata는 원 MEDEA의 YHe=.248과 동일하다고 강제하지 않는다.[S3,S4,S5]

upgrade 코드의 `get_elec_cooling_tf(eleceng, photeng, rs, xHII, xHeII, ...)`는 xHeII를 **nHeII/nH**로 받고 H/He 분율을 독립적으로 넣는다. 다만 현재 코드에는 HeIII 입력이 없고 내부 electron temperature에 LCDM 근사를 쓰며 기본 ICS와 excitation 계산은 외부 h5에 의존한다. 따라서 자유로운 HeIII/T 및 anisotropic radiation까지 해결하는 drop-in provider라는 승격은 하지 않는다. 후속 lane의 명확한 출발점은 이 MIT 코드와 표준 cooling equation이다.[D3]

CRIME 원 논문은 proton/electron SDCS와 secondary-electron source의 결합을 보여 주지만, 실제 소개된 loss closure는 H2 환경이다. 논문의 free web interface와 CC-BY-NC-SA 문서 license를 atomic H/He 실행코드 license로 오인하지 않는다. 현재 선택은 H2를 H/He로 대체한 재명명이 아니다.[S6]

## 실제 adapter와 냉각시간 후속 검증

`src/fs10.py`에 고정 xi=.01 loader를 구현했다. 실제 취득파일 SHA256을 검사하며, 현재 구현의 이차 이온화 문턱은 선언된 근사값 `[13.6,24.6,54.4] eV`다. 원 Monte Carlo의 정확한 상수를 복원했다는 주장은 하지 않는다. 사건수 기반 에너지와 원 fion 열은 분리한다.

원표 xi=.01의 `fion+fheat+fexc-1` 최대값은 3.2×10^-5, 선언한 문턱을 이용한 count 기반 에너지 결함은 9.525291×10^-5 E다. 각 f의 출력자리 반올림만으로 이를 모두 설명할 수 없다. 따라서 interpolation probe 전에 고정한 `10^-4 E` bound 아래에서만 heat를 닫는 **bounded numerical closure projection**을 사용했다. 전체 f의 재정규화는 하지 않는다. `event_energy_residual_eV`, `source_projection_correction_eV`, `threshold_interpolation_correction_eV`를 각각 출력한다. 문턱 아래 양의 사건수가 퍼지지 않도록 zero anchor를 삽입하며, 10.2 eV 아래 excitation/Lyα를 차단하는 별도 유한격자 규칙을 기록했다. 이 threshold 보정은 source rounding bound로 위장하지 않는다.

258개 원 knot와 문턱 부근을 포함한 2,265점에서 닫힌 에너지 잔차는 최대 1.82×10^-12 eV였고 HI/HeI/HeII 문턱 아래 사건수는 0이었다. 범위 밖 입력과 허용하지 않은 xi를 거부한다. 이는 adapter 검증이며 전자 cascade의 독립적인 재계산이 아니다. `FS10_LOADER_VALIDATION.json`이 실제 실행결과다.

`electron_loss_timescale_estimate`는 FS10 Eqs.8–10의 1 keV 부근 Coulomb/HI 손실 추정을 제공한다. z=10, xi=.01에서 두 atomic rate의 harmonic estimate는 E=100 eV에서 약 5.97 kyr, 1 keV에서 0.189 Myr, 9.94 keV에서 5.91 Myr다. 이것은 순간 E/b 추정이지 threshold 및 helium photon 재흡수까지 포함한 cascade 지연시간 상한이 아니다. 따라서 10^10 s의 새 source가 즉시 terminal yields를 냈다고 해석하면 안 된다. 10^14 s도 최고에너지 tail의 충분한 완화시간을 보증하지 않는다. 현재 허용 결과는 **충분히 오래 존재한 reservoir의 quasistatic terminal-deposition rate**이고, causal turn-on 결과가 아니다. 최고에너지에서 atomic/ICS 시간비도 약 .087이므로 전체 9.94 keV 범위를 ICS 무시 오차 1%라고 선언하지 않는다. 낮은 전자에너지 대역에 대해 이 비율과 적분에너지 weight를 따로 검증해야 한다.

`FS10_THRESHOLD_AUDIT.json`은 source 내부 문턱 진단을 남긴다. 전체표의 수치추론 후보 `[13.598,24.586,54.392]`는 원 생성 코드에서 읽은 값이 아니며, 공식 photon 예제 상수와도 완전히 같지 않다. 또 원표 생성의 정확한 helium abundance는 `null`이다. 예제의 H/He 수비중 `.92/.08`을 실제 table-generation abundance라고 승격하지 않는다. 결과는 source-defined primordial mixture를 사용하는 조건부 kernel이며 정밀 YHe 비교는 별도 소속이다.

## 완료·남은 작업

자료 취득과 FS10 우선 선정, 재사용 경로, 조성/에너지 domain, proton bridge 원장, MEDEA 데이터 감사 및 실제 FS10 adapter 구현까지 완료했다. 독립 agent는 실제 `src/fs10.py`를 읽고 20개 검사와 10,274개 off-grid probe를 수행하여 `PASS_DECLARED_FINITE_ADAPTER`로 판정했다. 최대 닫힌 에너지 잔차는 1.82×10^-12 eV이며 source heat projection은 고정 bound를 만족했다. `FS10_INDEPENDENT_REVIEW.json`이 해당 코드 hash와 범위를 기록한다. 이 판정은 전체 물리 Monte Carlo, cascade 지연시간 또는 진화하는 IGM의 검증이 아니다. source provider와 proton SDCS를 개발하는 상위 작업은 이 계약을 소비할 수 있다.

당장 얻을 수 있는 과학량은 clean fixed composition마다 `(primary ionizations, secondary HI/HeI/HeII yields, Lyα yield, heat, unresolved tail)`의 proton-spectrum 의존성이다. 이것은 CR을 끄거나 photon source로 교체한 계산이 아니다. 실제 evolving IGM으로의 승격은 조성 manifold 이탈, 냉각시간, admitted electron tail 및 에너지 원장을 확인한 이후다. 최종 승격은 독립 reviewer가 결정한다.

## 원전·코드 포인터

- S1 공식 공개 배포: https://cosmicdawn.astro.ucla.edu/codes_and_tools.html ; tar https://cosmicdawn.astro.ucla.edu/elec_interp.tar
- S2 Furlanetto & Stoever, MNRAS 404, 1869 (2010): https://arxiv.org/pdf/0910.4410 ; 읽은 범위 §2, §6.1–6.3, §7 및 note 6.
- S3 Liu, Ridgway & Slatyer, DarkHistory: https://arxiv.org/html/1904.09296v1 ; §III.4, §III.6.2, Eq.45.
- S4 Sun & Slatyer electron upgrade: https://arxiv.org/pdf/2303.07366 ; §II.A–C, Fig.1, Appendix 비교.
- S5 Valdés, Evoli & Ferrara: https://arxiv.org/pdf/0911.1125 ; §2.1.
- S6 Krause, Morlino & Gabici, PoS(ICRC2015)518: https://s3.cern.ch/inspire-prod-files-2/2dbcc1af795ec577cd1ac937fc2b3dd8 ; abstract, §2, 특히 Eq.2.19–2.22.
- D1 https://github.com/21cmfast/21cmFAST/tree/c01373543fb83a721c48cdcbcd0a08ea53afe78c/src/py21cmfast/_data/x_int_tables ; `FS10_ACQUISITION.json`.
- D2 https://github.com/hongwanliu/DarkHistory/tree/7a09f1991b0028cf00ec386bdea81b963f78794f/darkhistory/low_energy ; `DARKHISTORY_ACQUISITION.json`, `TABLE_AUDIT.json`.
- D3 https://github.com/hongwanliu/DarkHistory/blob/b556d0f0418a0665719fd6da26dcc303466b9659/darkhistory/electrons/elec_cooling.py ; `DARKHISTORY_UPGRADE_INSPECTION.json`.
