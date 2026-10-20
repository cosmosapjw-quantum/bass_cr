# C21I callback optimization research

이 단위는 C21H의 원 물리 RHS와 event driver를 유지하는 선택형 callback 최적화다. H runtime 8개는 변경하지 않았다. `vectorized`는 cohort Jacobian을 축소 행렬에 직접 조립하고, `vectorized_exact`는 같은 cell의 정확히 같은 입력에서 성공한 RHS 결과를 재사용한다. Native 재사용은 별도의 출처·수명·deadline 계약을 통과해야 한다.

**지역 구현과 제조 검증은 완료됐지만 원격 GitHub 게시는 아직 완료되지 않았다.** 최신 H `create_tree` 요청은 `user rejected MCP tool call`을 반환했고 tree SHA가 없었다. I 원격 write는 0이다. 현재 상태는 publication receipt와 외부 최종 delivery receipt로 확인한다.

## 읽기 순서

1. [연구 결과와 채택 범위](C21I_RESEARCH_REPORT_KO.md)
2. [실행 manifest](EXECUTION_MANIFEST.json), [검증 범위](VALIDATION_SUMMARY.json), [DAG](DAG_C21I.json)
3. [같은 binary의 32개 제조 적분 분석](evidence/paired_pilot_analysis_01/PAIRED_PILOT_REPORT_KO.md), [FD 부모 연결 2개](evidence/optimized_fd_followup_01/RECEIPT.json)
4. [게시 영수증](PUBLICATION_RECEIPT.json), [백업 snapshot 영수증](BACKUP_RECEIPT.json), 최종 외부 delivery receipt
5. [NCP 실행 인계](CODEX_HANDOFF_KO.md)

## 구현과 결과

| 구성 | 범위 |
|---|---|
| `optimized_adapter.py` | 원래 산술·FD node 순서를 유지한 직접 축소 Jacobian, cell별 scratch, 선택형 exact RHS cache |
| `native_cache_contract.py` | 고정 source/provider/process/binary/config, 실제 call cap, deadline, 종료 전 hash 확인 |
| `run_optimized_pilot.py` | H의 budget·cleanup·create-only·FD 부모 계약을 유지하는 실행 경로; 최신 H/I PUBLISHED receipt 필요 |
| `block_solver/` | 실제 Rust Schur/JVP 제조 커널. 현재 H backend와 연결하지 않은 독립 prototype |

같은 새 bridge binary의 32개 제조 적분은 모두 COMPLETE였다. 24개 비자기 모드 비교에서 accepted trace·물리 출력·수지·FD node·Rust counter가 원 H와 같았다. Exact 실제 RHS는 VigilODE 423→372, Diffsol 74→71이었다. 추가 FD 부모 연결은 backend별 한 번씩 2/2 COMPLETE였다. 이 34개 job의 실제 native 호출은 0이다.

후반 세 paired process 배속 중앙값은 VigilODE vectorized 0.845647 / exact 0.920985, Diffsol vectorized 1.045230 / exact 0.985440이다. **이 작은 제조 문제의 일관된 전체 가속은 확립되지 않았다.** Component 및 standalone 선형대수 결과를 native/전체 trajectory 가속률로 이전하지 않는다.

`native_chemistry=NOT_RUN`, `native_performance=NOT_EVALUATED`, `global_error_bound=null`이다. Population, exact Y=0, 15개 ledger, accepted output, 원 error norm을 유지한다. Clipping/floor/silent fallback을 추가하지 않는다. 독립 검증 전 기존 HOLD 항목은 유지한다.
