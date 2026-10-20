# C21I: callback 벡터화·exact RHS cache와 실행 비용 검증

## 목적과 변경

C21H의 원 RHS, cell/birth 순서, accepted state, ledger와 오차 기준을 유지하면서 Python callback의 중복 계산과 Jacobian 조립 비용을 줄인다. 고정된 C21H source를 private module로 읽고 세 가지 모드 `baseline`, `vectorized`, `vectorized_exact`를 제공한다.

- `optimized_adapter.py`: FP64 원소별 연산 순서를 유지한 reduced Jacobian 벡터화와 per-cell successful RHS exact cache. Cache key는 전체 binary64 t/state·ledger·signed zero와 불변 scope를 포함하며 소유 복사와 bounded LRU를 사용한다. 실패·비유한 값·근사 state는 재사용하지 않는다.
- `native_cache_contract.py`: source-defined 원 NativeMicro/private H wrapper, pinned owner/build, 파일 identity, live deadline과 terminal full hash를 확인하는 선택적 native cache admission. 실제 RHS 요청·평가·cache hit를 구별한다.
- `run_optimized_pilot.py`: 원 H의 예산·cleanup·create-only output·FD parent 검사를 private binding으로 재사용한다. I source와 mode를 FD identity에 포함하고, native 실행에는 최신 외부 PUBLISHED H/I receipt와 detached I content checkout을 요구한다.

Runtime은 위 3파일이며 execution manifest SHA256은 `f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec`다. H의 runtime source, VigilODE pin, Diffsol lock, rtol/atol은 변경하지 않았다.

## 실제 검증과 범위

동일한 실제 bridge binary를 사용한 제조 pilot **32 jobs가 COMPLETE**였다. 원 H와 후보의 accepted trace, endpoint, 물리 수지, FD nodes, Rust work counter에 대한 bitwise 비교가 통과했고 실행 전후 source identity가 일치했다. Exact mode의 실제 원 RHS 평가는 VigilODE **423→372**, Diffsol **74→71**로 줄었다.

Matching base를 연결한 **FD followup 2개**도 완료했다. 새 연결부의 focused 계약과 C9 검토 근거를 보존하고, 기존 유효한 검증은 재사용했다. 이 결과의 **native 호출은 0**이며 실제 native chemistry·NCP 결과가 아니다. Clipping/floor/silent fallback을 추가하지 않았고 `global_error_bound=null`을 유지한다.

## 성능 판정

후반 3개 paired process 비교에서 원 H 대비 배속 중앙값은 다음과 같다. 1보다 크면 해당 비교에서 빠르다는 뜻이다.

| Backend | vectorized | vectorized_exact |
|---|---:|---:|
| VigilODE | 0.845647 | 0.920985 |
| Diffsol | 1.045230 | 0.985440 |

RHS 감소가 전체 process 가속으로 일관되게 이어지지 않았다. **전체 가속은 확립되지 않았으며**, 느려진 결과·반복값·분산·실패 및 cleanup 비용을 함께 보존한다. Component callback 결과나 반복점 warm cache 결과를 실제 ODE/native 성능으로 확대하지 않는다.

`block_solver/`의 Schur/JVP/exact factor-cache는 실제 standalone Rust 제조 검증을 마친 별도 prototype이다. **현재 H backend에 연결되지 않았으며** 이 PR의 native 가속 경로로 주장하지 않는다.

주요 근거는 `EXECUTION_MANIFEST.json`, `VALIDATION_SUMMARY.json`, `DAG_C21I.json`, `evidence/paired_pilot_final/SUMMARY.json` 및 각 focused/FD 실행 영수증이다. NCP의 다음 작업은 현재 자원 확인, published content의 locked compile, 실제 발견한 작은 호환 수정과 bounded native 실행이다.

## 게시 의존성과 현재 상태

이 문서는 **C21H 별도 draft의 게시를 부모 의존성으로 하는 C21I draft PR 본문**이다. H는 PR84 branch 위에, I는 실제 게시된 H 위에 순서대로 연결해야 한다.

현재 최신 H 594파일 `create_tree`는 정확히 `user rejected MCP tool call`, `isError=true`를 반환했고 tree SHA와 상세 이유는 없었다. 이후 commit/branch/PR write는 없었다. 이를 자동 승인 심사의 거절로 바꾸어 설명하지 않는다.

**H/I remote content commit과 PR은 null이며, I GitHub write는 0이다.** 최신 거절 이후의 명시적 재승인과 실제 ref/PR 확인 뒤 게시를 재개한다. 아직 존재하지 않는 PR 번호나 I content commit을 지정하지 않는다. 실제 content/ref/PR ACK 및 문서 receipt commit은 게시 단계에서 별도로 기록한다.
