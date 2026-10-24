# C23D 독립 C9 검토

**판정: `PASS_SCOPED_C23D_SOURCE_EE_BRIDGE`, 현재 blocking finding 0.**

이 판정은 `C23D_FROZEN_MAXWELL_EE_LOW10_V1`의 명시된 세 redshift 입력, 0 < W < 10 eV source pulse, fixed Maxwell ee 채널, primary 세 discrete-population 진화와 저장된 수렴 비교에 적용한다. 전체 `CR_N4_STOPPING_KERNEL`은 neutral/inelastic/reciprocal finite-bath/escape/coupling 의무를 유지한다. `global_error_bound`와 전체 물리적 stopping/heating은 null이다.

검토자 `/root/stopping_physics_review`는 새 production adapter·runner를 작성하지 않았다. 같은 상위 대화 문맥을 받은 별도 agent이며, blind review나 독립 외부 기관 검토를 주장하지 않는다. 실제 독립성은 production numerical provider를 import하지 않은 SI 유도·Decimal 특별함수·원 CSV contraction과 별도 코드 독해에 있다. 선행 Maxwell 계수·cutoff 원장·MFPT 이론은 `EE_COEFFICIENT_REUSE_REVIEW_KO.md`의 기존 PR59 대응을 재사용했다.

## 계약과 입력

읽은 frozen contract는 `FROZEN_CONTRACT.md`이고, 새로운 `inputs/CASE.json`은 SHA256 `107bfddf5df0fd21690e86bff999fbf30809f5a5e55a11237e72e1663962bfc6`이다. 원 C23B CSV 32592행, 1681578 bytes, SHA256 `f5bcfe477b8a073341a7496c079e6eb2737f6ca578b884376887b04989e57fc3`를 독립 checker에서도 확인했다. 기존 provider는 3984 bytes, SHA256 `0fae93ddfd555e1d135606eab51cfe010911c7624f661d27317024cf3f54ba86`다.

새 source는 각 redshift에서 10864행 중 384행을 선택한다. 코드의 `n_target*q_atom`에 `exposure=10000 s`를 곱해 초기 pulse를 만든다. rate와 초기 count를 구별하고 Lorentz 또는 lifetime 인자를 추가하지 않는다. HI/HII/HeI/HeII/HeIII 다섯 label이 명시되며, 처음 열전자 밀도 0.14 cm^-3와 전체 자유전자 밀도는 별도 필드로 존재하고 이번 초기 조건에서만 같다. 이 조건이 곧 이후 photoionization 또는 열 bath 갱신을 뜻하지 않는다.

선택한 count coverage는 약 91.31–91.65%, energy coverage는 약 64.46–65.90%다. 제외된 count/energy와 exact endpoint의 source totals를 별도 저장한다. 전체 50 keV 부근 source를 이 ee 저에너지 계산으로 승인하지 않는다. 실제 선택 pulse의 count/bath 및 energy/bath 비는 각각 약 7.07–7.35e-8과 1.50–1.56e-7로 frozen 1e-3 screen을 통과한다. 이 screen은 근사 오차의 전역 증명이 아니다.

## 식–코드 대응

1. **실제 밀도 정규화:** SI \(\Gamma=n_e e^4\ln\Lambda/(4\pi\epsilon_0^2m_e^2)\)와 \(v_\theta=\sqrt{2k_BT/m_e}\)에서 기존 eV provider의 anchor는 \(b_*=m_e\Gamma/(\epsilon_{\rm eV}v_\theta)\)다. 코드가 이 대응을 사용한다. 독립 계산은 algebraically equivalent SI 식에서 시작했다.
2. **차원 없는 시간:** \(\tau=(\Gamma/v_\theta^3)t\), \(y=W/\theta\)에서 dimensionless provider anchor loss가 2가 된다. 실제 `mfpt_dimensionless`의 `(energy_anchor,loss_anchor,temperature_energy)=(1,2,1)`은 맞는 정규화다.
3. **signed exchange:** source-weighted drift는 eV cm^-3 s^-2이고 pulse 초기 열교환은 여기에 exposure를 곱한 eV cm^-3 s^-1이다. 배경 heat는 같은 test kinetic moment의 반대 부호다. 별도 cold stopping heat를 더하지 않는다. 낮은 에너지의 upward drift가 실제로 보존된다.
4. **projection:** 각 source atom을 두 이웃 centre에 비음성 barycentric weights로 투영하므로 count와 에너지가 동시에 보존된다. finite band 안의 source만 투영한다.
5. **진화:** 기존 reversible generator가 column count에 작용한다. backward Euler band matrix의 양 끝과 upper/lower diagonal 배치는 \((I-\Delta\tau Q)N^{n+1}=N^n\)에 맞는다. 반사 경계와 midpoint discrete equilibrium을 사용하며, 아래 core를 Maxwellian으로 덮어쓰지 않는다.
6. **cutoff 원장:** 각 \(q_h\)에서 tail count rate는 공통 edge current다. 실제 tail kinetic contraction은 \(q_hJ+I_h\), `moving_interface`의 반대 원장은 배경 bath와 낮은 에너지 tagged core를 합친 reservoir다. 이것과 배경만의 \(-E\cdot\dot N\) heat를 코드가 따로 표기한다. diffusion boundary 기여가 누락되지 않는다.
7. **MFPT:** absorbing lower threshold와 reflecting 40theta/80theta upper boundary의 첫 진입 문제다. 초기 threshold 이하 atom의 관측값 0, active mean과 전체 selected mean, prescribed evolution time의 비를 구별한다. 이를 영구 assimilation 시간으로 부르지 않는다. 원전 공식을 재사용했고 원 과거 예제를 재실행하지 않았다.

## 새로운 독립 산술 실행

실행: `python cr_stopping_loop_20261024/theory/independent/C23D_C9_reference.py`.

처음 `python3` 실행은 `mpmath` 미설치 때문에 import 단계에서 종료했다. 과학 연산·run directory·lease 전의 환경 실패이며 `C23D_C9_ENVIRONMENT_REPAIR.json`에 보존했다. 의존성을 설치하지 않고 표준 라이브러리 Decimal의 exp/sqrt와 명시적 수렴 erf 급수로 바꾸었다. 내부 110자리에서 80자리 reference를 산출했다. 물리 상수는 production에서 사용한 scipy.constants의 decimal 값에 결속하며, 80자리는 산술 정밀도다.

| 독립 검사 | 결과 |
|---|---|
| SI density anchor 5개 | PASS |
| 세 redshift의 raw CSV count/energy/coverage/diluteness/upward fraction/signed weighted drift 33개 | PASS |
| 세 redshift에서 세 selected atom의 drift/diffusion 18개 | PASS |
| 총 56개 비교, 사전 선택 허용 relative error 2e-12 | 최대 **1.7389330148070301e-15** |
| 저장된 primary 3개 trajectory의 count/energy 재합산 | PASS, 새 진화 없음 |
| reviewer CPU / native threads | CPU1 / 1 |
| 측정 CPU / wall / RSS | **0.2863936 s / 0.28848147 s / 64776 KiB** |

실제 affinity0–8, CPU quota8, memory8GiB를 읽었고 CPU8을 coordinator용으로 남겼다. CPU55는 이 host에 없고 건드리지 않았다. reviewer의 exclusive lease는 생성·해제됐다. 외부/NCP lease는 `UNOBSERVED`다. reference 결과는 `C23D_C9_reference_run_v1/RESULT.json`에 있다. 이 실행의 새 population integration과 과거 과학 replay는 모두 0이다.

## primary 저장 결과와 frozen acceptance

Primary run `c23d_source_ee_20261023T220714Z_v1`은 실제로 새로운 선형 EE population ODE trajectory 3개를 적분했다.

| 항목 | 관측 | frozen 기준 |
|---|---:|---:|
| 256→512 mean-energy spatial 차이 | 1.8700193872942585e-4 | 5e-3 |
| dtau 0.01→0.005 mean-energy temporal 차이 | 1.4715805528588597e-4 | 3e-3 |
| MFPT upper boundary 40→80 active mean 차이 | 1.8651486594044342e-14 | 1e-8 |
| 최대 count relative drift | 3.0993811274902116e-13 | 1e-9 |
| 최대 shared-face energy relative residual | 2.858233592703015e-16 | 1e-11 |
| projection count/energy residual | 최대 1.629537921919144e-16 | 1e-12 |
| negative population | 0 | clipping 금지 |

모든 실제 step에서 entropy 증가의 저장된 최대 양수분이 0이다. 작은 pulse count 때문에 느슨해질 수 있는 count-weighted 표시를 `mechanical/PER_PARTICLE_ENTROPY.json`에서 particle당으로 다시 표현했다. 512/dtau0.005의 sampled relative entropy는 0.90221125에서 0.00126157로 감소한다. 이 표시는 저장된 결과를 rescale한 것이며 새 적분이 아니다. 해당 finite-band equilibrium과 mean-energy 수렴에 대한 scoped 판단이다.

## 발견 사항과 동일 범위의 교정

### C9-F1 — 게시 경로에서의 실행 가능성, CLOSED

- 대상: 원 `source_ee_bridge.py`, `run_bridge.py`, `dispatch.py`의 scratch 절대 구조 의존.
- 근거/영향: repository의 `research/cr_c23d_finiteT_source_bridge_20261024/`로 옮기면 원 하드코딩 경로와 빈 `runtime` directory가 존재하지 않는다. 실제 이번 계산은 유효하지만 새 배송본의 재개 명령은 실패한다.
- 최소 교정: `--provider`, `--source-csv`, `--inputs` 및 package/repo 상대 후보, dispatcher의 runtime/runs parent 생성. 새 child run은 exclusive `mkdir`를 유지한다.
- 근거: `mechanical/RELOCATION_SMOKE.json`에서 경로·provider identity·import·guard를, `mechanical/FRESH_PARENT_SMOKE.json`에서 두 parent가 없는 레이아웃의 print-only child dispatch와 lease 해제를 확인했다. 후자의 dispatch SHA256은 `3fc88f8cc53bc6b48f6d0ce425a86625d92f7d8ee30b0953d410d64d68ea3859`다. 과학 실행은 없다.
- 범위 보존: 원 실행 3개 파일은 `implementation/history/primary_20261023T220714Z/`에 보존됐다. AST 비교에서 `load_provider`, `validate`, `anchor`, `read_source`, `project`, `mfpt_dimensionless`, `evolve`의 numerical 함수가 변경되지 않았다. main의 변경은 입력 경로 및 보고 metadata다.

### C9-F2 — 새 ODE 실행 수의 모호한 metadata, CLOSED

- 대상: 원 `RESULT.json`의 무자격 `new_ODE:0`.
- 근거/영향: 실제 \(\dot N=QN\)를 backward Euler로 적분했으므로 읽는 사람이 과학 실행이 없었다고 오해할 수 있다.
- 최소 교정: 원 raw result는 그대로 보존하고 `RESULT_CLARIFICATION.json`에 coupled cosmological ODE0, 필수 선형 EE trajectory3을 구분했다. 현재 future producer도 explicit field를 출력한다.
- 실제 비용: 추가256/dtau0.01은 root의 no-optional-run clarification이 도착하기 전에 이미 완료됐다. 별도 raw run을 보존하고 비용을 누적한다. **총 관측 새 선형 trajectory4, 이번 admission 근거3, supplement는 NOT_REQUIRED/NOT_ADMISSION**이다. 완료된 추가 실행을 없던 일로 하지 않는다.

## 검토 종료와 다음 gate

필수 새 입력의 source→provider 대응, 지정된 population 진화와 scoped 수렴, 독립 산술, 배포경로의 실제 결함 교정이 처리됐다. 닫힌 PR59 이론·과거 ODE·2048-cell suite를 다시 실행할 의무가 없다. 새로운 no-go 주장은 없으며 NG1–NG7의 신규 admission은 `NOT_APPLICABLE`이다.

**EXECUTION:** C9 독립 산술 PASS, production 새 primary3 + 별도 supplement1의 실체 확인, 과거 replay0.  
**PUBLICATION:** root가 expected-SHA 게시를 진행할 수 있다. reviewer remote write0.  
**BACKUP:** reviewer 신규 전송0, 실제 artifact의 provider 상태는 root receipt에 결속한다.  
**DAG:** named C23D bridge는 `NUMERICALLY_CHECKED_SCOPED`에 적합하다. 전체 stopping, N5 실제 atomic/isotope-rate coverage, N6 coupling은 별도 OPEN을 유지한다.
