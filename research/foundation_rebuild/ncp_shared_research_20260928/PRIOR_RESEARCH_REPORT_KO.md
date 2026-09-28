# NCP 3-session 연구 루프: 공유 자원과 이론적 DAG 단축

## 결론

세션별 최대 병렬도를 각각 키우는 대신, 호스트 전체 CPU/RAM lease를 하나로 관리하고 benchmark는 독점 구간에서 측정해야 한다. bass_cr의 다음 수정은 resource grant 분리와 fresh-output resume identity 수리부터 시작한다. 과학 수식 수준에서는 기존 F1 reducer의 요청 의존성을 유지하는 lazy metric evaluation, same-center 공통부분 추출, 정확한 평면 반사대칭 sector, finite-span observable 후처리 분리가 유효한 후보다.

이번 연구에서 실제 수행한 것은 GPT-6 research/coding harness 원본 검증·선택적 독서, 세 관련 repo 자료 조사, SciSpace 문헌 탐색, Wolfram exact algebra 두 회, 원 TP2D archive task counting, 원 engine builder의 fake-compiler 최소 재현, read-only inventory 도구와 자원모형 16개 신규 test다. NCP scientific 계산·프로세스 변경·resource 설정·grant 수정·repo push는 하지 않았다.

## 핵심 산출물

| 항목 | 결과 | 근거 범위 |
|---|---|---|
| WU088_HH와 BASS 동시 간섭 | HH M3B benchmark가 같은 VM/cgroup의 BASS pool 진입으로 중단됐다는 게시 증거 확인 | 원 repo 보고; 현재 live PID는 미관측 |
| R2 full task count | 297개 | exact archive와 formula로 직접 계산 |
| Lazy metric prefix | historical selection 유지 시 201개 | 현재 F1 reducer의 모든 representative full11 검사를 유지; 다음 contract 필요 |
| Same-center 공통부분 | 호출 594→54 | 하위 호출 수 90.91% 감소; wall speedup 미측정 |
| Planar even sector | cross pair 81→49, finite dimension18→14 | 조건부 수학적 불변부분공간; full18 contract는 그대로 |
| Resume identity | 동일 source/binary/env, output path 변경만으로 engine identity/context가 달라짐 재현 | 원 builder+fake compiler; 실제 native 계산0 |
| Preflight typo | MemTotal key가 MemTota가 되어 KeyError 재현 | control25ba handoff의 snippet; source 변경0 |
| Projector/metric/residual | exact Wolfram 결과 보존 | toy exact algebra 및 직접 유도; 물리 production 인증 아님 |
| Read-only sampler/helpers | 16tests PASS, CLI smoke PASS | 이 sandbox; NCP에서 아직 실행하지 않음 |

## 먼저 바로잡는 상태

원 R2의 최대60 workers는 전용 VM 전제다. 다른 workload 사용량을 보지 않는 이 규칙을 세 코드가 각각 적용하면 충돌한다. 현재 guard는 affinity64를 요구하므로 외부 taskset18만 적용하는 방법도 맞지 않는다.

저장 task가 존재한다는 사실과 fresh output에서 resume가 성공한다는 사실은 다르다. 원 builder가 `argv`의 output path를 engine identity에 넣고 R2가 새 out/engine을 다시 빌드하므로, 기존 exact-context gate는 재개를 거절할 수 있다. 앞선 대화에서 resume가 이미 보장된 것처럼 설명한 부분은 이 경로에 대해 정정해야 한다.

이전 final audit ETA 18–35h/중앙24–28h는 아직 정의되지 않은 후반 basis, all-bound, b-grid 작업량과 실제 scaling으로 뒷받침되지 않았다. 현재 검증된 일정으로 사용하지 않는다.

## 문헌의 역할

Dominant Resource Fairness는 CPU/RAM의 dominant share를 함께 다루는 공정성 출발점이다. 이번 단일 사용자 3-job 목적에서는 fairness만으로 throughput/makespan 최적성이 보장되지 않아 목적함수를 별도로 둔다. SciSpace가 찾은 co-location/interference-aware 연구도 독점 성능과 공유 성능을 분리해야 함을 뒷받침하지만 그 논문의 배속을 NCP에 적용하지 않았다.

Linux cgroup v2/PSI 및 SciPy parallel execution 공식 문서는 resource admission·측정 설계의 근거다. 통계모형의 가정이 아니라 실제 호스트에서 읽어야 하는 제약이다. 이를 읽는 도구만 제공하며 현재 프로세스를 다른 cgroup으로 옮기지 않는다.

Schrödinger FE a posteriori error-control 연구와 MORe DWR는 residual/observable 중심으로 expensive refinement를 줄이는 경로다. MORe DWR의 heat/elastodynamics 결과를 이 moving-basis collision code에 직접 이식했다고 주장하지 않는다. 필요한 domain/reconstruction/stability 조건은 MATHEMATICS_KO.md에 명시했다.

## 재현과 반환

1. `python3 -m pytest -q -p no:cacheprovider tests` : 도구/자원모형16개.
2. `python3 scripts/reproduce_identity_issue.py` : 실제 원 builder의 path-dependent identity를 fake compiler로 재현.
3. `python3 scripts/analyze_archive.py --archive /실제/TP2D_RETURN.zip` : native 실행 없이297/201 counts 재계산.
4. `python3 scripts/collect_inventory.py --out /새/파일.json` : 호스트에서3회 read-only sample; 자동탐지가 불완전하면 `--session PID:label` 지정.

TP2D archive는 source SHA로 고정돼 있지만 이 작은 연구 packet에32MB archive를 중복 포함하지 않는다. `evidence/snapshot`은 필요한 기존 code/contract exact bytes만 포함한다. `SANDBOX_INVENTORY_SMOKE.json`은 NCP evidence가 아니다.

다음 한 단계는 한 Codex 세션이 `CODEX_READ_ONLY_COORDINATOR_PROMPT_KO.md`를 수행해 세 PID↔repo↔stage와 cgroup 자원 상태를 반환하는 것이다. 그 결과 없이 live worker 배분을 바꾸거나 paid benchmark를 실행하지 않는다.

## 상태

연구 산출: COMPLETED_SCOPED_RESEARCH.
실제 cloud 배포/속도 개선: NOT_EXECUTED_NOT_MEASURED.
검토 유형: OWNER_SELF_REVIEW. 별도 reviewer 프로세스의 독립 검토를 했다고 주장하지 않는다.
원 claim ceiling: capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO, original_capture_gap_resolved=false, continuous_global_supremum_bound=false.
