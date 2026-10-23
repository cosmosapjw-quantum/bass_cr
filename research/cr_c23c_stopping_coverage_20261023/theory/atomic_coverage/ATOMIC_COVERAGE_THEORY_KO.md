# C23C N5: 원자율 coverage와 동위원소 축약의 정확한 계약

## 결과와 사용 범위

21개 원자·핵종 population과 별도 자유전자 총수에서, 13개의 인접 전하 전이를 구성했다. 광이온화(PI), 전자충돌 이온화(CI), 복사재결합(RR)의 반응물/생성물 계수는 각각 다르며 같은 전하 전이의 net stoichiometry를 공유한다. 각 반응은 8개의 개별 핵종 수와 전하를 보존한다. 새 `atomic_contract.py`는 이 계약, 알려진 문턱 아래 0과 미지원 구간의 null 구별, 공급된 사건 에너지 회계, 유한 질량 recoil 계수, 동위원소 수·에너지 축약 판별을 구현한다. 실제 경험적 rate는 추가하지 않는다.

이 문서는 parent가 선택한 C23C 전체 연구의 N5 하위 단위다. PhysMath 1.3.0 및 POLICY_INTEGRATION을 읽고 적용했으며, 기본 1.0.0 R/C 단계 정의는 parent의 연속 연구 문맥에 대응시켰다. 자식은 구현과 구문 컴파일만 수행했다. 수용 테스트는 root의 자원 lease 아래 새 run ID로 실행한다. 완료 계산의 재실행, 원자율 평가, ODE는 이 자식에서 0이다.

## 1. 종과 전하: 총 자유전자와 열 bath의 구별

순서는 n; H1(0,1), D(0,1), T(0,1); He3(0,1,2), He4(0,1,2); Li6(0,1,2,3), Li7(0,1,2,3)이다. 합계는 1+6+6+8=21이다. 자유전자 e는 22번째 보존 회계 변수이며, 원래 21개 inventory를 변경한 것이 아니다. 입력 inventory는 21개 키 모두를 요구한다. 명시된 n/T 초기 0은 허용하고, 누락된 키를 0으로 대체하지 않는다.

한 isotope A의 charge q에 대한 CI는

\[
A^q+e\rightarrow A^{q+1}+2e,
\qquad \Delta N_{A^q}=-1,\quad\Delta N_{A^{q+1}}=1,\quad\Delta N_e=1.
\]

PI는 들어오는 photon을 방사장 소유자로 지정하며, RR는 역전하 전이와 나가는 photon 소유자를 갖는다. 원자 inventory와 자유전자만 세는 monatomic particle count는 CI/PI에서 +1, RR에서 -1이다. 이 수를 핵종 수 또는 baryon 수와 혼동하지 않는다.

여기서 e는 **자유전자 총수**다. 이후 Coulomb bath가 사용하는 전자 수는 별도 `n_e,th`다. `n_e,total = n_e,th + n_e,fast`를 유지해야 한다. PI 직후 fast electron에 소유권을 주면 자유전자 총수는 증가하지만 열 bath 입자 수는 assimilation 전까지 증가하지 않는다. 따라서 전하 중성으로 얻은 전자 총수를 자동으로 Maxwellian bath 밀도로 전달하지 않는다.

8개 핵종 행렬 B와 전하 행 벡터 z에 대해 모든 원자 반응의 stoichiometry S는

\[
BS=0,\qquad zS=0.
\]

실제 핵반응에서는 B의 각 isotope 보존을 요구할 수 없으므로 별도 baryon/charge 계약으로 바꾼다. 이 모듈은 원자 반응만을 허용한다. n에 원자 ionization rung을 만들려는 입력을 거절한다.

## 2. Rate support는 에너지 회계와 따로 고정한다

source의 incident-energy interval, chemical defect, kinematic threshold, 수치 온도 domain, 물리 정확도 domain을 각각 저장한다. 이 다섯 값의 구별은 실제 자료에서 필요하다. PHYS81의 H1 source 하한 13.6058 eV와 chemical defect 13.598434599702 eV는 다르다. HE37 source model threshold는 13.6 eV다. PHYS83 CE는 source-native LS gap 10.20435 eV를 유지한다. [G1–G4]

`SourceSupport.classify(E)`는 세 상태를 반환한다.

| 상태 | 값 | 의미 |
|---|---|---|
| PHYSICAL_THRESHOLD_ZERO | 0 | 해당 provider에 명시적으로 승인된 threshold보다 낮음 |
| SOURCE_COVERED_VALUE_NOT_EVALUATED | null | source interval 안이며 실제 provider 평가가 필요함 |
| UNCOVERED_UNKNOWN | null | source 밖의 물리 값을 확보하지 않음 |

table의 첫 knot를 물리 threshold로 추정하지 않는다. finite operator에서 밖을 제외하는 연산 정의는 물리 cross section이 0이라는 명제와 구별한다. 이 모듈은 covered metadata만으로도 rate 값을 발행하지 않는다.

## 3. 사건 에너지와 온도 방정식

같은 normal frame에서 공급된 일전자 이온화 사건은

\[
K_{\rm in}+E_{\gamma,{\rm in}}
=\chi+\sum_j K_{{\rm out},j}+K_{\rm recoil}+E_{\gamma,{\rm out}}.
\]

\(\chi>0\)는 해당 reaction의 chemical binding defect다. 코드가 제공되지 않은 secondary-electron energy나 heat를 잔차로 만들어내지 않고, 별도로 공급된 값들의 residual을 반환한다. Recoil 입력은 명시적인 0을 포함해 필수다. 출력의 electron pool은 `all_free_kinetic`으로 고정된다. 이 기능은 공급된 에너지 원장의 contraction이며, 실제 consumer가 source/common frame/reaction multiplicity를 결속한다. Differential collision provider 또는 thermal-heating admission gate로 승격하지 않는다.

모든 입사·출사 전자가 같은 열 pool에 속하고 recoil을 그 pool에 포함시키면 CI의 순 병진 에너지 변화는 \(-\chi\)다. reaction-selected mean incoming energy 전체를 추가 cooling으로 빼면 이미 되돌아온 outgoing kinetic energy를 이중 계산한다. RR의 열 에너지 변화에는 포획되는 전자의 rate-weighted kinetic moment가 필요하다. 총 RR coefficient 하나로 그 moment나 photon spectrum을 얻지 않는다.

monatomic bath에서 \(U_{th}=3n_{th}k_BT/2\), \(P_{th}=n_{th}k_BT\), \(\dot n_{th}+\Theta n_{th}=S_{n,th}\), \(\dot U_{th}+(U_{th}+P_{th})\Theta=Q_{th}\)이면

\[
\frac32 n_{th}k_B\dot T
=Q_{th}-n_{th}k_BT\Theta-\frac32 k_BT S_{n,th}.
\]

마지막 항은 반응과 assimilation에 의한 열 입자 수 변화다. 핵종/charge equations만 닫아도 이 EOS 항과 excitation storage/radiation/stopping의 소유권은 별도로 필요하다. HH83의 핵 fast-first 계약은 stopping과 assimilation을 분리하고 이 구조를 재사용할 수 있게 한다. 실제 nuclear rates/stopping은 그 기록에서도 OPEN이다. [G4]

## 4. 정확한 isotope quotient 조건

한 원소 Z의 각 isotope charge 벡터를 \(n_A\), 공통 bath state를 \(\lambda\), column-oriented generator를 \(G_A(\lambda)\)라 하자. \(\dot n_A=G_A n_A\), \({\bf1}^TG_A=0\), off-diagonal entries는 음이 아니다. 합 \(X=\sum_A n_A\)가 임의 isotope allocation에 대해 같은 \(\dot X=\bar G X\)를 만족할 필요충분조건은

\[
G_A(\lambda)=\bar G(\lambda)\quad\text{모든 }A.
\]

충분성은 합에 직접 대입하면 따른다. 필요성은 주어진 charge vector를 한 isotope에만 배정한 입력들을 각각 선택하면 따른다. 모든 bath state에서의 축약을 원하면 이 등식이 domain 전체의 함수 identity여야 한다. 유한 sample의 같은 rate는 이를 증명하지 않는다.

binding storage \(U_b=\sum_A\epsilon_A^Tn_A\)의 source까지 quotient로 계산하려면, 수 closure에 추가하여

\[
\epsilon_A^TG_A(\lambda)=\bar\epsilon^T\bar G(\lambda)
\]

가 모든 isotope에서 성립해야 한다. 공통 G의 charge graph가 irreducible이면 left nullspace는 상수 행이므로 \(\epsilon_A-\bar\epsilon=c_A{\bf1}\)와 동치다. 이 isotope별 상수 offset은 보존된 전체 isotope 수에만 곱해져 \(\dot U_b\)에 기여하지 않는다. 곧 각 charge rung의 binding defect가 같아야 에너지 source의 같은 quotient를 얻는다. reducible/zero generator에서는 더 큰 nullspace가 가능하므로 코드가 직접 \(\epsilon_A^TG_A\)를 비교한다.

손으로 계산한 판별 예는

\[
G=\begin{pmatrix}-2&1\\2&-1\end{pmatrix},\quad
\epsilon_a=(0,13),\quad\epsilon_b=(0,14).
\]

수 generator는 같지만 binding source rows는 각각 \((26,-13)\), \((28,-14)\)다. 대신 \(\epsilon_b=(5,18)\)이면 constant offset만 있어 둘 다 \((26,-13)\)다. 이것은 isotope reduction의 적용 조건을 검증하는 합성 반례이며 새 일반 no-go나 실제 원자 데이터 주장이 아니다.

실제 H/D/T의 NIST source는 서로 다른 ionization energies를 열거한다. Li7 원논문의 직접 공개된 결과는 43487.15940(18) cm^-1이며 Li6/Li7 ionization isotope shift도 측정한다. 따라서 energy defect까지 동일한 exact physical isotope quotient는 자동 채택할 수 없다. 본 연구는 isotope-resolved 표를 새로 활성화하지 않고 필요한 equality/approximation contract를 명시한다. [P1,P2]

## 5. Recoil와 finite-T averaging에서 남기는 질량

정지 표적 질량 M, 전자 질량 m, 비상대론 elastic collision의 CM scattering angle \(\theta\)에서 표적이 받는 에너지는

\[
\Delta E_M=\frac{2mM}{(m+M)^2}E(1-\cos\theta).
\]

따라서 \(\sigma_{mt}=\int(1-\cos\theta)d\sigma\)를 사용하면 한 에너지에서 stopping power는 \(n_MvE[2mM/(m+M)^2]\sigma_{mt}\)다. 질량 계수는 별도 pure-rational 함수로 구현했다. Heavy-target limit에서 \(2m/M\)로 작아지지만 isotope 사이의 상대적인 energy-transfer 차이를 지워 주지는 않는다.

모든 isotope의 같은 lab-energy momentum-transfer cross section을 **추가 가정**하면 mixture stopping은 \(n_{eff}=\sum_A n_A 2mM_A/(m+M_A)^2\) 하나로 정확히 계산할 수 있다. 수 opacity의 \(\sum_A n_A\)와 다른 가중 합이다. 실제 isotope-dependent cross sections, 움직이는 target, excited state는 이 식의 외부 의무다.

서로 독립인 isotropic NR Maxwellian 입사/표적과 zero drift에서 relative velocity 분산으로부터

\[
\mu=\frac{mM}{m+M},\quad T_{rel}=\mu\left(\frac{T_e}{m}+\frac{T_A}{M}\right),\quad
\langle\sigma g\rangle=\sqrt{\frac8{\pi\mu}}(k_BT_{rel})^{-3/2}
\int E_r\sigma(E_r)e^{-E_r/k_BT_{rel}}dE_r.
\]

같은 T면 \(T_{rel}=T\)다. source가 stationary-target lab-energy 표이면 \(E_r=(\mu/m)E_{lab}\)의 좌표 변환과 mass convention을 확인해야 한다. 전자 질량으로 평균한 기존 rate에 reduced-mass prefactor만 교체하지 않는다. CI의 stationary-target relativistic threshold도 chemical defect와 구별된다. 중성원자 rest mass \(M_0\)와 입사 전자 m에 대해 invariant threshold는

\[
K_{lab,th}=\chi\left(1+\frac m{M_0}\right)+\frac{\chi^2}{2M_0c^2}.
\]

이는 final ion+two-electron rest-energy 합 \((M_0+m)c^2+\chi\)와 initial invariant를 같게 놓아 얻는다. 이 식은 source axis를 자동 보정하라는 처방이 아니다. source-native model과 finite-mass physical model은 서로 다른 identity를 가져야 한다.

## 6. 최신 donor를 통합한 coverage 결정

| Provider | 확보 범위 | 다음 연결의 실제 의무 |
|---|---|---|
| PHYS81/C22D CCC CI | H1 13.6058–968.61, He4 24.6–60, Li7 6–15 eV finite operator; 수치 T 255–50000 K | D/T/He3/Li6 transfer, physical tail/interpolation accuracy, moving-target energy moments |
| PHYS82 Li gap | CCC 6 eV endpoint에 붙인 네 조건부 family와 별도 역사 실험 slope comparator | isotope-resolved unsmeared true curve와 uncertainty enclosure; full tail |
| HE37 Le–Cambier Eq85 | H1 stationary heavy target/isotropic outgoing source model; 수치 T 2000–200000 K | 실제 angular calibration, finite mass, isotope transfer; empirical cross-section accuracy |
| HH83 PR140 source/physics | H I 1s/2s/2p finite matched CE/reverse source, A branches 및 nuclear ownership derivation | 새 CE scientific rates/steady/transient는 실제 ledger상 NOT_RUN; level augmentation과 coupling 필요 |
| C23B source | 이미 복원된 H/He fit-label UV primary source와 finite FS operator | full21 mapping, low-E thermalization, numeric FS He/H composition, complete energy closure |

HH83 head `65c6751d363363cfc15eba0c7debf50eb493c1c9`의 `EXECUTION_LEDGER.json`은 new CE attempts/completed/rates/steady/transient 모두 0이다. PR 이름의 completion 또는 prepared implementation을 계산 완료로 세지 않는다. 새 데이터가 확인되면 그 descendant에 대해서만 갱신한다.

OPEN-ADAS는 다운로드 가능한 데이터이지만 현재 공식 약관은 파일 재배포/코드 동봉에 사전 서면 허락을 요구한다. 이 패킷은 ADAS raw data를 추가하지 않는다. CCC index/README에서 명시적 redistribution licence를 확인하지 못한 상태와, 공개적으로 찾아 읽은 소수 수치 사실/자기 프로젝트 코드의 재사용을 구별한다. [P3,P4]

Li–H/D/T inelastic 충돌의 isotope effects는 source마다 별도다. Belyaev–Voronov 원논문의 공개 abstract는 low-level resonant channels에서 큰 isotope dependence를 보고한다. 여기서는 그 결과를 electron-CI rate로 옮기지 않고, He/Li charge-exchange에 임의 isotope equality를 부여하지 않는 근거로만 사용한다. fulltext는 authorization wall로 미열람이다. [P5]

## 7. 독립 C9 교정과 실행·재개

독립 intake reviewer가 code docstring의 connected 조건을 지적했다. 위 본문 정리는 이미 irreducible로 기술했으며, 구현 docstring을 rank(G)=n−1 (특히 irreducible)로 맞췄다. Weakly connected reducible generator에서는 constant binding offset이 필요하지 않을 수 있다. 예를 들어 G=((0,1,0),(0,−2,0),(0,1,0)), epsilon_a=(0,13,24), epsilon_b=(0,14,26)이면 양쪽 energy-source row는 (0,−2,0)이다. 중간 charge에서 이웃 두 charge로만 전이하고, 비상수 차이 (0,1,2)가 left-null에 속한다. 기존 직접 energy-row 비교 구현은 이 경우를 올바르게 다룬다.

같은 C9에서 일반 자유전자 kinetic ledger에 thermal loss라는 말을 붙인 검증 설명을 교정하고 recoil_eV를 필수 입력으로 바꿨다. 실행된 v1 source 2개는 implementation/history/v1에 exact bytes로 보존했다. 기존 155개 assertion은 재실행하지 않으며, 새 verify_atomic_repair.py의 6개 targeted check를 root가 별도 lease/run ID 아래 수행한다. 코드 의미가 바뀐 곳과 설명 교정의 영향을 REVISION_MAP.json에 구별한다.

`implementation/verify_atomic_contract.py`는 새로운 합성 rational 입력과 39 reaction direction의 보존을 확인한다. supplied event energy를 독립된 값으로 넣어 closure residual을 검사하고, isotope quotient의 참/거짓 witness를 구별한다. 실제 empirical rate evaluation 0, ODE 0으로 설계했다. 구문 컴파일은 성공했으며 본 단위의 runtime verification은 root lease runner의 별도 receipt가 권위다.

EXECUTION: root run c23c_atomic_contract_20261023_v1의 155개 및 c23c_atomic_repair_20261023_v2의 targeted 6개 모두 PASS_SCOPED. 원본155 재실행0, empirical rate0, ODE0. 실행된 source와 현재 revision의 대응은 implementation/history/v1 및 REVISION_MAP.json에 보존했다.
PUBLICATION: root-owned C23C additive publication pending.
BACKUP: root-owned C23C checkpoint/delivery pending.
DAG: N5 algebra/ownership contract COMPLETE_SCOPED → N4/N5 integration; physical full-rate and full21 energy closure OPEN. 독립 C9 세 지적은 같은 검토 pass에서 교정 및 targeted evidence 확인으로 닫혔다. CLOSEOUT.json이 이 자식의 최신 상태를 기록한다.

### 근거

- G1: `sources/PHYS81_PARENT_REGISTRY.json` 및 `sources/finite_ci.py`, PHYS82 final `ca9d5398…`; exact source pins는 SOURCE_PINS.json.
- G2: `sources/LI_THRESHOLD_SOURCE_CONTRACT.json` 및 HH82_FINAL_REPORT_KO.md, 같은 final commit.
- G3: `sources/HE37_PROVIDER_README.md`, HE37_SOURCE_ADMISSION.json, historical donor `a5a67096…`; 최신 다른 HE node와 합치지 않음.
- G4: `sources/HH83_CONTRACT.json`, HH83_EXECUTION_LEDGER.json, HH83_HI_CE_SOURCE_CONTRACT.json, HH83_NUCLEAR_OWNERSHIP_CONTRACT.json, PR140 current head `65c6751d…`.
- P1: NIST ASD ionization-energy output, https://physics.nist.gov/cgi-bin/ASD/ie.pl?at_num_out=on&biblio=on&e_out=0&el_name_out=on&format=1&level_out=on&seq_out=on&shells_out=on&unc_out=on&units=1 . Search-extracted official rows read; complete output open exceeded tool size; no complete-table claim.
- P2: Bushaw et al. (2007), DOI10.1103/PhysRevA.75.052503; primary-author institutional abstract https://www.pnnl.gov/publications/ionization-energy-li-6li-7-determined-triple-resonance-laser-spectroscopy .
- P3: OPEN-ADAS terms, https://open.adas.ac.uk/terms-and-conditions , read 2026-10-23.
- P4: Author CCC index, https://atom.curtin.edu.au/CCC-WWW/index.html , read 2026-10-23.
- P5: Belyaev & Voronov (2021), DOI10.1103/PhysRevA.104.022812, https://journals.aps.org/pra/abstract/10.1103/PhysRevA.104.022812 , public abstract read; fulltext UNAVAILABLE.

Exa query returned 402 credit-limit error; same query was not blindly retried. SciSpace search succeeded and supplied candidate papers, followed by primary-page checks. Neither result is a scientific rate provider. Private conversations were not accessed by this subtask.
