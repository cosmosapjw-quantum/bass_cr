# CR-PHYS02C — NCP local Codex 전달 시작

아래 내용을 NCP local Codex에 전달해 기존 `bass_cr` 연구를 이어서 수행한다. 계산에 필요한 모든 전달 파일은 아래 ZIP 내부에 포함되어 있다. 별도 사용자 첨부는 필요하지 않다.

## 정확한 백업과 고정 참조

| 항목 | 값 |
|---|---|
| 완전 ZIP | `CR_PHYS02C_20261011_f34a0cc1_HANDOFF.zip` |
| ZIP byte size | `3251044` |
| ZIP SHA256 | `cd47c755730bd208d7b5360fb18e53351f63af481055994e5c8bcdb355b961fb` |
| Drive 파일 ID | `1fikr0Wjcd_fm_rC1DYhv0JLrYENAKmex` |
| Drive 링크 | [완전 ZIP](https://drive.google.com/file/d/1fikr0Wjcd_fm_rC1DYhv0JLrYENAKmex/view?usp=drivesdk) |
| Drive 폴더 ID | `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI` |
| Dropbox 파일 ID | `id:BSpOijBcT10AAAAAAD32mg` |
| Dropbox 경로 | `/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02C_20261011_f34a0cc1_HANDOFF.zip` |
| Dropbox namespace 경로 | `ns:183516487//BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02C_20261011_f34a0cc1_HANDOFF.zip` |
| Dropbox revision | `65d8022cd3a1d0af03d47` |
| Git 저장소 | `cosmosapjw-quantum/bass_cr` |
| Branch | `research/cr-phys02c-atomic-consistency-20261011` |
| Science commit | `f34a0cc1484247caf252afde3d5fbe834640e9e4` |
| Draft PR | [#28](https://github.com/cosmosapjw-quantum/bass_cr/pull/28) |
| 내부 BUNDLE_MANIFEST SHA256 | `fab9b26fcf73e76f6a0df0e05c44ae621053c5dfd07986eecb8bd275bd4e96e7` |
| 새 연구 FILE_MANIFEST SHA256 | `76db903de5805f5a18cf61321ddf78911cf2f3ea3832686a8d45124b8d36c145` |
| 독립 최종 decision SHA256 | `f1b736d543ff94dd5dc027e337e57a90ef46c189e240eebfb0161ab5ca4bec27` |

이 science commit과 ZIP이 계산의 고정 기준이다. 이후 branch에 추가되는 게시 영수증만을 담은 commit은 계산 기준을 바꾸지 않는다. ZIP을 우선 사용할 수 있고, 기존 Git 접근이 가능한 경우 격리 checkout을 정확한 science commit에 고정해 같은 연구를 확보할 수 있다. 사용자 작업을 덮어쓰지 않는다.

## 실제 완료 상태

- 독립 최종 판정: `PROMOTE_SCOPED`. 2400/4800-node full BED 비교가 완료됐다.
- 이 ZIP: 236개 항목 중 자기 자신인 BUNDLE_MANIFEST를 제외한 235개 payload의 byte size·SHA256과 ZIP CRC를 실제 검증했다. 새 디렉터리 복원과 전달된 `--plan` 실행은 exit 0이었다.
- 다음 노드 `CR-PHYS02C-NCP-MATCHED-THIRD-GRID`: `READY_FOR_CONDITIONAL_RUNTIME_ADMISSION`.
- NCP 실제 계산: `PREPARED_NOT_EXECUTED`. 현재 ChatGPT 환경은 최소 working memory 12 GiB 조건을 충족하지 않아 자원 HOLD였으며, NCP 자원은 그 호스트에서 실제 확인한다.
- Drive/Dropbox 업로드 완료와 정확한 ID·이름·크기·경로 metadata를 확인했다. Provider checksum은 응답에 없어서 `UNAVAILABLE`이다. 원격 다운로드 복원을 수행한 것으로 주장하지 않는다. NCP는 위 외부 SHA256과 내부 manifest를 실제 다운로드한 bytes에 적용한다.

## 그대로 실행할 지시

승인되어 설정된 Git/Drive/Dropbox 접근 중 사용 가능한 경로로 위 자료를 확보하고, 다음 내장 프롬프트를 수행해라. 시작 문서만 읽고 멈추지 말고, 모든 identity·review·실제 resource 조건이 충족되면 정해진 계산 한 건과 실제 결과 반환까지 진행해라. 모든 자료 접근 경로가 실제로 차단되거나 resource 조건이 실패할 때에는 정확한 상태를 보존하고 원인을 보고해라. 새로운 사용자 첨부를 기본 요구로 삼지 마라.

---

# NCP local Codex 시작 프롬프트 — CR-PHYS02C

`bass_cr`의 `CR-PHYS02C-ATOMIC-CONSISTENCY`를 아래의 고정된 결과에서 이어서 진행해라. 이 파일과 필요한 코드·원천 입력·실행 계약·저장 결과·복원 검증·결과 수집기는 같은 handoff ZIP에 들어 있다. 추가 사용자 첨부가 필요하지 않다.

## 자료를 확보할 위치와 정확한 연구 정체성

- 저장소: `cosmosapjw-quantum/bass_cr`
- 연구 branch: `research/cr-phys02c-atomic-consistency-20261011`
- ZIP 이름 형식: `CR_PHYS02C_20261011_<scienceSHA8>_HANDOFF.zip`
- Dropbox 폴더: `/BASS_DERIVATION_DOSSIERS_20260912`
- Drive 폴더 ID: `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`
- 연구 디렉터리: `research/cr_phys02c_20261011`
- 고정 과학 계약 SHA256: `e0445ecbf052a3441f6203f9e0463defcf0c24c0ee018a67e112d338991f47ee`
- 완료된 full BED R001 JSON SHA256: `36ea403320bcc711c4955de55e2a7e9f65c2deaf851a882bd9581585fb857624`
- 부모 운영 pin: `b5b0f2244311a6e46692da55e75db6d04d3ef305`

백업과 함께 게시된 `CR_PHYS02C_20261011_NCP_START_KO.md` 또는 최종 전달 영수증에 정확한 archive 이름·object ID·외부 SHA256·Git pin이 있으면 그것을 우선한다. 이 ZIP 안에 자기 자신의 외부 hash나 게시 후 object ID를 순환적으로 기입하지 않는다. 내부 파일 검증은 archive-root `BUNDLE_MANIFEST.json`으로 한다. 해당 시작 문서는 위치 편의용이고 계산에 필요한 추가 입력 파일이 아니다.

이미 승인·설정된 Git/Drive/Dropbox 인증 경로로 자료를 확보해라. ChatGPT connector 인증이 NCP에도 있다고 가정하지 말고 자격정보를 출력하지 마라. 사용 가능한 다른 기존 인증 경로가 있으면 이어서 사용해라. 모든 경로가 실제로 차단되어 있으면 부족한 접근 capability와 이미 시도한 경로만 보고해라. 별도 첨부를 요구하는 것을 기본 우회로로 삼지 마라.

## 복원과 읽기

1. dirty work를 보존하고 새 디렉터리 또는 격리 worktree를 사용해라. 외부 archive SHA가 제공되면 추출 전에 검사해라. ZIP의 경로 탈출·절대 경로·symlink 항목을 거부하고 안전하게 추출한 뒤 전체 내부 manifest의 bytes와 SHA256을 확인해라. 외부 hash를 확보하지 못했으면 이를 UNAVAILABLE로 기록하고 확인한 내부 identity와 구분해라. 부분 hash 실패를 무시하지 마라.
2. Git 경로에서는 원격 exact HEAD를 한 번 확인해 pin으로 기록하고 그 commit을 checkout해라. 제공된 최종 영수증의 pin과 다르면 변경 파일의 범위를 먼저 검토해라. README, 과학 계약, R001 result, 독립 decision, FILE_MANIFEST identity를 확인하고 임의의 다른 branch 결과를 혼합하지 마라.
3. `<복원 root>/research/cr_phys02c_20261011`를 작업 디렉터리로 삼고 `REPORT_KO.md`, `state/RESEARCH_STATE.md`, `state/CLAIM_GATE.json`, `state/NEXT_DAG.json`, `review/FINAL_DECISION.json`, `state/SCIENTIFIC_CONTRACT.json`, `ncp/NCP_EXECUTION_CONTRACT.json`, `ncp/README_KO.md`를 읽어라. 묶음에 포함된 두 Astra v4.0.0 harness ZIP은 연구·코딩 지침의 원본이다. 현재 실행 모델과 역할을 정직하게 기록하고 이미 완료한 과학 suite를 반복하지 마라.

## 다음 허용 작업

`python3 ncp/launch_refinement.py --plan`을 먼저 실행해라. 이 명령은 수송을 수행하지 않는다. 코드가 확인하는 실제 cgroup v2 계층의 모든 읽기 가능한 상위 제한, affinity/quota, RAM/current/available, disk, 현재 프로세스 및 reserve를 확인해라. 최소12 GiB working availability, 추정 peak8 GiB, 메모리 reserve12.5%(최소1 GiB)를 지켜라. 실행기는 모든 BLAS/MKL/OMP/NumExpr thread를1로 고정한다.64 CPU 광고 사양을64 rank 실행 명령으로 바꾸지 마라.

`state/NEXT_DAG.json`의 `CR-PHYS02C-NCP-MATCHED-THIRD-GRID`가 READY이고 hash-bound 독립 review가 scoped pass이며 실제 resource admission도 통과할 때만 실행해라. `requirements.txt`의 Python 패키지는 기존 환경 또는 격리 venv에 준비해라. 필요한 설치가 막히면 실제 원인과 계산 전 상태를 기록해라.

실행할 과학 작업은 다음 하나다: 동일한 원천·bath·CCC27 native effective costs·Coulomb·FP64·허용값을 유지하고, full BED와 legacy BEQ-total/BED-shape를 `(3200,6400)`, 총9600 node에서 순차적으로 계산한다. 두 수송 호출과 wall3600 s 한도를 지킨다. 저장된4800 결과와 같은 관측량 및 paired delta를 비교한다. 한 모형의 절대 격자 변화와 두 모형 차이의 격자 변화를 함께 보고해라. r<1/3·같은 부호는 경험적 진단이며 물리 오차 인증이 아니다.

새 실행 이름을 정한 뒤:

```bash
python3 ncp/launch_refinement.py --execute --run-dir evidence/ncp_runs/<새실행이름>
python3 ncp/ops.py collect --study . --run evidence/ncp_runs/<새실행이름> --out <반환폴더>
```

placeholder는 실제 충돌하지 않는 경로로 치환해라. 실패·timeout도 첫 실제 stderr/stdout/exit/reservation과 결과를 보존하고 수집해라. 독립 Astra가 새 결과를 최종 판정하게 해라. 계산 완료만으로 science 또는 production을 자동 승격하지 마라.

## 유지할 경계

- `PHYS02_DELAY OPEN`, `production_history HOLD`, `atomic_G02 UNRESOLVED`, `b_grid NO_GO`, `all_bound OPEN`, `R17B2B NO_CERTIFIED_SOURCE_SHARPENING`.
- 현재 full BED는 소스가 명시된 조건부 모형이다. NIST CGI 동등성, CCC 물리 문턱 및 atomic completeness를 확인한 것으로 바꾸지 마라.
- 이번까지의 실제 결과는 H 이온화+5.19218%, He 이온화+0.516080%, 열률+0.0258541%이며 대부분의 주입 에너지가 아직 활성 전자에 남는다. 다음 계산 결과를 이 수치에 맞춰 조정하지 마라.
- 고에너지 출생 성분의 전체 열률과 그 성분이 실제 E≤10 eV에서 낸 열률을 구분해라.
- ordinary backup upload 확인과 실제 복원 byte 검증은 다른 증거다. 현재 NCP 상태는 PREPARED_NOT_EXECUTED이며 실제 실행 후에만 갱신해라.

