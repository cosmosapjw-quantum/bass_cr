# 원자물리 → reionization 즉시 이월 패키지

2026-10-04 · 계획 v1 · 네 저장소의 지정 branch를 실제 읽어 만든 선행연구/실행 계약.

목표는 외부 공개 원자율로 reionization 응용을 먼저 완성하고, 기존 정밀 원자물리 연구를 다시 호출 가능한 독립 확장 lane으로 보존하는 것이다. 원자물리의 전체 엄밀 인증 완료와 선택한 우주론 응용의 완료는 서로 다른 상태다. 이번 패키지는 선행 물리·소스 비교·유한 회계 검산과 상세 실행 계획을 완성했다. 실제 Rust 소비자 구현·인증·우주론 적분은 아직 실행하지 않았다.

## 바로 시작

현재 저장소에 맞는 시작문 하나를 Codex에 전달한다. 저장소 루트의 기존 AGENTS.md를 먼저 적용하고 `CODEX_ROUTING.json`의 branch/source commit을 확인한다. 이 문서만 보고 기존 branch를 reset하거나 다른 legacy 작업을 재실행하지 않는다.

| 스레드 | 시작문 | 이번 빠른 경로의 역할 | 원래 연구 재호출 |
|---|---|---|---|
| rei_bianchi | [CODEX_START_KO.md](threads/rei_bianchi/CODEX_START_KO.md) | H/He 소비자·엄밀 microstep·Bianchi/FLRW 비교·공통 감도 실행 | [LEGACY_LANE.json](threads/rei_bianchi/LEGACY_LANE.json) |
| bass_cr | [CODEX_START_KO.md](threads/bass_cr/CODEX_START_KO.md) | 첫 baseline의 CR-off 무호출 계약; CR-on은 선택 확장 | [LEGACY_LANE.json](threads/bass_cr/LEGACY_LANE.json) |
| WU088_HH | [CODEX_START_KO.md](threads/WU088_HH/CODEX_START_KO.md) | 외부 HH 계수 family·분기·회계·동일 감도 결과 수락 | [LEGACY_LANE.json](threads/WU088_HH/LEGACY_LANE.json) |
| BASS_HE | [CODEX_START_KO.md](threads/BASS_HE/CODEX_START_KO.md) | 기존 B3 API 재사용·He RCT 소스 충돌 명시·감도 수락 | [LEGACY_LANE.json](threads/BASS_HE/LEGACY_LANE.json) |

GitHub의 각 저장소에는 공통 파일과 해당 스레드만 들어 있다. 다른 스레드 링크는 전체 ZIP 또는 해당 저장소에서 연다. 전체 ZIP에는 네 스레드 모두 들어 있다.

```bash
python3 docs/atomic_reionization_handoff_20261004_v1/tools/task_packet.py next --thread rei_bianchi
```

`--thread`만 현재 저장소명으로 바꾼다. 이 도구는 준비된 작업 카드 하나를 출력하며 실행·승격하지 않는다. 초기 상태에서 rei는 REI-F00, He는 HE-F1이 준비되어 있다. CR/HH의 선행 물리 검산은 끝났고 실제 소비자/과학 domain 계약을 기다린다. WAITING은 원래 대규모 원자 계산을 재개하라는 뜻이 아니다.

## 필요한 파일만 읽기

1. `common/DECISIONS.json`, 자기 `CODEX_START_KO.md`, 출력된 작업 카드.
2. 작업 카드가 요구한 `PREWORK_KO.md` 절과 source/contract. `LOW_COST_RUNBOOK_KO.md`의 반환 규칙.
3. 전체 맥락이 필요할 때만 `RESEARCH_PROGRAM_KO.md`, `GLOBAL_DAG.json`, `PR_PLAN.json`.
4. 원계획 재개 시에만 `LEGACY_LANE.json` → 해시 보존 원문 `legacy_sources/`.

`PROGRAM.json`과 `TASK_CARDS.jsonl`은 `threads/*/TASKS.json`에서 생성한 정규화 전역 DAG다. 실행 의존성은 전역 DAG를 따른다. 후속 변경 시 네 원본 카드와 전역 DAG를 함께 갱신한다. 단일 저장소 사본에서 타 스레드 파일이 없는 상태로 `build_program.py`를 실행하지 않는다.

## 게시/백업 확인

- 실제 Git 커밋과 PR: `publication/GITHUB_RECEIPT.json` 또는 동봉된 전달 영수증.
- Drive/Dropbox 위치: `publication/BACKUP_FOLDERS.json`.
- 패키지 파일 해시: `PAYLOAD_MANIFEST.json`; ZIP 자체 해시: 배포 폴더의 `CHECKSUMS.sha256`.
- 독립 검토: `review/REVIEW.json`, `review/INDEPENDENT_REVIEW_KO.md`.
- 실행 확인 범위: `publication/PREPUBLICATION_CHECKS.json`; 업로드 확인 범위는 최종 전달 영수증.

공개 논문·코드의 사용은 저자와 별도 협상 없이 가능한 경로를 우선한다. 인용·라이선스 의무는 유지하며, 웹에서 읽을 수 있다는 사실을 무조건적 코드 재배포 허가로 취급하지 않는다. Grackle의 선택 소스와 LICENSE는 그대로 보존했다.
