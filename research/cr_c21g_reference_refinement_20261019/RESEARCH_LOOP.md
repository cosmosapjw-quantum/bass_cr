# C21G 연구 루프 기록

단계 번호와 이름은 현재 선택된 **PhysMath Research Loop 1.3.0**의 `references/STAGE_GUIDE_KO.md`를 따른다. 이 기록에서 완료는 C21G의 이론·reference control·독립 진단·제조 검증이라는 명시한 범위의 완료다. 새 native 실행의 물리 검증과 수렴 검증, 전체 연구 목표, 게시·백업은 각각 독립 상태로 남긴다.

현재 새 소프트웨어 검사 35개(9+9+14+3), 제조 analytic 9 cases, 제조 wiring smoke 3 jobs가 PASS다. 새 native reference 8개와 refinement 4개는 `NOT_RUN`이다. 실제 PR84 게시와 새 ZIP의 세 제공처 create-only 저장 응답을 확인했다. `PUBLICATION_RECEIPT.json`, `BACKUP_RECEIPT.json`, `DAG_C21G.json`에 실제 commit·ID와 검증 수준을 기록했다.

## 이론 R1–R10

| 단계 | 이번 범위의 작업과 상태 | 근거 | 게시·백업 |
|---|---|---|---|
| R1 연구 목표·계약 | GitHub·백업의 새 결과를 먼저 확인했다. 확인 범위 내 새 C21F native 결과는 없었고, reference 오차와 이산화 오차의 분리 및 128/256 refinement를 이번 목표로 고정했다. 범위 계약 완료. | `evidence/intake/`, `README_KO.md` | PUBLISHED_PR84 / BACKED_UP_THREE_PROVIDERS |
| R2 문헌조사·기존 성과 재사용 | PR82/83의 원시 근거를 재사용하고 SciPy 1.17.0 문서·구현 및 Cao–Petzold 원문을 조사했다. 이 계산 계약에 필요한 조사 완료이며 전 분야 문헌조사를 주장하지 않는다. | `theory/LITERATURE_INTAKE.json`, `theory/THEORY_REFERENCE_ERROR_KO.md` | 동일 |
| R3 주장·전제 정합성 검토 | 고정 9/27 cohorts, source·geometry·원 kernel·binding convention을 유지한다. 국소 허용오차, 경험적 reference 차이, 전역 오차 상계를 구별했다. 전제 검토 완료. | `campaign_contract.py`, `EXECUTION_MANIFEST.json`, 이론 문서 | 동일 |
| R4 발산적 가설·모델 탐색 | 허용오차 ladder와 step cap, log-survivor와 EOS 관측량, reference 없이 계산하는 두 스케일 계수 진단을 구성했다. 이번 수치 판별에 필요한 후보 탐색을 완료했고 광범위한 물리 모델 탐색은 수행했다고 주장하지 않는다. | 이론 문서, `diagnostics.py`, `campaign_contract.py` | 동일 |
| R5 구성적 수학 유도·증명 | Tau–count–log 관계, 정확한 EOS 차분, 가정된 reference 상계에 조건부인 차수 구간, Ahat/Bhat 식과 세제곱항의 오염식을 유도했다. 명시한 전제 아래 완료. | `theory/THEORY_REFERENCE_ERROR_KO.md`, `theory/WOLFRAM_VERIFICATION.json` | 동일 |
| R6 독립 검증·적대적 심사 | 독립 이론·과학 검토를 수행했다. 실행 gate, 유효 cohort의 log 누락, binary64 비교 명칭, receipt/payload 결합에 관한 S1–S4를 모두 교정하고 닫았다. 범위 내 검토 완료. | `evidence/review/SCIENCE_REVIEW_KO.md`, `evidence/tests/` | 동일 |
| R7 판별 검증·경량 계산 | 새 제조 analytic 9 cases PASS, 실제 wall time 1.9097576049971394 s. 기존 endpoint에 새 두 스케일 계수 진단을 적용했다. 이론식의 기호 검증과 경량 계산 완료. | `evidence/analytic_reference/ANALYTIC_REFERENCE_CHECK.json`, `evidence/baseline_coefficient/BASELINE_COEFFICIENT_DIAGNOSTIC.json` | 동일 |
| R8 과학적 결과 판정 | 기존 native 자료에서 Ahat은 약 −7.654×10⁻⁵로 음수지만 n⁻² drift는 검증되지 않았다. Common_ic의 Bhat은 미안정이다. 제조해의 binary64 차이와 경험적 ladder 반경을 전역 인증으로 승격하지 않았다. 이번 근거의 판정 완료, 새 native 판정은 대기. | 이론 문서, 계수 진단, `global_error_bound=null` | 동일 |
| R9 이론 정식화·계산 연결 | 유도식을 vector atol의 좌표 축소, 안정한 endpoint 비교, 독립 수지 재계산, 조건부 차수 구간과 고정 job 계약으로 연결했다. 구현 가능한 계산 정식화 완료. | `diagnostics.py`, `campaign_contract.py`, `run_campaign.py`, `analyze_campaign.py` | 동일 |
| R10 연구 정리·체크포인트 | 이론·새 증거·실행 source identity·남은 의무·재현 및 인계를 정리했다. PR84와 새 ZIP 세 제공처의 실제 응답으로 이번 연구 체크포인트 전달을 완료했다. | `EXECUTION_MANIFEST.json`, `DAG_C21G.json`, `REPRODUCE.md`, `handoff/CODEX_HANDOFF_KO.md` | PR84 게시 / 새 ZIP 3개 저장처 완료 |

## 코딩 C1–C10

| 단계 | 이번 범위의 작업과 상태 | 근거 | 게시·백업 |
|---|---|---|---|
| C1 목표·기준 결과 설정 | 기존 실행 source/fixture/raw를 기준으로 두 fixture의 고정 reference ladder, native 128/256 refinement, 사전 pilot budget을 정의했다. 기준 설정 완료. | `evidence/intake/`, `campaign_contract.py` | PUBLISHED_PR84 / BACKED_UP_THREE_PROVIDERS |
| C2 코드·수식·데이터 조사 | 원 `reference_tau.py`, `run_experiment.py`, Fixture·NativeMicro 계약과 원시 결과를 수식·ledger·실행 경로에 대응시켰다. Source/data map 완료. | `EXECUTION_MANIFEST.json`, `evidence/intake/SOURCE_LOCAL_VERIFICATION.json`, 이론 문서 | 동일 |
| C3 알고리즘·수치기법 설계 | Full/reduced vector atol, mesh cap, 실제 RHS/provider counters, 안정한 log/EOS 차이, 독립 물리 수지와 차수 진단을 설계했다. 이번 알고리즘 설계 완료. | `campaign_contract.py`, `diagnostics.py`, 이론 문서 | 동일 |
| C4 구현 계획·병렬화 설계 | 8개 reference와 조건부 후속 4개 history, 한 CPU·예산·create-only 출력·재사용 identity를 계약화했다. 원격 자원 할당은 실제 NCP 상태 재확인 후 수행한다. 설계 완료, 원격 실행 대기. | `DAG_C21G.json`, `run_campaign.py`, `handoff/CODEX_HANDOFF_KO.md` | 동일 |
| C5 코드 구현 | 기존 reference control 한 파일의 수정과 새 실행기·분석기·독립 진단·제조 검증기를 구현했다. 여기서 가능한 구현 완료. NCP에 큰 기능 구현을 남기지 않는다. | `EXECUTION_MANIFEST.json`, `run_campaign.py`, `analyze_campaign.py`, `diagnostics.py`, `verify_analytic_reference.py` | 동일 |
| C6 소프트웨어 검증·디버깅 | 새 reference control 9, diagnostics 9, runner 14, analysis binding 3: 총 35/35 PASS. 별도 wiring smoke 3 jobs COMPLETE/PASS, wall time 4.494274969001708 s. 범위 내 소프트웨어 검증 완료. | `evidence/tests/reference_patch/`, `evidence/tests/diagnostics/`, `evidence/tests/campaign/`, `evidence/tests/wiring_smoke/`, `tests/test_analysis_binding.py` | 동일 |
| C7 물리적·과학적 검증 | 제조 analytic 9 cases의 수지·정확해 비교와 underflow/log 기록은 PASS다. 기존 native 물리 근거는 재사용했다. **새 C21G native 물리 검증은 NOT_RUN**이며 제조 검증으로 대체하지 않는다. | `evidence/analytic_reference/`, `diagnostics.py`, `DAG_C21G.json` | 동일 |
| C8 수치 정확도·성능 검증 | 제조해의 binary64 analytic 비교와 기존 결과의 새 계수 분석을 완료했다. Step cap이 실제 grid를 바꾸지 않은 경우 `MESH_CAP_INACTIVE`다. **새 native ladder·128/256 수렴·실행 성능 검증은 NOT_RUN**이며 `global_error_bound=null`이다. | `evidence/analytic_reference/`, `evidence/baseline_coefficient/`, `DAG_C21G.json` | 동일 |
| C9 독립 코드 심사·개선 | 보완 범위를 나눈 독립 심사 후 gate·provenance·metadata 문제를 수정하고 필요한 집중검사로 확인했다. S1–S4 closure를 포함한 이번 심사 완료. | `evidence/review/SCIENCE_REVIEW_KO.md`, `evidence/tests/` | 동일 |
| C10 배포 판정·실행 인계 | 실행 manifest·재현 명령·보존 조건·NCP 인계를 작성했다. PR84 실행 코드와 새 ZIP 세 제공처의 실제 응답을 확인하여 이번 구현 전달을 완료했다. 새 native 실행 완료를 포함하지 않는다. | `REPRODUCE.md`, `handoff/CODEX_HANDOFF_KO.md`, `PUBLICATION_RECEIPT.json`, `BACKUP_RECEIPT.json` | PR84 게시 / 새 ZIP 3개 저장처 완료 |

## 검증 재사용과 실패 구별

기존 C21F Rust compile/tests·Python 56개·24 native histories·27,140 point 감사는 PR82/83 근거를 재사용한다. 이번 재실행 횟수에 더하지 않는다. 새 reference patch 9개, diagnostics 9개, runner 14개, analysis binding 3개는 서로 구별한 소프트웨어 검사다. 제조 analytic 9 cases와 wiring smoke 3 jobs도 별도 집계한다. Analysis binding의 unittest 시간은 0.022 s, process wall time은 0.1276116609951714 s다. 일부 교정에서 얻은 red/green 근거는 보존하지만 모든 검사가 red-first였다고 주장하지 않는다.

현재 확인한 remote quota 0은 실행 환경 의존성이다. Native 과학·수렴 실패를 뜻하지 않는다. 제조 benchmark의 binary64 analytic 비교 명칭 교정은 원 수치를 보존한 metadata·그림 변경이며 ODE 재실행이 아니다. `MESH_CAP_INACTIVE`는 별도 mesh 검증 완료를 뜻하지 않는다. 기존 dirty files·watcher·checkpoint·완료된 C21F 산출물을 보존하고, 새 source/fixture/raw SHA와 실행 상태를 새 create-only 산출물에 기록한다.

## 성과 수용과 남은 의무

이번 수학 성과는 명시한 fixed-fixture 전제 아래의 항등식과 조건부 정리다. 새로운 불가능성 정리·강한 no-go·방법론 novelty를 주장하지 않는다. Native global bound를 수용하려면 별도의 residual·stability tube·roundoff 근거가 필요하다. 차분과 경험적 반경은 정확도 상계가 아니며, 두 스케일 계수에서 zero crossing을 예측하지 않는다.

다음 실행 node는 새 reference 8개다. **8개 모두 operational COMPLETE이고 native_source의 pilot가 READY일 때** 새 FULLMID/hybrid 128/256 네 job을 실행한다. Common_ic의 pilot budget 초과만으로는 native 후속을 막지 않지만 operational 실패는 별도로 차단한다. NCP에서는 실제 자원과 다른 campaign을 확인하고 CPU 55를 제외한 한 CPU를 선택한다. 검증된 기존 native binary를 재사용할 수 있으면 전체 native build를 반복하지 않으며, 필요 시 검증한 새 build 또는 작은 호환성 수정만 수행한다.

Full48, source-age/spectral/angular, Case B, signed Bianchi, full EoR, standalone Grackle driver parity는 해당 독립 검증 전까지 HOLD다. 이 문서의 범위별 완료 표시는 그 목표를 해제하지 않는다.

## 실제 게시 응답

PR84와 실행 코드 commit `e742d44f605c51c06615451774ba90af8f41f622`를 확인했다. 변경90개(새89+기존reference1)의 blob identity가 모두 일치했다. 새 ZIP의 세 provider 응답을 확인하고 전달 상태를 갱신했다. Dropbox의 현재 경로 불일치와 실제 새 저장 위치는 BACKUP_RECEIPT.json에 남겼다. Native 실행 상태는 NOT_RUN이다.
