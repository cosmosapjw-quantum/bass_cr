# C23A integration C9 독립 검토

검토자: `/root/cr_deposition`. 검토 입력·SHA는 `REVIEW_INPUTS.json`, 수정 뒤 source snapshot은 `source_snapshot_v1/`에 있다. 이 snapshot의 `v1`은 review snapshot 번호이며 과거 실패 kernel version을 뜻하지 않는다.

**판정: 현재 동결한 source-only campaign에 PASS_SCOPED.** 발견한 두 launcher finding은 부모가 수정했고 현재 source에서 그 수정을 확인했다. 과거 source 계산·kernel·ODE를 재실행하지 않았다. 부모가 완료한 새 campaign의 bytes와 실행 receipt를 읽어 판정했다. 이후 제공될 figure는 별도 시각·caption 검토로 연결한다.

## 1. 수정된 finding

### CR-C9-F1 — CPU lease encoding 검증

초기 launcher는 `set(item['cpus'])`를 정수 `{0,1}`과 바로 교차시켰다. 예를 들어 `cpus='0-1'` 또는 `cpus=['1']`은 CPU 1 충돌을 검출하지 못한다. `LEASE_PARSER_COUNTEREXAMPLES.json`에 이 Python 표현만 독립 평가한 결과가 있다. 실제 lease나 CPU를 변경하지 않았다.

부모 수정은 `cpus`가 list이고 모든 원소가 `type(c) is int`이며 0 이상일 것을 먼저 검사한다. 범위 문자열·문자열 원소·bool을 포함한 미지원 encoding은 allocation을 중단한다. **현재 launcher SHA256 `090ee2639f0c26576c11758134c571a4bdb4c3e57aff328ad219f4302fb7a0d2`에서 CLOSED.**

### CR-C9-F2 — incomplete resource observation

`resource_control.observe_resources()`는 `memory_available_bytes`를 실제 반환하므로 key mismatch는 없다. 다만 값이 `None`일 때 초기 비교식은 `TypeError`로 종료됐다. 부모는 CPU/memory가 `None`이거나 memory observation이 incomplete이면 `BLOCKED.json`에 `NOT_RUN_RESOURCE_BLOCKED`, `source_subflows=0`을 쓰고 명시적으로 중단하도록 수정했다. **현재 launcher에서 CLOSED.**

## 2. 물리·단위·계수 확인

| 대상 | 확인한 대응과 판정 |
|---|---|
| 모델 범위 | fixed proper volume, frozen redshift, externally regulated H/He photoionization subflow. P19 prescribed moments와 별도 FS electron response를 결합하지 않음 |
| inventory | 정확히 HI,HII,HeI,HeII,HeIII 다섯 population이 필요. 누락·추가 종을 reject. He/H=0.083은 명시한 diagnostic 입력이며 FS의 미확정 He/H를 채우지 않음 |
| rate 단위 | Γ는 target당 s⁻¹, heat는 target당 eV s⁻¹. heat/Γ는 사건당 eV이며 적분 event count와 곱해 가열 증분을 계산 |
| H event | HI→HII 전이 횟수가 전자 생성 수와 같고 H nuclear count 보존 |
| He event | HeI→HeII와 HeII→HeIII를 각각 세며, 초기 HeI에서 두 번 진행한 경로는 두 ionization event로 귀속. He nuclear count 보존 |
| binding | 첫 번째/두 번째 He ionization의 caller χ를 각 event에 곱함. P19 실제 spectral threshold와 같다는 주장은 없음 |
| thermal particles | 원자/이온 수 + 자유전자 수로 최종 N을 구성. U=(3/2)NkBT이므로 ionization에 따른 N 변화가 온도에 반영 |
| external energy | imported=heat+binding으로 정의한 외부 조절기 ledger. 동일 에너지를 내부 photon reservoir에서 다시 차감하지 않음 |
| 큰 노출 | dt=dose/maxΓ는 각 독립 fixed-source exposure의 시간. 일부 값이 cosmic age를 넘을 수 있으며 cosmological history로 읽지 않는 scope가 code와 contract에 명시됨 |
| 미포함 과정 | recombination, thermal CI/excitation, Compton, secondary cascade, expansion, finite photon reservoir, isotope/Li/nuclear 등은 contract에 명시적으로 제외 |

`energy_event_residual`은 이 명시적 ledger의 부동소수점 일관성 검사다. incident photon spectrum을 독립 복원한 에너지 검증으로 해석하지 않는다. `global_error_bound=null`이 유지된다.

순수 birth kernel의 독립 high-precision 검증은 다른 agent의 `review/photo_subflow_v2`에서 수행했다. 그 `EXECUTION.json`, `PLAN.json`, 빈 `FAILURES.json`과 source SHA를 실제 읽었다. kernel SHA `36af631c24b3d1a2c34c9d7a4f470cbe85334a505e3cbad9ea3228d862c95079`가 현재 코드와 일치한다. 기록된 범위는 283 rate cases, 1,915 operator calls, 28 invalid-input checks이며 모두 PASS_SCOPED다. 이 검토에서는 그 numerical execution을 반복하지 않았다.

## 3. launcher와 실제 실행 identity

### 코드에서 확인

- run ID는 lowercase 영숫자·`_`·`-`만 허용하고 `runs/run_id`를 `exist_ok=False`로 생성한다.
- 주요 JSON/CSV/NPZ는 `x`/`xb`로 생성한다. 완료 run의 overwrite 경로는 없다.
- dispatcher가 actual resources를 관측하고, cooperative lease directory를 lock한 상태에서 모든 보이는 lease를 검사한다. CPU 0/1을 자기 소유로 예약한다.
- native thread 환경변수 6개를 NumPy import 전에 1로 고정한다.
- coordinator는 CPU 0, child는 NumPy import 전에 CPU 1로 pin한다. Linux의 child가 상속한 `{0}` affinity를 cgroup이 허용하는 `{1}`로 바꾸는 것은 유효하다. 실제 run receipt도 CPU 1을 확인한다.
- worker subprocess의 wall timeout은 60 s다. 정상 return code와 stdout/stderr를 기록하고 자신의 정확한 lease만 제거한다.
- 6개 주요 source/input 파일을 SHA256으로 pin하고 worker에서 다시 비교한다. P19 provider는 actual table bytes를 자체 고정 SHA로 검사한 뒤 그 메모리 bytes를 parse한다.

### 완료 run의 실제 bytes readback

`runs/c23a_p19_subflow_20261023_v1`의 readback은 `COMPLETED_RUN_READBACK.json`에 있다.

| 검토 항목 | 실제 결과 |
|---|---|
| source SHA/size | 6/6 일치 |
| aggregate source identity SHA | 일치 |
| `INPUT.json` vs pinned `CONTRACT.json` | 일치 |
| `COMPLETE.json`에 든 출력 SHA/size | 7/7 일치 |
| CSV exposure 수/중복 | 826행, unique key 826개 |
| CSV numeric field finite | 모두 finite |
| worker/threads | affinity `[1]`, 환경변수 6개 모두 1 |
| dispatcher | exit code 0, timeout 60 s, CPU55 미사용 |
| lease | 생성·관측한 다른 lease hash 기록, 자기 lease release receipt 존재 |

실제 admission 관측은 8 CPU quota, spare 6.26893 cores, memory limit 8 GiB, available **2,303,217,664 bytes**, CPU 0/1 busy fraction 각각 0이었다. summary의 wall/CPU는 **1.203676858 / 1.203441613 s**다. 이는 실행 당시 관측이고 미래 availability를 보장하는 값은 아니다.

완료 결과의 최대 inventory residual은 `1.1102230246251565e-16`, charge residual은 `2.220446049250313e-16`, energy ledger relative residual은 `9.573613404646192e-17`, semigroup population difference는 `1.1102230246251565e-16`이다. 826개의 새 source exposures와 1,652개 semigroup comparison subflows로 기록돼 있다. cosmological ODE와 과거 science rerun은 0이다.

## 4. 현재 결과와 구별할 runtime 범위

현재 완료 run에는 실패 증거가 없고 source/input bytes가 실제 pin과 일치한다. 다음 launcher 변경 때 다룰 수 있는 범위는 아래와 같다. 이 항목들은 현재 science를 다시 실행할 이유가 아니다.

1. Python module import는 worker의 digest 비교보다 먼저 일어난다. 동결한 코드와 후속 hash 일치가 이번 실행 identity를 지지한다. 수정과 실행이 동시에 일어나는 워크플로로 확장한다면 동일한 검증 bytes의 snapshot에서 import하고 INPUT 자체를 prelaunch digest에 포함하는 방식이 더 강한 계약이다.
2. CPU별 busy 관측과 memory headroom은 기록되지만 process RSS hard cap으로 적용되지는 않는다. 실제 제한으로 주장할 수 있는 것은 cooperative affinity/thread/lease 및 60 s child timeout과 환경 cgroup 한도다.
3. Timeout·일부 lease parse/affinity exception 경로는 정상 `DISPATCH_COMPLETE.json`과 달리 전용 terminal failure receipt가 완전하지 않다. 다음 launcher 수정에서 예외 유형과 부분 stdout/stderr를 create-only 실패 record로 보존할 수 있다. 현재 run은 정상 exit 0이고 이 경로를 타지 않았다.

## 5. 공개 deposition subset의 재사용

49-file public subset은 `upstream/x_int_tables/`를 포함하지 않는다. frozen audit 두 script는 당시 원 경로와 완료 run ID를 보존하므로 public subset에서 그대로 replay할 수 없다. 확인한 현재 operator 자체는 explicit table directory를 받아 MIT mirror 경로로 소비할 수 있다.

`PUBLIC_SUBSET_USAGE_KO.md`와 `consume_mit_mirror_example.py`를 제공했다. helper는 공개 mirror의 commit, SHA256, Git blob, license 보존을 검사하고 우리 operator의 정확한 검증 bytes를 사용한다. 이 helper의 상태는 **syntax PASS, numerical execution NOT_RUN**이다. 새 lease를 받은 worker 안에서만 새 입력·create-only output으로 호출한다. 과거 완료 audit 복구는 기존 결과와 manifest를 읽는다.

Attribution은 FS2010 논문, 21cmFAST pin과 동봉 MIT license, 선택 DarkHistory 파일의 동봉 MIT license를 보존하도록 명시했다. 원저자 archive/C의 license 부재를 MIT로 소급하지 않는다.

## 최종 상태

| EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|
| static review와 완료 artifact readback; science/kernel 재실행0 | 부모가 review와 public consumer 안내를 통합할 수 있음 | 로컬 review bytes; durable receipt는 부모 배송 기록에 연결 | launcher finding2 CLOSED, C9 integration PASS_SCOPED → figure 검토 별도 → C10 게시/백업 |
