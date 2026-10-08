# R4Z: 공간 적분이 검증된 표본으로 중앙 overlap 미분을 독립 검산

2026-10-02 KST. **별도 R4X 연속 기저 후보의 중앙 미분 항등식에 대한 국소 수치 검산을 통과했다.** D를 입력받지 않는 overlap 표본 미분과 수정하지 않은 \(D(0)+D(0)^\dagger\)를 비교해, 사전에 고정한 두 미세 window·세 공간 적분 규칙에서 모두 10⁻¹²tₐ⁻¹ 절대 기준을 만족했다. 완료 payload는 40개이며, 중단된 3개를 포함한 예약·실행 시도는 43회다. 독립 검토도 `PASS_LOCAL_CENTRAL_CANDIDATE_DERIVATIVE_ONLY`다. G02 전체는 UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO를 유지한다.

## 문제와 고정 입력

R4Y는 같은 후보의 중앙 z=0 공간 적분을 통과시켰다. 그러나 한 위치의 공간 수렴만으로 미분 차분에 쓰이는 이동 표본이나 그 차분 오차가 검증되지는 않는다. 따라서 이번에는 z=0과 ±h 여섯 쌍의 모든 표본에 공간 qualification을 적용하고, 서로 다른 두 미세 차분 window 및 세 공간 적분 규칙으로 얻은 미분을 함께 비교한다.

고정 입력은 b=2a₀, 100keV/u, v=2.00798106651023a₀/tₐ, charge=1인 두 중심과 18채널이다. tₐ=ℏ/Eₕ이며 S는 무차원, D와 Ṡ의 단위는 tₐ⁻¹이다. 정지 target의 위치는 (0,0,0), projectile의 위치는 (2,0,z), 표본 시간은 실제 부동소수점 t=z/v다. requested z와 시간의 hex 표현 및 실제 궤도 위치를 기록한다. R4X 후보 identity는 `17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef`다. 원본 기저의 identity를 바꾸거나 후보를 production bank로 채택하지 않았다.

## 직접 유도와 계산식

직선 궤도와 시간 독립 radial 계수에서 ETF 기저는

\[
\chi_{Ca}(\mathbf r,t)=
e^{i m_e(\mathbf v_C\cdot\mathbf r-v_C^2t/2)/\hbar}
\phi_{Ca}(\mathbf r-\mathbf A_C-\mathbf v_Ct)
\]

다. 고정 lab 점에서 미분하면 공간 이동 항의 부호는 음수이며

\[
\partial_t\chi_C=e^{i\vartheta_C}
\left(-\mathbf v_C\cdot\nabla\phi_C-
\frac{i m_ev_C^2}{2\hbar}\phi_C\right).
\]

연속 조각 polynomial radial 함수는 원점과 외곽에서 u=0이고 zero extension이 H¹에 속한다. 따라서 translation의 L² 강미분과 내적의 곱 미분으로

\[
\dot S_{ab}=\langle\dot\chi_a|\chi_b\rangle+
\langle\chi_a|\dot\chi_b\rangle=(D^\dagger+D)_{ab}
\]

를 얻는다. 이 유도는 함수 trace의 연속성과 경계조건에 의존한다. H¹ 성질만으로 S의 9차 미분이나 8차 수렴 오차 상계가 따라오지 않는다. 같은 중심 S는 정확한 적분에서 시간 독립이지만 원시 수치 원소를 0으로 덮어쓰지 않는다. 자세한 정의·단위·ETF 위상 소거·독립 geometric derivative 유도는 `DERIVATION_KO.md`에 있다. geometric derivative의 별도 적분 구현은 이번 단계의 실행 범위 밖이다.

실제로 사용하는 독립 구성은 overlap S만 입력받는

\[
F(h)=\frac{v}{2h}[S(h)-S(-h)],\qquad
R_8(H)=\frac{-F(H)+84F(H/2)-1344F(H/4)+4096F(H/8)}{2835}
\]

다. 가중치는 계산 전에 유리수 선형계로 고정했다. 계수·차수·window를 D와의 일치에 맞추지 않았으며, 보정계수·재정규화·raw D 투영을 사용하지 않는다. 네 항의 실수부·허수부는 각각 compensated FP64 합으로 누적한다. 가중치 moment는 정확산술로 (1,0,0,0,−1/4096)이며 다항식의 차수 8까지 중앙 미분을 재현한다. R₈이라는 이름은 이 대수적 조합을 가리키며 실제 물리 S의 C⁹ 정칙성이나 인증된 8차 수렴을 뜻하지 않는다.

## 사전에 고정한 판정

h=[0.4,0.2,0.1,0.05,0.025,0.0125]a₀로 총 13개 위치를 사용한다. 각 위치에서 (q40,β24), (q48,β24), (q48,β12)의 세 적분을 계산한다. q는 Gauss 차수, β는 R4Y inner 위상 budget이다. 기존 outer FEM 경계와 반지름 적분 측도, batch1024, full sector, FP64, same-center order20을 유지한다.

공간 검증은 각 위치의 q40→q48과 q48의 β24→β12 비교에서 여섯 raw cross block의 최대 상대 Frobenius 차이≤10⁻⁹를 요구한다. 양쪽 full S/H Hermiticity 상대값≤10⁻¹¹과 metric λmin/λmax≥10⁻⁸도 요구한다. 별도로 z=+0.4, q40,β24의 C++/Python과 Fortran/Fortran raw6개·full3개 배열의 bitwise parity를 확인한다. Hermiticity screen은 reverse block의 analytic conjugacy와 조립 구조를 공유하므로 독립 적분 정확도 증명으로 해석하지 않는다.

R₈ window는 H=0.4,0.2,0.1a₀의 세 개다. 모든 결과를 보존하고, 판정은 세 공간 규칙의 두 미세 window H=0.2와 0.1 모두에서 수행한다. 원시 중앙 D+D†와의 spectral·Frobenius·최대 성분 절대 잔차, 두 미세 window 간 차이, 공간 규칙 간 미분 차이가 모두 10⁻¹²tₐ⁻¹ 이하여야 한다. 중앙 동일 s–s 대각의 exact-zero control도 원시 D로 검사한다.

원래 R₂ `compare_ladder`의 spectral·Frobenius abs/rel 조건과 전체 최대 성분 abs/rel 조건, 두 연속 2차 관측차수 조건을 그대로 보존한다. 첫 네 h 및 전체 여섯 h에 각각 적용한다. 새 R₈ 검산 결과가 기존 R₂ 또는 offcentral 8개 지점의 실패를 PASS로 치환하지 않는다.

## 실제 결과

13개 위치 모두 인접 차수 비교와 별도 β12 probe 비교를 통과했다. 여섯 raw block의 최대 상대 차이는 q40→q48에서 **1.0734092×10⁻¹³**(z=+0.4), β24→β12에서 **6.3603144×10⁻¹⁵**(z=+0.0125)였다. full S/H Hermiticity의 전체 최대 상대값은 각각 5.9842664×10⁻¹⁸, 1.5078949×10⁻¹⁷이고, 최소 metric 비율은 0.72694099였다. z=+0.4의 backend 비교는 raw6개와 full S/H/D의 bitwise equality를 만족했다.

다음은 \(R_8(H)-[D(0)+D(0)^\dagger]\)의 절대 잔차다. 모든 수치의 단위는 tₐ⁻¹이며, 세 norm의 기준은 각각 10⁻¹²다. H=0.4는 보존한 큰 window 진단이고, 채택 여부는 계산 전에 고정한 H=0.2와 0.1의 모든 행으로 결정했다.

| 공간 규칙 | H/a₀ | spectral | Frobenius | 최대 성분 | 판정 |
|---|---:|---:|---:|---:|---|
| q40, β24 | 0.4 | 2.2979588e−12 | 4.6518294e−12 | 1.7641912e−12 | 실패 보존 |
| q40, β24 | 0.2 | 1.3822410e−14 | 3.0332068e−14 | 6.9163425e−15 | 통과 |
| q40, β24 | 0.1 | 8.4002261e−15 | 1.9320208e−14 | 4.5297967e−15 | 통과 |
| q48, β24 | 0.4 | 2.2980761e−12 | 4.6518516e−12 | 1.7642728e−12 | 실패 보존 |
| q48, β24 | 0.2 | 1.2828449e−14 | 3.0490414e−14 | 6.8955258e−15 | 통과 |
| q48, β24 | 0.1 | 1.8411873e−14 | 3.1031892e−14 | 8.4913076e−15 | 통과 |
| q48, β12 | 0.4 | 2.2979655e−12 | 4.6517515e−12 | 1.7642814e−12 | 실패 보존 |
| q48, β12 | 0.2 | 1.0297199e−14 | 2.4945960e−14 | 6.9388939e−15 | 통과 |
| q48, β12 | 0.1 | 1.9744554e−14 | 3.0606149e−14 | 8.9842513e−15 | 통과 |

미세 window 간 차이의 세 규칙 전체 최대값은 spectral 2.6722366×10⁻¹⁴, Frobenius 4.1851155×10⁻¹⁴, 성분 1.2920291×10⁻¹⁴였다. 두 미세 window에서 공간 규칙 간 모든 쌍의 최대값은 각각 **3.7325953×10⁻¹⁴, 5.3045132×10⁻¹⁴, 1.7312673×10⁻¹⁴**다. 중앙 동일 s–s 원시 D 대각 control도 최대 7.2943124×10⁻¹⁶으로 통과했다. 수치가 더 작은 특정 규칙이나 window 하나만 선택한 결론이 아니다.

TT 미분 잔차는 0, PP 최대 성분 잔차는 모든 R₈ window에서 1.6653345×10⁻¹⁵다. PP의 spectral·Frobenius 잔차는 각각 1.9912234×10⁻¹⁵, 2.7372850×10⁻¹⁵다. 저장된 same-center S의 전체 표본 간 변화는 최대 2.2204460×10⁻¹⁶이었다. 이번 중앙 차분에서는 이 값들이 기준을 방해하지 않았으므로 same-center assembly를 사후 수정하지 않았다.

### 원래 R₂ 실패는 별도로 유지

원래 네 h 및 전체 여섯 h에 대한 R₂ 진단은 세 규칙 모두 `RESIDUAL_TARGET_NOT_MET`다. 관측차수는 약 1.980913, 1.995207, 1.998801, 1.999700, 1.999925로 2차 절단오차와 일관되지만, 가장 작은 h=0.0125a₀에서도 허용오차에 도달하지 않았다.

| 가장 작은 R₂ 간격의 규칙 | spectral 절대 | Frobenius 절대 | 최대 성분 절대 | spectral 상대 | 최대 성분 normalized |
|---|---:|---:|---:|---:|---:|
| q40, β24 | 2.8705382e−6 | 5.7417354e−6 | 1.6691560e−6 | 3.6346919e−5 | 1.6653345e−3 |
| q48, β24 | 2.8705382e−6 | 5.7417354e−6 | 1.6691560e−6 | 3.6346919e−5 | 4.9679526e−3 |
| q48, β12 | 2.8705382e−6 | 5.7417354e−6 | 1.6691560e−6 | 3.6346919e−5 | 5.6330588e−3 |

절대 잔차의 단위는 tₐ⁻¹이다. 작은 실제 원소에서는 denominator floor 10⁻¹² 때문에 10⁻¹⁵ 규모의 잔차도 normalized 값으로는 10⁻³ 수준이 될 수 있다. 원래 elementwise 판정은 전체 최대 절대 또는 전체 최대 normalized 조건이며, 원소별로 유리한 조건을 섞지 않았다. R₂의 절단오차가 큰 상태와 고정 R₈ 조합의 국소 통과는 양립한다. 기존 실패를 지우거나 원래 gate를 통과했다고 보고하지 않는다.

## 중단 복구와 계산 비용

2026-10-02 재개 시점에 이전 pilot의 7개와 main의 18개, 총 25개 완료 operator payload가 남아 있었다. 기존 main에는 STARTED만 있고 완료 payload가 없는 3개와 아직 시작하지 않은 12개 task가 남아 있었다. 중단된 3개가 메모리 안에서 어느 내부 단계까지 진행했는지는 확인되지 않는다. 완료 payload·원래 context·예약·로그를 변경하지 않고, 별도 recovery context에서 미완료 15개를 계산해 완료했다. 과거 25개 완료 결과를 hash 검증하여 재사용했고 중복 완료 계산은 0개다. 합계는 **40개 완료 결과, 43회 예약·실행 시도, 3개 과거 중단 기록**이며 전역 cap64 안에 있다. 사용자가 재개를 요청한 뒤 별도로 선언한 수동 복구이고 자동 재시도는 0회다. 완료 결과 수, 예약·시작한 시도 수, 내부 native batch 호출 수를 구분한다.

완료된 pilot의 batch wall time은 37.3329733s, recovery는 73.8944536s다. 확인 가능한 두 batch의 소계는 111.2274269s지만, 중단된 기존 main의 전체 wall time은 종료 기록이 없어 미확정이다. 이 소계를 전체 실행시간이나 speedup으로 해석하지 않는다. 서로 다른 runtime의 파일 수정 시각도 경과시간 측정으로 사용하지 않는다.

실제 계산 환경은 CPU quota8, RAM8GiB이며 최대 3worker×2CPU와 coordinator1CPU를 배정했다. BLAS는 1thread, moment kernel 설정은 2thread, radial Fortran의 관측 team은 1이다. moment ABI는 실제 OpenMP team 크기를 보고하지 않는다. 관측된 최대 worker RSS는 88,988KiB다. OpenMPI 실행이나 NCP64 scaling은 이번 로컬 자료로 주장하지 않는다.

## 검증 상태와 다음 우선 과제

중단 전 새 runner·분석기 테스트 23개가 통과했다. 그 로그를 보존하고 재실행하지 않았다. 복구 시 추가 adapter의 8개 테스트가 통과했으며, 기존 과학 해상도 변경 거부·완료 task 재계산 거부·누락 15개 집합·중복 차단·create-only·byte 변조 탐지·원본 분석기 identity를 검증한다. 합계 31개는 서로 다른 두 시점의 테스트이며 한 번에 재실행한 suite가 아니다. `VALIDATION.json`이 두 실제 로그의 SHA256과 결과를 구분한다.

독립 검토자는 구현 작성에 참여하지 않았고 새 물리 호출을 하지 않았다. 원래 72개와 복구 73개 source pin, 11개 input pin, 40개 raw/full payload와 예약 기록을 검토했다. 저장 S만으로 재귀 Richardson 표를 별도로 계산하여 가중치 합과 비교했으며, 전체 최대 spectral 차이는 **2.6690201×10⁻¹⁷**이었다. 3531개 검토 조건과 925개 수치 비교를 수행하고 공간 판정·두 미세 window·원래 R₂ 진단·복구 횟수·경로 identity를 확인했다. 구현 blocker는 없었고 최종 판정은 `PASS_LOCAL_CENTRAL_CANDIDATE_DERIVATIVE_ONLY`다.

실행 context는 원래 `81f8caeb79a366ae88f1309a59aa6ebd92d68f51f176debcbcf33d89ff1d0d23`, 복구 `b26ff8ee6915b551aea66af0bb4e71a3c697534b6dc4cd101a9b314c140cedf3`의 SHA256으로 구분한다. `RECOVERY_BINDING.json`은 이전 완료 결과와 새 실행의 관계를 고정한다. 원래 과학 계약 및 미분 분석 함수는 변경하지 않았고, adapter는 collection·복구 결합·보고 의미만 확장했다. 기존 main을 완료된 batch로 위조하지 않았다. `RUN_STATE.json`은 중단 전 상태로 보존하며 최종 상태는 새 `FINAL_STATE.json`을 따른다.

`DERIVATIVE_RESULT.json` SHA256은 `80e700282d23636e960213e91f2c13d7aae749b4c120cbbbd45b36ae9938a841`, 독립 검토 SHA256은 `fed6dfb717cd06e12b3b5203101f739b391ca4f13a94e7c89563ea6d771f0236`이다. DBv12에는 이 근거와 테스트·복구 기록 7개 및 국소 상태 overlay 1개를 추가했다. DBv11의 46개 table/3309개 과거 row(시스템 `sqlite_sequence` 포함), 과거 view 및 G02 이외 상태를 보존했으며 integrity check와 foreign-key check를 통과했다. 실제 검증 결과는 `DB12_VALIDATION.json`에 있다. DBv12 크기는 8,179,712byte, SHA256은 `7f673e631282992a52812d02bbcaea4dec874900e9af3a859f8b8f91c7ac7291`이다.

이번에 닫힌 범위는 **별도 후보의 중앙점에서 공간 검증된 S-only 미분과 raw D+D†의 국소 수치 일치**다. 원래 8개 offcentral 미분 gate, same-center order20의 독립 refinement, 기저 전역 채택, 전 궤도 certificate 및 capture는 미해결 또는 미실행 상태다. H¹ 항등식의 유도, 다항식 가중치의 정확산술, 실제 수치 관측, 구현 검증을 구분하며 관측 차이를 인증 오차 상계로 바꾸지 않는다.

다음 우선 과제는 **z=−32a₀ 한 점의 offcentral 미분 pilot**이다. shell 접촉 기하와 1/h 오차 증폭을 반영해 간격을 먼저 정하고 모든 S 표본의 공간 qualification과 독립 미분 비교를 수행한 뒤 원래 8점으로 확장할지 판단한다. 작은 h를 무작정 줄이거나 same-center 코드를 선제 변경하지 않는다. 이번 중앙 계약의 완료 후 추가 물리 계산은 수행하지 않았다. 게시·DB·백업 identity는 별도 delivery receipt를 따른다.
