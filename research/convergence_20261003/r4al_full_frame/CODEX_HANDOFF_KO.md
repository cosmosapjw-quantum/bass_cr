# R4AL 이후 Codex 인계: 실제 실행과 원자 데이터만

이 전달본은 R4AL의 완료 결과와 실행되지 않은 R4AH m64를 분리한다. R4AL은 두 기존 z=-32a0 window의 full18 Gram 양성과 거친 weak norm을 닫았으나 precise K와 physical bridge는 미완료다. 같은 R4AL 계산/시험·R4AF 중심점·M9·old R8을 반복하지 않는다. rei_bianchi의 우주론 동역학은 여기서 구현하지 않는다.

## 1. 파일 검증과 게시

ZIP을 새 디렉터리에 추출하고 `python verify_package.py .`로 SHA/크기만 확인한다. 이 명령은 과학 계산을 하지 않는다. README, REPORT_KO, DERIVATION_KO, NEXT_DAG, FINAL_STATE 및 detached DELIVERY_RECEIPT를 읽는다. 실제 완료 소스 2개/시험 파일 3개/README는 다음 commit에 게시됐다.

```
repo: cosmosapjw-quantum/bass_cr
branch: research/r4q-gap-closure-20261001
expected HEAD: ce1a050b581791462e9b2f0954a88ea49278c3f0
expected TREE: 8b31de053caf837e9cda553219c743d5fc854d40
```

publication/PENDING.patch는 과거 R4AK pending192개와 이번 아직 게시되지 않은 파일만 합친 새 create-only patch다. 게시된 현재6개/과거8개는 제외됐다. 원 R4AJ146/R4AK192 patch를 중복 적용하지 않는다. 최신 repo를 읽은 뒤 HEAD/branch가 정확하고 worktree/index가 clean일 때에만:

```bash
python tools/apply_pending.py --repository /absolute/path/to/bass_cr \
  --manifest publication/PENDING_MANIFEST.json
# 적용하려면 같은 명령에 --apply를 추가한다.
```

helper는 fetch/commit/push/과학실행을 하지 않는다. 적용된 경로와 hash를 검토한 뒤 사용자 승인 범위의 같은 branch에 commit하고 non-force push한다. HEAD가 전진했거나 대상 파일이 있으면 자동rebase/overwrite하지 말고 실제 diff를 보고 새 적용 계약을 만든다. 전체git객체이력이 없는 상태에서 synthetic parent로bundle을 만들지 않는다. 과거R4AA379와금지된mutation은이patch로소급완료하지않는다.

## 2. NCP의 첫 실제 원자 실행

`runtime/R4AH_M64_RUNTIME.zip`은 원본 바이트 동일한 m64 전용 launcher와 R4AG 필수 코드·입력을 포함한다. 재구현하지 않는다. 먼저 파일 SHA가 runtime/RUNTIME_REFERENCE.json과 일치하는지 확인하고 새 작업 디렉터리에 푼다. 원래 runtime handoff를 읽되 우주론/host 작업에 관한 역사적 항목은 최신 원자 전용 범위가 우선한다.

필요 환경: Linux cgroup-v2, Python>=3.11, numpy/scipy/mpmath, C++17, GMP/GMPXX 개발 헤더. 실제 CPU와 메모리, compiler 및 library identity를 관측한다. 사용자가 가진64CPU/128GB를관측값으로기입하지않는다. 먼저prepare만실행한다.

```bash
cd /absolute/new/extracted_R4AH
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python verify_delivery.py .
python source/m64_launch.py prepare \
  --session /absolute/new/r4ah_m64_session --workers 3
```

workers는1~3이며 실제가용CPU>=workers+1, headroom>=workers*512MiB+1792MiB가필요하다. 부족하면그대로실패receipt를반환한다. guard완화/fixture메모리/다른프로세스종료/강제cache회수는하지않는다. 완료된이채팅의실패prepare를반복하는것이아니라새NCP환경의새identity를관측하는것이다.

BATCH/environment/build/native/library/outputbinding을검토하고정확한SHA와m64범위를승인한뒤에만:

```bash
S=/absolute/new/r4ah_m64_session
H=$(sha256sum "$S/batch/BATCH.json" | cut -d ' ' -f1)
python source/m64_launch.py execute \
  --session "$S" --confirm-batch-sha256 "$H" --authorize-native
python source/m64_launch.py bundle \
  --session "$S" --output /absolute/new/R4AH_M64_RETURN.zip
```

실행은 z=-2049/64a0의m64한점뿐이다. point반경1e-16과source/native/geometry/epoch/cover/pole/완료cell을확인한다. D에맞추는보정은금지한다. 성공/실패/부분기록모두반환하며실패를자동재시도하지않는다. m64수락전나머지9점은실행하지않는다. 이후9점은별도승인된batch로실행하고m64를재사용하는수집기가필요하며,기존m64승인파일을all10으로수정하지않는다.

## 3. 반환과 판단

원 BATCH/AUTHORIZATION/ENVIRONMENT/build/nodecontract/RESERVATION/cellcertificates/Gaussrules/nativeinputs/workeroutputs/intervals/S_ONLY_SEAL/RESULT/RETURN_MANIFEST/COMPLETED 또는FAILURE를반환한다. summary만으로완료하지않는다. 실제wall/RSS/중단여부를기록하고자료가빠진window의total_upper는null을유지한다.

m64반환은S표본pilot이지fullbridge/단면적/production승인이아니다. G02UNRESOLVED,productionHOLD,capturefalse,all_boundOPEN,b_gridNO_GO 유지. 기존R4ALfull18하한은동일candidate/phase/frame/두window에한해재사용하고다른basis,b,E에확장하지않는다.

## 4. 이 대화에서 계속 가능한 일

로컬다음노드=R4AM_WEAK_K_CONTACT_CELL_PROVIDER_AND_REMAINDER. weak gradient/Coulomb/ETF integrand와원점/인터페이스처리를회수하여고차검증적분과나머지를설계·구현하고exactfixture로시험한다. 실제K평가는새one-shot계약이필요하며최초cap0이다. 그다음원자exportschema의채널/단위/에너지/질량/보간/오차/provenance검사를완성할수있다. 연구전체가NCP대기만남았다고보고하지않는다.
