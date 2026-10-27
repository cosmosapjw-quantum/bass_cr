# C5 HeIII consumer 구현 초안 인계

## 상태와 편집 범위

이 묶음은 `run_20261027/implementation_work/`에만 작성했다. 기존 H1/HeI source와 solver는 수정하지 않았다. 새 생산 모듈을 import하거나 controls·provider point·solver·plot을 실행하지 않았다. Python 파일 7개를 `py_compile`로 기계적으로 구문 확인하고 JSON template 두 개를 파싱했다. 이 확인은 C6/C7/C9 PASS가 아니다. 부모가 C5 원문을 검토·복사·게시한 뒤 실제 stage 실행을 지휘한다.

구현 기준은 THEORY SHA256 `3e5f31d271c32efcd1ee9a1eb23625c2ead0dc0b6c4a78732de34ef4a696ceae`, R6 독립 검토 SHA256 `d072afe65f309490168dc2ac77404d3c6ec3e902c72f3554c69f65233c0a5304`, 최종 R9 FROZEN_CONTRACT SHA256 `73ec000acf2dc737bd5902bc761b2f3ccb662f1d800565b85a3cb128bd632e9b`다. 현재 읽은 bass_cr AGENTS SHA256는 `8d62d9758fe173263eb3820c7b00ca569193bb7f912fc3d95d145e73d4a40970`이다. 독립 C9 source는 별도 담당자가 제공한다.

`AUTHORING_RECEIPT.json`은 각 작성 파일의 bytes/SHA256, top-level 함수, 36개 control 이름과 기계적 확인 CPU를 기록한다. `mechanical_compile/`의 pyc는 검사용 임시 부산물이며 과학 실행 증거·게시 source에 포함할 필요가 없다.

## 파일과 고정 사상

| 파일 | 역할 |
|---|---|
| `engine.py` | 정확한 21입력/authority 검증, native HeII point provider, 새 coefficient, Z/Thomas pivot 확인, shared K1의 18+5+4+1 RHS, source 평균 |
| `primary.py` | 8 cases/224 RHS, 24 source rows와 integrated events, 252 grid/domain 비교, 실패·부분 결과 보존 |
| `export_adapter.py` | 명시 frame/source-review pin, 적분 N/E와 rate 분리, native25/별도 retained photon, canonical ID 중복 방지 |
| `controls.py` | 변경된 36 control; 두 one-state consumer fixture 56 RHS와 추가 tiny analytic 5 RHS; 과거 31 controls 재실행 0 |
| `dispatch.py` | create-only run/lease/source snapshot, 전체 과거 시도 비용, 고정 CPU/RAM/wall/affinity, 실패 receipt |
| `prepare_inputs.py` | pin된 기존 파일 21개의 exact-byte 복사, CONFIG/INPUT_MANIFEST 생성; 과학 import/계산 0 |
| `plot_saved.py` | 저장된 finest6행만 읽는 4-panel PNG/PDF |
| `CONFIG_TEMPLATE.json` | nHeIII=.01, d1, I54.42, explicit actual nb=null, 기존 bath/criteria, 30 CPU subcap |
| `INPUT_PINS_TEMPLATE.json` | 현재 복구된 입력 21개 총15,912,941B의 exact SHA256; private payload 내용은 포함하지 않음 |

physical18은 old first10 + new λ/λE + old bath6이다. conditional5는 new physical columns `[0,1,6,8,10]`를 사용한다. stable4는 `-λ*[oldHeI CE,time,pH1,pHeI]`다. w는 old exact stored K0의 새 λ RHS이다. 모든 세 RR 채널의 물리 reward와 conditional moments는 하나의 K1에 속한다. old generator/source projection/source quadrature/old primary/ODE counters는 0이다.

출력 NPZ는 `K_HeI_diag`, `K_diag`, old offdiagonal, `lambda_H1`, `lambda_HeI`, `lambda_HeII`, 각 sigma, 18/5/4 RHS와 solutions, w, explicit H1/HeI/HeII p/r/v, 세 photon/internal, stable4, energy terms, 새 diagonal addition-loss diagnostic을 저장한다. 독립 reference는 exact stored HeI diagonal에 Decimal(lambda)를 더하는 별도 C9 코드가 담당한다.

## 실행 전에 root가 배치할 파일

7개의 `.py`와 두 template JSON을 새 unit의 `implementation/`에 복사한다. `review/R6_THEORY.json`, `intake/HEIII_NATIVE25_MAP_R5.json`, `THEORY_KO.md`, 최종 `FROZEN_CONTRACT.md`가 unit에 있어야 한다. C9 전에 별도 독립 `review/c9_independent.py`도 배치한다. 모든 작업은 해당 stage의 AGENTS/HEAD/병렬 변경 확인 후 진행한다.

## 정확한 CLI

아래는 인계용 명령이며 이 child는 실행하지 않았다.

```bash
HEIII_UNIT=/workspace/scratch/5fcfe17050d5/bass_cr/research/cr_heiii_ground_rr_20261027
HEIII_OLD_UNIT=/workspace/scratch/5fcfe17050d5/bass_cr/research/cr_he4_ground_rr_20261025

python -B "$HEIII_UNIT/implementation/prepare_inputs.py" \
  --unit "$HEIII_UNIT" \
  --old-unit "$HEIII_OLD_UNIT" \
  --prep-run-id cr_heiii_inputs_20261027_v1

python -B "$HEIII_UNIT/implementation/dispatch.py" \
  --unit "$HEIII_UNIT" --mode controls --run-id cr_heiii_rr_controls_20261027_v1

python -B "$HEIII_UNIT/implementation/dispatch.py" \
  --unit "$HEIII_UNIT" --mode primary --run-id cr_heiii_rr_primary_20261027_v1

python -B "$HEIII_UNIT/implementation/dispatch.py" \
  --unit "$HEIII_UNIT" --mode review --run-id cr_heiii_rr_c9_20261027_v1

python -B "$HEIII_UNIT/implementation/dispatch.py" \
  --unit "$HEIII_UNIT" --mode plot --run-id cr_heiii_rr_plot_20261027_v1
```

prepare는 old unit 내용을 읽기만 하며, destination inputs와 preparation run을 create-only로 만든다. 성공 receipt는 `preparations/<prep-run-id>/PREPARATION_RECEIPT.json`이다. 중단된 inputs/attempt를 지우거나 기존 receipt를 덮지 않는다. 입력 변경·부분 복구가 필요하면 부모가 별도 provenance를 보존해 처리해야 한다.

각 dispatcher 실행은 `runs/<run-id>/`를 create-only로 만든다. 사전 admission 거절도 `DISPATCH_RECEIPT.json`에 기록한다. 기존 run ID 재실행은 허용하지 않는다. retry가 필요하면 `implementation/RUN_AUTHORIZATIONS.json`에 `runs:[{mode,original_run_id,authorized_run_id,reason}]`를 명시한다. 하위 stage가 성공한 retry를 입력으로 채택할 경우 `selected_input_runs:{primary:...,controls:...}`를 별도로 명시한다. 이 선택은 기존 실패 비용을 없애지 않는다.

C9 child 명령은 담당자와 합의한 `--unit-dir UNIT --primary-dir PRIMARY --controls-dir CONTROLS --out-dir OUTPUT`다. dispatcher가 root가 선택한 해당 run 경로를 전달한다.

## 적분 export schema와 C9 증거

`SOURCE_WEIGHTED_RESULTS.json.rows`와 `INTEGRATED_EVENT_EXPORTS.json.events`에는 각각 24개의 case,z 대안이 있다. 대안을 합산한 실제 population/time history라는 의미가 아니다. `SOURCE_WEIGHTED_ROWS.csv`도 생성한다.

각 event의 주요 필드는 다음과 같다.

- `canonical_event_id`, `case`, `z`, `source_id`, `frame="bath_frame_rest_target"`, `source_qualification`, `per_event_template`
- `integrated_count_m3`
- `integrated_energy_J_m3:{binding,thermal_kinetic,fast_kinetic,radiation,recoil,escaped,external}`
- `density_delta_m3:{"He4:2", "He4:1", "e:fast", "photon"}`
- `native25=null` (actual rows)
- `retained_photon_port:{integrated_count_m3,integrated_energy_J_m3,count_per_baryon:null,energy_J_per_baryon:null,...}`
- `event_rate_m3_s=null`, `exposure_s=null`, `instantaneous_rhs=null`, `physical_heating_J_m3=null`, `irreversible_assimilation=false`

C6의 `NATIVE25_POSITIVE_NB_CONTROL.json`은 `{schema,status,input,event}`를 저장한다. 입력은 count=1.25 cm^-3, kinetic=2.5 eV cm^-3, 명시 nb=2.5e6 m^-3다. 이 파일을 C9가 production import 없이 독립 검사한다. C6 `CONTROL_RESULTS.json.checks`에는 `integrated_duplicate_event_id_rejected`와 `integrated_cross_frame_rejected`가 실제 rejection reason과 함께 남는다. 선택된 toy 사건에서 thermal count와 selected-model thermal source는 0이며, 이를 전역 physical heating 완료로 해석하지 않는다.

## 예산·실패·검증 한계

새 unit만 controls5, primary8, review10, plot5, localmisc2 =30 CPU seconds다. `prepare`와 coordinator time은 localmisc에 합산한다. 같은 stage의 실패/retry worker 비용도 stage subcap에 누적한다. run directory의 receipt가 없거나 worker/coordinator 비용이 boolean·음수·비유한·누락이면 `UNKNOWN_PRIOR_ATTEMPT_BUDGET`로 다음 admission을 거절한다. 과거 H1/C23E/HeI/interface 예산을 빌리지 않는다.

Dispatcher는 실제 허용 affinity에 worker0/reviewer2/coordinator8이 모두 있고 서로 다른지 확인한다. Native threads=1, worker AS512MiB, wall60, clean inactive cache+half clean active estimate에서 reserve1GiB를 뺀 RAM admission을 사용한다. 지연 제한에는 소유한 child process group만 종료한다. worker와 coordinator의 실측 비용을 보존한다. RLIMIT_CPU 정수 단위 때문에 retry의 fractional remaining은 내림하여 보수적으로 예약한다.

이 묶음에서 확인한 것은 구문/JSON/hash/schema뿐이다. 실제 C6 control36, C7 224 RHS/24 rows/252 comparisons, C9 Decimal70 56 RHS/고정 coefficient samples, C10 저장 plot은 아직 실행하지 않았다. N4/N5 PARTIAL_OPEN, N6/N7 PREDECESSOR_GATED, L4=false, global physical error/completion/budgetremaining/currency null과 과거 UNKNOWN_NO_ACK를 유지한다. source ZIP/이중 backup/expected-SHA publication/DAG 갱신은 root 책임이다.

## C4 runtime readback의 범위 한정 보완

부모 요청으로 C6 첫 control에 실제 worker affinity `{0}`, RLIMIT_AS soft/hard 각각512MiB, 여섯 native thread 환경변수의 값1, NumPy/SciPy import 이후 threadpoolctl의 모든 관찰 pool `num_threads=1`을 확인하는 `worker_runtime_resource_readback`을 추가했다. 이 guard가 실패하면 coefficient/fixture solve 전에 중단하고 실제 readback·실패를 보존한다. 실제 증거는 `WORKER_RUNTIME_RESOURCE_READBACK.json`이다. 따라서 control 총수는36이다. Dispatcher는 OMP_DYNAMIC=FALSE, OMP_NESTED=FALSE, OMP_MAX_ACTIVE_LEVELS=1을 설정한다. Resource admission에는 coordinator process의 VmRSS/VmSize/VmHWM/VmPeak와 cgroup aggregate의 의미를 기록한다. memory.current가 coordinator 등 기존 resident를 포함하고, owned worker는 한 번에 하나이며, 1GiB reserve가 coordinator 및 nonreclaimable growth를 덮는다는 해석을 명시한다. 물리·수치 acceptance·예산은 바꾸지 않았다. 이 보완도 작성/구문 확인만 수행했다.
