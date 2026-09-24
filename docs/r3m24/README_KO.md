# R3M24: 감사 기반 안전 실행 및 검증 판정 수리

기준은 `cr/r3m23-b2-cross-window-work-precision-20260923`의
`381b00e800bf1e7e2a78b5c0e9a56cbed5db56a5`다. 이 변경은 새 opt-in 실행 경로다.
기존 `cr_repro`, R3M23 이하 scripts, 과거 계약, 결과, seal, checkpoint는 변경하지 않는다.
**production HOLD / GLOBAL_TIME_ERROR 미검증 / b-grid NO_GO는 유지한다.**

## 구현한 수정

- `r3m24_guard.py`: 선택된 manifest의 실제 SHA, 구성·done·시간·NPY extent를 확인한다.
  state를 한 번 stream-hash한 동일 fd로 read-only mmap하고, 전송 전후 inode/size/mtime/ctime를
  확인한다. 같은 크기 변조, 경로 교체, metadata 변조, symlink를 거절한다.
- `r3m24_execution.py`: GPU 이전 exclusive output 예약, 완결 결과의 무계산 replay,
  창별 RESULT+MANIFEST의 fsync/create-only 저장을 구현한다. 둘째 창 실패가 첫째 창을
  지우지 않는다. 재사용은 새 계약의 명시적 sealed-window 포인터로만 허용한다.
  cleanup 오류가 최초 실패를 덮거나 잘못된 COMPLETED를 만들지 않게 한다.
- `r3m24_gpu.py`: 동결된 Strang/CF4 계산 함수를 사용하는 실제 opt-in CuPy 어댑터다.
  inner tightening이 같은 stopping index를 줄 때 실행을 생략하고 독립 증거로 세지 않는다.
  substep 변경 검사는 필수 작업으로 예산에 넣고, 모든 실제 Arnoldi 차수와 matvec를 기록한다.
- `r3m24_metrics.py`: 실제 작업 동일성 판정, REFERENCE_FOR_STRANG 전용 gate,
  projector 확률오차의 안정적인 state-budget 역산, t=0/B3 design-only 산출을 제공한다.
- `r3m24_cross_window.py`: config의 실제 값, transitive 원본 소스, successor source,
  Python/NumPy/CuPy/SciPy 버전, 입력 선택을 결합한 계약을 만든다.
  runtime도 reuse key에 포함되므로 다른 환경의 결과를 같은 계산으로 묵시 재사용하지 않는다.

state-file mmap은 직접 강제 unmap하지 않는다. 남은 NumPy view와 exception traceback이
mapping을 참조할 수 있으므로 NumPy 수명 관리에 맡긴다. 개발 중 발견한 이 문제의
subprocess SIGSEGV 재현과 수정 전후 로그를 보존했다.

## 실행 방법

repository root에서 아래 명령을 사용한다. 기존 R3M23 진입점을 직접 재호출하지 않는다.
`freeze`는 사용자 로컬의 기존 B2 generation 경로를 읽으므로 해당 배열이 있어야 한다.
출력의 부모 폴더를 먼저 준비하고 각 출력 파일/attempt 경로는 새 경로를 지정한다.

```bash
python -m pytest -q tests/test_r3m24_safe_execution.py
python -m scripts.r3m24_cross_window design --out /absolute/fresh/design.json
python -m scripts.r3m24_cross_window freeze --contract /absolute/fresh/contract.json
```

`design`은 최근접 시각을 실제로 포함하는 4-step 창과 warm-up step 수,
B3의 `nstep=7172`, `actual_dt=dt_B2/2`, P1/P2/P3 state-budget을 계산한다.
**이는 GPU/full collision 실행 권한이나 수렴 PASS가 아니다.** B3 dispatcher는 없다.

새 계약을 검토하고 실행을 명시적으로 승인한 뒤에만 다음을 사용한다.
`--approve-sha256`에는 freeze가 출력한 정확한 파일 SHA-256을 넣는다.

```bash
python -m scripts.r3m24_cross_window run \
  --contract /absolute/fresh/contract.json \
  --approve-sha256 <EXACT_CONTRACT_FILE_SHA256> \
  --out /absolute/fresh/attempt
```

완결 attempt의 같은 계약 재호출은 저장된 결과 무결성을 확인하고 반환한다.
불완전 attempt는 자동 재시도하거나 덮어쓰지 않는다. 성공한 창만 재사용할 때는
`freeze --reuse-window /old/attempt/windows/closest`로 새 계약을 만들고
새 output으로 실행한다. 소스·입력·설정·runtime key가 다르면 재사용을 거절한다.
이 경로도 기존 두 짧은 창의 Strang-scale 비교만 허용한다. t=0 새 창/B3는 별도 계약이다.

## 자원과 수학적 한계

원래 R3M23의 4,000 matvec 계약은 그대로다. 이 새 템플릿은 두 창의 필수 반복을
최악 비용에 포함하여 `3 + 2*(160+34+1600+640) = 4,871` matvec를 요구하고,
별도로 승인할 새 상한을 5,000으로 둔다. 충분하지 않은 예산은 GPU 이전 거절하며
독립검증을 optional로 바꾸지 않는다. 시간상한은 전체 7,200초/창 1,800초,
reserve는 GPU 2 GiB/host 8 GiB다. GPU 커널은 강제 선점하지 않으므로
wall 검사는 cooperative boundary 검사이지 모든 순간의 hard realtime 보장이 아니다.

정확산술 Arnoldi 상계는 부동소수점 인증서가 아니다. 강화 반복 생략은 기존 작업의
재사용이며 새 정확도 실험이 아니다. local reference gate는 CF4 차수, 최종 채널 정확도,
전체 충돌 시간수렴, all-bound completeness, 공간수렴 또는 production을 승격하지 않는다.
MGS reduction/synchronization의 세부 성능분해, 새 채널/defect 저장, residual-driven
preparation, 전체 B3 실행과 공간 표현 변경은 이번 구현 범위에 포함하지 않았다.

입력보호는 동시 authorized writer가 없는 로컬 POSIX 환경을 전제로 한다.
일반적인 in-place/path 변경을 검출하며 hostile filesystem/privileged attacker에 대한
보안 인증은 아니다. host/GPU 여유는 검사 시점 값이고 절대 peak 보장이 아니다.

## 실제 검증과 미실행 항목

새 소스 5개와 CPU 회귀시험 파일 1개에 대해 **57 passed, 0 failed, 0 skipped**,
`python -m compileall -q scripts tests` 및 CLI help 종료코드 0을 확인했다.
검증에는 실제 작은 NPY/manifest 입출력과 coordinator test double을 사용했다.
새 CuPy 어댑터의 production array 실행 결과로 해석하지 않는다.

이 세션의 환경은 Python 3.13.5/NumPy 2.3.5/pytest 9.0.2다.
GitHub connector로 기준 소스를 읽었지만 container의 Git DNS 실패로 전체 checkout은
구성하지 못했다. 따라서 **기존 365개 통합시험, frozen-kernel 통합실행, CUDA/GPU,
B2 대형 배열 복원, B3 full collision은 NOT_RUN**이다. 기존 PASS를 이번 결과로 재사용하지 않는다.
독립 reviewer는 실행하지 않았고 검토 상태는 OWNER_SELF_REVIEW다.

`evidence/r3m24/TEST_RECEIPT.json`에 시험 범위와 실제 소스 byte/Git blob identity를,
`FINAL_PATCH_SUITE.txt`에 최종 patch-only pytest 출력을 기록했다.
Git에는 `RED_LIFETIME.txt`, `RED_RUNTIME.txt`의 최초 실패 원문 및 `TEST_LOG_INDEX.json`의
전체 로그 해시를 남긴다. 모든 원본 red/green 로그의 `TEST_LOGS.json.gz`와 원문은
별도 전달 파일 `BASS_CR_R3M24_REPAIR_AND_TEST_LOGS_20260924.zip`에 보존한다.
이 companion archive는 Git tree에 넣었다고 주장하지 않는다.
업로드된 blob SHA와 테스트한 로컬 blob SHA를 대조하여 게시하며,
원격 branch/commit/tree 확인은 R1 게시 검증이다. 대형 배열 restore 검증과는 다르다.

다음 최소 조치는 로컬 exact checkout에서 새 시험과 기존 `python -m pytest -q tests`를
실행하고, CUDA 로딩 및 imported source 경로를 확인하는 것이다. 기존 성공 창을 다시
계산하는 것보다 다음 물리 판별 계약의 t=0/B3 적용을 우선한다.
