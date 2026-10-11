# PHYS02H — NCP local Codex 시작 프롬프트

`cosmosapjw-quantum/bass_cr`의 다음 물리 연구 루프를 이어서 실행하라. 이번에 허용된 실행 unit은 `CR-PHYS02H-NCP-FULL9600-COLUMN-PARALLEL-QUALIFICATION`이다. 여기서 이미 끝난 정확 모멘트 분석, 작은 전체240점·선택16열 파일럿, 과거 검사와 PR39/40 intake는 재실행하지 않는다. NCP에는 원래 저장9600점의 전체 생성행렬에 대한 동일 런타임 직렬/병렬 qualification만 수행한다.

## 정확한 시작 백업

- 완전 ZIP: `CR_PHYS02H_20261011_7907a2f5_HANDOFF.zip`
- 크기: `68158856` B
- SHA256: `fbc505a9515d483c84c984eaf7a9666ddf1a55e3d94c57f43e013ab34d557adf`
- Google Drive file ID: `1KChWc0w0EFcuArlpEEoDCSja67p4yKGE`
- Drive folder ID: `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`
- Dropbox file ID: `id:BSpOijBcT10AAAAAAD4MiA`
- Dropbox 경로: `/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02H_20261011_7907a2f5_HANDOFF.zip`
- H science commit: `7907a2f50cfd3282ef336e02fb2ec758f8ddd8d0`
- H science tree: `4382f410a2fc25b083be77190d7a772efae4598a`
- H source unit manifest SHA256: `8698a233ea5988be93410ec1b9cc4620676a2aee0c128663b2de9870c5524b7b`
- 최종 execution manifest SHA256: `14f9ad1319146c72d13b1e30583dc27d3b9272c8d23913e63467782fa57b35ec`
- 독립 NCP 준비 판정 SHA256: `756eb62b0ec9ac2db5a470bf7eb6523af5ecf54d35ed7faa66f8bf990e7c2820`
- H 게시 branch: `research/cr-phys02h-exact-parallel-20261011`
- H draft PR: `https://github.com/cosmosapjw-quantum/bass_cr/pull/41`

Drive 또는 Dropbox의 정확한 한 파일을 기존 연결이나 실제 확인한 rclone remote로 가져온다. 이미 동일 bytes의 ZIP이 있으면 재다운로드하지 않는다. 계정·remote 이름은 추측하지 않는다. 추가 사용자 첨부는 필요 없다. 이 ZIP에는 H source·실제 local 값·검토·계약·handoff와 기존 완전 G/F payload 및 canonical Astra 하네스가 포함된다.

## 복구와 실행 조건

ZIP 전체 bytes/SHA를 먼저 확인하고 새 빈 경로에 안전하게 복구한다. 절대 경로, `..`, symlink, 중복 entry, 기존 파일 덮어쓰기를 거부하고 outer manifest의 정확한 entry 집합을 확인한다. 원본 ZIP을 보존한다. `publication/helpers/restore_plan.py`와 내부 `START_NCP_CODEX_KO.md`를 읽고 제공된 복원 helper를 사용한다. `source/`는 실행 입력이며 `provenance/`는 원본 중첩 archive와 원래 실패 기록이다.

Helper CLI는 다음과 같다. Helper의 파일 위치는 안전하게 확인한 실제 추출 경로를 쓴다.

```sh
<verified-python> /ABS/restore_plan.py \
  --zip /ABS/CR_PHYS02H_20261011_7907a2f5_HANDOFF.zip \
  --dest /ABS/NEW_PHYS02H_RESTORE \
  --receipt /ABS/NEW_PHYS02H_RESTORE_RECEIPT.json
```

H의 기존 reservation/run/return이 있는지 과제 범위에서 확인한다. 실행 중인 같은 unit을 중복 시작하지 않는다. 이미 실행한 H가 있으면 그 원래 run을 수집·판정하고 새 폴더로 예산을 초기화하지 않는다.

다음 문서의 원래 계약과 보완을 읽는다.

- `research/cr_phys02h_20261011/state/SCIENTIFIC_CONTRACT.json`
- `ncp/NCP_EXECUTION_CONTRACT.json`, `ncp/NCP_RESOURCE_AMENDMENT.json`, `ncp/NCP_WRAPPER_ACCOUNTING_AMENDMENT.json`
- `inputs/INPUT_IDENTITIES.json`, `ncp/EXECUTION_SOURCE_MANIFEST.json`, `ncp/NCP_READY.json`
- `review/exact/`, `review/parallel/`, `review/ncp/`의 독립 판정
- 제공된 canonical Astra 연구/코딩 하네스와 프로젝트 실행·정확성·읽기확인 정책

Source identity549개, 직접 실행 pin19개, F 의존 payload538개와 독립 준비 판정의 결속을 유지한다. 현재 source 준비 판정은 PASS_SCOPED이며 실제 NCP 결과나 성능에 대한 PASS가 아니다. 원래 NCP 준비 HOLD, 그 교정 중 실패, 최종6개 영향 검사 통과 기록을 모두 보존한다.

실제 interpreter와 자원을 확인한다. 요구 런타임은 Python3.12.3 / NumPy2.4.2 / SciPy1.17.0이다. 예전 `/root/bass_cr_phys02d_ncp_20261011/venv/bin/python`은 탐색 후보일 뿐 현재 존재나 버전을 가정하지 않는다. 모든 OpenBLAS/MKL/OMP/NumExpr thread는1로 제한한다. 실제 CPU dispatch와 라이브러리 identity를 관측하되 강제로 바꾸거나 원래 F 오류의 원인이라고 단정하지 않는다.

실제 affinity/cgroup quota/topology와 memory limit/current/available bytes, 출력 disk를 사용한다. 명목64코어128GB만으로 시작하지 않는다. 실제64 logical CPU에서는 모델당29 workers와 wrapper1+root1+lane2+support2를 합쳐64슬롯이다. 작은 자원에서는 worker를 줄이거나 HOLD한다. Reserve는 max(16GiB, 실제 한도의1/8), paired serial 작업 여유는24GiB, candidate는 parents4GiB+workers×512MiB+support64MiB+wrapper64MiB다. 출력 free disk는 최소16GiB이며 source 백업 공간은 별도다.

복구 helper가 동일하게 검증한 interpreter와 같은 출력 파일시스템에서 wrapper plan을 이미 수행했다면 그 receipt를 사용한다. 수동 plan을 반복하지 않는다. 필요한 첫 plan만 다음처럼 수행한다.

```sh
<verified-python> research/cr_phys02h_20261011/ncp/run_and_collect.py \
  --plan --source-root /ABS/RESTORED/source --run /ABS/NEW_PHYS02H_RUN
```

Source binding과 resource/runtime admission을 따로 판독한다. ChatGPT 복구 확인의 자원/runtime HOLD는 현재 NCP admission을 대신하지 않는다. 실행 가능 조건과 최초 H 예약 조건이 모두 충족될 때에만 아래 wrapper를 한 번 실행한다.

## 허용된 전체 크기 실행

```sh
<verified-python> research/cr_phys02h_20261011/ncp/run_and_collect.py \
  --execute --source-root /ABS/RESTORED/source \
  --run /ABS/NEW_PHYS02H_RUN --out /ABS/NEW_PHYS02H_RETURN
```

Wrapper가 execute와 finally collect를 소유한다. 직접 qualifier execute로 우회하거나 wrapper를 중복 실행하지 않는다. 실행 admission부터 startup·생성·persist·조립·비교·종료 receipt까지 whole-command 누적900초다. 복구/전송 및 deadline 이후 수집 시간은 따로 기록하되 과학 시계는 초기화하지 않는다.

각 반복에서 fullBED와 legacy의 원본 직렬 reference lane을 동시에 수행하고, 이어 두 모델의 병렬 candidate lane을 수행한다. 원본 직렬 기준 단계는 모델 두 개의 독립 lane을 사용하고,64슬롯 배치는 병렬 candidate 단계에 적용한다. 전체 실행 내내64 CPU가 바쁘다는 의미로 보고하지 않는다. 두 반복에 serial4+candidate4=총8논리 전체9600생성, 총76800열 평가가 상한이다. Worker partial 진입·열 수와 논리 생성 수를 따로 기록한다. Pulse/expm/resolvent/solve/F retry/G frontier 실행은0이다.

대응하는 fresh reference와 candidate의 CSC data/indices/indptr, matrix shape, 원래 energy와 rates의 dtype/shape/raw bytes, 순서 있는 diagnostics를 정확 비교한다. 전체0..9599열이 누락·중복 없이 한 번씩 계산되어야 한다. 반복2 reference와 반복1 reference도 정확히 같아야 한다. 허용오차 완화, clipping, grid 재생성, 원래 물리 source 변경을 금지한다.

첫 오류·timeout·자원 조건 상실 시 소유한 계산 group을 즉시 취소한다. Qualifier가 이미 죽어도 wrapper가 자기 잔여 작업을 정리한 후 수집한다. 불명확한 PID namespace/소유권은 typed HOLD/경고로 남기고 무관한 프로세스를 일괄 kill하지 않는다. 자동 retry나 추가 scaling sweep은0이다. 이미 소모한 예약과 실패 전 부분 값을 보존한다.

양쪽 실제 CSC·에너지·rate 값, worker partial values, sidecar identities, exact comparison, 원래 command·UTC·wall·exit·stdout/stderr·runtime/resources·reservation/completion과 archive manifest·외부 collection receipt를 모두 보존한다. Hash만 남기지 않는다. 정상 wrapper가 수집했다면 collect를 반복하지 않는다. 수집 실패 때만 동일 원래 run에 대해 내부 handoff의 `--collect` 절차를 적용한다.

## 결과 판정과 반환

정확성과 성능을 별도로 판정한다. 두 반복의 같은 모델·입력 build-and-persist wall에서 median ratio를 보고하고 worker 시작·persist·gather를 포함한다. Lane/root wall과 peakRSS의 관측 범위를 구별한다. 더 느리면 PERFORMANCE_NOT_IMPROVED를 기록하고 이번 계약에서 추가 실행하지 않는다. 아직 측정하지 않은64 CPU 가속률을 제시하지 않는다.

실제 결과에는 후보·허용조건·구현에 참여하지 않은 새로운 독립 reviewer가 필요하다. 준비 심사의 PASS를 실제 결과 PASS로 복사하지 않는다. 과거 지문 비교는 정보이며 새 행렬을 옛 CSC 복구나 옛 pulse 승인으로 부르지 않는다. F는 HOLD_OPERATOR_BINDING_UNRESOLVED, G frontier는 BLOCKED_BY_F_OPERATOR_BINDING_HOLD를 유지한다. 다른 inherited physical gate도 유지한다.

H 게시 branch의 실제 head를 읽고 위 science commit의 descendant임을 확인한다. 그 실제 head/tree를 기록한 새 additive return branch에 `research/cr_phys02h_ncp_return_.../`로 반환을 추가하고 draft PR을 만든다. Merge·force push·원래 run/history 덮어쓰기를 하지 않는다.

원본 H outer 전체 또는 그와 정확히 동등한 완전 input payload, 이번 실제 NCP 값과 성공/실패 family, 새 독립 판정을 하나의 create-only 완전 outer return에 넣는다. 기존 Drive/Dropbox 폴더에 고유 이름의 완전 반환과 START를 올린다. Provider 성공·정확ID·size·제공되는 checksum으로 R1을 확인하고 선택 SHA가 없다는 이유로 재다운로드하지 않는다.

최종 답변에는 실제8개 중 예약/완료/실패 수, 열 평가 수, 모델별 exact parity, 반복 일관성, 두 반복 시간·관측 가속률 또는 미개선, 실제 CPU/memory/runtime·exit·독립 판정, 새 PR/head/tree 및 반환 ZIP의 이름·bytes·SHA256·Drive/Dropbox ID를 제공한다. 다음 세션에서도 추가 첨부 없이 이어갈 수 있게 한다.
