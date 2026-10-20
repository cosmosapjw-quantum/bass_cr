# C21G/H/I 선택 native 실행 결과

## 결과 요약

고정 I 실행 콘텐츠 `fe6bbaec2de5032b938aed0713623b9618ba70e6`에서 Rust 1.94.1 locked bridge를 빌드하고, C21H common-IC 원본 solver base, C21I vectorized base 및 그 자체의 `fd_half` follow-up을 실제 native microphysics와 실행했다. Python/Cargo runtime source는 모두 게시 manifest와 바이트 단위로 일치했고 호환성 수정은 필요하지 않아 source diff는 없다.

intake 당시 공개 H receipt는 `native_physics_run_this_publication=false`였고 C21H DAG도 native `NOT_RUN`이었다. 검색한 현재 NCP 로컬 결과와 확인 가능한 프로젝트 Drive/Dropbox 폴더에도 matching terminal H base가 없어, 과거 smoke를 재사용하지 않고 I의 선행조건을 만족하는 H base 한 행만 새로 실행했다. 실행된 H base를 I runner에 같은 fixed bridge와 native owner identity로 연결했다.

| 행 | 상태 | wall (s) | peak RSS (KiB) | accepted steps | native/original-RHS calls | 결과 |
|---|---:|---:|---:|---:|---:|---|
| H `common_ic / vigilode-rodas5p / base` | COMPLETE | 1.212 | 85,560 | 36 | 823 | native original nonphoto RHS + manufactured common-IC source |
| I `common_ic / vigilode-rodas5p / vectorized / base` | COMPLETE | 1.432 | 85,812 | 36 | 823 | H endpoint와 binary64 값 동일 |
| I `common_ic / vigilode-rodas5p / vectorized / fd_half` | COMPLETE | 1.435 | 85,920 | 36 | 823 | 같은 I base를 부모로 사용 |

I base의 측정 job wall은 H base보다 약 18.1% 길었고 native call 수는 823으로 줄지 않았다. 이 한 행은 속도 향상을 지지하지 않으며 일반 성능 순위도 아니다. 조건부 FD half에서 최대 normalized gas endpoint 차이는 `2.03e-15`, 안정 photon count 차이는 `2.50e-18/H`, log-survivor 차이는 `1.94e-16`이었다. 이는 관측된 민감도이지 오차 상계가 아니다.

## 입력과 수치 검산

- C21G content: `e742d44f605c51c06615451774ba90af8f41f622`; manifest SHA256 `7b14b62a20714fc66216ebd9d446af1ed1a05de889447ec410158b52e5923fed`.
- C21H content: `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8`; manifest SHA256 `7d1e521aa78ffc1be2cac66d26863b2a542d67a7d856e8711e8b60f8252df6fb`.
- C21I content: `fe6bbaec2de5032b938aed0713623b9618ba70e6`; manifest SHA256 `f868b23a3188e959e60b79ffc8974ae399a28d63228a79b18c2da3c40f0cb9ec`.
- C21F baseline runtime is taken from the pinned I content; original native owner is `rei_bianchi@6ea2b1b4b3875c9163cafc45efe720afded43fc4`, binary SHA256 `1e7265185960cd91c3c589057b3e29d191d83bce95e59d803a399f9eb234ad40`.
- Rust bridge: VigilODE `8a8bd409b1d96c7b7421f496d229e119fd3d284e`, Diffsol `0.17.1`; successful bridge SHA256 `717c477cc3df7f7964faaaf11e9f50643ba59a0bde31cecdb62ed592a37dce30` (4,888,736 bytes). Full toolchain/binary identity is in `TOOLCHAIN_IDENTITY.json` and `build_success/BUILD_RECEIPT.json`.
- All three rows used the same fixture SHA256 `befb0c8a7a113ff0efccc450af05b1157592a8d91cc7e994cfdfd2768905cc65`, `rtol=2e-11`, alpha `2e-14`, max-step divisor 8, and one CPU affinity (62). H and I source/fixture/bridge/native identities are retained in each job receipt.
- Fixture is the explicit, manufactured C21F common-IC case: three-energy photon cohorts and opacity multiplier 0.001 with `FLRW_EXPLICIT_TEST_IC_NOT_CHECKPOINT`. Chemistry calls the pinned original native nonphoto provider; this is not the real MD14 native 12-cell source matrix.

H base independent recomputation: photon-number defect `+7.18e-18/H`, energy defect `−4.56e-16 eV/H`, species defects `[-7.46e-17, −9.33e-17, −4.92e-18]`. Maximum normalized C21G L0 endpoint difference is `7.80e-16`; direct temperature difference is `7.28e-12 K`. H/I endpoints and photon number/energy summaries are exactly binary64-equal in this fixture. `global_error_bound` remains `null`.

## Build 및 실패 보존

첫 locked bridge build는 source/API 오류 없이 300초 budget에서 dependency compile 도중 종료(outer timeout exit 124)했다. 그 partial target과 stdout/stderr identity는 `BUILD_TIMEOUT.json` 및 `build_attempt_01/`에 기록했다. 이 실패 폴더를 재사용하거나 덮지 않았다. 두 번째 새 target은 Rust 1.94.1, Cargo locked, release, jobs=1로 PASS했고 source checksum이 before/after 동일하다. 필요한 호환 수정은 없었다.

NCP에서 실행을 실제로 허용한 affinity는 CPU62였고 CPU55는 사용하지 않았다. H/I native job은 각각 300초 상한 이내에 2초 전후로 끝났으며 최대 RSS는 약 84MiB였다. 빌드 중 관측 compiler RSS는 약 1.1GiB까지였고 메모리 OOM은 없었다. 각 실행 `LIVE_INVENTORY.json`은 다른 공유 노드 process argv를 포함하여 비공개 archive에 원본 그대로 보존하고, 공개 GitHub copy에서는 해당 세 파일만 제외한다. 공개 job receipts 및 그 안의 원 SHA 목록은 변형하지 않는다.

## 범위와 다음 DAG

이번에는 C21G의 독립 8-reference ladder, H의 나머지 3 base/조건부 FD, I의 `vectorized_exact` 또는 다른 fixture를 실행하지 않았다. H native base와 I의 첫 pilot/조건부 FD만 닫았다. 이는 native callback 최적화가 유용한지를 판별하는 scoped row이며 full driver parity나 production accuracy 인증이 아니다.

`DAG_GHI_NATIVE.json`이 단계별 실행/미실행을 기록한다. 다음 선택 작업은 (a) 필요할 때만 C21G reference ladder를 별도 budget으로 열고, (b) 전체 H 행이 요구되는지 결정하며, (c) I 성능을 주장할 필요가 있으면 반복 matched timing을 계획하는 것이다. Full48/native MD14 source, source-age/spectral/angular convergence, Case B, signed Bianchi, full EoR, standalone full-driver parity는 독립 검증 전까지 HOLD다.
