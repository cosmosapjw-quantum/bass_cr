# C21H GitHub 재개 intake — 2026-10-19

현재 branch/PR/태그/릴리스 inventory를 먼저 읽었다. `bass_cr` PR84 head는 `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5` 그대로이며, 조회한 현재 refs/PR/releases에서 **새 C21G native 실행 증거는 발견하지 못했다**. 이것은 NCP 파일시스템의 부재 판정이 아니다.

| Repository | 현재 branches | 모든 상태 PR | tag refs | releases | 끝 확인 |
|---|---:|---:|---:|---:|---|
| bass_cr | 161 | 84 | 1 | 1 | branches 100+61; PR84+0 |
| rei_bianchi | 247 | 205 | 18 | 0 | branches100+100+47; PR100+100+5 |
| vigilode | 147 | 71 | 0 | 0 | branches100+47; PR71 |

`tags` collection URL은 connector400으로 거부됐고 허용되는 실제 `git/matching-refs/tags/`를 읽었다. 숫자는 각각 반환된 완전 배열/마지막 page<100에 근거한다. 모든 역사 branch의 모든 blob을 읽었다는 뜻은 아니다.

## 새 VigilODE 자료와 runtime 분리

[PR71](https://github.com/cosmosapjw-quantum/vigilode/pull/71)의 현재 head는 `0bab431e1031f86eb3ddb44371240bce49ae2376`; base는 `a21d573980f66fe02891bd216153443b5352f921`이다. 현재 actual diff는 10개 추가 파일이며 solver source 수정은 없다. PR body의 6개 설명 이후 CI workflow와 세 run receipt가 추가됐다.

두 CSV를 GitHub에서 base64로 읽고 decoded 원본 바이트를 create-only 저장했다. 전체 SHA256, Git blob SHA, CRLF, row 수와 주요 통계를 실제 계산했다.

| 원시 CSV | bytes | rows | SHA256 | 측정 source |
|---|---:|---:|---|---|
| run1 endpoint | 52654 | 154 | `8a78b5a9c9b9e37dcc599efc7a348457437f606399d2bf236759b7e02d14909c` | `ccaeaa50beb4580505a36d25ccb919ec3ca38c7f` |
| run2 CT | 1005255 | 2700 | `03eda7909f39c467d1ddce7990dd2707b94a4dbb9bde5e036e21f1cf9435e2fa` | `8a8bd409b1d96c7b7421f496d229e119fd3d284e` |

154개는 모두 completed/deterministic이며 endpoint WRMS+empirical spread 최댓값은 0.9917799399710141이다. CT는2639 ok/54 refused/7 solver_failure; ok중 R_up≤1/10/100은2329/2580/2626이다. fast-ctl-pi144개 모두R_up≤1이며 적용가능한 시험subset에서만의 결과다.

`prothero-robinson-nl/uniform101/rtol1e-8/h0_scale1`에서 direct-grid R_up=6.632710004483773e-7, dense-off=1751.990412875421, dense-enforce=1.0933030660056111을 raw에서 재계산했다. 세 행 모두status=ok이므로 실행성공과 요구출력격자정확도는 별도 gate다. R_up은 경험적 reference radius를 포함하는 지표이며 연속시간 error bound가 아니다.

최신 GitHub Actions run39252371864의 `status.json`은 `BOOTSTRAP_ONLY`, `benchmark_executed=false`다. host.txt가 가리키는 실행 checkout은 `c2488199eedc40bb6b563dd4e14867771d24f7c6`, 기록시각은12:28:58UTC이다. 새 solver comparison 완료로 분류하면 안 된다. run1/run2의 측정commit을 a21d573 또는 PR71게시head로 바꾸지 않는다. 원저 상세 profiler, reference, paired timing 데이터가 CSV에 없는 제한을 유지한다.

## rei_bianchi의 변경 범위

고정 native owner `6ea2b1b4b3875c9163cafc45efe720afded43fc4`는 actual GET에 존재하며 tree=`2a695e87f9fe89f82f599b34569cebd0880bcfa8`, commit시각2026-10-16T01:10:22Z이다. 현재 main은 `ae3402713c4b6530ab2b27f008f5f5d5c6a999ed`(2026-08-11)로 이 owner보다 오래됐다. 현재 PR206 BR05, PR205 RUN16, PR199 age-envelope, PR198 V14에 새 결과/코드가 있으나 별도 fixture와 native owner/연구 lane다. 해당PRbody를 실제 읽어 범위를 분리했으며 C21G통과결과로 재표시하지 않았다. 이 다른lane 변경은 고정된 owner 바이트를 자동 교체하지 않는다.

## 보존·범위

- 원복/merge/push/실행/기존 evidence 수정0. 이 폴더의 현재 intake와 다운로드만 새로 생성했다.
- `GITHUB_INTAKE.json`: 모든 목록/HEAD/분류/한계. `VIGILODE_CSV_INTAKE_VALIDATION.json`: 실제 CSV 검산 결과.
- 원본CSV는 decoded `.csv` 두 개다. `.b64`는 다운로드 중간자료이며 별도 원시 캠페인이 아니다.
- 현재 NCP resource/dirty files/watcher/checkpoint는 이 GitHub intake로 확인되지 않았다.
- 조사대상은 현재task의 세 링크된repository다. unreferenced/deleted objects, 다른저장소, unpublished NCP disk와 모든역사branch blob에 대한 전역 부재 증명은 하지 않는다.

