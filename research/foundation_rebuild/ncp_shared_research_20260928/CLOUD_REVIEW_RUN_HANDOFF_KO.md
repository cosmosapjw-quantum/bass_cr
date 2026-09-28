# Cloud Codex: 구현된 R3 점검·필요 수정·cache-only 실행

역할: CLOUD_REVIEW_REPAIR_EXECUTOR. 주요 구현은 ChatGPT에서 완료했다. 새 코드가 없다는 전제로 전체 기능을 다시 만들지 않는다.

Repository cosmosapjw-quantum/bass_cr. 사용자에게 전달된 PUBLICATION_RECEIPT의 implementation branch/HEAD/tree를 exact 기준으로 사용한다. 원 main/source worktree를 바꾸지 않고 별도 clean worktree를 사용한다. 이미 동일 worktree가 있으면 identity/status를 확인해서 재사용하며 지우지 않는다.

## 읽을 최소 자료
1. AGENTS.md와 docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md
2. 이 디렉터리의 IMPLEMENTATION_RESULT_KO.md, IMPLEMENTATION_MANIFEST.json
3. runtime_r3/{cache_bridge.py,metric_diagnostics.py,run_cache_audit.py}; 문제와 관련된 integrity.py/tests만 추가로 읽는다.

## 이미 여기서 확인한 범위
실제 저장297task/2673array를 검증했다. finalized evidence를 두 fresh output으로 원 bytes/IDs 그대로 재사용하는 테스트, source/context/payload/ZIP/NPY 변조 negative tests와 noncommuting whitening 검사를 통과했다. 저장 다섯 sentinel의 기존 residual은 그대로 재현됐다. 클라우드 실행이나 독립 심사까지 끝났다고 가정하지 않는다.

## 점검 및 실행
- 원격 branch/HEAD/tree를 확인하고 구현 manifest와 실제 파일 identity를 비교한다.
- 새 native build 또는 scientific evaluator 경로가 없고 source/thresholds가 그대로인지 관련 diff를 한 번 집중 검토한다.
- Python>=3.11, NumPy2.3.5, SciPy1.17.0의 준비된 환경을 사용한다. 없으면 정확한 환경 blocker를 보고한다. 기존 시스템을 업그레이드하거나 cloud 자원을 변경하지 않는다.
- 신규 코드 변경이 없으면 이미 통과한53개 test를 다시 전부 반복할 필요는 없다. 실제 결함을 수정한 경우 해당 test와 영향 범위를 실행한다. CLI --help와 아래의 actual cloud cache-only run 하나가 새 환경 확인이다.
- 다른 세션의 대규모 job을 시작/정지/이동하지 않는다. 이 작업은 single-process 작은 행렬 후처리뿐이다.

```bash
SIDE=research/foundation_rebuild/ncp_shared_research_20260928
ROOT="$HOME/.local/state/bass_r3"
mkdir -p "$ROOT/runs"
OUT="$ROOT/runs/cache_audit_$(date -u +%Y%m%dT%H%M%SZ)"
# BASS_R3_PYTHON은 필요할 때 이미 준비된 venv/bin/python 경로로 지정한다.
bash "$SIDE/run_reviewed_r3.sh" "$OUT"
```

동일 implementation/input/reader environment의 결과가 이미 존재하면 duplicate run하지 말고 그 결과 identity를 반환한다. 출력 경로 충돌을 이유로 원 폴더를 삭제하지 않는다.

실패 시 첫 실패와 partial output을 보존한다. 재현된 in-scope implementation/environment wiring 오류는 수정 가능하지만 scientific source, threshold, input pins의 임의 변경은 금지한다. '통과'를 위해 source pin을 현재 값으로 덮거나 native fallback을 추가하지 않는다. 수정 commit과 변경 test 결과를 반환한다.

## 반환과 stop
R3_RETURN.json, CACHE_AUDIT.json, IMPORT_BRIDGE.json, METRIC_DIAGNOSTICS.json, READER_ENVIRONMENT.json, OUTPUT_MANIFEST.json을 보존한다. 원 operator bytes는 기존 repo archive에 있으므로 같다는 이유로 GitHub에 다시 중복 저장하지 않는다. 필요하면 output directory의 portable ZIP을 만들고 manifest/hash를 남긴다.

자기 implementation branch에 별도 evidence/<run_id>/와 review/repair receipt만 non-force push한다. 비밀정보 검사 후 업로드하고 remote ref/tree로 확인한다. source 변경이 있었다면 manifest도 함께 갱신한다. R1 publication과 provider restore를 혼동하지 않는다. create-only Drive/Dropbox 권한은 기존 승인 범위지만 cloud 자격증명이 없으면 blocker로 남기고 ChatGPT 연결 도구가 처리할 수 있게 ZIP을 반환한다.

완료 상태: R3_CLOUD_REVIEW_AND_CACHE_AUDIT_COMPLETE 또는 R3_CLOUD_BLOCKED.
반환 항목: implementation HEAD/tree, review finding, changed files, 실제 실행한 test/command/exit, cache count/hash, 다섯 metric 결과, reader environment, 새 native evaluations=0, publication/backup receipts, next gate.

이후 중단한다. capture/F2/F3/full trajectory/b-grid를 시작하지 않는다. 이전3600초/4000원 one-shot은 이미 소비됐다. R3 결과는 read-only evidence reuse의 검증이지 original R2의 generic interrupted native resume까지 수리했다는 뜻이 아니다.
