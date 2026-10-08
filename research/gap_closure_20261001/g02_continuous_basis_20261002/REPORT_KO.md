# R4X: 공유 경계 기저 표현의 구현 및 정적 검증

2026-10-02 KST. 작업 범위는 남은 G02 연구 중 R4W가 식별한 기저 표현 결함을 해결하는 별도 후보의 구현·국소 검증이다. 원본 기저·원래 G02 실패와 판정 기준을 유지한다. 전체 G02는 UNRESOLVED, production은 HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO다.

## 새 표현과 의미

R4W에서는 저장된 단항식 계수가 요소 경계에서 최대 1.5876189252139739×10⁻¹⁴만큼 불연속이고, 이것이 지배적인 같은 중심 미분 잔차에 기여함을 확인했다. 이번 후보는 셀 좌표 s∈[0,1]에서

`u(s)=(1−s)L+sR+s(1−s)(q₀+s(q₁+s q₂))`

로 표현한다. 인접 셀은 하나의 endpoint 배열을 공유하며 원점과 외곽 trace를 0으로 고정한다. 각 저장 FP64 값을 정확한 이진 유리수로 해석하면 모든 내부 value jump가 정확히 0이다. 셀 경계에서 derivative jump는 허용된다. 이는 후보의 연속 piecewise polynomial 표현에 대한 진술이며 FP64 평가 오차가 0이라는 주장이 아니다.

원래 eigensolve의 nodal vector는 입력 파일에 없으므로 복원했다고 주장하지 않는다. 공유 endpoint는 기존 각 셀의 상수항을 사용하고 q는 기존 높은 차수 계수에서 정확산술로 계산한 뒤 FP64로 한 번 반올림한다. 후보 nodal vector는 새 함수의 절점 표본이다. 재정규화·새 eigensolve·상태 삭제·raw D의 반대칭화는 하지 않았다.

`ContinuousRadial`은 기존 `FEMRadial`을 상속하지 않으며 기존 monomial payload 속성도 제공하지 않는다. 원본 공급자가 새 표현을 잘못 읽지 못하도록 거부한다. 명시적으로 분리한 연구용 연산자 adapter만 실제 공유 endpoint/bubble payload를 검증한 뒤 사용한다.

## 실제 기저 검증

아래 상대 L² 변화는 원본 저장 함수와 후보 함수의 정확 polynomial 적분으로 계산했다. weak residual은 기존 159×159 Coulomb FEM의 H,M과 기존 에너지 ε를 사용한 ‖Hc−εMc‖₂다. 여기의 c는 후보의 정확한 절점값을 FP64로 반올림한 벡터이므로 원래 nodal 자료의 복구나 전공간 연산자의 residual을 뜻하지 않는다.

| 모드 | 상대 radial L² 변화 | 정규화 오차 | weak FEM residual |
|---|---:|---:|---:|
| 0 (l=0, n=1) | 1.1313045e-14 | 7.9052005e-15 | 1.4151484e-13 |
| 1 (l=0, n=2) | 7.6152213e-15 | 3.7478313e-15 | 4.6615167e-14 |
| 2 (l=0, n=None) | 1.1827393e-14 | 1.1808153e-14 | 2.9896430e-14 |
| 3 (l=1, n=2) | 7.7000811e-15 | 8.6426192e-15 | 6.5560636e-14 |
| 4 (l=1, n=None) | 1.0123068e-14 | 9.3185791e-15 | 3.9173343e-14 |

5개 모드의 39개 내부 경계와 양 끝 trace가 모두 정확히 0이다. 같은 l의 Gram 행렬 오차는 최대 1.1768364×10⁻¹⁴, FEM mass matrix의 2-norm 조건수는 240.29783이다. 사전 고정한 상대 변화≤10⁻¹², 정규화·직교성 오차≤10⁻¹⁰, weak residual≤2×10⁻⁸와 기존 에너지 부호 분리 조건을 모두 통과했다.

R4W의 정확한 affine lift와 새 후보의 차이는 bubble 저장 반올림에 한정되며 상대 L² 차이는 최대 5.6121733×10⁻²⁹다. 후보와 불연속 원본 사이의 derivative 차이는 셀 내부 적분에 대한 broken L²로 기록했다. 이를 global H¹ 차이 상계로 부르지 않는다.

## 정확도를 보존한 평가기 최적화

새 hot loop는 Fortran/OpenMP와 SIMD로 구현했다. FP64, `-fno-fast-math`, `-ffp-contract=off`, `-fprotect-parens`를 사용하고 각 점의 계산 순서를 유지했다. GNU Fortran 13.3.0의 vectorization 기록에서 16-byte SIMD 경로가 확인된다. Python은 좌표 위치 찾기·입력/해시 검증·배열 준비를 담당한다.

5개 모드의 임의점 및 경계 인접점에서 Python/Fortran의 u,du가 비트 단위로 일치했다. 별도 정확 유리수 기준 845개 표본에서 최대 절대 오차는 u 4.1610×10⁻¹⁷,du 1.0419×10⁻¹⁶이다. 이 표본 오차는 전 구간 인증 상계가 아니다.

같은 100만 개 반경, 1개 모드, warmup 후 3회 측정의 중앙값은 다음과 같다. 현재 host의 CPU quota는 8, RAM 한도는 8GiB다.

| 평가 경로 | 전체 평가 시간(s) | Python 대비 |
|---|---:|---:|
| Python 벡터화 | 0.078008 | 1.00× |
| Fortran 1 threads | 0.038507 | 2.026× |
| Fortran 2 threads | 0.038611 | 2.020× |
| Fortran 4 threads | 0.031463 | 2.479× |
| Fortran 8 threads | 0.033834 | 2.306× |

이 workload의 전체 평가는 4 threads에서 가장 빨랐다. 8 threads가 항상 유리하지 않으며, Python의 위치 검색·메모리 준비 비용도 남는다. 위치가 미리 주어진 구간의 시간에는 ctypes·입력 검증·출력 할당이 여전히 포함되며 1→8 threads의 speedup은 1.733×다. 측정 peak RSS는 193,760KiB였다. 모든 측정 thread 수에서 같은 입력의 출력 비트가 일치했다.

이 결과는 radial 평가기의 국소 benchmark다. 아래 S/H/D 비교는 표현 변화만 분리하기 위해 양쪽 모두 기존 strict C++ moment backend와 후보 Python 평가기를 사용한다. 전체 solver의 2.48배 가속이나 NCP64/OpenMPI scaling을 측정한 것이 아니다. 새 Fortran 평가기는 실제 구현·국소 검증된 선택 경로이며 production provider에는 아직 채택하지 않았다.

## 실제 S/H/D 비교: 8회 완료

b=2a₀,100keV/u의 기존18채널 trajectory를 사용했다. z=−32,0의 각 위치에서 cross order32,40을 원본/후보 각각 계산했다. 같은 중심 order20, subdivision1, phase_budget=None, batch1024, 기존 strict C++ moment backend를 고정했다. 새 연산자 adapter의 diff는 형식·payload 검증과 metadata에 한정된다. 적분식·배치와 원소 누적 순서는 유지했다.

4개의 독립 worker를 각각 CPU0–3에 고정하고 coordinator는 CPU4를 별도로 예약했다. BLAS와 각 worker의 OpenMP는1 thread로 제한했다. 실행 전 단일 manifest와 raw-attempt 예약을 만들었으며 정확히8회 완료했다. 자동 재시도·시간 전파·capture 호출은0회다. batch wall time은27.9623s이며 동시 실행된 개별 시간을 합산하지 않는다. worker peak RSS는 최대85,136KiB다.

| 전체 행렬 | 원본–후보 최대 원소 차이 | 최대 상대 Frobenius 차이 |
|---|---:|---:|
| S (무차원) | 1.5543122×10⁻¹⁴ | 9.0083206×10⁻¹⁵ |
| H (Eh) | 3.0420111×10⁻¹⁴ | 9.8305234×10⁻¹⁵ |
| D (ta⁻¹) | 3.1086245×10⁻¹⁴ | 9.3979155×10⁻¹⁵ |

사전 고정한 local representation screen은 모든36개 full/raw operator 비교에서 통과했다. 원래 G02 미분 screen을 바꾸거나 이 결과로 대신하지 않았다. 전체 S의 최소 λmin/λmax는0.72693808이며 기존 metric ratio 기준10⁻⁸을 통과했다. S/H reverse cross block은 정확한 conjugacy로 조립되므로 이를 독립 Hermiticity 계산이라고 부르지 않는다.

| 위치 | 원본 PP max\|D+D†\|entry | 후보 PP max\|D+D†\|entry | 감소율 |
|---|---:|---:|---:|
| z=−32a₀ | 1.6542323×10⁻¹⁴ | 1.5543122×10⁻¹⁵ | 10.64배 |
| z=0a₀ | 1.6431301×10⁻¹⁴ | 1.6653345×10⁻¹⁵ | 9.87배 |

같은 중심의 정확한 표현 trace 결함은 사라졌지만 FP64 raw D의 합은 0이 아니며 arithmetic·quadrature 수준의 잔차가 남는다. 원본이나 후보의 raw D를 후처리하지 않았다.

## 확인된 한계와 다음 우선 과제

z=−32의 order32→40 최대 차이는 약1.65×10⁻¹⁶이다. 반면 z=0에서 후보의 S,H,D 최대 원소 차이는 각각1.74962×10⁻⁴,2.41354×10⁻⁵,3.48977×10⁻⁴이고 원본도 사실상 같은 민감도를 보인다. 따라서 이번32/40 두 차수를 충돌 중심의 수렴된 물리 연산자로 채택할 수 없다. 이 관측값은 엄밀한 quadrature 오차 상계가 아니며, 표현 변경의 작은 차이가 두 표현의 절대 물리 정확도를 보장하지 않는다.

다음 G02 우선 작업은 **이 후보의 별도 입력 identity를 유지하며 충돌 중심의 공간 적분 qualification을 확보하고, 그 결과에 독립 geometric derivative 또는 사전 설계한 고차 FD 검증을 적용하는 것**이다. R4V의 tiny-h 반복이나 단순 lab ETF phase 제거로 대신하지 않는다. 전 충돌 구간·연속 오차 상계·capture·all-bound·b-grid는 이번에 실행하거나 닫지 않았다.

## 테스트·독립 검토·소스 경계

새 기저10개와 adapter9개, 총19개의 고유 단위 테스트를 실행했다. 해시 불일치·잘못된 경계/shape/native 입력·legacy 경로의 거부·기존 수치 경로 보존·자원 예약과 실패 정리를 검사했다. 기존에 완료한 전체 테스트들은 반복 실행하지 않았다. 별도로5건의 잘못된 native 직접 입력을 거부했다.

정적 계산을 마친 뒤 coordinator가 예약 파일을 쓴 직후 프로세스 시작에 실패하면 실패 영수증의 예약 횟수를 작게 보고할 수 있는 경로를 발견했다. 계산식과 무관한 예약 카운트3줄을 수정하고 해당 실패를 재현하는 테스트를 추가했다. 실제8회 계산에 사용한 runner 원문과 SHA는 `source_at_run/`에 보존했고, 최종 수정 runner는 새 identity로 구별했다. 수정 후 물리 계산을 다시 실행하거나 기존 manifest를 새 코드에 덮어 씌우지 않았다. 실제 계산 중 실패한 사례로 보고하는 것은 아니다.

독립 검토는 후보 코드를 import하지 않는 Fraction·9점 Newton–Cotes 정확 적분으로1,065개 항목을 검산했다. 모든 모드의 norm·절점·trace·변화량·Gram 항목이 일치했다. 기존 monomial 변환을 사용하지 않는 cardinal-basis 직접 조립으로 weak FEM residual도 검산했고 최대1.2306810×10⁻¹³으로 기존 기준을 통과했다. 이는 서로 다른 부동소수 조립 방식의 잔차 검산이며 원본 계산과 비트 단위 일치를 주장하지 않는다.

또한 실제8개 RAW/FULL payload와72개 비교 행의495개 scalar 지표를 별도로 재계산했다. 최대 차이는 합산·고유값 계산의 순서 차이에 따른8.88×10⁻¹⁶이었고, 국소 판정과 z=0의 적분 미수렴 관측은 일치했다. 최종 검토 기록은 `INDEPENDENT_REVIEW.json`이다. 허용되는 결론은 국소 표현·정적 비교 검증뿐이다.

## 산출물과 상태

후보 원본은 `runs_r4x/candidate_v1/`, strict native build와 SIMD 기록은 `runs_r4x/native_v1/`, 모든8회 정적 원자료·manifest·예약·완료 영수증은 `runs_r4x/static_v1/`에 있다. `BASIS_DIAGNOSTICS.json`, `EVALUATOR_VALIDATION.json`, `VALIDATION.json`, 독립 검토 및 실행 후 수정 기록을 함께 보존한다. 패키지의 `new_native_calls=8`은 완전한 raw cross-operator 평가 횟수이며 각 배치의 native 함수 호출이나 평가기 benchmark 호출 수를 뜻하지 않는다.

DBv10은 DBv9의42개 표와3,290개 기존 행 및 기존 view 의미를 보존하고 이번 G02 근거와 상태만 추가한다. 최신 상태는 `current_research_gap_status`에서 읽고 이전 effective view는 `current_research_gap_status_v9`로 보존한다. Git commit과 실제 backup 결과는 별도 최종 delivery receipt에 기록한다.

이번에 완료한 한 단계는 **별도 연속 기저 구현·정확산술 및 weak FEM 검증·같은 입력의 정적 S/H/D 비교·국소 Fortran/OpenMP 최적화 검증**이다. 최종 G02 상태는 UNRESOLVED, production=HOLD다.
