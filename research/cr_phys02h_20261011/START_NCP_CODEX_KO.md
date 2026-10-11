# PHYS02H — NCP local Codex handoff

## 목적과 현재 상태

프로젝트는 `cosmosapjw-quantum/bass_cr`, 새 과제는 `CR-PHYS02H-NCP-FULL9600-COLUMN-PARALLEL-QUALIFICATION`이다. ChatGPT에서 정확 모멘트 분석, 독립 산술 검증, 작은 전체240점 및 저장9600점의 선택16열 파일럿을 완료했다. 이 경량 작업을 NCP에서 다시 실행하지 않는다.

NCP에서 할 일은 원래 저장9600점의 전체 생성행렬을 현재 동일 런타임에서 원본 직렬 및 새 열별 병렬 방식으로 만들고, 모든 원시 값을 저장하여 정확히 비교하는 것이다. 두 모델·두 반복, 총8논리 생성과76800열 평가만 허용한다. 전파·resolvent·선형계·F 재시도·G frontier 실행은0이다. 이전 F의 `HOLD_OPERATOR_BINDING_UNRESOLVED`와 G의 `BLOCKED_BY_F_OPERATOR_BINDING_HOLD`를 유지한다.

## 1. 추가 첨부 없는 복구

외부 시작 프롬프트/START 파일의 실제 H ZIP 이름·크기·SHA256·Drive/Dropbox ID·science commit/tree를 기준으로 정확한 백업 하나를 사용한다. 이미 같은 바이트의 백업이 있으면 재다운로드하지 않는다. 기존 연결 또는 실제 확인한 rclone remote를 사용하며 계정·remote alias를 추측하지 않는다. Drive 백업 폴더는 `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`, Dropbox는 `/BASS_DERIVATION_DOSSIERS_20260912`다.

H outer의 크기와 SHA256을 먼저 확인한다. 안전한 새 빈 경로에 복구한다. 절대경로·`..`·중복 entry·symlink·기존 파일 위 덮어쓰기를 거부하고 `BUNDLE_MANIFEST.json`의 전체 entry 집합과 bytes/SHA를 확인한다. 기존 dirty checkout·run·return을 수정하지 않는다.

Outer에는 H source 전체와 값 payload, 독립 검토, 실행 계약, 이 handoff, actual science receipt, 다음의 기존 완전한 G outer가 포함된다.

- 이름: `CR_PHYS02G_20261011_0ad3be0f_WITH_F_HOLD_HANDOFF.zip`
- bytes: `58470931`
- SHA256: `2920fd78632ba41dce1f2d428db328862d4ad121f1b97bc746962ae847117707`

G outer 안에는 원래 G core와 완전한 F handoff 및 실제 F 실패 family가 보존돼 있다. F handoff에는538개 의존 파일, 저장된 E grid·원자 데이터·canonical Astra v4.0.0 연구/코딩 하네스가 있다. 이 새 outer의 PR39/40 입력은 출처가 고정된33개 선택 파일이며 두 과거 archive 전체의 새 복구를 주장하지 않는다. 이번 H 실행에 필요한 모든 파일은 outer 및 그 byte-identical 중첩 payload로 공급된다.

제공된 `publication/helpers/restore_plan.py`를 사용하면 새로운 복구 base의 `source/`에 repository-root 실행 배치를 만들고, `provenance/`에 원래 archive와 manifests를 별도 보존한다. 실제 helper CLI와 게시된 복구 receipt를 먼저 읽는다. Helper는 생성 후 stdlib `--plan`을 정확히1회 실행하며 어떤 G도 만들지 않는다. Git에서 같은 source를 가져왔더라도 `inputs/INPUT_IDENTITIES.json`과 `ncp/EXECUTION_SOURCE_MANIFEST.json`의 전체 파일 identity를 확인한다. 복구는 R3, 통상 업로드의 metadata 확인은 R1이다.

## 2. 이미 소비된 작업과 실행 준비를 확인

이 H 과제의 기존 reservation/run/return이 현재 호스트에 있는지 해당 작업 범위에서 확인한다. 같은 unit의 실행 중인 작업을 중복 시작하지 않는다. 완료 또는 실패한 H 예약은 수집·판정으로 이어가며 새로운 빈 폴더를 만들어 재시도 허가처럼 사용하지 않는다. 처음 실행하는 H라는 사실이 확인된 경우에만 다음 단계로 간다. 이 확인은 완료된 PR39/40 intake를 다시 수행하라는 요청이 아니다.

다음 문서를 읽는다.

1. `research/cr_phys02h_20261011/state/SCIENTIFIC_CONTRACT.json`
2. `ncp/NCP_EXECUTION_CONTRACT.json`, `ncp/NCP_RESOURCE_AMENDMENT.json`, `ncp/NCP_WRAPPER_ACCOUNTING_AMENDMENT.json`
3. `inputs/INPUT_IDENTITIES.json`, `ncp/EXECUTION_SOURCE_MANIFEST.json`, `ncp/NCP_READY.json`
4. `review/exact/`, `review/parallel/`, `review/ncp/`의 각 독립 판정
5. `research/context/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md`, `HPC_ACCURACY_POLICY_KO.md`, `READBACK_POLICY.md`, `ASTRA_TIER_ROUTING_POLICY.md`

`NCP_READY.json`은 정확한 execution manifest·input manifest·independent NCP decision의 SHA를 결속해야 한다. 판정은 `PASS_SCOPED`, `independent_of_implementation=true`, `ncp_preparation_admitted=true`, 동일한 unit과 execution manifest SHA를 요구한다. 임의로 PASS를 써서 통과시키지 않는다. Source/contract/입력 변경 시 현재 승인은 적용되지 않는다.

실제 interpreter를 확인한다. 이전 관측 경로 `/root/bass_cr_phys02d_ncp_20261011/venv/bin/python`은 탐색 후보이며 현재 존재·버전의 증거가 아니다. 실행 시 Python3.12.3 / NumPy2.4.2 / SciPy1.17.0과 모든 OpenBLAS/MKL/OMP/NumExpr pool1을 요구한다. Library/dispatch는 관측해서 기록하고 지문을 맞추기 위해 라이브러리·CPU dispatch·물리 입력을 바꾸지 않는다. Requested model label은 backend 인증이 아니다. 기존 canonical Astra 흐름에 따라 고정 계약 구현은 lower worker, 실제 결과의 최종 판정은 후보·허용조건·구현에 참여하지 않은 independent reviewer가 담당한다.

## 3. 실제 자원에 맞는 계획

복구한 source root에서 다음을 실행한다. `--run`과 `--out`은 source 밖의 새 절대경로를 사용한다.

```sh
<verified-python> research/cr_phys02h_20261011/ncp/run_and_collect.py \
  --plan --source-root /ABS/RESTORED/source --run /ABS/NEW_PHYS02H_RUN
```

복원 helper가 동일하게 검증한 interpreter와 같은 출력 파일시스템에서 이미 이 plan을 수행했다면 그 기록을 사용하고 수동 plan을 반복하지 않는다. 실제 execute의 자체 admission은 유지한다. Source 확인과 resource admission을 따로 읽는다. Exit0만으로 실행 가능하다고 해석하지 않는다. 실제 affinity·가시적 cgroup hierarchy/quota·CPU topology·memory limit/current·available bytes·disk 여유를 확인한다. 64코어128GB라는 이름만으로 자원을 인정하지 않는다.

실제64 logical CPU가 허용되면 후보 모델당29worker, watchdog wrapper1·qualifier root1·lane2·spawn support2를 합쳐64슬롯이다. 초기 계약의30worker·고정3슬롯 식과 첫 보완의 고정5슬롯 식은 두 amendment가 순서대로 보완한다. 최종 고정 슬롯은6이며 별도의 spare CPU 보장은 없다. 더 작은 실제 자원에서는 메모리·CPU에 맞추어 worker 수를 줄이며 최소2/model도 허용되지 않으면 typed resource HOLD한다. 모든 내부 수치 thread는1이다.

Reserve는 실제 한도 기준 max(16GiB,1/8)이며 paired 직렬 lane은 합계24GiB 작업 여유가 추가로 필요하다. 후보는 lane parents4GiB + workers×512MiB + support64MiB + wrapper64MiB를 합계로 판단한다. 출력용 disk는 최소16GiB, source 백업 공간은 별도다. 128GB를128GiB로 간주하지 않는다. 정적 예산과 실제 프로세스/cgroup 관측의 의미를 구분한다.

## 4. 전체 크기 실행은 wrapper 한 번

준비·실제 source·자원 조건이 통과한 최초 H 실행만 다음 명령으로 수행한다.

```sh
<verified-python> research/cr_phys02h_20261011/ncp/run_and_collect.py \
  --execute --source-root /ABS/RESTORED/source \
  --run /ABS/NEW_PHYS02H_RUN --out /ABS/NEW_PHYS02H_RETURN
```

Wrapper가 execute와 finally collect를 소유한다. 별도 `--execute`를 먼저 호출한 뒤 wrapper를 다시 실행하지 않는다. Whole-command 과학 실행 시간은900초이며 admission·child 시작·생성·persist·조립·비교·종료 receipt를 포함한다. Source 전송/복구 및 deadline 이후 필요한 수집은 별도 측정한다. 모델 또는 반복마다 과학 실행의 시계를 초기화하지 않는다.

각 반복에서 두 모델의 원본 직렬 reference lanes를 동시에 수행한 후 두 모델의 병렬 candidate lanes를 수행한다. 총 두 반복, serial4 + candidate4 =8논리 전체 생성, 총76800열 평가다. Worker 부분 생성과 실제 열 수·예약·완료를 별도 기록한다. 선택 열 probe나 작은 검사·정확 분석·과거 suite를 다시 수행하지 않는다.

첫 오류·timeout·자원 admission 상실 시 소유한 process group을 취소한다. Qualifier가 이미 종료됐더라도 wrapper가 남은 자기 작업을 정리한 후 수집한다. 실행은 검증한 wrapper를 통해서만 시작한다. 프로세스 소유권이나 PID namespace 매핑을 확인할 수 없는 경우 typed HOLD/경고를 보존하며 다른 작업을 일괄 종료하지 않는다. 이미 예약한 예산과 완성·부분 열 값을 보존한다. 자동 재시도·다른 backend로의 무기록 우회·허용오차 완화·부호 clipping·grid 재생성·원래 source 덮어쓰기는 허용하지 않는다. 실패를 분석·수집하는 것으로 이번 유한 실행을 마무리한다.

## 5. 정확성과 성능의 별도 판정

모델별·반복별 candidate와 해당 fresh reference의 다음 항목을 실제 값으로 정확히 비교한다.

- CSC data, indices, indptr와 matrix shape
- 원래 energy, 모델 반응률의 dtype·shape·raw bytes
- 원래 순서의 normalization diagnostics
- 전체0..9599열의 누락·중복 없는 한 번의 평가
- 반복2 reference와 반복1 reference의 동일성

양쪽 원시 CSC·에너지·반응률 파일과 sidecars를 보존한다. Hash만 남기는 반환은 충분하지 않다. 실패 전 저장된 worker partial values도 보존한다. 부동소수 tolerance로 exact parity 실패를 통과시키지 않는다.

`HISTORICAL_OPERATOR_IDENTITIES.json`의 과거 reference 및 F 실패 지문과도 비교하되, 이 비교는 정보다. 새 직렬/병렬 결과가 같아도 원래 E/F의 CSC 저장값을 회수한 것은 아니며, 옛 pulse·residence를 자동 채택하지 않는다. 과거 mismatch가 현재 지문과 연결됐다는 이유만으로 CPU dispatch 인과성을 확정하지 않는다.

성능은 같은 입력·같은 모델의 두 반복 build-and-persist wall에서 median ratio를 보고한다. Worker 시작·부분 결과 저장·gather 비용을 포함한다. Lane wall, root total wall, worker 부분 시간, peakRSS의 관측 범위를 구분한다. 동시 측정이 아닌 peak들의 합을 실제 동시 메모리로 부르지 않는다. Candidate가 더 느리면 `PERFORMANCE_NOT_IMPROVED`를 남기고, 이 계약 안에서 추가 scaling sweep이나 반복 최적화를 시작하지 않는다.

최대 준비 claim은 현재 런타임의 `SAME_RUNTIME_FULL9600_ASSEMBLY_EQUIVALENCE`이며 실제 exact parity와 별도의 실제 결과 독립 심사를 모두 통과해야 한다.64 CPU speedup은 측정 전 미평가다. 이 결과로 물리 모델·production history·격자 수렴·옛 F binding을 닫지 않는다.

## 6. 실패 후 수집과 완전한 반환

정상 wrapper는 이미 수집하므로 별도 collect를 반복하지 않는다. Wrapper가 수집을 완료하지 못한 실패 상황에서만 같은 원래 run을 다음처럼 수집한다. Collection은 새 G를 만들지 않으며 deadline 이후에도 가능하다.

```sh
<verified-python> research/cr_phys02h_20261011/ncp/run_and_collect.py \
  --collect --source-root /ABS/RESTORED/source \
  --run /ABS/ORIGINAL_PHYS02H_RUN --out /ABS/NEW_COLLECTION_RETURN
```

Actual command·UTC·wall·actual exit·stdout/stderr·source/runtime/resource identity·reservation/completion·첫 실패·값 payload·비교 결과와 wrapper가 실제 생성한 archive manifest·외부 collection receipt·로그를 모두 보존한다. 실제 NCP 결과는 준비 코드 심사와 분리하여 새로운 independent reviewer가 판정한다. 현재 준비 심사자가 후보·허용조건·구현에 참여하지 않았다는 조건은 실제 반환 심사에도 적용한다.

새 additive return branch는 외부 START가 지정한 H 게시 branch의 실제 head를 읽고, 그 head가 고정된 H science commit의 descendant인지 확인한 후 그 기준에서 만든다. 외부 START가 존재하지 않는 미래 commit을 자기참조하도록 요구하지 않는다. 실제 base head/tree를 반환 receipt에 기록한다. 기존 경로를 덮어쓰지 말고 별도 `research/cr_phys02h_ncp_return_.../`에 반환을 추가하여 draft PR로 게시한다. Merge·force push·history overwrite는 하지 않는다.

원본 H outer 전체 또는 그와 정확히 동등한 완전 입력 payload, 실제 NCP raw values와 실패/성공 family, 새로운 독립 판정을 하나의 create-only 완전 outer return에 담는다. Manifest는 자신을 제외한 모든 payload의 bytes/SHA와 정확한 entry 집합을 기록한다. 기존 Drive/Dropbox 폴더에 고유 파일명으로 완전 반환과 짧은 START를 올린다. R1 성공·정확ID·size·제공되는 checksum을 확인하며 제공되지 않는 SHA 때문에 재다운로드하지 않는다.

최종 답변에는 실제8개 중 예약·완료·실패한 수, 총 열 평가, 모델별 exact parity, 반복 일관성, 두 반복 시간·관측 가속률 또는 성능 미개선, 실제 자원·exit·독립 판정, 새 PR/head/tree 및 완전 백업의 이름·크기·SHA·Drive/Dropbox ID를 포함한다. 경량 재실행0, F retry0, pulse/expm/solve0과 유지된 gate도 명시한다. 추가 첨부 없이 다음 세션이 이어받을 수 있어야 한다.
