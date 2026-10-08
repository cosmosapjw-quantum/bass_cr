# R4U 실행기 통합·실제 계산·원본 요구사항 재감사

작성일: 2026-10-01. 기준 소스는 R4T `e1438233548cf01fa9894d17e194acba49e0ac7b`이며, 새 게시 commit과 백업 식별자는 별도 전달 영수증에 기록한다.

**Fortran 물리 연산자 → 원래 수치 검증 → 캐시 → 체크포인트 전파를 연결하고 실제 B0 파일럿까지 실행했다. 전체 과학적 production 인증은 아직 완료되지 않았다.** DB를 다시 읽은 결과도 최초 연구 단계 전체를 완료했다고 뒷받침하지 않는다.

## 이번에 구현하고 실행한 것

이전 R4S의 Fortran/OpenMP 커널과 MPI 큐는 실제 물리 실행기에 연결되지 않았다. 기존 전파기는 전체 시간 격자 실행을 다시 시작하는 방식이었고, 부분 진행 상태에서의 재개 경로가 없었다. 이번에는 다음을 연결했다.

- 원래 B0 입력 배열뿐 아니라 basis 의미 identity와 과학 계약도 고정한다. 새 backend를 기존 승인·context로 위장하지 않는다.
- 각 rank의 실제 CPU·quota·RAM을 검사하고, 모든 rank의 확인이 끝난 뒤 native 연산자를 만든다. 독립 query의 qualification ladder를 통째로 배분하고 전체 시도 예산은 coordinator 한 곳에서만 차감한다.
- 기존 FP64, same-center order20, cross 적분 순서·차수 ladder·허용오차를 유지한다. C++ 기준 backend와 Fortran 후보를 함께 보존한다.
- 원시 cross 결과와 full S/H/D의 6개 TP/PT 블록이 정확히 일치해야 캐시를 발행·사용한다. 독립 검토에서 발견한 기존 검증 공백을 보완했다.
- 전파기는 정확한 endpoint/midpoint 캐시만 사용하고 매 step의 whitened state를 저장한다. 초기 상태·소스·환경·캐시·checkpoint chain이 일치할 때 새 출력 폴더에서 재개한다. orphan checkpoint는 자동 삭제하지 않고 거부한다.
- 외부 watchdog이 제한 시간을 집행하고, 실패·부분 파일·이미 사용한 예약은 보존한다. 자동 재시도나 cache-miss native fallback은 없다.

실행 직전에는 cgroup 사용량에 포함된 파일 캐시를 모두 상주 작업 메모리로 취급하는 과도한 차단도 확인했다. 깨끗하고 매핑되지 않은 leaf-cgroup file-LRU의 보수적 추정량 절반만 가용량에 반영하도록 고쳤다. dirty/writeback/shmem/unevictable 및 보호 메모리는 제외하고, ancestor cap·host MemAvailable·기존 최소1GiB/1⁄8 reserve를 유지한다. 이는 명시적 프로젝트 추정 정책이며 커널의 메모리 할당 보장이 아니다. quota를 바꾸지 않았다. 자세한 공식 counter 근거와 테스트는 `MEMORY_ADMISSION_VALIDATION`에 있다.

## 실제 파일럿 결과

범위는 실행 전에 `ACCEPTANCE_SCOPE.json`에 고정했다. **100keV/u, b=2a0, archived B0 18채널, z=32→32.02a0, midpoint2 step**이다. 초기 상태는 S에서 한 번 정규화한 명시적 e0 시험 벡터다. 저장된 incoming scattering state나 기존 tail state가 아니다.

| 검증 | 실제 결과 |
|---|---|
| 신규 물리 연산 | Fortran4 query + 같은 첫 시간의 C++1 query, 서로 다른 물리 시간4개 |
| raw full-operator 호출 | 합계10회: Fortran8, C++2 |
| 공간 qualification | 모든 query에서 원래 order32→40, subdivisions1 통과 |
| Fortran/C++ 비교 | 두 적분 차수의 full/raw 배열18개 모두 비트 단위 동일, 차이0 |
| 전체 전파 vs 1 step 후 재개 | 초기 상태·최종 상태·norm history 모두 비트 단위 동일 |
| 파일럿 norm drift | 2.220446049250313×10⁻¹⁶ |
| 집중 코드 검증 | 중복을 제외한 test method43개 통과, skip0 |
| Fortran 전체4 query | 88.923초, 최대 child RSS86,292KiB |
| C++ 첫 query 실행 | supervisor35.925초, 최대 child RSS85,616KiB |

동일 첫 query의 두 raw attempt 시간 합은 **Fortran2스레드22.288초, C++1스레드35.002초**였다. 이 1회 관측의 시간 비는1.5704다. 스레드 수가 다르고 반복 측정·분산 평가가 없으므로 확정 benchmark나 backend만의 가속률로 해석하지 않는다. Fortran 실행은 실제 Cartesian specialization, 2,239,488/3,499,200 radial pairs를 처리했다. 순수 synthetic 결과를 물리 실행으로 계산하지 않았다.

이 짧은 전파는 연결·재개 기능의 acceptance다. 시간 수렴, 독립 ODE reference, 긴 window 또는 실제 capture 정확도 인증을 대신하지 않는다. 별도 선택 부분공간 population은 결과 파일에 시험 진단으로만 저장했다.

## Dropbox·Google Drive 재조사

SHA256으로 중복을 구분해 **SQLite11종**을 실제로 읽었다: CR v1–v6, 별도 NUMERICS 중간본, HE v1–v3, WU088 acquisition v3. SQLite integrity는 모두 정상이다. CR v3의 기존30개 테이블은 이후 판본에서 schema와 전체 행이 그대로 보존됐다.

현재 CR31개 선정 문헌과 추가 업로드4건은 반영돼 있다. 오래된 `sources/report_gaps`의 미확보 표기를 현재 미확보 DOI 목록으로 재사용하면 안 된다. 다만 역사적 방법 문서5개에서 31-work corpus 밖 DOI11종을 추가 확인했다. 별도 CSV에 문헌 언급으로 기록했고, 새 원문 확보나 내용 검증으로 계산하지 않았다.

HE v3는 논문24편·dataset6·code9의 선정39개 payload 모두 byte/hash 일치가 확인됐다. 후속 B1 정정에서는 P04 “표 없음”이 잘못된 판정이었다. native5keV/u 표63개 cell 확보가 최신 상태다. 단위·lab/CM·target-state 비교 권위와 일부 저자 raw는 여전히 미해결이다. WU088 원래 deep-research DB bytes도 복구되지 않았다. 손상된 NUMERICS v1은 실패 이력으로 남기고, 대체 v2의 실제 ZIP과 별도 DB를 확인했다.

Drive 관련 metadata705개, Dropbox347개를 정규화했다. provider 간 복제본이 있으므로 합계1,052개가 서로 다른 데이터1,052종이라는 뜻은 아니다. **Drive의 binary folder 목록은1,000개 상한 이후 continuation을 주지 않아 전 계정의 모든 binary DB 전수 조사는 확정할 수 없다.** Dropbox의 해당 검색 pagination은 끝까지 확인했다. 삭제본·모든 과거 revision·모든 원문 전체의 새 과학적 재검증은 이번 감사 범위가 아니다.

## 맨 처음 프롬프트의 단계는 전부 끝났는가

**아니다.** 가장 이른 첨부는 HE 원자료 복구 계약이고, 현재 CR 연구 계약과 다르다. 이를 섞지 않고 HE17절+A–H8개, CR37절+10 STEP, 합계72개 항목을 각각 증거와 대조했다. 감사 matrix는 R4T 기준이며 이번 R4U 진전은 별도 실행 증거다.

| 연구 단계 | 현재 상태와 필요한 다음 증거 |
|---|---|
| 원자료·DB·기존 결과 보존 | 선정 corpus 범위 확인. 더 넓은 방법 문헌·일부 원 DB/수치 원자료는 남음 |
| 유한 모형의 관측량·국소 변화율 이론 | 조건·정의역을 명시한 증명 있음. 완전한 물리적 capture 인증은 아님 |
| HPC 물리 연산자·전파 연결 | 이번에 구현하고 제한된 실제 파일럿 통과 |
| G02 독립 Sdot/FD ladder | 전체 물리 검증 미실행. 이번 backend parity로 대체하지 않음 |
| G03/G04 연속 tail 제어 | 제한된 점 자료·reference bound. 물리 complex interval enclosure 미완성 |
| G06/G11 nested window·양쪽 tail | ±16/20/24/32 확장 전파·오차 폐쇄 미실행 |
| G12 독립 전파기 | 실제 동일 IVP의 독립 방법 비교 미실행. checkpoint 일치는 다른 검증임 |
| 상태·metric transfer | 정리의 실제 모형 대입·오차 합산 미완성 |
| G13 고차 l·B1/B2/B3 | backend·수치 기저 검증·완전성 확인 남음 |
| all-bound·b-grid·단면적 | 선행 gate가 열려 있어 미실행 |

이전 error-budget의 named-reference bridge 표기는 최신 정확 유리수 **25227/50=504.54**로 동기화했다. 예전55408/11 값과 직접 출처는 history에 보존했다. 개선된 bound도 목표를 통과하지 않으며, 기존 B0 total budget에 합산할 수 없다.

## 실행 환경과 다음 순서

실제 로컬 quota는8 CPU, RAM cap8GiB였다. NCP에 연결된 실행 채널은 확인되지 않았다. OpenMPI5.0.11·mpi4py 로드는 확인했지만 로컬2-rank launcher는 root 보호로 차단됐고 우회하지 않았다. 따라서 **MPI 물리 실행, NCP64 실측 및 scaling은 NOT_RUN**이다.

다음 순서는 (1) 일반 사용자 NCP에서 동일 입력 MPI/Fortran parity 및 topology별 반복 측정, (2) 독립 Sdot·signed48 최소 구분 실험, (3) 같은 IVP의 독립 전파기와 첫 nested window, (4) complex weak-residual/enclosure·state-transfer·total-error ledger, (5) higher-l와 B1–B3다. 새 host에서는 native build와 실행 manifest를 새로 만들고, 기존 checkpoint를 자동 승계하지 않는다. 현재 구현의 CLI와 source/input/native payload를 패키지에 넣어 재구현 없이 이 순서로 이어갈 수 있게 했다.

DBv7에는 DB 감사11행, 계약 감사72행, 운영 검증4행을 추가했다. 기존 v6의34개 테이블·3,168행과 연구 claim36개·gap13개는 그대로다. 최종 DB SHA256은 `43eccec81e0c82f82d06128d4a04523e412279169a7b357ebfff4c2d4ed62d93`이다.

**유지 상태: production=HOLD, capture=false, all_bound=OPEN, b_grid=NO_GO.** 소프트웨어 연결과 실제 파일럿의 성공, 남은 과학적 검증을 각각 기록했다.
