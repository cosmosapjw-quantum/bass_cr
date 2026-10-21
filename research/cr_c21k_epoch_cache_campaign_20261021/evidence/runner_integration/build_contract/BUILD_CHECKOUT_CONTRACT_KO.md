# 기존 build·checkout 계약 추출

작성 범위: C21J 최종 인계문과 현재 byte 검증된 원 H/G/F helper를 읽어 추출했다. 실제 checkout, compile, native probe 및 native 실행은 수행하지 않았다. 현재 binary 또는 Rust 설치가 존재한다고 가정하지 않는다. 새 C21K 캠페인의 작업 선택·동시성은 별도 계약이다.

## 고정 checkout

| Lane | 실행 content | 문서·영수증 head |
|---|---|---|
| G | `e742d44f605c51c06615451774ba90af8f41f622` | `bf7f7abbe5d2b1844a8fb90bd7e48df23dc5a0c5` |
| H | `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8` | `0ec4c55102766c40c554ffc6141eb08fba741c79` |
| I | `fe6bbaec2de5032b938aed0713623b9618ba70e6` | `26ab505dac2bfcb0cfd3d049f22bc408f4c86241` |
| K | 새 실제 게시 content를 사용 | 이후 문서 commit과 구분 |

실제 기존 repo의 remote·dirty/worktree 상태를 읽고, commit object를 회수한 뒤 새 절대 경로에 `git -C "$C21K_REPOSITORY" worktree add --detach "$C21K_NEW_LANE_WORKTREE" "$C21K_FIXED_CONTENT"` 형식으로 준비한다. 기존 worktree를 reset/clean/stash하지 않는다. 이 명령은 기존 계약을 구현하는 행정 예시이며 여기서 실행하지 않았다. Shallow repository는 원 H→I ancestry와 content objects를 실제 확인할 수 있도록 필요한 원 history를 확보해야 한다.

I runner는 detached HEAD=fe6와 같은 root의 H/I를 강제한다. K runner는 detached HEAD=새 K content, 원 H→I→K ancestry 및 원 inherited committed bytes를 강제한다. G는 독립 input/native 계약이다. G published receipt의 schema는 `C21G_PUBLICATION_RECEIPT_V1`, status는 `PUBLISHED_OPEN_DRAFT_PR`이고 `unit` 필드는 없다. H/I receipt처럼 고쳐 쓰지 않는다.

F runtime10, G runtime4, H runtime8, I runtime3, H/I/G manifests와 baseline6을 원 bytes로 확보한다. 두 fixture의 baseline이 모두 필요하다. Live full checkout을 C21J replay용 source24만으로 대신하지 않는다. H/I PUBLISHED controls는 checkout 밖에 원 bytes로 둔다. 이 문서 옆 `controls/`에는 고정 문서 refs에서 실제 회수한 원 G/H/I receipt를 보존했다.

## Bridge: 유효한 원 build 우선 재사용

- 원 binary: `bass-cr-c21h-rust-bridge`, 4,888,736 bytes, SHA256 `717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30`.
- 원 성공 receipt: SHA256 `c846c35621dd9a0aa3c5bbfb90e94da0f022e934cf2ea1342270d61eda4b5190`.
- 현재 실제 bytes, executable bit, architecture/ELF loader와 필요한 shared libraries, receipt source identity를 확인한다. 원 receipt의 과거 binary path를 편집하지 않고 현재 path를 `--bridge`에 전달한다.
- 과거 성공 toolchain은 Rust1.94.1이었다. 원 helper는 version을 강제하지 않으며 `--cargo`/`--rustc`로 받은 현재 실제 executable의 version을 기록한다. 현재 toolchain을 관측하고 선택해야 한다.

원 helper 파일명은 `rust_bridge/build_bridge.sh`다. 새 build가 실제 필요한 경우 원 호출은 다음과 같다.

```bash
taskset -c "$CPU" bash "$H/rust_bridge/build_bridge.sh" \
  --cargo "$CARGO" --rustc "$RUSTC" --target-dir "$BRIDGE_BUILD"
```

`BRIDGE_BUILD`는 아직 없는 절대 경로다. Locked dependencies의 현재 cache가 확인된 경우에만 `--offline`을 추가한다. 내부 명령은 `cargo build --locked --release --jobs 1 --manifest-path "$H/rust_bridge/Cargo.toml" --target-dir "$BRIDGE_BUILD"`이며 `RUSTC`, `CARGO_BUILD_JOBS=1`, `CARGO_INCREMENTAL=0`, `RAYON_NUM_THREADS=1`을 설정한다. 원 `Cargo.lock` SHA256은 `d30f7f6437b7704f845ba85f8206c94810fbd4ec1a48db9cba06b7b77604c892`, VigilODE commit은 `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, Diffsol은 `0.17.1`이다.

출력: `rustc.version.txt`, `cargo.version.txt`, `SOURCE_BEFORE.json`, `build.stdout`, `build.stderr`, `BUILD_RECEIPT.json`, 성공 시 `release/bass-cr-c21h-rust-bridge`. Receipt schema는 `C21H_RUST_BUILD_V1`이며 exit_code0, source_files_unchanged=true, binary hash와 runtime manifest의 Cargo.toml/lock/main.rs records 일치를 확인한다. Compile budget은 native job300초와 별도다. 원 첫 timeout300초/exit124와 뒤 Rust1.94.1 성공421초 기록을 지우거나 재작성하지 않는다.

## Native owner build 계약

원 owner는 `cosmosapjw-quantum/rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`다. 우선 복구할 known binary는 5,003,448 bytes, SHA256 `1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`이다. 현재 파일·build provenance·host compatibility를 확인한다. PR87 archive에 native binary가 있다고 가정하지 않는다.

원 helper 호출은 `bash "$F/build_native.sh" "$NATIVE_NEW_BUILD" ["$EXISTING_OWNER_GIT_REPOSITORY"]`다. Optional owner repository가 없으면 별도 bare repo에 정확한 owner commit만 fetch하고, dirty working files 대신 `git archive`한 원 commit을 사용한다. 내부 build는 다음과 같다.

```bash
export CARGO_TARGET_DIR="$BUILD/target"
export CARGO_BUILD_JOBS=2
cargo build --offline --locked --release \
  --manifest-path "$BUILD/owner/rust/rei_microphysics/Cargo.toml" --lib
export C21E_OWNER_SHA=6ea2b1b4b3875c9163cafc45efe720afded43fc4
rustc --edition=2021 -O "$F/native/native_point.rs" \
  --extern rei_microphysics="$BUILD/target/release/librei_microphysics.rlib" \
  -L dependency="$BUILD/target/release/deps" -o "$BUILD/native_point"
```

이는 원 helper의 핵심 build 명령 발췌다. 실제 helper는 toolchain/명령 stdout·stderr를 파일에 보존하고 wrapper test binary도 컴파일하여 `--test-threads=1`로 실행한다. Helper를 대신 위 발췌만 실행해 provenance 파일을 빠뜨리지 않는다. Helper는 `$HOME/.cargo/bin`을 PATH 앞에 추가하므로 실제 선택될 cargo/rustc와 Rust1.94.1 선택 방식을 확인해야 한다. CPU 한 개 taskset은 내부 cargo child 수2를1로 바꾸지 않는다.

G native authority가 요구하는 파일: `native_point`, `owner_commit.txt`, `build_exit.txt`의 `exit_code=0`, `input_sha256.txt`, `owner_source.tar`, 고정 `native/native_point.rs`. Native source export는 `owner/`, toolchain은 `toolchain.txt`, Cargo/Rust/test logs는 build root에 남긴다. 이 원 native helper는 JSON BUILD_RECEIPT를 생성하지 않는다. 그 JSON receipt는 H bridge build와 구분한다.

G의 일반 admission은 `RECORDED_PINNED_OWNER_BUILD`를 지원한다. 그러나 원 C21J `run_exact_once.sh` 선택행 wrapper는 known native SHA를 강제하며 다른 새 build SHA를 자동으로 허용하지 않는다. 새 K 캠페인의 별도 build 선택·실행 신원은 새 계약에서 명시해야 한다. 동일 source/toolchain이라는 이유만으로 새 binary의 SHA가 같다고 추정하지 않는다.

CPU55 보호, actual resource admission, 원 실패/receipt 보존, 자동 retry 금지와 global_error_bound=null은 유지한다. 본 추출은 새 native 코드·helper 수정 또는 실제 build 실행이 아니다.
