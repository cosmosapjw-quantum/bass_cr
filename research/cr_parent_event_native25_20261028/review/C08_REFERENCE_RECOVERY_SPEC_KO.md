# C08 독립 reference의 정확한 반분 경계: 네 검사 전용 복구 계약

Unit: `CR_PHYS02_PARENT_EVENT_NATIVE25_V1`.

이 문서는 실제 첫 독립 실행의 네 실패를 보존한 상태에서 작성한 **실행 전 수리 명세**다. 새 recovery 코드의 실제 실행·성공은 아직 주장하지 않는다. 작성자 `/root/theory_review`는 원 이론·독립 reference 저자이며 production 저자가 아니다. 별도 검토자 `/root/source_qualification`의 실제 정적 검토 및 root의 새 code manifest/budget 결속 뒤에만 실행한다.

## 실제 원 결과와 원인

원 `implementation/independent_reference.py`는 61,964 B, SHA256 `52511cdb8762b4a33b125bbeb72e46adfdeb7acc6c793d20622785ad1f786f55`이며 변경하지 않는다. 실제 실행 snapshot도 같은 bytes다.

`runs/independent_v1/RESULT.json`은 1,651,412 B, SHA256 `fedc2a34a857f5de7c8035db580bdc746319366914efa9094a36a71e6923f8c9`, 상태 FAILED다. 실제 3,450 evaluations 중 3,446 PASS와 네 FAIL이 있다. 네 실패는 모두 `conditional_family`의 다음 IDs다.

| ID | 원 observed | 원 expected |
|---|---:|---:|
| `prefixes.0.fixture.2.s_m3` | 0 | −1E−107 |
| `prefixes.2.fixture.2.s_m3` | 0 | +1E−106 |
| `prefixes.3.fixture.2.s_m3` | 0 | +1E−106 |
| `observation_bins.0.fixture.2.s_m3` | 0 | −1E−107 |

원 reference는 `d=N*f; s=N−2*d`를 90자리 Decimal context에서 계산했다. 정확한 `f=1/2`, `p=0` fixture에서는 실수 대수상 `s=N(1−2f)−p=0`이다. 유한 자리수에서 `N/2`를 먼저 반올림한 뒤 다시 두 배 하면, 마지막 자리의 차이가 `s`에 비물리적 잔여로 남을 수 있다. 이 잔여를 기대값으로 삼아 자기 크기로 나눈 결과가 네 `relative_error=1`이다.

이 진단은 허용치를 완화할 이유가 아니다. 원 `1E−11` relative criterion과 `exact when scale is zero` 규칙을 유지한다. 실제 primary는 `runs/primary_v2/RESULT.json`, 399,835 B, SHA256 `efbd18ba864982ca6436345b1d25d75ad084b3c5f77db6e3bb40186db07b4901`이며 변경하지 않는다. 별도 독립 정적 진단은 `review/C08_REFERENCE_ORACLE_FAILURE_STATIC.json`에 보존돼 있다.

원 FAILED runtime receipt는 12,103 B, SHA256 `8b033baf8c39fd45ec75eadd5ae478c108f34144f1e8f54838224d16e25cf756`다. 원 worker 0.317903 + coordinator 0.180326 + tail 0.05 = charged **0.548229 CPU-s**를 지우지 않는다. 이후 canonical debit amendment가 있으면 최종 ledger가 그 최대 누적 비용을 계속 소유한다.

## 복구 계산의 정확한 범위

새 파일은 `implementation/independent_half_boundary_recovery.py`다. 원 reference나 production module을 import하지 않는다. 실제 원 RESULT/receipt/executed-source manifest/code/primary의 byte pins를 코드에 고정한다.

각 실패 ID에서 원 독립 RESULT의 다음 값을 그대로 읽는다.

```text
/window_reference/<prefixes or observation_bins>/<index>/source/He/number_m3
```

해당 90자리 Decimal **저장 문자열을 정확한 Fraction으로 변환**한다. Decimal constructor는 문자열을 정확히 읽는 데만 쓰며, context-dependent 산술은 하지 않는다. 실제 primary fixture의 `p=0`, `f=1/2`, conditional·not-actual label, 같은 interval과 양의 N을 확인한 뒤 다음 식만 새로 계산한다.

\[
s_{\mathrm{ref}}=N_{\mathrm{saved,independent}}(1-2f)-p=0.
\]

Production의 식별 coefficient나 반올림된 `d_m3`를 oracle로 쓰지 않는다. `N`을 새 fit으로 다시 계산하지 않는다. 새 기대값과 actual primary `s_m3`를 Fraction으로 비교하며, nonzero observed를 작은 floor로 지워 주는 경로는 없다.

선택은 위 네 IDs에 고정한다. 원 failure set이 하나라도 다르거나 새 실패가 추가돼 있으면 거절한다. 원 3,446 PASS rows를 다시 계산하지 않는다. Source/primitive/3×3 solve/Q8/old RR/전파/전체 reference 재실행은 모두 0이다. 새로운 수치 evaluations는 네 개뿐이다. Byte pin 및 기존 boolean inventory 확인·집계는 metadata validation으로 구분한다.

## Root 실행 계약

원 unit cap 40 CPU-s, 1 thread, 256 MiB와 기존 independent role worker reservation 6 CPU-s 및 coordinator reservation 2.05 CPU-s를 유지한다. 새 고유 run ID는 `independent_v2`다. Runtime source와 원 reference를 변경하지 않는다. Root가 새 6-file code manifest와 실제 revised budget을 고정해야 한다.

실제 runner가 실행할 worker argv:

```text
python implementation/independent_half_boundary_recovery.py \
  --failed-reference runs/independent_v1/RESULT.json \
  --primary runs/primary_v2/RESULT.json \
  --out runs/independent_v2
```

이 문서의 명령은 아직 실행 결과가 아니다. Code는 unit/out/attempt environment, create-only reservation, actual admitted revised budget과 frozen contract/input manifest를 확인한다. Worker의 비용 판단은 실제 runner receipt와 immutable ledger에 맡긴다.

## 결과와 합성 승인 schema

새 `runs/independent_v2/RESULT.json`:

- `schema=CR_PARENT_EVENT_INDEPENDENT_TARGETED_RECOVERY_V1`.
- 성공할 경우에만 `status=PASS_SCOPED_EXACT_HALF_RECOVERY`.
- `checks`는 실제 새 네 검사만 담는다. `acceptance.executed/passed/failed`도 새 실제 수다.
- 원 code/result/receipt/primary pins, selected IDs, 원 네 failure rows 및 각각의 독립 saved N 문자열·JSON pointer를 보존한다.
- Fatal input/guard 문제 또는 새 check 실패는 실제 실패로 남으며 accepted composite를 만들지 않는다.

네 검사가 실제로 모두 통과할 경우에만 별도 `ACCEPTED_REFERENCE.json`을 생성한다.

- `schema=CR_PARENT_EVENT_INDEPENDENT_COMPOSITE_V1`.
- `status=PASS_SCOPED_INDEPENDENT_REFERENCE_COMPOSITE`.
- `source_results`는 원 FAILED reference, 원 FAILED receipt, 원 executed reference code 및 새 네-check recovery RESULT의 실제 path/bytes/SHA를 결속한다.
- `checks`는 원 3,450 ID 순서를 유지하면서 **원 3,446 PASS rows를 그대로 복사하고 위 네 oracle rows만 새 검사로 대체한 accepted view**다. 원 FAILED file과 `superseded_oracle_failures`는 그대로 남는다.
- `acceptance.unique_checks=3450`, `passed=3450`, `failed=0`은 accepted distinct checks다.
- `acceptance.actual_evaluations=3454`, `reused_passed_checks=3446`, `newly_evaluated_checks=4`, `previous_failed_evaluations=4`로 실제 평가 history를 따로 기록한다.
- 전체 3,450개를 다시 실행했다는 `executed=3450` 필드를 새 합성 결과에 두지 않는다. Category summary도 accepted metadata view다.
- `full_reference_rerun=false`, `old_successful_checks_reexecuted=0`, `original_failure_erased=false`, `fit_or_Q8_or_old_source_or_RR_replay=0`.

최종 C9와 root admission은 합성 결과와 양쪽 원 evidence를 읽어 채택해야 한다. 중앙 builder의 `files.reference`는 실제 생성된 `ACCEPTED_REFERENCE.json`을 가리키도록 하고, builder는 composite의 두 source RESULT pin을 읽어 원 3,446 rows와 새 네 rows의 정확한 합성을 검증하도록 제한적으로 확장한다. 이 합성은 실제 root admission이나 C9 독립 판정을 대신하지 않는다.

Full physical native25·actual He branch·partner·proton work·physical-heating·global completion/error/budget/currency의 기존 null/false는 바뀌지 않는다.
