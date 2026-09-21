# BASS CR R3M11 -> R3M12 local continuation

여기는 BASS **CR** numerical-source 스레드다. 사용자는 repo/백업 쓰기를 승인했다.
대상 repo는 `https://github.com/cosmosapjw-quantum/bass_cr`이며 이번 입력 정본은
`77237751bdd2aed5934bf7fc3bc626d631a09058`이다.

이번 턴의 목적은 원 저자 code 회수를 기다리지 않고, 실제 반환된 100 keV/u, b=2 a0
TDL/AOCC NO_GO 원인을 제어변수별로 분리하는 것이다. Nichols 구현 재현이라고 부르지 않는다.

## 0. 전달물과 적용

먼저 이 패키지의 SHA256SUMS를 검증하고 docs/r3m11/REPORT_KO.md 및
원 repo의 results/R3M10_LOCAL_RETURN_20260921/README_KO.md와 report/DECISION.json을 읽는다.
과거 루트 R3M10_STATUS.json을 현재 state로 읽지 않는다.

이번 ChatGPT 세션에서는 remote writer action 부재와 direct Git DNS 실패로
push/Google Drive/Dropbox upload가 실행되지 않았다. 완료됐다고 가정하지 말 것.

기존 bass_cr clone과 Python scientific environment를 사용하되 원 worktree의 변경을 버리지 않는다.
전달 패키지 최상위 apply_and_push.py는 새 worktree에 addition-only patch를 적용하고 테스트한다.
기존 인증과 Git user identity만 사용하고 credential 내용을 출력하지 않는다.

```bash
python /path/to/packet/apply_and_push.py \
  --repo /path/to/existing/bass_cr \
  --worktree /path/to/new/bass_cr-r3m11 \
  --branch cr/r3m11-fixed-cap-gram-20260921 \
  --receipt /path/to/new/GIT_PUBLICATION_RECEIPT.json --push
```

입력 origin/main이 바뀌었으면 이 script는 중지한다. 최신 HEAD와 pinned base의
scientific/code diff를 검토한 다음 별도 branch에서 명시적으로 rebase해야 한다.
main에 force push/자동 merge하지 않는다. 기존 remote branch도 덮어쓰지 않는다.
Git user identity가 없거나 인증이 막혔으면 환경 blocker로 기록하고 scientific work는 가능한 범위에서 계속한다.

설치가 필요한 경우 새 venv에 기존 requirements와 `pip install -e .`를 실행하고 freeze를 보존한다.
CuPy는 **실제 로컬 CUDA에 맞는 기존 설치**를 우선한다. 이미 실행됐던 cuFFT loader repair
및 CPU/GPU parity receipt를 참고하되 현 runtime에서도 검증한다. CUDA를 무작정 교체하지 않는다.

## 1. 가장 먼저: 기존 상태를 재전파 없이 후처리

원 930,236,215-byte archive는 사용자 local의
`/mnt/sn850x2t/R3M11_LOCAL_SINGLE_B_RESULTS_20260921.tar.gz`에 있었고 동일 repo release에 있다.
로컬 파일부터 확인한다. archive SHA256:
`5af567f4be6f5dfd1dc9e7b42f24409a775de7f9bf776c3485303e6c306b9506`.
release tag: `r3m11-single-b-20260921`.

source 권위는 repo provenance/RELEASE_ASSETS.json과 원 archive manifest다.
원 archive를 검증하고 새 디렉터리에 해제한다. 실행 결과가 존재한다고 추정하지 말고 파일/해시를 확인한다.

```bash
cd /path/to/new/bass_cr-r3m11
python -m cr_repro.r3m11_jobs audit-return \
  --repo . --return-root /path/to/extracted/return \
  --out /path/to/new/R3M11_POSTPROCESS
```

이 명령은 baseline과 dx03125 두 개를 기본 대상으로 사용하며 state.npy의 source-owned
SHA/size, checkpoint completeness, result/config 일치를 검사한다. 새 sidecar만 쓴다.
`--names tdl_baseline_retry tdl_dt025 tdl_dx03125 tdl_plane25 tdl_z75 tdl_boxwide`로 확장 가능하다.
원 state 또는 result를 수정하지 않는다. 추가 nmax는 별도 sidecar/새 경로로 계산한다.

반드시 비교할 값: old raw overlap sum, P_span_nmax, P_span_by_nmax, G-I,
Gram condition/eigenvalues, finite-grid orbital norms, gap identity residual, region-minus-span.
`eps_complement_inside`는 higher bound/target states도 포함하며 **continuum이 아니다**.
결과를 physical all-bound cross section으로 승격하지 않는다.

## 2. 검증된 새 제어 코드의 새 baseline

기존 cr_repro/tdl.py는 역사적 그대로이며 cr_repro/r3m11.py가 opt-in 새 lane이다.
기존 mask는 dt마다 같은 M을 곱하므로 dt를 반으로 줄이면 유효 CAP 강도도 바뀐다.
새 lane은 M_ref^(dt/dt_ref)를 대칭 potential halves에 배치한다.
이는 기존 결과의 재해석이 아니라 새로운 propagation이므로 새 baseline을 계산해야 한다.
옛 checkpoint에서 새 dynamics를 resume하지 않는다.

```bash
python -m cr_repro.r3m11_jobs generate --out /path/to/new/R3M11_MATRIX
python -m cr_repro.r3m11_jobs run-one \
  --matrix /path/to/new/R3M11_MATRIX --name tdl_cap_base \
  --out /path/to/new/R3M11_RUNS/tdl_cap_base --max-steps 128
```

동일 command를 다시 호출하면 검증된 completed chunk에서 이어진다.
완전히 마치려면 --max-steps를 생략한다. 모든 attempt는 stdout/stderr/config/environment/receipt를
별도 폴더에 남긴다. source/state/meta hash가 틀리면 정상 checkpoint라고 강제 승인하지 않는다.
interrupted inconsistent checkpoint는 보존하고 새 output directory로 다시 시작한다.

선택 순서: tdl_cap_base -> tdl_dt025 -> 필요시 tdl_dt0125.
그 다음 tdl_imag025(준비 총시간 동일), tdl_imag025_long(준비시간만 연장).
초기 target stationary residual과 E+0.5를 별도로 검사한다.
TDL dx03125, dx025, 필요시 dx020은 같은 CAP/초기 parameter에서 비교한다.
초기상태 설정을 바꿨으면 해당 refined initial state에서 공간 비교 기준도 일관되게 다시 만든다.
설정 생성은 14개이나 자동 전체 실행은 금지한다. 결과를 읽으며 한 job씩 진행한다.

목표가 source 일치가 아니라 수치 안정성이라는 점을 유지한다.
Coulomb potential을 reference sigma에 맞추어 보정하거나 grid phase를 유리한 값으로 선택하지 않는다.
초기 E error가 capture error와 같다고 추정하지 않는다.

## 3. AOCC는 기존 one-electron 구현 그대로, 변수만 분리

`aocc_base`, `aocc_dt025`, `aocc_radial_only`, `aocc_exponent_only`,
필요시 `aocc_window_only`를 run-one으로 실행한다. --max-steps는 AOCC에 지원되지 않는다.
기존 baseline vs large는 radial counts와 s-exponent upper bound를 함께 바꿨다.
새 matrix는 이를 분리한다. vendor/two-electron W1R physics는 수정하지 않는다.

metric norm만으로 generator의 anti-Hermitian defect나 basis convergence를 승인하지 않는다.
s+p AOCC와 n<=3 TDL(d 포함)은 동일한 bound truncation이 아니다.
동일 channel의 비교를 먼저 하며, state resolution이 없는 기존 AOCC aggregate를 같은 n<=3 total로 부르지 않는다.
d를 추가해야 하는 다음 단계에서는 s/d와 d/d cross overlap을 포함한 전체 atomic generalized
eigensystem이 필요하다. 단순히 기존 independent s/p groups에 Cartesian d group을 붙이지 않는다.

## 4. 판정·보존

현재 global b-grid NO_GO를 유지한다. parent의 1% screening을 사후 완화하지 않는다.
한 b에서 안정적이어도 full b support와 tail이 닫힌 것이 아니다.
50/225 keV/u, integrated sigma, physical gas rate, chemical source evolution, production central,
P0 covariance, source-owned continuous D102563 승격은 하지 않는다.

두 solver는 독립적으로 계산한다. 서로 같은 숫자가 나오는 방향으로 보정하지 않는다.
H8에서 가져온 BDSCx/PCHIP 또는 posthoc 8% margin은 calibration target/physical UQ가 아니다.

첫 local session stop: archived-state Gram table + fixed-CAP dt table + initial-state/spatial table
+ 분리된 AOCC radial/exponent/dt table 또는 정확한 미수행/blocker 상태를 반환한다.
`R3M12_LOCAL_CONTROLLED_SINGLE_B_RETURN`을 작성하되 NO_GO/진행조건과검증하지 않은 항목을 분리한다.

## 5. Git와 실제 dual backup

code/docs/tests 변경은 전용 branch에 commit/push하고 remote SHA를 다시 조회한다.
큰 state.npy를 Git history에 직접 넣지 않는다. 완전한 output archive는 명시적인 archive/release
또는 dual cloud storage로 보존한다. 기존 release/실패 로그는 변경하지 않는다.

현재 이미 인증된 rclone remotes를 찾되 secrets를 출력하지 않는다. 두 provider가 준비돼 있으면:

```bash
python scripts/r3m11_dual_backup.py --file /path/to/return.tar.gz \
  --drive-remote ACTUAL_DRIVE_REMOTE: --dropbox-remote ACTUAL_DROPBOX_REMOTE: \
  --receipt /path/to/new/DUAL_BACKUP_RECEIPT.json
```

실제 remote 이름은 로컬 설정에서 확인한다. 이 script는 remote를 새로 만들거나
credentials를 요구하지 않는다. local synced-folder 복사만으로 online backup이라 부르지 않는다.
양 provider raw readback SHA/size가 일치해야 complete다. 권한/연결이 없으면 BACKUP_PENDING
상태로 실패를 보존하고, 성공한 한쪽만 완료했다고 보고한다.

반환 archive에는 config/code identity/environment, stdout/stderr/exitcode, checkpoint seal,
분류된 실패 ledger, 결과표, raw source SHA와 commit/remote SHA를 넣는다.
그 archive 자체의 해시와 업로드 결과를 적는 detached backup receipt는 archive 밖에 둔다.
이 CR 대화에 붙일 return prompt에는 발견한 실제 변화, numerical gate, 미수행 작업,
archive SHA/위치와 다음 최소 작업만 적는다. 전체 과거 대화를 다시 읽을 필요는 없다.
