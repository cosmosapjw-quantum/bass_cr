# C22D 독립 preflight review

판정: **PASS_SCOPED_PREFLIGHT**. 2026-10-22 15:08 UTC에 확인한 changed source와
아래 유한 근거에서 실행을 막는 미해결 오류를 발견하지 않았다.
이는 새4개 궤적의 결과 승인이나 원자 rate의 물리 정확도 인증이 아니다.

검토자는 C22D model/runner, CI provider, optimized kernel의 작성자가 아니다.
현재 단계의 검토는 코드 직접 읽기, AST/JSON 파싱, 저장된 scalar·boundary receipt의
독립 산술 재구성이다. **Science module import0, RHS call0, ODE0, 기존 계산 재실행0**이다.

## 1. 검토한 정확한 source

| 파일 | SHA256 |
|---|---|
| model.py | f270c8a2d926f9c318268483b869cfcac771162023ab44b09a4eca12a819bec5 |
| CONTRACT.json | 4022fc0c2e72d9cf18d9064f42170b524050f0eebe35b7b8db6d080880e9be4b |
| run_pilot.py | 9694aba9e25af05c01aa3fe6a59e19aace2c846c35e56de4032505e40bfdd129 |
| ci_finite.py | 859cdf616ffa165c9fb3c3372d2202f5449e4b9a74a289a725fe456e26eb55b2 |
| optimized_kernel.py | f0451a7349fa4682d17435336a3d3c413409fdbf442b44330eb008d33f7a8bf6 |

Source root:
`resume_c22c_20261022/recovery/restored_c22b/repository/research/cr_c22d_cold_ci_20261022`.
기존 A/B/C에서는 새 코드가 실제로 위임하는 fields/events/energy/summary/transition,
projection/lift 경로만 읽었다. 과거 campaign 전체 재감사는 하지 않았다.

## 2. 물리·구현 연결

CI의 physical abundance 증가분을
`δY = r(-e_HI + e_HII)`라 두면 nuclei 합은0, 자유전자 증가량은r,
전체 기체 입자수 증가량도r이다. 코드의 scaled-coordinate 증가분은 해당
`atomic.scales`로 한 번 나누어 이 사건률을 구현한다.

단일 registry에서 binding 차이는χ=13.6058eV이고
`δU=-χr`, `I·δY=+χr`이므로 CI는 kinetic↔binding만 교환한다.
CI에 별도 escaped-energy source를 붙이지 않는다. 온도는
`T=U/(1.5kB N)`이므로 직접 미분하면
`δTprime=-(2χ/(3kB)+T)r/N`이다. 코드가 U와 조성을 함께 진화하기 때문에
입자수 항이 자동으로 한 번 들어간다. 별도 중복 보정은 없다.

D summary의 charge ledger는
`ne/Href + C_RR - C_PI - C_CI - ne_initial`로 교정되었다.
Photon number ledger에는 CI가 들어가지 않는다. 두 식은 기존 C summary에서 얻은
원자·광자 배열을 사용하되 최종 D charge 진단을 덮어써 올바른 사건 장부로 돌려준다.

`AlignedAtomicView`는 frozen network를 감싸는 wrapper이다. A.events가
`self.atomic.provider.sigma`를 직접 호출하므로 새 HI support가 실제 PI에 적용된다.
원래 shared provider/configuration은 바꾸지 않는다. 새 threshold는 copy,
binding은 fresh array이며 두 배열을 read-only로 둔다. Fresh A→B→C의
initial_energy는 bottom-up으로 다시 계산하고 D의 energy reference도 그 뒤에 계산한다.
Bath/excitation/CI counter를 energy에 중복 더하지 않는다.

13.6058eV는 **CCC source convention에 정렬한 model support**다. 정확한 physical
H1 ionization threshold를 개선했다는 주장을 하지 않는다. 기존 PI shape/energy axis,
RR number/capture fit을 유지한 근사임이 contract에 드러난다. Milne/LTE 및 finite-mass
isotope consistency는 OPEN이다.

모든21 populations를 출력하며 solver에서 제거하는 것은 선언된 exact-zero n/T
세 좌표뿐이다. 비영 입력을 project로 지우지 않고 거절한다. H1-only CI를 추가한 뒤
H1/D ionization-fraction quotient를 사용하지 않는다.

Optimized RHS는 같은 `(eta,y)`에서 방금 계산한 fields만 공유한다. 온도 반올림,
다른 state의 rate cache, 허용오차 변경, passive ledger 제거는 없다.
기본 positive-moment path는 원래 항별 연산 순서를 유지하며 Horner candidate는
production 경로에 채택되지 않았다. 실제 speedup 수치는 별도 optimization receipt의
측정 범위에 속한다.

## 3. 발견한 문제와 해결

### F1. 후속 segment 준비 실패에서 partial raw 보존 누락 — 해결

원 runner에서 endpoint_inset 및 overlap guard가 IntegrationFailure를 만드는
try 밖에 있었다. 후속 segment의 준비 실패가 generic ValueError로 빠지면 이미
끝난 segment의 accepted points가 실패 raw 파일에 남지 않는 경로였다.

Root의 수정은 준비 실패도 현재 accepted arrays, 실패 segment 시작 상태,
완료 segment receipts를 가진 IntegrationFailure로 전환한다.
직접 diff를 읽었으며, physics RHS나 solver tolerance의 변경은 없다.

실제 fault-injected receipt는 다음을 구분한다.

- RED: 이전 driver28546349…, fake_solver1회 후 inset3번째 호출에서 실패,
  prior points 보존 누락.
- GREEN: 수정 driver9694aba9…, 같은 주입에서 **accepted points2개와 segment1개 보존**.
- 두 검사의 배열은 test stub이고 **physical ODE0**이다.

### F2. 작은 CI 증가분의 부적절한 상대오차 predicate — 독립 진단 후 명시 교체

최초 light check는 **34/36 PASS, 두 검사 FAIL**로 그대로 남는다.
문제 검사는 큰 전체 RHS 두 개의 차이로 얻은 작은 CI 증가분에
5e-12의 CI-relative 오차를 요구했다.

Root가 보존한6개 point diagnostic의4개 CI 좌표씩, 총24개에 대해
`Fraction.from_float`로 실제 binary64 입력을 정확한 유리수로 읽었다.
독립 결과는 다음과 같다.

- **24/24**에서 observed don이 정확한 유리수 `off+expected`를 binary64로
  올바르게 round한 값과 bitwise 일치.
- Addition error는 최대 **0.5 ULP**.
- **24/24**에서 후속 `don-doff` subtraction 자체는 exact.
- 부모가 기록한 CI-relative 오차6개가 모두 그대로 재현됨.

따라서 더 정확한 설명은 “큰 baseline에 작은 CI를 더할 때 생긴 정상 rounding을
후속 차감이 노출했다”이다. UV를0으로 바꾸어도 expansion 등 다른 baseline이 남아
같은 문제가 나타날 수 있다. 실제로8000K UV0 사례도 옛 predicate를 약간 넘는다.

원래 두 predicate를 조용히 PASS로 바꾸거나 유리한 state만 고르지 않았다.
Contract의 `light_check_correction`과 `LIGHT_CHECK_ACCEPTANCE.json`이
원실패를 보존하면서 exact-input addition proof와 full-RHS scale 검사를 명시적으로
연결한다. 물리식, source interpolation, ODE tolerance의 변경은 없다.
V1 validator는 이 실패 이력을 재현하는 자료이므로 해당2개 실패를 현재 물리식의
새 실패로 다시 해석하지 않는다.

독립 계산과 입력·코드 hash는 `SAVED_ADDITION_REVIEW.json` 및
`check_saved_addition.py`에 있다. 이 검토는 이미 저장한 수치만 사용했고
새 RHS나 ODE를 호출하지 않았다.

### F3. V1 validator source identity — 보완

원 RESULT에는 model/CI/kernel hash만 있어 검사 자체의 버전 연결이 부족했다.
검토자가 읽은 validator7734bytes SHA
`43ab6caa3fa4fc374de5d6e686418388c0a8efcf03e1908272e0f8f5aecc40c1`을
`sources_v1/validate_model.py`로 보존했다. Root도 원validator와 원model의
exact SHA snapshot을 실패 evidence에 보존했다. 원실패 receipt를 덮어쓰지 않았다.

## 4. 새 threshold와 endpoint branch

Transition times는 새 threshold를 가진 A layer에 위임되며 Li 알고리즘 switch도
유지한다. Endpoint inset은 실제 photon-energy arithmetic의 모든 branch sign이
segment 내부와 같아질 때까지 bounded ULP 이동을 사용한다. State는 바꾸지 않는다.

Root의 ODE0 endpoint 검사36개를 그대로 PASS라고 인용하는 데 그치지 않고,
저장 receipt에 대해 stdlib math.exp/nextafter로 독립 재구성했다.

- **18segments × 2endpoints = 36/36 PASS**.
- Recorded photon energies의 binary64 bits 일치.
- 계산한 actual/expected branch signs 일치 및 모든 sign이 strict.
- Evaluation eta가 해당 segment의 strict interior에 있음.
- Recorded ULP walk 일치, 최대 **12ULP**, cap256 이내.

결과는 `SAVED_ENDPOINT_REVIEW.json`, 재구성 코드는
`check_saved_endpoints.py`다. Runtime endpoint 함수 및 RHS는 호출하지 않았다.

## 5. 실행 경계

Driver는 새 run directory를 `exist_ok=False`로 만들고 각 결과 파일은 임시파일
완성 후 hardlink의 create-only 설치로 덮어쓰기를 거부한다.
Source freeze와 실제 source의 일치, worker 초기화, 각 case의 전후 hash를 확인한다.
Input cases/method/tolerance도 별도 identity로 묶는다.

CPU55 제외, coordinator와 worker CPU 구분, 각 worker1thread, fresh resource/lease
관측과 동적 dispatch 보류가 명시되어 있다. 다른 lease의 만료를 임의 인정하거나
수정하지 않으며 exclusive CPU reservation을 확보했다고 주장하지 않는다.
이 code review가 실제 dispatch 당시 resource observation을 대신하지 않는다.

## 6. 승인 범위와 네 축

| 축 | 이 review의 상태 |
|---|---|
| EXECUTION | PASS_SCOPED_PREFLIGHT; 코드 읽기 및 저장24개 scalar/36개 endpoint 산술 검토; RHS/ODE0 |
| PUBLICATION | Local review artifacts 완료; source freeze·원격 게시 ACK는 parent 담당 |
| BACKUP | Parent의 admission/final package에 포함할 준비; child upload0 |
| DAG | 변경 의존성 preflight COMPLETE_SCOPED; preregistered4개 새 IVP의 실제 자원 admission과 실행·결과 gate로 진행 가능 |

실제 saved/accepted-mesh energy·charge·nucleus·positivity·temperature gate,
BDF/Radau 비교, effect-versus-numerical-resolution 판단은 새 결과 뒤에 수행해야 한다.
현재4개 trajectory를 완료했다고 주장하지 않는다.

Finite CCC source의 continuum interpolation error·물리적 high-energy tail,
Maxwellian/thermalization·secondary-electron closure, all-level inverse/다른 종 CI,
완전한 열·복사·핵 closure는 OPEN이다. 원래 full nuclear high-energy 및
general triaxial/tilted/polarized CMB HOLD와 `global_error_bound=null`을 유지한다.

