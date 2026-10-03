# R4AI: Dropbox 복구·동일 branch patch·R4AH 첫 실행 handoff

2026-10-03. 이 문서를 Codex 실행 지시로 사용한다. 새 연구를 처음부터 재구현하는 지시가 아니다. `AUDIT_AND_REVISED_PLAN_KO.md`, `REVISED_WORKFRONT.json`, `FINAL_STATE.json`을 먼저 읽는다. **여기서 가능한 이론이 전부 끝난 것은 아니다.** G04/G05의 actual bridge/selector 연속 bound, B1의 continuous quadrature/tail, C0 실제 state/host binding은 독립 로컬 연구로 남는다. 외부 첫 수치 노드는 여전히 R4AH의 m64 한 점이다.

## 1. 완전한 release를 확보한다

같이 제공된 detached DELIVERY_RECEIPT 또는 CODEX_START_PROMPT의 실제 Dropbox ID/name/bytes/SHA256로 `BASS_CR_R4AI_LOCAL_THEORY_AND_CODEX_PACKAGE_20261003_v1.zip`을 확보한다. connected Dropbox fetch/download 또는 기존 Dropbox 동기화 파일을 우선 사용한다. 이 파일은 공개 공유로 전환할 필요가 없다. exact object ID로 받은 ZIP을 새로운 폴더에 안전하게 추출하고 아래를 실행한다.

```sh
cd /absolute/new/R4AI_release
export PYTHONDONTWRITEBYTECODE=1
python verify_release.py .
```

기존 API 인증이 이미 설정돼 있고 connector/sync가 없는 경우에만 `tools/download_dropbox.py`를 사용한다. `--id`, `--sha256`, `--bytes`는 detached receipt의 실제 값을 복사한다. `DROPBOX_ACCESS_TOKEN`은 기존 로컬 비밀 저장소로 공급하고 대화/로그/패키지에 쓰지 않는다. script는 file bytes의 SHA256을 검사한다. Dropbox의 자체 content_hash와 일반 whole-file SHA256은 다르다. 다운로드용 임시 bearer URL을 handoff에 고정하지 않는다.

## 2. Git 반영: 신규 경로에만 create-only

등록 branch: `research/r4q-gap-closure-20261001`.
등록 parent: `0d7bdbe76dc35d38668d750e6312919cecb09144`.
신규 prefix: `research/convergence_20261003/r4ai_local_pre_codex/`.

release는 실제 object ancestry를 보유한 git bundle이 아니라 **검증된 binary-capable create-only patch**를 제공한다. 임의의 synthetic parent를 실제 저장소 조상이라고 부르지 않는다. 새 branch/main merge/force는 금지한다. 이전 R4AD 안전성 차단 mutation이나 기존 동명 경로를 이 patch에 넣지 않았다. 과거 R4AA379 및 개별 R4AE/AF/AG mapping 전체의 동기화는 이 patch 적용으로 소급 완료되지 않는다.

먼저 실제 repo/branch/HEAD/dirty 상태를 읽고 원격을 fetch한다. 로컬과 원격이 등록 parent와 다르면 **reset하지 말고** 실제 diff와 겹치는 source를 검토해 별도 새 publication contract를 만든다. 현재 helper는 차이가 있으면 거절한다.

```sh
P=/absolute/new/R4AI_release
R=/absolute/path/to/bass_cr

git -C "$R" fetch origin research/r4q-gap-closure-20261001
git -C "$R" branch --show-current
git -C "$R" rev-parse HEAD
git -C "$R" rev-parse origin/research/r4q-gap-closure-20261001
git -C "$R" status --short

python "$P/tools/apply_checked_patch.py" \
  --repo "$R" \
  --patch "$P/publication/CREATE_ONLY.patch" \
  --manifest "$P/publication/PATCH_MANIFEST.json"
```

helper는 clean branch와 exact parent, patch SHA, 신규 path 부재를 확인한다. `git apply --check --index` 후 적용하고 working-tree/index의 모든 payload SHA를 검사한다. 자동 commit/push는 하지 않는다. 검토 후 정확한 새 prefix만 commit하고 동일 branch에 non-force push한다. 실제 HEAD/tree/ref 응답과 coverage를 반환한다. 실패 시 reset/force/기존 파일 덮어쓰기로 통과시키지 않는다.

## 3. R4AH 코드는 그대로 사용한다

release에는 original R4AH runtime ZIP과 그 안의 R4AG complete source/input가 있다. 새 mutable workspace에 안전하게 추출한다.

```sh
P=/absolute/new/R4AI_release
python "$P/tools/unpack_runtime.py" \
  --output /absolute/new/R4AH_runtime
```

원 archive SHA는 `95f9c09b7c5108384d440c6fb21026d9dff03046194b27c58abeee3f18bb4119`이다. 원 R4AH 내부 `verify_delivery.py`도 bytes만 확인하며 완료 science/test를 재실행하지 않는다. actual Linux CPU quota/affinity/memory headroom, compiler/GMP dependencies를 새로 관측하고 기존 resource guard를 지킨다. 모의 메모리값·임의 reserve 감소·다른 프로세스 종료로 승인하지 않는다.

```sh
cd /absolute/new/R4AH_runtime
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python verify_delivery.py .
python source/m64_launch.py prepare \
  --session /absolute/new/R4AH_m64_session --workers 3
```

prepare는 원자적분을 하지 않는다. PREPARED/BATCH/ENVIRONMENT/BUILD/LDD와 exact BATCH SHA를 검토한다. 승인된 실행 owner가 exact batch와 m64를 승인한 뒤에만 다음 명령을 실행한다. 일반적인 동기화 승인을 무제한 원자계산 승인으로 해석하지 않는다.

```sh
H=$(sha256sum /absolute/new/R4AH_m64_session/batch/BATCH.json | cut -d ' ' -f1)
python source/m64_launch.py execute \
  --session /absolute/new/R4AH_m64_session \
  --confirm-batch-sha256 "$H" --authorize-native
python source/m64_launch.py bundle \
  --session /absolute/new/R4AH_m64_session \
  --output /absolute/new/R4AH_m64_RETURN.zip
```

첫 node는 `m64`, z=-2049/64 a0다. point-target≤1e-16, candidate/source/geometry/epoch/pole/cover/cell/native completeness를 확인하고 반환한다. 실패·중단·폭 미달은 그대로 보존한다. 완료된 center/M9/Peano/oldR8를 재실행하지 않는다. 원래 허용오차를 바꾸거나 D에 맞춰 보정하지 않는다.

## 4. m64 수락 후의 별도 remaining9 계약

이 항은 **미실행 후속 계획**이며 첫 m64 수락과 별도9점 승인이 있어야 열린다. m64 승인파일을 수정하지 말고 원 R4AG root에서 새 batch를 준비한다. 과학 코드나 resource policy를 바꾸지 않는다.

```sh
cd /absolute/new/R4AH_runtime/r4ag
python source/batch.py prepare --output /absolute/new/R4AI_remaining9_batch --workers 3
B=/absolute/new/R4AI_remaining9_batch/BATCH.json
H=$(sha256sum "$B" | cut -d ' ' -f1)
# 별도 explicit approval 이후에만:
python source/batch.py authorize --batch "$B" --confirm-sha256 "$H" \
  --nodes m128 m256 m512 m1024 p1024 p512 p256 p128 p64 --authorize-native
python source/batch.py run --batch "$B" --max-new-nodes 9
```

두 batch는 같은 native bytes와 같은 R4AG source/input lock을 요구한다. 원 runtime 경로를 유지한 NCP에서 `runtime_tools/merge_returns.py`로 읽기 전용 합산한다. selection JSON의 두 path는 절대 BATCH 경로, SHA는 실제값이다.

```json
{
  "schema": "R4AI_MULTI_BATCH_SELECTION_V1",
  "batches": [
    {"path": "/absolute/new/R4AH_m64_session/batch/BATCH.json", "sha256": "REPLACE_WITH_ACTUAL_M64_BATCH_SHA256", "nodes": ["m64"]},
    {"path": "/absolute/new/R4AI_remaining9_batch/BATCH.json", "sha256": "REPLACE_WITH_ACTUAL_REMAINING9_BATCH_SHA256", "nodes": ["m128","m256","m512","m1024","p1024","p512","p256","p128","p64"]}
  ]
}
```

```sh
python /absolute/new/R4AI_release/runtime_tools/merge_returns.py \
  --r4ag-root /absolute/new/R4AH_runtime/r4ag \
  --selection /absolute/new/selection.json \
  --output /absolute/new/FINAL_MULTI_BATCH_STENCIL_RETURN.json
```

이 도구는 native 실행을 하지 않으며 원 verifier로 각 결과를 검사한다. 기존 m64를 재계산하지 않는다. source/ABI/native가 다르거나 runtime이 이동됐다면 별도 검토 없이 완화하지 않는다. missing point이면 해당 window total=null이다. 10점 실제 end-to-end 실행은 R4AI에서 수행하지 않았다.

## 5. 새 reference code의 사용 범위

`local_theory/cr_reion`은 MODEL/REFERENCE 계산이다. discrete count exact intervals, Maxwell floating core, H5 dp measure, CX ledger, Bianchi-I map, moving-metric diagnostic와 조건부 residual/error chain을 제공한다. actual H5 state/host/source certificate가 아니다. fixture를 physical packet으로 승격하지 않는다. 현재137개 신규시험 결과는 evidence에 있다. 원 R4Z–R4AH suite를 자동으로 전부 다시 실행하지 않는다. 환경/소스 변경에 영향받는 필요한 새 검사만 별도 실행한다.

reference CLI 예시는 다음이며 원자적분이 아니다. 결과 path는 새 경로여야 한다.

```sh
cd /absolute/new/R4AI_release
S=$(sha256sum fixtures/SOURCE_MODEL.json | cut -d ' ' -f1)
E=$(sha256sum fixtures/EVENT_MODEL.json | cut -d ' ' -f1)
PYTHONPATH=local_theory python -m cr_reion \
  --source fixtures/SOURCE_MODEL.json --source-sha256 "$S" \
  --event fixtures/EVENT_MODEL.json --event-sha256 "$E" \
  --output /absolute/new/MODEL_ONLY_COUNT.json
```

## 6. 외부 반환 계약과 병렬 로컬 연구

source/base/new HEAD/tree, patch coverage, actual environment/native SHA, exact input/authorization/reservation, 성공 또는 실패한 전체 node outputs, 구간반경과 elapsed/RSS, SHAmanifest, read-only collect를 반환한다. actual provider ACK 없는 backup 성공은 쓰지 않는다. old completed m64/center/M9를 반환 검증 핑계로 반복 실행하지 않는다.

병렬 로컬 next는 `LOCAL_BRIDGE_SELECTOR_AND_PHASE_GAP_DISCRIMINATOR`다. `audit/archived_theory/`의 기존 조건부 bridge 및 selector 정리를 현재 finite candidate/selected1s와 연결한다. source-owned phasegap/continuous bounds가 없으면 그항을 정확히 남기고 일반식을 실제값으로 위장하지 않는다. 그뒤 rigorous continuous rate quadrature/tail과 actual consumer binding을 진행한다.

모든 단계에서 G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO를 유지한다. fullH/D/continuous trajectory/basis/b/energy/rate admission은 이 자료에 의해 자동 열리지 않는다. `all_possible_local_work_finished=false`다.
