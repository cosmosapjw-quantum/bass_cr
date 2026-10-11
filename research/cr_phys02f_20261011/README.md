# CR-PHYS02F

PHYS02E 실제 NCP 반환(PR35)을 입력으로 조기·후기 열 지연과 출생 성분을 분해한 연구 unit이다. NCP용 새 task는 저장된 9,600점 연산자의 adjoint·체류시간 진단이며 G 최대2, solve 최대10, pulse/expm0, wall900s이다.

- 과학 결과: `REPORT_KO.md`, `research/theory/`, `evidence/analysis/`.
- 유일한 새 실행 계약: `state/SCIENTIFIC_CONTRACT.json`, `ncp/NCP_EXECUTION_CONTRACT.json`.
- 독립 판정과 현행 DAG: `review/INDEPENDENT_DECISION.json`, `state/NEXT_DAG.json`.
- 상세 NCP 절차: `START_NCP_CODEX_KO.md`.
- 정확한 백업 ID가 있는 최종 시작 파일: publication 단계에 별도로 제공.
- 전체 원시 입력 및 실행 의존 파일은 complete handoff ZIP에 포함된다.

이전 PHYS02E READY는 이미 소모된 실제 작업의 과거 준비 상태다. 새 NCP 실제 실행은 여기서 수행하지 않았다. source/physical/runtime/publication gates를 구별한다.

