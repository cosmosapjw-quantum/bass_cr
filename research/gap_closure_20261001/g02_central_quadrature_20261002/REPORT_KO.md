# R4Y: 충돌 중심의 공간 적분 qualification

2026-10-02 KST. 이번 한 단계는 R4X 연속 기저 후보의 z=0 공간 적분 실패를 해명하고, 정확도를 유지하는 패널 분할을 구현·실행하는 작업이다. **고정된 중앙 한 점의 국소 공간 적분 판정은 통과했다.** 전체 G02 미분 검증은 아직 UNRESOLVED, production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO다.

## 원인과 직접 유도

b=2a₀, 100keV/u, 정지 target과 z 방향 projectile의 18채널 입력을 그대로 사용했다. 상대 속도는 2.00798106651023a₀/ta이고 ta=ħ/Eh다. 기저는 원본과 별도 identity를 가진 R4X 연속 후보이며, 재정규화·재 eigensolve·상태 삭제·raw D 보정은 하지 않았다.

두 중심 거리 좌표에서 ETF 위상은 `k_parallel*a + k_perp*rho*cos(phi)`다. 물리 파수는 k=m_e Δv/ħ다. 중앙에서는 k_parallel=0, k_perp=2.00798106651/a₀이므로 기존 종방향 phase budget은 아무 패널도 추가하지 않는다. 반면 실제 order40의 단일 inner FEM 패널에서 횡위상 argument 변화는 128.494rad에 이른다. z=−32a₀에서는 최대 2.360rad다. Bessel moments로 방위각 적분을 수행해도 이 두 거리 적분의 진동은 해상해야 한다.

고정 r₀에서 a=r₀cosθ, rho=r₀sinθ를 쓰면 모든 방위각에 대해 `|dPhi/dtheta| ≤ |k| r0`를 직접 얻는다. 새 `phase_pairs.py`는 기존 inner FEM 경계를 모두 보존하면서 `|k| r0 Δtheta ≤ beta`가 되도록 내부 경계만 추가한다. θ는 분할 경계를 정하는 데만 쓰며, 실제 Gauss 적분 변수 r₁와 양의 Jacobian r₀r₁/R 및 기존 native contraction은 유지한다. 이는 위상 변화의 수학적 상계이며 Gauss 적분 오차의 인증 상계가 아니다.

독립적인 대칭 진단도 유도했다. 같은 실수 s 모드를 두 중심에 배치하면 중점 좌표의 radial 곱은 공간 반전에 대해 짝함수이고 ETF의 시간 carrier가 소거된다. 따라서 overlap은 실수이며 z에 대해 짝함수다. 연속·compact·zero outer trace 후보가 H¹에 속하므로 중앙의 시간 미분이 0이고, 정지 target ket에서 D_PT=0이어서 **세 동일 s–s 대각 원소의 D_TP(0)는 정확히 0**이다. 이 정리는 raw 값을 0으로 덮어쓰는 데 사용하지 않았다. 일반 p 원소나 전 행렬·전 구간으로 확장하지 않는다. 상세 가정과 유도는 `DERIVATION_KO.md`에 있다.

## 유지한 판정 기준과 실제 계산

기존 공간 qualifier의 여섯 raw cross block에 대해

`max_blocks ||A−B||F / max(||A||F, ||B||F, 1e−300) ≤ 1e−9`

를 그대로 사용했다. 두 해상도 모두 full S/H Hermiticity 상대값≤1e−11 및 S의 λmin/λmax≥1e−8을 만족해야 한다. 추가한 중앙 대칭 진단은 계산 전에 고정한 세 s–s raw 대각 절대값≤1e−12/ta다. 이 허용오차들은 실행 후 바꾸지 않았다. S/H reverse block은 analytic conjugacy로 조립되므로 Hermiticity screen을 독립 적분 정확도 증거라고 부르지 않는다.

새 context에서 총 **13개의 완전한 cross-operator 평가**를 수행했다. 전역 cap24 중 예약과 완료는 모두13, 자동 재시도0, 시간 전파·capture 호출0이다. native 함수의 내부 batch 호출 횟수와 완전한 operator 평가 횟수를 구별한다. FP64, 같은 중심 order20, batch1024, full sector와 원소별 native 누적 순서를 유지했다.

| 비교 목적 | 실제 비교 | 여섯 raw block 최대 상대 차이 | 판정 |
|---|---|---:|---|
| fresh backend parity | 원래 q40,h1의 C++/Python ↔ Fortran/Fortran | 0, raw/full bitwise 동일 | backend parity 통과; 공간 정확도는 실패 |
| 기존 규칙의 p 증가 | q56,h2 ↔ q64,h2 | 1.2400208e−14 | 통과 |
| 독립 h 증가 | q64,h2 ↔ q48,h4 | 2.0461033e−14 | 통과 |
| 새 규칙의 p 증가 | q40,β24 ↔ q48,β24 | 1.1951568e−14 | 통과 |
| 독립 phase budget 감소 | q40,β24 ↔ q40,β12 | 3.7957240e−15 | 통과 |
| 두 규칙의 교차 비교 | q48,β24 ↔ q64,h2 | 2.9560514e−14 | 통과 |

q는 Gauss 차수, h는 기존 균일 subdivisions 수, β는 새 inner 위상 budget(rad)이다. 위 통과 행은 원래 raw criterion에 더해 양쪽 full screens와 중앙 대칭 진단까지 만족했다. `CENTRAL_RESULT.json`에는 선택 비교뿐 아니라13개 결과의 모든78쌍 관측을 보존했다.

기존 q40,h1에서 양의 에너지 s 대각 잔차는 1.6159235294e−4/ta였다. 새 q40,β24에서는 같은 원소가 7.6659378e−17/ta이며, 세 s 대각 중 최대는 6.5130915e−16/ta다. q48,β24의 세 대각 최대는 7.2943124e−16/ta, 기존 q64,h2는 3.3668676e−16/ta다. 횡위상 분할 후 이 독립 대칭 잔차와 두 규칙의 일치가 함께 개선되어, 중앙 실패를 횡위상 미해상으로 해석하는 수치 근거가 확보됐다. 이 결론은 관측된 고정 입력에서의 원인 진단이며 연속 quadrature 오차 증명은 아니다.

## 실패한 낮은 해상도를 보존한 이유

낮은 차수의 오차는 단조롭게 줄지 않았다. 기존 h1의 q40/q48/q56/q64에서 세 s 대각 최대 잔차는 각각 1.6159e−4, 3.8556e−4, 1.0337e−5, 2.8425e−9/ta였다. 모두 중앙 진단에 실패했다. q48,h2도 4.8445e−11/ta로 실패했고, q48,h2→q56,h2의 raw 상대 차이2.98185e−9는 원래 기준1e−9보다 컸다.

새 패널도 q32만으로 충분하지 않았다. q32,β24→q40,β24의 raw 차이는4.57804e−8, q32의 중앙 잔차는8.17150e−10/ta로 두 기준 모두 실패했다. 이를 버리거나 기준을 낮추지 않고, 사전에 허용한 q48,β24를 한 번 더 계산해 성공한 인접 차수 쌍과 독립 budget 비교를 확보했다. 패널 설계만으로 정확성이 자동 보장되지 않음을 보여주는 실제 실패다.

## 비용과 병렬 실행의 범위

성공한 두 차수 쌍의 실제 radial pair 점 수는 다음과 같다.

| 규칙 | 첫 차수 점 수 | 둘째 차수 점 수 | 합계 |
|---|---:|---:|---:|
| 기존 q56/q64, h2 | 4,910,976 | 6,414,336 | 11,325,312 |
| 새 q40/q48, β24 | 1,541,560 | 2,220,192 | 3,761,752 |

같은 raw 판정과 대칭 진단을 통과하는 차수 쌍에서 **계산점 수가 3.01065배 적다**. 추가 검증에 사용한 q48,h4 및 β12 계산도 실제 총13회와 전역 비용 기록에 포함되어 있다. 이 비율은 선택한 qualification pair의 점 수 비교이며 이번 전체 탐색 비용이나 solver wall-time speedup이 아니다.

관측된 worker 시간은 q64,h2 29.9248s, q40,β24 8.13984s, q48,β24 9.64617s였다. 서로 겹친 로컬 worker 및 단회 관측이므로 통제된 성능 benchmark로 해석하지 않는다. 네 순차 batch wall time의 합은99.5042s다. 동시에 실행된 개별 worker 시간을 합산하지 않았다.

실제 환경은 CPU quota8, RAM8GiB다. 최대3worker×2CPU와 coordinator1CPU로7CPU를 배정하고 BLAS는1thread로 제한했다. radial Fortran의 관측 OpenMP team은1, moment kernel의 설정값은2다. 기존 moment ABI는 실제 team 크기를 보고하지 않으므로2thread가 관측됐다고 주장하지 않는다. 최대 worker RSS는90,960KiB였다. 실제 OpenMPI 실행 및 NCP64 scaling은 미실행이다. fresh q40의 C++/Python과 Fortran/Fortran 비교에서 raw6개와 full3개 배열의 bitwise parity를 확보한 뒤 refinement에 compiled 경로를 사용했다.

## 검증·재현·다음 단계

새 테스트는 phase panel8개와 staged runner12개, 총20개의 고유 테스트를 실행해 통과했다. 경계 보존·양의 weight·기하 moments·큰 budget/속도0의 원래 규칙 parity·입력 거부와 node cap, task identity, 중복 task 차단·create-only 전역 예약·launch 실패·timeout·worker cleanup을 검사한다. Source/context binding은 실행 시 검증과 독립 검토로 별도 확인했다. 완료된 R4X 전체 suite는 반복 실행하지 않았다.

독립 코드 검토는 새 규칙의 유도와 기존 contraction·threshold 보존을 확인했고, 별도 atan2/Heron 기하로15개 arc 사례를 검산했다. 최종 독립 검토는 **PASS_LOCAL_CENTRAL_SPATIAL_ONLY**다. 연구 분석기나 provider helper를 import하지 않고77개 input/source pin,13개 raw/full payload의 해시·shape·finite·조립 일치,236개 저장 scalar와78쌍의 raw6개/full3개 norm 총702값을 다시 계산했다. 수치 불일치는0이었고 원래 threshold, 선택 비교의 결합 판정, 실패 보존,13개 전역 예약과 자원 기록을 확인했다. 검토자는 새 물리 호출이나 기존 suite 재실행을 하지 않았다. 최종 근거는 동봉 `INDEPENDENT_REVIEW.json`이다.

실행 context의 SHA256은 `2b28f6ee484de9075e769ded2e9777edd50017dd6b3338f6662a2294a8d021c6`이다. 실행 전에 고정한 수치 소스와 입력, 네 batch manifest,13개 예약 및 raw/full payload가 `runs_r4y/central_v1/`에 있다. `analyze_results.py`와 이 보고서는 실행 후 작성한 읽기 전용 분석·서술이다. 이를 실행 당시 source pin에 소급 포함하지 않는다. 기계 판독 결론은 `CENTRAL_RESULT.json`, 세부 실행 API는 `RUNNER_API.md`다. 최종 DB·commit·백업 identity는 별도 delivery receipt를 따른다.

이번에 닫힌 범위는 **별도 R4X 연속 기저와 한 개 중앙 geometry의 cross 공간 적분 qualification**이다. 같은 중심 적분의 order20은 고정했으며 이번에 독립적으로 세분하지 않았다. 다음 우선 과제는 이 공간 qualification을 미분 stencil의 모든 필요한 위치에서 새 context로 확보한 뒤, 독립 geometric derivative 또는 사전 설계한 FD와 `dot S=D+D†`를 비교하는 것이다. 전 구간 trajectory·capture·all-bound 또는 기존 production gate를 이번 결과로 승격하지 않는다.
