# C21O 연구 루프: 최적화 준비 → 물리 계약 → 결합 계산

## 1. 이 기록의 범위와 현재 판정

이 문서는 `physmath-research-loop` 내장 운영 규약 **1.0.0**의 단계 이름을 유지해,
이번 단위에서 수행한 **최적화 코딩 C1–C10 → 새 물리 이론 R1–R10 → 결합 코딩
C1–C10**의 근거를 연결한다. 구현·문헌 조회·독립 검토 일부는 병렬로 진행했다.
아래 순서는 의존성과 인계 순서이며, 같은 검사나 실행을 세 번 수행했다는 뜻이 아니다.
최적화 준비에서 선택한 원자 rate cache와 결합 Jacobian은 물리 계약을 받은 뒤 최종
구현·검증되었으므로 해당 근거는 첫째와 셋째 루프에서 공유한다.

새로운 과학 실행은 **45개 격자 + 6개 판별 사례 = 51개**이며, 모두 샌드박스에서
`COMPLETE_SCOPED`로 반환되었다. 최초 선택 실행의 4개 격자 사례는 나머지 41개 실행
시에 재사용했다. 과거 C21L 81개, C21M/N 125개와 offgrid4의 ODE는 재실행하지 않았다.
이번 문서 작성에서도 계산·테스트·문헌 조회를 추가하지 않았다. [E08, E09]

현재 확보한 결과는 **처방된 UV·온도, photoionization + Case-A radiative
recombination, trace-gas 전자밀도–Thomson 결합을 사용한 non-tilted LRS Bianchi I
조건부 pilot**이다. 요청된 모든 핵반응·분자·isotope별 전자 반응·자기일관적
thermal/stellar/UV 역사를 완성한 상태는 아니다. 그 미완료 의무를 이 pilot의 성공과
분리한다. `global_error_bound=null`을 유지한다. [E01, E03, E09]

| 구분 | 이 문서 작성 시점의 상태 |
|---|---|
| EXECUTION | **51/51 COMPLETE_SCOPED**; 격자 45 + controls 6; 분석·focused 검증·독립 그림 검토 완료 |
| PUBLICATION | **CONTENT_PREPARATION**; 새 content commit 게시 준비. 이 문서는 아직 새 commit·PR 성공을 주장하지 않음 |
| BACKUP | **NEW_DELIVERY_PREPARATION**; 신규 배송 준비. 현재 C21O provider ACK를 만들어 기록하지 않음 |
| DAG | 과학·분석 근거 수렴 → **content publication → backup → document closeout** |

이는 content 게시 전 체크포인트다. 이후 실제 commit·provider 응답은 별도 최종 영수증으로
결속하며, 여기의 시점이 있는 상태를 소급해 성공으로 바꾸지 않는다.

## 2. 고정 baseline과 재사용 경계

- 원 REI 물리 source는 `3b85dedce84d37b3e165da00685a8a984950aafe`다. C21L adapter,
  C21N 독립응력 builder·prepared canonical momentum·mass-shell derivative를 재사용한다.
- 부모 문서 head는 `8dc5031b3323d4be42a7444843294200aa8887f2`다. 이번 실행 source identity는
  `c60d734b0ed8cc7d1a147e181da27c282e3f47be90f8b0eb1d65c030faabea0f`다.
- 새로운 문제에서만 끝점을 $a=1/3$, 즉 $z=2$로 설정했다. 기존 $z=20\to4$
  source lock·원 raw·과거 solver provenance는 유지한다.
- FP64, `rtol=3e-11`, scaled-state `atol=3e-13`, 저장점 201개를 기록했다. 새 stiff
  chemistry에는 BDF + analytic Jacobian을 사용하고 FLRW Radau 비교를 별도 실행했다.
  이 solver 선택은 새 결합 문제의 선택이며, 과거 DOP853 결과를 대체하지 않는다.
- 최신 intake는 7개 repo의 advertised heads 1,246개와 최근 PR metadata 280건을 확인한
  범위다. 모든 branch의 모든 source나 모든 과거 PR 본문을 읽었다는 주장은 하지 않는다.
  다른 대화 검색은 해당 서비스에서 `UNAVAILABLE`이었다. 백업 조회는 알려진 폴더와
  한정된 검색 범위이며, 전역적으로 새 결과가 없다고 결론내리지 않았다. [E02]

## 3. 첫째 루프 — 최적화 코딩 C1–C10

목표는 기존 운동론의 계산식과 초기분포 재정규화를 유지하면서 새 결합 문제를 현재
샌드박스에서 끝낼 수 있게 만드는 것이었다. 준비 비용·반복 계수 계산·Jacobian 평가·
독립 사례 dispatch를 다루었으며, 별도의 성능 벤치마크 캠페인을 열지 않았다.

| 단계 | 실제 수행과 판정 | 근거·남은 범위 |
|---|---|---|
| **C1 목표·baseline** | 고정 REI/C21L/C21N의 계산 경로와 원 source identity를 읽고 수용했다. 기존 계산의 source·정확성 근거는 재사용했다. | [E01, E02, E08]. 기존 81/125/4 ODE 재실행 **NOT_RUN**. |
| **C2 식–데이터–코드** | immutable canonical quadrature와 A 의존 distribution을 구분했다. 새 A마다 packet weight와 energy normalization을 다시 만드는 source 경로를 유지했다. 원자 계수의 z 의존성과 population/ne 의존성을 분리했다. | C21N builder를 고정 재사용; `atomic_network.py`의 exact-z rate/operator cache. 분포의 scalar A만 바꾸는 shortcut은 사용하지 않음. |
| **C3 수치 설계** | canonical grid 재사용, 원자 PI/RR basis 사전 생성, exact-z 한 항목 cache, electron rank-one feedback을 포함한 analytic Jacobian, bounded independent-case dispatch를 선택했다. | z를 반올림하거나 보간하지 않음. `nextafter`로 달라지는 입력은 다른 cache key. 모델 상태에 의존하는 ne는 cache 밖에서 계산. [E04, E05] |
| **C4 실행 DAG·자원** | 현재 affinity·cgroup quota·memory·부하를 읽고 coordinator와 worker를 함께 예산에 넣었다. 최초 격자 4개는 4 workers, 나머지 41개와 controls는 5 workers로 수행했다. | 실제 샌드박스 관측은 quota 8 CPU, memory limit 8 GiB. CPU55 보호, numerical threads=1, task 수 상한·신규 dispatch 재관측·기존 작업 비침범. NCP 64 CPU/128 GB 실측을 주장하지 않음. [E06, E08] |
| **C5 구현** | 기존 prepared-momentum 경로를 재사용하고, `atomic_network.py`, `coupled_model.py`, `resource_control.py`, `run_sandbox.py`에 필요한 최적화·운영 구성을 구현했다. | 후속 이론 계약을 받은 원자 cache/Jacobian의 완성은 셋째 루프와 공유하는 같은 변경이다. 미구현 buffer 최적화·C++ 전환·GPU 가속은 구현했다고 주장하지 않음. |
| **C6 구현 검증** | 원자 6개 focused group, 결합 5개 검사, 운영 2개 negative fixture의 결과를 확보했다. 자원 모듈 9개 fixture PASS는 작성자 근거로 보존했다. | 독립 운영 검토자가 자원 9개 fixture를 다시 실행한 것은 아님. exact-z cached/direct coefficient·operator byte identity를 확인. [E04–E06] |
| **C7 과학 검증** | 같은 현재 전자밀도에서 기존 kinetic RHS와 새 kinetic block을 3개 정적 상태, 120 scalar에 대해 대조했다. packet/radiation 에너지 항등식과 초기 양성분포를 검사했다. | 실제 검사는 `assert_array_equal`의 **exact numerical equality**다. 영수증의 역사적 metric 이름에 `bitwise`가 있지만 별도 raw-byte·signed-zero 검사는 아님. 전체 원 solver paired ODE replay는 **NOT_RUN**. [E05] |
| **C8 수치·재현성** | cache key·고정 계수·소스 SHA·입력·Python/NumPy/SciPy build·출력·receipt를 결속했다. 완료 사례 재사용과 source 변경 거절을 구현했다. | speedup, peak RSS 감소, 64-core scaling은 **NOT_MEASURED**. per-worker 512 MiB는 보수적 planning allowance이며 측정 peak나 강제 quota가 아님. [E06, E08] |
| **C9 독립 검토** | 물리/대수 검토와 runner 운영 검토를 분리했다. 잘못된 completed-case 수용, worker identity 누락, gate 한 번에 여러 dispatch, resume build 비교 누락을 범위가 지정된 수정·검사로 닫았다. | 운영 source는 최종 `99057bdf…`에 결속. 자원 모듈은 작성자 self-review라는 한계를 보존한다. [E06, E07] |
| **C10 판정·인계** | 최적화 구성은 새 결합 계산에 사용 가능하며 실제 51개 실행에서 사용됐다. source·설정·재개 계약을 다음 물리/결합 단계에 인계했다. | 최적화 기능·정확성의 scoped 수용과 성능 향상 측정은 별개다. 외부 content 게시·배송은 현재 남은 마감 단계. |

운영 관측은 독점 CPU 예약이나 강제 memory cap이 아니다. 실제 부하를 새로 확인하고,
cooperative lease가 주어지면 존중하며, 다른 owner의 프로세스·출력을 건드리지 않는
범위에서 사용한다. 프로세스의 보조 thread 수와 numerical-library thread 설정 1을
혼동하지 않는다. [E06]

## 4. 둘째 루프 — 새 물리 이론 R1–R10

질문은 “원 source의 matter/radiation stress 분리를 유지하며, 요청된 light-isotope
전하 population과 전자–Thomson 결합을 $z=20\to2$에서 실제로 풀 수 있는가”였다.
문헌·도식의 전체 범위를 먼저 조사한 뒤, 지금 입력과 계수를 갖춘 조건부 모델을
구성했다. 전체 반응망의 미구현 부분은 typed 상태로 남겼다.

| 단계 | 실제 수행과 판정 | 근거·남은 범위 |
|---|---|---|
| **R1 연구 위치·계약** | 사용자의 새 z2·H/D/T/He3/He4/Li6/Li7 요청과 원 LRS 범위를 고정했다. 로컬 첨부 도식과 project text 01/04/05/07/08을 읽었다. | 첨부를 Library 대체본으로 읽거나 archive/bootstrap을 실행하지 않음. 원 40성분 + 21 populations + optical depth = L8에서 62성분. [E01, E03] |
| **R2 근거·재사용** | SciSpace·Exa를 실제 사용해 원전과 저자 공식 계수 위치를 조사했다. Git 원본으로 확인한 R9 Provider와 공식 입력 6개를 그대로 재사용했다. | Verner PI/RR 채택. Voronov CI, Badnell DR, CX·분자·nuclear 문헌은 범위/후속 판단용이며 해당 rate를 이번 RHS에 넣었다고 주장하지 않음. [E02–E04] |
| **R3 주장·전제 정렬** | 원자/이온 20개 + 자유 중성자 1개, algebraic electron, isotope 전자율 공유, illustrative abundance prior, 등방 trace gas, prescribed UV/T를 명시했다. | “21 ions” 또는 “모든 핵종 완성”으로 표현하지 않는다. n/T 초기 0은 실제 선언 입력이고, missing species의 0 대체가 아님. [E01] |
| **R4 가설·표현 탐색** | 외부 ne donor만 넣는 경로와 현재 전하 state에서 ne를 계산하는 경로를 구분했다. 현재 state→ne→photon Thomson→H→chemistry의 조건부 연결을 선택했다. | 새 온도·UV의 자기일관적 진화 및 모든 nuclear block은 이번 closure 밖의 구체적 후속 문제. 낮은 UV support만으로 전체 핵반응이 없다고 추론하지 않음. [E01, E03] |
| **R5 구성적 유도** | $Y=Dx$, $n_e=n_{H,ref}q^TY$, PI/RR/beta operator RHS, rank-one electron Jacobian, baryon·charge identities, full Frobenius 및 SI 대응, 순간 trace-energy H-shift 식을 유도했다. | 아래 식과 [E01, E03]. $m_i\simeq A_i m_u$ 변환을 선언하며 정확한 isotope atomic mass 사용과 구분. |
| **R6 독립 검증** | Wolfram으로 tensor contraction·shear work·원자/중성자/tritium 보존 identity를 계산했다. 별도 검토자가 원 source와 부호·단위·population·Jacobian 구조를 대조했다. | CAS의 미정 symbolic variable 경고도 원 출력에 보존. CAS는 trajectory 검증이 아님. 물리 독립 review는 `PASS_SCOPED_SOURCE_AND_ALGEBRA`. [E03, E07] |
| **R7 판별 검증** | 보존·양성 generator·경계·LiIV로 가는 비영 graph path·beta bookkeeping·정적 Jacobian 검사로 실행할 모델을 가렸다. 이후 6개 controls에서 solver·L cutoff·Thomson·cancellation의 영향을 분리했다. | 원자 정적 6개 group의 ODE0와 실제 controls 6 ODE를 별도로 센다. LiIV의 초기 정적 Taylor/graph 확인을 cosmological integration으로 부르지 않음. [E04, E08, E09] |
| **R8 결과 판정** | 선택한 conditional closure를 실행 가능한 물리 구성으로 수용했다. UV 최대 150 eV가 지정 MeV photonuclear threshold 아래라는 support 결과를 적용했다. | 이는 해당 photon field의 채널 support 결과이며 full-network 불가능 정리 또는 새로운 strong no-go가 아니다. NG1–NG7을 갖춘 새 no-go 성과는 채택하지 않았다. |
| **R9 정식 결과·코딩 연결** | 물리 계약에 species registry, 단위, 초기조건, source 경계, signed/norm 정의, solver 입력, 에너지 진단과 미채택 channel을 옮겼다. | 실행의 실제 cohorts는 10/20/40/60/100/150 eV. 초기 이론 메모의 아직 구현 전이라는 문장은 그 작성 시점 기록이며 현재 실행 상태는 [E08–E10]으로 갱신된다. |
| **R10 종료·재개** | 조건부 pilot 이론 단위를 코드와 검증에 인계했다. 사용자 요청 중 full reaction/thermal/stellar 역사에 남은 의무를 별도로 식별했다. | 이론 단위의 완료가 전체 요청의 완료를 뜻하지 않는다. 지금은 게시·배송·문서 마감으로 진행하며, 다음 연구는 실제 미완료 물리 입력/closure를 이어간다. |

### 실제 구현으로 전달한 핵심 식

\[
Y=Dx,\qquad n_e=n_{H,ref}\,q^TY,\qquad
\frac{dx}{d\eta}=\frac{D^{-1}}{H_t}
\left[(P+B)Y+n_{H,ref}(q^TY)RY\right],
\]

\[
J_x=\frac{D^{-1}}{H_t}
\left[P+B+n_eR+n_{H,ref}(RY)q^T\right]D.
\]

Geometry와 atomic blocks의 교차 미분에는 $H_t$의 state dependence와 photon opacity의
charge derivative를 포함한다. Proper $n_{H,ref}\propto a^{-3}$는 코드 API에서
cm⁻³이며, 원 energy density는 $c^2$로 나눠 질량밀도로 변환한다. [E01, E05, E07]

\[
S_F=\frac{\sqrt6\,s}{H_t},\qquad
P_X=\frac{\sqrt6(8\pi G/c^2)p_X}{H_t^2},\qquad
\Sigma=|S_F|,\quad\Pi_X=|P_X|.
\]

이는 $\kappa_E=8\pi G/c^4$, $H_{geom}=H_t/c$와 대응한다.

\[
P_r=P_\gamma+P_\nu,\qquad P_{tot}=P_m+P_r,\qquad
\Pi_{tot}=|P_{tot}|.
\]

Tensor는 $\operatorname{diag}(-p_X,-p_X,2p_X)$이며 $\Delta p_X=3p_X$다.
source half-contraction과 full Frobenius 사이의 $\sqrt2$ 인자를 보존했다.
Matter의 비등방 stress는 nonbaryonic massive Vlasov에서 나오며, atomic gas는 등방
trace closure다. 기존 dust에 포함된 baryon rest mass를 다시 더하지 않는다. [E01, E07]

\[
\epsilon_{H^2}=\frac{u_{th}+u_{ion}+u_{UV}}{3c^2H_t^2/(8\pi G)},\qquad
\left.\frac{\Delta H_t}{H_t}\right|_{\text{state fixed}}
=\sqrt{1+\epsilon_{H^2}}-1\le\frac{\epsilon_{H^2}}2.
\]

이 부등식은 순간 상태를 고정한 positive-energy 추가의 대수적 진단이다. 누락 반응의
영향이나 장시간 trajectory error의 상계로 사용하지 않는다. [E01, E10]

## 5. 셋째 루프 — 결합 코딩 C1–C10

| 단계 | 실제 수행과 판정 | 근거·남은 범위 |
|---|---|---|
| **C1 목표·baseline** | 이론 계약을 받아 $z=20\to2$, L8, 45개 독립 초기응력 격자를 정의했다. 비교용 6개 사례를 별도 controls manifest에 넣었다. | signed $(S_0,P_{m,0},P_{r,0})$ 축은 각각 5×3×3. 기존 raw를 새 문제의 계산 결과로 재명명하지 않음. [E01, E08] |
| **C2 식–데이터–코드** | isotope-scaled $x\to Y\to n_e\to\Gamma_T\to\gamma$ moments 경로와 kinetic source를 연결했다. 전자는 별도 ODE가 아니고 optical depth가 마지막 ODE다. | L8 62성분, L12 78성분. 원 unused $u=0$ slot 유지. beta charge 매핑, Li valence branch, 원자 단위 변환 추적. [E01, E04, E05] |
| **C3 수치 설계** | stiffness에 맞춰 analytic-Jacobian BDF, isotope scaling, fixed output times를 채택했다. Newton trial의 finite signed state는 허용하되 출력 물리 population을 검사했다. | clipping·실행 후 abundance renormalization 없음. Radau 한 사례와 L12 두 사례로 남은 구체적 민감도를 확인. [E04, E05, E09] |
| **C4 실행 DAG·자원** | source 검증→초기 certificate→선택 4개→완료 수용 후 나머지 41개→controls 6개→postprocessing 순서로 수행했다. | 실제 completed raw·receipt·COMPLETE seal을 create-only 저장. 초기 4개는 후속 41개 단계에서 다시 적분하지 않음. [E06, E08] |
| **C5 구현** | 21-population atomic network, full kinetic coupling/Jacobian, runner, saved-output validator, CSV/NPZ 및 PNG/PDF 분석을 완성했다. | 실제 반응은 인접 valence PI + Case-A RR와 별도 beta adapter. 현재 n/T 초기 0. CI/DR/CX·분자·핵충돌·UV transport는 `UNMODELED`. [E01, E04] |
| **C6 구현 검증** | 원자 441 Jacobian entries의 complex-step 비교와 62-state 결합 Jacobian 3,782 entries의 central-difference 비교를 수행했다. | 결합 검사는 62×61이다. invariant $u=0$ 열은 음의 trial이 원 source domain을 위반해 제외했다. 최대 scaled difference $7.8866\times10^{-8}$. 새 ODE 없는 정적 검사 범위. [E04, E05] |
| **C7 과학 검증** | 51×201=10,251개 저장 상태의 finite FP64, isotope/baryon/charge·signed/norm/tensor closure·초기값·전자밀도·redshift 대응을 검사했다. | Hamiltonian/massive packet 항목은 source에 결속된 실행 receipt 근거를 재사용. validator는 ODE0/RHS0. Radiation 1,025 μ nodes의 saved-state 검사이며 연속 양성성 정리가 아님. [E09] |
| **C8 수치·재현성** | BDF/Radau 한 쌍, L8/L12 두 쌍, Thomson on/off 한 쌍, 초기 opposing-stress 두 사례를 실제 출력으로 비교했다. 원 source/build/input/time/raw SHA를 유지했다. | 공통 radiation-mode 차이 최대 $2.0780\times10^{-4}$, stress 차이 최대 $8.6329\times10^{-11}$. BDF/Radau atomic 차이 $1.8418\times10^{-9}$, local-scale ratio 858.47. 모두 제한된 진단이며 전체 hierarchy 수렴·global bound 아님. [E09, E10] |
| **C9 독립 검토** | source/대수, runner, saved-output 해석, PNG5 및 PDF2를 서로 구분해 검토했다. Plot v1의 네 결함을 수정하고 v2를 독립적으로 직접 확인했다. | 독립 그림 검토는 출력14개 hash, 좌표45개, endpoint495 scalar equality를 확인. 기존 validator/ODE를 반복하지 않음. resource 모듈 self-review 경계를 보존. [E06, E07, E10, E11] |
| **C10 판정·인계** | 51개 actual return, 조건부 해석, 원본 실패, 최종 분석, source/input identity를 새 content 패키지에 넣을 준비를 마쳤다. | **과학·분석 COMPLETE_SCOPED; publication/backup/document closeout OPEN**. 실제 새 commit·provider ACK·최종 document head가 확보된 뒤 그 영수증으로 닫는다. |

### 수행 결과와 그 의미

45개 격자의 $z=2$ endpoint 최대값은 $\Sigma\simeq0.0319657$,
$\Pi_m\simeq4.05334\times10^{-5}$, $\Pi_r\simeq7.42838\times10^{-4}$,
$\Pi_{tot}\simeq7.82659\times10^{-4}$다. 이는 이 격자의 조건부 결과이며 보편적
상계가 아니다. $P_{m,0}=\pm5\times10^{-4}$, $P_{r,0}=-P_{m,0}$, $S_0=0$의
두 control은 초기 상쇄가 지속되지 않고 shear가 생성됨을 보여 준다. 실제 초기
floating-point offset을 0으로 강제하지 않았다. [E09, E10]

He III의 이른 증가는 처방된 soft cohort의 60 eV 광자가 He II threshold를 넘는 것과
연결된다. Li I의 FLRW 저장점 peak fraction은 약 0.623761이며, 선언된 Li II 초기조건과
UV/T 입력에 대한 응답이다. 이 둘을 관측에서 추론한 cosmic reionization history로
설명하지 않는다. Thomson on/off 차이는 물리 항을 바꾼 모델 비교이므로 solver 오차
측정으로 재해석하지 않는다. [E01, E10, E11]

## 6. 실패·교정·독립성 기록

| 실제 발견 | 분류와 최소 교정 | 원본·후속 근거 |
|---|---|---|
| 원자 v1 column conservation의 절대 tolerance $10^{-10}$ 위반; 관측 잔차 $2.98\times10^{-8}$ | 큰 beta/H column에 대한 FP64 cancellation scale을 반영하지 못한 **검사 기준 오류**. scale-aware roundoff 기준으로 교정했다. 당시 실패를 물리 반응 비보존으로 승격하지 않았다. | `checks/atomic_v1_test_failure/`에 실패 당시 source·test·영수증, [E04]에 후속 PASS. |
| 유효한 hash를 가진 다른 target의 completed receipt 수용 가능성 | **운영 P0**. source/hash뿐 아니라 현재 target과 recorded case의 정확한 일치를 요구하도록 수정. | [E06] OPS01 및 부정 fixture PASS. 과학 결과의 바뀐 target 수용 없이 닫음. |
| worker source identity, dispatch 단위, resume runtime 대조의 누락 | **운영 P1**. 초기화/실행 전후 identity, 한 gate당 한 task, build 비교를 추가. | [E06] OPS02–04. 실행한 negative fixture와 정적 검토만 한 분기를 구분. |
| 운영 negative test의 scientific import stub 누락 | **test harness 오류**. production guard 실행 전 실패했으며 누락된 forbidden-constructor stub을 추가. | [E06]에 최초 실패 코드/로그·수정·후속2개 PASS 보존. |
| Plot v1의 Python `\nu` newline, 겹치는 heatmap 숫자, 약한 S0=0 대비, 큰 common-mode 차이 미표시 | **시각화 결함**. 문자열·주석 배치·색 대비·진단 곡선만 고쳐 v2 생성. | `analysis_v1/`, `checks/PLOT_V1_ANALYZER.py.txt`, `checks/PLOT_V1_REVIEW.json` 보존. [E11]에서 v1/v2 NPZ·CSV2 byte identity와 v2 PNG5/PDF2 직접 검토. |

독립 물리 검토는 source·대수 검토이며, 실행하지 않은 paired ODE를 인증하지 않는다.
독립 운영 검토의 resource 모듈은 작성자 self-review다. Saved-trajectory validator는
실제 raw로 보존·closure를 확인했지만 원 RHS를 다시 계산하거나 ODE를 적분하지 않았다.
독립 그림 검토는 이 validator의 영수증을 읽고 결속했으며, 그 대규모 배열 검사를
자신의 별도 재실행으로 중복 계상하지 않았다. [E06, E07, E09, E11]

## 7. 미수행·미완료의 정확한 경계와 다음 DAG

| 항목 | 현재 상태 | 다음에 필요한 실제 작업 |
|---|---|---|
| 기존 81/125/offgrid4 물리 재실행 | **NOT_RUN_BY_DESIGN** | 기존 source-bound 결과를 계속 재사용. 새 의존성 변화가 없는 반복 실행은 필요 없음. |
| 현재 C21O 51개 NCP 재실행 | **NOT_RUN** | sandbox에서 완료했으므로 마감의 필수 조건이 아님. 새 고유 입력을 실행할 때만 NCP 현재 자원을 새로 확인. |
| 성능 캠페인·64-core scaling·메모리 개선율 | **NOT_MEASURED** | 이번 요청의 추가 완료 조건으로 만들지 않음. 구현상의 계산 재사용과 실측 speedup을 구분. |
| 무한 radiation hierarchy·전체 구간 엄밀 오차 | **NOT_ESTABLISHED** | 두 L cutoff 비교의 실제 차이를 보존. 필요 물리 정확도가 정해지면 해당 의존성만 추가 검증. `global_error_bound=null`. |
| 원 full40와 새62의 paired full-trajectory 동일성 | **NOT_RUN / 서로 다른 물리 문제** | 같은 ne의 정적 RHS 대응 근거만 현재 존재. 다른 closure의 두 ODE를 동일 결과로 주장하지 않음. |
| CI·DR·CX·secondary ionization·Li core/Auger | **UNMODELED** | 각 rate의 온도/전하/에너지 정의역 및 energy/charge bookkeeping을 선택해 새 source 계약으로 구현. 조사된 문헌과 계수 후보 재사용 가능. |
| 분자·음이온·Be7 등 확장 registry | **ABSENT_FROM_THIS_REGISTRY** | species·반응·초기 입력·isotope-specific 근사 범위를 명시해 확장. 단순 0 population으로 대체하지 않음. |
| 첨부 nuclear capture/fusion block·고에너지 photodisintegration | **NOT_IMPLEMENTED_IN_ACTIVE_NETWORK** | 유효 nuclear rates, 고에너지 spectrum이 필요한 경우 cascade, energy ledger와 baryon/charge closure를 연결. 현재 UV support의 threshold 결과만 유지. |
| Self-consistent temperature·stellar sources·UV transfer | **NOT_IMPLEMENTED** | photoheating/cooling·particle-number term·photon production/absorption·중력 source의 에너지 계약을 실제로 결합. |
| 새 content 게시 | **OPEN, 준비 완료** | 현재 source·실행 raw·검사·최종 분석과 실패 근거를 content commit에 결속하고 실제 remote ref 확인. |
| 새 배송 백업 | **OPEN, 준비 중** | 새 create-only archive 및 SHA256 생성 후 provider별 ACK·ID·크기·검증 수준을 실제 응답으로 기록. |
| Document closeout | **OPEN** | 실제 content head·provider 영수증·최종 DAG·다음 인계를 결속. 이전 Drive `UNKNOWN_NO_ACK`와 다른 대화 `UNAVAILABLE` 이력을 유지. |

남은 full-network 작업은 이론적 불가능성 판정이 아니다. 위의 입력·rate·closure를 확보해
구현할 수 있는 구체적 후속 의무다. 이 체크포인트의 즉시 다음 작업은
**publication → backup → document closeout**이며, 후속 사용자 지시와 승인 범위에 따라
다음 실제 미완료 물리 단위로 이어간다. 완료된 계산의 반복이나 무한 검토 루프를
새로운 선행조건으로 추가하지 않는다.

## 8. 근거 색인

- **[E01] 물리 계약:** [PHYSICAL_CONTRACT_KO.md](PHYSICAL_CONTRACT_KO.md).
- **[E02] 외부 근거 수용 범위:** [GitHub intake](intake/github/INTAKE_LEDGER.json),
  [source blob 대조](intake/github/SOURCE_GIT_BLOB_REVIEW.json),
  [백업·다른 대화 조회](intake/backups/SCOPED_INTAKE_RECEIPT.json).
- **[E03] 직접 유도·원전·CAS:** [조건부 이론](theory/CONDITIONAL_NETWORK_THEORY_KO.md),
  [SciSpace/Exa 실제 조회와 source 위치](theory/PRIMARY_SOURCE_RECEIPT_SANITIZED.json),
  [Wolfram 코드·원 출력](theory/WOLFRAM_SYMBOLIC_RECEIPT.json).
  주요 채택 원전은 [Verner et al. photoionization](https://arxiv.org/abs/astro-ph/9601009),
  [Verner–Ferland RR](https://arxiv.org/abs/astro-ph/9509083) 및 저자 공식
  [photo](https://www.pa.uky.edu/~verner/photo.html)/[RR](https://www.pa.uky.edu/~verner/rec.html)
  계수다. Nuclear threshold 범위는 [ACROPOLIS 원논문](https://arxiv.org/html/2011.06518v1)을
  사용했으며 GPL 코드를 vendor하거나 실행하지 않았다. 원 fetch의 긴 저작권 본문은
  게시하지 않고, 정제 영수증·자체 유도·필요 계수만 보존한다.
- **[E04] 원자 source·focused 검증:** [ATOMIC_SOURCE_MANIFEST.json](ATOMIC_SOURCE_MANIFEST.json),
  [ATOMIC_FOCUSED_V2.json](checks/ATOMIC_FOCUSED_V2.json),
  [원자 최초 실패](checks/atomic_v1_test_failure/FAILURE.json).
- **[E05] 결합 정적 검증:** [COUPLED_STATIC_FOCUSED.json](checks/COUPLED_STATIC_FOCUSED.json),
  [실제 검사 코드](tests/test_coupled.py).
- **[E06] 운영 검토:** [INDEPENDENT_OPERATIONS_REVIEW.json](checks/INDEPENDENT_OPERATIONS_REVIEW.json).
- **[E07] 독립 물리·대수 검토:** [INDEPENDENT_PHYSICS_REVIEW.json](checks/INDEPENDENT_PHYSICS_REVIEW.json).
- **[E08] source·입력·실제 실행:** [SOURCE_IDENTITY.json](prepared_v1/SOURCE_IDENTITY.json),
  [초기 certificates](prepared_v1/INITIAL_CERTIFICATES.json),
  [격자 manifest](runs/c21o_grid45_v1/MANIFEST.json),
  [격자 완료](runs/c21o_grid45_v1/SUMMARY_20261021T151056Z_2.json),
  [controls manifest](runs/c21o_controls6_v1/MANIFEST.json),
  [controls 완료](runs/c21o_controls6_v1/SUMMARY_20261021T151234Z_2.json).
- **[E09] 저장 trajectory 검증:** [TRAJECTORY_VALIDATION.json](checks/TRAJECTORY_VALIDATION.json).
- **[E10] 최종 분석:** [SUMMARY.json](analysis_v2/SUMMARY.json),
  [OUTPUT_MANIFEST.json](analysis_v2/OUTPUT_MANIFEST.json).
- **[E11] 독립 그림·PDF 검토:** [INDEPENDENT_PLOT_REVIEW.json](checks/INDEPENDENT_PLOT_REVIEW.json),
  [v1 지적](checks/PLOT_V1_REVIEW.json).

**최종 체크포인트:** `EXECUTION=51/51 COMPLETE_SCOPED | PUBLICATION=CONTENT_PREPARATION |
BACKUP=NEW_DELIVERY_PREPARATION | DAG=publication -> backup -> document closeout`.
