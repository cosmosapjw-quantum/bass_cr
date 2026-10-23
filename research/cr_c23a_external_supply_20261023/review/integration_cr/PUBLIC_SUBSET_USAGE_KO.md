# C23A 공개 deposition subset의 사용·재현 안내

이 안내는 부모가 `NEW/deposition/`에 복사할 **49개 공개 파일**에 적용한다. 공개 subset은 우리 Python 구현·결과·수치 provenance와, 선택한 MIT 배포본을 포함한다. 기존 완료 계산을 복구 목적으로 다시 실행하지 않는다.

## 실제 사용 경로

`fs2010_operator.py`의 `FS2010Response`는 table directory를 명시적으로 받는다. 공개 subset에서 사용 가능한 경로는 다음이다.

```text
deposition/external_comparison/21cmFAST/src/py21cmfast/_data/x_int_tables/
```

원 archive용 `upstream/x_int_tables/`는 공개 subset에 포함되지 않는다. 같은 위치에 빈 directory를 만들거나 누락 파일을 0으로 채우지 않는다. MIT mirror의 14개 표는 원 archive와 numeric token이 모두 같고 terminal newline이 달라 bytes는 다르다. mirror를 사용하는 새 입력에는 mirror SHA/Git blob identity를 기록한다.

`consume_mit_mirror_example.py`는 위 공개 경로만으로 사용할 수 있는 작은 helper다. 원 tar·원 C·과거 audit 디렉터리를 요구하지 않는다. operator SHA256, mirror receipt SHA256, 14개 표와 MIT license의 bytes 및 Git blob을 먼저 검사한다. 그 뒤 검증한 operator bytes를 메모리에서 직접 읽어 소비한다. 서로 다른 3-node PL spectrum을 예제로 사용한다. **이 helper는 syntax 확인만 했고 실행하지 않았다.**

사용자 또는 coordinator가 새 worker의 CPU·thread·lease를 배정한 후 그 worker에서 다음과 같이 호출한다. 완료된 기존 run ID를 재사용하지 않으며, 결과 저장은 새 directory와 `open('x')`를 사용한다.

```python
from pathlib import Path
import json
from consume_mit_mirror_example import consume_public_subset

# This path is supplied by the admitted caller, after public-subset checkout.
deposition = Path("/absolute/path/to/cr_c23a_external_supply_20261023/deposition")
output = Path("/absolute/path/to/new_create_only_run")
output.mkdir(parents=True, exist_ok=False)
result = consume_public_subset(deposition)
with (output / "response.json").open("x", encoding="utf-8") as handle:
    json.dump(result, handle, indent=2, ensure_ascii=False, allow_nan=False)
    handle.write("\n")
```

이 예제의 response는 ξ=0.5인 유한 표 응답이다. P19의 광이온화/가열 moments를 spectrum으로 복원하거나, 현재 H/He photo-subflow와 자동 결합하지 않는다. source의 He/H와 helium photon 재흡수, primary binding/post-primary electron ownership, loss time 등은 원 `SOURCE_COVERAGE.json`의 의무로 유지한다.

## 과거 audit script의 의미

공개 subset의 `audit_fs2010_operator.py`와 `benchmark_precontract.py`는 당시 입력·연산·방법을 보존한 증거다. 두 파일은 다음 경로와 run ID를 고정하고 있다.

| 파일 | 원 입력 경로 | 원 출력 |
|---|---|---|
| `audit_fs2010_operator.py` | `upstream/x_int_tables` | `c23a_fast_electron_source_audit_20261023_v1` |
| `benchmark_precontract.py` | `upstream/x_int_tables` | `c23a_precontraction_timing_20261023_v1` |

공개 subset만 받은 상태에서 두 script를 그대로 실행하면 기존 출력 directory의 create-only 검사 또는 원 입력 경로 누락으로 중단된다. 이는 현재 public artifact의 자동 replay 명령이 아니다. 원 provenance를 보존하기 위해 frozen script를 고쳐 완료 실행인 것처럼 취급하지 않는다.

완료 결과의 복구에는 기존 CSV/JSON과 manifest를 사용한다. 새로운 구현 변경을 검증할 필요가 생기면 새 run ID·입력 SHA·승인된 자원을 가진 별도 wrapper를 만든다. mirror 입력을 사용했다면 원 archive의 byte identity라고 기록하지 않는다. 동일 numeric token을 확인한 근거는 재사용한다.

## Attribution과 배포 범위

- 표의 과학적 출처: Furlanetto & Stoever (2010), *Secondary ionization and heating by fast electrons*, [DOI10.1111/j.1365-2966.2010.16401.x](https://doi.org/10.1111/j.1365-2966.2010.16401.x).
- mirror: [21cmFAST commit72d8a2d23702f1b69fbc85abd25d4592a7bcd3f5](https://github.com/21cmfast/21cmFAST/tree/72d8a2d23702f1b69fbc85abd25d4592a7bcd3f5). `external_comparison/21cmFAST/LICENSE`의 실제 내용을 보존한다.
- DarkHistory 선택 파일을 포함할 때는 `external_comparison/DarkHistory/LICENSE`도 함께 보존한다. 이번 numerical provider는 DarkHistory가 아니다.
- 원저자 archive/C에는 명시적 license를 찾지 못했다. 그 source evidence를 MIT mirror와 같은 배포 허가로 기술하지 않는다.
- 우리 `fs2010_operator.py`는 원 C reader를 실행하거나 그대로 복사하지 않은 독립 구현이다.

## 상태

| EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|
| 이 소비 예제 NOT_RUN, syntax만 확인 | 부모가 안내와 helper를 공개 subset에 추가할 수 있음 | 본 안내는 로컬 review 산출물; durable ACK는 부모 책임 | public path/attribution 확인 → caller resource/새 입력 → 필요 시 새 유한 계산 |
