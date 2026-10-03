# BASS_CR R4AJ: 원자물리 데이터 전용 최종 전달

사용자의 최신 지시: Bianchi 물리는 rei_bianchi에서 처리한다. 이 패키지는 원자 데이터 producer에 필요한 유도·코드·오차·출처만 다음 연구 대상으로 둔다.

1. `atomic_scope/SCOPE_AUTHORITY.json`과 `SCOPE_KO.md`가 소유권의 최신 기준이다.
2. `atomic_scope/ATOMIC_ONLY_DAG.json`이 유효 계획이다. 과거 DAG를 수정하거나 완료로 바꾸지 않았다.
3. `atomic_scope/CODEX_ATOMIC_HANDOFF_KO.md`를 따른다. 통합 v2 patch만 한 번 적용한다.
4. `R4AI_PREVIOUS_REPLY_KO.md`는 사용자가 요청한 직전 보고의 전체 한국어 재출력이다. 그 안의 Bianchi 참조 구현 언급은 과거 기록이지 현재 작업범위가 아니다.
5. `base/R4AJ_v1.zip`에 이번 selector/reference 공진 판별의 실제 과학 결과·코드·시험 및 R4AI 전체부모가 보존돼 있다. source/result 바이트는 바꾸지 않았다.
6. `atomic_scope/BASS_CR_SOURCE_DATABASE_20261003_v23.sqlite`는 v22에 최신 scope만 append했다. 과학 상태 view와 gap13행은 동일하다.

새 과학실행·재시험·m64 prepare는 범위수정 중 수행하지 않았다. 범위/파일/DB/patch 검사만 했다. 원자 데이터와 Bianchi 소비자의 실제 통합 완료는 별도다.

경로 안내: 이 문서의 `base/`, `atomic_scope/`, `verify_package.py`는 전체 배포 ZIP 기준이다. Git에 적용된 scope 문서는 `research/convergence_20261003/r4aj_selector_bridge/atomic_scope_20261003/`에서 읽는다. 전체 부모 archive는 Git 개별 파일 mapping에 추가하지 않고 배포 ZIP에 보존한다.
