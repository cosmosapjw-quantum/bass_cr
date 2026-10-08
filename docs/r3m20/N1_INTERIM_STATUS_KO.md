# N1 중간 실행 상태 — 2026-09-23

입력 `cr/r3m19-fullh-diagnostics-20260923`의 fetch 후 remote HEAD는
`83dc465443f8b4fdf7c720304118207cc5267dfc`로 확인했다. 이 HEAD에서
`cr/r3m19-n1-gpu-short-window-20260923` 작업 branch를 분리했다.

보존된 B2의 작은 원본 13개(16,672 bytes)를 `results/R3M20_N1/intake/`에
원문 bytes 그대로 복사하고 source/copy 해시를 검증했다. `result.json`은
6,029 bytes, SHA-256 `f73ebb98708aabe48a77466bca8d0c108d0983d83cb8516db76bbac6c9993edc`로
기대값과 일치한다. 대형 state/preparation/generation 배열은 복사하거나
재해시하지 않았다. 이 확인은 local provenance이며 remote restore 시험이 아니다.

현 장비 실측: Ryzen 9 5900X, affinity 내 물리 12코어, 사용 가능 RAM
84,539,527,168 bytes, RTX 3090 24 GiB, inventory 시 GPU free
24,895,881,216 bytes. Python 3.12.3, NumPy 2.5.3, SciPy 1.18.1,
CuPy 14.2.0이다. 기존 scientific interpreter에 없는 `threadpoolctl`
3.6.0은 이미 설치된 모듈의 동일 bytes를 별도 지원 경로로 노출했고,
기존 `libcufft.so.11`을 loader 경로로 노출했다. 오류 원문과 각 재시도는
`results/R3M20_N1/performance/`에 보존했다. 과학 패키지는 업그레이드하지 않았다.

동일 상태·격자·CAP·actual dt의 4-step/5-repeat microbenchmark에서
GPU buffer 후보는 64×64×96에서 wall 비율 1.02495, 128×128×64에서
0.99965(기준/후보)를 기록했다. 각 state 상대 L2는 각각
7.81e-16/7.85e-16으로 parity PASS다. CPU 64×64×96의 native buffer,
SciPy FFT 1/4 worker 비율은 각각 1.09037/1.56182/2.09368이고
state 상대 L2는 6.44e-16이다. 실제 GPU 시험은 20 passed, 0 skipped다.
이는 setup/reset/검산/projector/checkpoint를 제외한 microtrajectory이며
63M점 또는 전체 collision 성능은 `NOT_MEASURED`다.

matrix-free full-H sidecar 외부 검증 시험은 작성했고 예상 첫 red(모듈 부재)를
보존했다. 현재 CUH-G opportunity는 원래 checkout에 묶여 별도 branch
worktree에 대한 실행을 `ROUTING_OPPORTUNITY_MISMATCH`로 거부한다. 같은
opportunity의 Host fallback은 `PRE_ADMISSION_STATE_REQUIRED`다. 이
라우팅 실패를 numerical failure 또는 budget 소진으로 해석하지 않는다.
sidecar 구현, 작은 독립 oracle, 큰 격자 allocation probe, B2 짧은 구간,
독립 검토, 원격 게시와 dual backup은 아직 실행하지 않았다. 새 full
collision과 preparation 재실행은 0회다.

과학 판정은 `TIME_REFINEMENT_STILL_OPEN`, production은 `HOLD`, b-grid는
`NO_GO` 그대로다. 다음 canonical node는 정확히 하나:
`N1_TDL_PRODUCTION_H_SHORT_WINDOW_GPU_REFERENCE_AND_WORK_PRECISION`.
