# PHYS11 | 원본 재결합 광전자 2차 이온화의 운동학적 상한

## 정의와 경계

공간 metric signature는 `(-,+,+,+)`이지만 본 계산은 오직 방출원 정지틀에서의 원자 사건/고유시각 문제다. PHYS10에 고정된 중성 기체 100 K, 원본 H I/He I 수밀도와 6,400 RR source photon 에너지 원자 및 시간 출생 bin을 그대로 유지한다. 수치 이온화 문턱은 PHYS07–10의 원본 코드 `I_H=13.60 eV`, `I_He=24.59 eV`; 참고 NIST He II 추가 문턱 `I_HeII=54.4177655282 eV`. 모든 문턱은 에너지 보존상의 **필요조건**이다. 원본 code source maximum `E_H,max=23.60 eV`, `E_He,max=34.59 eV` (실제 저장된 배열에서 검증). 전자 초기 운동에너지 `epsilon_a(E)=max(E-I_a,0)`.

관측 시각 T까지의 최초 광흡수 조건부 확률은 원본 PHYS09와 정확히 동일하게

`P_a(T|s,E) = k_a/k [1 - exp(-k(T-s))]`, where `k_a(E) = c n_a sigma_a(E)`, `k=Σ_a k_a` and P=0 for T<=s or k=0.

원본 광자 출생 확률 가중치 `w_{ij} [photon m^-3]`는 수정하지 않는다. 최초 광흡수가 일어났을 때 전자가 **추가로** 중성 H I를 한 번 이온화할 수 있는 운동학적 지원 함수는

`chi_{a->H}(E) = 1{E-I_a >= I_H}`.

추가 H I 이온화 사건수의 **기대 상한**은

`C_H(T) = Σ_{i,j,a} w_ij P_a(T|s_j,E_i) chi_{a->H}(E_i) [m^-3]`.

이것은 실제 충돌 전자에 대한 효과적 σ, free path, stopping, 중성 history, 열적 운동, 추가 복사나 외부장에서 유입되는 에너지를 포함하지 않으므로 **실제 이온화 사건수/률이 아니다**. 별도 전자 에너지 공급이 없고 표적은 source-frame 정지 원자로 근사한다. 실제 electron-impact 이온화에 대한 확률은 아직 0과 1 사이에 있다.

## 지원영역 분리 정리 (유도/동일 작성자 검산)

1. H 기원 E<=23.60 eV; He I 첫 광이온화 문턱 24.59 eV 불충족. H I 첫 흡수 후 초기 전자 ε<=10 eV이므로 추가 H I는 불가능.
2. He 기원 E<=34.59 eV. He I 첫 흡수 후 초기 전자 ε<=10 eV이므로 추가 H I는 불가능.
3. He 기원 광자가 **H I에 처음 흡수**될 때 ε=E-13.60 eV ≤20.99 eV. 추가 H I 사건은 E>=27.20 eV에서만 에너지상 허용된다. 원본 He 기원 3,200 energy atoms 중 2,389 원자가 이 구간이다.
4. ε_max=20.99 eV <24.59 eV와 < 2×13.60=27.20 eV. 초기 광전자 한 개당 추가 He I 이온화 0, 추가 H I 이온화 최대 1회.
5. He I 원자의 **단일 광자 직접 이중 광이온화** 문턱은 He I+He II 이온화 에너지 합 약 79.0078 eV (원본 I_He와 NIST I_HeII 결합). 원본 광자의 E_max=34.59 eV는 문턱보다 44.4178 eV 작다. 이를 **전체 BASS/REI helium double-event kernel이 0**이라는 주장으로 확대하지 않는다. 충돌성 He 이중 사건 또는 고에너지 외부 photon owner는 별개다.

## 에너지/인과 응답

일차 추가 H 사건 발생 조건부로 결합에너지 `I_H e_J`가 필요하다. 최대 H 이온화 결합에너지 용량:

`B_H^cap(T)=I_H e_J C_H(T) [J m^-3]`, where `e_J=1.602176634e-19 J/eV`.

허용 사건이 모두 실현되었다는 반사실 조건의 최초전자 운동에너지 예산 분할:

`Q_eligible(T) = B_H^cap(T) + Q_leftover^if-all-eligible(T)`.

이는 충돌/여기 과정에 실제로 얼마가 침적됐는지 나타내지 않는다. 두 자유전자의 운동에너지 합이 남은 예산 이하라는 상한이다. 인과적 로그중성 변분 `[u,v]`에 대해 PHYS09 기존 원본 커널 `G_ab^[u,v]`을 재사용하여

`D_b^[u,v] C_H(T) = Σ_{i,j,a} w_ij chi_{a->H}(E_i) G_ab^[u,v](E_i,T|s_j)`.

본 source에서는 He 기원 / H I 최초 흡수만 비영, 다른 origin/absorber 채널은 정확히 0. C_H의 도함수는 signed response이며 충돌 발생률이 아니다. PHYS09 G 합·차원·인과조건을 상속한다.

## 검증과 의미

(1) Source arrays에서 kinematic support 2,389/3,200 positive; (2) 원본 첫 흡수 총합 PHYS10 108/108 재현; (3) 출력 에너지 예산 최대 잔차는 실제 스크립트 수치 로그 참조; (4) 독립 구현의 직접 competing hazard 적분/유한차분, 내부 C9 같은 모델 적대적 검사. Genuine independent distinct-author R06/C09는 NOT_RUN.

공통 진화 중성기체·복사장·clock/geometry 및 실제 전자충돌 K와 stopping, energy-sharing differential kernel은 아직 미확보다. 중앙 물리 DAG 28/88 변화 없음. 본 노드는 정확한 source-supported zero/one channel pruning만 제공한다.
