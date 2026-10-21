# BASS_CR C21M — Codex용 NCP 선택 후속 실행 인계

작성 기준: 2026-10-21. **첫 독립 초기응력 pilot27은 완료됐다.** 여기서 NCP에 넘기는
98점은 새로운 해상도 보강 연구 단위이며 첫 pilot의 미완료분이 아니다.
NCP의 실제 접속·자원 관측·98점 적분은 이 인계 시점에 `NOT_RUN`이다.

## 1. 복사해서 전달할 지시문

```text
$physmath-research-loop를 사용해 cosmosapjw-quantum/bass_cr의 C21M을 이어서 수행해줘.
완료한 C21L81, C21M 신규26+재사용중심1, 외부 완료625/600+6/729의 ODE를 다시 실행하지 마.
과학 content 659c94312eb9c12ebb987de934459c12a63d67b0와 문서 head SELF_DOCUMENT_COMMIT_RESOLVE_FROM_FINAL_AUTHORITY_RECEIPT,
C21L 문서 head e954467132eef864a0fb86ba5de44f90f76b08e0, C21M PR https://github.com/cosmosapjw-quantum/bass_cr/pull/91를 먼저 확인해.
고정 REI source는 3b85dedce84d37b3e165da00685a8a984950aafe다.

시작 시 최신 Git refs·관련PR·외부 실행 반환·Drive/Dropbox/Library를 확인하고 새 결과의
source/input/solver/tolerance/build/runtime/raw/검증 범위를 대조해 수용해줘.
접근하지 못한 대화나 저장처는 UNAVAILABLE로 기록하고 전역 부재를 주장하지 마.

선택 후속으로 준비된 grid_ncp_refinement98.json만 새 run에서 실행해줘.
SHA256은 768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04다.
이 격자는 nested125에서 이미 완료한27 요청좌표를 제외한98점이다.
그 사이 새로 완료된 동일 입력이 있으면 먼저 수용하고 중복 ODE를 피해야 한다.

아래 SSH·독립checkout·ncp_run.sh 명령을 사용해 실제 host를 확인하고 가용자원 안에서
실행해줘. CPU55와 기존 공유lease를 보호하고 coordinator비용을 포함해줘.
worker62는 요청상한이지 보장된사용수나성능주장이 아니다. 다른owner의 process/output을
변경하거나 종료하지 말고 신규dispatch만 부하에맞춰 조절해줘.
원40성분 RHS, FP64, z20→4, DOP853 n101/rtol3e-11/atol3e-13을 유지해줘.

98점이 완료되면 기존26+새98+원C21L중심1을 analyze_campaign.py로 결합해125점
CSV/NPZ/그림과 검증영수증을 생성해줘. 기존raw/source를 수정하지 마.
각단계 EXECUTION | PUBLICATION | BACKUP | DAG를 분리해 갱신하고 실제결과를
별도content/document commit과 새버전 백업으로 게시해줘. global_error_bound=null.
```

## 2. 권위 식별자와 백업

| 항목 | 고정 값 |
|---|---|
| BASS_CR repository | `https://github.com/cosmosapjw-quantum/bass_cr` |
| C21M 과학 content | `659c94312eb9c12ebb987de934459c12a63d67b0` |
| C21M 문서 head | `SELF_DOCUMENT_COMMIT_RESOLVE_FROM_FINAL_AUTHORITY_RECEIPT` |
| C21M draft PR | `https://github.com/cosmosapjw-quantum/bass_cr/pull/91` |
| C21L 성분 분리 content | `17244259d25f793a25e0874443a28806e7c31d17` |
| C21L 문서 head | `e954467132eef864a0fb86ba5de44f90f76b08e0` |
| C21L 원 pilot content | `60a3f1cb0d8f0875820d18c0d10c448d480334c4` |
| REI 고정 물리 source | `3b85dedce84d37b3e165da00685a8a984950aafe` |
| 최종 배송 ZIP | `BASS_CR_C21LM_RESEARCH_DELIVERY_20261021T082802Z.zip` |
| ZIP SHA256 | `e0592be2859b7db606ec5a2ca008015c5ab02a3b2ff09fdd97fafe209cfe167a` |
| ZIP bytes | `17539759` |
| Drive object ID | `UNKNOWN_NO_ACK — 객체 ID 미수신` |
| Dropbox object ID | `id:BSpOijBcT10AAAAAAD_fqQ` |
| Library object ID | `libfile_9ec015516fd48191bf149640f43bea7a` |

Provider의 성공 응답과 실제 다운로드 후 byte 재검증은 다른 단계다. 최종 권위
영수증의 provider별 상태를 읽고 수행한 단계만 보고한다. 위 object ID만으로
다운로드 후 SHA 일치까지 완료했다고 해석하지 않는다. 배송 ZIP을 복원하면
파일 크기와 SHA256, 내부 manifest의 각 파일 hash를 실제 bytes와 대조한다.
이전 배송본을 덮어쓰지 않는다.

## 3. 시작 시 수용해야 할 기존 결과

- C21L81: 원 z20→4, A=0 collisionless LRS trajectory를 그대로 보존했고 matter,
  photons, massless neutrinos 분리를 후처리했다. 독립 초기 matter/radiation 격자가 아니다.
- C21M27: (S_0=-0.012,0,0.012), (P_{m,0}=P_{r,0}=-0.0002,0,0.0002).
  새로운26점을 실제 적분했고 중심은 C21L `s04_p04` raw를 재사용했다.
  새 run identity는 `ff462f48e264b2032ec50018e9969a6eb1808c7a6fc2a60139b98efacb01c05a`다.
- REI PR198의 고정 결과 `b140170ce0c58159368b6b81be49ac35ca764851`: 기존625
  분해와 신규 matter600+mixed6. 같은 원 물리 source지만 reduced8-state·65시점이다.
  Half-contraction 좌표는 full 비교 시 sqrt(2)배한다. 현재 대화에서 외부606의
  전체 raw를 모두 다시 검증한 것으로 승격하지 않는다.
- REI213/BASS176의729와 REC116 axis 재사용은 C15 warm a=.1999→.2 source-on
  계열이다. 동일729의 게시 mirror/후처리를 중복 실행 수로 세지 않고 C21M
  collisionless long-window 정확도 근거로 옮기지 않는다.
- REC116의 축 재구성 방법은 실제 C21M27에서 사후 검산했다. 최종 채택 경로는
  `axis_response_diagnostic_results_v2/`다. Support15/held-out12×101 비교의
  `signed P_tot` 최대 절대잔차는 약 `2.5829708927e-9`이다. Solver 대체 승인은 없다.

최신 refs의 존재만으로 기존 계산의 source SHA를 변경하지 않는다. 새 외부 결과의
입력좌표가 NCP98에 포함되면 그 결과의 provenance와 실제 raw를 검증해 재사용을
우선한다. 필요하면 원98 입력을 보존한 채 별도 run ID의 미실행 subset manifest를
만들고 제외 이유를 기록한다.

## 4. 확인된 SSH 계약과 실제 NCP 상태

기존 `SHARED_OPERATIONS_KO.md`에 고정된 명령은 다음과 같다.

```bash
ssh -i /home/cosmosapjw/.ssh/ncp_key root@49.50.142.2 -p 22
```

이번 sandbox에는 `/usr/bin/ssh`가 있지만 위 key 파일이 없었다. 키 내용은 읽지
않았으며 remote 접속·자원 probe·적분을 실행했다고 기록하지 않았다. 키가 있는
정상 환경에서 명령을 실행한다. Credential을 다른 저장처로 복제하거나 추측하지 않는다.
명목64 logical CPUs/128 GB와 실제 affinity·quota·메모리·load는 구분한다.

## 5. 독립 checkout과 환경 준비

아래 명령은 NCP shell에서 실행한다. `C21M_WORK_ROOT`는 이 연구 소유의 새 작업
루트다. 이미 다른 작업이 사용하는 checkout은 바꾸지 않는다. `C21M_CONTENT_COMMIT`
에는 과학 content를 넣고, 문서 head로 solver source를 재해석하지 않는다.

```bash
set -euo pipefail
set -o noclobber

export C21M_CONTENT_COMMIT='659c94312eb9c12ebb987de934459c12a63d67b0'
export C21M_WORK_ROOT="${C21M_WORK_ROOT:-/root/bass_cr_c21m_runs}"
mkdir -p "$C21M_WORK_ROOT"
C21M_CHECKOUT="$(mktemp -d "$C21M_WORK_ROOT/checkout_XXXXXXXX")"

git clone --filter=blob:none --no-checkout \
  https://github.com/cosmosapjw-quantum/bass_cr.git "$C21M_CHECKOUT"
git -C "$C21M_CHECKOUT" fetch origin "$C21M_CONTENT_COMMIT"
git -C "$C21M_CHECKOUT" sparse-checkout init --cone
git -C "$C21M_CHECKOUT" sparse-checkout set \
  research/cr_c21l_rei_pilot_20261021 \
  research/cr_c21m_independent_stress_20261021
git -C "$C21M_CHECKOUT" checkout --detach "$C21M_CONTENT_COMMIT"
test "$(git -C "$C21M_CHECKOUT" rev-parse HEAD)" = "$C21M_CONTENT_COMMIT"

C21M_UNIT="$C21M_CHECKOUT/research/cr_c21m_independent_stress_20261021"
C21M_BASE_PYTHON="${C21M_BASE_PYTHON:-python3.12}"
C21M_VENV="$C21M_WORK_ROOT/venv_$(basename "$C21M_CHECKOUT")"
"$C21M_BASE_PYTHON" -m venv "$C21M_VENV"
export C21M_PYTHON="$C21M_VENV/bin/python"
"$C21M_PYTHON" -m pip install -r "$C21M_UNIT/requirements-science.txt"
"$C21M_PYTHON" -c 'import sys,numpy,scipy,matplotlib; print(sys.version); print("numpy",numpy.__version__,"scipy",scipy.__version__,"matplotlib",matplotlib.__version__)'

C21M_GRID="$C21M_UNIT/grid_ncp_refinement98.json"
printf '%s  %s\n' \
  '768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04' \
  "$C21M_GRID" | sha256sum --check
```

원 sandbox의 관측 Python은 `3.12.14`였다. 고정 requirements는 NumPy `2.3.5`,
SciPy `1.17.0`, Matplotlib `3.10.8`이다. 현장 Python 실행 경로가 다르면
`C21M_BASE_PYTHON`에 실제 승인된 Python3.12 경로를 지정한다. 실제 patch version,
라이브러리와 platform은 새 manifest/receipt에 기록하고 기존 환경과 구분한다.

## 6. 자원 관측, 실행, 재개

```bash
export C21M_WORKERS=62
export C21M_LEASE_DIR="${C21M_LEASE_DIR:-/tmp/bass_cpu_leases}"
export C21M_TIMEOUT_SECONDS=3600
export C21M_ACTIVE_GRACE_SECONDS=300
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
export OMP_DYNAMIC=FALSE OMP_MAX_ACTIVE_LEVELS=1 PYTHONDONTWRITEBYTECODE=1

C21M_TAG="$(date -u +%Y%m%dT%H%M%SZ)_$$"
C21M_RUN_DIR="$C21M_WORK_ROOT/runs/ncp_refinement98_$C21M_TAG"
test ! -e "$C21M_RUN_DIR"

bash "$C21M_UNIT/ncp_run.sh" plan \
  "$C21M_CHECKOUT" "$C21M_GRID" "$C21M_RUN_DIR"

bash "$C21M_UNIT/ncp_run.sh" run \
  "$C21M_CHECKOUT" "$C21M_GRID" "$C21M_RUN_DIR"
```

`plan`은 source/input과 현재 관측 자원만 검사하며 ODE, output 생성, lease 점유를
하지 않는다. `run`도 첫 단계에서 계획을 다시 출력한다. 단순히 plan에
`execution_site=ncp`가 있다고 실제 remote science가 실행된 것은 아니다.
관측 hostname/platform, resource 영수증, 실제 COMPLETE raw와 반환을 함께 확인한다.

62는 명목64 logical CPU에서 CPU55와 coordinator를 제외한 요청 상한이다.
Runner는 실제 affinity·v1/v2 cgroup과 보이는 ancestor quota·가용 RAM·부하·lease·
남은 작업 수에 따라 더 적게 배정한다. coordinator 예산256 MiB, worker당512 MiB와
별도 memory reserve는 보수적 계획값이며 측정된 개선이나 강제 OS limit이 아니다.
각 science worker는 기본1 thread다. 다른 작업의 부하가 늘면 새 dispatch를 줄이고
완료 결과를 보존한다. 다른 owner의 process, output, lease를 침범하거나 종료하지 않는다.

현장의 기존 협력 lease 경로가 `/tmp/bass_cpu_leases`와 다르면
`C21M_LEASE_DIR`만 현장 표준으로 맞춘다. 별도 CPU partition이 배정되었다면
`C21M_CPU_LIST`에 그 목록을 지정한다. CPU55 제외는 유지한다.

동일 run을 재개할 때는 **원 `C21M_RUN_DIR`와 같은 checkout·환경·입력**을 복원한 뒤:

```bash
bash "$C21M_UNIT/ncp_run.sh" resume \
  "$C21M_CHECKOUT" "$C21M_GRID" "$C21M_RUN_DIR"
```

완료 raw/receipt/seal은 hash 검증만 하며 다시 적분하지 않는다. 아직 시작하지 않은
case만 재개된다. `STARTED.json` 이후 완료되지 않은 case와 FAILED case는
자동 재시도하지 않으며 원 실패 증거를 보존한다. 새로운 source, tolerance, input으로
기존 run manifest를 덮어쓰지 않는다.

## 7. 신규98 + 기존26 + 원중심1 결합 분석

새98의 COMPLETE가 모두 확인된 후 실행한다. 아래 첫 run 경로는 sparse checkout에
포함된 **이미 완료한 원26 raw**다. 그 적분을 다시 수행하지 않는다.

```bash
C21M_ANALYSIS_DIR="$C21M_WORK_ROOT/analysis/campaign125_$C21M_TAG"
test ! -e "$C21M_ANALYSIS_DIR"

"$C21M_PYTHON" -B "$C21M_UNIT/analyze_campaign.py" \
  --run "$C21M_UNIT/runs/pilot26" \
  --run "$C21M_RUN_DIR" \
  --reference "$C21M_UNIT/REFERENCE_REUSE.json" \
  --output "$C21M_ANALYSIS_DIR" \
  --plots
```

각 원 run의 physics source/settings, manifest, reservation, COMPLETE seal,
history/receipt hash를 검증하며 `2e-13` 이내로 중복되는 물리 요청 좌표를 거부한다.
선택 `--plots`는 완전한 균등 stress grid의 실제 셀을 그리며 보간하지 않는다.
CSV/NPZ만 필요하면 이 옵션을 뺀다. 결합 NPZ는 각 case의 원40성분×101시점,
gamma/nu multipole, 성분 tensor·signed 값·norm·cancellation을 보존한다.

현재 범용 분석기의 실제 검증 범위는 기존26+중심1이다. `analysis_pilot27`의
60개 NPZ 배열과 CSV 공통 값이 모두 동일했고 중복 물리좌표 거부 fixture를 통과했다.
미래125 실행과 수치·시각 검토를 이미 완료한 것으로 기록하지 않는다.

## 8. 해석·검증·게시·백업 반환 계약

물리 정의는 `sigma_hat=diag(-s,-s,2s)`, `pi_X_hat=diag(-p_X,-p_X,2p_X)`다.
원 `Pi_*_J_m3`는 `p_X=Delta p_X/3`이며 tensor norm이 아니다. Full norm은
`sqrt(6)*abs(p_X)`, shear norm은 `sqrt(6)*abs(s)`다. H가 s^-1이고 stress가
J/m^3이므로 dimensionless signed stress는 `sqrt(6)*(8*pi*G/c^2)*p_X/H^2`다.
에너지 Einstein coupling `8*pi*G/c^4`에는 `H_geom=H/c`를 사용하면 같다.
Photon과 massless neutrino를 분리하고 없는 UV sector를 임의의 0으로 추가하지 않는다.

| 단계 | EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|---|
| 인계 수용 | 기존 결과 검증 범위 기록 | 위 고정 content/document 확인 | provider ACK와 byte 검증 분리 | 기존 COMPLETE/HOLD 보존 |
| NCP plan | ODE `NOT_RUN` | 준비 코드/입력 게시 상태 유지 | 자원 관측 영수증 준비 | 선택98 `READY` |
| NCP run | 실제 COMPLETE/FAILED/미시작 개수 | 새 raw의 게시 여부를 따로 기록 | 완료 raw와 실패 증거 보존 | 실제 완료점만 진척 |
| 분석/검토 | 125점 source·물리·그림 확인 | 새 content commit과 실제SHA 확인 | 새 버전 ZIP·manifest·provider 영수증 | scoped 검증만 promotion |
| 마감 | 실제 실행 범위 확정 | content/document head 구별 | ACK/다운로드 hash 검증 단계를 개별 표기 | NOT_RUN/HOLD를 남김 |

`INDEPENDENT_CLOSEOUT_REVIEW.json` 및 하위 review의 통과 범위를 확인하고,
새 실행에 필요한 저장 trajectory 검산·독립 검토만 수행한다. 새 대규모 benchmark,
64-core scaling, 메모리 개선 측정 캠페인은 필요하지 않다. 수행하지 않은 speedup을
주장하지 않는다. P0 물리 오류나 source identity 충돌이 있으면 해당 promotion만
중단하고 증거를 보존한다. 독립적인 다른 연구를 일괄 중단하지 않는다.

새 ZIP은 기존 배송본을 덮어쓰지 않고 content/document/source/run identity를
명확히 결속한다. Google Drive + Dropbox + Library에 create-only로 저장하고
실제 ACK/object ID/bytes/SHA와 다운로드 후 byte 검증을 각각 기록한다.
완료 시 한국어로 결과·그림·검산 범위·source·commit·provider·DAG·다음 명령을 보고한다.
일반 triaxial/full H/He/UV/stars 재이온화 및 완성 CMB 예측은 `HOLD`이고
`global_error_bound=null`을 유지한다. 기존 C21F/G/H/I/J/K의 원 science,
실패 raw, 역사적 NOT_PUBLISHED 및 HOLD를 변경하지 않는다.

## 최종 문서 identity와 백업 확인

이 Git 문서에 쓰인 `SELF_DOCUMENT_COMMIT_RESOLVE_FROM_FINAL_AUTHORITY_RECEIPT`는 자신을 포함한 commit을 뜻한다.
파일에 자기 commit SHA를 넣는 순환을 피했으며, 별도 배포용 handoff와
`FINAL_AUTHORITY_RECEIPT.json`에는 실제 document SHA를 채운다.

통합 ZIP은 Library 성공 ACK 후 실제 다운로드 bytes·SHA256 일치를 확인했고,
Dropbox는 완료 ACK와 크기 일치를 확인했다. Drive는 320초 뒤 응답 없는 호출을
중단했으며 ACK와 object ID를 받지 못했다. Drive의 파일 부재나 실패를 확정하지
않는다. 모호한 호출은 정확한 파일명·폴더 조회와 필요 시 다운로드 검증으로
해소하고, 확인 없이 같은 파일을 중복 업로드하지 않는다.
