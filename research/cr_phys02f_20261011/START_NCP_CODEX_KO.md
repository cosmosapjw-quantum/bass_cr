# PHYS02F NCP local Codex handoff

이 문서는 완전한 PHYS02F handoff ZIP 안의 실행 절차다. ZIP 밖 `NCP_START_WITH_BACKUP_IDS_KO.md` 또는 동일 내용의 독립 시작 파일에는 실제 ZIP 이름·Drive/Dropbox ID·SHA256·science commit·최종 독립 판정 식별자가 결속된다. 추가 사용자 첨부 없이 그 백업에서 복구한다.

## 목표와 권한

`CR-PHYS02F-NCP-ADJOINT-RESIDENCE`를 새 작업으로 한 번 실행하고 원시 결과·실제 종료·백업·독립 판정을 반환한다. 사용자에게 이미 승인된 bass_cr 계속 연구 및 create-only 이중 백업 범위다. ChatGPT에서 구현·scalar 분석·작은 검증을 마쳤다. NCP는 실제 큰 연산자 구성·풀이와 결과 수집을 수행한다.

기존 PHYS02E 실제 작업은 PR35 commit `459018cffc3d57dcf8670997b4029fb6891e8101`에서 완료되었다. 그 G/pulse 2/2 및 실행 예산은 소모되었다. 과거 E NEXT_DAG의 READY는 보존된 준비 스냅샷이다. 새 F 계약만 따른다.

과학 의미·scope·gate·허용오차는 `state/SCIENTIFIC_CONTRACT.json`과 `ncp/NCP_EXECUTION_CONTRACT.json`이 기준이다. 코드·문서 제작자는 독립 decision reviewer가 될 수 없다. 이 프로젝트의 Astra 역할 정책과 확인 가능한 실제 모델 metadata를 적용하되 도구 호출 model label을 backend 인증으로 기록하지 않는다.

## 1. 정확한 백업 복구

1. 외부 시작 파일이 지정한 ZIP을 기존 Drive 또는 Dropbox 연결에서 정확한 ID로 읽는다. 이미 byte-identical 파일이 있으면 재다운로드하지 않는다. 공유 폴더는 Drive `1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI`, Dropbox `/BASS_DERIVATION_DOSSIERS_20260912`다. 기존 승인된 rclone 경로가 있다면 실제 설정을 확인하여 사용하며 remote alias를 추측하지 않는다.
2. 외부 파일의 ZIP 크기·SHA256을 대조한다. 새로운 빈 디렉터리에서 archive entry의 절대경로·상위 이동·중복·symlink를 거부하고 압축을 푼다. 기존 dirty checkout이나 이전 run 위에 덮어쓰지 않는다.
3. `BUNDLE_MANIFEST.json`은 `cr-phys02f-self-contained-bundle.v1`이어야 한다. 정확한 entry 집합은 manifest가 열거한 files와 manifest 자체 하나다. 모든 payload의 bytes/SHA256을 확인한다. `SCIENCE_COMMIT_RECEIPT.json`의 실제 science commit/tree를 외부 시작 파일과 대조한다.
4. 저장소형 archive root의 `research/cr_phys02f_20261011/FILE_MANIFEST.json`은 `cr-phys02f-file-manifest.v1`, path_basis `repository-root`이다. 이 파일과 정확히 538개 의존 파일, 18개 직접 입력, 새 독립 review가 결속된 사실을 확인한다.
5. 두 canonical Astra v4.0.0 ZIP은 `handoff_harness/`에 포함되어 있다. `START_HERE`와 해당 핵심 지침 및 현재 F state만 읽고, 현재 task와 무관한 이전 full suite를 다시 실행하지 않는다.
6. 새 F `state/NEXT_DAG.json`이 이 task의 READY와 미소모 새 예산을 가리키고, `review/INDEPENDENT_DECISION.json`의 SHA 및 과학·NCP·입력·코드 binding이 맞는지 확인한다. 현재 root가 검토한 scope는 준비·유도·cached 분석·toy 구현이며 실제 NCP 결과까지 승인했다는 뜻은 아니다.
7. 이 복구는 R3 source recovery다. 성공한 일반 업로드의 R1 metadata 확인과 구별해 기록한다.

## 2. 실행 장소와 runtime

소스 밖의 새로운 작업 루트에 `external_logs/`를 만들고, 실제 Python 경로·버전·환경 준비·소스 복구 결과·실제 command를 남긴다. source, run, return은 서로 분리한다. run/return 디렉터리는 wrapper 호출 전에 존재하면 안 된다.

직전 NCP에서 사용한 interpreter는 `/root/bass_cr_phys02d_ncp_20261011/venv/bin/python`이었다. 현재도 존재하고 정확한 버전인지 확인한 경우에만 재사용한다. 경로 존재나 버전을 추정하지 않는다.

필수 버전은 Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0이다. OpenBLAS/MKL/OMP/NumExpr 및 실제 수치 thread pool은 모두 1, OMP_MAX_ACTIVE_LEVELS도 1이다. 장비 표기 대신 실제 affinity, cgroup, quota와 메모리 reserve를 확인한다. 기존 probe는 reserve 적용 후 working memory 12 GiB 이상, disk 8 GiB 이상, CPU 1 이상을 요구한다. NCP64 병렬 성능으로 외삽하지 않는다.

각 명령의 stdout/stderr와 실제 exit, UTC 시작·종료를 외부 로그에 기록한다. `--plan`은 표준 라이브러리로 source·review admission을 검사하며 exit 0 자체가 READY는 아니다. resource probe는 plan에서 `NOT_PROBED_BY_STDLIB_PLAN`일 수 있다. 실제 자원 허용은 worker가 G 예약 전에 검사한다.

저장소형 source root에서 순서대로 실행한다.

```sh
<verified-python> research/cr_phys02f_20261011/ncp/launch_residence.py --plan
<verified-python> research/cr_phys02f_20261011/ncp/launch_residence.py --preflight
<verified-python> research/cr_phys02f_20261011/ncp/run_and_collect.py \
  --run-dir /ABS/NEW_PHYS02F_RUN \
  --out /ABS/NEW_PHYS02F_RETURN
```

`--preflight`는 정확한 runtime, source NPZ 두 개와 pulse NPZ 두 개의 전체 바이트 및 의미·immutable array를 확인하고 G를 만들지 않는다. 이후 worker가 같은 필수 preflight를 자체적으로 수행한다. 이는 임의적인 반복 suite가 아니라 실행 계약에 결속된 보호 단계다.

`--execute`를 별도로 먼저 실행한 다음 wrapper를 다시 실행하지 않는다. wrapper가 execute 한 번과 finally collect 한 번을 소유한다. 실행 중인 run 또는 실패한 run에 같은 승인을 재사용하지 않는다.

## 3. 실제 수치 범위

- 모델 순서: fullBED → legacy.
- 저장된 9,600점 E, 두 출생 source 열, 저장된 pulse의 u=1 active 상태를 그대로 사용한다.
- G 최대 2회, resolvent block 최대 2회, 희소 삼각계 풀이 호출 최대 10회.
- 모델당 q0/q1/q2 adjoint 3회와 w/v forward 2회이며, forward RHS는 두 출생 열이다.
- 새 pulse 0회, expm 0회, 장시간 전파 0회, 이전 전체 suite 0회.
- coordinator `--execute` 진입부터 전체 wall 한도 900 s. 종료 시 owned child process group을 정리한다.
- G가 돌아오면 완료를 기록한다. 그 후 data/indices/indptr의 shape·dtype·raw SHA와 E를 PR35 실제 G 기록과 비교한다. module alias 문자열은 물리 identity가 아니며 실제 parent method object/name binding은 유지한다.
- G identity가 다르면 생성된 G를 이전 G로 간주하지 않는다. `OPERATOR_IDENTITY_MISMATCH`와 이미 소비된 G를 기록하고 resolvent를 예약하지 않는다.
- 저장된 모멘트와 adjoint 결과, 두 출생 및 selected의 부호 있는 잔차, per-state 합과 6개 bin 합을 고정 기준으로 확인한다. 음수·NaN·Inf를 자르거나 source를 다시 만들어 통과시키지 않는다.
- bin은 (0.1,1], (1,10], (10,30], (30,100], (100,300], (300,900] eV다. source birth, T 시각 미래 열 분포, 미래 체류시간, local heat deposition은 구별한다.

## 4. 실패와 수집

실패는 실제 layer로 기록한다. source/G identity, 구현, 수치 잔차, runtime·자원, 독립 evidence는 서로 다르다. 최초 로그와 partial result를 보존한다. 예산을 새 코드로 이전하거나 완료된 model을 자동 재실행하지 않는다.

wrapper 실행 실패·collection 성공은 전체 실패이며, 실행 성공·collection 실패도 전체 실패다. solve reservation, 실제 solver 반환 완료, 성공한 resolvent block을 구분한다. 예약과 완료 사이의 중단에서는 정확한 호출 수를 만들어내지 않고 기록된 하한·상한과 불확실성을 남긴다.

기본 collector가 만든 ZIP은 현재 F unit, 정확한 의존 파일, 입력 복사본과 실제 run을 담는다. `RETURN_MANIFEST.json`은 자기 자신을 제외한 모든 payload bytes/SHA를 열거한다. ZIP 이후 만들어진 `WRAPPER_COLLECTION_EXIT.json`과 `WRAPPER_ACTUAL_EXIT.json`은 ZIP 외부의 필수 sidecar이며 `RETURN_FAMILY_MANIFEST.json`에 결속된다.

운영 로그는 source 밖 `external_logs/`에 보존한다. 최종 전달 family에는 다음을 함께 넣는다.

- numerical return ZIP와 정확한 return/family manifests;
- 필수 wrapper sidecar 두 개 및 실제 execute/launcher/runtime 기록;
- 복구 검증, 환경 준비, plan/preflight stdout·stderr·actual exit;
- wrapper 호출 stdout·stderr·actual process exit;
- 새로운 독립 review와 그 검토 대상 identity;
- Git 반환 commit/tree 및 Drive/Dropbox provider 영수증.

wrapper가 이미 만든 family manifest는 변경하지 않는다. 추가 외부 운영 로그가 있으면 이 기존 family와 그 manifest를 포함하는 새 바깥 family envelope 및 manifest를 create-only로 만든다. 원본 ZIP·최초 실패·기존 manifest를 보존한다. 수집이 실패한 경우 raw run과 외부 로그를 남기고 실패를 성공 ZIP으로 표시하지 않는다.

## 5. 독립 판정과 반환 게시

실제 NCP 반환에 대해 새 독립 Astra reviewer가 frozen source, G parity, q/occupation 자료, finite·positive·residual 조건, saved scalar·bin 합, runtime, actual exit·예산을 검토한다. 이 reviewer는 실제 candidate·acceptance·implementation 기여와 분리되어야 한다. 모델 label과 실제 검증 가능 범위도 기록한다.

PASS_SCOPED는 named 9,600점 frozen-operator 진단에만 적용한다. PHYS02_DELAY OPEN, production_history HOLD, atomic_G02 UNRESOLVED, b_grid NO_GO, all_bound OPEN, R17B2B NO_CERTIFIED_SOURCE_SHARPENING, CCC_2026_exporter_identity SOURCE_IDENTITY_UNRESOLVED를 유지한다. 에너지 격자 수렴, continuum tail, cosmic production, NCP64 scaling은 승격하지 않는다.

실제 source science commit에서 새 additive 반환 branch와 draft PR를 만든다. 기존 branch의 dirty 작업을 보존하고 merge·force-push·기존 원본 덮어쓰기를 하지 않는다. source 코드 수정이 불가피한 결함이면 최초 실패, 변경 diff, 영향을 받은 가벼운 검사와 별도 review를 보존한다. 기존 물리 실행 예산이 자동으로 재발급되는 것은 아니다.

지정된 Drive와 Dropbox에 새로운 고유 파일명으로 완전한 return family와 짧은 한국어 요약·재현 안내를 올린다. 기본 R1은 provider 성공·정확 ID/ref·available size/hash 확인이며 remote 원시 readback과 다르다. mismatch·복구 등 실제 R3 trigger가 있을 때만 범위를 정해 추가 확인한다. SHA256 미제공만으로 원시 다운로드를 반복하지 않는다.

최종 답변에는 실제 실행 여부, 양 모델별 결과, energy-bin의 지연 기여와 T 시각 미래 열 분포, 독립 판정, actual exit·소모 예산, 새 PR/head/tree, 정확한 두 백업 ID·크기·SHA256을 제공한다.

