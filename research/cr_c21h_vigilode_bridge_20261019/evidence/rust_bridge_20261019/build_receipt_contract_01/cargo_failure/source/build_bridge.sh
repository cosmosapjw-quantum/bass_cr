#!/usr/bin/env bash
# Build only this new bridge. An existing output directory is never reused.
set -euo pipefail
bridge_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
c21h_cargo=''
c21h_rustc=''
c21h_target=''
c21h_offline=0
while (($#)); do
  case "$1" in
    --cargo) c21h_cargo=${2:?missing Cargo path}; shift 2 ;;
    --rustc) c21h_rustc=${2:?missing rustc path}; shift 2 ;;
    --target-dir) c21h_target=${2:?missing new target directory}; shift 2 ;;
    --offline) c21h_offline=1; shift ;;
    *) echo 'usage: build_bridge.sh --cargo PATH --rustc PATH --target-dir NEW_ABSOLUTE_DIRECTORY [--offline]' >&2; exit 64 ;;
  esac
done
[[ -x "$c21h_cargo" && -x "$c21h_rustc" && "$c21h_target" = /* && ! -e "$c21h_target" ]] || {
  echo 'Cargo/rustc must be executable; target directory must be absolute and new.' >&2; exit 64;
}
[[ -f "$bridge_dir/Cargo.lock" ]] || { echo 'Cargo.lock must be delivered before a locked build.' >&2; exit 66; }
mkdir -- "$c21h_target"
"$c21h_rustc" --version --verbose > "$c21h_target/rustc.version.txt"
"$c21h_cargo" --version > "$c21h_target/cargo.version.txt"
python3 - "$bridge_dir" "$c21h_target" <<'PY'
from pathlib import Path
import hashlib,json,sys
source,target=map(Path,sys.argv[1:3])
files=['Cargo.toml','Cargo.lock','src/main.rs','build_bridge.sh']
def identity(path):
 data=path.read_bytes()
 return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
with (target/'SOURCE_BEFORE.json').open('x') as stream:
 json.dump({name:identity(source/name) for name in files},stream,indent=2)
 stream.write('\n')
PY
c21h_args=(build --locked --release --jobs 1 --manifest-path "$bridge_dir/Cargo.toml" --target-dir "$c21h_target")
if ((c21h_offline)); then c21h_args+=(--offline); fi
set +e
env RUSTC="$c21h_rustc" CARGO_BUILD_JOBS=1 CARGO_INCREMENTAL=0 RAYON_NUM_THREADS=1 \
  "$c21h_cargo" "${c21h_args[@]}" > "$c21h_target/build.stdout" 2> "$c21h_target/build.stderr"
c21h_exit=$?
python3 - "$bridge_dir" "$c21h_target" "$c21h_exit" "$c21h_offline" <<'PY'
from pathlib import Path
import hashlib,json,sys
source,target=map(Path,sys.argv[1:3]); code=int(sys.argv[3])
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def identity(path):
 data=path.read_bytes()
 return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
binary=target/'release'/'bass-cr-c21h-rust-bridge'
files=['Cargo.toml','Cargo.lock','src/main.rs','build_bridge.sh']
before=json.loads((target/'SOURCE_BEFORE.json').read_text())
after={name:identity(source/name) for name in files}
unchanged=before==after
effective=code if code else (0 if unchanged and binary.is_file() else 78)
receipt={'schema':'C21H_RUST_BUILD_V1','exit_code':effective,'cargo_exit_code':code,'offline':bool(int(sys.argv[4])),
 'vigilode_commit':'8a8bd409b1d96c7b7421f496d229e119fd3d284e','diffsol_version':'0.17.1',
 'sources':{name:after[name]['sha256'] for name in files},
 'source_files':{'rust_bridge/'+name:before[name] for name in ['Cargo.toml','Cargo.lock','src/main.rs']},
 'source_files_unchanged':unchanged,'sources_before':before,'sources_after':after,
 'build_failure_reason':None if effective==0 else ('source files changed during build' if not unchanged else ('cargo failed' if code else 'cargo returned no binary')),
 'rustc_version':(target/'rustc.version.txt').read_text(),
 'cargo_version':(target/'cargo.version.txt').read_text(),
 'stdout_sha256':sha(target/'build.stdout'),'stderr_sha256':sha(target/'build.stderr'),
 'binary':str(binary) if effective==0 else None,
 'binary_sha256':sha(binary) if effective==0 else None,
 'native_chemistry_executed':False,'c21h_campaign_executed':False}
with (target/'BUILD_RECEIPT.json').open('x') as f:
 json.dump(receipt,f,indent=2); f.write('\n')
print(json.dumps({'exit_code':effective,'receipt':str(target/'BUILD_RECEIPT.json'),'binary_sha256':receipt['binary_sha256']}))
raise SystemExit(effective)
PY
c21h_receipt_exit=$?
set -e
exit "$c21h_receipt_exit"
