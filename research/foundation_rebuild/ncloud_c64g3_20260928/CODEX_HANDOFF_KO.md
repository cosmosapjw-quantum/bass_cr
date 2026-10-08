# Codex start handoff: BASS c64-g3 F0

역할: **BASS_NCLOUD_F0_FIXED_EXECUTOR**.
승인된 설계를 다시 설계하지 말고, 고정 패키지의 검증·실행·evidence 반환만 수행한다.
첫 blocker에서 원본을 보존하고 중단한다. 이 인계는 F1–F3 자동 구현/실행 지시가 아니다.

## 1. 정확한 계획과 원본을 읽는다

Repository: cosmosapjw-quantum/bass_cr.
Plan branch: research/fnd-ncloud-c64g3-codex-handoff-20260928.
Plan commit/tree: 시작 프롬프트 또는 배포 PUBLICATION_RECEIPT.json의 exact 값을 사용한다.
Scientific source commit: c954d68fdc86527453765a563b3a025351163ed9.
Scientific source tree: 0e13583301e271e9a9e8aa0eae3c05eaf8580a1a.

먼저 현재 HEAD/tree/branch/status와 프로젝트 실행 중 여부를 읽어 기록한다.
사용자 checkout을 바꾸지 않아도 git fetch와 git show PLAN_COMMIT:path로 이 계획을 읽을 수 있다.
원 source checkout과 새 docs commit을 혼동하지 않는다. 원 branch가 움직였으면
자동 rebase/reset하지 말고 불일치를 보고한다. 원 작업 디렉터리와 .codex/는 보존한다.

읽기 순서: root AGENTS.md, docs/READBACK_POLICY.md,
research/foundation_rebuild/ncloud_c64g3_20260928/{AGENTS.md,ARTIFACTS.json,
STATUS.json,IMPLEMENTATION_PLAN_KO.md,CODEX_HANDOFF_KO.md}.
다음으로 승인 ZIP의 REDESIGN_KO.md, MIGRATION_RUNBOOK_KO.md,
IMPLEMENTATION_PLAN_KO.md와 원 TP2E README/GRANT를 읽는다.
ChatGPT 대화 내용, 다른 프로젝트 문서, 추정 최신 branch를 입력 SSOT로 사용하지 않는다.

## 2. 입력을 찾되 없으면 대체하지 않는다

Cloud 우선 경로: /data/bass/inputs.
Local 우선 경로: $HOME/Downloads 및
$HOME/Dropbox/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/runs.
한정된 위 경로와 사용자가 지정한 실제 경로만 확인한다. 비밀키·.env·계정 설정은 수집하지 않는다.

필수 archive는 ARTIFACTS.json의 원 설계 ZIP과 원 TP2D 전체 RETURN ZIP이다.
원 설계 ZIP 안 upstream/BASS_TP2E_RESEARCH_20260928.zip을 사용한다.
그 TP2E ZIP도 독립 hash를 검사한다. 요약 JSON이나 재압축한 유사 ZIP으로 대신하지 않는다.
기존에 같은 F0 결과가 있다면 its input/package/environment identity를 확인해 보고하고
DUPLICATE_F0_NOT_RERUN으로 중단한다. 다른 환경의 결과는 cloud PASS로 이식하지 않는다.

원 Python minor, NumPy/SciPy/pytest 기록과 승인된 실행 환경을 확인한다.
준비가 안 됐으면 ENVIRONMENT_BLOCKED를 반환한다. apt/pip upgrade나 패키지 버전 변경으로
자동 수리하지 않는다. c64-g3를 이미 할당받았다고 가정하거나 SSH host를 발명하지 않는다.
실제 cloud가 준비되지 않았으면 준비된 사용자 local host에서 F0가 가능한지 확인하고,
그 결과는 local로 표시한다. 가용한 실행 환경이 없으면 필요한 최소 입력만 반환한다.

## 3. 준비된 호스트에서 F0만 한 번 실행한다

/data가 의도한 작업 볼륨인지 findmnt/lsblk로 확인한다. format/mount 변경을 하지 않는다.
입력과 승인 ZIP은 read-only 취급한다. code/env/output 기존 경로에 덮어쓰지 않는다.
source hash와 archive member 안전성을 확인한 뒤 새 경로에 해제한다.
아래 변수는 실제로 확인한 경로를 설정한다. 예시 경로가 없으면 mkdir로 무조건 대체하지 않는다.

```bash
# 승인된 Python 환경을 활성화한 상태.
ROOT=/data/bass
DESIGN="$ROOT/code/BASS_NCLOUD_C64G3_REDESIGN_20260928"
PKG="$ROOT/code/BASS_TP2E_RESEARCH_20260928"
SOURCE="$ROOT/inputs/tp2d_runtime_self_qualified_20260927T074944Z_RETURN.zip"
HOSTREC="$ROOT/receipts/HOST_$(date -u +%Y%m%dT%H%M%SZ).json"
python "$DESIGN/cloud_preflight.py"   --tp2d-archive "$SOURCE"   --tp2e-package "$DESIGN/upstream/BASS_TP2E_RESEARCH_20260928.zip"   --out "$HOSTREC"
```

preflight의 실제 exit/status를 읽는다. 실패하면 다음 명령을 실행하지 않는다.
worker RSS 미측정 safe_worker_ceiling=null은 native를 막지만 single-process F0를 막지 않는다.
실제 준비된 local host에서는 ROOT 등을 local 전용 경로로 바꾸고 host_is_ncloud=false를 기록한다.

```bash
OUT="$ROOT/runs/tp2e_cache_$(date -u +%Y%m%dT%H%M%SZ)"
printf 'OUT=%s\n' "$OUT"
export PYTHON_BIN="$(command -v python)"
bash "$DESIGN/run_cache.sh" "$PKG" "$SOURCE" "$OUT"
RC=$?
printf 'EXIT=%s\n' "$RC"
```

PIPEFAIL을 사용하고 tee로 exit를 잃지 않는다. 실패 exit 뒤에도 원 output을 읽어 보고하되
자동 재시작하지 않는다. tmux는 실제 terminal이 있고 필요할 때만 사용한다.
실행 task가 끝났는지 확인하기 전에 완료 또는 background 성공을 약속하지 않는다.

고정 조건: worker 1, BLAS/OpenMP 1, 새 공간적분 0, reference 재적분=false.
원 TP2E entrypoint가 수행하는 새 환경 첫 admission test를 한 번 그대로 실행한다.
32라는 과거 count를 강제로 맞추거나 실패 test를 skip하지 않는다. 실제 count가 근거다.

## 4. 반환과 종료

아래 요약과 SHA를 반환한다. 출력 누락 시 null을 과학 실패/통과로 해석하지 않고
누락 상태를 별도 설명한다. 기존 RETURN_REPORT 자체를 고치지 않는다.

```bash
jq '{status,original_tp2d_status,new_tests,source_audit,
 new_method_temporal_comparison_qualified,
 comparison:{selected_nstep:.comparison.selected_nstep,
 historical_replay:.comparison.historical_replay,
 candidates:.comparison.candidates,pairs:.comparison.pairs,
 new_operator_evaluations:.comparison.new_operator_evaluations,
 reference_reintegrated:.comparison.reference_reintegrated},
 capture_execution_allowed,production_admission,all_bound,b_grid,
 first_failure,wall_seconds}' "$OUT/RETURN_REPORT.json"
sha256sum "$OUT/RETURN_REPORT.json" "${OUT}_RETURN.zip" "$HOSTREC"
```

CLOUD_PIP_FREEZE, Python/Codex version, BLAS configuration을 private output receipt로 기록한다.
pip freeze에 credential-bearing URL이 있으면 공개본에서 가리고 원 private provenance는 보존한다.
반환 파일: 새 RETURN ZIP, HOST receipt, environment receipt, F0_RETURN_HANDOFF.json.
환경 때문에 실행 전 중단됐으면 blocker receipt와 실제 확인한 input identity만 반환한다.
F0_RETURN_HANDOFF.json의 형식은 RETURN_CONTRACT.json을 따른다.

원 TP2D status는 TEMPORAL_REFINEMENT_UNRESOLVED로 고정한다.
F0 성공도 capture=false, production=HOLD, all_bound=OPEN, b_grid=NO_GO,
original_capture_gap_resolved=false, continuous_global_supremum_bound=false를 유지한다.
F0가 성공하면 STOP_F0_COMPLETE. 실패면 해당 원 status를 보존해 종료한다.

## 금지

F0 실패 후 자동 patch/retry, F1–F3 코드 작성, native compile/probe,
probe_native.py --workers 64, 새 DOP853/full spatial run, tolerance 완화,
near-time cache merge, source/basis/library hash 교체, 자동 의존성 업그레이드는 금지한다.
main merge/force push/reset --hard/git clean/자동 stash/자동 새 worktree,
VM·disk·bucket 생성/삭제, credentials 공유, 승인 없는 SSH/provisioning도 금지한다.
이 프롬프트만으로 GitHub 결과 게시나 새 provider upload 권한을 만들지 않는다.
원격 변경을 별도로 승인받은 경우 root readback policy의 R1을 기본으로 하며,
ACK/metadata와 실제 restore 검증은 구분한다. 첫 증거 세트로 gate가 닫히면 중복 검증 루프를 멈춘다.
