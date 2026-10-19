# C21G optical-depth reference 제어 확장

## 변경 계약

원본 `reference_tau.py` SHA256:
`d34209d1cd1a07f120c2e2c22b797a76c7420929c022df04135270a874172e1d`

최종 변경본 SHA256:
`714c40a4e3a0577784e6a754b95cdb34b247cb2e529953a375c74a43efafc3e0`

첫 GREEN 단계의 중간 변경본 SHA256은
`1f53471c024bd9a96a6bc4896dc39332408df3a64b7616fde8fce29fc3309502`로 별도 보존되어 있다.

원본 실행·의존성 manifest는 수정하지 않았다. 새 변경본의 identity는 상위 C21G manifest에서 따로 기록한다.

```python
run_reference_tau(
    fixture,
    provider,
    rtol=2e-10,
    atol=2e-13,
    max_cohorts=128,
    max_evaluations=200000,
    max_step_divisor=8.0,
)
```

`atol`은 양의 유한 scalar 또는 **full state 길이 M+19**인 1차원 벡터다. 벡터는 원래 순서인 optical depth M개, gas 4개, ledger 15개에 대응한다. 입력 벡터를 복사하며, Y=0에서는 기존 state/Jacobian 축소와 동일하게 M+1, M+2 위치의 He fraction tolerance 두 개만 제외한다. Full vector와 solver에 실제 전달된 reduced vector를 모두 결과에 기록한다.

`max_step_divisor`는 1 이상의 유한 scalar다. 각 event interval의 x=ln(a) 폭을 이 값으로 나눈 것이 max_step이다. 기본값은 기존의 interval/8과 같다.

`rtol`은 양의 유한 scalar이고, 설치된 SciPy 1.17.0의 실제 `validate_tol` 구현에서 확인한 `100*float64_eps = 2.220446049250313e-14` 이상이어야 한다. 작은 요청을 다른 값으로 바꾸는 SciPy 동작 앞에서 `RADAU_RTOL_BELOW_FLOAT64_FLOOR`로 명시적 거절한다. Array shape·비유한/비양수 tolerance·max-step 입력 오류도 provider 호출 전에 DomainError를 반환한다.

## 추가 진단의 의미

기존 top-level `nfev`, `rhs_evaluations`, schema V1을 유지한다. 새 `solver_diagnostics`는 segment마다 x0/x1, SciPy nfev/njev/nlu, accepted_steps, min/max x-step, 요청한 max_step, 실제 RHS callback 수, 종료 status/message를 기록한다. 전체 합계도 따로 기록한다.

각 segment의 `accepted_grid_sha256`는 initial point와 모든 accepted endpoint를 포함한 `solution.t`를 C-contiguous little-endian float64로 인코딩한 바이트의 SHA256이다. 요청 max_step이 달라도 실제 grid가 같을 수 있으므로, bound 설정 자체를 독립 mesh 증거로 사용하지 않는다. 후속 분석은 grid hash를 직접 비교할 수 있다. Max-step active 여부를 추정하는 boolean은 추가하지 않았다.

`tolerance_contract.endpoint_sampling_policy`는 기존 provider epoch·opacity·H 평가점의 `xx=min(max(x,lo+1e-9*(hi-lo)),hi-1e-9*(hi-lo))` 정책을 기록한다. 해당 식과 상태·integrator grid의 x는 원래 코드대로 유지한다.

`rhs_evaluations`는 finite-difference Jacobian을 구성하는 실제 callback까지 포함한다. 따라서 SciPy가 반환하는 nfev와 같다고 가정하지 않는다. 새 zero-micro fixture에서도 191 reported nfev와 341 실제 callback을 관측해 이 구별을 검사했다.

`tolerance_contract.coordinate_blocks`에는 다음 단위를 기록한다.

| 좌표 | 허용오차의 단위 |
|---|---|
| tau | 무차원 |
| x_HII, y_HeII, z_HeIII | 각 원소에 대한 species fraction |
| w | eV / total H nucleus |
| photo, CI, RR, DR ledger | events / total H nucleus |
| escape, CMB, photon work, gas work, heat ledger | eV / total H nucleus |

이 값은 적분기의 좌표별 local error scale이다. Global state 오차나 photon population 오차의 상한으로 해석하지 않는다.

## 실제 RED → GREEN 기록

| 단계 | UTC 시작 | 실제 unittest exit | unittest 결과 | process wall |
|---|---|---:|---|---:|
| RED | 2026-10-19T08:08:53.575701+00:00 | 1 | 9 tests, failures=1, errors=21 | 1.417183298 s |
| GREEN | 2026-10-19T08:10:51.000542+00:00 | 0 | 9/9 PASS, unittest 0.347 s | 1.197796508 s |
| GREEN_GRID | 2026-10-19T08:14:33.523546+00:00 | 0 | 동일 9 tests PASS, unittest 0.451 s | 1.403449995 s |

첫 RED/GREEN 두 실행의 test source SHA256은 모두
`6a3b515db6d7db35a21fe1d725f787bde53a8e1c8b411e48c020a0dd6e0dd3ab`다.
원본 scalar 결과와의 호환성 검사는 RED 단계에서도 통과했다. 따라서 9개 모두가 먼저 실패했다고 표현하지 않는다. 새 vector·Y=0 vector 전달·입력 거절·step 제어·diagnostic 요구가 기존 source에서 실패하고 변경본에서 통과한 기록이다.

독립 검토의 구체적 후속 요청으로 기존 두 test method에 실제 grid-byte hash와 scalar/vector grid hash 안정성을 추가했다. 이 후속 test source SHA256은 `fd51ce0b7543b228897eeec303519e170d851ca017f8d2158854854f96d43fed`이며, 해당 실행을 `GREEN_GRID.json`과 log에 새로 기록했다. 이 진단 추가를 별도 red-first 실행이라고 주장하지 않는다.

실행 명령은 `RED.json`, `GREEN.json`의 `command_argv`에 정확히 보존했다. 실행 entry point는 아래와 같았다.

```bash
python3 c21g_work/reference_patch_tests/record_test_run.py RED
python3 c21g_work/reference_patch_tests/record_test_run.py GREEN
python3 c21g_work/reference_patch_tests/record_test_run.py GREEN_GRID
```

최종 checkout에서 focused tests만 실행할 때:

```bash
C21F_SOURCE_DIR=/absolute/path/to/research/cr_c21e_event_native_20261018/src \
python3 -m unittest discover -s /absolute/path/to/reference_patch_tests \
  -p test_reference_patch.py -v
```

`record_test_run.py`의 RED/GREEN 기록은 create-only다. 일반 재실행에는 위 unittest 명령을 사용한다.

## 확인한 범위

- 원본 scalar default의 작은 zero-micro fixture 물리 출력은 변경 후 **완전히 동일**했다. 입력 fixture digest는 `31a79cf722cc06cfab3cae6a68cbf12a841f6e5f5ab4b67e98013cb472573705`이다.
- Uniform full-state atol vector와 같은 scalar의 gas·photon·tau·ledger·수지 출력은 동일했다.
- Y=0의 full vector는 실제 solve_ivp 전달 지점에서 두 원소가 제거되었고, 모든 provider callback의 He fraction 두 개가 정확히 0이었다.
- 잘못된 길이/차원·NaN·infinity·0·음수 atol과 잘못된 rtol·max-step 입력을 거절했다. 양의 rtol floor 경계는 허용했다.
- max_evaluations=1에서 기존 evaluation-budget StepRejected를 확인했다.
- 새 과학 source 변경은 `reference_tau.py` 하나다. RHS 식, photo/nonphoto 소유권, birth 처리, gas domain 검사, clipping 정책, native Rust, discrete solver를 수정하지 않았다.
- 기존 56개 검사와 native matrix는 재실행하지 않았다. 이 검증은 작은 non-native 실행 계약과 default 보존에 한정된다. 실제 native tolerance ladder 및 fine refinement의 물리·수치 판정은 후속 실행 의무다.

## 검토 상태

작성자 자체 code/contract 검토: COMPLETE_SCOPED. 독립 검토·게시·백업은 상위 연구 단위가 실제 영수증과 함께 갱신한다.
