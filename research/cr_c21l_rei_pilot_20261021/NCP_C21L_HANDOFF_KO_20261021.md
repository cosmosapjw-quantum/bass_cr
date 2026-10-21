# C21L NCP / Codex 인계문

**상태: 실행 가능한 코드와 완료된 sandbox pilot의 인계. Git content 자리표시자는 게시 후 문서 commit에서 실제 pin으로 결속한다.**

## 1. 목표와 현재 완료 범위

C21L의 원래 목표인 REI 기반 초기 shear–stress 9×9 격자 **81개 물리 사례는 이미 모두 완료**되었다. 기본 인계 작업은 저장된 PNG/PDF, endpoint CSV, 전체 NPZ 이력을 사용하는 것이다. 완료된 81개를 NCP에서 다시 계산하는 것은 기본 작업이 아니다.

현재 산출물은 LRS, non-tilted, collisionless Einstein–Boltzmann–Vlasov, z=20→4의 **EXPLORATORY / PRELIMINARY** 결과다. Full H/He·UV·stars, 일반 triaxial dynamics, NCP 성능·scaling, 전역 오차 보증으로 확대하지 않는다. `global_error_bound=null`을 유지한다. 기존 과학 HOLD와 다른 프로젝트의 작업 경계도 유지한다.

사용자는 이미 NCP 실제 실행을 요청했다. 접근과 가용 자원을 확인한 뒤, 아래 별도 실행 절차에 따라 **새 출력 디렉터리에서 한 번의 bounded run**으로 수행한다. 기존 81개 결과, 과거 suite, 벤치마크를 반복 실행하지 않는다. 실패는 raw로 보존하고 blind rerun하지 않는다.

### 현재 원격 접근 상태

이 인계 기준 **NCP remote probe = UNKNOWN**이다. NCP 로그인·가용성·실제 CPU affinity/cgroup·quota·메모리·idle core·다른 session의 lease 사용 여부는 확인하지 않았다. 아래 NCP 명령은 복사 가능한 실행 지침이며, 이미 NCP에서 수행했다는 기록이 아니다. 로컬 sandbox 결과로 NCP 실행 또는 성능을 주장하지 않는다.

## 2. 전달할 내용과 고정된 위치

대상 저장소는 `cosmosapjw-quantum/bass_cr`이며, 전달 단위는 다음 디렉터리다.

```text
research/cr_c21l_rei_pilot_20261021/
```

Git content revision은 배포 담당 parent가 확정한 **`@CONTENT_SHA@`**로만 지정한다. 이 자리표시자를 branch 이름이나 임의의 최신 HEAD로 대체하지 않는다. 실제 content commit을 확인하기 전에는 pinned 가져오기 명령을 실행하지 않는다.

필수 구성은 다음과 같다.

| 위치 | 역할 |
|---|---|
| `README.md` | 실제 결과, CLI, 물리 범위와 실행 방식 |
| `adapter.py` | 고정된 PR147 물리 source 재사용, 초기 S/P mapping, full history |
| `runner.py`, `resources.py` | v2 실행·resource admission·resume |
| `plotter.py` | 저장된 case 결과만 읽는 plotter |
| `SOURCE_MANIFEST.json`, `vendor/rei/` | 변경하지 않은 원본 source closure와 identity |
| `runs/pilot81/` | 완료된 원래 81개 raw 결과·CSV·NPZ·그림 |
| `archived_execution_v1/` | 원래 81개를 만든 정확한 v1 코드와 vendor closure |
| `checks/`, `focused_checks.log` | 원래 7개 focused check의 실제 결과 |
| `repair_checks_final/`, `repair_checks_final.log` | v2 repair의 focused 결과; 실제 worker + 명시적 solver test double |
| `REPAIR_RETURN.json` | v1/v2 분리, 새 hash/identity, 추가 물리 ODE 0 기록 |

원래 결과의 핵심 파일은 다음이다.

```text
runs/pilot81/plots/initial_norms_final_Sigma_F.png
runs/pilot81/plots/initial_norms_final_Sigma_F.pdf
runs/pilot81/plots/initial_norms_final_Pi_F.png
runs/pilot81/plots/initial_norms_final_Pi_F.pdf
runs/pilot81/endpoints_*.csv
runs/pilot81/cases/*/history.npz
runs/pilot81/cases/*/RESULT.json
runs/pilot81/RESOURCES_*.json
runs/pilot81/RETURN_*.json
runs/pilot81/SUMMARY_*.json
```

PNG/PDF 두 그림은 실제 완료된81개 case를 읽어 생성했으며, actual initial Frobenius norm 축과 네 sign branch, zero-axis 공유, PRELIMINARY 표시를 포함한다.

## 3. 기존 작업을 건드리지 않고 가져오기

**현재 checkout의 branch 전환·reset·clean·merge·전체 동기화나 다른 프로세스 종료를 하지 않는다.** 기존 checkout에 필요한 content object가 있으면 그 object에서 대상 unit만 읽어 별도 디렉터리로 추출한다. 없으면 pinned archive에서 대상 unit만 별도 디렉터리로 추출한다. 현재 작업 tree에 덮어쓰지 않는다.

아래는 Bash 기준이다. `C21L_WORK_ROOT`와 `C21L_CHECKOUT`만 해당 운영 환경의 실제 경로로 지정한다. `$HOME` 등 시스템 변수를 다른 용도로 재정의하지 않는다.

### 경로 A — 기존 checkout에 pinned content object가 있는 경우

```bash
C21L_WORK_ROOT="$HOME/c21l_runs"
C21L_CHECKOUT="/absolute/path/to/existing/bass_cr"
mkdir -p "$C21L_WORK_ROOT"
C21L_STAGE=$(mktemp -d "$C21L_WORK_ROOT/c21l_import.XXXXXXXX")
mkdir "$C21L_STAGE/source"

git -C "$C21L_CHECKOUT" archive --format=tar \
  @CONTENT_SHA@ research/cr_c21l_rei_pilot_20261021 \
  > "$C21L_STAGE/unit_pinned.tar"
tar -xf "$C21L_STAGE/unit_pinned.tar" -C "$C21L_STAGE/source"
C21L_UNIT="$C21L_STAGE/source/research/cr_c21l_rei_pilot_20261021"
cd "$C21L_UNIT"
```

이는 기존 Git object를 읽기만 한다. content object가 없어서 실패하면 기존 checkout을 변경하는 대신 경로 B를 사용한다. 다른 작업의 branch·작업 파일을 교체하지 않는다.

### 경로 B — pinned archive를 별도 디렉터리에 추출하는 경우

```bash
C21L_WORK_ROOT="$HOME/c21l_runs"
mkdir -p "$C21L_WORK_ROOT"
C21L_STAGE=$(mktemp -d "$C21L_WORK_ROOT/c21l_import.XXXXXXXX")
mkdir "$C21L_STAGE/source"

curl --fail --location --retry 1 \
  --output "$C21L_STAGE/content_pinned.tar.gz" \
  "https://github.com/cosmosapjw-quantum/bass_cr/archive/@CONTENT_SHA@.tar.gz"
tar -xzf "$C21L_STAGE/content_pinned.tar.gz" \
  --wildcards --strip-components=1 \
  -C "$C21L_STAGE/source" \
  '*/research/cr_c21l_rei_pilot_20261021/*'
C21L_UNIT="$C21L_STAGE/source/research/cr_c21l_rei_pilot_20261021"
cd "$C21L_UNIT"
```

저장소가 비공개이면 이미 승인된 read-only 다운로드 경로로 동일한 pinned archive를 받는다. 인증 실패를 이유로 접근 설정·remote·기존 checkout을 바꾸거나 인증 정보를 출력하지 않는다. archive를 받을 수 없으면 접근 상태와 실패를 기록하고, source를 추정하여 다시 만들지 않는다.

추출한 unit에는 고정된 vendor closure가 포함되어 있으므로 다른 연구 checkout의 물리 모듈을 import하도록 경로를 바꿀 필요가 없다.

## 4. Python 의존성

표준 Python 모듈 외 과학 의존성은 **NumPy, SciPy, Matplotlib**이다. 별도 Fortran/C++ build, MPI launcher, 새 heavyweight framework 설치는 필요하지 않다. 원래 pilot에서 실제 사용한 버전은 다음이다.

| 패키지 | 원래 pilot 실제 버전 |
|---|---|
| NumPy | 2.3.5 |
| SciPy | 1.17.0 |
| Matplotlib | 3.10.8 |

이미 이 패키지를 import할 수 있는 기존 Python 환경이 있으면 추가 설치 없이 사용한다. 원래 버전 목록은 관측된 실행 환경 기록이며, 현재 NCP에 같은 패키지가 설치되어 있다는 뜻은 아니다. 새 실행은 실제 Python/NumPy/SciPy 버전을 case runtime에 기록한다.

패키지가 없다면 기존 공용 환경을 변경하는 대신, 별도 환경에 설치한다. 다음은 설치가 필요한 경우에만 사용하는 예시다.

```bash
python -m venv "$C21L_STAGE/venv"
. "$C21L_STAGE/venv/bin/activate"
python -m pip install numpy==2.3.5 scipy==1.17.0 matplotlib==3.10.8
```

실제 플랫폼·Python과 wheel 호환성이 맞지 않거나 설치가 실패하면 오류를 남긴다. solver 설정이나 source를 바꾸어 설치 문제를 우회하지 않는다. 의존성 확인을 이유로 기존81개·old suite·성능 benchmark를 실행하지 않는다.

## 5. 기본 작업 — 이미 저장된 결과 사용

원래 81개는 **81/81 COMPLETE**, failed/incomplete0, worker exit `[0,0,0,0]`이다. 우선 저장된 두 PNG/PDF와 CSV/NPZ를 열어 사용한다. 이를 위해 `runner.py`를 실행할 필요가 없다.

원래 물리 실행의 actual scope는 sandbox였으며, 원래 manifest의 `NCP_execution=false`는 그 실행에 맞는 기록이다. NCP에서 그 파일을 열었다는 이유로 원래 결과를 NCP 결과로 바꾸지 않는다.

그림을 다시 생성해야 한다면 plotter는 **saved outputs only**다. 기존 `plots/`가 있으면 create-only 규칙으로 거부하므로 원본 결과를 덮어쓰지 말고 별도 view 디렉터리에 저장된 case 결과를 복사한다.

```bash
C21L_VIEW="$C21L_STAGE/saved_view"
mkdir "$C21L_VIEW"
cp -a "$C21L_UNIT/runs/pilot81/cases" "$C21L_VIEW/cases"
python plotter.py "$C21L_VIEW"
```

이 명령은 저장된 결과의 그림만 생성하며 물리 ODE를 풀지 않는다. 원래 `runs/pilot81/plots/`는 그대로 둔다. 이미 저장된 그림을 사용할 수 있으면 이 재생성도 생략한다.

## 6. 별도 작업 — 사용자 요청 범위 내 실제 NCP 실행

이 절차는 이미 요청된 **별도 NCP 실행**에 적용한다. 추가 사용자 확인을 요구하지 않는다. 기본 saved-result 인계와 분리한다. 새 출력 디렉터리는 run마다 create-only이며, 아래 예시는 한 번의600초 bounded campaign이다. 같은 입력의 전체 campaign을 blind rerun하지 않는다.

### 자원과 공유 규칙

- **CPU55는 보호한다.** runner는 actual affinity와 visible cgroup-v2 cpuset을 교차한 뒤 CPU55를 제외한다. `--cpu-list`로 다시 넣으려 하지 않는다.
- `--workers 63`은 **요청 상한**이다. 실제 worker 수는 affinity, 모든 보이는 ancestor CPU quota, memory limit/available, 짧은 `/proc/stat` load sample, cooperative lease에 의해 더 작아진다.
- **코디네이터도 CPU 한 개로 센다.** 허용 CPU0–63 중 CPU55를 제외한63개만 있다면 최대는 worker62개 + coordinator1개다.63 worker 실행을 보장한다고 쓰지 않는다.
- worker budget512MiB, coordinator256MiB, memory reserve `max(1GiB, effective limit의12.5%)`를 적용한다.
- 각 worker와 coordinator는 서로 다른 admitted CPU에 고정된다. 과학 import 이전 threads1 환경을 runner/adapter가 설정한다. 아래 launch에서도 threads1을 명시한다.
- **모든 협력 session은 같은 lease 디렉터리**를 사용한다. 기본은 `/tmp/bass_cpu_leases`, 파일 이름은 `cpu_N.lock`이다. C21K 등도 동일 경로를 사용해야 상호 배제가 된다.
- lock은 이를 따르는 client 사이에서만 협력한다. unmanaged job은 관측할 뿐 제어·예약하지 않는다. 다른 job/session이 존재한다는 이유로 host 전체를 blocker로 두지 않고, idle하고 lease 가능한 실제 core를 사용한다.
- 다른 session의 lock 파일을 지우거나 lease를 강제로 뺏지 않는다. 관련 없는 프로세스에 signal을 보내지 않는다.

### CLI site 의미와 plan-only

`--execution-site ncp`는 **운영자 선언**이다. 자동 NCP attestation이 아니다. receipt는 관측된 hostname/platform과 자원 관측을 함께 기록한다. 옵션을 생략한 기본값은 `unspecified`이고 `NCP_execution=null`이다. `ncp` 선언과 `NCP_execution=true`만으로 실제 원격 실행·정확도·성능이 입증되는 것은 아니다.

먼저 실제 NCP에서 가벼운 plan-only를 실행한다. 이 단계는 ODE를 풀지 않으며 lease 획득·최종 idle CPU 배정까지 증명하지 않는다. 실제 admission은 실행 시작 시 다시 관측한다.

```bash
python runner.py --plan-only \
  --workers 63 \
  --execution-site ncp \
  --lease-dir /tmp/bass_cpu_leases
```

추가 CPU 제한이 필요하면 지원되는 `--cpu-list 0-54,56-63` 같은 형식을 사용한다. 이 옵션은 실제 허용 범위를 **줄일 수만 있으며 확대하지 않는다**. 실제 machine의 CPU 번호가 다르면 임의의64-core 배치를 가정하지 않는다.

### 새 디렉터리에서 단 한 번 실행

```bash
C21L_RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)_$$"
C21L_OUT="$C21L_WORK_ROOT/c21l_ncp_$C21L_RUN_ID"

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
BLIS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 \
python runner.py \
  --out "$C21L_OUT" \
  --workers 63 \
  --execution-site ncp \
  --lease-dir /tmp/bass_cpu_leases \
  --timeout-seconds 600 \
  > "$C21L_OUT.stdout.log" 2>&1
C21L_EXIT=$?
printf 'C21L runner exit=%s\n' "$C21L_EXIT"
```

`C21L_OUT` 자체는 사전에 만들지 않는다. runner가 create-only로 만든다. 기존 디렉터리가 있다는 오류를 지우기·덮어쓰기·동일 실행 반복으로 해결하지 않는다. 출력의 RESULT/RETURN/SUMMARY에서 실제 exit, completion counts, raw failures와 resource observations를 확인한다. shell exit0만으로 scoped science admission이나 NCP 성능 승격을 선언하지 않는다.

campaign의 computation deadline 외에 bounded global process teardown grace가 추가될 수 있다.600초를 전체 wall-time의 엄밀한 debit cap으로 설명하지 않는다.

새로 저장된 결과를 그리는 명령은 다음이다. 이 또한 saved outputs만 읽는다.

```bash
python plotter.py "$C21L_OUT"
```

실패한 case가 있어도 좋은 case 결과는 보존한다. plotter는 완료된 저장 case만 읽으며, 실제 완료 개수를 보고한다.81개가 아니면 partial로 보고하고 누락을 보간해 채우지 않는다.

## 7. v1 executed identity와 v2 runtime identity

다음 값들은 **Git revision이 아니라 실행 manifest identity digest**다. Git content 지정에는 계속 `@CONTENT_SHA@`만 사용한다.

| 실행/선언 | manifest identity |
|---|---|
| 원래81개를 만든 v1 executed identity | `0090e1549b21b07e46001de2bf9cb2eab9bf0cba87ffe3d4d824ba117fecb44a` |
| repaired v2 / unspecified | `b5324118085fdd3e431b82bf602856ee92fae1332a7aeae7ff10e3b26c1999d7` |
| repaired v2 / sandbox 선언 | `2130237831e08f21331b3744292a437c04c4737f600d36b1ca96d768416b5f1f` |
| repaired v2 / ncp 선언 | `11541eb423eecd1a6d7caeb1bc9de5a56456b9f8d762e326644ad1aeda2f046b` |
| repaired v2 / other 선언 | `cfc7a4c56835d3379e5ec1b96315049104580462b530d979e9919a20ff646730` |

v1 실행 후 parent가 허용한 repair는 site provenance와 queued/started recovery를 고쳤다. 물리 adapter·원본 source·기존81개 raw/manifest는 바꾸지 않았다. **추가 물리 ODE 실행0, 추가81개 campaign0**으로 repair를 확인했다. 실제 worker를 사용한 repair control은 명시적인 solver test double이며 새 물리 검증으로 세지 않는다.

현재 v2 runner는 옛 v1 manifest의 `--resume`을 의도적으로 거부한다. 이를 해결하려고 기존 manifest의 identity를 고쳐 쓰거나 old81개를 다시 돌리지 않는다. 원래 실행 코드가 필요한 read-only 확인은 `archived_execution_v1/`를 사용하고, 기본 결과 이용은 저장된 그림·CSV·NPZ로 충분하다.

## 8. v2 resume 정책

새 v2 실행이 중단되었을 때만 동일 output과 동일 source/settings/site로 다음을 사용한다. `C21L_OUT`은 위 새 실행의 실제 경로여야 한다.

```bash
python runner.py \
  --out "$C21L_OUT" \
  --workers 63 \
  --execution-site ncp \
  --lease-dir /tmp/bass_cpu_leases \
  --timeout-seconds 600 \
  --resume
```

| 저장 상태 | v2 resume 동작 |
|---|---|
| MISSING | 아직 예약되지 않은 case로서 실행 가능 |
| 새 QUEUED 형식, STARTED 없음 → NOT_STARTED | 알려진 미시작 case만 실행 가능 |
| COMPLETE | manifest identity와 history SHA256 확인 후 기존 결과 재사용 |
| STARTED가 있으나 COMPLETE 없음 → INCOMPLETE | 이미 시도한 raw를 보존하며 자동 재시도하지 않음 |
| FAILED | 실패 raw 보존, 자동 재시도하지 않음 |
| 옛 v1 reservation, 완료 receipt 없음 | 명시적 미시작 증거가 없으므로 INCOMPLETE 유지 |
| source/settings/code/site identity 불일치 | resume 거부; 기존 결과를 변경하지 않음 |

resume은 누락된 완료를 허위 PASS로 바꾸지 않는다. FAILED/시작된 INCOMPLETE를 다시 시도해야 하는 과학적·운영상 판단은 parent에게 반환하고, 동일 failure를 지운 뒤 blind retry하지 않는다. 이미 전부 완료된 원81개에는 이 새 실행 절차를 적용하지 않는다.

## 9. Codex에게 그대로 전달할 작업 지시

> `@CONTENT_SHA@`의 `research/cr_c21l_rei_pilot_20261021/`만 별도 실행 디렉터리로 가져오세요. 기존 checkout·branch·dirty/untracked 작업·다른 프로세스를 변경하지 마세요. 코드는 frozen이며 source/solver/물리 설정을 수정하지 마세요.
>
> 기본 목표는 이미 완료된81개 결과의 saved PNG/PDF·CSV·NPZ를 이용하고 실제 evidence를 인계하는 것입니다. old81개, old suite, benchmark를 다시 실행하지 마세요.
>
> 이미 요청된 NCP 실행을 위해 접근과 실제 자원을 확인한 뒤, 문서의 v2 명령으로 새 create-only output에서 한 번의600초 bounded run을 하세요. `--execution-site ncp`는 operator declaration이며 실제 hostname/platform/resource observations와 구분하세요. 현재 사전 remote probe는 UNKNOWN입니다.
>
> `--workers 63`을 요청하되 actual CPU/cgroup/quota/memory/load/lease cap을 따르세요. CPU55를 보호하고 coordinator CPU도 세세요. threads1, 동일 `/tmp/bass_cpu_leases`와 `cpu_N.lock`을 사용하세요. 다른 작업이나 lock을 중단·제거하지 마세요. 허용 CPU가0–63뿐이면 CPU55 제외와 coordinator 포함으로 worker 최대62개입니다.
>
> raw 결과·실패·실제 exit와 completion counts를 보존하세요. v2 resume은 동일 manifest의 MISSING/알려진 NOT_STARTED만 새로 실행하고 COMPLETE는 재사용합니다. FAILED/시작된 INCOMPLETE는 자동 재시도하지 마세요. old v1 manifest를 v2에 맞춰 수정하지 마세요.
>
> 완료 시 resource plan/observations, 실제 worker CPU/exit, RETURN/SUMMARY, CSV/NPZ/plots 위치를 보고하세요. `global_error_bound=null`과 preliminary LRS collisionless scope를 유지하고, 성능·NCP scaling·full H/He·일반 triaxial 채택을 주장하지 마세요. Git/remote publication이나 다른 프로젝트 campaign은 이 인계 작업에 포함되지 않습니다.

## 10. 반환해야 할 최소 evidence

인계 결과에는 source content placeholder의 실제 결속 여부, 실행/미실행 상태, 저장 결과 사용 여부, 실제 수행한 명령과 exit, 새 실행을 했다면 그 output 경로와 source/runtime identity, resource observation·worker exits·completion counts를 적는다. 추가 실제 실행을 하지 않았다면 **NCP execution NOT_RUN, remote probe UNKNOWN**을 그대로 적는다.

새 run의 물리 결과가 있어도 시간 기록은 telemetry로만 보고하며, matched performance experiment를 하지 않은 상태에서 speedup·63/64-core scaling을 계산하지 않는다. 결과 validity, provenance, packaging을 구분하고 parent의 기존 scoped scientific admission 경계를 유지한다.
