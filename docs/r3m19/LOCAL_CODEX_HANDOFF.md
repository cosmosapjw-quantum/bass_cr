# Local Codex handoff — R3M19 이후 같은 H의 짧은 GPU 기준해와 성능

## 목표와 권위

현재 사용자 요청은 물리/수학/수치/구현 원인의 분리, 외부 원전·코드 조사, 필요한 코드 수정, CPU/RAM/GPU의 정확도 보존 성능 개선이다. 저장소 `cosmosapjw-quantum/bass_cr`, 입력 branch `cr/r3m19-fullh-diagnostics-20260923`를 fetch하고 **실행 전에 remote branch의 exact HEAD를 기록**한다. 이번 handoff 파일을 포함한 enclosing commit과 remote가 일치해야 한다. 그 exact SHA에서 별도 `cr/` 후속 branch를 만든다. main merge/force push를 하지 않는다. ZIP 수동 다운로드나 기존 대형 백업 재전송이 선행조건은 아니다.

읽을 파일: `docs/r3m19/{SCIENTIFIC_CONTRACT,REPORT_KO,LITERATURE_AND_DERIVATION_KO,CROSS_THREAD_REVIEW_KO}.md`, `FINAL_DECISION.json`, `results/R3M19/{VALIDATION,INDEPENDENT_REVIEW}.json`, `docs/roadmap/{DAG,ERROR_BUDGET}.json`. 기존 GPT-6 연구/코딩 v4 계약을 이어 쓰되 template state를 실제 이력으로 수입하지 않는다. 출처를 정확히 남기고 제한된 구현/실험은 독립 reviewer가 검토한다.

과학 기준 R3M18 `3d033eb08a0efd99257470f0fa27214f569b427a`; numerical source digest `581ff84930bb862efafdfec5d39d5b25aebf9297ce7ce45f833a5abe125b2a5b`. 판정 `TIME_REFINEMENT_STILL_OPEN`. 다음 node는 정확히 하나:

`N1_TDL_PRODUCTION_H_SHORT_WINDOW_GPU_REFERENCE_AND_WORK_PRECISION`

이 node는 기존 checkpoint에서 별도 진단을 시작한다. 새로운 full collision, B3/A2, preparation 재실행, finer h, Coulomb/FFT 공간표현 변경, CAP/box/energy/b 변경, b-grid, physical rate는 예산 0이다. 기존 `cr_repro/*.py`를 바꾸지 말고 후보를 opt-in sidecar로 구현한다. R3M19 outer coordinator repair가 과거 numerical authority를 바꾸지는 않는다.

## A. 로컬 identity와 작은 원문부터 확보

scientific interpreter는 `/mnt/sn850x2t/bass_cr_r3m11_20260921/.venv/bin/python`이다. 마지막 실측은 Python3.12.3, NumPy2.5.3, SciPy1.18.1, CuPy14.2.0, RTX3090 24GB, CUDA runtime12090/API13020/driver595.84였다. 현재 버전·모델을 직접 확인하고 변경을 기록한다. 환경을 업그레이드하거나 GPU 실패를 CPU fallback으로 덮지 않는다. 예전 Ryzen5900X/64GB 정보는 inventory 전까지 가정이다.

`/mnt/sn850x2t/bass_cr_r3m18_20260923/B2`와 R3M18 `LARGE_ARTIFACT_POINTERS.json`을 읽는다. 기존 result.json, state.json, seal/witness, preparation receipt, run receipt, final generation manifest 등 작은 JSON을 찾아 실제 경로/크기/SHA를 기록하고 후속 `results/.../intake/`에 원 bytes 그대로 게시한다. B2 result 기대값은 6029 bytes, SHA `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc`. final state 기대값은 1,008,000,128 bytes, SHA `7aff4ae72bfc28f8fb63da9aae1e7b660534d1a4a680f4930abcf3f70aff288b`. prepared initial SHA는 `ed2ff41eb7517f245d5d5a2df4ce699b607f101406c1a588d3fd4a9b522f5daa`다.

새 provenance를 과거 receipt인 것처럼 만들지 않는다. 작은 원본 누락은 `MISSING`으로 기록하고 재실행으로 보충하지 않는다. local checkpoint 검증은 remote restore 검증이 아니다. 모든 29개 대형 배열을 불필요하게 다시 해시하지 말고 진단에 실제 선택한 generation만 기존 guard로 config/frontier/seal/array identity를 검증한다.

## B. 현재 구현의 로컬 GPU 동등성과 하드웨어 계측

새 고유 output root를 만들고 다음을 위 scientific interpreter의 `-m`으로 실행한다. stdout/stderr와 exit code를 보존한다. 아래 `python`은 반드시 그 절대 interpreter로 치환한다.

```bash
python -m scripts.r3m19_performance inventory --backend cupy --out /NEW_ROOT/hardware.json
python -m scripts.r3m19_performance benchmark --backend cupy --candidate buffer_reuse --shape 64,64,96 --steps 4 --repeats 5 --max-working-mib 512 --max-seconds 30 --out /NEW_ROOT/gpu_medium
python -m scripts.r3m19_performance benchmark --backend cupy --candidate buffer_reuse --shape 128,128,64 --steps 4 --repeats 5 --max-working-mib 512 --max-seconds 30 --out /NEW_ROOT/gpu_larger
```

CPU benchmark도 같은 64,64,96 shape에서 native buffer와 SciPy workers 1/4를 순차 측정한다. 실제 physical-core/affinity/quota cap이 4를 허용할 때만 4를 사용한다. `--backend numpy --candidate scipy_fft_workers --fft-workers 4`가 명시적 CPU 비교이며 production fallback은 아니다. 실제 GPU test를 포함한 새 R3M19 관련 시험을 실행한다. 웹 결과의 GPU 1 skipped를 그대로 PASS로 수입하지 않는다.

microbenchmark hard cap은 ≤2^20 points, 8 steps, 10 repeats, 1GiB, 60초다. cap을 풀어 이 script로 생산 격자를 실행하지 않는다. state 상대 L2≤5e−13, norm 상대차≤2e−13의 등록된 구현 parity를 유지한다. GPU events/synchronized wall/host enqueue를 구분하고 timed region에서 memory query나 host transfer를 하지 않는다. 초기 copy/reset·준비·검산·projector·checkpoint 시간은 step 시간 밖임을 명시한다. FFT cache/pool counter와 lifetime RSS를 실제 peak 절감량처럼 더하거나 해석하지 않는다.

이 단계를 마치면 실제 장비에서 가장 빠른 **검증된 후보**를 말할 수 있다. 모든 shape/전체 collision에 대해 최적이라고 말할 수는 없다. 이번 결과만으로 frozen production backend를 교체하지 않는다.

## C. matrix-free full-H action: 구현 및 작은 독립 시험

현재 dense diagnostic을 큰 격자로 확대하지 않는다. 새 sidecar에서 `A(t)ψ=−i[T_hψ+(V_T+V_P(t))ψ]−Wψ`를 FFT matvec로 구성한다. 같은 FFT 주기 경계, cell-center, complex128, CAP rate, actual time을 유지한다. CAP 때문에 Hermitian 전용 Lanczos를 무검증 적용하지 않는다. 비Hermitian Arnoldi 또는 검증된 scaling/Taylor action 등 실제 구현·메모리·inner error를 밝히는 방식을 택한다. 공식 API가 시간 의존 H(t)를 자동 해결한다고 가정하지 않는다.

CF4는 두 시점/두 **전체 generator exponential action**을 사용한다. 내부를 다시 2차 Strang으로 바꾼 뒤 4차라고 부르지 않는다. 각 action의 inner error, 외부 timestep, CAP 오차를 별도 기록한다. scalar action tolerance는 global state/observable certificate가 아니다.

새 구현은 먼저 R3M19 dense H/독립 DOP853의 64점 케이스와 임의 비Hermitian constant generator, CAP off/on, v=0/±v, 직사각형 격자에서 비교한다. inner tolerance를 최소 한 번 강화하고 고정 horizon timestep refinement도 별도로 한다. independent action 또는 ODE repeat의 차이가 비교하려는 최소 오차의 1% 미만이어야 해당 사례를 oracle-resolved라고 쓴다. 필요시 DOP853 max_step을 줄이는 검사를 **새로 실행**한다; R3M19는 tolerance repeat만 실행했다. R3M19 refined h=.20 CF4의 oracle gate FAIL을 소급 PASS로 바꾸지 않는다.

tiny stage caps는 기존 fullh 도구의 ≤512점, ≤64steps/method, ≤20,000RHS/oracle, horizon≤2를 유지한다. 작은 레벨에 대한 새 code tests를 먼저 통과하고 독립 검토 후 D로 진행한다. 구현을 계획만 했으면 IMPLEMENTED나 RUN으로 기록하지 않는다.

## D. 같은 production h/box의 짧은 구간: 실행 전 계약

B2의 보존된 generation 중 incoming, closest approach, outgoing을 대표하는 **최대 3개**를 실제 times/zp로 선택하고 선택 규칙·목록·SHA를 계산 전에 JSON으로 고정한다. 원본 checkpoint는 read-only다. 초기 psi를 다시 준비하거나 보간하지 않는다. 각 구간의 길이는 B2 실제 dt `0.01249892352238994`의 **4배 이하**, 종료시각은 B2 전체 종료보다 이르거나 같아야 한다. 같은 checkpoint에서 시작해 같은 horizon을 비교한다. 이 짧은 restart는 새 full collision이 아니며 asymptotic P1/P2/P3를 다시 계산한 것으로 세지 않는다.

각 구간에서 frozen Strang과 검증된 buffer 후보의 parity, Strang dt/dt2/dt4, full-H midpoint/정확 평균/CF4를 비교한다. 방법 수가 예산을 넘으면 최초 1구간에서 원인을 구분하는 최소 세트를 우선하고 생략을 기록한다. CF4 dt refinement와 inner-action refinement를 서로 분리한다. raw-vector decomposition과 Gram 교차항은 모든 중간 상태를 동시에 VRAM에 보관할 필요 없이 검증된 순차 staging으로 계산할 수 있다. global phase 정렬은 별도 metric에만 쓴다.

생산 격자 실행 전 자원 preflight를 새로 작성한다. 63M complex128 한 벡터≈.939GiB이며 Arnoldi m개 basis는 m배에 static arrays/FFT workspace/temporary가 추가된다. RAM/VRAM 중복 상주를 모두 계산한다. GPU free≥2GiB와 available host RAM≥8GiB를 남기는 계획, workspace/pool 예상, 실제 allocation probe가 동시에 만족해야 한다. 고정 예산은 **총 GPU wall≤2시간, 구간당≤30분, 전체 FFT matvec≤4000, GPU 전파 job 1개**다. 측정된 속도로 이 예산 안에 inner/outer reference가 가능한지 먼저 계산한다. budget은 OOM 보장이 아니므로 관측치를 함께 기록한다.

초기 1구간에서 메모리 부족, NaN/Inf, parity 실패, inner reference 미해결, 예상비용 초과가 나오면 해당 큰 실행을 중지하고 원인/최초 실패를 보존한다. tolerance 완화·새 checkpoint 무제한 선택·CPU fallback·자동 retry·새 full collision으로 넘어가지 않는다. basis memory 때문에 불가능하면 구조적 resource blocker와 검증 가능한 다음 action 하나를 반환한다.

이 단계는 **조건부 실행 계약**이다. B와 C의 accuracy gate 및 D의 preflight가 통과한 경우에만 이미 허용된 짧은 구간을 실행한다. 매번 사용자 허락을 다시 묻는 절차가 아니다.

## E. 성능 판정과 다음 과학 판정

GPU propagation/FFT/potential, projection, host transfer, hash/write의 시간을 분리한다. 원래 B2 전체 collision timing이 없으므로 속도 개선을 가상의 기존 전체시간에 나누지 않는다. 단순 utilization 대신 같은 실제 상태오차에서 wall time/FFT matvec/RAM/VRAM을 비교한다. 짧은 구간 성능을 전체 collision 수치로 외삽하면 반드시 모델 추정으로 표시한다.

GPU에는 전파·큰 배열을 두고 CPU는 작은 분석·검증을 맡긴다. 전체 CPU/RAM/GPU 점유율을 강제로 높이기 위해 여러 대형 job을 동시에 실행하지 않는다. FFT workers와 BLAS 중첩을 제어한다. 향후 checkpoint overlap은 immutable staging, 기존 generation 검증 완료 후 다음 chunk라는 순서, crash 복구를 먼저 입증해야 한다. 이 node에서 retention/backup 정책을 성능 핑계로 완화하지 않는다.

관측된 오차를 split/time quadrature/time ordering/inner action/roundoff/IO implementation으로 가능한 범위만 분리한다. 작은 구간이 production 전체 시간예산을 인증하지는 않는다. CF4가 같은 error에서 빠르면 차후 **별도 한 collision**의 propagator 선택 근거가 될 수 있고, buffer reuse만 이득이면 기존 시간법의 성능 개선을 우선할 수 있다. 이번 예산 안에서 그 collision을 실행하지 않는다.

최종 값은 scientific `TIME_REFINEMENT_STILL_OPEN`을 유지하되 이번 구간의 결과에 따라 다음 canonical node **정확히 하나**를 갱신한다. 시간·공간·CAP·preparation·all-bound·b integration 각 gate를 분리한다. physical model이나 total cross section 정확도를 tiny/short-window 검증에서 추론하지 않는다.

## F. 보존·배송·마지막 응답

actual input SHA/환경/설정/명령/최초 실패/시험/정확도·성능표/독립검토/한 다음 node를 repository-native 파일로 남긴다. 새 결과는 새 이름으로 create-only 저장한다. 기존 R3M15–R3M19 result bytes를 수정하지 않는다.

작은 source/tests/raw JSON/report/manifest는 전용 branch에 commit/push하고 원격 exact HEAD를 확인한다. 새 대형 artifact가 있다면 기존 사용자가 지정한 Dropbox dossier 경로와 Drive dossier folder의 **새 대상**에만 dual backup한다. 기존 938MB R3M18 archive와 29개 checkpoint를 반복 업로드하지 않는다. provider ACK/objectID/size/hash를 얻은 수준대로 기록한다. upload verification, raw readback, local checkpoint validation, restore는 별도 등급이며 미실행 restore는 `RESTORE_NOT_TESTED`다.

최종 응답에는 branch/exact HEAD/R1 확인, 실제 새 full collision 수(0), 짧은 구간 수와 GPU 실행 수, 시험 pass/skip, GPU 및 CPU 실측 속도·정확도, 과학적 판정, backup scope/tier, 다음 한 canonical node를 적는다. 완료되지 않은 구현이나 미실측 속도를 완료로 보고하지 않는다.
