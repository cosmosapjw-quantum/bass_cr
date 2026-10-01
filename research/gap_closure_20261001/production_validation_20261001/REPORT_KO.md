# BASS CR R4V 연구 실행·복구 보고서

작성일: 2026-10-01. 대상: archived B0 18채널, 100 keV/u, b=2 a0, 전하1/1. 복구 기준은 R4U commit `0551d0055dd9dae9fec705b1c1b5fd8dbb7ae972`이다. 이번 게시 commit·백업 객체·패키지 검증은 별도 최종 전달 영수증으로 식별한다.

**미실행 상태였던 G02 물리 유한차분, G03 ±48 독립 예측점, G12의 짧은 동일 초기값 비교를 실제로 수행했다. G03의 바깥 영역 R⁻² 모형과 G12 국소 파일럿은 정해진 진단을 통과했지만, G02의 원래 잔차 기준은 8개 중심 모두 미달했다. 따라서 전체 production은 여전히 HOLD다.**

| 이번 실제 계산 | 신규 qualified query | raw full-operator 호출 | 결과 |
|---|---:|---:|---|
| G02 독립 Sdot 유한차분 | 72 | 144 | 2차 수렴 관측, 원래 잔차 기준 미달 |
| G03 signed ±48 holdout | 2 | 4 | 바깥3점 기반 R⁻² 예측 진단 통과 |
| G12 동일 초기값·독립 적분법 파일럿 | 18 | 36 | 직접 DOP853 대 midpoint 1/2/4 step 국소 비교 통과 |
| 합계 | 92 | **184** | 91개 고유 시간에 대한92회 query 실행; 공통 시각도 각 단계에서 새로 계산 |

모든 query는 기존 order32→40, subdivisions1의 첫 인접 쌍에서 공간 qualification을 통과했다. 원래 FP64, quadrature ladder, same-center order20, raw 상대 기준10⁻⁹, S/H Hermiticity 기준10⁻¹¹, metric 고유값 비율10⁻⁸을 유지했다. 이 내부 resolution 일치는 엄밀한 연산자 오차 상계와 다르다.

**중단 복구와 실행기는 실제 증거를 기준으로 이어 갔다.** 자동 작업공간 정리로 사라진 R4U 파일을 복원하고 manifest에 포함된 681개 파일, 49,016,175 bytes의 크기·SHA256을 전부 대조했다. 681/681이 일치했다. 마지막 R4U의 완료된 파일럿이나 의도적인 1-step paused checkpoint를 실패한 production 실행으로 재분류하지 않았다. 이전 43개 테스트와 Fortran/C++·재개 일치 결과는 보관 증거로 계승했으며 이번에 다시 실행한 것으로 세지 않았다.

새 batch 실행기는 고정된 완전 query 사다리를 나누고, lane마다 독립 watchdog·CPU affinity·raw 예산을 적용한다. G02는 18-query lane4개, 각2스레드로 분할했고 최대198회씩 총792회로 미리 제한했다. 이번 실제 사용은144회다. 과거 C++ 중심6개를 새 Fortran 실행에 자동 편입하지 않아, 이전의 66-new+6-reuse 계획 대신72개 모두 새로 계산했다.

사전 독립 검토에서는 wrapper가 갑자기 종료된 뒤 별도 session의 자식이 남는 결함을 재현했다. **수정 전 실행기는 물리 계산에 사용하지 않았다.** 수정본은 process-local child subreaper, 정확한 자식 PID/start-time identity 보존, 종료 시 owned descendant 정리·reap, 실행 영수증 결합을 사용한다. 관련 없는 process의 종료를 허용하지 않으며, 남은 owned child가 있으면 성공으로 처리하지 않는다. 즉시 exit·SIGKILL·자식이 살아 있는 exit0 등을 주입한 검증과 동일 독립 재현에서 수정이 확인됐다. 사용한 계획과 출력은 create-only이며 자동 재시도·예산 이전·허용오차 완화는 하지 않았다.

실제 호스트는 **CPU quota8, RAM cap8GiB**였다. 실행은 Fortran/OpenMP와 별도 serial worker lane을 이용했다. MPI root 보호를 우회하지 않았으며 이번 물리 계산에서 MPI launcher를 사용하지 않았다. G12는 G02의 lane1–3 완료와 자식 종료를 확인한 뒤 CPU2–7을 사용했고, 진행 중인 G02 lane0의 CPU0–1과 겹치지 않았다. 동시 compute thread8개, 메모리 추정량과 reserve는 별도 overlap admission에 기록했다.

G02 batch wall time은1,390.947초, G03 supervisor는43.259초, G12 batch는165.067초였다. G12는 G02의 일부와 겹쳐 실행됐으므로 이 시간을 전체 경과 시간처럼 단순 합산하면 안 된다. G02 lane0의1,390.697초와 나머지 lane의334.119/340.468/440.409초 사이에 큰 차이가 있었고 원인은 확정하지 않았다. 이를 속도 향상이나 kernel scaling의 근거로 사용하지 않는다. **64코어·128GB NCP 실측, MPI 물리 실행과 scaling은 NOT_RUN**이다.

**G02는 실행을 완료했지만 원래 판정은 통과하지 않았다.** 중심 z=±12, ±16, ±24, ±32 a0와 h=0.4, 0.2, 0.1, 0.05 a0에서 독립적으로 얻은 S를 사용해

\[
E_h=v\,\frac{S(z+h)-S(z-h)}{2h}-(D+D^\dagger)
\]

를 계산했다. 시간·좌표는 기존 계획의 hexadecimal float identity를 그대로 사용했다. 새 현재 context의 query/입력/native/source·payload·full/raw 블록 결합과 완료 영수증을 확인한 후 기존 `compare_ladder`를 변경하지 않고 호출했다.

| G02 진단 | 실제 결과 | 원래 판정 |
|---|---|---|
| 관측 수렴차수 | 각 중심에서 약1.985–1.999, 마지막 구간 약1.9991–1.9992 | 연속2구간 [1.5,2.5] 조건 충족 |
| h=0.05 spectral 절대 잔차 | 1.348×10⁻⁶–3.286×10⁻⁶ atomic_time⁻¹ | 절대 목표10⁻¹² 미달 |
| h=0.05 spectral 상대 잔차 | 4.126×10⁻⁴–5.298×10⁻⁴ | 상대 목표10⁻⁶ 미달 |
| h=0.05 성분별 최대 정규화 잔차 | 약1.643×10⁻²–1.654×10⁻² | 상대 목표10⁻⁶ 미달 |
| 8개 중심의 최종 상태 | 모두 `RESIDUAL_TARGET_NOT_MET` | 전체 `FD_VALIDATION_UNRESOLVED` |

추가로 저장된 S 표본만으로 Richardson R2/R4/R6/R8 조합을 계산했다. 외삽 계수 결정에 해석적 D를 사용하지 않았으며 새로운 native 호출은0회다. R8과 D+D†의 spectral 상대 차이는 **4.675×10⁻¹²–6.562×10⁻¹²**였다. 이 결과와 하위 차수의 수렴은 중앙차분 절단 오차가 주요 원인이라는 해석을 지지한다. 그러나 상관된 표본의 오차·차분 소거·quadrature 오차를 배제한 엄밀한 bound는 아니다. R8 한 층만으로 그 층의 관측 수렴차수를 검증할 수도 없다.

R8은 `OBSERVATIONS_ONLY_NO_GATE_DECISION`으로 보존했다. 작은 R8 차이를 원래 h=0.05 중앙차분 결과 대신 넣거나, G02 PASS로 바꾸거나, total error budget의 인증된 항으로 더하지 않았다. 독립 성분 검토에서는 최대 정규화 잔차를 만드는 projectile–projectile 성분(0-based9,13)의 FD가 모든 h에서 정확히0이고, D의 약±0.56093 항이 상쇄된 뒤 약1.64×10⁻¹⁴가 남는 것을 확인했다. 이를10⁻¹² denominator floor로 나누어 약0.0164가 된다. 이 작은 성분만으로 도함수의 큰 물리적 불일치를 주장할 수 없지만, 다른 성분의 spectral/Frobenius 잔차도 각각 원래 기준에 미달하므로 G02 실패 판정은 그대로다. h를 줄이는 것만으로 이 h-독립 상쇄 잔차를 해결할 수는 없다.

**G03는 바깥 영역과 내부 영향을 구분하는 실제 예측 검증으로 진행됐다.** 기존 ±16/20/24/32의 역사적 C++ 자료로 만든 모형·예측을 실행 전에 고정하고, 새 Fortran context에서 ±48을 각각 계산했다. 기존 baseline의 native/context를 새 것으로 바꾸어 표기하지 않았다. R4U의 backend parity는 실제 비교한 z32 입력과 차수에서의 보조 증거로만 사용한다.

새 값은 양쪽 모두 rho≈1.877660071256205×10⁻⁴ atomic_time⁻¹이다. order32/40의 인접 rho 차이는 상대7.22×10⁻¹⁶와8.66×10⁻¹⁶였다. 부호별 query는 독립 실행했으며 서로를 재사용하지 않았다.

| 실행 전 고정한 모형 | ±48의 상대 예측 잔차 | 2% 경험적 기준 |
|---|---:|---|
| 바깥3점(|z|=20,24,32)의 M1: R⁻² | **0.2644%** | 양쪽 통과 |
| 바깥3점의 M2/M3/M4 | 약0.3705% / 0.3714% / 0.8104% | 양쪽 통과 |
| 내부16도 포함한 전체4점 M1/M2/M3/M4 | 약2.4566% / 6.5270% / 4.8814% / 6.7901% | 모두 미달 |

점16을 삭제한 것이 아니다. 바깥3점 가설과 전체4점 민감도를 함께 유지하고 사전 예측대로 비교했다. 바깥 모형 M2의 지수는48을 추가하기 전1.9983866, 추가한 후2.0025816으로, 사전의 |p−2|≤0.05 및 |Δp|≤0.05 기준도 만족했다. 이 결과는 내부16의 preasymptotic 영향과 바깥 영역의 near-R⁻² 예측군을 지지한다. 여러 모형이 동시에 통과하므로 유일한 계수·함수형을 식별했다고 주장하지 않는다. 다음 독립 점은 계획대로 ±44이며, **아직 실행하지 않았다.** 연속 supremum·전체 tail·G04/G05는 닫히지 않았다.

**G12는 서로 다른 전파법을 같은 초기값에 실제 적용했다.** 구간은 z=32→32.02 a0이며 초기 상태는 초기 S에서 정확히 한 번 정규화한 e0 시험 벡터다. 직접 계수 방정식

\[
\dot c=S^{-1}(-iH-D)c
\]

의 DOP853과 기존 Cholesky midpoint recurrence의1/2/4 step을 비교했다. DOP853은 rtol5×10⁻¹³, atol5×10⁻¹⁵, 사전 지정한 단일 step과 RHS13회만 허용했다. SciPy1.17.0 코드·tableau·정확한 stage time을 고정했고, 모든 방법의 합집합18개 시간에 새 qualified 연산자를 확보했다. 보간, dense output, adaptive 추가 query, cache-miss native fallback은 없었다.

| 비교 | endpoint의 unaligned metric 거리 |
|---|---:|
| midpoint1 대 DOP853 | 1.0449678434×10⁻¹¹ |
| midpoint2 대 DOP853 | 2.6124166160×10⁻¹² |
| midpoint4 대 DOP853 | 6.5310589217×10⁻¹³ |

midpoint 차이의 관측 수렴차수는2.000003475다. DOP853 초기·끝점 metric-norm drift는0, midpoint의 최대 discrete whitened-norm drift는2.2204460493×10⁻¹⁶이다. 모든 방법의 실제 초기값 해시는 `07398559dda76cd440225f94d5bc32566fd094c1d41b0900649cf4a0a280cedb`와 일치한다. midpoint4와 DOP853의 선택 부분공간 population 차이는7.7283×10⁻²²로, 사전 국소 기준도 통과했다. 이는 finite-span 시험 진단이며 capture나 물리 반응률이 아니다.

독립 검토자는 저장된 `STATES.npz`와 최종 S의 고유기저로 거리를 별도 재계산했다. 보고된 값과의 최대 차이는1.62×10⁻²⁷이었고 population, 초기값, norm, 소스·계획·18개 캐시 및 producer 완료 영수증도 일치했다. 추가 물리 계산이나 전파 재실행은 하지 않았다.

이 성공은 좁은 구간의 국소 engineering screen 통과다. 원래 G12는 실제 incoming state와 [-12,+12] 구간을 요구하므로 여전히 OPEN이다. midpoint는 Sdot=D+D†를 사용하며, 직접 ODE와의 일치만으로 독립 Sdot 검증을 선언하지 않는다. DOP853 norm은 두 endpoint에서만 샘플링했고 embedded local controller도 rigorous global error enclosure가 아니다.

**테스트와 과학 판정을 구분했다.** 이번 추가 코드의 서로 다른 집중 test method는41개 통과했다: batch13, 현재-context 분석기13, G12 파일럿8, Richardson7. 최종 batch 수정 후3개 관련 테스트를 다시 확인한 것은41개에 추가하지 않았다. 이 테스트는 synthetic cache·해석적 시험계·실제 작은 subprocess 실패 주입을 사용하며 물리184회와 별도다. 독립 orphan 재현과 정확한 실제 시간 크기의 G12 해석적 장난감 검증도 각각 기록했다. 이전 R4U43개 테스트를 다시 통과한 것으로 합산하지 않았다. G02의 독립 과학 검토는 원시 잔차와 Richardson 조합을 별도 경로로 재구성해 보고·해석 PASS로 판정했으며, 원래 G02 gate는 미해결로 유지했다. 최종 runtime 독립 검토도 계획·완료·자원·184회 ledger·캐시 결합에 결함 없이 PASS였다. 알려진 실행기 PID/start-time identity16개는 모두 종료된 상태로 확인했다. G12 수치 독립 검토와 함께 상세 근거를 review 영수증에 보존했다.

**최초 프롬프트의 연구 단계는 모두 완료되지 않았다.** R4U에서 서로 다른 SQLite11판본을 실제 감사하고 HE/CR 원계약72항목을 대조한 결과를 계승한다. 이번에는 동일한 cloud 전수 검색을 다시 수행한 것이 아니라 복구된 판본과 기록을 근거로 다음 연구를 실행했다. Drive binary 목록은1,000개 이후 continuation이 없어 모든 binary DB의 전 계정 전수성은 미확정이고, WU088 원 deep-research DB bytes도 아직 없다. 역사적 acquisition DB를 그 원본으로 대체하지 않는다.

| 연구 단계 | R4V 뒤 상태 |
|---|---|
| CR/HE/WU 원자료·DB·요구사항 감사 | 기존11 SQLite 판본·72항목 감사 계승. corpus 밖 DOI·일부 raw·원 DB의 공백 유지 |
| 유한 모형 관측량·국소 변화율 이론 | 조건부 정리·정의역 기록 유지. 완전한 물리 capture 인증은 아님 |
| Fortran 물리 연산자·검증 캐시·실행/재개 | R4U 연결에 R4V 병렬 batch·실패 처리·실제 검증을 추가 |
| G02 독립 Sdot | 전체72점 실행 완료, 원 잔차 판정 미해결. R8은 보조 증거 |
| G03 asymptotics | ±48 외부 예측 진단 진전. ±44 미실행, 연속 tail 인증 미완료 |
| G04/G05 complex enclosure·연속 bound | 물리 complex interval assembly·연속 오차 인증 미완성 |
| G06/G11 nested window·양쪽 tail | ±16/20/24/32 확대 전파와 tail 오차 폐쇄 미실행 |
| G12 독립 전파기 | e0·짧은 구간 파일럿 통과. 실제 incoming state·원 구간 비교 미실행 |
| state/metric transfer·total error | 실제 모형 대입·오차 합산과 인증 미완성 |
| G13 higher-l·B1/B2/B3 | backend·기저 검증·완전성 검사 남음 |
| all-bound·b-grid·단면적 | 선행 gate가 열려 있어 미실행 |

**DBv8을 생성하고 보존 검증을 완료했다.** 기존 v7의38개 테이블·3,263행은 schema와 전체 행 multiset이 그대로이며, 새 evidence15행과 현재 상태3행을 별도 추가했다. `current_research_gap_status` view는 G02를 `UNRESOLVED`(자원 차단 해소, 실제 잔차 목표 미달), G03/G12를 `RESOLVED_WITH_LIMITATION`으로 보여 준다. 이 제한 상태는 전체 과학적 폐쇄를 의미하지 않는다. 과거 scientific claim 행을 다시 쓰지 않았다. SQLite integrity는 `ok`, foreign-key 위반은0이다. 최종 크기는6,037,504 bytes, SHA256은 `29cb9f002be65c48e4b002771b4f3649ddbc947ec626b805e381a0bfaf154ba2`이다. 게시·백업 완료 여부는 별도 최종 전달 영수증을 기준으로 한다.

**다음 연구는 아래 순서로 좁혀 진행한다.**

1. **G02는 확인된 두 오차 구조를 분리해 다음 실험을 설계한다.** 기존 캐시에서 관측한 중앙차분의 O(h²) 절단 오차와 같은 중심 D 항의 상쇄 잔차를 분리한 오차 예산을 먼저 만든다. 이미 확인된 PP(9,13) 성분을 다시 발견하는 작업부터 반복하지 않는다. 위상 구조를 명시적으로 처리한 도함수 설계 또는 필요한 부분의 고정밀 검증이 잔차를 구분할 수 있는지 조사하고, quadrature·차분 계수에 의한 표본 오차 증폭도 평가한다. 원래 전체 최대값 OR 판정식은 보존하며, spectral O(h²)만으로 h≈0.002를 정하거나 허용오차를 바꾸지 않는다. 새 정보가 생기는 h·고차 stencil·고정밀 비교를 사전에 고정한 뒤 양쪽 대표 중심의 제한된 물리 실험으로 간다. R8 한 값의 작은 차이를 인증된 오차항으로 넣지 않는다.
2. **G03의 다음 독립 예측점 ±44를 검사한다.** 이번 출력에 고정된 모든 모형의 ±44 예측값을 다음 계약에 직접 결합한다. 같은 B0·원래 qualification으로 두 부호를 각각 계산하고, signed parity·지수 안정성·인접 resolution·전체4점 민감도를 모두 보고한다. 통과해도 유일 모형이나 연속 tail bound로 승격하지 않는다.
3. **G12를 실제 물리 IVP로 확대한다.** 원래 incoming-state payload·metric·window identity를 먼저 결합하고 직접 ODE와 midpoint/필요한 독립 고차법의 동일 초기값 비교를 수행한다. 각 방법의 실제 stage operator를 확보하며 sparse snapshot 보간으로 대체하지 않는다. G02의 독립 derivative 증거를 별도 항목으로 유지한다.
4. **첫 nested-window와 양쪽 tail을 닫는다.** 정해진 ±16/20/24/32 순서에서 endpoint/state-transfer와 양쪽 tail 기여를 분리하고, 물리 complex weak-residual/interval enclosure를 구현해 G04/G05와 total-error ledger에 실제 입력을 연결한다. 현재 경험적 rho fit은 그 rigorous enclosure를 대신하지 않는다.
5. **higher-l·B1–B3와 NCP 실측을 연결한다.** 기저 확대의 오차와 backend 지원을 검증한다. 일반 사용자 NCP 실행 채널에서 source/native/input/resource manifest를 새로 결합한 뒤 OpenMPI의 완전 query 병렬화, Fortran/OpenMP, SIMD의 정확도·반복 성능을 측정한다. 실제 topology에 따른 rank/thread 조합을 비교하고 8CPU 관측을64CPU 수치로 외삽하지 않는다. all-bound·b-grid·단면적은 필요한 선행 gate가 닫힌 후에만 진행한다.

**재현 자료의 상대 경로**는 최종 패키지 루트를 기준으로 다음과 같다. 구체적인 byte identity의 기준은 패키지 `MANIFEST.json`이며, 자체 ZIP 해시·외부 업로드 상태는 패키지 바깥의 검증/전달 영수증에 있다.

| 자료 | 패키지 상대 경로 |
|---|---|
| 이번 구현·수치/실행 계약·집중 테스트 | `source/research/gap_closure_20261001/production_validation_20261001/` |
| 고정 B0 입력과 native build | `runtime_inputs/`, `native_build_portable/` |
| G02의 원 판정·R8 보조 진단 | `runs_r4v/G02_RESULT.json`, `runs_r4v/G02_RICHARDSON_RESULT.json` |
| G03의 실행 전 예측·실제 점수 | `runs_r4v/G03_PREDICTIONS_BEFORE_RUN.json`, `runs_r4v/G03_ANALYSIS/G03_RESULT.json` |
| G12의 정확 stage 계획·실제 상태 | `runs_r4v/G12_PILOT_PLAN.json`, `runs_r4v/G12_ANALYSIS/` |
| producer·자원 중첩 admission | `runs_r4v/G12_PRODUCER_ADMISSION.json`, `runs_r4v/G12_OVERLAP_ADMISSION.json` |
| 복구 inventory·독립 검토 | `recovery_r4v/` |
| 이 보고서·최종 DBv8 | `reports/` |
| 변경하지 않은 R4U 원 패키지·11 DB 감사·기존 결과 | `base/` |

현재 과학 상태는 **production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO**다. 이번 결과는 실행기와 물리 검증을 실제로 전진시킨 증거이며, 남은 최초 연구 단계를 완료했다고 주장하는 근거는 아니다.
