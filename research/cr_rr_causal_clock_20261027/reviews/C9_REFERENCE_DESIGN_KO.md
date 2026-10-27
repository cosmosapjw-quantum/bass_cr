# C9 독립 Decimal70 참조 계산기 — 준비 계약

## 현재 상태

**후보 구현 작성 완료, 실제 science 실행 전.** 이 폴더의 파일은 root가 frozen C 계약·C4 실행 lease·C5 production code pin에 연결할 후보다. 이 단계에서는 AST syntax parse만 했으며, 해당 module을 import하거나 solver를 실행하지 않았다. 실제 CPU 사용량·PASS·reference output은 아직 존재하지 않는다.

후보 `independent_reference.py`는 **30,004 bytes**, SHA256 **`4d1bbb8cbb9f12cbc25fd4847f48239d793ac70e96196c09f2c10eab33c5f7e1`**다. 이후 root가 복사한 실행 파일의 exact hash를 `REFERENCE_PLAN.json`에 넣어야 한다. 이 문서는 새 실행 허가나 기존 budget의 초기화가 아니다.

## 시작 시 현재 상태와 읽은 근거

2026-10-27 **07:21:48 UTC**에 새 branch `research/cr-rr-causal-clock-20261027`의 실제 원격 HEAD **`8687d1cab2bdc89364d8e6d6559177b01a074e3a`**를 확인했다. 원격 AGENTS는 R6에서 읽은 CR AGENTS와 exact bytes가 같으며 SHA256은 `8d62d9758fe173263eb3820c7b00ca569193bb7f912fc3d95d145e73d4a40970`이다. 로컬 같은 branch HEAD는 기존 D `ec463db0c7e5c7fb5070796071c926caa4db6445`였고 root의 새 stage 파일들이 staged/작성 중이었다. 이 차이는 별도로 기록하고 원격·로컬을 임의 동기화하지 않았다. 로컬 `research/AGENTS.md`와 새 단위의 AGENTS는 없었다.

기존 HeIII의 `review/c9_independent.py`에서 exact binary64→Decimal 입력, scalar Thomas solve, original source contraction, own-column 비교·실패 보존·process CPU guard의 필요한 부분을 읽었다. `implementation/dispatch.py`의 create-only run directory와 lease, stage/aggregate 누적 비용, 실패 receipt, unknown prior budget, native threads, memory admission, 서로 다른 CPU affinity, owned child-only termination을 읽었다. 기존 code를 import하거나 실행하지 않았다. 기존 provider coefficient 계산·56개 과거 참조 RHS·source projection은 새 계산기에 옮기지 않았다.

수학 기준은 R6가 승인한 `THEORY_KO.md` SHA `c736e9ab4377bc3bbbdcacd7c7a86c3a3a65dfd7c0c6700d60eb298025d07c6a`, `FORMULA_CONTRACT.json` SHA `73d06e1d244768490afa9df4a2a9c78246e3ed06bfd499f0a168a83e8d82ec07`다. 준비 작업에는 `physmath-research-loop` C1–C4/C9 지침을 적용했다.

후속 root 지시에 따라 R9 commit **`ea5ee9183ae4a51eb356eca4c60724e4f32165e0`**의 `research/cr_rr_causal_clock_20261027/CODING_CONTRACT.json`을 실제 원문으로 읽었다. 이 계약의 **own-column relative≤5e−10**와 **exact target solution의 production radius 포함**을 실제 PASS 조건에 반영했다. 후자를 nominal Decimal70 point 비교만으로 판정하지 않도록, 추가 RHS 없이 독립적인 directed Decimal100 residual/witness enclosure를 덧붙였다. 입력·32 RHS footprint·15 CPU s cap는 바뀌지 않았다.

## Root가 수락한 최소 참조 범위

| case | 실제 interior n | proper T | m | δ | clock |
|---|---:|---:|---:|---:|---|
| `chi1.5_R80_N2048` | 2,479 | 100,000 s | 4 | 0.5 | minus·plus |
| `chi3_R80_N2048` | 2,479 | 1,000,000 s | 4 | 0.5 | minus·plus |

두 channel RHS는 **저장 `rhs_physical18[:,10]` count와 `[:,11]` kinetic**뿐이다. 각 case에서 두 shifted matrix를 한 번씩 Decimal70 factorization하고, 각 shift의 4개 recurrence 단계×2개 RHS를 푼다. 따라서 **4 factorizations, 32 RHS, 32 step vectors와 8 cumulative vectors, 24 source scalar**를 비교한다. 전체 vector component 비교는 `(32+8)×2479=99,160`개이며, 각 step vector는 exported 성분별 radius와 `epsilon_steps*h` 두 조건을 함께 확인한다.

원래 세 source z=2.316,2.479,2.649를 모두 사용한다. source는 저장된 `source_z[1:]`를 Decimal로 직접 읽고, `source_z[0]` 경계 mass를 결과 metadata에 보존한다. 새 source generation·projection·rate evaluation·all-time solve는 없다. T는 선택한 pulse 관측 horizon이고 actual injection exposure가 아니다.

production의 전체 m=64/256/1024 campaign을 Decimal로 반복하지 않는다. 작은 m=4 qualification에서도 실제 전체 fine grid와 실제 저장 RHS·source를 사용하므로 구현 recurrence·matrix orientation·input identity·scalar contraction을 독립적으로 비교할 수 있다. 일반 m에 대한 certificate 주장은 C9의 별도 code/arithmetic 검토로 확인한다.

## 고정 입력 identity

입력 file hash와 NPY header는 실제 기존 저장 파일에서 읽었다. 이 read-only 확인은 새로운 science 계산이 아니다.

| 역할 | 파일 | bytes | SHA256 |
|---|---|---:|---|
| HeIII K/RHS χ1.5 | `research/cr_heiii_ground_rr_20261027/runs/cr_heiii_rr_primary_20261027_v1/chi1.5_R80_N2048.npz` | 2,055,186 | `44171ed99a638bf33eb4ec969bb6b91eb61a6deec5aea4d1d809e63363c45f4e` |
| source χ1.5 | `research/cr_heiii_ground_rr_20261027/inputs/reused/pr104/chi1.5_R80_N2048.npz` | 962,791 | `883c2bb5fd658d3ecc1c7b423bc9d3282d7da08fd1763ffbb63733985c878f20` |
| HeIII K/RHS χ3 | `research/cr_heiii_ground_rr_20261027/runs/cr_heiii_rr_primary_20261027_v1/chi3_R80_N2048.npz` | 2,062,237 | `7334e37ecf555a01dd83d769600166a7d8115a62a57f5646227ad2301e379aa3` |
| source χ3 | `research/cr_heiii_ground_rr_20261027/inputs/reused/pr104/chi3_R80_N2048.npz` | 967,255 | `46965a9669350f38ede9825ecb96e0b1b3ecec6c0a9fd4ad7541f1785c79ecff` |

새 target K는 **이미 HeIII가 들어 있는 저장 `K_diag/K_lower/K_upper`**다. 이전 independent reference처럼 HeI diagonal에 새 Decimal hazard를 더하지 않는다. RHS도 저장 count/kinetic entries를 그대로 채택한다. `Decimal.from_float`는 해당 binary64 값의 exact real을 읽으며, 그 후 solve arithmetic은 precision70이다. gamma도 production의 `gamma_hex`를 `float.fromhex` 후 `Decimal.from_float`로 복원한다.

## Production과 합의한 qualification protocol

primary는 `capture=False`로 둘 수 있다. 위 네 qualification clock에만 `capture=True`를 적용하여 각 clock의 NPZ와 JSON metadata를 저장한다. root runner가 실제 파일명과 hash를 reference plan에 연결한다. production module을 reference worker에서 import하지 않는다.

### NPZ 배열

| 이름 | shape | dtype/의미 |
|---|---|---|
| `z_steps` | `(4,n,2)` | 실제 FP64 recurrence 중심값, channel 순서 count·kinetic |
| `h` | `(n,)` | strict positive witness의 저장 binary64 값 |
| `epsilon_steps` | `(4,2)` | 각 단계 weighted-error radius의 상향 binary64 값 |
| `step_radius` | `(4,n,2)` | 각 성분의 독립 상향 binary64 radius |
| `cumulative` | `(n,2)` | Σz의 저장 binary64 중심값 |
| `cumulative_radius` | `(n,2)` | recurrence, 누적 및 binary64 변환 오차를 포함한 상향 radius |

`epsilon_steps`와 `step_radius`가 각각 별도 상향 반올림될 수 있으므로 `step_radius≥encoded_epsilon*h`라는 불필요한 관계는 강제하지 않는다. 대신 independent directed reference enclosure 전체가 양쪽 주장 radius 안에 각각 들어가는지 비교한다.

### 각 clock JSON metadata

```json
{
  "case": "chi1.5_R80_N2048",
  "clock_label": "minus",
  "T_s": 100000.0,
  "m": 4,
  "delta": 0.5,
  "gamma_hex": "ROOT_WRITES_ACTUAL_BINARY64_HEX",
  "epsilon_steps_hex": [["OPTIONAL_HEX", "OPTIONAL_HEX"]],
  "source_rows": [
    {
      "z": "2.316",
      "count": {"A_lower": "OUTWARD_ENDPOINT", "A_upper": "OUTWARD_ENDPOINT", "A_nominal": "CENTER"},
      "kinetic": {"A_lower": "OUTWARD_ENDPOINT", "A_upper": "OUTWARD_ENDPOINT", "A_nominal": "CENTER"}
    }
  ]
}
```

위 예의 source_rows는 실제로 세 z를 모두 갖고, optional epsilon hex는 실제로 4×2 entries여야 한다. 숫자가 JSON number이면 Python float를 거쳐 exact encoded binary64로 읽는다. hex 문자열도 binary64로 읽는다. decimal 문자열은 선언된 exact decimal endpoint로 읽으며, producer는 그 serialization의 상향/하향 방향까지 책임져야 한다. 평범한 `str(float)`를 무조건 underlying binary64의 exact 값이라고 취급하지 않는다.

## 독립 계산·비교 알고리즘

1. Frozen plan, reference code, production code, 기존 NPZ 네 개, qualification NPZ/JSON 여덟 개의 실제 bytes/hash를 확인한다. root가 아직 pin하지 않은 candidate를 통과 대상으로 사용하지 않는다.
2. numpy는 NPZ 입출력·배열 header/shape/sign 검증에만 사용한다. factorization과 recurrence는 별도 scalar Decimal Thomas 코드다.
3. `B=K+gamma I`의 approximate Decimal70 factors를 만들고, `z0=B⁻¹r`, `zj=gamma B⁻¹z(j−1)`를 전체 2,479 grid에서 계산한다. 저장 K/RHS/γ를 exact represented input으로 해석하지만 Decimal factorization 자체를 exact solve라고 주장하지 않는다.
4. Decimal100 `ROUND_FLOOR/ROUND_CEILING`의 명시적 context 연산으로 exact 저장 K에 대한 `Kh≥βh>0`를 독립 검증한다. 각 solve의 residual은 diagonal·γ·두 off-diagonal의 exact products를 outward enclosure하고, j>0 RHS의 `γ*zref_previous` 형성 오차도 포함한다. `η/α` 및 이전 ε의 전파로 reference 자체의 exact-solution interval을 만든다. 별도 Decimal100 nominal scaled-residual `≤1e−55`는 보조 품질 진단이며 enclosure proof의 대용이 아니다.
5. 모든 step vector와 cumulative vector의 reference interval 전체가 production 중심±radius에 포함되는지 확인한다. exact error의 상한을 reference exact norm의 하한으로 나눈 **own-column relative upper≤5e−10**도 함께 요구한다. 한 component라도 containment를 입증하지 못하면 실패를 기록한다. 임의 tolerance를 더해 interval을 넓히지 않는다.
6. 세 저장 source의 Decimal70 dot product를 진단값으로 기록하고, nonnegative w와 cumulative reference interval을 directed Decimal100으로 contraction한 **A interval 전체**가 exported `[A_lower,A_upper]` 안에 있는지 검사한다. scalar 비교 24개 모두 필요하다.
7. 네 CSV에 모든 단계·모든 grid index의 count/kinetic Decimal70 값을 보존한다. JSON 결과는 input/code pins, 전체 비교 수, 최대 오차·최소 margin·own residual, 각 실패와 실제 worker 비용 관측을 담는다.

**Decimal70 point만으로 exact containment를 증명하지 않는다.** 이 참조 계산기는 위 독립 directed enclosure를 실제로 계산한 뒤 qualification된 m4 문제의 containment를 판정한다. 이 유한 참조 결과가 production의 전체 m64/256/1024 campaign을 자동 증명하지는 않는다. C9 최종 검토는 production의 native long-double rounding bound, FP64 solve residual, exact shift/RHS, inherited recurrence error, h/β witness, all-time cap, tail 상향 bound와 최종 outward serialization을 별도로 읽어야 한다. primary export도 공통 N,E correlation·부호·SI 변환 및 실제 history/nb의 null을 실제 결과에서 확인한다.

Directed reference의 row image는 `(Kdiag*x)+(gamma*x)+Klower*xprev+Kupper*xnext`를 각각 아래/위로 계산하므로 rounded shifted diagonal을 exact target으로 바꾸지 않는다. residual 양끝에서 `η≥||rho||h`를 얻고, α의 하한을 사용한 `εj↑=(gamma*εprev+η)↑/α↓`로 상한을 만든다. 모든 reference z interval은 M-matrix positivity로 `[0,∞)`와 교차할 수 있다. 누적 interval과 source contraction도 같은 방향의 연산만 사용한다. production에 대한 상대오차 분모는 exact reference norm의 하한이므로 오차 판정을 느슨하게 만들지 않는다.

## Root가 채울 reference plan

계산기는 다음 구조를 읽는다. 아래는 **미승인 설계 예**이며 그대로 실행할 수 없다. root C4 허가 및 C5/C6 결과 pins 후에 실제 plan을 고정한다.

```json
{
  "schema": "CR_RR_CLOCK_C9_REFERENCE_PLAN_V1",
  "root_C4_authorized": false,
  "authorized_run_id": "ROOT_FROZEN_REFERENCE_RUN_ID",
  "precision_decimal_digits": 70,
  "expected_reference_sha256": "4d1bbb8cbb9f12cbc25fd4847f48239d793ac70e96196c09f2c10eab33c5f7e1",
  "expected_rhs_count": 32,
  "expected_factorizations": 4,
  "frozen_contract": {"path": "ROOT_FROZEN_C_CONTRACT", "sha256": "ROOT_C4_PIN"},
  "production_sources": [{"path": "ROOT_C5_EXECUTED_ENGINE", "sha256": "ROOT_C5_PIN"}],
  "cases": [
    {
      "case": "chi1.5_R80_N2048",
      "heiii_npz": {"path": "OLD_HEIII_CASE_PATH", "sha256": "FIXED_HASH_FROM_TABLE"},
      "source_npz": {"path": "OLD_PR104_CASE_PATH", "sha256": "FIXED_HASH_FROM_TABLE"},
      "clocks": [
        {"clock_label": "minus", "arrays": {"path": "QUALIFICATION_NPZ", "sha256": "ACTUAL_SHA"}, "metadata": {"path": "QUALIFICATION_JSON", "sha256": "ACTUAL_SHA"}},
        {"clock_label": "plus", "arrays": {"path": "QUALIFICATION_NPZ", "sha256": "ACTUAL_SHA"}, "metadata": {"path": "QUALIFICATION_JSON", "sha256": "ACTUAL_SHA"}}
      ]
    }
  ]
}
```

실제 cases에는 χ3도 같은 구조로 추가한다. 상대 경로는 `--root-dir`을 기준으로 해석하고, absolute path도 허용한다. 각 file record는 optional bytes 필드도 검사한다.

동결 후 root의 bounded dispatcher가 호출할 command 형식은 다음과 같다.

```bash
python -B EXECUTED_SOURCE/independent_reference.py \
  --root-dir /workspace/scratch/5fcfe17050d5/bass_cr \
  --plan ROOT_FROZEN_REFERENCE_PLAN.json \
  --out-dir ROOT_CREATE_ONLY_REFERENCE_RUN \
  --run-id ROOT_FROZEN_REFERENCE_RUN_ID \
  --cpu-limit-s 15
```

## 자원·실패·누적 비용

참조 stage cap은 root가 승인한 **15 CPU s**, primary cap은 **30 CPU s**, 새 unit cap은 **60 CPU s**다. 참조의 실제 비용은 아직 측정되지 않았다. 복잡도는 4개의 O(n) factorization, 32개의 O(n) solve, 약 10만 vector component 비교와 세 source contraction이며, full m1024 Decimal replay를 피한 유한 footprint다. 이 규모 설명을 실행 비용 측정으로 기록하지 않는다.

worker는 15 s 이내 전달된 실제 remaining cap을 받아 guard를 cap−max(0.3 s,3% cap)로 설정한다. process CPU에는 import와 dense CSV 작업도 포함한다. 최종 JSON 직전 worker가 측정한 CPU는 중간 관측이며, **최종 serialization과 coordinator 비용을 포함한 authoritative 누적 비용은 dispatcher receipt**가 기록한다. native thread=1, address-space≤512 MiB로 제한한다. CPU hard limit, wall≤60 s, 독립 reviewer affinity, memory reserve/lease와 이전 실패 비용 합산은 root dispatcher가 맡는다.

출력 JSON/CSV는 create-only다. 중간 실패나 budget stop이면 완료된 파일과 error receipt를 남기고 PASS로 바꾸지 않는다. kill 등으로 worker receipt가 없으면 root dispatcher의 실제 attempt ledger를 남기며, missing prior receipt를 unused credit로 간주하지 않는다. 기존 HeIII 30 s나 PHYS91 예산을 빌리지 않는다.

## 다음 단계

root가 위 후보를 C4/C5의 실제 frozen 계약·source snapshot·qualification output pins에 연결한 뒤 단 한 번의 허가된 참조 실행을 맡긴다. 그 실행 결과와 production code/interval/export의 독립 검토를 합쳐 C9 판정을 작성한다. 이 준비만으로 C9 완료나 numerical PASS를 선언하지 않는다.

중앙 표시 **27/88**, 새 count effect **0**. N4/N5 partial, N6/N7 predecessor gate, global completion/error null, L4 false, 과거 UNKNOWN_NO_ACK와 공급자·isotope 범위는 유지한다.
