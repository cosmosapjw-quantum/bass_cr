# PHYS02G NCP local Codex handoff

## 현재 목표

이번 연구 단위는 `CR-PHYS02G-MOMENT-ENVELOPES-AND-FRONTIER-STRATIFICATION`이다. 저장된 PHYS02E 실제 pulse와 PHYS02F의 검토된 scalar 분석으로 열 방출 지연의 모멘트 범위를 계산했고, PHYS02F가 저장하도록 준비된 adjoint와 마지막 active state를 이용하는 후처리를 추가했다. G의 실제 NCP 과제는 `CR-PHYS02G-NCP-FRONTIER-ENVELOPE`다.

G는 새로운 G 구성·선형계 풀이·pulse·expm을 모두 0회 사용한다. PHYS02F의 기존 실제 과제 `CR-PHYS02F-NCP-ADJOINT-RESIDENCE`가 만든 결과를 읽는다. 현재 ChatGPT가 조회한 GitHub·백업에는 F 실제 반환이 보이지 않았다. 이 사실은 NCP에서 아직 실행되지 않았다는 증거가 아니다. 기존 F 준비 DAG의 `consumed=false`를 현재 예산 상태로 간주하지 않는다.

과학·수치 범위는 `state/SCIENTIFIC_CONTRACT.json`, `state/VALIDATION_CONTRACT.json`, `state/CONVENTION_CLARIFICATIONS.json`, `ncp/NCP_EXECUTION_CONTRACT.json`으로 고정되어 있다. 새 실제 결과에 대한 독립 심사를 거치기 전까지 G frontier 결과는 `AWAITING_INDEPENDENT_ASTRA_REVIEW`다.

## 1. 추가 첨부 없는 정확한 복구

외부 `NCP_START_WITH_BACKUP_IDS_KO.md` 또는 동일 내용의 독립 시작 파일에 실제 G ZIP 이름·크기·SHA256·Drive/Dropbox ID·science commit/tree·검토 판정 식별자가 있다. 그 파일에 지정된 정확한 백업 하나를 사용한다. 이미 동일 바이트의 파일이 있으면 재다운로드하지 않는다.

1. 기존 승인된 Drive/Dropbox 연결 또는 실제 확인한 rclone remote를 사용한다. remote alias, 계정, 경로를 추측하지 않는다. 백업 폴더는 Drive `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`, Dropbox `/BASS_DERIVATION_DOSSIERS_20260912`다.
2. G ZIP의 전체 크기·SHA256을 외부 시작 파일과 대조한다. 새로운 빈 디렉터리에 복구하며 절대경로, `..`, 중복 entry, symlink를 거부한다. 기존 dirty checkout, source, run, return 위에 덮어쓰지 않는다.
3. `BUNDLE_MANIFEST.json`의 schema는 `cr-phys02g-self-contained-bundle.v1`이다. 열거된 payload와 manifest 자신 하나가 정확한 전체 entry 집합이어야 한다. 모든 크기·SHA256, G unit의 `FILE_MANIFEST.json`, `SCIENCE_COMMIT_RECEIPT.json`을 확인한다.
4. G ZIP의 `dependency_payload/CR_PHYS02F_20261011_39e27281_HANDOFF.zip`은 이전 완전한 F ZIP의 바이트 그대로다. 크기 `26927005`, SHA256 `9d91d2971eab2db05e0039fe1fc2a5827086a28d585e792d56f6851840e6ebef`다. 필요할 때 별도의 빈 F source root에 복구한다. 이 안에 F 실행 코드·538개 의존 파일·실제 E 반환 family·두 canonical Astra v4.0.0 하네스가 들어 있다. 추가 사용자 전달 파일이 필요하지 않다.
5. F ZIP의 `BUNDLE_MANIFEST.json` schema `cr-phys02f-self-contained-bundle.v1`, manifest SHA256 `3fae031ded7d1760f11fe6936f660227c55135c6068ce11a0dd73c8551a31ede`, 실제 science commit `39e272815ef13069d7c54fa8c50eab4103f14a79`와 source identities를 대조한다. F core와 이미 소비되었을 수 있는 예산 기록을 수정하지 않는다.
6. 모델 표시 이름에 `Pro`가 있다는 이유만으로 exact router alias를 만들어내지 않는다. 이 프로젝트가 채택한 canonical Astra v4.0.0 흐름을 보존한다. 후보·계약·물리 판단은 Astra, 고정 계약 구현은 lower worker, 최종 판정은 후보·허용조건·구현에 참여하지 않은 independent Astra다. 요청한 모델 label을 backend 인증으로 쓰지 않는다.

실행 소스 복구는 R3다. 통상 업로드의 R1 성공·ID·metadata 확인과 구별하여 실제 달성한 수준을 기록한다.

## 2. 먼저 NCP의 기존 F 실행을 확인

기존 bass_cr 작업 루트, 실제 프로세스와 작업 로그, F reservation/completion/return family를 확인한다. 읽을 범위는 이 과제와 관련된 작업으로 한정한다. 별도 파일 요청으로 사용자를 멈추게 하지 말고, 현재 접근 가능한 실제 호스트와 백업 자료를 먼저 사용한다.

- **이미 F가 실행 중이면:** 해당 작업의 원래 로그·예산을 이어 관찰한다. 두 번째 F를 시작하지 않는다.
- **F가 완료되었으면:** 원래 `RETURN_FAMILY_MANIFEST.json`이 있는 wrapper outdir를 사용한다. 외부 envelope 안에 보관했다면 해당 원본 inner family를 정확히 복구한다. 원본 family를 새로 쓰거나 빈 성공 기록을 만들지 않는다.
- **F가 실패했거나 reservation이 소비되었으면:** 최초 실패·실제 소모량·남은 불확실성을 보존한다. 이 G 프롬프트는 F 재시도 예산을 발급하지 않는다. 승인된 기존 범위에서 원인 분류와 수집을 완료하고 실제 필요한 다음 변경을 명시한다.
- **실제 호스트 증거로 기존 F가 미예약·미실행임을 확인했으면:** 기존 F 계약의 최초 한 번만 수행한다. 아래 순서를 적용하며 새 G 예산과 합산하여 4G·20solve 등으로 늘리지 않는다.

마지막 경우에만 F source root에서, 실제 버전이 확인된 interpreter로 다음을 실행한다. 이전 NCP 경로 `/root/bass_cr_phys02d_ncp_20261011/venv/bin/python`은 확인 후보일 뿐 존재·버전을 가정하지 않는다.

```sh
<verified-python> research/cr_phys02f_20261011/ncp/launch_residence.py --plan
<verified-python> research/cr_phys02f_20261011/ncp/launch_residence.py --preflight
<verified-python> research/cr_phys02f_20261011/ncp/run_and_collect.py \
  --run-dir /ABS/NEW_PHYS02F_RUN \
  --out /ABS/NEW_PHYS02F_RETURN
```

`--plan`의 실제 `admission_status`를 읽는다. exit 0만으로 READY를 선언하지 않는다. F는 fullBED → legacy, 저장 9600점(3200+6400), G 최대 2회, resolvent block 2개, triangular solver API 10회, pulse/expm 0회, coordinator 전체 900초다. 정확한 Python 3.12.3 / NumPy 2.4.2 / SciPy 1.17.0과 모든 수치 pool 1을 유지한다. 실제 cgroup·affinity·quota와 reserve를 확인하며 reserve 후 working RAM 12 GiB 이상, disk 8 GiB 이상, CPU 1 이상을 요구한다. 재구성 G의 exact CSC identity가 원본 E와 일치하기 전 resolvent를 예약하지 않는다.

별도의 `--execute` 후 wrapper를 다시 부르지 않는다. wrapper는 execute 1회와 finally collect 1회를 소유한다. ZIP 후 생성되는 `WRAPPER_COLLECTION_EXIT.json`, `WRAPPER_ACTUAL_EXIT.json` 및 원래 `RETURN_FAMILY_MANIFEST.json`을 반드시 보존한다. 정상 흐름에 별도 collect를 추가하지 않는다.

## 3. F 실제 family에 G 후처리 한 번

G source root에서 실행한다. `--f-family-dir`은 원본 F wrapper의 outdir이며, 내부 numerical ZIP·원래 family manifest·필수 sidecar가 정확한 집합으로 있어야 한다. 외부 운영 로그가 더 있다면 원본 family와 나누어 보존한다. 새로운 G output과 안정적인 G ledger는 source와 F family 밖에 둔다. 매번 다른 ledger를 만들어 중복 reservation 방지를 무효화하지 않는다.

```sh
<verified-python> research/cr_phys02g_20261011/ncp/postprocess_frontier.py --plan
<verified-python> research/cr_phys02g_20261011/ncp/postprocess_frontier.py \
  --plan --f-family-dir /ABS/EXISTING_F_RETURN_FAMILY
<verified-python> research/cr_phys02g_20261011/ncp/postprocess_frontier.py \
  --execute --f-family-dir /ABS/EXISTING_F_RETURN_FAMILY \
  --out /ABS/NEW_PHYS02G_OUTPUT \
  --ledger-dir /ABS/STABLE_PHYS02G_LEDGER
```

첫 plan에 F family가 없으면 `WAITING_FOR_F_ACTUAL_RETURN`가 정상적인 준비 상태다. 실제 실행은 F source·family·내부 ZIP identity, 필수 종료·예약·완료·parity 기록과 G의 고정 코드·독립 준비 판정이 모두 결속되어야 허용된다. 검증 실패를 막기 위해 파일을 고치거나 약한 검증 모드로 바꾸지 않는다.

G coordinator 예산은 **후처리 1회·90초**이며 G/선형계/pulse/expm은 전부 0회다. 실제 runtime도 Python 3.12.3 / NumPy 2.4.2 / 설치된 SciPy 1.17.0, pool 1을 요구한다. 모든 F family/ZIP entry의 bytes·SHA와 frozen F source를 확인한 뒤 `allow_pickle=False`로 배열을 읽는다. 저장 E, 두 출생 source, 마지막 pulse active state는 정확히 일치해야 한다.

## 4. 물리 해석과 실패 기준

열 정규화 측도 `dF=K(tau)d tau/H0`의 survival `P(tau>t)`를 계산한다. 이것은 입자 생존율이나 전체 주입 에너지 중 지연된 비율이 아니다. T 시각 state i의 future-heat weight는 `q0_i*xT_ij/H0_j`이고 조건부 모멘트는 `a_i=T0*q1_i/q0_i`, `b_i=2*T0^2*q2_i/q0_i`다. 기존 residence weight `q0_i*w_ij`와 구별한다.

- 상태별 모멘트 → 출생별 모멘트 → pooled 모멘트의 질량·1차·2차 모멘트를 각각 확인한다. 모델별 두 출생 열과 selected 결과를 모두 남긴다.
- 각 nonnegative 2-moment survival bound를 가중합하고 기존 unconditional/pool/birth 범위와 교집합을 취한다. 이 교집합을 주어진 유한 연산자 클래스에서 최적이라고 주장하지 않는다.
- T에서 residual survival은 정확히 `1-p`다. bound의 우극한이 달라질 수 있지만 물리 CDF의 점프가 아니다.
- `q0=0`이면 `q1=q2=0`이어야 한다. 이 zero-yield 상태는 명시적으로 기록하고 나눗셈을 하지 않는다. 양의 heat weight에 비양의 조건부 평균, 음수 값, 음의 variance가 나오면 새로운 확률 표현은 성립하지 않는 것으로 분류한다. clipping이나 임의 floor로 통과시키지 않는다.
- 기존 scalar와의 일치, state→birth→pool 범위가 좁아지는 관계를 고정 허용오차로 확인하고 signed residual을 보존한다.
- 50%, 90%, 95%, 99%, 99.9% 방출시간은 상·하한과 끝점 조건으로 보고한다. 실제 CDF를 밖으로 보간·외삽한 분위수나 적합한 대표 시각으로 바꾸지 않는다. 모든 열이 정확히 방출되는 유한 종료시간은 두 모멘트로 보증하지 않는다.
- 저장 FP64 모멘트를 정확하다고 놓은 수학적 범위와 수치·물리 오차의 인증 범위를 구별한다. Decimal 검산은 입력 문자열에 대한 산술 비교일 뿐이다.

실패 시 actual command, UTC, wall, 실제 exit, 원본 stdout/stderr, source/code/runtime identity, 이미 예약한 G 후처리 기록을 보존한다. 원본 F 실행이 실패한 경우 G 후처리 성공으로 바꾸지 않는다. 이미 완료한 model이나 이전 전체 suite를 자동 반복하지 않는다.

## 5. 독립 판정과 완전한 반환

새 independent Astra reviewer가 실제 F 원본 family와 G 결과를 함께 검토한다. 기존 G 심사는 준비 코드·직접 유도·저장 scalar 분석 범위이며 미래 actual result까지 승인한 것이 아니다. reviewer는 후보·허용조건·구현에 참여하지 않아야 한다. root의 자기 검토만 있으면 actual frontier claim은 HOLD를 유지한다.

다음 gate는 유지한다: `PHYS02_DELAY OPEN`, `production_history HOLD`, `atomic_G02 UNRESOLVED`, `b_grid NO_GO`, `all_bound OPEN`, `R17B2B NO_CERTIFIED_SOURCE_SHARPENING`, `CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED`. named 9600 finite-operator 진단을 continuum tail·cosmic production·NCP64 scaling으로 승격하지 않는다.

반환에는 원본 F family 전체, G source/unit·actual output·ledger reservation·actual exit, 복구/환경/명령 외부 로그, 새 독립 판정과 검토된 파일 identity를 모두 담는 create-only outer envelope를 만든다. 원래 F ZIP와 manifests는 변경하지 않는다. G output이 F family를 identity로만 참조하면, 그 참조만을 완전한 전달 파일이라고 부르지 말고 실제 F family도 outer envelope에 포함한다. `RETURN_MANIFEST.json`은 자기 자신을 제외한 모든 payload bytes·SHA와 정확한 entry 집합을 열거한다.

Git 반환은 외부 시작 파일이 지정한 G 게시 branch의 실제 최신 head가 고정 science commit의 descendant인지 확인하고, 추가 변경이 publication 범위뿐인지 대조한 후 그 head에서 새 additive return branch와 draft PR로 게시한다. 필요한 actual F와 G 반환은 각각 별도 `research/..._ncp_return_...` 경로에 추가한다. 기존 dirty 작업·과거 source·실패를 보존하고 merge·force push·history overwrite는 하지 않는다.

기존 Drive와 Dropbox 폴더에 완전한 새 outer return family와 짧은 시작/요약 파일을 고유 이름으로 올린다. R1은 provider 성공·정확 ID/ref·size·제공되는 hash를 확인한다. 제공되지 않는 SHA 때문에 raw readback을 반복하지 않는다. source 복구나 실제 불일치가 있을 때만 해당 범위의 R3를 수행한다.

최종 답변은 실제 수행된 F/G 여부와 예산, 모델별 방출시간 범위의 개선, source birth와 frontier/residence의 구별, 독립 판정, 유지된 gate, 실제 exit, 새 PR/head/tree, 두 백업의 정확한 ID·크기·SHA256을 포함한다. 추가 첨부 없이 다음 세션이 같은 원본으로 이어갈 수 있어야 한다.
