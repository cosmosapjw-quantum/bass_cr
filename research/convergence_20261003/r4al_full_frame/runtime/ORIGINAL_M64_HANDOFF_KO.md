# R4AH: m64 한 점만 실제 실행하는 NCP 인계

현재 결과는 R4AH_RUNTIME_PREPARATION_BLOCKED다. 이 채팅의 실제 R4AG prepare는 minimum 1-worker 자원 guard에서 종료됐고 native build/authorization/원자적분은0이다. 제한을 완화하거나 메모리값을 fixture로 바꿔 과학 계산을 실행하지 않았다. 추가한 source/m64_launch.py는 원 R4AG 코드를 바꾸지 않는 m64 전용 외부 launcher다.

## 고정 범위

같은 candidate 17c0215979675e40db364207ce138c5efb58cb24c22824e418f5abe3cfeb49ef, b=2a0, E=100keV/u, stored actual epoch, m64 z=-2049/64 a0 한 점만 실행한다. point target=1e-16, final stencil criterion=1e-12 ta^-1이며 변경하지 않는다. 기존 중심점/M9/Peano/R8 및 완료suite를 재실행하지 않는다. 나머지9개 shifted point와 원래다른7offcentral centers는 서로 다른범위이고 지금은둘다열지않는다.

## 실행

이 ZIP을 새 디렉터리에 푼다. `r4ag/`는 필수 source/input/vendor와부모증거를포함한바이트동일release다. Python≥3.11,numpy/scipy/mpmath,C++17,GMP/GMPXX개발환경과Linux cgroup-v2가필요하다. 의존성을갱신하면새native/환경identity로계약을만든다. 실제NCP환경은아직관측하지않았고아래값을관측값으로날조하지않는다.

```bash
cd /absolute/path/to/BASS_CR_R4AH_RUNTIME_HANDOFF_20261003_v1
python verify_delivery.py .
python source/m64_launch.py prepare \
  --session /absolute/new/r4ah_m64_session \
  --workers 3
```

prepare는source49pin검증,실제resource관측,build/pin만한다. R4AG가요구하는가용RAM은workers×512MiB+1792MiB,CPU는workers+1이다. worker수는1,2,3중실제조건에맞게실행전에선택한다. 부족하면그대로차단하고새session의PREPARATION_FAILED.json/prepare.stderr를반환한다. limit을낮추거나globalcache를강제purge하지않는다. /sys/fs/cgroup의요구파일이없으면관측실패를반환하고임의host total로대체하지않는다.

출력 BATCH의 SHA와ENVIRONMENT,build/COMPILER.txt,LDD.txt,native 및공유librarypin을검토한다. 이검토와m64한점실행승인을거쳐아래명령을실행한다. `--nodes all10`을사용하지않는다.

```bash
S=/absolute/new/r4ah_m64_session
H=$(sha256sum "$S/batch/BATCH.json" | cut -d ' ' -f1)
printf '%s\n' "$H"
# 정확한 BATCH와 m64 한 점의 native 실행을 승인한 뒤:
python source/m64_launch.py execute \
  --session "$S" --confirm-batch-sha256 "$H" --authorize-native
```

launcher는원parent CLI의authorize(m64만),run(max-new-nodes1),collect를동기적으로호출한다. 한번실행요청하면EXECUTE_REQUEST.json으로소비를기록하며실패/중단을자동재시도하지않는다. 기존승인/기존point폴더가있으면거절한다. source/계약/geometry/epoch/pole/cover/native/cell/반경검사는원parentengine/collector가수행한다. source를수정해기존identity라부르지않는다.

## 반환

성공또는실패후아래명령은바이트포장만한다. 원자적분/collect/기존suite를재실행하지않는다. ZIP은session바깥의새파일이어야하며symlink와덮어쓰기를거절한다.

```bash
python source/m64_launch.py bundle \
  --session /absolute/new/r4ah_m64_session \
  --output /absolute/new/R4AH_M64_RETURN.zip
```

반환ZIP에는REQUEST/PRECEDING_RESOURCE_SNAPSHOT,준비/실행stdout/stderr,실제BATCH/AUTHORIZATION/ENVIRONMENT/build/nodecontract,RESERVATION/CELL_CERTIFICATES/GAUSS_RULES/NATIVE_INPUT/NATIVE_DISPATCH/worker출력/반경/S_ONLY_SEAL/RESULT/RETURN_MANIFEST/COMPLETED 또는FAILURE,수집된PILOT_RETURN과PILOT_ACCEPTANCE가있어야한다. 없는파일을성공상태로채우지않는다. partial고유파일을삭제하지않는다. RETURN_PAYLOAD_SHA256.json은바이트manifest이며과학검증을대신하지않는다.

firstpilot수락조건: m64만available,1e-16pointtarget,진짜source/native/geometry/epoch/cover/pole와완료cell확인,synthetic fixture거절,새D/V/M9/center0,두windowtotal_upper는아직null,globalceiling유지. 성공후결과를이연구스레드에돌려보내고나머지9점의별도승인계약을정한다. m64승인에나머지9점을추가하지않는다.

## 다음 단계와 금지사항

다음scientific node는계속R4AH_SHIFTED_S_RUNTIME_PILOT이다. 이번자원차단으로그노드를CLOSED하거나R4AI로이동하지않는다. 결과반환전에는이환경에서동일prepare/기존검증을반복하지않는다. 별도C0actualreceiverbinding은pending이며Bianchi재이온화의count를자유전자/가열률로바꾸지않는다.

GitHEAD를새로읽어samebranch/create-only/non-force로추가한다. R4AA379/R4AD/R4AE/R4AF/R4AG의과거미게시mapping은각각별도다. 이번패키지는R4AG원27-file mapping을보존하나원격적용성공을가정하지않는다. Drive/Dropbox의실제ACK/ID/크기를확인할때만UPLOAD_VERIFIED라한다.
