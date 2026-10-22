# C23A: 유한 에너지 fast-electron source와 스펙트럼 사전 적분

## 판정과 실제 산출물

**전자 침적표의 유한 보간 연산자와, 선언한 piecewise-linear(PL) 전자 공급 스펙트럼을 채널별로 정확하게 사전 적분하는 Python 구현을 완성했다.** 표의 원값·출처 충돌·에너지 잔차를 보존한다. 이 작업 단위의 계산은 원자/이온 상태를 진화시키는 ODE가 아니라 외부 source의 유한 응답 계산이다. `global_error_bound=null`, 새 ODE 0, 기존 ODE 재실행 0이다.

적용 규약은 `physmath-research-loop` 내장 1.0.0이다. 주 계산 결과는 `fs2010_operator.py`, 독립 수치 검산은 `audit_fs2010_operator.py`, 동일 입력 성능 측정과 모멘트 반례는 `benchmark_precontract.py`에 있다. 모든 실행은 CPU 3, native thread 1, create-only run directory와 lease를 사용했고 두 lease 모두 해제됐다. 부모 coordinator의 최종 독립 검토·게시·백업은 별도 상태다.

| 축 | 이 하위 작업의 실제 상태 |
|---|---|
| EXECUTION | 두 새 유한 source 계산 완료, PASS_SCOPED, ODE 0 |
| PUBLICATION | 부모 통합용 로컬 packet 작성; remote 게시 수행 0 |
| BACKUP | 로컬 실제 bytes와 SHA manifest; durable provider ACK는 부모가 확인할 의무 |
| DAG | R1–R9, C1–C8 산출물 완료; C9 부모 독립 검토와 C10 배송 확인 연결 |

전체 21-population 화학 상태에 결합하려면 source의 He/H, source-state axis 충돌, 원자료 버전, 1차/2차 에너지 귀속, 지연·방사 escape 조건을 먼저 닫아야 한다. 아래의 유한 연산자는 그 준비 단계에서 바로 재사용할 수 있다.

## 1. 취득한 1차 자료와 identity

### FS2010 원저자 배포본

원저자의 [codes and tools 페이지](https://cosmicdawn.astro.ucla.edu/codes_and_tools.html)에서 [elec_interp.tar](https://cosmicdawn.astro.ucla.edu/elec_interp.tar)를 실제 내려받았다. 2026-10-22 22:26:44 UTC에 HTTP 200, 310,272 bytes를 확인했다.

```text
SHA256 e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101
```

14개 표 × 258개 에너지 = 3,612행이며, 실제 에너지 범위는 **10.0–9937.21 eV**다. 표의 첫 열 제목은 `Photon Energy`지만 원 논문과 배포 C 인터페이스는 초기 **전자 운동에너지**를 정의한다. 원 C 코드는 실행하지 않았다. 원 tar에서 명시적 license 파일은 확인되지 않았다. `UPSTREAM_DOWNLOAD.json`의 최초 `license=PENDING_READ`는 당시 상태로 보존하며, 현재 판정은 `SOURCE_COVERAGE.json`에 있다.

물리 정의의 1차 문헌은 Furlanetto & Stoever, *Secondary ionization and heating by fast electrons*, MNRAS 404, 1869–1878 (2010), [DOI](https://doi.org/10.1111/j.1365-2966.2010.16401.x), [본문](https://academic.oup.com/mnras/article/404/4/1869/1083930), [arXiv](https://arxiv.org/abs/0910.4410)이다. 정적 primordial H/He 기체에서 전자 충돌 이온화·여기·전자 가열을 추적한다. §7의 상태는 \(\xi=x_{\mathrm{HII}}=x_{\mathrm{HeII}}\), \(x_{\mathrm{HeIII}}=0\)이다. He 여기 광자의 에너지는 재흡수한다고 가정한다. Lyα는 H 선복사 여기 에너지의 부분집합이다. 표 header에는 z=10, T=100 K가 있다. 논문의 collective plasma prescription은 가열률의 온도 의존을 단순화하지만, 임의의 뜨겁고 조밀한 기체에 대한 검증을 제공하지 않는다. 이 호출 계약에서는 온도·밀도·시간척도를 별도로 확인한다. [FS2010 §§2, 4, 6, 7]

### 재사용 후보의 실제 code/data bytes

| 자료 | 실제 pin과 취득 범위 | 이번 결정 |
|---|---|---|
| [21cmFAST](https://github.com/21cmfast/21cmFAST/tree/72d8a2d23702f1b69fbc85abd25d4592a7bcd3f5) | commit `72d8a2d23702f1b69fbc85abd25d4592a7bcd3f5`; tree `e3753fd2fc2ef42c9ca396d4420e382d0714c6d8`; MIT license와 14개 표의 Git blob 검증 | 원저자 표와 14/14 token-identical. 각 파일 끝 newline 차이로 byte-identical은 아니다. 전달 mirror 근거로 재사용 |
| [DarkHistory](https://github.com/hongwanliu/DarkHistory/tree/7a09f1991b0028cf00ec386bdea81b963f78794f) | commit `7a09f1991b0028cf00ec386bdea81b963f78794f`; tree `32ab51525baf4b7425c522ef09ad4468682cc5b0`; MIT license, legacy low-energy module, 작은 8개 MEDEA 표 | 실제 bytes 취득·검토. 이번 연산자의 수치 provider로는 채택하지 않음 |

총 25개 선택 blob을 실제 Git SHA1 및 SHA256으로 확인했다. 전체 repository 검증과는 범위를 구분한다. 상세 receipt는 `EXTERNAL_REUSE_DOWNLOADS.json`이다. 21cmFAST의 같은 표는 독립 물리 검증이 아닌 동일 수치 자료의 mirror다. MIT 배포본의 license와 attribution을 함께 보존하되, 원저자 C 코드에 임의로 MIT license를 소급하지 않는다.

DarkHistory 선택 module은 양의 floor와 재정규화를 수행한다. raw header와 반환 채널 순서의 연결에는 전체 call chain 검토가 더 필요하다. 이번에는 그 처리를 복사하지 않았다. 원자로 세분된 후속 provider 탐색은 [DarkHistory 2023 update](https://arxiv.org/abs/2303.07366)와 [MEDEA 원 논문](https://academic.oup.com/mnras/article/404/3/1569/1053924)에서 이어갈 수 있다. 이 후보들을 설치하거나 실행한 상태로 기록하지 않는다.

SciSpace와 Exa는 실제 사용했다. discovery receipt를 보존했다. SciSpace의 자동 요약 중 collisional ionization을 다루지 않는다는 문장은 원 논문 초록과 충돌하므로 배제했다. publication year는 원 학술지의 2010을 사용한다.

## 2. 원자료에서 직접 확인한 차이와 취급

### 좌표 메타데이터

공급 C 좌표와 raw header가 다음 네 파일에서 충돌한다.

| 파일 | C의 \(\xi\) | header의 HeII fraction | 의미 |
|---|---:|---:|---|
| `log_xi_-4.0.dat` | 0.0001 | 0.001 | header의 HeI+HeII=1.0009 |
| `log_xi_-3.6.dat` | 0.0002318 | 0.0002138 | C와 header 좌표 불일치 |
| `log_xi_-2.6.dat` | 0.002318 | 0.002138 | C와 header 좌표 불일치 |
| `log_xi_-1.6.dat` | 0.02318 | 0.02138 | C와 header 좌표 불일치 |

두 명시적 정책을 구현했다. `published_c_axis`는 C의 14개 좌표를 문자 그대로 사용하여 배포 연산자를 조사한다. `unambiguous_high_ionization`은 C와 header가 출력 정밀도에서 일치하는 마지막 다섯 좌표 **0.1, 0.5, 0.9, 0.99, 0.999**만 사용한다. 후자가 이번 성능 측정의 범위다. 데이터 자체를 수정하거나 저이온화 좌표를 추정하여 교체하지 않았다.

### 에너지 채널과 원 논문 표의 비교

raw 값에서 \(f_{ion}+f_{heat}+f_{exc}-1\)은 약 \([-2.0990\times10^{-7},3.9000\times10^{-5}]\)이며, 최대 `f_heat=1.00001`이다. \(10.2N_\alpha/E-f_{exc}\)의 최대 양의 차이는 약 \(4.01\times10^{-8}\)다. 이 작은 출력 잔차를 clipping이나 renormalization으로 숨기지 않았다.

논문 Table 1의 3 keV 가열 fraction과 현재 배포표의 3 keV 선형 보간 결과도 다르다. 예를 들어 \(\xi=0.9\)에서 각각 0.973과 0.9894905084이고, \(\xi=0.999\)에서 0.979와 0.9973633086이다. 5개 비교점의 실제 수치는 `SOURCE_DEFECTS.json`에 있다. 자료 버전·전제의 차이가 아직 해소되지 않았으므로 현재 downloaded interpolant와 논문 인쇄표를 하나의 동일 baseline으로 부르지 않는다. [FS2010 Table 1; 실제 원저자 표]

배포 C reader에는 `char label[]=" "`에 unbounded `%s`를 읽는 코드가 있다. 첫 header token만으로 버퍼 크기를 넘는다. 따라서 그 reader를 compile/run하지 않고 독립 Python parser를 작성했다. 원 C의 out-of-range clamp와 상단 endpoint 조정도 채택하지 않았다. 새 구현은 정의역 밖을 거부하고 실제 최상단 저장값을 포함한다.

## 3. 공급 source의 물리 계약

이 절의 식은 입사 공급과 기체 응답의 단위를 정의한 뒤 직접 유도한 보존·계수식이다. \(c,\hbar,k_B\)를 유지한다. 시간 변수는 \(\eta=\ln a\), \(d/d\eta=H^{-1}d/dt\)이고, \(n_{H,ref}(t)\)는 고정된 comoving reference number에 대응하는 물리 밀도다. 원자 종의 abundance는 \(X_s=n_s/n_{H,ref}\)로 정의한다. 전체 에너지 방정식의 팽창 일은 기존 closure가 담당한다.

### 3.1 UV/X-ray 흡수와 1차 결합에너지

등방 광자 수밀도 spectrum을 \(n_\gamma(\epsilon,t)\,[\mathrm{cm}^{-3}\,\mathrm{eV}^{-1}]\), 단면적을 \(\sigma_s(\epsilon)\), threshold를 \(\chi_s\)라 두면 흡수 사건 밀도는

\[
A_s(\epsilon,t)=n_s c\,n_\gamma(\epsilon,t)\sigma_s(\epsilon),\qquad
R_s^{pri}=\int_{\chi_s}^{\infty} A_s(\epsilon,t)\,d\epsilon.
\]

단일 광이온화에서 방출 전자 운동에너지는 \(E=\epsilon-\chi_s\)이고 Jacobian은 1이다. 따라서

\[
Q_e^{PI}(E,t)=\sum_s A_s(E+\chi_s,t),\qquad
\dot u_{bind}^{pri}=\sum_s\chi_sR_s^{pri},\qquad
\dot u_{e,kin}=\int E Q_e^{PI}(E,t)dE.
\]

FS response에 들어가는 것은 이미 생성된 전자의 **운동에너지**다. 최초 광자의 \(\chi_s\)는 별도 1차 ionization ledger에 남긴다. absorbed photon energy가 primary binding과 injected electron kinetic energy로 분해되는 등식이 입구 검증이다. Auger, double ionization, recoil 등의 채널이 채택되면 이 단일전자 식을 그 채널 정의에 맞춰 확장한다.

\[
q_e(E,\eta)=\frac{Q_e(E,t)}{H n_{H,ref}},\qquad
[q_e]=\mathrm{electron}\ H_{ref}^{-1}\eta^{-1}\mathrm{eV}^{-1}.
\]

정적 source-state 응답 \(N_s(E,\xi)\)와 \(f_c(E,\xi)\)에 대해

\[
(X_s')_{sec}=\int q_e N_s\,dE,\qquad
U'_{heat}=\int q_e E f_{heat}\,dE,\qquad
U'_{exc}=\int q_e E f_{exc}\,dE.
\]

\(N_\alpha'=\int q_e N_\alpha dE\)이며 \(10.2\,\mathrm{eV}\,N_\alpha'\)는 \(U'_{exc}\)의 부분항이다. 구현은 reported \(\int q_eE f_{ion}\)와 ionization counts를 모두 반환한다. chemistry에서 \(\sum_s\chi_s N_s\)를 사용할 때는 선택한 threshold registry와 raw `f_ion`의 차이를 별도로 검사해야 한다.

### 3.2 Cosmic-ray primaries의 위치

입자종 \(a\)의 등방 미분 intensity를 \(j_a(T)\,[\mathrm{cm}^{-2}\mathrm{s}^{-1}\mathrm{sr}^{-1}\mathrm{eV}^{-1}]\)로 두면

\[
Q_e^{CR}(E)=4\pi\sum_{a,s}n_s\int j_a(T)\frac{d\sigma_{a,s}}{dE}(T,E)\,dT.
\]

이 식의 입력은 proton/alpha 등의 입사 spectrum, 대상별 미분 secondary cross section, 그리고 column·loss·수송 조건이다. 하나의 총 이온화율 \(\zeta\)는 이 세 정보를 대신하지 않는다. 1차 이온화율은 별도로 \(4\pi n_s\int j_a\sigma_{a,s}^{ion}dT\)에서 계산한다. CR의 에너지 손실에는 primary binding, ejected kinetic energy, 직접 여기, recoil, 핵반응 등이 각각 귀속돼야 한다.

핵자당 에너지 \(\varepsilon\)와 핵 전체 운동에너지 \(T=A\varepsilon\)를 바꾸면 \(q^{(T)}(T)=q^{(\varepsilon)}(T/A)/A\)다. 단위 변환에서 이 differential Jacobian을 보존한다. 이 구현은 proton stopping 또는 nuclear spallation provider를 추가하지 않았다.

[Voyager local interstellar spectrum](https://iopscience.iop.org/article/10.3847/0004-637X/831/1/18)은 은하 국소 측정이므로 IGM 정규화로 옮길 때 별도 공간·시대·수송 모델이 필요하다. [Ivlev et al. 2021](https://arxiv.org/abs/2101.05803)의 secondary 계산은 molecular H2 column을 대상으로 한다. 이 두 source ensemble을 primordial atomic H/He 응답과 하나의 검증 ensemble로 합치지 않는다.

### 3.3 에너지 귀속과 중복 계산 방지

| 결합 위치 | 필요한 동작 |
|---|---|
| 기존 photoheating이 \(\epsilon-\chi_s\)를 즉시 열로 넣음 | 해당 fast-electron 구간의 즉시 열 항을 침적 채널로 대체하고 primary ionization은 보존 |
| thermal collisional ionization | Maxwellian thermal population의 rate를 유지하고 nonthermal source와 분리 |
| 2차 전자 cascade | FS의 후손 전자 계산에 이미 포함된 에너지를 다시 주입하지 않음 |
| helium excitation photon | FS가 가정한 재흡수 결과와 별도 radiation transport의 동일 광자를 중복 반영하지 않음 |
| 외부 \(\zeta\)에 secondary multiplier 포함 | primary 사건과 secondary 소유권을 해체한 뒤 필요한 항만 연결 |
| \(x_e=n_e/n_H\) 제공 | He 기여를 포함한 \(x_e\)를 FS의 \(\xi=x_{HII}\)로 직접 대입하지 않음 |

source의 수치 He/H는 취득한 표/code에서 명시적으로 확정하지 못했다. caller가 임의의 primordial 값으로 채우지 않는다. 가스 상태 \(x_{HII}=x_{HeII}\), \(x_{HeIII}=0\), He/H, thermal/nonthermal 분리, loss time과 background 변화 시간의 비교, secondary photon 재흡수/escape, IC 및 dense-gas 추가 손실을 함께 확인해야 물리 coupling을 채택할 수 있다. `require_physical_coupling`은 필요한 조건을 검사하는 함수이며, caller가 boolean을 전달했다는 사실만으로 이 과학적 근거가 생기지 않는다.

## 4. 계산 단순화의 유도와 구현

### 4.1 정의역과 보간

입력 `PLSpectrum`은 에너지 node \(E_k\)와 비음수 수 공급률 \(q_k\)가 **선형으로 연결된 함수 자체**를 뜻한다. node를 power law로 만든 검산 입력도 사이 구간의 정의는 PL이다. spectrum support가 [10, 9937.21] eV를 벗어나면 거부한다. 보간 좌표 \(\xi\)도 선택한 source axis 안에 있어야 한다.

표 에너지 node와 spectrum node의 합집합으로 구간을 나누면, 각 구간에서 \(q(E)\)와 각 \(f(E,\xi)\) 또는 \(N(E,\xi)\)가 affine이다. counts integrand는 2차, energy integrand는 추가 인자 \(E\)로 3차다. 따라서 적응형 ODE나 고차 quadrature가 필요 없다.

\(E=a+(b-a)u\)와 affine endpoint pair \((v_{r0},v_{r1})\)를 쓰면

\[
\int_a^b\prod_{r=1}^n v_r(E)dE
=(b-a)\sum_{\mathbf{s}\in\{0,1\}^n}
\frac{k!(n-k)!}{(n+1)!}\prod_{r=1}^n v_{r,s_r},\quad k=\sum_r s_r,
\]

여기서 \(n=2\) 또는 3이다. 이 양의 Bernstein 적분식을 `affine_product_integral`로 구현했다. 모든 입력 인자가 비음수이면 항도 비음수이고, 부호 교대 monomial 전개의 불필요한 상쇄를 피한다. 다항식 항등식은 정확하며 floating-point roundoff는 별도로 남는다.

### 4.2 상태 보간과 적분의 교환

\(\xi_i\le\xi\le\xi_{i+1}\)에서 \(K(E,\xi)=(1-t)K(E,\xi_i)+tK(E,\xi_{i+1})\)이다. \(q(E)\)의 모양이 이 query 동안 고정돼 있으면

\[
\int qK(E,\xi)dE=(1-t)\underbrace{\int qK(E,\xi_i)dE}_{P_i}
+t\underbrace{\int qK(E,\xi_{i+1})dE}_{P_{i+1}}.
\]

`prepare`는 모든 source \(\xi_i\)에서 7개 채널을 한번 적분하고, `PreparedResponse.at`은 이후 query를 채널 수에 비례하는 일로 처리한다. 스펙트럼 shape·support·table source가 바뀌면 다시 준비한다. 진폭만 변하면 선형 scaling을 사용한다. 고정 UV spectrum과 primary target별 photoelectron kernel을 사용한다면 종별로 미리 준비한 채널을 abundance로 조합하는 확장도 가능하지만, 먼저 threshold/energy coverage를 연결해야 한다.

### 4.3 보존 잔차의 정확한 범위

\(\delta=1-f_{ion}-f_{heat}-f_{exc}\)라 두고, 실측 node 최대값 \(\delta_{max}=3.900000000012227\times10^{-5}\)를 사용한다. bilinear convex interpolation은 이 node bound를 보존한다. 따라서 비음수 공급에서

\[
\left|\int q(E)E\delta(E,\xi)dE\right|
\le\delta_{max}\int q(E)E\,dE.
\]

이것은 **다운로드한 유한 표의 reported 채널 잔차**에 대한 bound다. cross-section, gas composition, 실제 Monte Carlo/물리 모형 또는 cosmological evolution의 global error bound로 확대하지 않는다. `reported_energy_defect`는 관측한 수치 잔차이며 새로운 물리적 energy reservoir가 아니다.

## 5. 실제 검증과 성능 측정

### 독립 검산

`c23a_fast_electron_source_audit_20261023_v1`의 실제 실행은 wall 1.432290 s, CPU 1.426292 s였다.

| 검사 | 실제 결과 |
|---|---|
| 3,612 table node 재현 | 저장된 float 값 exact |
| 3,341 bilinear cell midpoint/convex hull | PASS; 최대 normalized barycentric 차이 1.94e−15 |
| positive Bernstein vs 독립 70-digit Decimal monomial | 최대 상대차 3.55e−15 |
| 정의역·가스 상태 invalid input 13개 | fail-closed PASS |
| 사전 적분 vs 독립 2-point Gauss 적분 | 3 PL spectra × 9 \(\xi\); 최대 상대차 2.21e−16 |
| raw energy defect의 convex bound | PASS; 위 \(3.90\times10^{-5}\) bound |
| 비음수, 상단 endpoint, 5-row 원값 재사용 | PASS |

### 동일 입력 microbenchmark

`c23a_precontraction_timing_20261023_v1`는 결과를 보기 전에 `INPUT.json`을 create-only로 썼다. 입력 SHA256은 `b3f2db1ea3bdcb8bac79f0772a7b10903ef8797bd7b0eaa6d05eb3b97faf0fd7`이다. 3개의 선언된 PL spectrum, 각 64개의 같은 \(\xi\in[0.1,0.999]\), 3번의 paired repetition을 사용했다. 각 pair에서 사전 적분을 새로 만들었고 direct/query 순서는 번갈아 측정했다.

| 측정량 | 결과 |
|---|---:|
| 최대 direct/prepared 상대차 | 4.35066e−16 |
| query-only 시간비 median | 1008.21 |
| construction + 64 query 포함 시간비 median | 4.91144 |
| construction 상각 query 수 median | 12.9844 |
| construction 포함 시간비 범위 | 1.86383–5.91058 |
| 실제 전체 wall / CPU | 4.09255 / 4.08366 s |
| 최대 RSS | 14,976 KiB |

측정 시간의 변동과 모든 pair를 `RESULT.json`에 보존했다. 이 수치는 해당 Python 구현·작은 source grid·동일 입력에서의 microbenchmark다. cosmological ODE, 안정적인 생산 환경 wall time 또는 NCP 전체 작업의 speedup은 측정하지 않았다. 첫 audit의 16-query 비교는 construction을 포함하면 불리했으며, 그 원 기록도 보존했다.

## 6. 두 모멘트만 보존하는 축약의 판별 예제

다운로드한 유한 보간표의 \(\xi=0.1\)에서 다음 두 비음수 전자 공급 measure를 비교했다.

\[
q_A=\delta(E-100\,\mathrm{eV}),\qquad
q_B=\tfrac12\delta(E-10\,\mathrm{eV})+\tfrac12\delta(E-190\,\mathrm{eV}).
\]

둘 다 전자 수는 1, 운동에너지 모멘트는 100 eV다. 실제 table response는 다음과 같다.

| 채널 | A | B |
|---|---:|---:|
| reported ionization energy / eV | 6.38994453 | 8.94383421 |
| heat / eV | 86.49070834 | 81.91488963 |
| excitation / eV | 7.12006987 | 9.14221129 |
| HI ionization count | 0.43518703 | 0.60156979 |

가열 차이는 −4.57581871 eV다. \(\xi=0.5,0.9\)에서도 같은 입력 비교를 기록했다. 이 구체적인 유한 응답 예제는 전자 수와 총 운동에너지만 고정한 입력들이 같은 침적 채널을 준다는 가정을 반박한다. 계산 전략은 채널 response에 대한 적분 또는 충분한 spectrum 정보를 유지하는 방향으로 정해진다. 일반 수송에 대한 새로운 strong no-go 정리나 문헌 신규성은 채택하지 않는다.

## 7. 남은 의무와 다음 DAG

이번 unit의 후속 순서는 다음과 같다.

1. 부모가 frozen code·raw data·독립 수치 근거를 C9에서 검토하고 publication/backup receipt를 연결한다.
2. FS 원자료의 저이온화 좌표와 인쇄표/현재 archive 차이, source He/H 및 threshold registry를 확인한다. 동시에 현재 high-ionization 유한 연산자는 별도의 diagnostic provider로 보존한다.
3. UV/X-ray primary absorption 또는 proton differential injection에서 \(q_e(E)\)를 만드는 하나의 독립 source를 지정한다. 입사 spectrum의 단위·정규화·유효 에너지·공간/시간 상태·1차/2차 ownership을 고정한다.
4. 보존식에 필요한 gas-state submanifold, thermal/nonthermal 분리, local loss/transport·IC·escape 조건을 검증한다. 21종 상태는 이 제한된 source gas로 자동 projection하지 않는다.
5. admission된 조건에서만 chemistry/energy RHS adapter를 만들고, 새 입력·새 run ID의 경량 실행으로 이어간다.

핵반응을 추가할 때는 baryon number \(A^TS=0\), 전자·positron 등을 포함한 전하 보존, rest-mass Q value와 원자 결합에너지의 중복, 각 입사 에너지 정의와 channel coverage를 별도 검사한다. 현재 작업은 spallation·stellar/nuclear network를 완료하지 않았다. full nuclear high-energy와 general triaxial/tilted/polarized CMB의 HOLD를 변경하지 않는다.

## 다음 스레드에 복사할 하위 작업 handoff

```text
C23A CR/IGM source packet: cr_deposition/THEORY_AND_SOURCE_CONTRACT_KO.md.
Original author elec_interp.tar: 310272 bytes,
SHA256 e9760d637b5bd97fe981cb459a7e2d733692a9f9f8deb9a757224b14be632101.
14x258 raw table rows, E=[10,9937.21]eV. 4 axis/header conflicts;
printed paper/current archive discrepancy and source He/H remain open.
Use explicit published_c_axis for literal diagnostics or high-xi 5-row
unambiguous_high_ionization (xi=[.1,.5,.9,.99,.999]); no extrapolation.
fs2010_operator.py implements exact-PL positive-Bernstein spectral contraction.
2 new CPU3/thread1 create-only runs completed; leases RELEASED; ODE0.
First audit max prepared/Gauss relative difference2.21e-16; timing audit4.35e-16.
Same-input measured construction+64-query median ratio4.9114,
query-only1008.21, amortization12.984; wall-variable microbenchmark only.
Equal-number/equal-energy spectra100eV vs .5*10+.5*190eV atxi=.1:
heat86.49070834 vs81.91488963eV. Preserve channel-sensitive spectrum information.
Physical21-species coupling NOT_ADMITTED; global_error_bound=null.
PUBLICATION/BACKUP are root-owned and must use actual later receipts.
Next: independent review -> source He/H/axis/version/ownership resolution ->
one admitted primary source kernel -> gas/energy adapter -> fresh scoped run.
Do not rerun completed ODE or call this a completed full thermochemical network.
```
