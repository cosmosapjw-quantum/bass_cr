# CR-PHYS02D — 실제 백업에서 시작하는 local Codex 지시문

이 문서는 실제 science publication 및 immutable handoff ZIP의 외부 시작 문서다. 아래 JSON identity는 실제 완료된 science commit 및 두 백업 영수증과 결속되어 있다. 이 ZIP의 로컬 전체 바이트 복원과 plan 입력 admission은 통과했다. 원격 게시 검증은 이름·ID·크기·경로/rev metadata이며 원격 ZIP 재다운로드 검증은 수행하지 않았다. 이 문서의 작성은 물리 실행 또는 새 과학 판정을 뜻하지 않는다.

## 1. 실제 publication binding

다음 JSON은 확정된 시작 identity다. 두 백업에는 동일한 로컬 ZIP을 새 파일로 업로드했고, 두 provider의 실제 완료 및 4,903,951 bytes metadata를 확인했다. Provider checksum은 connector 응답에서 제공되지 않았다. 다운로드 후에는 반드시 아래 SHA256을 대조한다.

```json
{
  "science_commit": "6ed83ff61aff24fe51ff0370736f70e0e52893f8",
  "zip_filename": "CR_PHYS02D_20261011_6ed83ff6_HANDOFF.zip",
  "zip_sha256": "100e0cf1fec443067b74aed9f8d508f1daae1d117bf9005f57ebcd68e1cf2673",
  "zip_bytes": 4903951,
  "drive_zip_id": "1H3Gn3xb7InyPuXCQKxQtQ1_m02e2OnIW",
  "drive_zip_url": "https://drive.google.com/file/d/1H3Gn3xb7InyPuXCQKxQtQ1_m02e2OnIW/view?usp=drivesdk",
  "dropbox_zip_id": "id:BSpOijBcT10AAAAAAD36cQ",
  "dropbox_zip_rev": "65d8467123fdc0af03d47",
  "dropbox_zip_path": "/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02D_20261011_6ed83ff6_HANDOFF.zip"
}
```

이 JSON을 빈 새 로컬 작업 디렉터리의 `PUBLICATION_BINDING.json`으로 저장한다. 실제 science commit은 정확히 40자리 lowercase hex, ZIP SHA256은 정확히 64자리 lowercase hex다. 파일 이름/크기와 각 원격 ID·rev·path·URL이 영수증에 일치하는지 확인한다. 이후 아래 표준 라이브러리 검증도 이 JSON을 사용한다.

## 2. 연결된 백업에서 ZIP 확보

추가 사용자 첨부 없이 기존 Drive 또는 Dropbox 연결/인증/동기화 경로를 재사용하여 위 **정확한 ZIP**을 받는다. 같은 이름의 다른 ZIP이나 최신 검색 결과로 대체하지 않는다. 가능하면 정확한 Drive ID 또는 Dropbox ID+rev를 지정한다. 이미 받은 파일이 있으면 그 파일부터 크기와 SHA256을 대조한다. URL/이름만으로 동일성을 확정하지 않는다. 다운로드 출처, 실제 ID/rev, 수행한 readback 범위를 외부 로컬 receipt에 기록하며 자격증명은 출력하지 않는다.

local Codex가 연결된 백업에 접근할 수 없으면 `BACKUP_ACCESS_BLOCKED`로 정확한 대상 ID/rev/path, 실제 접근 시도와 오류, 가능했던 readback 범위만 보고한다. 다운로드·첨부·인증 성공을 지어내거나 다른 ZIP을 대신 사용하지 않는다. scoped blocker 상태에서 물리 호출은 시작하지 않는다.

받은 ZIP을 `PUBLICATION_BINDING.json`과 같은 새 작업 디렉터리에 실제 `zip_filename` 이름으로 저장한다. 기존/dirty 작업 디렉터리에 추출하지 않는다. 다음 검증 코드를 그 새 작업 디렉터리에서 실행한다. 이 코드는 stdlib만 사용하고 ZIP hash, 이름·경로 안전성, 중복·symlink·special entry, CRC, 내부 manifest 전체를 확인한 뒤에만 새 디렉터리에 추출한다. 실패하면 새 부분복원 폴더를 보존하고 덮어쓰기/자동 재시도를 하지 않는다.

```bash
python - <<'PY'
import datetime, hashlib, json, pathlib, re, stat, uuid, zipfile
work = pathlib.Path.cwd().resolve()
binding = json.loads((work / 'PUBLICATION_BINDING.json').read_text())
if '{{' in json.dumps(binding):
    raise SystemExit('PUBLICATION_BINDING_UNRESOLVED')
if not re.fullmatch(r'[0-9a-f]{40}', binding['science_commit']):
    raise SystemExit('SCIENCE_SHA_INVALID')
if not re.fullmatch(r'[0-9a-f]{64}', binding['zip_sha256']):
    raise SystemExit('ZIP_SHA256_INVALID')
name = binding['zip_filename']
if pathlib.PurePosixPath(name).name != name or '\\' in name or not name.endswith('.zip'):
    raise SystemExit('ZIP_FILENAME_INVALID')
archive = work / name
if type(binding['zip_bytes']) is not int or archive.stat().st_size != binding['zip_bytes']:
    raise SystemExit('ZIP_BYTES_MISMATCH')
hash_value = hashlib.sha256()
with archive.open('rb') as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b''):
        hash_value.update(chunk)
if hash_value.hexdigest() != binding['zip_sha256']:
    raise SystemExit('ZIP_SHA256_MISMATCH')
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
restored = work / ('CR_PHYS02D_RESTORE_' + stamp + '_' + uuid.uuid4().hex)
with zipfile.ZipFile(archive) as z:
    infos = z.infolist()
    names = [i.filename for i in infos]
    if len(names) != len(set(names)):
        raise SystemExit('ZIP_DUPLICATE_ENTRY')
    for i in infos:
        path = pathlib.PurePosixPath(i.filename)
        mode = i.external_attr >> 16
        if (not i.filename or path.is_absolute() or '\\' in i.filename
                or re.match(r'^[A-Za-z]:', i.filename)
                or any(p in ('', '.', '..') for p in i.filename.split('/'))
                or path.as_posix() != i.filename or i.is_dir()
                or stat.S_ISLNK(mode)
                or stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
            raise SystemExit('ZIP_UNSAFE_ENTRY: ' + i.filename)
    if z.testzip() is not None:
        raise SystemExit('ZIP_CRC_FAILURE')
    manifest = json.loads(z.read('BUNDLE_MANIFEST.json'))
    if manifest['science_commit'] != binding['science_commit']:
        raise SystemExit('BUNDLE_SCIENCE_COMMIT_MISMATCH')
    expected = manifest['files']
    if set(names) != set(expected) | {'BUNDLE_MANIFEST.json'}:
        raise SystemExit('BUNDLE_ENTRY_SET_MISMATCH')
    for entry, pin in expected.items():
        raw = z.read(entry)
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise SystemExit('BUNDLE_ENTRY_IDENTITY_MISMATCH: ' + entry)
    receipt = json.loads(z.read('publication/SCIENCE_COMMIT_RECEIPT.json'))
    if receipt.get('science_commit') != binding['science_commit']:
        raise SystemExit('SCIENCE_RECEIPT_MISMATCH')
    restored.mkdir(exist_ok=False)
    for i in infos:
        target = restored.joinpath(*pathlib.PurePosixPath(i.filename).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as handle:
            handle.write(z.read(i.filename))
    for entry, pin in expected.items():
        raw = (restored / entry).read_bytes()
        if len(raw) != pin['bytes'] or hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise SystemExit('RESTORE_READBACK_MISMATCH: ' + entry)
restore_receipt = {
    'status': 'ZIP_AND_EVERY_PAYLOAD_ENTRY_VERIFIED',
    'restore_root': str(restored), 'science_commit': binding['science_commit'],
    'zip_filename': name, 'zip_bytes': binding['zip_bytes'],
    'zip_sha256': binding['zip_sha256'], 'entries': len(names),
    'binding_path': str(work / 'PUBLICATION_BINDING.json')
}
with (work / ('RESTORE_RECEIPT_' + stamp + '_' + uuid.uuid4().hex + '.json')).open('x') as handle:
    json.dump(restore_receipt, handle, indent=2)
print(json.dumps(restore_receipt, indent=2))
PY
```

`restore_root`는 이 코드가 실제 출력한 새 절대경로다. 이후 실행에 그 경로를 사용한다. Git을 별도로 사용할 경우 actual science receipt의 commit을 새 checkout/worktree에서 확인하고 기존 dirty work를 보존한다. main 병합이나 force push를 하지 않는다. 이 ZIP은 dependency-complete repository-layout overlay이며 전체 역사 checkout은 아니다. 필수 inherited 259 files는 base PR #31 commit `f98ed974c3f3158dabd16cd854ecc5e04b9f5b31`에 대해 고정되어 있다. 이전 PHYS02C 후기 receipt의 sibling provenance는 base ancestry로 바꾸지 않는다.

## 3. 동결 지시문 및 harness 읽기

복원된 다음 파일을 먼저 읽고 그 범위를 유지한다.

- `research/cr_phys02d_20261011/START_NCP_CODEX_KO.md`
- 같은 단위의 `ncp/README_KO.md`, `REPORT_KO.md`, `state/SCIENTIFIC_CONTRACT.json`, `ncp/NCP_EXECUTION_CONTRACT.json`
- 모든 `state/IMPLEMENTATION_AMENDMENT_*.json`, `inputs/INPUT_IDENTITIES.json`, `inputs/DEPENDENCY_PAYLOAD_MANIFEST.json`
- `review/INDEPENDENT_DECISION.json`, `state/NEXT_DAG.json`
- `research/context/REMOTE_AGENTS.md`, `CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md`, `HPC_ACCURACY_POLICY_KO.md`, `READBACK_POLICY.md`

`handoff_harness/`의 두 Astra v4.0.0 ZIP은 별도 새 위치에서 안전 검증하여 읽고 관련 `START_HERE.md` 및 project instructions를 적용한다. frozen unit이나 원본 adapter를 수정하지 않는다. 기존 9600 raw return, 모든 FIRSTFAILURE 및 adapter sidecars를 보존한다. 실제 host가 알려 주는 모델/runtime metadata를 기록하고 모델을 추정하여 기록하지 않는다.

Scientific contract SHA256은 `bc05614e9812f616c4a4bb45805e4c0359a171813f7329794b0c10c3bf37dde2`, NCP contract SHA256은 `9dd8b098d828fcad5ddd5138afd29e9dce4805e26fbac897bd4c9a07779e8ff9`다.

## 4. stdlib plan → READY 확인 → 단 한 번 execute → 모든 결과 collect

실제 수치 실행은 기존의 일치하는 Python **3.12.3**, NumPy **2.4.2**, SciPy **1.17.0** 환경과 실제 수치 threadpool **1 thread**가 필요하다. 전역 환경을 변경하거나 다른 version으로 진행하지 않는다. plan은 NumPy/SciPy를 import하지 않는다. 실제 runtime pin은 worker가 수치 import 후에도 확인한다.

실제 host·CPU affinity·cgroup 및 보이는 부모 제한·동시 작업·사용 메모리·reserve·disk를 확인한다. 가장 제한적인 보이는 메모리에서 max(12.5%, 1 GiB)를 예약한 후 작업 가능 메모리 ≥12 GiB, 여유 disk ≥8 GiB, 유효 CPU ≥1이 필요하다. NCP64 성능이나 자원을 가정하지 않는다.

아래 script의 `RESTORE_ROOT`만 앞에서 실제 검증·출력된 절대경로로 지정한다. 선택한 pinned Python 환경에서 실행한다. UTC는 실제 시계에서 만들고 UUID를 붙인다. 공통 시스템 변수나 HOME을 재정의하지 않는다. 한 invocation만 수행하며 실패 후 script를 자동 재실행하지 않는다. 코드의 `subprocess.run`은 실제 아래 명령들을 그대로 실행한다.

```text
python ncp/launch_pulse.py --plan
python ncp/launch_pulse.py --execute --run-dir <새 실제 run directory>
python ncp/launch_pulse.py --collect --run-dir <동일 실제 run directory> --out <새 return directory>
```

```bash
python - <<'PY'
import datetime, json, pathlib, subprocess, sys, time, uuid
RESTORE_ROOT = pathlib.Path('/REPLACE_WITH_ACTUAL_VERIFIED_RESTORE_ROOT').resolve()
if 'REPLACE_WITH' in str(RESTORE_ROOT):
    raise SystemExit('ACTUAL_RESTORE_ROOT_REQUIRED')
unit = RESTORE_ROOT / 'research/cr_phys02d_20261011'
if not (unit / 'ncp/launch_pulse.py').is_file():
    raise SystemExit('RESTORED_UNIT_MISSING')
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
identifier = 'PULSE_' + stamp + '_' + uuid.uuid4().hex
operational = RESTORE_ROOT.parent / ('CR_PHYS02D_LOCAL_RECEIPTS_' + identifier)
operational.mkdir(exist_ok=False)
command = [sys.executable, 'ncp/launch_pulse.py']
plan = subprocess.run(command + ['--plan'], cwd=unit, capture_output=True, text=True)
(operational / 'PLAN.stdout.json').write_text(plan.stdout)
(operational / 'PLAN.stderr.log').write_text(plan.stderr)
if plan.returncode != 0:
    raise SystemExit('PLAN_COMMAND_FAILED; physical calls not started')
result = json.loads(plan.stdout)
if result.get('admission_status') != 'READY' or result.get('resource_probe', {}).get('admitted') is not True:
    raise SystemExit('SCOPED_ADMISSION_OR_RESOURCE_HOLD; physical calls not started')
run_dir = unit / 'evidence/runs' / identifier
return_dir = unit / 'evidence/returns' / identifier
if run_dir.exists() or return_dir.exists():
    raise SystemExit('CREATE_ONLY_RUN_OR_RETURN_COLLISION')
start = time.monotonic()
execution = None
try:
    execution = subprocess.run(command + ['--execute', '--run-dir', str(run_dir)], cwd=unit)
finally:
    record = {'command': command + ['--execute', '--run-dir', str(run_dir)],
              'cwd': str(unit), 'run_dir': str(run_dir),
              'actual_process_exit': execution.returncode if execution is not None else None,
              'elapsed_s': time.monotonic() - start,
              'execute_invocations': 1, 'automatic_retry': False}
    with (operational / 'LOCAL_EXECUTE_RECEIPT.json').open('x') as handle:
        json.dump(record, handle, indent=2)
    if run_dir.is_dir():
        collection = subprocess.run(command + ['--collect', '--run-dir', str(run_dir),
                                              '--out', str(return_dir)], cwd=unit,
                                    capture_output=True, text=True)
        (operational / 'COLLECT.stdout.json').write_text(collection.stdout)
        (operational / 'COLLECT.stderr.log').write_text(collection.stderr)
        with (operational / 'LOCAL_COLLECT_RECEIPT.json').open('x') as handle:
            json.dump({'actual_exit': collection.returncode, 'run_dir': str(run_dir),
                       'return_dir': str(return_dir)}, handle, indent=2)
        if collection.returncode != 0:
            print('COLLECTION_FAILED_PRESERVE_ALL_RAW_FILES: ' + str(operational))
    else:
        print('EXECUTE_CREATED_NO_RUN_DIRECTORY; preserve external receipts: ' + str(operational))
print('Local receipts: ' + str(operational))
PY
```

`--plan` exit 0 자체는 허가가 아니다. 반드시 `admission_status=READY`와 `resource_probe.admitted=true`를 함께 확인한다. DAG READY, independent PASS_SCOPED binding, code·input·payload identity가 모두 맞아야 한다. HOLD면 이유/plan/환경 증거를 보존하고 물리 호출 없이 보고한다. 예기치 못한 host 종료나 wrapper 중단으로 script의 finally도 실행되지 못했으면 살아 있는 실행을 중복 시작하지 않는다. 기존 coordinator/worker의 실제 종료 및 terminal receipt 생성 여부를 먼저 확인한다. 아직 실행 중이거나 쓰기가 진행 중이면 수집하지 않는다. 모두 종료된 동일 run directory에서 `--collect`만 수행한다. terminal receipt가 없다면 실제 종료 상태와 마지막 raw evidence를 확인·보존하고 종료 영수증을 지어내지 않는다.

실제 execute는 **한 번**, fullBED 다음 legacy, 동일 9600 격자 `[3200,6400]`만 허가된다. 최대 **G build 2회 + pulse 전파 2회**, 전체 coordinator wall **3600초**, 자동 재시도 없음이다. 두 birth column은 모델별 한 호출에 함께 전파한다. coordinator의 예약과 deadline을 우회하거나 직접 `--worker`를 실행하지 않는다. 기존 ramp 및 2400/4800/9600 suite를 반복하지 않고 네 번째 격자·64-rank sweep을 실행하지 않는다.

matching NPZ 원본 source_vectors 전체, direct cutoff와 internal counter를 보존하고 초기 heat는 0, 이후 source는 없다. source/bath, atomic model, CCC markers/energy axis, cutoff, Coulomb prescription, precision, quadrature, 코드·허용값·budget을 바꾸지 않는다. 실패한 run을 삭제/덮어쓰기하지 않는다. 변경이 필요하면 첫 실패와 정확한 원인, bounded amendment 요청을 반환한다.

## 5. 반환, 기존 백업, 다음 독립 심사

성공·비영 exit·timeout·HOLD_BEFORE_BUILD를 포함한 모든 실제 run은 동일 run directory로 `--collect`한다. 아직 run을 시작하지 않은 admission HOLD에는 plan 및 외부 로컬 receipt를 보존한다. collect 자체가 실패하면 실제 stderr/exit/raw 산출물과 scoped blocker를 보존하고 물리 실행을 다시 하지 않는다.

Return ZIP의 `RETURN_MANIFEST.json` 모든 path·bytes·SHA256, 중복/CRC/안전경로를 검증한다. actual run, frozen source unit, pinned transitive dependencies, 원본 실패 evidence 및 사용한 operational adapters가 포함되는지 확인한다. `RESTORE_LAYOUT.json`, `README_RESTORE.txt`를 읽고 별도 새 위치에 검증 복원한다. actual return과 짧은 실행 요약을 기존 Drive folder `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI` 및 Dropbox `/BASS_DERIVATION_DOSSIERS_20260912`에 create-only 새 파일로 백업한다. 연결이 막히면 실제 로컬 ZIP identity 및 해당 백업의 scoped blocker만 보고한다. 기존 파일을 덮어쓰거나 다른 수신자에게 보내지 않는다. Git 전달은 additive 새 branch/draft PR, non-force ancestry를 유지한다. 각 실제 remote ID/rev/path/URL과 수행한 readback 범위를 외부 영수증에 기록한다.

최종 보고는 실제 command/cwd/UTC/exit/벽시계, runtime·threadpool·resource, build/pulse 예약과 실제 완료 증거, 두 모델 CDF·moments·reference residuals, 실패 및 미해결 항목, return ZIP path·bytes·SHA256, 실제 두 백업 식별자를 구분한다. 성공 exit만으로 과학 PASS를 발행하지 않는다. actual numerical return에 대한 **다음 독립 Astra 심사**가 필요하다.

CDF, ramp ancestry age, finite-window clipped moments, infinite frozen-operator moments는 서로 다른 양이다. infinite moments는 고정 연산자의 수학적 연장에 조건부이며 우주론적 장기 이력으로 승격하지 않는다. 동일 9600 pulse는 pulse mesh convergence, production 승인, PHYS02_DELAY 전체 해결, CCC identity 해결, NCP64 scaling을 뜻하지 않는다.

기존 gates `PHYS02_DELAY OPEN`, `production_history HOLD`, `atomic_G02 UNRESOLVED`, `b_grid NO_GO`, `all_bound OPEN`, `R17B2B NO_CERTIFIED_SOURCE_SHARPENING`, `CCC SOURCE_IDENTITY_UNRESOLVED`를 유지한다.
