# bass_cr CR-PHYS02A 물리 연구 루프

작성일: 2026-10-10 (KST). 기준: PHYS01 branch의 commit
`e41e18873af438ef989ff44f505fe2665118fdec`.

## 결과

**양성자 충돌에서 직접 생성된 0.1–10 eV 전자의 인과적 Coulomb 감속 성분을
유도하고 실제로 계산했다.** 원 source의 full-spectrum normalization을 유지하고,
초기 양성자 분포의 증가에 따른 `Q_e(W,t)=t A(W)`를 사용했다. 317년 시점의
열 전달률은 이 구간을 즉시 열로 바꾸는 terminal proxy의 22.0765%였다.
누적 주입 에너지의 15.5763%가 stopping을 통해 고정 bath에 전달되었고,
83.8894%는 추적 중인 전자의 kinetic energy, 0.5343%는 cutoff 잔량이다.

이는 **고정된 가스에 대한 classical leading-log Coulomb-only 모형의 조건부
결과**이다. 전체 cascade, 가스 열화, evolving IGM 또는 물리 정확도 인증은 아니다.
독립 최종 판정은 `review/INDEPENDENT_DECISION.json`을 기준으로 한다.
상위 `CR-PHYS02-DELAY`와 production history는 아직 완료되지 않았다.

## 1. 이번 루프에서 선택한 문제

최신 저장소에는 두 별도 경로가 있다. R17B2B는 CR_OFF의 FT03 photon source
homotopy 문제이고, PHYS01은 실제 proton source/transport → H/He ionization →
terminal electron yields → local REI receiver이다. 이번 작업은 후자의 DAG에
명시된 PHYS02-DELAY를 이어갔다. R17B2B와 원 정밀 atomic gate는 변경하지 않았다.

FS10 표에는 최종 ionization/excitation/heat yields가 있지만 time response가 없다.
실제로 FS10 §6.1은 instantaneous-deposition approximation을 전제로 하고,
빠르게 변하는 국소 환경에는 주의가 필요하다고 설명한다. 표의 normalization을
확인하는 것만으로 finite-time result를 얻을 수 없다는 점을 직접 증명했다.

\[
Y_c(W)=\int_0^\infty k_c(a,W)da,\qquad
P_c(t)=\int dW\int_0^tQ_e(W,t-a)k_c(a,W)da.
\]

동일한 terminal Y_c를 주는 `k(a)→λ k(λa)` 변환은 평균 지연을 1/λ배 바꾼다.
따라서 arbitrary exponential lag나 terminal fractions만으로 시간 지연을
추정하지 않았다. 재현 가능한 전체 유도는 `research/DERIVATION_KO.md`에 있다.

## 2. 고정된 물리 조건과 새 근사

| 항목 | 조건 |
|---|---:|
| source snapshot | z=8; PHYS01의 Leite17/MD14 정규화 |
| source 전체 proton 구간 | 10 keV–1 PeV |
| 실제 impact-ionization 구간 | 1–4 MeV; H/He neutral targets |
| proper n_H, n_He | 140, 11.5425532 m^-3 |
| 이온 분율 | x_HII=x_HeII=0.01, x_HeIII=0 |
| proper electron density | 1.51542553 m^-3 |
| prescribed bath | T=100 K |
| elapsed source time | 10^10 s = 316.880878 yr |
| 실제 계산한 직접 생성 전자 | 0.1–10 eV |
| 추적 하한 | 0.1 eV; 남은 에너지는 별도 보존 |

원 Bianchi 배경은 H=3.3×10^-17 s^-1, s=3.3×10^-18 s^-1이다. 새 시간응답은
HΔt≪1의 leading local approximation에서 계산했다. 기존 정확한 Bianchi
proton source와 세 시점의 계수를 비교한 최대 상대 차이는 6.93×10^-7이었다.
이는 표본 수치 비교이며 연속구간 인증이 아니다. 실제 시간에 따라 변하는 가스,
전자 각도 수송 또는 self-consistent Bianchi electron history를 계산한 것은 아니다.

이 구간의 전자는 hydrogen excitation 문턱보다 낮으므로 본 H/He ground-state
closure에서 새 atomic excitation/ionization을 열지 않는다. 단, neutral elastic
energy transfer, electron-ion exchange, Fokker–Planck energy diffusion 및
near-thermal matching은 포함하지 않았다. 고정 bath에 전달한 stopping energy를
heat로 계상하는 국소 모델이다.

## 3. 감속 시간과 실제 시간 의존성

Khrapak (2020), Eq. (6)의 classical superthermal stopping cutoff를 채택했다.
SI 물리 에너지 ℰ에 대해

\[
-\dot{\mathcal E}
=\frac{4\pi\kappa^2 n_e}{m_ev}\ln\frac{v\mathcal E}{\kappa\omega_p},
\quad
\kappa=\frac{e^2}{4\pi\epsilon_0},\quad
\omega_p=\sqrt{\frac{n_ee^2}{\epsilon_0m_e}}.
\]

| 생성 전자 에너지 | 국소 E/b | 0.1 eV까지의 적분 감속 시간 |
|---:|---:|---:|
| 1 eV | 92.01 yr | 61.30 yr |
| 3 eV | 452.74 yr | 309.95 yr |
| 10 eV | 2,603.86 yr | 1,789.99 yr |

`E/b`와 실제 구간 적분시간은 같은 양이 아니다. 또한 3 eV 전자의 감속 시간이
317년보다 조금 짧아도, 317년 내내 생성된 전자가 모두 그 나이를 갖는 것은 아니다.
초기 proton population이 0이므로 `Q_e∝t`이고, 아직 소멸을 고려하지 않은 생성
전자 ensemble의 평균 age는 t/3이다. 이 birth-time 분포를 응답 적분에 넣었다.

위 수치의 오차는 numerical quadrature error와 물리 모형 오차를 구분해야 한다.
10 eV에서 고전적/양자적 길이비 κ/(ℏv)≈1.17은 큰 scale separation이 아니며,
0.1 eV에서도 E/(k_B T)≈11.6이다. cutoff 도달을 열평형 완료로 부르지 않았다.
FS10의 E>13.7 eV 식을 저에너지에 외삽하지 않았으며, 독립 문헌 검토를 기록했다.

## 4. 실제 source와 합성한 정량 결과

| 316.880878 yr 시점의 양 | 값 |
|---|---:|
| 선택 구간의 terminal heat proxy | 1.09406629×10^-43 J m^-3 s^-1 |
| 인과적 stopping heat power | 2.41531063×10^-44 J m^-3 s^-1 |
| 현재 power / terminal proxy | **0.220764561** |
| 선택 구간의 누적 electron injection | 5.47033143×10^-34 J m^-3 |
| 누적 stopping heat | 8.52077400×10^-35 J m^-3 |
| active electron kinetic storage | 4.58902564×10^-34 J m^-3 |
| cutoff residual kinetic storage | 2.92283935×10^-36 J m^-3 |
| 현재 cutoff residual energy flux | 7.70093707×10^-46 J m^-3 s^-1 |

실제 계산은 다음 보존 관계를 충족한다.

\[
U_{e,\rm injected}=H_{\rm stop}+U_{e,\rm active}+U_{e,\rm cutoff}.
\]

선택한 0.1–10 eV 성분은 **직접 생성된 전체 secondary kinetic energy의
4.46752%**를 차지한다. 여기서 전체란 active 1–4 MeV 양성자 impact가 내놓는
전자 스펙트럼의 전체이며, 10 keV–1 PeV CR 주입 에너지 전체와는 다르다.
더 높은 에너지 전자가 cascade 도중 이 구간으로 내려오는 추가 source도 미포함이다.

이 성분의 terminal proxy와 causal stopping power의 차이는 PHYS01의 전체
terminal heat 숫자의 약 **7.05%에 해당하는 크기**이다. 이는 규모 비교이며
전체 heat의 실제 지연 억제율이나 엄밀한 하한이 아니다. W>10 eV의 시간 kernel과
cutoff 이후의 열화가 아직 없으므로 전체 CR heat power는 이번 결과로 채우지 않는다.

에너지별 직접 생성 kinetic input 분율은 다음과 같다.

| 전자 에너지 구간 | 분율 |
|---|---:|
| <0.1 eV | 0.00110% |
| 0.1–1 eV | 0.09750% |
| 1–3 eV | 0.61900% |
| 3–10 eV | 3.75102% |
| 10–100 eV | 28.72366% |
| 100–1000 eV | 42.34583% |
| ≥1000 eV, 각 proton endpoint까지 | 24.46189% |

이 결과는 다음 구현의 우선순위도 정한다. 나머지 직접 입력의 가장 큰 구간은
100–1000 eV이며, 10–1000 eV를 합하면 약71.07%다. 따라서 다음 물리 루프는
이 구간의 ionization/excitation branching과 시간 clock을 확보하고, 본 저에너지
module로 내려오는 flux를 연결하는 데 집중하는 것이 타당하다.

## 5. 검증과 근거의 수준

신규 검산은 9개 항목에서 PASS_SCOPED였다. 실제 Python 실행은 exit 0이며,
종료 코드와 stdout/stderr, 코드 SHA-256 및 버전은 evidence에 남겼다.
원 PHYS01의 변경 없는 전체 suite는 재실행하지 않았다.

| 검사 | 최대 상대 차이 또는 결과 |
|---|---:|
| Ei 감속 시계 vs adaptive 에너지 적분 | 1.61×10^-14 |
| energy-coordinate 응답 vs 직접 forward ODE | 1.32×10^-13 |
| 분리한 source 계수 vs 직접 SDCS 적분 | 3.53×10^-16 |
| 64→96 quadrature 비교 | 1.24×10^-12 |
| selected energy ledger | 7.85×10^-16 |
| local ramp vs exact Bianchi source 표본 | 6.93×10^-7 |
| zero/OFF, 잘못된 입력 거절, spectral partition | 통과 |

Ei primitive와 ODE는 별도의 수치 경로지만 동일한 physical closure와 상수를
공유한다. 이 일치는 구현·수치 검산이며 원 모형의 물리오차 인증이 아니다.
독립 문헌 감사는 후보 생성과 별도로 수행했고, 최종 decision review도 별도
검토자가 수행하도록 분리했다. 실제 판정 파일을 확인한 뒤 status를 확정한다.

## 6. 상태와 다음 work unit

이번 산출물은 PHYS02의 **인과적 저에너지 하위 성분**이다. `PHYS02-DELAY`
전체 및 `PHYS05-RECEIVER`, `PHYS06-HISTORY`는 자동 승격되지 않는다.

다음 `CR-PHYS02B`는 10–1000 eV electron-impact H/He ionization/excitation의
absolute collision rates와 branching을 고정하여 시간 generator를 만들고,
0.1–10 eV로 내려가는 flux를 본 모듈에 연결한다. FS10 terminal limit와의 비교는
같은 조성·채널·threshold 계약에서 수행하고, helium excitation에서 나온
ionizing photons는 재흡수 전의 에너지/number reservoir로 별도 추적한다.

`CR-PHYS03-COMPOSITION`과 `CR-PHYS04-LOSSES`는 기존 병렬 과제로 유지한다.
전체 receiver를 만들 때에는 새 ionization에 의해 생성된 free electron과
thermal pressure에 참여하는 electron을 구분해야 한다. 생성된 전자를 곧바로
모두 thermal count에 넣는 terminal contract를 delayed system에 재사용하지 않는다.

## 재현과 근거 파일

- 유도: `research/DERIVATION_KO.md`
- 실제 입력·허용범위: `state/SCIENTIFIC_CONTRACT.json`
- 계산 구현: `src/causal_subthreshold.py`
- 실행: `python tests/verify_causal.py`
- 원 숫자·모든 검사: `evidence/NUMERICAL_RESULT.json`
- source identity: `inputs/PARENT_SOURCE_MANIFEST.json`
- 원문 검토: `research/literature/SOURCE_AUDIT.md`
- 최종 독립 판정: `review/INDEPENDENT_DECISION.json`
- 후속 지시: `START_CODEX_HANDOFF_KO.md`, `DAG.json`

## 주요 원문

- Furlanetto & Stoever (2010), *Secondary ionization and heating by fast electrons*,
  §§2–6, arXiv:0910.4410v1: https://arxiv.org/html/0910.4410v1
- Khrapak (2020), *Reduction of the Coulomb logarithm due to electron-neutral collisions*,
  pp.1–3, Eq.(6), arXiv:2006.00128v1: https://arxiv.org/pdf/2006.00128
- 기준 PHYS01: https://github.com/cosmosapjw-quantum/bass_cr/pull/24
