# C21F PR82 실행 근거 intake

현재 GitHub와 백업에서 2026-10-18에 완료된 새 NCP 실행 기록을 발견했고, PR82의 **text 167개 전체**를 새로 읽어 원시 바이트를 확인했다. `MANIFEST.sha256`에는 payload 168개가 있으며 이번에 직접 검증한 범위는 **166/168개**다. 남은 두 개는 native 실행 파일이다. Manifest 파일 자체는 별도로 Git blob와 intake 영수증으로 검증했으므로, 확보한 text 파일은 166개 payload + manifest 1개다.

## 실행 코드와 문서의 분기

- 실행 anchor: `f8359232df8d0dd4fe91fcdabeb6701eb06089ba`.
- PR81 현재 head: `249d9b29b0adc5a8cf615a9999065aff26ff6900`. 실행 anchor 이후 변경은 executable manifest·publication receipt·DAG·handoff 등 문서 5개다. 현재 PR82 source의 실행·테스트·의존성 17개는 기존 executable manifest의 바이트·SHA256·Git blob와 모두 일치한다.
- PR82 head: `c4a502e0c931a201edfa3c7046f7a91230c2278f`. 실제 root tree는 `af9db874c235a4140d93d02d1cc9320586fce533`다. Recursive tree가 반환한 top `sha`는 commit ID였으므로 그대로 tree ID로 채택하지 않았다. 반환된 전체 tree 목록의 **1,418개 Git tree object**를 각각 재직렬화해 hash를 계산했고, root와 모든 subtree가 일치했다.
- GitHub compare는 PR81에 대해 `diverged`, ahead 2 / behind 1, merge base `f8359232df8d0dd4fe91fcdabeb6701eb06089ba`를 반환했다. Change list의 169개는 모두 새 실행 evidence 파일이다. 이 목록은 merge-base에서 비교하는 GitHub 결과이며, PR81 문서 커밋까지 포함한다는 직접 tip-to-tip 동치 주장이 아니다. PR81 authority 6개를 별도 경로에 보존했고 자동 merge는 하지 않았다.

## 새로 검증한 원자료

Text 전체 크기는 **23,343,696 bytes**다. 각각 UTF-8 payload, byte length, SHA256, Git blob를 확인하여 원 manifest와 현재 GitHub tree 및 `intake_receipts_01.json`–`08.json`의 기록을 대조했다. 일치하지 않는 파일은 0개다. 영수증 JSON에는 8개 원 intake 파일의 SHA256과 normalized record 전체, 확보한 167개 파일의 개별 identity, 미수신 binary 두 개, 실행 source 17개 및 authority 6개의 검증 결과를 포함한다.

Native binary `build/native_point`, `build/native_point_tests`는 이번에 바이트를 받지 않았다. 두 파일의 원 manifest SHA256·Git blob·크기는 기록으로 남겼으며, 현재 바이트 검증을 주장하지 않는다. 저장 native point 26개 / **27,140개 요청·응답**의 독립 감사는 완료됐고 결과는 `native_point_audit/POINT_AUDIT.json`이다.

## 백업 identity의 근거 상태

기존 실행 archive `C21F_NATIVE_NCP_20261018T1358Z_evidence.tar.gz`는 **7,902,411 bytes**이며 이번 조회에서 두 provider root에 존재함을 확인했다.

| 저장처 | 실제 ID / 경로 | 마지막 수정 UTC |
|---|---|---|
| Google Drive | `1sQiP-1RHuCUaQnNkolLGSsmNfVA-0rjo` | 2026-10-18T13:59:14.777Z |
| Dropbox | `id:BSpOijBcT10AAAAAAD_NlA`, `/C21F_NATIVE_NCP_20261018T1358Z_evidence.tar.gz` | 2026-10-18T13:59:27Z |

통상 archive SHA256 `05bd41fc998c2bda46e7606c07653cd5ab7ea36fa35556c1c480c5ca06384a90`은 원 PR82 `BACKUP_RECEIPT.json`에 기록된 양 provider raw readback 근거를 재사용한 값이다. **이번에는 archive 바이트의 전체 readback SHA256을 다시 계산하지 않았다.** Dropbox content hash `e3b3073f7e4edf1700a943edfab9dd2ed10b0ce262e5a49d408d2b5b93921c08`은 별도 provider hash로 보존했다.

Drive raw fetch는 실제 file reference를 반환했지만 local workspace 경로와 Library ID는 반환하지 않았다. Dropbox archive HTTP 취득은 sandbox 네트워크 권한에 막혔고, 정식 escalation은 자동 승인 검토 모델 용량 문제로 실행되지 않았다. Dropbox text fetch는 5 MiB 제한에 걸렸다. Library exact filename 및 C21F title 검색에서는 새 native archive의 Library ID를 찾지 못했으며, 이는 전체 Library에 없다는 판정이 아니다. 이 한계 때문에 기존 archive와 native binaries의 이번 byte verification은 분리했고, 확보된 GitHub text 원자료로 연구를 진행했다.

## 실행·게시 상태

과거 PR81의 native `NOT_RUN`은 그 문서 제작 시점의 기록으로 보존한다. 새 PR82 evidence는 두 고정 native matrix의 NCP 실행 완료를 담고 있다. 현재 turn의 NCP 자원 inventory는 root가 관측한 quota blocker로 얻지 못했으며, 과거 환경 상태를 상속해 runtime을 판정하지 않았다. 본 intake 단계에서는 새 NCP job, 기존 solver 재실행, patch 재적용, merge, 업로드 또는 기존 raw 변경을 하지 않았다. 이후 새 평가의 게시·백업은 별도 PUBLICATION_RECEIPT.json과 BACKUP_RECEIPT.json에 연결한다.

이 receipt은 원자료 intake와 근거 상태의 구분을 완료한다. Full48, source-age/spectral/angular, Case B, Bianchi, full EoR는 각각의 독립 검증까지 HOLD다.
