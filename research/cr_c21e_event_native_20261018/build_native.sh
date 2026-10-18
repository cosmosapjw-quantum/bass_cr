#!/usr/bin/env bash
# Immutable-source build only. Never edits an owner checkout or global settings.
set -euo pipefail
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
OWNER=6ea2b1b4b3875c9163cafc45efe720afded43fc4
REPO_URL=https://github.com/cosmosapjw-quantum/rei_bianchi.git
if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "usage: bash build_native.sh NEW_BUILD_DIRECTORY [EXISTING_OWNER_GIT_REPOSITORY]" >&2;exit 2
fi
BUILD=$(realpath -m "$1")
if [ -e "$BUILD" ]; then echo 'Refusing existing build directory' >&2;exit 2;fi
export PATH="$HOME/.cargo/bin:$PATH"
command -v cargo >/dev/null;command -v rustc >/dev/null;command -v git >/dev/null
mkdir -p "$BUILD"
trap 'code=$?; printf "exit_code=%s\n" "$code" > "$BUILD/build_exit.txt"' EXIT
{
  rustc --version;cargo --version;git --version;uname -a
} > "$BUILD/toolchain.txt"
if [ "$#" -eq 2 ]; then
  SRC=$(realpath "$2")
  git -C "$SRC" cat-file -e "$OWNER^{commit}"
else
  SRC="$BUILD/source.git"
  git init --bare "$SRC" > "$BUILD/git_init.log"
  git -C "$SRC" remote add origin "$REPO_URL"
  git -C "$SRC" fetch --depth=1 origin "$OWNER" > "$BUILD/git_fetch.log" 2>&1
fi
# Export the COMMIT, not dirty working files. Preserve include_str! relative paths.
git -C "$SRC" archive --format=tar "$OWNER" > "$BUILD/owner_source.tar"
mkdir "$BUILD/owner"
tar -xf "$BUILD/owner_source.tar" -C "$BUILD/owner"
printf '%s\n' "$OWNER" > "$BUILD/owner_commit.txt"
sha256sum "$BUILD/owner_source.tar" "$HERE/native/native_point.rs" > "$BUILD/input_sha256.txt"
export CARGO_TARGET_DIR="$BUILD/target"
export CARGO_BUILD_JOBS=2
cargo build --offline --locked --release --manifest-path "$BUILD/owner/rust/rei_microphysics/Cargo.toml" --lib > "$BUILD/cargo_stdout.log" 2> "$BUILD/cargo_stderr.log"
export C21E_OWNER_SHA="$OWNER"
rustc --edition=2021 -O "$HERE/native/native_point.rs" \
 --extern rei_microphysics="$BUILD/target/release/librei_microphysics.rlib" \
 -L dependency="$BUILD/target/release/deps" -o "$BUILD/native_point" \
 > "$BUILD/rustc_stdout.log" 2> "$BUILD/rustc_stderr.log"
rustc --edition=2021 --test "$HERE/native/native_point.rs" \
 --extern rei_microphysics="$BUILD/target/release/librei_microphysics.rlib" \
 -L dependency="$BUILD/target/release/deps" -o "$BUILD/native_point_tests" \
 > "$BUILD/test_compile_stdout.log" 2> "$BUILD/test_compile_stderr.log"
"$BUILD/native_point_tests" --test-threads=1 > "$BUILD/native_test_stdout.log" 2> "$BUILD/native_test_stderr.log"
sha256sum "$BUILD/native_point" "$BUILD/native_point_tests" >> "$BUILD/input_sha256.txt"
printf 'NATIVE_BUILD_READY %s\n' "$BUILD/native_point"
