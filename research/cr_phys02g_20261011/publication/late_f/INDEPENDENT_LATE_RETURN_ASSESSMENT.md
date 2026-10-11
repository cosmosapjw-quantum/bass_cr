# PHYS02G 출판 도중 도착한 실제 F 실패 반환의 독립 사실 평가

## 현재 판정

**F: `HOLD_OPERATOR_BINDING_UNRESOLVED`. G 실제 frontier: `BLOCKED_BY_F_HOLD`.** fullBED의 G 생성은 1회 예약·완료됐으나 기준 CSC 값의 동일성 검증에서 중단됐다. residence 결과는 없으며 G frontier를 실행할 실제 F 입력도 없다. 허용되는 다음 작업은 보존된 자료와 원래 환경·저장 CSC 값의 존재 여부를 확인하는 **읽기 전용 진단 intake**다. F 재실행, legacy 자동 진행 또는 G frontier 실행은 승인하지 않는다.

기계 기록은 `INDEPENDENT_LATE_RETURN_ASSESSMENT.json`, **25,839 bytes**, SHA256 **`21660351ae76c3e5b63d1a975cc7a33871f07d06925fe69bf0d0522f1ec613c9`**이다. 이 평가는 이미 고정된 G 후보·과학 계약·수치 결과·독립 판정을 수정하지 않는다. 기존 G 판정 SHA256 `9dd9c623fdd881667b6692ea8c3c9fbac08d545ba821fe33f66c2dbd38322002`는 당시 관측 범위에 대한 기록으로 유지한다. 그때의 제한된 F 반환 미관측은 현재의 실제 실패 관측으로 앞으로 갱신한다.

## 새로 관측된 source와 읽기 범위

[PR37](https://github.com/cosmosapjw-quantum/bass_cr/pull/37)은 2026-10-11 **07:02:57 UTC**에 생성됐다. 직접 조회 당시 open·draft·unmerged 상태이며 파일 **47개 추가, 삭제 0개**다.

| 객체 | 고정 identity |
|---|---|
| PR37 head | `a490ab7af8e7b1b4db9a604293867df8e6d035dd` |
| PR37 tree | `73e5941c887d5ce395fd019cf6722adde086b9f4` |
| 단일 parent | `b21009893b93ed9b7e4af22ac4f480fe4b8e5c4b` |
| F 실행에 사용된 science commit | `39e272815ef13069d7c54fa8c50eab4103f14a79` |
| F science tree | `a0d6229b92092ee055ffe54ba5a9563c7f904aab` |

PR37의 결정문·실행 계약·이전 중단·setup 수정·원시 stderr·실제 exit·예약·완료·입력 preflight·runtime·자원·wrapper·family·backup 기록 **31개를 commit에 고정한 GitHub raw URL로 직접 읽었다.** 각 실제 텍스트의 Git blob SHA를 계산해 변경 목록의 blob과 비교했고 **31/31 일치**했다. SHA256과 길이도 JSON에 기록했다. 전체 47개 복구·manifest 검증은 root와 별도 recovery worker가 담당한다.

원래 E의 `G_COMPLETION_1.json`과 `RUNTIME.json`, F의 입력 manifest와 launch/residence의 실패 경로를 직접 대조했다. source hash는 읽은 자료의 동일성을 보장하며 수치적 동등성이나 물리적 타당성을 대신하지 않는다. 새로운 실험·테스트·행렬 생성·solve는 수행하지 않았다.

## 확정된 실패 위치와 불일치

원시 traceback은 `launch_residence.py:119`의 `operator_parity(identity, ref)` 호출에서 `residence.py:47`의 `OPERATOR_IDENTITY_MISMATCH`가 발생했음을 보여 준다. 소스 순서는 **G 생성 → G completion 저장 → exact parity → 구조 검사 → resolvent 예약 → solve**다. 실제 기록도 parity 성공 및 resolvent 예약 이전 중단과 일치한다.

두 `operator_identity` 객체를 필드별로 비교하면 차이는 **`G.arrays.data.raw_C_sha256` 한 곳**이다.

| 항목 | 기준 E | 현재 F |
|---|---|---|
| G data SHA256 | `6bd1d6aeeaccf4cc717229e3f9beff0cf072a157c844dd75ba2353be5f15f4cd` | `8e33e916c4a24d57c9dad0f82ef046a81a818437e64cafb2e580d4c8809ea3fa` |
| CSC shape | 9,611 × 9,611 | 동일 |
| nnz / data 길이 | 36,193,027 | 동일 |
| data dtype | `<f8` | 동일 |
| indices·indptr | 원시 SHA 및 shape·dtype | 동일 |
| 저장 energy | 9,600개, 원시 SHA·shape·dtype | 동일 |
| method bindings | parent-object guards·qualname·기록 module | 동일 |

current completion 파일 자체는 **2,562 bytes**, SHA256 `5190e333ca53badb0539e41a0acd408953ff3a7f7764a2e3366258002b8c32a5`다. 기준 completion 파일은 **2,583 bytes**, SHA256 `9f152a1f475a2f102b2c068a468da7be770f387a7992da79b06ac45b3f8e936c`이며 F의 `actual_fullBED_G` 입력 pin과 일치한다.

이 결과로 알 수 있는 것은 **고정된 exact-operator 입력 binding이 성립하지 않았다는 사실**이다. 해시만으로 서로 다른 원소 수, 최대 절대·상대 오차, ULP 차이 또는 물리적 영향은 알 수 없다. roundoff-only, 수치적 동등성, scientific-integrity failure 모두 입증되지 않았다. 현재 계약에서 G는 이미 계산된 pulse와 adjoint/resolvent를 연결하는 정확한 frozen input이므로, 기준 해시 교체 또는 tolerance 완화로 통과시킬 수 없다.

## 실제 소모와 실행 상태

이는 기록상 승인된 **local-host 실행**이며 이 자료만으로 NCP cloud 실행을 입증하지 않는다. 기존 archive의 prepared 상태를 새 실행의 현재 상태로 재사용하면 안 된다.

| 작업·호출 | 실제 관측 |
|---|---:|
| plan | 1회, exit 0 |
| preflight | 1회, exit 0 |
| wrapper | 1회, exit 1 |
| wrapper 내부 execute | 1회, exit 1 |
| finally collection | 1회, exit 0 |
| G 예약 / 완료 | **1 / 1**, fullBED |
| resolvent 예약 / 완료 | 0 / 0 |
| triangular solve 예약 / 실제 | 0 / 0, 실제 bounds `[0,0]` |
| pulse / expm / retry | 0 / 0 / 0 |
| legacy 시작 | 없음 |
| residence 결과 | 없음 |

coordinator는 **06:41:06–06:42:54 UTC**, elapsed **107.954172934 s**다. wrapper 내부 execute receipt는 **108.148999693 s**, 가장 바깥 wrapper receipt는 **109.790418950 s**다. 이들은 서로 포함되는 시간이며 합산하거나 coordinator 전체 시간을 순수 constructor 시간으로 부르면 안 된다. collection exit 0은 실패 반환을 수집했다는 의미다. 실행·wrapper exit 1을 성공으로 바꾸지 않는다.

기존 G≤2 등의 상한에 남은 수량이 있다고 해서 실패 뒤 fullBED 재시도 또는 legacy 후속 진행이 허용되지 않는다. **현재 관측된 F allocation은 최소 G 1회를 소모했고 terminal HOLD다.** 이번 자료가 모든 전역 실행의 완전한 목록을 보장하지는 않는다. 어느 경우에도 준비 이력의 `consumed=false`로 되돌리지 않는다.

초기의 `OSError(30, 'Read-only file system')` 중단은 실제 plan/preflight/wrapper 이전이며 당시 물리 소모는 0이다. 이어진 기록은 동일 allocation·준비 deadline을 유지한 1회 transport/setup 수정 후 첫 실제 과학 실행이다. 그 이전 중단과 이후 parity 실패를 구분해 보존해야 한다.

## Runtime와 원인 미확정 범위

기준 E와 현재 F의 기록은 Python **3.12.3**, NumPy **2.4.2**, SciPy **1.17.0**, OpenBLAS **0.3.31.dev**, numerical thread **1개**로 같다. 그러나 OpenBLAS runtime이 보고한 architecture/dispatch는 **기준 `SkylakeX`, 현재 `Haswell`**로 다르다.

이것은 관측된 provenance 차이이며 실패 원인이라는 증명은 아니다. shared-library basename과 버전 문자열이 같아도 실제 binary byte identity나 build flags가 같다고 단정할 수 없다. 현재 기록은 원래 binary SHA·원래 CPU feature 호환성·전체 dispatch 설정을 충분히 고정하지 않는다. 지원 여부가 확인되지 않은 dispatch를 강제로 설정해서는 안 된다.

실행 전 host probe는 after-reserve working RAM **14,410,289,152 bytes**, disk **311,643,226,112 bytes**, effective CPU **24개**, admitted true를 기록한다. build 직전 기록도 working RAM **15,365,836,800 bytes**, disk **311,643,906,048 bytes**, admitted true다. 따라서 현재 자료의 실제 중단 원인은 기록상 자원 gate가 아닌 exact operator binding gate다. 자원 여유가 있었다는 사실도 수치 동등성을 보장하지 않는다.

## 기존 Astra 실패 심사의 provenance 평가

PR37의 `CR_PHYS02F_ASTRA_ACTUAL_FAILURE_DECISION_20261011.md`는 **2,461 bytes**, SHA256 **`6721230ca5379da25957a51f01b235385dad29a994709aab2075af37eb69c7f9`**다. 이 문서는 `/root/astra_cr_phys02c_execution_review`의 기존 Astra-ultra task가 read-only 4 commands로 검토한 결과를 controller가 전사했다고 명시한다. requested/legacy model label이 independently observed backend identity가 아니라는 제한도 스스로 적고 있다.

PR37 변경 목록과 제공된 outer archive 인벤토리에서 해당 reviewer의 원시 4-command session transcript 또는 독립적으로 관측된 backend attestation은 식별하지 못했다. 따라서 **그 reviewer의 독립성·backend는 전사된 역할 기록 이상의 수준으로 입증할 수 없다.** 이번 심사는 그 제한을 유지한다. 다만 해당 문서의 HOLD 결론, exact data SHA 차이, 실행 소모와 solve 이전 중단은 이번 심사자가 별도로 읽은 원시 receipt·기준 metadata·고정 소스 순서와 일치한다. 이 일치는 F 또는 G 성공 승인이 아니다.

executor도 요청 모델은 `gpt-6-sol/medium`, transport-selected identity는 client에서 미노출, backend는 `NOT_INDEPENDENTLY_OBSERVED`로 기록돼 있다.

## 백업과 저장 CSC 값의 현재 가용성

| 객체 | bytes | SHA256 |
|---|---:|---|
| 실제 실패 return ZIP | 30,587,901 | `f64b263fd8dd99121d3114a66a2a70616b383cbd5ce0823acd45f9893babdd8d` |
| 전체 failure backup tar.gz | 30,522,967 | `0b6d54f5811f4f8ee651a79e734c9dddf37a722133bd51acad3fcf16c110a4e5` |

현재 Git backup receipt는 Drive **`1r2KGKDNTH09ul2C2qQhRVxHn0FNVQ0B_`**, Dropbox **`id:BSpOijBcT10AAAAAAD4IqA`**를 기록한다. 원래 receipt의 검증 수준은 `R1_UPLOAD_ACK_AND_METADATA_MATCH`이며 당시 remote byte restore는 `NOT_EXECUTED`다. 현재 root는 이 Dropbox 객체를 실제 복구해 outer/inner SHA가 맞았다고 별도로 보고했고, 전량 manifest/Git binding은 별도 recovery worker가 처리 중이다. 이번 평가는 그 별도 R3 receipt를 대신하거나 이미 완료됐다고 앞당겨 기록하지 않는다.

심사자가 직접 읽은 outer archive 인벤토리는 member 70개·regular file 64개다. nested return ZIP은 **660개 entry**를 가지며 wrapper가 기록한 659개는 payload file 수다. 14개 NPZ의 필드 이름을 archive metadata로 확인했지만 현재 또는 기준 G의 CSC `data/indices/indptr` 값 payload는 식별하지 못했다. 알려진 G completion은 fingerprint 자료다. 새로운 F residence 수치 결과도 없다. 인벤토리 확인에서 배열값 계산이나 G 재구성을 수행하지 않았다.

따라서 **현재 반환만으로 수치 차이를 계산할 수 없다.** 원래 실행 위치나 기존 추가 백업에 CSC 값이 이미 저장돼 있는지, 원래 numerical-library/build/CPU-dispatch provenance가 남아 있는지가 최소 추가 입력이다. 이것은 사용자에게 새 파일 첨부를 요구한다는 뜻이 아니다. 전달받은 전체 백업과 명시적으로 식별된 기존 원본 위치부터 조사한다.

## NCP local Codex에 넣을 현재 지시

아래 지시는 배포 묶음의 가장 먼저 읽는 current-status/late-return 문서에 넣어야 한다. 기존 core START의 준비 당시 조건부 실행 분기보다 **현재 관측된 F HOLD**가 우선한다.

```text
현재 작업은 READ_ONLY_OPERATOR_BINDING_DIAGNOSTIC_INTAKE다.

PHYS02F 실제 결과는 HOLD_OPERATOR_BINDING_UNRESOLVED다. fullBED G 예약/완료 1/1,
resolvent/solve/pulse/expm 0, execute/wrapper exit 1, finally collection exit 0이다.
실제 residence 결과가 없으므로 PHYS02G frontier 실행은 BLOCKED_BY_F_HOLD다.
기존 prepared consumed=false 또는 명목상 남은 G allowance로 재실행하지 마라.

보존된 실제 F failure ZIP, 외부 WRAPPER_COLLECTION_EXIT.json 및
WRAPPER_ACTUAL_EXIT.json, 원시 stderr, 실제 exit/runtime, 예약/완료 기록과
고정 기준 E identity를 읽고 현재 상태를 기록하라. source와 reference SHA는 유지하라.

명시적으로 식별된 원래 E/current F 실행·source·기존 backup 위치에서 이미 있는
numerical-library build/binary/CPU-dispatch 기록 및 저장된 CSC 배열의 존재를 조사하라.
기존 shared-library를 읽어 hash를 얻는 것은 가능하나 import·rebuild·install·dispatch
설정 변경은 하지 마라. 실제 파일이 있으면 path/bytes/hash와 원래 identity의 대응을,
없으면 NOT_FOUND_IN_QUERIED_LOCATIONS와 정확한 조회 범위를 기록하라.

current G data SHA:
8e33e916c4a24d57c9dad0f82ef046a81a818437e64cafb2e580d4c8809ea3fa
reference G data SHA:
6bd1d6aeeaccf4cc717229e3f9beff0cf072a157c844dd75ba2353be5f15f4cd
OpenBLAS dispatch SkylakeX/Haswell 차이는 관측된 provenance 차이이며 원인으로 확정하지 마라.

G 생성·resolvent·solve·pulse·expm·old suite·benchmark·실제 분석 재실행은 0으로 유지하라.
launch --execute, wrapper 재제출, fullBED/legacy 후속 실행 및 G frontier --execute 금지.
reference SHA 교체, tolerance 완화, clipping, 다른 operator/source-grid 대체 금지.
지원하지 않는 CPU dispatch를 강제로 설정하지 마라.

결과는 발견/미발견 파일 identity, 기존 provenance와 카운터, 정확한 최소 blocker를 담은
사실 inventory로 반환하라. 저장된 양쪽 CSC 값이 없으면 수치 오차를 추정하지 말고 HOLD로
끝내라. 새 G 재구성은 새로운 유한 계약·할당이 필요하다. 기존 저장 배열의 값 비교도
그 입력과 범위를 별도로 고정한 진단 작업으로만 수행한다. 이번 전달은 새 물리 실행을
승인하지 않는다.
```

이번 late intake는 기존 G의 exact inequality 유도·점검된 FP64 저장 평가·미실행 frontier 준비라는 주장 상한과 G-R01의 8/10 끝점 제한을 유지한다. 상속된 물리 gate도 그대로다. 이번 심사자의 G·resolvent·solve·pulse·expm·생산자 테스트·실제 분석·원격 변경은 전부 0이다. 작성한 파일은 이 독립 late-return JSON과 설명문 두 개뿐이다.
