# BASS_CR R4AI: local theory / DB-DAG review / Codex handoff

이 패키지는 Bianchi 재이온화용 selected1s source 목적에 맞춘 로컬 reference work와 논문·코드 DB/DAG 재조정 결과다. 전체 물리연구 완료가 아니다.

먼저 `AUDIT_AND_REVISED_PLAN_KO.md`, `DERIVATIONS_KO.md`, `REVISED_WORKFRONT.json`, `CODEX_HANDOFF_KO.md`를 읽는다. `audit/DB_DAG_AUDIT.json`과47행 requirements crosswalk가 기존획득/정책/이론/실제수치상태를 분리한다. 과거파일은 immutable이다.

`local_theory/cr_reion/`은 새 reference package, `runtime_tools/merge_returns.py`는 multi-batch 읽기전용수집기, `legacy_runtime/`은 원본R4AH재현ZIP이다. 새독립test137건과소규모모델계산은evidence에있다. 과거과학시험/shifted적분/M9/D/V는다시실행하지않았다.

`python verify_release.py .`는manifest의payload bytes만 확인한다. 실제runtime은`python tools/unpack_runtime.py --output /absolute/new/R4AH`로추출한다. 이두명령은과학실행을하지않는다. 이후원R4AH launcher로prepare/explicitexecute/bundle을분리한다.

조건부계산의입력상계와실제source/host승인은외부이다. MODEL reference성공, 문헌확보, sourcehash, unit tests와실제물리결과를혼동하지않는다. 최종미분total=[null,null]; 새shifted적분0이다.
