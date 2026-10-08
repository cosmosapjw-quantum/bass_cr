# R3M24 로컬 통합 및 두 B2 짧은 창 bounded 실행

## 신원과 범위

`origin/repair/r3m24-audit-safety-gates-20260924`를 fetch한 뒤 remote/local exact HEAD `de2b78aa7dc7ec1f8b010e49277960bbfbafbf32`를 확인했다. 선행 R3M23은 `381b00e800bf1e7e2a78b5c0e9a56cbed5db56a5`다. 기존 primary checkout에서 branch를 전환했고 새 worktree를 만들지 않았다. 시작부터 있던 추적되지 않은 `.codex/`, `AGENTS.md`, ZIP, `docs/READBACK_POLICY.md`는 보존했다. 게시된 R3M24 solver/guard/metrics 코드는 변경하지 않았다.

이 pass는 게시된 corrective implementation의 **로컬 통합**과 한 번의 명시적 fresh GPU attempt다. R3M23 역사적 결과, 원본 B2 generation, numerical Hamiltonian/CAP/격자/box/에너지/b 및 threshold를 변경하지 않았다. full collision, preparation 재실행, finer h, representation 변경, checkpoint write, projection, B3 실행은 모두 0회다.

## 테스트와 환경

기본 `/usr/bin/python`은 Python 3.12.3/NumPy 2.4.2/SciPy 1.17.0이며 CuPy가 없어 GPU 경로에 부적합했다. canonical 과학 venv는 Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1, CuPy 14.2.0, CUDA runtime 12090, driver API 13020, RTX 3090이다. 패키지 upgrade는 0회다. `threadpoolctl 3.6.0`은 기존 user-site 파일을 repository 밖 지원 경로로 연결해 사용했고 canonical 수치 패키지 버전은 유지했다. `RUNTIME_AUDIT.json`이 실제 경로를 기록한다.

R3M24 전용 시험은 **57 passed, 0 failed, 0 skipped**다. 최초 전체 `pytest -q tests`는 `threadpoolctl` import 누락만으로 **418 passed, 4 failed**였고 로그를 보존했다. 위 기존 패키지 경로를 연결한 뒤 전체 repository 시험은 **422 passed, 0 failed, 0 skipped**다. `compileall -q scripts tests`, R3M24 CLI help 및 CuPy/CUDA import가 통과했다. 최초 Host 자원 감사 스크립트는 venv에 없는 `psutil` import로 GPU 전에 실패했으며, `/proc/meminfo`로 대체해 통과한 내역을 별도 원본 영수증으로 보존했다. 이는 과학 계산 실패가 아니다.

`source_snapshot()`은 historical `cr_repro`/`scripts`, 새 successor, B2 config, 선택표, strict CPU oracle의 실제 바이트 **60개**를 묶어 PASS했다. `bind_generation()`은 incoming/closest/outgoing의 state.npy 각각 1,008,000,128 bytes 및 manifest·seal·witness·receipt를 같은 fd 기반 read-only mmap으로 확인했고, 실행 뒤에도 원본 SHA가 유지됐다. 원격 복원은 시험하지 않았다.

## design-only와 실행 계약

Design-only 결과의 t=0 창은 `t0=-0.016665231363186095 < 0 < t1=0.033330462726373966`, `start_step=1194`다. historical closest g001152에서 42-step warmup이 필요하며, 이 파생 상태는 historical checkpoint authority가 아니다. P1/P2/P3의 0.10% 단일 성분 probability budget에 대한 sufficient raw-state L2는 각각 약 `3.8994e-5`, `4.3526e-5`, `4.4945e-5`다. 이 값은 production total-error 인증서가 아니다.

fresh `CONTRACT.json`의 SHA-256은 `0b3ca3812c0cf30c9b3c0db080901fabe9b898221bae20515100ce57fcbceb76`, computation key는 `36c68d83d3945695ed7357dd32a0e35663f3351b46e6571cf851f107edfad688`다. scope는 `REFERENCE_FOR_STRANG`, production admission은 false, reuse는 빈 목록이다. 선택된 창은 closest g001152와 outgoing g002048 각 4 B2-dt다. 새 계약의 최악 필수 비용 `4,871` kinetic matvec은 새 상한 `5,000` 안에 있다. R3M23의 옛 4,000 상한을 소급 변경하지 않는다. 창별 1,800초, 전체 7,200초, GPU 2 GiB, 호스트 8 GiB 하한을 그대로 적용했다. freeze 후 계약을 읽고 exact SHA로 한 번 승인했다.

## 실제 GPU 결과

preflight는 3 kinetic matvec/6 FFT transform으로 PASS했고, 당시 기록된 최소 GPU 여유는 `3,163,029,504` bytes, 호스트 available은 `79,876,485,120` bytes다. 단일 fresh attempt는 자동 재시도 없이 정상 완료됐다. 전체 실측은 **3,251 kinetic matvec = 6,502개 3-D FFT transform**, backend 작업 wall `762.350`초, attempt wall `763.940`초다. 두 창 모두 직후 `RESULT.json`과 `MANIFEST.json`을 create-only로 봉인했다. `FIRST_FAILURE.json`은 없다.

| 창 | local gate | matvec / FFT transform | 창 wall | CF4 n8→16 / 자체 Strang 척도 | tightening |
|---|---|---:|---:|---:|---|
| closest | Strang 척도 일치 | 1,434 / 2,868 | 343.132초 | 0.0412678% | 같은 작업이므로 생략, 독립 증거 아님 |
| outgoing | Strang 척도 일치 | 1,814 / 3,628 | 417.116초 | 0.0137612% | 다른 작업으로 실행, 차이 `6.1819e-15` |

각 창의 substep2↔4 반복은 실제 작업 fingerprint가 달랐고 사전 1% Strang 척도 한계보다 작다. 원본 배열 endpoint를 별도 보관하지 않았으므로 호스트 검증은 JSON seal·작업 trace·스칼라 gate·FFT 계수·전후 입력 SHA를 독립 재계산했고, endpoint 거리 자체를 배열에서 새로 계산했다고 주장하지 않는다. `HOST_VALIDATION.json`은 `PASS_REFERENCE_FOR_STRANG_ONLY`다. 자원 수치는 체크 시점 측정이며 연속 peak 보장은 아니다. 정확산술 Arnoldi bound는 부동소수점 오차 인증서가 아니다. R3M23과 다른 최적화 wall 차이를 production speedup으로 쓰지 않는다.

## 독립 검토

`gpt-6-astra`/`xhigh` read-only 검토는 **BLOCKER·MAJOR·조치할 MINOR 0건**으로 판정했다. reviewer는 60개 source hash, 세 generation, frozen SHA, 계산 없는 replay, 두 window seal·trace·scaling·work budget을 별도로 확인했다. 재실행이나 GPU 계산은 하지 않았고, 원본 endpoint 배열이 보관되지 않아 배열로부터 거리를 독립 재계산했다는 주장은 하지 않았다. 원문은 `INDEPENDENT_REVIEW.txt`에 보존했다.

## 과학 판정과 후속

`REFERENCE_FOR_STRANG`은 두 기존 B2 restart에서만 성립한다. `CF4_ORDER_CHARACTERIZATION`, `REFERENCE_FOR_TARGET_Q`, `GLOBAL_TIME_ERROR`는 모두 `NOT_EVALUATED`; `TIME_REFINEMENT_STILL_OPEN`, spatial/preparation/CAP/box/final-time/all-bound OPEN, b-grid `NO_GO`, production `HOLD`를 유지한다. R3M18의 B1→B2 P1/P2/P3 변화 0.2786926%/0.2591311%/0.2565637%는 여전히 0.10% screen을 초과한다. dt=.025에서 h=.25/.20 P3 gap 약 2.9527586%와 h-dt interaction 약 1.0445%도 남는다. `closest` historical 창은 실제 t=0을 포함하지 않는다.

B3는 **설계만** 준비했다. 같은 h=.20/box/CAP/target/projector/preparation bytes, `actual_dt=0.00624946176119497`, `nstep=7172`, automatic B4=false다. 128-step 봉인을 가정하면 새 state 파일 57개, 논리 용량 약 57.46 GB가 예상된다. 실제 B3 wall 및 peak VRAM은 미측정이다. P1/P2/P3 혼합 짝수차 예측 `0.0060884835814`/`0.0075857897381`/`0.0080882888941`은 반증 가능한 예측일 뿐 acceptance target이 아니다. 별도 새 계약과 B2→B3 pair, 4점 시간 모델, leave-one-out, 독립 기준/defect, 자원 ledger 전에는 B3를 실행하거나 시간 gate를 닫지 않는다.

다음 canonical action은 정확히 하나, `N1_TDL_PRODUCTION_H_PHYSICAL_T0_EVENT_WINDOW_REFERENCE_AND_ORDER_DISCRIMINATOR`다. 기존 g001152에서 비용을 계수한 warmup 후 실제 t=0을 포함하는 4-step 비교를 새 계약에서 수행하고, Strang 기준해 판정과 CF4 차수 판정을 분리해야 한다. B3 full collision은 그 뒤의 별도 승인 대상이다.
