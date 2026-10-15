# Codex handoff: BASS_CR_C20_ORIGINAL_RECOVERY → C21 same-clock source/HHe coupling

다음 지시를 현재 사용자 권한으로 진행하라. 이 문서는 `2026-10-16 KST`의 ChatGPT 비동기 실행이 아닌 **즉시 실행/재개 계약**이다. 질문이나 계획 작성만으로 종료하지 말고 읽기→원본 보존→검산→게시/백업→가장 짧은 다음 과학 계산까지 이어서 수행하라. 오너 저장소를 무단으로 변경하지 말고 실험·branch를 분리하라.

## 0. 상황·권위

- 최우선: `bass_cr` 원래 Ubuntu worktree `/home/cosmosapjw/chat_research/bass_cr_c20_20261015`, branch `chat/cr-c20-real-verner-cohort-20261015`, C19 기반 `e91ffe368c4e6db64c4b6c5962566302a33402b6`, 당시 **untracked** `research/cr_c20_verner_cohorts_20261015/`. 작업 후 파일 내용이 바뀌었을 수 있으므로 지금까지의 로컬 commit·변경 여부를 우선 기록하라.
- 이미 게시된 직접 부모: [`bass_cr` PR #72](https://github.com/cosmosapjw-quantum/bass_cr/pull/72), C19 원본 Rust + H/He microphysical RHS (C19 science commit `9305b2b177697c31fceb3f90c86e4711312596bd`, delivery commit `e91ffe368c4e6db64c4b6c5962566302a33402b6`). **이것을 C20 완료로 치환하지 말 것**.
- 원본 `rei_bianchi` frozen C20 source/checkpoint: `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`, 사용자 PC `/home/cosmosapjw/Dropbox/bianchi/rei_bianchi`; 원래 owner files pin은 C18 `OWNER_LOCK.json`. C20 source authoritative file 51개가 NCP stage002에 존재했던 사실이 이전 실행에서 검증됨.
- NCP host `${NCP_HOST}`, 64 vCPU / 약 125 GiB RAM, root SSH 공개키 인증 사용. 로컬 PC에는 `~/.ssh/ncp_key` (path only, do not expose key contents)가 설정되어 있었음. **키 내용을 출력·게시하지 말 것**. 실제 hostname/resource/affinity는 새로 확인.
- Rust NCP 설치: non-login 명령에서는 PATH에 없을 수 있으므로 `export PATH=/root/.cargo/bin:$PATH`; 과거 `rustc 1.99.0`.
- NCP 원래 최신 과학 실행 디렉터리: `/root/BASS_CR_C20_20261015_003/` (`c20_native.rs`, `c20_native`, `hpc_sweep.py`, `sweep_pass.json`). 원본 owner Cargo + cfg/checkpoint 참조 경로 `/root/BASS_CR_C20_20261015_002/`, `ZERO/{config.cfg,checkpoint.txt}`, `target/release/librei_microphysics.rlib`.
- 과거 C20 NCP science source SHA256: `13b6bc6fd3279d6b90f95baccf7bae20bbca838ee1eb83583c22071411c64de0` (`c20_native.rs`). 과거 NCP 전체 raw JSON SHA256: `7c1a39fd02294623f93c4c95da15827edae4644cb455cf114c85f9ed0cc3dc19` (`sweep_pass.json`). C20 과거 NCP 20/20 PASS, CPU40..47 8 threads of independent native tasks, 18.943053234s. 그전 raw 실패 20/20(`sweep_attempt1_failed_path`), 누적 오차로 실패한 19/20(`sweep_attempt2`), 보상 합산 후 최종 20/20 성공은 서로 다른 상태임.
- 이번 ChatGPT 환경은 Desktop Commander 월간 도구 quota로 원격 로컬 PC 실행이 **BLOCKED**. 제공된 복구 ZIP의 `src/c20_native_fallback.rs`는 이전 대화의 과학적 알고리즘을 재구성한 **비권위 fallback**이다. 실제 원본과 BYTE_IDENTITY를 절대 주장하지 말고 원본이 접근 가능하면 fallback을 덮어쓰지 말 것.
- 이 과제에서 **공개하지 말 것:** SSH 비밀키, API 토큰, 기존 private DB, 임의의 내부 전체 dump. 외부 저장소의 공개 가능 과학 코드는 원래 repo 정책을 준수하라.

## 1. FIRST: RUNTIME INTERRUPTION / recovery inventory, non-destructive

워크스테이션의 원래 C20 worktree를 읽을 수 있다면 먼저 아래 명령을 실행하고 stdout을 파일로 남겨라. `git clean`, 강제 checkout/reset, 기존 파일 overwrite, 현재 다른 사용자의 job kill은 금지한다.

```bash
set -euo pipefail
W=/home/cosmosapjw/chat_research/bass_cr_c20_20261015
P="$W/research/cr_c20_verner_cohorts_20261015"
[ -d "$W/.git" ] || git -C "$W" rev-parse --show-toplevel
mkdir -p "$W/../BASS_CR_C20_RECOVERY_20261016"
OUT="$W/../BASS_CR_C20_RECOVERY_20261016"
{ date -Is; hostname; git -C "$W" status --porcelain=v1 -b; git -C "$W" rev-parse HEAD;
  find "$P" -type f -not -path '*/__pycache__/*' -printf '%P\t%s bytes\t%TY-%Tm-%TdT%TH:%TM:%TS\n' | sort;
  find "$P" -type f -not -path '*/__pycache__/*' -print0 |sort -z | xargs -0 sha256sum;
} > "$OUT/WORKTREE_INVENTORY.txt"
```

1. 이때 `c20_native.rs`가 원래 NCP hash와 같은지 확인하고 다르면 **새 identity**로 보존한다. 수정본이 원래 파일보다 최신일 수 있다. 차이를 근거 없이 되돌리지 말 것.
2. Ubuntu 원본 worktree source/test/result 1개라도 있으면 create-only snapshot을 먼저 생성, 파일 목록·SHA256 manifest와 함께 보존한다.
3. NCP SSH 가능하면 `ssh -i ~/.ssh/ncp_key -o BatchMode=yes root@${NCP_HOST} 'export PATH=/root/.cargo/bin:$PATH; hostname;rustc --version;nproc;free -h;ps -eo pid,pcpu,rss,args --sort=-pcpu | head'`로 현재 상태를 확인한다. SSH 실패는 인증/네트워크 BLOCKER로 남기고 이후 로컬/게시 가능 작업부터 처리한다.
4. NCP에서 원본 보존이 가능하면 **먼저 `sha256sum` 및 tar create-only**. 과거 20사례 전체 `sweep_pass.json`의 bytes가 위 digest와 일치하는지 확인하고, 과거 컴파일 성공만으로 현재 case를 다시 실행했다고 주장하지 말라.

## 2. C20 과학 검증과 게시

- C20은 FLRW **고정 H/He 기체** source-age photon transport with actual Verner fits / original MD14 source. `q=a_birth E_birth`, `E=q/a`, `lambda_j=c nH(a)f_j sigma_j(E)`; `n_H∝a^-3`. Origin native AXBI 8 ray ×49 current energy stock, 48 source bins. Fit cutoffs 13.60/24.59/54.42 eV와 ionization binding 13.598434599702/24.587389011/54.41776 eV는 구분.
- Stepping: unabsorbed exp(-λ∆t), species competing risk, midpoint physical photoheat, absorbed+survived redshift work. Source birth quadrature GL2 positive, proper time GL4, separate optical threshold crossing at `log(q/E_fit)`. Kahan compensated accumulators, stable `-expm1` 사용. C20 종료 시 `N, U, A_HI, A_HeI, A_HeII, Q_heat, W_redshift` 정합성을 확인.
- 검증 우선순위: 재실행 전에 기존 원시 결과 및 tests 확인. 신규 source 변경이면 정확한 변경 영향을 받는 테스트만 다시 수행. `python3 -m pytest -q -p no:cacheprovider "$P/tests"` 후 실제 적절한 `PYTHONPATH`와 dependencies를 설정하라. 로컬 원래 10 tests PASS는 과거 관측이므로 재실행 여부를 구분.
- NCP raw 20건이 존재하면 `pass_count=20`, resource CPU40..47의 역사적인 기록 및 아카이브 checksum 대조. **현재 CPU40..47이 자유롭다고 가정하지 말고** 활성 REI_MICROPHYSICS/PR150 HPC 작업과 충돌하지 않는 CPU affinity와 총 메모리 한도를 확인해 배치하라.
- 원본 `C20` 성과: 이번 전달 아카이브 `evidence/NCP_STDOUT_EXTRACT.json`의 18개 HeII 숫자와 `sweep_pass.json` 각 행의 동일한 필드를 비교하라. 개별 key, 단위, 시각, source identity가 다르면 즉시 진단. 전사 JSON은 raw full bundle이 아니라는 표시를 보존.
- **실제 원본**  C20 source/tests/JSON/log/plots + 관련 pinned original Rust source/checkpoint/manifest를 `BASS_CR_C20_..._SOURCE.tar.gz` 및 `..._RAW.tar.gz` 같은 두 archive로 보존. SHA256 full manifest, compressed archive CRC/readback, relocated extracted tests 가능하면 테스트. Archive 내 private credential 제외.
- 그다음 GitHub에서 `git ls-remote origin 'refs/heads/chat/cr-c20-real-verner-cohort-20261015'` 확인 후, 실제 로컬 branch가 아직 미게시이면 원래 커밋 부모 위에 추가하거나 명확한 신규 branch를 사용해 commit/push. **기존 HEAD/PR를 강제로 덮어쓰지 말라.** C19 PR #72를 기준으로 Draft PR을 생성하고 현재 commit SHA / 비교된 원본 identity 기록.
- 업로드는 기존 설정 `rclone`의 `dbx:`와 `gdrv:` 대상 `BASS_DERIVATION_DOSSIERS_20260912/bass_cr/`를 사용하며 `--immutable` 혹은 create-only distinct name. 로컬 압축파일과 두 remote의 실다운로드 SHA256/size 일치로 backup 입증. 성공과 실패를 분리 기록. 코드 변경 없는 receipt commit은 과학 커밋과 구별한다.

## 3. NEXT SCIENCE: C21 동일 시각의 동적 H/He source/transport coupling

원본 C20과 백업이 닫히면 새로운 같은 물리 입력에서 한정된 연구를 실행하라. PR #150 HEAD는 마지막 확인 `efd7c4a1f64519185462def0c369d459a449ec47`이지만 **현 시점 실제 branch HEAD, 권위 문서, 나머지 병렬 PR을 다시 읽고 identity 갱신**해야 한다. 주 모델은 원래 `rei_bianchi` 생산 코드가 권위를 갖는다.

1. 오너 저장소는 읽기 전용. `bass_cr` 새 isolated branch/path에서 time-dependent `S_k(t), nH(t), σ(q_k/a(t)), x_i(t),w(t)`를 도입하라. `N_k`는 기존 C20의 진짜 birth-age, direction, q 구분을 유지한다. FLRW 방향 동등성은 1개 국소 reference에서만 사용하고 signed Bianchi에 바로 옮기지 말라. 원본 R/J 및 `dΩ`는 정확히 한 번만 적용.
2. 동일 `a0`, 동일 snapshot, 동일 source, 동일 proper `∆t`에서 source-free 및 no-absorption 단위 제한부터 시작하라. `C19`의 `IgmPhotoInput`는 per absorber/s, heat는 erg/(absorber·s), discrete event/H 단위 변환 및 nH proper density를 사용한다. `igm_point_rhs`에 h=0이면 owner geometry의 adiabatic gas `-2H w`를 정확히 한 번 적용한다. PR #150 현재 구현이 owner를 바꿨다면 기존 C19 방식을 강제로 이식하지 말 것.
3. 첫 구현은 positive reversible or implicit gas closure를 비교하되, original Rust owner chemistry rates와 exact photo event/energy ledgers를 공유하고 **source double-counting/absorber double-counting을 금지**. `N_{k}^{n+1}≥0`, `0≤x_HII≤1`, `x_HeII,x_HeIII≥0`, `x_HeII+x_HeIII≤1`를 line search/positive mapping으로 유지. Fail은 HOLD, clipping은 승인하지 말 것.
4. 광자+chemical binding+gas thermal+escaping radiation+cosmological work−external source−CMB reservoir 회계가 실제 owner와 호환되는지 확인. Born source changes photon *N and U*, threshold crossing selects correct species and heat. Fit thresholds and binding energies distinct.
5. 8/16/32 rays, energy 96/128/256, proper-time refinement을 먼저 1개 동일 입력에서 수행. NCP에서는 실제 free CPU/RAM에 맞춰 독립 parameter rays/cases만 병렬화하고 각 native job에 최소한의 OpenMP/BLAS threads를 부여. 원래 `PR150`의 실행 중인 full production campaign과 CPU를 중복 배정하지 말라.
6. 막히면 원인을 `THEORY / NUMERICAL / IMPLEMENTATION / INPUT_MISSING / RUNTIME / AUTHORIZATION`으로 분류하고 이미 완료된 부분을 무효화하지 말 것. 다음 가장 작은 실행 단위를 결정. 원래 FCI/BBN/HH 물리 범위로 drift하지 말 것.

선행 연구는 [`rei_bianchi` PR #152](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/152) original Verner angular threshold, [`PR #153`](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/153) source-free dynamic H/He positive map, [`PR #154`](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/154) conditional source-aware chemistry, [`PR #150`](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/150) canonical q/owner H/He production. These are *separate branches/scopes*; neither PR153 nor PR154 proves C21 full EoR.

## 4. 요구 반환

한 번의 작업 종료에서 다음을 모두 돌려줘:

- current `git` repo/branch/tree/commit SHA and exact original vs recovery package file identity; dirty/worktree changes before/after, actual latest owner PR150 SHA.
- C20 raw source + full NCP result 20행, unit tests and any reexecution command/runtime/exit/repro IDs. Missing data는 명시.
- 새 과학 결과의 수학·물리 가정·검증 등급, 불일치·실패 목록.
- C20 GitHub PR URL and exact published science commit, git remote readback; Dropbox + Google Drive backup paths, bytes, SHA256, two remote readbacks. 실패 시 정직한 한 곳 이상 백업과 실패 원인.
- C21 bounded first same-a comparison의 raw observable & source/clock/chemistry ledger, 또는 구체적 blocker+실행 가능한 다음 최소 조치.
- 재개를 위한 **하나의** concise machine-readable `NEXT_DAG.json`, readable Korean report, reusable Codex handoff only. 반복하는 정책/심사 메타루프 없이 실제 연구·증거를 우선하라.

필수 제한: Native subagent 기능이 없는 경우 SERIAL fallback; native agent receipt를 만들어내지 마라. 배포, 백업 성공, 과학 PASS는 현재 관측된 실행 증거만으로 선언. 원래 컴퓨터/원본 소스가 전혀 안 보이면 NCP stage003에서 우선 create-only tar/hash를 생성하고 소스 복구 우선으로 진행. PR150, rei_bianchi production baseline, immutable old checkpoints 및 역사적 NO_GO 판정은 변경하지 않는다.