# C21N off-grid 4 실행 반환: Codex 운영 인계

## 1. 완료 상태와 권위

**준비됐던 opposing-stress 네 경우는 2026-10-21 13:10 UTC에 sandbox에서 실제 완료됐다. 동일 네 경우를 NCP에서 다시 실행할 필요는 없다.** 기존 C21N 문서의 `offgrid4 NOT_RUN`은 그 문서가 작성된 당시 상태이다. 원 문서는 변경하지 않으며, 이번 실행 반환과 최종 마감 영수증이 네 경우의 현재 상태를 제공한다.

| 항목 | 권위 값 |
|---|---|
| 저장소 | https://github.com/cosmosapjw-quantum/bass_cr |
| 이번 반환 branch | `research/cr-c21n-offgrid4-sandbox-20261021` |
| 이번 반환 PR | https://github.com/cosmosapjw-quantum/bass_cr/pull/95 |
| 이번 반환 content commit | `e7729092abc6edbe74f31d0ed82aa84d5506b8d5` |
| 후속 NCP4 수용 addendum | `038aa0c8e5790f5c94e596035ea816fbca588a15` — parent는 위 반환 content, 같은 PR95 |
| 실제 ODE 실행 content | `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9` |
| 원 물리 source | REI `3b85dedce84d37b3e165da00685a8a984950aafe` |
| 실제 run identity | `f42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023` |
| Run ID | `c21n_offgrid4_opposing_z20_z4_20261021` |
| 관측 실행 host / site | `af4832b34a81` / `sandbox` |
| 최종 document head | 최종 document publication receipt의 실제 SHA를 따른다. 자기 문서 SHA를 source SHA로 쓰지 않는다. |
| 백업 권위 | 최종 backup receipt의 ZIP SHA256·provider object ID·ACK·download 검증 단계를 각각 따른다. |

Content commit과 draft PR95는 실제 GitHub 생성 ACK에 결속한다. 최종 remote-ref 대조·document 게시·백업 상태는 각각의 실제 마감 영수증을 따른다.

기존 C21L81, C21M26, NCP98, combined125 및 이번 새4의 ODE를 재실행하지 않는다. 기존125는 `26 sandbox + 98 NCP + 1 C21L reference`이고, 여기에 네 off-grid 표본을 더한129는 불규칙 ensemble이다. 기존 NCP98은 `COMPLETE_SCOPED`다. 초기 기록의 네 경우 NCP `NOT_RUN`·접근 `UNAVAILABLE`는 sandbox 실행 시점의 관측이며, 이후 도착한 외부 반환의 현행 상태를 대신하지 않는다.

### 이후 발견된 NCP4 반환

PR94(https://github.com/cosmosapjw-quantum/bass_cr/pull/94)는 13:06 UTC intake 이후인 13:14 UTC에 게시됐다. NCP attempt는 `20261021T131024Z`, hostname은 `s1a0e5abed09`, identity는 `a07a95f85042f9db7df2e3e465288524b458bcb6f190e9d4f01db1869c139360`이다. Sandbox는13:10:16, 이 NCP attempt는13:10:24에 시작한 서로 다른 실행이다. Source17개·grid·tolerance 및 NumPy2.3.5·SciPy1.17.0 metadata는 일치하며 Python은 sandbox3.12.14와 NCP3.12.3으로 다르다. 네 `history.npz` 전체 bytes와236개 FP64 배열의52,520개 값이 모두 일치하고 최대 절댓값 차이는0이다. 수용 단계의 새 ODE는0회다.

**현행 NCP4 상태는 `COMPLETE_SCOPED_EXTERNAL_RETURN_ACCEPTED`이다.** `external_ncp4/NCP_RETURN_ACCEPTANCE.json`은 `PASS_SCOPED`이며 SHA256은 `693e439f9d5cc90faab22c39d8dace299b537c49fd45f87306e5538c38e03af5`다. 외부 실행4회를 추가 수용했지만 새로운 고유 target은0개이므로 ensemble은129이며133으로 세지 않는다. 기존 sandbox raw와 identity는 별도로 보존한다. Addendum은 `external_ncp4/`의52개 새 파일만 게시했고 원 science/raw를 변경하지 않았다.

두 외부 CSV의 원 hash 불일치는 LF/CRLF 직렬화 차이로 기록했다. 메모리에서 줄바꿈만 변환했을 때 원 광고 hash와 정확히 맞았으며 Git 원 bytes·원 receipt를 변경하지 않았다. 따라서 원 export 전체 manifest가 모두 PASS라고 주장하지 않는다. 외부 `content_tree`의64자리 값은 Git tree가 아니라 run identity임을 명료화했고, 생략한 `components_campaign129.npz`의 기존125 prefix 주장도 이번 수용으로 검증·채택하지 않았다.

Sandbox와 NCP의 **저장된 전체 네 궤적의 byte 일치**는 같은 prepared/cached source를 실행한 두 site 사이의 결과이다. 원 uncached solver를 별도로 적분한 paired replay는 여전히 `NOT_RUN`이며, uncached 대비 증거는404개 저장 상태의 fields/RHS 정적 대조다. 이 구분을 유지한다.

## 2. Codex에 그대로 전달할 요청

```text
cosmosapjw-quantum/bass_cr의 C21N off-grid 4 실행 반환을 이어서 처리해줘.
이번 branch는 research/cr-c21n-offgrid4-sandbox-20261021,
PR은 https://github.com/cosmosapjw-quantum/bass_cr/pull/95,
반환 content는 e7729092abc6edbe74f31d0ed82aa84d5506b8d5이다.
최종 document head와 provider 백업 상태는 실제 마감 영수증에서 확인해.

준비됐던 네 경우는 2026-10-21 13:10 UTC sandbox에서 이미4/4완료됐다.
실제 실행 content5ecb8a6c4961302b7066b06278e72ecd2d77f8c9,
물리 source3b85dedce84d37b3e165da00685a8a984950aafe,
run identityf42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023이다.
기존81/125 및 새4를 재실행하지 마. 기존 NCP98 COMPLETE를 유지해.
PR94로 뒤늦게 발견된 NCP4는 COMPLETE_SCOPED_EXTERNAL_RETURN_ACCEPTED다.
Addendum038aa0c8e5790f5c94e596035ea816fbca588a15와
external_ncp4/NCP_RETURN_ACCEPTANCE.json의 PASS_SCOPED에 결속해.
과거 sandbox 시점의 NCP NOT_RUN을 현재 상태로 반복하지 마.
NCP4는 별도 실행 provenance이며 같은 target4이므로 고유 입력은129개를 유지해.

새 thread에서는 최신 결과/백업 ACK를 수용하고 현재 사용자의 목표에 맞는
다음 실제 미완료 질문·입력을 선정해. 이미 승인된 범위에서 가능한 작업은 계속하고,
사용자가 고정한 물리 가정을 바꿔야 할 때만 추가 선택을 확인해.
완료 입력의 반복이나 이름만 바꾼 cycle을 시작하지 말고 상세 benchmark는 하지 마.
이미 끝난 SciSpace/Exa/Wolfram 근거·이론·정적 검사와 독립 PNG review를 재사용해.

후속 미완료 질문에 맞는 새 grid를 선정하고 물리 타당성을 확인한 뒤,
completed_input_guard.py를 먼저 호출하고 exit0일 때 별도 고정5ecb checkout의
원 ncp_run.sh를 써. 이 인계문은 기존 사용자 승인에 새 승인 단계를 추가하지 않는다.
129 registry는 과거N runner에 자동 주입되지 않는다. 완료 입력을 이름만 바꾸거나
resume/다른 run ID로 다시 실행하지 마. Guard 통과 자체는 물리 타당성이나 새 입력
실행 승인을 대신하지 않는다. 지금 네 grid에 대한 정상 guard 결과는 exit2이다.

NCP의 명목64 logical CPU/128GB를 현재 실측으로 쓰지 말고, affinity/cgroup quota/
cpuset/RAM/load/기존lease/disk/inode를 새로 읽어. CPU55를 보호하고 coordinator
비용을 포함해. Numeric library thread1과 프로세스 전체 thread 수는 구분해.
다른 owner의 작업·파일·lease를 건드리지 않고 남은 case와 실제 유휴 자원에 맞춰
dispatch해. 과거99G root disk 고갈 보고를 현재 df/statvfs 관측으로 쓰지 마.

매 단계 EXECUTION | PUBLICATION | BACKUP | DAG를 별도 표시해.
다른 대화의 접근 불가 범위는 UNAVAILABLE, 이전 Drive의 무ACK 상태는
UNKNOWN_NO_ACK로 보존하고 새 근거 없이 전역 부재·실패나 백업 성공을 선언하지 마.
global_error_bound=null; preliminary non-tilted collisionless LRS scope를 유지해.
General triaxial/full reionization/CMB는 HOLD다.
```

## 3. 복원 직후의 읽기 전용 확인

아래는 실제로 복원한 반환/document checkout의 절대 경로를 지정한 뒤 실행한다. 새로운 checkout이 필요하면 현재 저장공간을 먼저 확인하고 별도 경로에 만든다. 다른 owner의 checkout을 변경하지 않는다. GitHub의 최신 branch head를 실제 실행 source로 소급하지 않는다.

```bash
set -euo pipefail
task_repo='/absolute/path/to/restored/bass_cr'
task_content='e7729092abc6edbe74f31d0ed82aa84d5506b8d5'
task_unit="$task_repo/research/cr_c21n_offgrid4_20261021"
task_python="${C21N_PYTHON:-python3}"

git -C "$task_repo" cat-file -e "$task_content^{commit}"
git -C "$task_repo" merge-base --is-ancestor "$task_content" HEAD
git -C "$task_repo" rev-parse HEAD

"$task_python" -B - "$task_repo" "$task_content" <<'PY'
import hashlib, json, pathlib, subprocess, sys
repo = pathlib.Path(sys.argv[1]).resolve()
commit = sys.argv[2]
relative = 'research/cr_c21n_offgrid4_20261021/CONTENT_MANIFEST.json'
data = subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + relative])
assert (repo / relative).read_bytes() == data, 'CONTENT_MANIFEST_CHANGED'
manifest = json.loads(data)
document_mutable = {
    'research/cr_c21n_offgrid4_20261021/RESEARCH_DAG.json',
    'research/cr_c21n_offgrid4_20261021/STAGE_LEDGER.json',
}
assert document_mutable <= {item['path'] for item in manifest['files']}, 'DOCUMENT_EXCEPTION_PATHS_MISSING'
git_payloads_verified = working_payloads_verified = 0
for item in manifest['files']:
    path = (repo / item['path']).resolve()
    assert path.is_relative_to(repo), 'PATH_OUTSIDE_RESTORED_REPOSITORY'
    payload = subprocess.check_output(['git', '-C', str(repo), 'show', commit + ':' + item['path']])
    assert len(payload) == item['size'], item['path']
    assert hashlib.sha256(payload).hexdigest() == item['sha256'], item['path']
    git_payloads_verified += 1
    if item['path'] not in document_mutable:
        assert path.read_bytes() == payload, 'WORKING_PAYLOAD_CHANGED:' + item['path']
        working_payloads_verified += 1
print(json.dumps({'content': commit,
    'historical_git_payloads_verified': git_payloads_verified,
    'current_working_payloads_verified': working_payloads_verified,
    'content_manifest_working_bytes_unchanged': True,
    'historical_content_files_including_manifest': git_payloads_verified + 1,
    'working_payload_exceptions_bound_by_document_receipt': sorted(document_mutable),
    'science_calls': 0}))
PY
```

이 검사는 원 content의 모든 payload를 고정된 `e7729092...` Git blob의 크기·SHA256으로 검증한다. 현재 working tree는 실제 게시·백업 상태를 갱신하는 `RESEARCH_DAG.json`과 `STAGE_LEDGER.json` 두 문서만 명시적으로 제외하고 나머지 science/source/raw를 같은 Git bytes와 대조한다. 두 상태 문서와 추가된 document 파일은 별도 document receipt에 결속한다. 출력 count는 manifest에서 실제 계산하며, 현재 snapshot은 Git payload92개·working payload90개와 불변 manifest1개이다. 완료된 물리 계산·전체 테스트를 다시 수행하는 명령이 아니다.

이92/90개 검증 범위는 초기 `e7729092...` content snapshot이다. 이후 NCP52개 추가 파일은 `038aa0c8...` addendum과 `external_ncp4/NCP_RETURN_ACCEPTANCE.json`에 별도로 결속되며, 위 명령이 그52개까지 검사했다고 보고하지 않는다.

### 현재 네 입력의 거부 확인

다음은 solver를 import하지 않는 읽기 전용 guard 호출이다. **기대 exit code는2**이며 이를 과학 실패로 기록하지 않는다.

```bash
task_completed_grid="$task_repo/research/cr_c21n_mass_shell_cache_20261021/prepared_offgrid4/grid_offgrid4.json"
if "$task_python" -B "$task_unit/completed_input_guard.py" --grid "$task_completed_grid"; then
  printf '%s\n' 'UNEXPECTED: completed four were not rejected' >&2
  exit 1
else
  task_guard_status=$?
  test "$task_guard_status" -eq 2
fi
```

이후 현재 네 입력에 `ncp_run.sh run`이나 `resume`을 연결하지 않는다. 이미 해당 guard 결과가 보존돼 있으므로, 복원 파일·명령 경로를 확인해야 하는 상황에만 이 짧은 호출을 한다.

### 현재 자원 관측

아래 코드는 CPU lease를 획득하거나 run directory를 생성하지 않는다. 출력 storage path는 실제 사용할 filesystem의 **이미 존재하는** 경로로 지정한다.

```bash
task_storage='/absolute/existing/path/on/intended/output/filesystem'
task_lease_dir="${C21N_LEASE_DIR:-/tmp/bass_cpu_leases}"
"$task_python" -B - "$task_repo" "$task_storage" "$task_lease_dir" <<'PY'
import importlib.util, json, os, pathlib, socket, sys
repo, storage, leases = map(pathlib.Path, sys.argv[1:])
source = repo / 'research/cr_c21n_mass_shell_cache_20261021/shared_resources.py'
spec = importlib.util.spec_from_file_location('readonly_c21n_resources', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
v = os.statvfs(storage)
print(json.dumps({'observed_host': socket.gethostname(),
    'resource_observation': module.observe_load(seconds=.2),
    'storage_path': str(storage.resolve()),
    'available_bytes': v.f_bavail * v.f_frsize, 'available_inodes': v.f_favail,
    'lease_directory': str(leases),
    'lease_names_only_not_lock_ownership': sorted(p.name for p in leases.iterdir()) if leases.is_dir() else [],
    'science_calls': 0}, indent=2))
PY
df -h "$task_storage"
df -i "$task_storage"
```

Lease 파일 이름만으로 잠금의 소유·유휴 여부를 판단하지 않는다. 실제 launcher는 기존 협력 lease를 원자적으로 획득할 수 있는 자원만 사용한다. 사용자·프로젝트 disk quota는 `statvfs`만으로 보증되지 않는다. 과거99G root filesystem의 고갈 보고와 이번 sandbox의24.36GB 관측은 모두 과거 특정 host/시각의 기록이다.

## 4. 다음 미완료 질문에 맞는 새로운 입력 실행

이번 반환 마감에는 추가 grid가 선정되지 않았다. 다음 대화에서는 실제 사용자 요청과 이미 승인된 연구 범위를 따라 미완료 질문·입력을 선정할 수 있다. 다음 블록은 **선정한 새 grid의 초기 물리 타당성을 확인한 뒤** 쓰는 명령 구조이며 별도 재승인을 요구하는 gate가 아니다. 사용자가 고정한 source·물리 가정·species·허용오차를 바꿔야 하는 경우에는 그 변경 선택을 확인한다. 현재 offgrid4 또는 기존125를 넣지 않으며 새 grid·실행 directory·source identity를 별도로 기록한다.

두 checkout을 구분한다. `task_repo`는 이번 반환 자료와129 guard가 있는 checkout이다. `task_exec_repo`는 원 실행 content `5ecb8a6c...`의 독립적이고 깨끗한 checkout이다. 원 launcher는 HEAD를 검사하므로 새 반환/document checkout을 원 실행 source로 대용하지 않는다.

```bash
set -euo pipefail
: "${C21N_NEXT_GRID:?Set the selected new physical grid absolute path}"
: "${C21N_EXEC_REPO:?Set an isolated clean checkout at the tested 5ecb content}"
: "${C21N_NEW_OUTPUT:?Set an unused absolute create-only run path}"

task_new_grid="$C21N_NEXT_GRID"
task_exec_repo="$C21N_EXEC_REPO"
task_new_output="$C21N_NEW_OUTPUT"
export C21N_CONTENT_COMMIT='5ecb8a6c4961302b7066b06278e72ecd2d77f8c9'
test "$(git -C "$task_exec_repo" rev-parse HEAD)" = "$C21N_CONTENT_COMMIT"
test ! -e "$task_new_output"

"$task_python" -B "$task_unit/completed_input_guard.py" --grid "$task_new_grid"

export C21N_PYTHON="$task_python"
export C21N_WORKERS="${C21N_WORKERS:-62}"
export C21N_LEASE_DIR="${C21N_LEASE_DIR:-/tmp/bass_cpu_leases}"
export C21N_TMPDIR="${C21N_TMPDIR:-/tmp}"
task_launcher="$task_exec_repo/research/cr_c21n_mass_shell_cache_20261021/ncp_run.sh"
bash "$task_launcher" plan "$task_exec_repo" "$task_new_grid" "$task_new_output"

# Same selected grid and current resource conditions; guard immediately before dispatch.
"$task_python" -B "$task_unit/completed_input_guard.py" --grid "$task_new_grid"
bash "$task_launcher" run "$task_exec_repo" "$task_new_grid" "$task_new_output"
```

이 블록은 실제 NCP host에서만 실행한다. `ncp_run.sh`의 `execution_site=ncp`는 operator 선언이므로 관측 hostname과 실제 완료 receipt를 함께 기록한다. Sandbox에서 이 launcher를 호출하여 NCP 실행으로 표시하지 않는다.

62는 요청 상한이며 worker 수의 보장이 아니다. CPU55를 제외하고 coordinator CPU·256MiB, worker별512MiB, reserve `max(1GiB, observed memory limit/8)`를 보수적 예산으로 취급한다. 실제 case 수·affinity·quota·공유 부하·RAM에 맞춰 worker 수를 줄인다. 이는 실측 memory bound가 아니다. Numeric library의 thread 수는1로 고정하지만 multiprocessing 관리 thread를 포함한 프로세스 전체 thread 수와 구분한다. 이번 실행에서는 반환 시 각 worker의2threads가 관측됐다.

다른 session의 부하가 늘어나면 신규 dispatch를 줄이고 완료 raw를 보존한다. 다른 owner의 process·lease·output을 변경하지 않는다. Disk/inode를 사전과 dispatch 전에 다시 확인하고 보수적 예산을 충족하지 않으면 시작하지 않는다. 운영 수정이 필요하면 원 source를 덮어쓰지 않고 차이·새 hash·적용 범위를 기록한다.

## 5. 분석·검증의 정확한 범위

새4는101점씩 총404개 저장 상태를 갖는다. Prepared/cached와 원 uncached source의 fields23,836값, RHS16,160값이 FP64 bytes까지 일치했다. 이는 저장 상태에 대한 정적 검산이다. 별도 수용한 NCP 실행과 sandbox 실행 사이에서는 같은 prepared source의 네 저장 궤적 전체 bytes가 일치했다. 원 uncached solver로 같은 네 경우를 다시 적분한 full-trajectory replay는 `NOT_RUN`이며 모든 adaptive 단계 또는 연속해의 동등성을 주장하지 않는다.

초기 target·Hamiltonian·입자수·tensor closure·massive/radiation/shear 항등식과 실제FPoffset을 검사했다. Radiation L8의4개E/N배열을64개 원 각도노드에서 복원한103,424값의 이산 최솟값은 양수였다. 연속 각도 전체의 양성 정리는 아니다. Independent PNG3개 직접 review는 `PASS_SCOPED`, PDF별도 raster review는 `NOT_RUN`이다. 승인된 기존 SciSpace/Exa/Wolfram 근거와 C21N 미분 모듈은 재사용했다.

새4 endpoint maxima는 $\Sigma_f=2.147246027\times10^{-5}$, $\Pi_{m,f}=9.961314242\times10^{-6}$, $\Pi_{r,f}=4.113985087\times10^{-5}$, $\Pi_{\mathrm{tot},f}=3.117853663\times10^{-5}$이다. 이는 새4의 표본 최대값이다. 실제초기jet와 저장점의 최대상대잔차는 첫 양의점2.12234%, $\eta\approx0.100456$에서15.83743%이며 전구간 오차상계가 아니다. `global_error_bound=null`이다.

선택적인 후처리 재현이 구체적으로 필요할 때만 아래처럼 **존재하지 않는 새 출력 경로**를 지정한다. 이는 완료 검증의 재실행 의무가 아니다.

```bash
: "${C21N_OPTIONAL_ANALYSIS_OUTPUT:?Set a fresh output path only for a concrete read-only analysis need}"
test ! -e "$C21N_OPTIONAL_ANALYSIS_OUTPUT"
"$task_python" -B "$task_unit/analyze_offgrid.py" \
  --repo "$task_repo" --input "$task_unit/raw_offgrid4" \
  --context "$task_repo/research/cr_c21m_independent_stress_20261021/analysis_campaign125_20261021/components_campaign.npz" \
  --output "$C21N_OPTIONAL_ANALYSIS_OUTPUT"
```

## 6. 문서·백업 마감과 다음 단계

사용자가 제공한 physmath 규약1.0.0의 완료 요청은 이번 실행 반환 단위의 남은 게시·백업·DAG·인계를 실제로 마치는 의무로 적용한다. 이미 완료된 수용·이론·구현·과학 계산·검산·그림 검토는 그 근거를 재사용한다. 연구 루프라는 이유로 후속 cycle이나 완료된 네 입력의 NCP 중복 실행을 시작하지 않는다.

`EXECUTION | PUBLICATION | BACKUP | DAG`를 별도로 보고한다. Content는 source/raw/분석 snapshot, document는 실제 게시·백업 결과를 결속하는 후속 기록이다. Git content snapshot과 원 manifest는 보존하며, 두 상태 문서의 실제 마감 갱신은 별도 document commit·receipt로 결속한다.

구체적인 마감 순서는 다음과 같다. 먼저 실제 branch/ref/PR가 위 content를 포함하는지 확인하고, 이미 존재하면 중복 게시하지 않는다. 이어 해당 배송 ZIP의 manifest·SHA256과 저장처별 실제 ACK를 최종 영수증으로 수용한다. 마지막으로 실제 document commit과 그 최종 영수증을 결속하고, 완료·미완료·HOLD를 기록한 다음 대화용 인계문을 제공한다. 이미 완료된 단계는 다시 실행하지 않는다.

Provider ACK, object ID/size, ZIP SHA256, 실제 다운로드 후 byte 검증은 별도 단계이다. 이전 C21N Drive `UNKNOWN_NO_ACK`를 임의로 성공·실패로 바꾸지 않는다. 미확정 작업이 남으면 exact object metadata 등 제한된 수용으로 해결하며 동일 파일을 추측으로 중복 업로드하지 않는다. 다른 대화는 이번 도구로 접근하지 못한 범위를 `UNAVAILABLE`로 기록하고 전역적으로 새 결과가 없다고 단정하지 않는다.

이 인계문 작성 시점의 이번 main 배송본은 Library·Dropbox의2개 ACK가 있고 Drive는 `UNKNOWN_NO_ACK`다. 외부 PR94의 Drive·Dropbox ACK/readback은 PR94 작성자가 남긴 별도 archive 영수증으로 수용했으며 이번 intake에서 provider를 재조회하지 않았다. 그 별도 영수증은 이전 미확정 Drive 업로드를 해결하지 않는다. 이후 document/addendum 배송의 정확한 ZIP·ID·SHA·ACK는 최종 authority receipt를 따른다.

이번 단위는 네 경우의 실행 반환·외부 NCP4 수용·문서·백업 마감까지 처리한다. 마감 후 완료 상태를 보고하되 이 인계문이 미래 사용자의 연구 요청이나 기존 승인 범위를 제한하지 않는다. 다음 대화에서는 완료 입력을 재실행하지 않고 실제 미완료 질문·입력을 선정하여 이어간다. 이름만 바꾼 반복 cycle이나 상세 benchmark를 만들지 않는다. Preliminary non-tilted collisionless LRS 범위, 원FP64·source·허용오차를 유지하며 general triaxial/full reionization/CMB는 `HOLD`다.
