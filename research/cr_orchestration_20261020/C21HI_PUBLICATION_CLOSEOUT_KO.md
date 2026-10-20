# C21H/I 게시 마감: 실제 content와 문서 상태

기록: 2026-10-20T10:31:09.900596+00:00. 이번 범위는 physmath-research-loop C10이다.

| 단위 | 실제 content | draft PR | 보존된 전체 tree와 대응 |
|---|---|---|---|
| C21H | `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8` | [PR85](https://github.com/cosmosapjw-quantum/bass_cr/pull/85) | H595, tree `e207fd00c67996514b7ee41cd28f8b0a8d5f79bd` |
| C21I | `fe6bbaec2de5032b938aed0713623b9618ba70e6` | [PR86](https://github.com/cosmosapjw-quantum/bass_cr/pull/86) | I1674, tree `6e33ecfa4b6b5ee427696dc426e5ed58d1403a2f` |

원격 전체 tree identity가 기존 검증된 local tree와 같다. 새 격리 Git 읽기에서 H8/I3 runtime과 두 manifest의 실제 SHA256·길이·Git blob을 대조했다. 기존 payload 전체를 다시 과학 실행한 검증은 아니다. H content는 I content의 실제 부모다. 문서 head는 content commit과 다르며 Native runner는 I content로 detached checkout한 뒤 최신 외부 두 receipt를 받는다.

현재 PR receipt의 `pull_request`를 number·url 객체로 맞춰 원 H handoff의 `publication["pull_request"]["url"]` 접근을 고쳤다. 오래된 현재 미게시 문장을 역사 기록으로 바꾸고 H/I DAG·backup receipt에 실제 게시와 기존 세 저장처 ACK를 반영했다. H 문서 변경은 H branch와 I branch에 동일 바이트로 반영하며, branch merge/rebase/force push를 하지 않는다. 과거 snapshot은 기존 content/doc commit과 변경분 백업에 남는다.

기존 구현·32개 제조 integration 및 FD2개·독립 검토 결과는 그대로 재사용한다. Exact mode 실제 원 RHS는 VigilODE423→372, Diffsol74→71이다. 같은 tiny fixture의 일관된 전체 시간 가속은 NOT_ESTABLISHED이고 native 성능은 NOT_EVALUATED이다. Schur/JVP block solver는 별도 제조 검증 prototype이며 H backend 통합은 수행하지 않았다. NCP에서 큰 기능 구현을 시작할 과제가 아니다.

이번 실행은 Git 객체/문서 identity 대조와 영수증 소비 경로의 작은 확인뿐이다. Rust 재컴파일·callback/ODE benchmark·native 실행은0이다. 과거 거절 응답에 tree SHA가 없다는 사실은 보존하며, 실제 발견한 PR/ref를 그 거절 요청이 만들었다고 추정하지 않는다.

실행·게시·백업·DAG는 독립 축이다. 로컬 구현과 제조 검증 완료, PR85/86 게시 완료, 기존 science payload의 세 저장처 ACK 완료, C10 문서 마감이다. 새 문서 변경분의 실제 ZIP/hash/provider ACK는 `C21HI_PUBLICATION_CLOSEOUT_RECEIPT_20261020.json`가 기록한다. 원 science ZIP을 덮어쓰지 않는다.

NCP는 `NCP_ORCHESTRATION_KO.md`와 수정된 각 CODEX_HANDOFF를 사용해 현재 자원·진행 campaign·dirty files·watcher·checkpoint를 읽고, 실제 할당에서 locked compile과 작은 호환 수정 및 native 실행을 수행한다. H base4와 matching FD최대4, G reference8과 조건부 refinement4, I의 bounded native 비교를 각 계약에 따라 구분한다. 동시 job1, workers1, CPU55보호,300초,200000호출,rtol2e-11,alpha2e-14,step divisor8을 유지한다. Affinity를 독점 할당으로 해석하지 않는다.

Native chemistry/NCP와 새 G reference ladder는 마지막 범위 한정 조사에서 NOT_RUN이다. `global_error_bound=null` 및 Full48/source-age/spectral/angular/Case B/signed Bianchi/full EoR/standalone Grackle parity HOLD를 유지한다.
