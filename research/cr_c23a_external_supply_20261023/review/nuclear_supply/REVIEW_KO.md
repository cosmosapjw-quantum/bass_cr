# C23A 핵 beta 공급 coverage — 독립 C9 검토

## 판정과 실제 검토 범위

**PASS_SCOPED.** 선택된 legacy 평가 중앙값에 대한 조건부 moment bound와 별도 F=1 phase-space 예시의 에너지-domain 계산을 채택할 수 있다. 필수 코드 수정이나 수치 재실행을 요구하는 결함은 발견하지 않았다. 물리적 beta-to-IGM deposition, spectrum reconstruction, 공급 rate, 21종 네트워크의 완성을 승인하는 판정은 아니다.

생산자 코드/API/quadrature/기존 계산을 실행하지 않았다. 소스·원 DAT·완료 결과·receipt를 읽고, 식을 독립적으로 유도했다. 별도의 0.007초 stdlib 검사는 파일 SHA와 Git blob 및 몇 개의 정확한 유리수 moment만 확인했다. 새 ODE0, 기존 ODE 재실행0, quadrature 재실행0, 외부 source API0이다.

검토한 packet manifest:

`f4d667d23e567b1165193ce6a43c6374058fc0d54b41cae40fb5ea8e462c11db`

실제 29개 payload, 233,841 bytes와 completed-run pin7개가 모두 일치했다. 상세 receipt는 `READ_AND_ALGEBRA.json`이다.

| 대상 | 고정 SHA256 |
|---|---|
| `beta_domain_coverage.py` | `b96f9e624fd7c43d2f71f8c7ee8e904a3d76c9fd4268830c0ca4e3e16c2fcd97` |
| `run_beta_domain_coverage.py` | `b096a5cd40af4b70a7d1afcd8247b7affd5a2eaef33bb612f3880b54b20a37f8` |
| energy/domain contract | `23426695877a9c156a474cc908d1dba7185f87c4e91b8b7b7abd46ee1335562b` |
| completed `RESULT.json` | `e11ac9f223f95d0d6f8d38796e615ffb20d91bc4fd2ac95afc6054a5c763c485` |

## 1. 실제 평가자료의 의미

기존 `EVALUATED_DECAY_INPUTS.json`을 읽고 Git blob `33fd920abce6cc28ff26a850b030bb7b4fd2462e`를 bytes에서 다시 확인했다. 파일은 neutron mean lifetime 및 tritium half-life와 단위 정의를 담고 있으며 평균/끝점 에너지 필드는 없다. 새 source에서 기존 lifetime 값을 덮어쓰는 경로는 없었다.

새 IAEA DAT 두 개의 MF8/MT457 수치와 저장된 ENDF-102 관련 형식 설명을 대조했다. 이번 선택은 EVAL-NOV05, ENSDF conversion20111222, DIST-FEB18의 역사적 중앙값이다. branch probability1, beta intensity1, TYPE1과 LCON0을 읽는 전용 parser의 field 위치가 해당 bytes와 맞는다. 평균값은 STYP1의 ERAV에서 가져오며, 전체 electron-related average와도 일치한다.

| 선택값 | neutron | tritium |
|---|---:|---:|
| Q=ER [eV] | 782347 | 18590 |
| 평균 beta 전자 운동에너지 [eV] | 301370 | 5690 |
| 기록된 평균 불확도 [eV] | 0 | 40 |

기록된 0 불확도를 물리적 불확도0으로 채택하지 않는다. Q/ER 중앙값은 선언된 support ceiling 및 예시 endpoint parameter다. ER=Q라는 기록을 recoil·atomic/molecular final state를 포함한 정밀 끝점으로 승격하지 않았다. LCON0은 tabulated continuous spectrum이 없다는 의미이며, beta branch 기록 하나를 실제 monoenergetic electron spectrum으로 취급하지 않는다.

source bytes와 기존 ENDF 수명·recoil0 항목을 읽는 행위, 그 값을 현재 물리 모델에 채택하는 행위가 분리되어 있다. 실패한 LNHB PDF 다운로드도 `PRIMARY_DOWNLOAD_RECEIPT.json`에서 오류로 유지된다.

## 2. 조건부 bound의 독립 증명

같은 frame의 전자 운동에너지 T에 대해 양의 확률측도 nu의 support가 [0,Q]이고 평균이 m이며 0<L<U<Q, 0<m<Q라고 하자. D=[L,U]에서

\[
P_D=\int_Dd\nu,\qquad F_D=\frac{\int_D T\,d\nu}{m}
\]

로 정의한다. 다음 점별 부등식은 support 전체에서 성립한다.

\[
\mathbf1_D\le1,\quad \mathbf1_D\le T/L,\quad
\mathbf1_D\le(Q-T)/(Q-U),
\]

\[
T\mathbf1_D\le T,\qquad
T\mathbf1_D\le\frac{U(Q-T)}{Q-U}.
\]

마지막 식은 D 안에서 분모를 곱한 차가 Q(U-T)>=0이므로 성립하며, D 밖에서는 좌변이0이고 우변이 비음수다. 따라서

\[
0\le P_D\le\min\left(1,\frac mL,\frac{Q-m}{Q-U}\right),
\qquad
0\le F_D\le\min\left(1,\frac{U(Q-m)}{m(Q-U)}\right).
\]

모든 비율은 무차원이다. F_D는 전체 beta 전자 운동에너지 중 구간 안 비율이며, 입자수 비율이나 전체 nuclear Q 대비 heat fraction이 아니다.

하한0은 (1-m/Q)delta_0+(m/Q)delta_Q에서 실현된다. 상한의 sharpness는 m<L이면 0,L의 혼합, L<=m<=U이면 delta_m, m>U이면 U,Q의 혼합으로 확인한다. 실제 연속 beta spectrum이 이 원자적 극값과 같다는 주장은 필요하지 않다. 연속 양의 밀도에서 경계점으로 집중하는 극한도 같은 상계를 보존한다.

neutron 입력에서 독립 유리수 검산은

\[
F_D\le\frac{477956945417}{23278113841230}
=0.020532460175980698
\]

을 주었다. 표 밖 운동에너지 비율의 조건부 하한은 0.9794675398240194이다. Tritium은 m이 D 안에 있어 moment-only 결과가 0..1이며, 유의한 양의 tail 하한이 없다.

정규화·평균·Q endpoint가 같은 두 atomic witness의 유리수 moment도 별도로 확인했다. smooth density의 경우 세 bump에 대한

\[
h=(c-b)\phi_a-(c-a)\phi_b+(b-a)\phi_c
\]

는 zeroth/first moment가0이다. D 안에 있는 bump의 계수는 -(c-a)이고 energy moment 변화는 -b(c-a)이므로 coverage가 변한다. 충분히 작은 양·음의 perturbation은 양수성과 원 support를 유지한다. 이는 주어진 두 moment의 비유일성을 구성적으로 보이는 결과이며, 추가 핵물리 정보로 spectrum을 정하는 가능성을 배제하지 않는다.

구현의 `moment_bounds`는 witness center를 이번 n/T 값에 맞춰 선택한다. 일반적인 m<=L 등의 입력에서 거부될 수 있다는 제한은 source comment와 작성자 인계에 명시되어 있다. 이번 판정은 일반-purpose beta-spectrum API를 승인하지 않는다.

## 3. F=1 예시의 차원과 독립 계산식

M=m_e c^2를 eV로 표현하면

\[
w(T)=\sqrt{T(T+2M)}(T+M)(Q-T)^2
\]

의 첫 인자는 p_e c이며 w의 차원은 energy^4다. 따라서 I_k=integral T^k w(T)dT의 차원은 energy^(k+5)이고, I_1/I_0은 mean energy, I_2/I_0은 energy^2, 구간 I_0/I_0,total과 I_1/I_1,total은 서로 다른 무차원 비율이다.

x=T/Q=u^2, r=M/Q를 대입하면 production의

\[
I_k/Q^{k+5}=\int 2u^{2k+2}\sqrt{u^2+2r}(u^2+r)(1-u^2)^2du
\]

와 일치한다. square-root endpoint를 제거하면서 energy 단위를 먼저 소거했다. 닫힌 primitive도 독립적으로 확인했다. y=T+M, R=sqrt(y^2-M^2)에 대해

\[
\frac{d}{dy}(y^{n-1}R^3)
=(n+2)y^nR-(n-1)M^2y^{n-2}R
\]

이므로 코드의 J_n recurrence가 성립한다. (y-M)^k y(Q+M-y)^2의 polynomial coefficient 전개와 Q^(k+5) 정규화도 맞다.

저장된 실행은 24개 moment/interval 비교에서 SciPy 대 mpmath80 최대 상대차 3.8778666753123036e-16, analytic 대 mpmath80 2.9699989207856394e-60을 기록한다. 리뷰어가 이를 재실행한 것은 아니다. 관련 source 식·기준·saved receipt의 일관성을 검토했다.

예시 mean은 302773.71918246703 eV와 6230.47603410111 eV로 평가 mean과 다르며, code/result/report가 이를 다른 모델로 표시한다. F=1을 TYPE1의 물리적 정확성 결과로 해석하거나 평가 mean에 강제로 맞추지 않았다.

## 4. Carrier·에너지 ownership·dominant omissions

`ElectronDomain.require_source`는 electron/kinetic/eV만 받는다. 소스 읽기에서 neutron, proton, photon, antineutrino 등 다른 carrier를 거부하는 분기를 확인했고 저장된 RESULT에도 여섯 종류의 명시적 거부가 기록되어 있다. `classify`는 low/high tails를 UNRESOLVED로 반환한다. 이 component는 FS deposition solver를 호출하지 않는다.

주입 후보는 이미 생성된 primary beta electron의 운동에너지다. Antineutrino, daughter recoil, radiative photons, born neutron/proton kinetic energy에는 별도 owner가 필요하다. 실제 Q-m을 neutrino/recoil의 유일한 분할로 채택하지 않는다. 예시의 Q-mean 필드는 recoil-free/massless-neutrino 모델 안에서만 정의된다.

두 tail의 입자수와 에너지는 보존되고 heat/ionization 출력은 null이다. 0 또는 자동 heat로 채우지 않는다. in-domain 값도 기존 FS bath/axis/energy-closure 문제를 닫지 않는다. 원 n/T 초기 inventory, 21종 abundance, 기존 수명, nuclear production rate 및 핵자 kinetic source를 변경하는 경로는 없다.

후속 adoption에서 우선 해결할 결손은 다음과 같다.

1. **지원 에너지 범위:** 선택된 neutron mean/Q만으로 이미 최소97.94675%의 beta electron kinetic energy가 현재 표 밖이다. 고에너지 electron transport/tail 처리 없이 full source를 연결할 수 있는 근거가 없다. Tritium의 실제 tail은 moment만으로 정해지지 않는다.
2. **물리 spectrum:** Coulomb/Fermi function, recoil/weak magnetism, radiative correction 및 photon branch, screening/exchange, atomic/molecular initial/final states와 해당 shape correction의 실제 채택이 필요하다. F=1 예시와 정밀 적분의 일치가 이 생략을 보정하지 않는다.
3. **frame 및 charge/isotope mapping:** mean/Q/support는 같은 energy frame에 속해야 한다. 움직이는 n/T나 cosmic-ray parent를 bath frame으로 변환하면 support와 spectrum도 변한다. Free/atomic/molecular, charge-state 및 daughter channel을 source 계약에 연결해야 한다.
4. **공급 진폭과 열화:** 실제 n/T abundance/production, decay source normalization, bath composition 및 transport/escape/thermalization 시간을 새 입력으로 정해야 한다. 현재 per-primary energy-domain 비율은 실제 heating rate가 아니다.

frame/initial-state 지적은 작성자의 `ADOPTION_OBLIGATIONS.json`과 report/handoff addendum에 반영됐다. 고정 source/code/RESULT를 바꾸지 않은 최소 문서 보충이다. C9의 scope 기록 의무는 처리됐고 물리 adoption 의무는 OPEN이다.

## 네 축과 인계

| 축 | 판정 |
|---|---|
| EXECUTION | 읽기·독립 대수 C9 COMPLETE_SCOPED / PASS_SCOPED; 생산자 코드·API·quadrature·ODE 재실행0 |
| PUBLICATION | 부모 통합 대기. reviewer 외부 게시0 |
| BACKUP | create-only 로컬 검토 자료. remote backup은 부모의 실제 receipt에 연결 |
| DAG | nuclear coverage source/proof/diagnostic/saved validation → **C9 완료** → 부모 C10. corrected spectrum/frame/transport/ownership OPEN |

`global_error_bound=null`. 전체 thermochemical 또는 nuclear 연구의 완성률로 이 C9 판정을 사용하지 않는다. Full nuclear high-energy와 general triaxial/tilted/polarized CMB HOLD를 유지한다. 다음 루프는 완료된 결과를 재사용하고 새로운 물리 입력·새 run ID에 연결한다.
