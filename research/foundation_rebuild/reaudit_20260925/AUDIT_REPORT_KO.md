# BASS_CR 재감사와 원인 분리: D5A 이후 연구 결과

## 판정 요약

**원래 GPU full collision을 다시 시작할 필요는 없다. 현재 FEM도 폐기할 단계가 아니다.** 이번에는 사전 설명을 그대로 따르지 않고 source/history/result를 다시 읽고, 기존 수치 행렬을 재계산한 뒤, 원인 가설에 대한 반례와 통제된 적분 수정을 수행했다.

반복 실패하던 18-channel FEM, z=-12 a0의 TP/PT cross block에서 basis/Hamiltonian/원래 threshold를 바꾸지 않고 수렴을 얻었다. 새 quadrature order20→24의 상대 Frobenius 변화는 S=1.211e-11, H=6.657e-12, D=2.388e-11이다. 이전 D4C order10과 새 구현 order10은 8e-13 이내로 일치하며, 이전 bound-only reference도 약1e-12 이내로 재현한다. 따라서 이는 다른 문제를 풀어 통과한 것이 아니라 **기존 문제의 적분 해상도와 구현을 바로잡은 결과**다.

다만 이 결과는 해당 유한 basis와 하나의 geometry의 정적 cross block에 대한 탐색적 수렴 증거다. full S/H/D 통합, 시간전파, capture gap, all-bound, b-grid는 완료되지 않았다. `production=HOLD`, `all_bound=OPEN`, `b_grid=NO_GO`, `capture_execution_allowed=false`를 유지한다.

## 1. 복구, 원본, 감사 범위

고정 source commit은 `8b7fef411ebca8dcdbfb45de542690c821fd7826` (`full backup`), tree는 `e17782911caad0af599715f37ac497639bf9e312`다. GitHub research branch의 실제 ref를 확인했다. source export archive의 SHA256은 `35ff8202f8d61bc8c70d9eb6972b23711be5b7b75577552ea4af489538b77dba`다.

2,482개 tracked files, 18,409,854 bytes를 manifest와 대조했고 불일치는 없었다. Python157개를 모두 AST parse하고 JSON1,243개를 모두 읽었으며 구문 오류는 없었다. 65개 NPZ의 array shape/finite 값을 조사했고 D1–D5A saved matrices를 수치 재분석에 사용했다. 모든 branch를 포함한 bundle에는111 reachable commits가 있고, 고정 source commit의 ancestry는100 commits다. 전체 git-object 복구와 fsck evidence를 보존했다.

**이 범위는 모든 과거 commit의 모든 줄을 각각 수학적으로 증명했다는 뜻이 아니다.** 파일 전수 inventory/구문/identity 검사와, 현재 scientific failure에 연결된 numerical source·호출 경로·config·test·result·gate의 내용 감사다. 세부 내용 감사는 원래 TDL/ControlledTDL/Gram/CAP/초기화/시간·공간 판정, Gaussian AOCC/metric 경로, FEM basis/gradient/support, D1–D5A 적분 및 판정기에 집중했다. `COVERAGE_INVENTORY.json`은 byte inventory와 Python 구조 정보를 담으며 scientific proof coverage를 과장하지 않는다.

원래 대형 GPU `state.npy`는 source archive에 없었다. source restore와 state restore, 원격 업로드와 실제 raw readback, test 통과와 과학적 production admission을 구분했다.

중단된 이전 응답에서 별도 `audit/fnd-d5a-forensic-20260925` branch와 source-export workflow를 만든 기록이 있다. 이 workflow는 pinned source/history export만 수행했고 과학 실행을 하지 않았다. 이번 수정 코드는 기존 research source와 별도의 `repair/`에 작성했으며 main/research branch를 merge하거나 기존 결과를 덮어쓰지 않았다.

근거: `SOURCE_VERIFICATION.json`, `export/SOURCE_INVENTORY.json`, `export/history.tsv`, `analysis/NPZ_INVENTORY.json`, `FND_RESULT_HASHES.json`.

## 2. 무엇이 실제 원인이었는가

### 2.1 D3에는 이전에 제공한 코드의 실제 support 오류가 있었다

D3 `element_pair_assemble()`은 rT와 rP를 둘 다64 이하로 제한하면서 전체 행렬을 적분했다. cross block에는 맞는 영역이지만 TT/PP에는 틀리다. 결과적으로 diffuse same-center states의 outer support가 잘렸다. D4A에서 z=-12의 약6% 차이가 거의 전부 same-center pseudostate blocks에서 나타난 것은 이 구현 오류와 대응한다.

이 오류는 사용자의 실행 방식이나 FEM 물리의 잘못이 아니라, 이전에 제공된 oracle 코드의 결함이다. D3 실패를 '다시 한 번의 물리적 pseudostate 실패'로 셀 수 없다. D3의 역사적 결과와 실패판정은 보존하되 올바른 full-matrix reference로 사용하지 않는다.

### 2.2 원인 추론이 너무 빨랐다

D1은 analytic/FEM bound-only와 diffuse pseudostate가 포함된 경우를 구별했다. 그러나 'C만 FAIL'은 positive state가 들어간 조합에서 미수렴이라는 뜻이지 positive-energy physics가 틀렸다는 뜻이 아니다.

D4B/D5A는 coordinate-axis refinement를 비교했다. 그러나 eta FAIL을 곧바로 longitudinal ETF underresolution으로 설명한 것은 논리적 비약이었다. 최대 q=126.76226068324343의 순수 exp(iq eta)는96점 Gauss–Legendre에서 약1.18e-15 절대오차로 적분되었다. 이것은 과거 설명의 구체적 반례다. 위상과 rough amplitude의 결합까지 배제하는 것은 아니다.

'부피가 정확하다', 'bound-only가 통과했다'를 diffuse H/D integral의 oracle 검증으로 넓게 표현한 것도 과했다. 부피는 integrand1을, bound control은 주로 원점 근처를 검사한다. 양에너지 mode가 차지하는 outer region의 oscillatory integral은 별도 문제였다.

### 2.3 유효한 FEM 함수와 부적합한 적분 가정의 결합

원래 FEM radial function은 C0 piecewise quartic이고 domain 밖에서0이다. mass normalization과 u 연속성은 좋지만 u'는 element/outer boundary에서 뛴다. 특히 pseudostate의 u'(64−)는 s 약-0.0388, p 약-0.0491이다. bound states의 outer slope는 훨씬 작다.

이 함수들은 weak Coulomb Hamiltonian의 정당한 기저다. 'C0이므로 무효'가 아니다. 다만 global rho/eta tensor quadrature는 비스듬한 FEM knot와 cutoff, derivative discontinuity, ETF oscillation을 동시에 다룬다. H와 D가 S보다 느리게 수렴하는 것은 이 구조와 일치한다.

D4C는 element/geometry boundary를 맞췄지만 local Gauss order6/8/10에서 diffuse phase-amplitude integrand를 충분히 분해하지 못했다. 새 구현을 동일 order10으로 실행하면 기존 D4C G3와 약8e-13 상대차로 일치했다. 이어16/20/24로 올린 고차 적분이 수렴했다. 따라서 **basis를 교체하지 않아도 현재의 실패를 제거할 수 있음**을 실제로 확인했다.

이 수정은 interface alignment, 효율적인 정확한 phi integration, 충분한 local quadrature를 결합했다. 개별 요인의 error contribution을 모두 독립적인 백분율로 분해했다고 주장하지 않는다. 충분한 원인-수정 대응을 보였다는 것과 유일한 단일 원인을 완전히 분리했다는 것은 다르다.

## 3. 오차 수치와 gate에 관한 적대적 재검토

D1–D3은 전체 matrix norm을 분모로 썼고, D4B 이후는 작은 TP block norm을 사용한다. diagonal near1 또는 v² terms가 지배하는 전체 matrix와 상쇄가 큰 cross block은 normalization이 다르다. 이 숫자들을 한 줄의 '오차 개선/악화' 시계열로 이어서는 안 된다.

D5A 최종 TP norm은 S 약0.0061753, H 약0.0082849, D 약0.0083988이다. eta192→256의 절대 변화는 각각2.428e-7,1.187e-5,2.330e-5이고 마지막 쌍 상대변화는 약3.93e-5,1.43e-3,2.77e-3이다.

그런데 새 고정-basis 수렴행렬과 D5A 최종행렬을 비교하면 차이는 S=5.885e-4, H=2.554e-3, D=4.787e-3이다. **S는 eta 마지막 쌍만 보면 통과했지만 실제 공동 적분수렴은 확인되지 않았던 것**이다. 이는 마지막 한 축 차분을 엄밀 error bound로 쓰면 안 되는 구체적 사례다. 과거 등록된 screen 결과 자체를 소급 변경하지는 않는다.

앞으로에는 absolute norm, reference norm, relative norm, block/channel identity, units를 함께 기록해야 한다. 실제 동역학에 들어가는 H−iD도 별도로 점검했다. 새20→24의 KTP 상대차는2.598e-11이고 D5A 최종 KTP와의 차이는5.873e-3이다. 이것도 S inverse와 time integration을 포함한 capture-error bound가 아니다.

## 4. 실제 코딩 수정과 검증 결과

새 파일 `repair/aligned_cross.py`는 기존 basis evaluator를 import한다. stationary amplitude에서 ETF를 분리하고 S/H/D의 유한 Fourier amplitude를 정확한 Bessel moments로 적분한다. two-distance radial partition은 FEM edges와 triangle activation breakpoints를 모두 포함한다. 지원 범위는 TP/PT cross blocks이며 같은 중심을 교집합에 잘못 넣지 않는다.

새 `repair/run_cross_probe.py`는 18-channel 고정-spec, z=-12를 기본으로 실행하는 bounded 정적 runner다. fresh output, source/kernel SHA, 실제 channel identities, matrices와 timing을 저장한다. new source digest는 원본 `cr_repro`와 분리되어 있다.

| 확인 항목 | 실제 결과 |
|---|---|
| 원본2,482개 파일 감사 후 hash | 모두 그대로 |
| 새 p10 vs old D4C G3 | S/H/D 최대7.92e-13 상대차 |
| 새 p16→20 | S3.226e-7 / H1.694e-7 / D6.480e-7 |
| 새 p20→24 | S1.211e-11 / H6.657e-12 / D2.388e-11 |
| 새 p24 bound subblock vs old B G3 | 최대7.20e-13 상대차 |
| 새 p24 sphere-intersection volume | 상대차2.47e-16 |
| 새 p24 S/H TP–PT† | 약1.2e-15 상대차 |
| DPT | 정지한 target ket이므로 정확한0 |
| 신규 패키지 시험 | 34 passed,0 failed,0 skipped |
| GPU propagation / capture run | 0 / 0 |

Bessel-moment 핵심 시험은 기존 단순 sampling 구현에서10 fail/5 pass인 RED를 기록한 뒤15 pass로 바뀌었다. 추가 geometry/FEM/uniform-phi/Laguerre 시험은 그 뒤 작성했으므로 전체34개를 모두 strict red-first TDD라고 표기하지 않는다. `RED_MOMENTS.txt`, `GREEN_MOMENTS.txt`, `NEW_TESTS.stdout`를 보존했다.

새 계산의 p16/p20/p24는 동일 bank byte identities를 사용했다. 이전 사용자 호스트와 현재 호스트의 regenerated eigenvector bytes가 같다는 주장은 하지 않는다. 현재 환경은 Python3.13.5, NumPy2.3.5, SciPy1.17.0이고, source/spec는 동일하다. old p10 matrix parity가 환경차의 수치영향이 이번 gate보다 훨씬 작음을 확인한다.

현재 컨테이너 timeout으로 초기 order16 두 시도가 중단된 기록이 있다. 이를 physicsFAIL로 처리하거나 숨기지 않았다. fresh output으로 재개한 계산이 완료했고 모든 child process는 이 응답 안에서 종료했다. wall-time 값은 프로세스 동시성/장비 차이가 있으므로 기존 사용자의 시간과 직접적인 speedup benchmark로 비교하지 않는다.

근거: `analysis/CONSOLIDATED_EVIDENCE.json`, `analysis/REFINEMENT.json`, `analysis/OLD_D4C_TO_NEW_REFERENCE.json`, `analysis/EFFECTIVE_CROSS_K.json`, 각 `analysis/E04*/RESULT.json`.

## 5. 전체 저장소에서 함께 확인한 문제와 비문제

기계 판독 가능한20개 finding은 `AUDIT_FINDINGS.json`에 있다. 우선순위가 높은 사항은 다음과 같다.

**현 실패를 만든 구현/추론 문제:** D3 support 오류, discontinuous derivative를 고려하지 않은 quadrature, p6/8/10의 부족, pure ETF로의 과잉 인과 추론, 전체와 cross norm의 혼용이다.

**검증 coverage 문제:** R2의 analytic bound cross tests와 atomic positive-energy bank tests는 실제 diffuse FEM cross block을 검증하지 않았다. 84pass와 후속 실패는 모순이 아니다. 새 test를 추가해야지 같은84개를 반복 실행해도 문제가 닫히지 않는다.

**실행 계약 문제:** R3A는 stop-on-first-failure를 선언하고도 모든 geometry를 실행했다. D1은 두 static geometry가 통과하면 capture 허용을 true로 만들었다. D2는 일부 declared gate/independent-rule comparison을 최종 classification에서 사용하지 않았다. return code0을 '실험 실행 완료'로 쓰는 것은 가능하지만 scientific pass와 분리해야 한다. 동일 output을 cp로 덮는 것을 create-only라고 부른 것도 잘못된 표현이다.

**manifest/authority 문제:** R2 strict SOURCE_MANIFEST에는 이후 추가된7개의 D1–D5A 스크립트가 없다. old `run_validation.py`를 현재 branch에서 다시 실행하면 undeclared source로 거부하는 것이 예상된다. 이것은 numerical regression이 아니라 manifest scope mismatch다. 이번 delivery는 별도 validator를 제공하며 historical manifest를 몰래 수정하지 않는다. root의 old implementer handoff와 nested test-only handoff, FND_STATUS의 pre-publication snapshot도 서로 다른 시점/authority를 가진다.

**원래 GPU에 대한 오탐 방지:** 실제 ControlledTDLRunner는 fixed CAP와 Gram-corrected projector를 사용한다. 기본 historical TDLRunner만 읽고 현재 B3가 raw overlap 또는 fixed-per-step CAP를 쓴다고 진단하면 틀린다. 실제 런칭 coordinator까지 추적했다.

**latent GPU edge case:** explicit cupy 요청 시 device_count0에서 numpy fallback 가능한 code path가 있다. 이것은 정적 발견이며 원래 GPU runs의 실패 증거가 아니다. 향후 backend health 실행을 준비할 때 작은 별도 fail-closed patch와 테스트로 다룬다.

**아직 열려 있는 과학:** 초기화의 유한 imaginary-time split 편향, full-space/finite-domain approximation, CAP/box/finite-time 영향, continuum/high-n completeness, 공통 projector, 실제 capture에 전달되는 시간·공간 오차는 이번 정적 적분 수렴과 별도로 남는다. 원래 h=.20 시간 evidence는 그 좁은 의미로 보존한다.

## 6. GPU 재실행은 어디서 필요한가

원래 R3M27의 CUDA-path/full-final 로그에는484pass가 보존되어 있다. 첫 libcufft 경로 실패도 별도 기록되어 있다. 이후 CPU-only3skip은 과거 GPU evidence를 지우지 않는다. 이번 source를 복원했어도 과거 대형 state bytes가 없으므로 GPU state restore를 주장하지 않는다.

현재 CPU cross-integral 수정 때문에 B3를 처음부터 다시 돌릴 필요는 없다. 실제 forward Hamiltonian/grid/CAP/initial state를 바꿀 때에만 해당 새 실험을 새로운 identity로 재실행한다. projector만 바뀌면 기존 endpoint를 복원하고 post-processing부터 하면 된다. GPU 환경만 바뀌었으면 small health/FFT parity가 먼저이며 full collision이 아니다.

상세 표와 보류 조건은 `GPU_RESTART_DECISION_KO.md`에 있다.

## 7. FEM 대안 조사와 실제 non-FEM 구성품

FEM의 대안은 아이디어 나열로 끝내지 않았다. `repair/laguerre_reference.py`로 smooth infinite-support L2 Laguerre radial basis의 M/H를 구성했다. N16/24/32, l0/1 원자 시험에서 N32 n≤3 최대 에너지 오차 약3.79e-13 Eh, mass-I 약1.22e-13 이하를 얻었다. 이 결과는 원자 구성품만의 검증이며 continuum/capture solver 완성이 아니다.

즉 현재 권고는 **동일 FEM의 정확한 적분을 유지하여 shortest corrective path를 확보하면서 smooth Laguerre를 독립 comparator 후보로 준비하는 것**이다. Gaussian AOCC, Coulomb DVR, BGM, 높은 연속성 B-spline/FEM-DVR, wavepacket continuum, Fourier-Galerkin의 trade-off와 문헌 적용 범위는 `FEM_ALTERNATIVES_KO.md`에 정리했다. B-spline을 완전히 FEM 바깥의 방법이라고 부르지 않았고, 정적 원자/분자 문헌을 moving collision의 완제품으로 취급하지 않았다.

## 8. 다음 한 작업과 불필요한 반복의 중지

다음 제안 work unit은 `FND_FULL_OPERATOR_INTEGRATION_FROM_VALIDATED_CROSS_V1`이다. 새 TP/PT kernel을 적절한 TT/PP full support와 결합하고, full metric과 direct D의 의미를 보존하는 통합이다. 원래 source/실패 결과를 바꾸지 않는 새 integration branch에서 한다.

새 kernel의 미해결 범위에 직접 필요한 시험만 추가한다. same-center isolated mass와 boost cancellation, 전체 Sdot=D+D† 및 직접 D 비교, 변경되는 geometry의 assembly를 확인한다. 이미 저장된 원자 에너지/old R2/old GPU full suite를 무조건 반복하지 않는다. 이러한 operator 통합이 확인되면 100 keV/u,b2의 작은 finite P1/P2 physical pilot로 진행한다. 모든 수학적 가능성을 검증하는 끝없는 audit loop로 다시 돌아가지 않는다.

이번 응답에서 full same-center assembly와 실제 capture pilot까지 구현했다는 주장은 하지 않는다. 사용자에게 미완성 핵심 구현을 알아서 추가하라고 떠넘기는 대신, 현재 완성된 standalone repair와 테스트·행렬 증거를 제공한다. 원래 GPU를 새로 돌리거나 또 다른 eta256→512 ladder를 실행하는 것은 지금 다음 작업이 아니다.

## 최종 claim ledger

- SOURCE/HISTORY RESTORE: source2482파일과history확인; 대형GPUstate 미복원.
- ROOT CAUSE: D3 support bug확인; pure-phase 원인단정 반박; 같은basis piecewise/oscillatory cross integration의 underresolution과 개선 수렴확인.
- FIX: z=-12,18channel TP/PT 정적수렴 확인. fullmatrix/trajectory의보편적정확성 미승인.
- TESTS: 신규34pass. 과거GPU/전체suite는 archived evidence만읽음.
- ALTERNATIVE: smoothLaguerre atomicprototype 구현·검산. two-center alternative collision 미실행.
- GPU RESTART: 지금 불필요. 실제H/initial/CAP변경 또는 회복불가payload요구에 따라 범위결정.
- PRODUCTION: HOLD. ALL_BOUND: OPEN. B_GRID: NO_GO. ORIGINAL_CAPTURE_GAP_RESOLVED: false.
