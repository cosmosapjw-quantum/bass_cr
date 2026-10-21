# 선택 후속 연구: NCP nested-grid 98개 신규점

**EXECUTION: `NOT_RUN` · PUBLICATION: 상위 content commit 참조 · BACKUP: 상위 배송 영수증 참조 · DAG: `OPTIONAL_NEXT_UNIT_READY`**

첫 독립 초기응력 pilot은 신규 26점과 기존 중심 1점의 27점이다. 이 문서의 98점은
그 첫 pilot의 마감에 필요한 작업이 아니며, 이후 해상도를 한 단계 높이려는 경우에
실행할 수 있는 별도 연구 단위다. 이 준비 과정에서는 ODE를 실행하지 않았다.

## 입력과 중복 제외

signed full Frobenius 축을 다음과 같이 세분했다.

```text
S0  = [-0.012, -0.006, 0, 0.006, 0.012]
Pm0 = [-0.0002, -0.0001, 0, 0.0001, 0.0002]
Pr0 = [-0.0002, -0.0001, 0, 0.0001, 0.0002]
```

전체 125점에서 기존 C21M 27개 요청 좌표를 제외해 98점을 얻었다. C21L81,
HH63, PR198 parent625·matter600·mixed6의 검토된 source grid와 비교한 결과,
기존 27점 이외에 추가로 제외할 외부 중복은 없었다. PR198 half-contraction 값은
모두 sqrt(2)배하여 비교했으며 각 축의 절대 비교 허용치는 `2e-13`이다.
이는 감사한 metadata 범위의 결론이며, 현재 접근하지 못한 대화·실행 반환·백업은
`UNAVAILABLE`이다. 향후 실제 실행 직전에는 그 사이에 완료된 동일 입력이
있는지 최신 결과 수용 목록을 갱신한다.

명시적 입력 파일은 `grid_ncp_refinement98.json`, run ID는
`c21m_ncp_refinement98_z20_z4_20261021`이다.

```text
grid SHA256:
768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04
```

## 여기서 완료한 초기조건 검산

`prepare_ncp_refinement.py`는 초기조건 builder를 98점 모두에 적용했다.
integrator 메서드에는 호출 시 실패하도록 guard를 걸었다. 새 matter A마다 원
canonical distribution·cell population·정규화를 다시 만들었으며 RHS·tolerance·
FP64·원 source를 변경하지 않았다.

| 검사 | 실제 결과 |
|---|---:|
| 최대 초기 물리좌표 절대오차 | (1.734723475976807\times10^{-18}) |
| 최대 Hamiltonian 상대잔차 | (2.220446049250313\times10^{-16}) |
| 최대 초기 massive energy 정규화 오차 | (2.220446049250313\times10^{-16}) |
| 최소 matter 연속 각분포 weight | 0.7074282019073919 |
| 최소 radiation 연속 각분포 weight | 0.9330122951577747 |
| 최소 massive cell number | (1.157793259790258\times10^{-30}) |
| ODE 적분 수 | 0 |

각 점의 A, 공통 photon/neutrino k, 실제 signed 초기좌표와 검산 수치, 고정
source/grid/generator hash는 `NCP_REFINEMENT98_PREPARATION.json`에 있다.
이 결과는 시간발전의 안정성이나 수렴성 검사를 대체하지 않는다.
`global_error_bound=null`을 유지한다.

## NCP 실행 명령

최종 게시된 content를 독립 checkout에 가져온 뒤 이 연구 디렉터리에서 수행한다.
먼저 실제 NCP host와 현재 affinity·quota·메모리·부하·공유 lease를 확인한다.
아래 첫 명령은 실행이나 lease 점유 없이 현재 관측 자원과 source identity를
출력한다. `--workers 62`는 명목 64 logical CPU 중 CPU55와 coordinator를
제외한 요청 상한이며 실제 사용 개수를 보장하지 않는다.

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1

C21M_NCP_RUN_DIR="$PWD/runs/ncp_refinement98_$(date -u +%Y%m%dT%H%M%SZ)"

python3 shared_runner.py \
  --grid grid_ncp_refinement98.json \
  --output "$C21M_NCP_RUN_DIR" \
  --workers 62 \
  --lease-dir /tmp/bass_cpu_leases \
  --execution-site ncp \
  --plan-only

python3 shared_runner.py \
  --grid grid_ncp_refinement98.json \
  --output "$C21M_NCP_RUN_DIR" \
  --workers 62 \
  --lease-dir /tmp/bass_cpu_leases \
  --timeout-seconds 3600 \
  --active-grace-seconds 300 \
  --execution-site ncp
```

서버의 기존 협력 lease 디렉터리가 다르면 실제 경로를 두 명령에 동일하게 적용한다.
다른 작업이 있으면 runner가 가용 CPU·quota·메모리 안에서 admission과 신규
dispatch를 조정한다. 다른 작업의 process·output·lease는 변경하지 않는다.
memory budget은 worker당 512 MiB, coordinator 256 MiB에 별도 reserve를 둔
보수적 분석 예산이다. 실제 사용량을 측정한 개선 주장이나 64-core 성능 주장이 아니다.

중단 후 같은 source·software·input manifest에서 아직 시작하지 않은 점만
계속할 때는 위 두 번째 명령에 `--resume`을 추가하고 **원 run 디렉터리**를 지정한다.
완료점이나 시작 후 실패한 점은 자동 재적분하지 않는다. 실행이 끝나면 각 case의
원 `history.npz`, `RESULT.json`, `COMPLETE.json`과 전체 manifest·resource·return
영수증을 보존하고 실제 실행 결과를 DAG에 수용한다.

## 준비된 후속 분석 명령

`analyze_campaign.py`는 완료된 여러 run의 source·manifest·raw·receipt·completion
seal을 검증하고 기존 C21L 중심을 한 번만 결합한다. 물리좌표가 `2e-13` 이내로
중복되면 output을 만들기 전에 거부한다. `analyze_pilot.py`의 source 검증·물리
검산과 C21L component 분해를 재사용한다. 원 26+1 전용 분석기의 계약은 그대로다.

98점 실행이 모두 완료된 뒤 다음 명령을 실행한다. `runs/pilot26`는 이미 완료한
26개 원본과 모든 manifest·receipt를 가져온 경로이며 해당 적분을 다시 하지 않는다.

```bash
C21M_NCP_ANALYSIS_DIR="$PWD/analysis/ncp_campaign125_$(date -u +%Y%m%dT%H%M%SZ)"

python3 analyze_campaign.py \
  --run runs/pilot26 \
  --run "$C21M_NCP_RUN_DIR" \
  --reference REFERENCE_REUSE.json \
  --output "$C21M_NCP_ANALYSIS_DIR" \
  --plots
```

CSV·NPZ·영수증만 필요한 경우 `--plots`를 빼면 된다. NPZ는 결합한 각 case의
원 `Y[40,101]`, signed stress·norm·tensor·cancellation 및 gamma/nu multipole를
보존한다. 선택 그림은 완전한 균등 stress grid의 각 S0 slice에서 최종 signed
총응력과 signed shear를 실제 셀로 표시한다. 보간하거나 추가 적분하지 않는다.

현재 환경에서는 이미 완료한 26개와 원 중심만으로 실제 분석을 실행했다.
기존 `analysis_pilot27`의 모든 NPZ 배열과 CSV 공통 값이 같음을
`checks/campaign_compatibility.json`에 기록했다. 미래 125개의 실행·검증을
이미 수행한 것으로 간주하지 않는다. 원 source는 non-tilted collisionless LRS
Bianchi I이며 z20→4, DOP853, rtol `3e-11`, atol `3e-13`을 유지한다.
