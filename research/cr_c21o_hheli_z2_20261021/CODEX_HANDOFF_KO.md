# Codex / NCP 실행 인계

이 51-case C21O pilot은 이미 샌드박스에서 완료됐다. NCP actual C21O execution은 NOT_RUN이며 완료 계산을 다시 돌릴 의무는 없다. 먼저 최신 refs·실제 원 실행 반환·백업 영수증을 확인하고 새로운 입력/미완료 작업만 실행한다.

## 복사할 작업 지시

```text
cosmosapjw-quantum/bass_cr의 research/cr-c21o-hheli-z2-sandbox-20261021을 읽고, publication/CONTENT_PUBLICATION_RECEIPT.json과 RESEARCH_DAG.json으로 최신 content/document 권위를 확인하라. 현재 unit은 research/cr_c21o_hheli_z2_20261021/이다.

원 source는 REI3b85dedce84d37b3e165da00685a8a984950aafe, C21O execution identity는 c60d734b0ed8cc7d1a147e181da27c282e3f47be90f8b0eb1d65c030faabea0f다. 기존 C21L81, C21M/N125+4, 외부NCP98/4, C21O45+6를 재실행하거나 provenance를 변경하지 말라.

PHYSICAL_CONTRACT_KO.md, REPORT_KO.md, checks/TRAJECTORY_VALIDATION.json과 독립 physics/operations/plot review를 먼저 읽어라. C21O는 prescribedUV/T, photo+CaseA_RR, 21population, ne->photonThomson의 조건부 LRS 모델이다. Atomicgas는 isotropic stress closure, massiveVlasov는 nonbaryonic, neutrinos는 collisionless다. CI/DR/CX/분자/전체핵반응/thermalUVstarsfeedback은 완료되지 않았다. global_error_bound=null을 유지하라.

필요하면 저장된 raw를 분석만 하여 새 create-only output에 그림을 만든다. NCP에서 새 IVP를 돌리기 전 affinity/cgroup quota/availableRAM/currentload/sharedlease/hostidentity를 새로 확인하라. CPU55 보호, coordinator CPU+768MiB, worker512MiB admission allowance+1GiB reserve, numericalthreads1, boundedqueue를 유지하라. --workers62는 상한이고 실제 유휴·quota·RAM·pendingcase 수가 결정한다. 다른 owner 작업을 종료/수정하지 말라. 부하 상승 때 신규dispatch를 줄여 완료 raw를 보존하라.

Source나 runtime이 다르면 기존run에 resume하지 말라. 정확한 동일 source/input/Pythonbuild/NumPy/SciPy에서만 미시작case resume가 허용된다. 실제 측정 없는 speedup/64core scaling/peakRSS 개선을 주장하지 말라. 다음 연구는 완성된 pilot의 replay보다 fullphysicalclosure의 rate/energy/UVspecification과 작은 신규검증을 우선하라. 단계마다 EXECUTION|PUBLICATION|BACKUP|DAG와 실제 hash/ACK를 기록하라.
```

## 완료 raw 분석 명령

Repository root에서 다음을 실행한다. 출력 폴더만 새로 만들며 ODE를 호출하지 않는다.

```bash
C21O=research/cr_c21o_hheli_z2_20261021
C21O_OUT=$(mktemp -d /tmp/c21o-review-XXXXXXXX)
python "$C21O/analyze.py" \
  --grid-run "$C21O/runs/c21o_grid45_v1" \
  --control-run "$C21O/runs/c21o_controls6_v1" \
  --output "$C21O_OUT/analysis"
```

Python3.12.14/NumPy2.3.5/SciPy1.17.0/Matplotlib3.10.8이 실제 실행 환경이다. Python 코드라 자체 compile gate는 없고 외부 의존성 설치만 필요하다. 실행 source를 다르게 빌드했다면 새 build 기록을 만들고, 그 환경의 실제 실행이 있기 전에는 완료를 주장하지 않는다.

## genuinely new validated grid의 실행 명령

아래 경로 세 개는 실제 site에서 확인해 치환해야 한다. 기존 45/6 입력을 복사해 재실행하는 예가 아니다.

```bash
python "$C21O/run_sandbox.py" run \
  --grid /absolute/path/to/new_validated_grid.json \
  --output /absolute/path/to/new_create_only_run \
  --workers 62 \
  --lease-json /absolute/site/path/to/current_cpu_leases.json
```

Lease formats는 `resource_control.py` docstring에 있다. Unknown/malformed 명시 lease는 빈 lease로 취급하지 않는다. 이 모듈은 read-only admission이고 전역 atomic reservation 시스템을 새로 만든 것이 아니므로 site의 기존 lease와 scheduler를 따른다. Source/input 또는 host별 path를 고치면 변경 source를 별도로 게시·검증하고 기존 원 실행 identity를 유지한다.

현재 한정된 검증에서 전체 62×62 Jacobian이 다 검사됐다고 쓰지 않는다. 62×61 columns만 검사했고 invariant u=0 column은 제외다. BDF/Radau 최대 절대 차이1.8418e-9(local scale ratio858.47), 선택 L8/L12 common radiation modes2.0780e-4를 보존하라. 작은 stress difference만으로 full hierarchy convergence를 선언하지 말라.
