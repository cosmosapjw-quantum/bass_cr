# N5 제한된 H1/He4 전자–이온 에너지 교환: 새 이론·코딩 루프

## 1. 이번 단위와 현재 판정

단위는 **CR_N5_EI_MAXWELLIAN_ENERGY_EXCHANGE**, 소비자는 **N5_C23D_H1_HE4_EI_ENERGY_V1**이다. 기존 PR102의 저장된 EE+첫 충돌 들뜸(CE) 배열을 그대로 소비하여, H1+, He4+, He4++의 유한 질량 Maxwell bath 에너지 교환과 새 결합 연산자를 구현했다.

실제 C6 controls 25개, C7 새 결합행렬 8개/96 RHS, C8 격자·상단경계 비교 18개와 **독립 C9가 모두 통과**했다. Root는 **NUMERICALLY_CHECKED_SCOPED_CONDITIONAL_EI_FINITE_CHAIN**을 채택했다. 독립 검토와 판정의 권위는 **review/C9_REVIEW.json 및 CLAIM_GATE.json**이다. 이 문서의 수치는 저장된 새 원자료에서 읽은 결과이며, 전체 N4/N5 또는 열화학 network의 완료를 뜻하지 않는다.

이론의 신규성은 표준 Rosenbluth/Landau 계수, Maxwell 가역성, MFPT, resolvent 정리가 아니다. 새 성과는 기존 source·입력·질량 조건에 결속한 EI 계수, 저장 격자에 대한 새 결합 소비자, 원자별·source 평균 수치와 검증된 제한된 비교다. Strong no-go NG1–NG7은 NOT_APPLICABLE이다.

## 2. 전수 조사와 재사용의 실제 범위

09:11:30–09:11:56 UTC(18:11 KST) 조사에서 관련7repo의 branch/open-PR14collection을29page 끝까지 열거했다. **1329branches / 863openPR**, ownerrepo목록51개와 끝 offset의 빈 결과를 확인했다. 7repo 밖 모든 branch 본문을 읽었다는 뜻은 아니다. 이 수치는 새 PR103 생성 전 snapshot이다.

| Repo | Branches | Open PR |
|---|---:|---:|
| bass |272|157|
| bass_cr |180|101|
| BASS_HE |102|97|
| WU088_HH |153|144|
| rec_bianchi |151|99|
| rei_bianchi |266|210|
| vigilode |205|55|

09:11:53–09:17:08 UTC의 백업 조사에서는12576개 중복 제거 metadata(Library3775, Dropbox5654, Drive3147),64개 실제 읽기 응답을 얻었다. Library/BASS와 지정 Dropbox 경로는 pagination 끝을 확인했다. Drive HE/dossier 직접 목록은1000개 상한에 걸렸고, 문서 MIME926개 별도 pagination은 ZIP/JSON 전체를 포괄하지 않는다. 따라서 Drive 계정 전체 전수 조사를 주장하지 않는다.

다른 대화 전문은 실제 Personal Context 응답상 **UNAVAILABLE**이다. Daily status PDF10쪽, GRID044 상태/계약, VigilODE ACK 등 접근 가능한 파일 증거를 읽었다. 외부 NCP runtime/lease는 UNOBSERVED다.

11:49:37 UTC(20:49:37 KST) 실행 전 freshness에서는7repo의 최신 openPR10개씩70개 metadata, 변경된12개 고정 source body를 다시 확인했다.12/12 Git blob identity PASS이며, 이전 창 이후 신규 openPR5개가 관측됐다. 이것은 앞선29page 전수 census의 재실행이 아닌 별도 한정 refresh다.

| Owner | 최신 관측과 실제 의미 | EI/N5에 대한 처리 |
|---|---|---|
| WU141 PHYS84 |d5c2c8d…; NUMERICAL_ADMISSION_WAIT|수치 provider로 승격하지 않음|
| WU143 PHYS86 |f4a6d550…; exact reference1099/1099, physical rate는null|참조/의미 조건 재사용|
| WU144 PHYS87 |496670cf… FINAL; finite-window neutron-capture scopedPASS|전자 stopping으로 전용하지 않음|
| WU145 PHYS88 |0528ca63… S0; atomic-to-bare remap activeowner, numeric0|중복 구현하지 않음|
| HE98 |d477aafc… D; TDCS413 shape13점 scopedPASS, PWBE C8 additive closeout|HE-ANG physical SOURCE_INPUT_PENDING 유지|
| REC134 |ccf2bd08… D; represented314×313 response scopedPASS|physical epsilon null/HOLD 유지|
| BASS187 |0a088e1f…; REC35×26 packet bridge|finite absorption/energy-owner 후속 분리|
| VigilODE85 |1c829f20…; native quotaHOLD|독립 owner·runtime 경계 유지|
| Central |3423209a… at11:49; stock/work scoped실행과HE/WUreturn 추가|원40contracts/7authorities/17edges와 병렬 결과 보존|

고정 source 목록과 전체 SHA는 intake/provider_public, intake/freshness_public 및 백업 intake에 있다. 새 완료 EI provider 충돌은 관측되지 않았다.

## 3. 물리 입력과 닫힘 가정

기존 C23D 고정 입력을 유지한다.

- Te=10000K, theta=0.8617333262145178eV, thermal ne=0.14cm^-3.
- prescribed lnLambda_ee=lnLambda_ei=20.
- HI/HII/HeI/HeII/HeIII 밀도=0.9/0.1/0.07/0.02/0.01cm^-3.
- source z=2.316,2.479,2.649마다384개, 총1152개 저장 원자.
- 초기0<W<10eV, exposure10000proper s로 정의한 impulsive population.
- closed box/no escape. Exposure는 연속 photoionization chemistry 적분 시간이 아니다.

이번 추가 조건은 **HII를H1+, HeII/HeIII를He4+/He4++로 해석하고, 세 이온 모두 Ti=Te인 정지·등방 Maxwellian bath로 두는 것**이다. 기존 source는 원소별 밀도였으며 isotope abundance를 공급하지 않았다. D/T/He3/Li6/Li7의 실제 기여는 null이다.

질량비는 H1+1836.152673426, He4++7294.29954171, He4+7295.29954171이다. 앞의 두 값은 [NIST2022 CODATA primary table](https://physics.nist.gov/cuu/Constants/Table/allascii.txt)에 결속하며, He4+는 alpha+전자1개의 관성질량 근사로 binding mass defect를 생략했다. 기존 EE anchor b(theta)=2.3306698113646996e-5eV/s를 새 상수로 다시 계산하지 않았다.

고전적·비상대론적·약결합 leading-log test-electron 모형이다. 이온은 순전하 point Coulomb scatterer로 취급하며, 이온 내부 들뜸·이온화·반동 상태분포·charge conversion·온도 feedback을 이번에 추가하지 않았다. Maxwell bath와 continuum 유효성의 물리모형 오차는 null이다.

## 4. 구성적 이론과 단위

r_b=M_b/m_e, eta_b=(n_b Z_b^2/ne)(lnLambda_eb/lnLambda_ee), x_b=r_b E/theta_b라 두고,

\[
A(x)=P(3/2,x)=\operatorname{erf}\sqrt{x}
-\frac{2\sqrt{x}e^{-x}}{\sqrt{\pi}},
\quad
A'(x)=\frac{2\sqrt{x}e^{-x}}{\sqrt{\pi}}
\]

를 사용한다. b_b(E)=b_ee(E)eta_b=C_b/sqrt(E)이면,

\[
D_b(E)=\frac{\theta_b b_b(E)}{r_b}A(x_b),\qquad
\mu_b(E)=b_b(E)\left[A'(x_b)-\frac{A(x_b)}{r_b}\right],
\qquad
\operatorname{Var}(dE)=2D_b\,dt.
\]

mu는eV/s, D는eV^2/s이다. 에너지 drift는 velocity friction만으로 얻지 않는다. Rosenbluth velocity drift와 전체 Hessian covariance에 Ito 변환을 적용하면 perpendicular diffusion의 평균 에너지 기여가 포함되고 위 질량 인자가 얻어진다. R6는 reduced-mass Rutherford impact-parameter 유도, Maxwell potential 및 Ito trace를 독립 방법으로 확인했다. 상세 계산은 THEORY_KO.md와 review/THEORY_R6_KO.md에 있다.

공통 온도에서는

\[
\mu_b=D_b'+D_b\left(\frac1{2E}-\frac1\theta\right),\qquad
p_\theta(E)\propto\sqrt{E}e^{-E/\theta}
\]

가 성립한다. 따라서 각 bath와 합성 연산자는 같은 Maxwell 가중치를 갖는다. r=1은 기존 PR59 EE 계수로 환원되고, 큰r에서 고정E의 에너지 교환은1/r로 작아진다. 이것이 angular scattering까지 사라진다는 뜻은 아니다.

정규화된 Maxwell test population theta_t의 평균 drift는

\[
\langle\mu_b\rangle
=\frac{2C_b(\theta_b-\theta_t)}
{\sqrt{\pi}r_b(\theta_t+\theta_b/r_b)^{3/2}}
\]

이다. 같은 온도에서는 개별 전자의 drift가 비영이어도 ensemble 평균은0이며, 그 양쪽에서는 온도 차에 맞는 교환 부호를 준다. 실제 C6의3계수검증 적분은9구간 호출로 이 식을 확인했다. 이는 새로운 source quadrature나 physical thermal-rate database 계산이 아니다.

Wolfram의 context 호출은 Internalerror였고 첫 evaluator는20초 timeout이었다. 이를 보존한 뒤 한정 retry에서 equilibrium defect0, A derivative defect0, small-x series를 얻었다. 확인되지 않은 CAS heavy-mass limit을 PASS로 기록하지 않았다. SciSpace/Exa의 intake도 사용했으며 original Rosenbluth PDF image는 읽지 못했다. 이 한계는 독립 계산과 원전의 서지 확인을 구분하여 남겼다.

## 5. 저장 격자의 새 소비자와 에너지 소유권

PR102 v3의8개 native-knot NPZ를 그대로 읽었다. chi=1.5,3; R=40,80; nominal N=1024,2048이며 finest 실제 node 수는2480이다. 원 EE generator, CE hazards, source projection, pi, conductance 및 baseline해를 재생성하지 않았다.

각 edge midpoint에서

\[
c_b=c_{ee}\frac{\eta_b}{r_b}
 \frac{A(r_b E_m/\theta)}{A(E_m/\theta)}
\]

를 계산해 새 ion generator24개와 합성 generator8개를 만들었다. 통상 primary matrix_count8은 **합성 행렬 수**다. 공통pi에 대한 양방향 flux로 상세평형을 유지한다.

q=chi theta를 absorbing first-entry 경계, U=R theta를 reflecting 상단으로 두고, G=Q_tot[1:,1:]^T, K=diag(h_2S+h_2P)-G를 구성했다. 첫6RHS는 CE확률2개·entry확률·정지시간·CE전 에너지모멘트2개, 다음2RHS는 CE시간모멘트, 마지막4RHS는 EE/H1+/He4+/He4++의 signed bath reward다.8case×12RHS=96이다.

각 bath의 gain은 같은 전자의 에너지 drift에 반대 부호를 취한 하나의 소유권이다. 별도의 stopping heat를 더하지 않았다. q로의 edge는 에너지q를 갖는 항으로 포함한다. source중 원래W<=q인 원자는 자기 원래 운동에너지를 terminal 값으로 유지하고, 원래active이지만 projection으로q에 놓인 질량은 따로 센다.

활성 상태의 에너지 장부는

\[
\sum_bH_b+q\,u_{\rm entry}
+\bigl(r_{\rm CE}-\Delta u_{\rm CE}\bigr)
+\Delta u_{\rm CE}=E
\]

이다. CE 내부에너지 Delta u_CE는 최종 gas heat로 합치지 않는다. 첫 CE에서 진단을 중단한다고 전자가 물리적으로 제거되는 것도 아니다. 첫 진입은 irreversible assimilation 또는 Maxwellization이 아니다.

전하·핵종 incidence는 이 elastic 채널에서 각각0이다. 이 leading-log diffusion 표현에 임의의 유한 collision event hazard를 부여하지 않는다. event count/hazard는 null이며, 에너지 계수와는 다른 양이다.

## 6. 새 결과

아래는 N2048,R80의 결과다. P_CE는 원래W>q인 **active population**에 대해 정규화했다. Ion gain은 **선택된 전체 source 전자당**, T_entry는 CE를 제거한 paired first-entry 평균이다.

| chi | z | P_CE(active) | Ion gain(eV/selected e) | T_entry(s) | EE 대비 T 변화 | EE+CE 대비 P_CE 변화 |
|---:|---:|---:|---:|---:|---:|---:|
|1.5|2.316|2.283240913e-5|8.784501148e-4|281907.563|-0.0510845%|-0.0447802%|
|1.5|2.479|2.261476513e-5|8.781799756e-4|281546.195|-0.0510953%|-0.0447814%|
|1.5|2.649|2.237786342e-5|8.786699717e-4|281347.313|-0.0511042%|-0.0447827%|
|3|2.316|3.471078746e-5|4.804842244e-4|271384.578|-0.0461653%|-0.0447242%|
|3|2.479|3.434638161e-5|4.798024125e-4|270490.447|-0.0461691%|-0.0447247%|
|3|2.649|3.393421302e-5|4.796499263e-4|269651.320|-0.0461729%|-0.0447254%|

q는 각각1.2925999893eV와2.5851999786eV다. U=80theta=68.9386660972eV이며 초기10eV선택은 경로의 상한이 아니다. 따라서 초기 W가 H 들뜸 gap10.20435eV 아래라도 EE diffusion으로 상향 이동한 뒤 첫 CE가 발생할 수 있다.

선택된 EI가 만드는 first-entry 평균의 단축은 chi1.5에서약143.85–144.08s, chi3에서약124.56–125.34s다. CE확률의 약0.0447% 감소는 이 저장 source/유한 격자의 실제 관측이다. 모든 가능한 CE경로에서 항상 단조 감소한다는 새 정리로 확대하지 않는다.

### 에너지 영역을 나누어 해석해야 한다

고정q이상에서는 D_EI/D_ee가

\[
\delta_{\max}=
\frac{\sum_b\eta_b/r_b}{A(\chi)}
\]

이하이다. chi1.5에서는0.0007359998333, chi3에서는0.0005040172473이다. 저장 finite-chain의 양의 conductance MFPT 공식으로

\[
\frac{T_{ee}}{1+\delta_{\max}}\le T_{ee+ei}\le T_{ee}
\]

를 얻으며, 모든 실제 state/source mean이 이 범위를 만족했다. 이 비교는 동일한pi, q, 상단반사 조건에 한정된다.

반면 **모든 초기저에너지 source에서 EI/EE가 같은 작은 비율이라고 말할 수는 없다**. 저장 source의 최소W는0.00313079184eV이고, 원자별D_EI/D_ee는 약0.0004477802–2.7146623이다. 매우 낮은 에너지에서는 이온 열속도 규모가 중요하다. 이번 source에서 EI가 초기에 전자에 에너지를 주는 count fraction은0.287812–0.290041%이며, 전체 선택 population의 초기 순 ion bath power는 양수이다. 기존 EE의 초기 heating fraction약24.85%와 다른 값이다.

| z | <mu_EI>(eV/s) | <D_EI>(eV^2/s) | 초기 pulse ion gain rate(eV cm^-3 s^-1) | EI heating count fraction |
|---:|---:|---:|---:|---:|
|2.316|-7.129421666e-9|8.649200483e-9|7.335118190e-17|0.2878122%|
|2.479|-7.123884254e-9|8.653588460e-9|7.232404796e-17|0.2888322%|
|2.649|-7.115455469e-9|8.657179444e-9|7.044519589e-17|0.2900407%|

이 순간 power에 exposure10000s를 다시 곱해 이번 source의 최종 전달 heat라고 해석하지 않았다. 최종 first-stop reward는 별도 resolvent에서 구했다. source 평균에서 signed drift와norm, cancellation을 구분한다.

## 7. 검증과 수용 범위

| Gate | 최대 관측값 | 고정 허용 |
|---|---:|---:|
| Q column scaled defect |9.77028e-17|2e-13|
| edge detailed balance |2.95967e-16|2e-13|
| 선형 backward scaled residual |5.96309e-13|2e-12|
| 확률 partition 절대오차 |4.59686e-11|2e-8|
| state 에너지 장부 scaled residual |2.16847e-11|2e-8|
| MFPT backward scaled residual |1.78456e-16|2e-12|
| grid N1024→2048, 5관측량 최대 상대변화 |1.14390e-4|5e-3|
| EI-induced CE change의 grid 상대차 |1.84708e-7|1e-2 및 절대floor|
| finest R40→80, 5관측량 최대 상대변화 |6.41338e-11|1e-5|
| EI-induced CE change의 상단 절대차 |3.52085e-11|1e-7|

MFPT flux-difference 진단값1.30874e-10은 frozen backward residual과 분모가 다른 보조량이다. 실행 전 명시한 대로 gate를 바꾸지 않았다. 실제25controls는 r1일치, 밀도/Z^2배율, null거부와 명시적zero구분, 단위/frame/clock오류거부, small-x, heavy-mass, Maxwell평형, thermalmean부호 등을 포함한다.

독립 C9는 생산 모듈을 import하지 않고 80자리 계수 55쌍, finest 두 행렬의 24 RHS를 계산했다. 최대 계수 차이는 3.329476627935646e-15, 확률·signed reward 해 비교 차이는 2.983316599388798e-11로 고정 기준 5e-10보다 작다. 24 RHS는 물리적 확률/시간/reward 16개와 signed reward의 절댓값 경계를 확인하는 8개다. Exact decimal 전하합, 원시 edge drift와 행렬/RHS 조립, source 에너지 장부 6행 및 실제 PNG도 확인했다. Blocking finding은 0이다.

C9 첫 시도는 완료된 plot의 lease가 남아 있어 child 시작 전에 거부되었다. 소유자가 완료 영수증과 실제 프로세스를 대조하고 원 lease를 보존한 뒤 정리했다. 두 번째 시도는 mpmath 미설치로 수치 계산 전에 종료됐다. 세 번째는 이미 존재하는 mpmath1.3.0 wheel을 정확한 SHA/CRC와 함께 복사하고 zipimport로 연결하여 같은 oracle을 실행했다. 패키지를 설치하거나 생산 계산을 반복하지 않았다. 두 실패와 비용도 그대로 남아 있다.

이 검증은 주어진 유한 chain의 계산적 일관성과 두 격자·두 상단 비교를 확인한다. continuum 전체오차, 실제 플라즈마 모형오차, 전체 network오차를 상계하지 않으므로 global_error_bound=null이다.

저장 결과만으로 만든 [4패널그림](runs/n5_ei_energy_saved_plot_20261024_v1/EI_ENERGY_DIAGNOSTICS.png)을 executor와root가 실제 열어 보았다. Signed drift·EI/EE확산비·정지 전 ion reward·CE/first-entry효과가 각기 표기되어 있다. 과학 계산을 그림 때문에 다시 실행하지 않았다.

## 8. 실제 실행량과 예산

- 새 primary:8합성행렬,96RHS,24source결과.
- 새 per-ion coefficient pair: source3456, edge43578, 그림1200; 그림용 EE400은 따로 센다.
- C6 coefficient-mean validation적분3회/9구간.
- source quadrature0, physical thermal-rate provider quadrature0, 새ODE0.
- oldgenerator/sourceprojection/primarysuite replay0.
- C23D의 역사적 실제ODE4와 원new_ODE:0 RESULT_CLARIFICATION은 그대로 보존한다.

Controls 0.769915, primary 0.638919, saved-plot 2.476255 CPU s로 생산실행 합계는 3.885089 CPU s다. C9는 prechild 거부 0, dependency startup 실패 0.030482, 실제 성공 1.124207 CPU s로 합계 1.154689 CPU s다. **이번 worker 합계는 5.039778 CPU s, 상속 24.830244114를 포함한 알려진 lineage는 29.870022114 CPU s**다. 60 CPU s의 이번 단위 상한에서 54.960222 CPU s가 사용되지 않았으며, 이 잔여량은 다른 campaign의 새 승인으로 사용하지 않는다.

Coordinator는 생산 0.018076813와 C9 0.009590821, 합계 0.027667634 CPU s로 별도다. Mechanical survey/recovery/packaging의 측정 표본과 측정하지 않은 model/tool/IO 비용도 분리한다. Global spend/remaining/currency는 null이며, 전체 mechanical CPU를 알려진 worker 합계와 혼동하지 않는다. 권위는 BUDGET_CONTINUITY.json과 뒤에 추가되는 delivery 비용 영수증이다.

실제 호스트 CPU0–8/quota8, memory8GiB를 확인했고 worker CPU0/reviewer CPU1/coordinator CPU8, native thread1, 각 worker 512MiB와 고정 CPU/wall 상한을 적용했다. CPU55는 없으며 다른 자원으로 대체하지 않았다. 외부 NCP runtime/lease는 UNOBSERVED다.

## 9. 중단 복원과 원자료 보존

S0 게시 뒤 과학 실행 전에 임시공간이 소실된 것을 확인했다. 원인은 UNOBSERVED다. Git 고정 S0의 53개 파일을 실제 읽어 복원했고, PR102 canonical의 actual-byte size/SHA/CRC/all250payload 검증 후 8 NPZ와 3 CSV를 복원했다. Local apply_patch가 CRLF를 LF로 바꾼 3 CSV는 최초 불일치/격리본을 보존하고 원 bytes로 수정했다. 최종 S0 전체 53/53와 입력 manifest 23/23 PASS다. **게시된 S0 Git 원본은 변하지 않았으며 과학복원 replay0**이다.

백업조사 64개 raw 응답과 root 9개 cached tool-response object를 복원했다. 이전 provider 29 raw page/22 source body와 theory private 17 files는 private cache에서 복구하지 못했다. 그 snapshot의 공개 요약과 identity는 S0에 남아 있고, 복구불가 영수증과 새 freshness를 구분해 보존했다. 새로운 조회로 잃은 과거 snapshot을 대체하지 않았다.

첫 checkpoint 동결은 병렬쓰기 stat 변화를 검출해 FAILED_RETAINED/upload0이었다. 이후 안정된 S0 checkpoint와 실행 checkpoint는 각각 Library/Dropbox 실제 R1 ACK를 받았다. 이 중간 ACK는 R3가 아니다. 최종 canonical 및 terminal의 실제 R3/Drive 상태는 delivery/BACKUP_RECEIPTS.json과 최종 authority를 따른다.

## 10. 남은 DAG와 다음 첫 노드

이번 EI 완료가 허용하는 변경은 N5의 세 조건부 질량/전하에 대한 새 child뿐이다. 과거 168-cell coverage 표를 완료표로 덮어쓰지 않는다.

| 항목 | 현재 채운 범위 | 남은 의존 |
|---|---|---|
| EE |PR59/C23D/PR102저장자료재사용|전체stopping및finitebath/coupling범위분리|
| EI |H1+,He4+,He4++;10000K,lnLambda20,정지Maxwell,leadinglog|다른isotope/밀도/T,내부상태,모형오차null|
| H bound-bound CE |기존2S/2P first-event소비자에EI추가|반복CE·radiative처리·다른종/charge|
| CI |이전source/gap-tail조건유지|secondary-energy및필요domain|
| RR |기존조건부H/D43pair재사용|state/energy/Milne/광자소유자결속|
| DR |실제누락값null|partially-strippedHe/Li provider|
| CX |기존조건부D43K pair재사용|missingpartner·productstate/recoil/radiation|
| Neutral elastic |누락값null|저에너지momentum-transfer/에너지법칙|

질량에 의존하는 A(rE/theta)/r 때문에 같은 전하나 원소 label만으로 동위원소를 합치지 않는다. 기존 quotient 조건 PQ=QbarP, c^T=cbar^T P와 목표 정확도를 적용해야 한다. Dominant omitted-process ranking은 비교에 필요한 rate가 없어 null이다.

**다음 첫 노드는 CR_N5_ATOMIC_ISOTOPE_COVERAGE이다.** 다음 단위는 current owner return과 neutral elastic/CI/RR/DR/CX의 종·전하·온도·에너지 domain을 연결한 뒤 선택한다. 실제 부족 공급자와 고유 energy owner가 확인되어야 N6를 열 수 있다. N7은 N6 이후이다.

CR_N4_STOPPING_KERNEL, CR_N5_ATOMIC_ISOTOPE_COVERAGE는 PARTIAL/OPEN이다. N6/N7은 PREDECESSOR_GATED이며 새 parcel/cosmological ODE0이다. Non-tilted LRS/full Frobenius, signed amplitude/norm/cancellation, atomic isotropic gas와 nonbaryonic Vlasov stress의 구분을 유지한다. Full high-energy nuclear 및 general triaxial/tilted/polarized CMB는 HOLD, 원 nuclear PNG는 NOT_RECOVERED_NOT_READ다. global_completion_percent=null이다.

