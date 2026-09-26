# TP2A 적대적 재감사: 해석적 축약과 물리적 pruning

## 결론과 범위

반복 실패를 하나의 새로운 물리 오류로 묶지 않는다. 제공된 데이터에서 수렴 blocker의 공통 원인은 ETF를 포함한 실제 거리 적분의 해상도와, 그 geometry-dependent 오차의 시간차분 증폭이다. 낮은 적분 차수의 이름, 작은 Hermiticity defect, metric positivity, 또는 Sdot=D+D† 하나만으로 raw S/H/D 정확도를 증명할 수 없었다. 기존 FEM 약한 형태 자체의 무효화나 GIL을 과학적 실패의 원인으로 볼 증거는 없다.

이번에는 직전의 전체 HP runner를 실행하지 않았다. 검증된 h/p 거리 규칙은 유지하되 불필요한 각도 기저 평가를 해석적으로 제거하고, 정확한 반사 대칭으로 허용되는 부분공간만 계산하는 backend를 새로 구현했다. 같은 모형과 같은 거리 노드에서 원래 비축약 계산에 대한 수치 일치와 실제 속도 개선을 확인했다. 개선은 현재 s+p 및 고정 collision-plane/even-initial-state 조건에 한정된다. 전체 양의 z, 새로운 full transport, basis completeness, 원래 GPU의 약3% capture 차이는 이번 결과로 닫히지 않는다.

## 입력 권위와 복구

- 원격 source anchor: fa5903a54c57326c12d7f60cb2444c68a8eb2392.
- 물리 basis: 이전 제공된 BASIS.npz, SHA256 172303585e254e6ad3ea7543fe0c1e695bd9364dc60040fad49c99b06ee84abe.
- 최신 사용자48-task raw payload는 받지 않았다. 여기서는 제공된 기존 계수 bytes와 저장 행렬을 사용한 별도-host 재현 및 비교다.
- 핵심 scientific dependency15개 hash를 확인했다. 이는 전체 GitHub 저장소의 모든 과거파일/commit 전수감사라는 뜻이 아니다.
- 이전 분석 scratch가 남지 않은 부분은 archive에서 복원했다. 사라진 실행의 시험통과를 현재 증거로 상속하지 않고, 새 구현·시험·실험을 실행했다.

INPUT_INVENTORY.json, evidence/E0_DEPENDENCY_CHECK.json, PLAN.json, EVIDENCE_LOG.md에 근거와 탐색 범위를 기록했다.

## 적대적 판정

### 1. 버리면 안 되는 물리

finite-element radial eigenvalue는 자신의 weak test space에서 성립하는 Ritz 관계다. 다른 중심에서 번역한 상태에 대해 cross kinetic을 단순 E*S로 바꾸면 interface/outer-support residual을 무시할 수 있다. 이를 채택하지 않았다. Positive pseudostate도 작은 에너지나 추정 점유로 삭제하지 않았다. D는 직접 fixed-lab derivative로 계산하고, Sdot에 맞춰 재구성하지 않았다.

### 2. 제거해도 되는 계산

s+p에서 f=A(r)(q0+q·x), grad f=A q+B(q0+q·x)x다. xT·xP=(rT²+rP²-R²)/2를 먼저 사용하면 S와 비부스트 kinetic의 각도차수는2, ETF를 포함한 H,D도3이다. Wolfram으로 다항식 항등식과 차수를 확인했다. 기존 9-ring-node 표현은 충분한 상한이었지만 불필요하게 큰 중간배열과 기저 평가를 요구했다.

남는 방위각 적분은 J0,J1,J2,J3로 표현되는 여섯 moment로 닫힌다. 따라서 phi 점별 기저·gradient·D 배열을 생성하지 않고, bilinear/trilinear form을 C++에서 직접 축약한다. 복소 구면조화 기저의 완전한 p multiplet을 실수 Cartesian 기저로 unitary 변환해 복소 연산도 줄이고, 출력은 원래 기저로 되돌린다. 적분용 움직이는 frame을 물리적 상태 기저의 회전으로 혼동하지 않으며 Udot를 누락하지 않는다.

S_PT와 H_PT는 정확한 conjugacy로 복원한다. 이는 사후 평균이나 임의 대칭화가 아니지만, 이 구현의 Hermiticity는 독립 정확도 증거도 아니다. 그래서 원래 양방향을 독립 계산한 raw6 block과 비교했다. D의 두 방향은 각각 직접 계산한다.

### 3. 정확한 상태공간 pruning

고정 xz collision plane 및 vy=0에서 reflection y→-y가 S,H,D를 보존한다. 완전한 p multiplet의 p_y 네 채널은 odd이고 나머지14개는 even이다. Target1s의 odd 초기계수가 정확히0이면 비특이 metric 아래 homogeneous odd ODE의 유일한 해는0이다. 따라서 이 초기값 문제에는18→14 축약이 정확하다.

이것은 임의18차원 초기상태와 동등하다는 뜻이 아니다. 매우 작은1e-14 odd 초기진폭도 물리적 상태이므로 최종 guard는 이를 거절한다. 비평면 속도, 불완전한 p multiplet, 대칭을 깨는 상호작용에 적용하지 않는다. 직접 even-sector assembly와 U†fullU의 일치를 시험했다.

### 4. 같은 수치 요청의 중복 제거

basis/source/backend/sector/time/effective integration mesh/order가 같으면 candidate/reference라는 역할 이름이 달라도 같은 적분이다. 새 runner의9개 역할 요청은6개 고유 계산으로 묶인다. 그3개 alias는 독립 수렴증거로 세지 않는다. q56/q64 refinement와 과거의 별도 ring 결과가 실제 비교 증거다.

## 실제 결과

### 고정18-channel z0 stencil

새 full analytic kernel로 h2q56 및 h2q64의 z=-1e-4,0,+1e-4 여섯 node를 계산했다.

| 항목 | 결과 |
|---|---:|
| q56 connection 상대잔차 | 2.3253694e-9 |
| q64 connection 상대잔차 | 2.3253680e-9 |
| 기존 독립 ring h2q64 대비 raw 최대 상대차 | 1.308014e-14 |
| q56→q64 raw 최대 상대차 | 1.371767e-14 |
| 고유 새 적분/역할 요청 | 6 / 9 |

epsilon_z=1e-4, connection1e-6, raw1e-9 기준은 변경하지 않았다. 자세한 raw 행렬, identity, 실행시간은 evidence/E5_SCIENCE/에 있다. E5실행 이후에 변경한 것은 disjoint/입력/initial-state 경계 guard뿐이다. 당시 정확한 source manifest는 evidence/E5_SOURCE_MANIFEST.json에 별도 보존하고, 이를 최종 guard수정본의 실행 manifest라고 재표기하지 않는다.

기존 원래패널 q64의 미수렴 행렬도 새각도코드로 재현했으며, 같은노드에서의 차이는 약2.3e-15였다. 이 결과는 각도 축약이 수치문제를 바꿔서 통과시킨 것이 아님을 보여준다. 각도 축약만으로 잘못된 radial quadrature가 고쳐지는 것은 아니다.

z=-2의 phase32 중앙 snapshot은 기존 plain64와 최대3.3e-15, z=-4의 phase24 중앙 snapshot은 plain48과 최대3.5e-15 상대차로 일치했다. 이 두 추가결과는 중앙node만이며 전체시간stencil 검증으로 세지 않는다. exact수치는 evidence/E2_EXTRA_NODES.json에 있다.

Reflection 검사에서는 off-sector 상대 norm S/H/D가 각각 약2.78e-17,4.63e-17,3.95e-17이었다. 직접14-channel cross는 full18을 even부분에 투영한 값과 최대1.28e-14 상대차로 일치했다.

### 동일호스트 속도

동일 basis·동일 h2q56·z0·BLAS1에서 각backend를 한번씩 측정했다. 적분거리pair수는모두4,910,976으로 같다.

| backend | wall seconds | 기존 optimized-native 대비 |
|---|---:|---:|
| 기존 C++ ring | 75.8136 | 1 |
| 새해석 full18 | 23.0847 | 3.284x |
| 새해석 even14 | 17.8582 | 4.245x |

기존 ring은 이미 앞선 성능개선을 적용한 비교대상이다. 더 오래된 원본Python과의비교가 아니며, 이배수를 사용자5900X에서이전에측정한7.44배와곱하지 않는다. 단일실험의관측값이지분포나보장속도가아니다. 개발호스트CPUquota4,memoryquota4GiB의조건이다.

3process even작업의wall은spawn포함19.7439s,유효CPU사용은약2.77core였다. 세결과는직렬과arraybytes가정확히같았다. 세부정확수치와원시배열은 evidence/PAIRED_BENCHMARK/SUMMARY.json에있다. 기존benchmark script실행본과나중에정리한CLI경로도구분해보존했다.

## 발산탐색과 pruning 결정

| 경로 | 판정 | 근거/남은 조건 |
|---|---|---|
| exact cubic angular moments | 채택 | Wolfram 항등식, arbitrary-velocity raw oracle, 저장18-channel parity |
| 실수 Cartesian 표현 | 채택 | unitary 동일공간, 원래complex 출력으로 복원 |
| collision-plane even sector | 조건부 채택 | exact symmetry와exact even 초기값, full/projection parity |
| 중복 역할 task canonicalization | 채택 | 같은적분재계산만삭제,독립증거로중복집계금지 |
| target polar-shell+full-wavevector phase budget | 이번규칙탈락 | 4개실험모두raw1e-9미달 |
| Levin/Filon oscillatory integration | 보류 | 문헌은유망하나현재piecewiseFEM/endpoint기준으로미구현·미검증 |
| STO/Gaussian/Laguerre 재표현 | 이번교체에서제외 | 기저/continuum표현이달라새과학비교필요 |
| cross kinetic=Ritz energy×S | 거절 | translated test함수에weak eigenrelation그대로적용불가 |
| 작은pseudostate/odd진폭 threshold삭제 | 거절 | 물리상태삭제,정확대칭pruning과다름 |

Polar-shell 대안은 새Jacobian을 유도하고Wolfram으로확인했다. 모든FEMshell경계와phase budget8rad를유지해q12/16/24/32를계산했다. 체적오차는약6.5e-16이었지만 raw최대오차는1.0423e-5,6.5265e-6,2.8862e-6,4.5780e-8이었다. 따라서채택하지않았고,반복해서q나budget을바꿔통과할때까지돌리지않았다. 위상변화량제한이움직이는경계·Jacobian·진폭의전체오차상한은아니라는추론만지지하며,좌표법자체의불가능성은뜻하지않는다.

## 검증·실패 보존

최종 관련시험31개, failures/errors/skips0. 초기 개발의 fixture오류, alias결함, disjoint early return, 작은odd진폭거절의 RED/GREEN을보존했다. 모든시험을TDD로소급호칭하지않는다. 외부CAS및독립수치oracle는사용했지만 별도human/subagent reviewer가코드전체를승인한것은아니다.

EVIDENCE_LOG.md, FINDINGS.json, math/proofs.wl, math/WOLFRAM_RECEIPT.json, tests/, evidence/FINAL_TESTS.txt가검증경로다. verify_research.py는manifest와rawNPZ를읽어기존결과를재계산하며새physics/compile/GPU를실행하지않는다. SOURCE_MANIFEST.json은현재소스및필수입력identity를보존한다.

## 전달과 다음 단위

현재GitHubconnection에는쓰기동작이노출되지않고container git접속은DNS조회에실패했다. 원격push나이중백업을했다고주장하지않는다. code는독립패키지로검증했으며기존repo/branch/runs는변경하지않았다. 예전HP apply_and_push.py를이패키지에적용하지않는다.

다음코딩단위는이검증된analytic backend를기존h/p qualification의계산함수로연결하는integration이다. 그때옛source/context를보존한입력계약과alias출처를유지해야한다. 양의z/연속시간을이미통과했다고간주하지않는다. 현단계의최소로컬실행은README에있는새6-nodekernel검증이며,기존TP1/GPU/전체HP실행을다시요구하지않는다.

항상 capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO다. 이번culprit판정은선택된유한모형의적분·검증·계산표현에대한것이지원래전체capture discrepancy의최종원인판정이아니다.
