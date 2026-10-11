# PHYS02H 최신 실제 반환 intake

## 판정

새 실제 반환 PR39와 PR40를 exact commit으로 읽었다. 두 반환은 모두 `MISSING_PERSISTED_OPERATOR_VALUES`이며 F operator-binding HOLD와 G frontier BLOCKED가 유지된다. PR40는 180초 한도 안에서 끝난 실제 읽기 전용 진단의 새 독립 판정을 제공한다. 원래 CSC 값 쌍이나 새 residence/frontier 수치 결과는 제공하지 않는다. 완료된 진단을 다시 실행할 이유는 없다. 이 intake는 다음 물리 계약의 설계·승인 또는 독립 최종 심사가 아니다.

| 반환 | exact head | tree | 실제 독립 판정 |
|---|---|---|---|
| [PR39](https://github.com/cosmosapjw-quantum/bass_cr/pull/39) | `0c1379efe9b60d70d9cdb69f447eeb62c8720d13` | `5a612fe8afe78bc1bf5f290e9628fe5601854c45` | `ACCEPT_FACTUAL_TYPED_HOLD_CLOSEOUT` |
| [PR40](https://github.com/cosmosapjw-quantum/bass_cr/pull/40) | `839309f6f1edc69e3c24f4d34cc8adba4f7a161f` | `89adf2564bdbc173398e946745e613fe83c04283` | `PASS_SCOPED_READ_ONLY_INTAKE` |

두 커밋의 직접 부모는 모두 PR38 게시 head `f5ac634e67ab17e8820eed8f53d625b6c230a252`이다. 둘은 별개의 sibling이다. 같은 `research/cr_phys02g_operator_intake_return_20261011/` 아래에 추가됐고 `REPORT_KO.md`의 bytes가 서로 다르므로 이 intake는 `pinned/pr39/`와 `pinned/pr40/`로 분리 보존한다. 한 반환을 다른 반환 위에 복사하지 않는다. PR37과 PR38의 head는 지난 전달본과 동일했다. 모두 open draft이며 merged=false다.

## 실제 명령·예산

PR40의 최초 supervisor 시작은 2026-10-11 08:19:34.739130 UTC, 보완 종료는 08:21:01.817706 UTC다. 같은 180초 창에서 87.078602552초가 흘렀다. 이 창은 닫혔다.

| 명령 | 실제 wall | 실제 exit |
|---|---:|---:|
| `intake_readonly.py` | 1.968340949초 | 0 |
| `intake_supplement.py` | 0.164529745초 | 0 |

두 명령은 `/root/bass_cr_phys02d_ncp_20261011/venv/bin/python`으로 실행됐다. 실제 command/cwd/UTC/timeout/코드 SHA 및 raw stdout·빈 stderr는 `pinned/pr40/.../diagnostic/`에 있다. 첫 main이 timestamped E run basename을 놓친 것을 원본 그대로 보존했고, 원래 실행 기록의 `--run-dir`를 직접 사용한 보완을 같은 창 안에서 수행했다. 두 내부 측정시간과 supervisor wall은 중첩되므로 합산하지 않는다. Exit0은 metadata 수집 종료이며 F/G 과학 성공이 아니다.

PR39는 별도 사실형 closeout이다. 진단 elapsed/query count는 원 기록에서 측정되지 않아 null이다. raw command event 목록을 완전한 진단 질의수로 바꾸지 않았다. 180초 준수도 주장하지 않는다. 원래 `OUTPUT_RECEIPT_MISSING` 과정 오류와 첫 reviewer exit124를 유지한다. Exit124는 response deadline mismatch이며 backend 부재나 과학 FAIL을 뜻하지 않는다.

PR39·PR40의 새 G/resolvent/solve/pulse/expm/F retry/G frontier/저장 배열 비교는 모두0이다. 이전 실패 F의 G 예약/완료1/1 및 execute/collect/wrapper exit1/0/1은 계속 소비된 실행으로 보존한다. 원래 G frontier 1회·90초 준비 allowance는 미소비·비활성이다. 전체 전역 실행목록의 완전성은 주장하지 않는다.

## 원본 경로와 결손 입력

PR40에서 원래 E 실행에 연결된 `/root/CR_PHYS02E_NCP_20261011_0412/actual_run_20261011T0418Z`의 일반 파일23개를 조사했다. 두 2,846,750B pulse NPZ는 아래 다섯 member만 담는다.

`sample_u.npy`, `pulse_states.npy`, `integrator_states.npy`, `energy_eV.npy`, `source_vectors.npy`

- fullBED NPZ SHA256: `52a582b3caf7a26929a5f7dda11a332ba87a933154f9f4cdd2b1346213306128`
- legacy NPZ SHA256: `3c44da3a46f8387b7f13fecea4036b22842461de588d489dffe3642990f8d761`

원래 F run `/tmp/CR-PHYS02F-EXECUTION-20261011.euer7hqa/run`은 이 진단 호스트에서 FileNotFoundError였다. F의 기록된 `/home/cosmosapjw/.local/lib/python3.12/site-packages/numpy.libs/libscipy_openblas64_-096271d3.so` 역시 이 호스트에서는 없었다. 기록으로 식별되는 별도 cache root는 없었고 unbound cache 채택0이다.

PR39는 이름이 기록된 F run/external_logs/return, `/tmp/CR-PHYS02E-RESUME-20261011-naaftoyz`와 E recovery archive member 목록을 조사했으며 pair를 찾지 못했다. PR39의 `/home/cosmosapjw/...` 계열 조사와 PR40의 `/root/...` 계열 호스트 조사를 서로 같은 실행으로 합치지 않는다. 두 결과 모두 명시한 경로의 관측이며 다른 위치·호스트 전체의 부재를 증명하지 않는다.

필요한 결손은 원래 reference와 failed-current 각각의 CSC `data/indices/indptr` 값 전체와 해당 원래 실행에 연결된 저장 출처다. 현재 fingerprint만으로 차이 개수, 절대/상대/ULP 크기, ΔA, heat row 차이, roundoff-only, 수치·물리 동등성을 정할 수 없다. 새로 만들 연산자를 원본으로 소급 채택할 수 없다.

## Runtime provenance

PR40의 실제 Python은3.12.3이고 실행파일 `/usr/bin/python3.12`는8,020,928B, SHA256 `1643dacd9feaedc58f3cc581e4d22577dfe25c09b10282936186ccf0f2e61118`이다. NumPy2.4.2/SciPy1.17.0 metadata, 현재 library 파일들의 hash를 읽었으며 numerical import는 하지 않았다.

- 현재 NumPy OpenBLAS 파일25,364,017B, SHA256 `c0f0784c075afdeb2d57cb78e6225221f7c97ef8d03e512b3c98e105054e73c2`.
- 현재 SciPy OpenBLAS 파일24,805,561B, SHA256 `8fb864c29cac4b25f6e2c139491ea96f2724dde42d51394f84e9c4a622e34790`.
- CPU model 기록은 Intel Xeon Gold5220이다. 이 정보 자체는64core/128GB resource admission이나 scaling 측정이 아니다.
- 과거 E의 SkylakeX/F의 Haswell은 저장 provenance다. 현재 dispatch는 `NOT_OBSERVED_WITHOUT_NUMERICAL_IMPORT`다.
- 과거 runtime receipt에 original binary hash는 없었으므로 현재 파일의 hash를 과거 bytes 동일성으로 올리지 않는다.
- `wheel_sha256`은 WHEEL metadata 텍스트 hash이며 whole-wheel archive hash가 아니다.
- 실제 allowlist의8변수는 모두null이었다. 후보 C04의 GOTO_NUM_THREADS는 조회되지 않았다. 대신 LD_LIBRARY_PATH/VECLIB_MAXIMUM_THREADS가 읽혔으며 둘 다null이었다. 독립 심사는 이를 비차단 한계로 보존했고 닫힌 진단을 다시 열지 않았다.

독립 review의 requested model/effort는 gpt-6-astra/xhigh지만 관측표시는 generic GPT-6다. Backend NOT_ATTESTED/exact alias MODEL_UNRESOLVED를 유지했다. PR39는 controller transcription과 미인증 backend라는 더 좁은 근거 상태를 유지한다.

## 새 archive의 필요성 판단

PR40의 완전 ZIP은89,785,721B, SHA256 `6c9ffa8e781a5d8db45eab906e609c09eb4cdd0b006b3b534cf1560fc0e6f4c4`이며 payload42개+manifest1개다. Exact commit의 manifest를 직접 읽었다. 이전 완전 G/F source outer58,470,931B와 실제 실패 F family를 그대로 담고, 새 text 진단·helper·심사를 추가한다. 원래 CSC 값 쌍이나 새 물리 수치 결과를 추가하지 않는다.

이번 경량 G-R01 또는 이론 후속에는 기존 저장 입력과 새 raw text 증거면 충분하다. 따라서 이 intake는89.8MB 또는68.1MB 새 archive를 다시 내려받아 전체 복원하지 않았다. 이 판정은 새 archive의 R3 복원 성공을 주장하지 않는다.

| 반환 백업 | Drive ID | Dropbox ID | 이번 metadata 대조 |
|---|---|---|---|
| PR39,68,071,016B | `1a8oXMSWdU13s5J7hLbMREe08cjf3GitZ` | `id:BSpOijBcT10AAAAAAD4KBA` | ID/name/size/parent/path 일치 |
| PR40,89,785,721B | `1pTfplUwlt04xLhx-ziwUEquqpJ35Oj7H` | `id:BSpOijBcT10AAAAAAD4KTw` | ID/name/size/parent/path/rev 일치 |

PR39 Dropbox rev는 `65d8c26a231950af03d47`, PR40 rev는 `65d8c614f56930af03d47`다. Provider SHA는 반환되지 않았다. 이 단계는 metadata R1 확인이며 원격 byte restore가 아니다.

## 이번 intake의 증거 범위

Git search는 repo의 updated>=2026-10-11 PR, state all, updated desc, top20으로8건을 반환했다. `phys02` branch 검색은13건과 다음 빈 페이지로 종료됐다. PR39·PR40 외의 새 PHYS02 branch는 그 검색에서 관측되지 않았다. 이는 저장소 밖의 모든 실행 부재를 의미하지 않는다.

33개 text 파일237,581B를 exact commit/raw Git blob으로 확보했고33/33 blob identity가 일치했다. 원시 connector body는 `raw/`, exact bytes는 `pinned/pr39/` 및 `pinned/pr40/`, 파일별 bytes/SHA256/Git blob/조회시간은 `PINNED_FILE_IDENTITIES.json`에 있다. 세부 정규화 결과와 실제 request는 `LATEST_INTAKE_REPORT.json`에 있다.

PR40 판정 `DECISION.json`: 30608B, SHA256 `8be8f80afd50d03eede1ea38f7908a087592bda8347279ce87a06f6863cf142c`.
PR39 `INDEPENDENT_REVIEW.txt`: 1716B, SHA256 `41a345f062b7137a8846b30f4d4e4bd8d11ce1440848551fb1388d20bd257687`.

빈 stderr raw URL 두 번은 connector가 empty content를 거부했다. 이후 exact empty Git blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`을 직접 읽어 두 경로에 정확히 복구했다. Percent-encoded branch URL 두 건의 INVALID_ARGUMENT은 보존하고 PR head metadata와 branch search로 범위를 확인했다. 진단·과학 suite·NCP host/cache 조회·물리 실행·remote mutation·대형 다운로드는 이 intake에서 모두0이다.

F operator-binding과 inherited physical gates를 유지하고, 완료된 결손 탐색은 반복하지 않는다. 다음 작업은 저장자료로 가능한 경량 수학·구현 진전을 여기서 수행하고 실제로 새로운 불변 입력과 유한 예산이 고정된 무거운 작업만 별도 NCP 계약으로 다루는 것이다. 이 마지막 문장은 연구 분업에 대한 권고이며 새 physics 실행 승인이 아니다.
