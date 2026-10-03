# R4AM 후 NCP/local Codex 인계

이곳은 원자 데이터 생산자다. Bianchi 물리는 rei_bianchi 소유다. REPORT_KO, DERIVATION_KO, RESULT_SUMMARY, NEXT_DAG, SOURCE_INPUT_LOCK과 detached DELIVERY_RECEIPT를 읽고 실제 게시기준을 확인한다. 완료된 R4AM153시험과기하/fixture, 과거center/M9/R8를 수신만으로 반복하지 않는다.

## 1. 백업과 저장소 반영

`python verify_package.py .`는 파일무결성만 확인하고 과학을 실행하지 않는다. publication/PENDING_MANIFEST.json의정확parent/tree/branch와현재원격을비교한다. 새pendingpatch는이미게시된파일을제외한과거pending과이번자료만추가한다. 이전R4AL250/다른patch를중복적용하지않는다. manifest와각대상hash를확인해cleanworktree/index일때만 `python publication/apply_pending.py --repository /path/to/bass_cr --manifest publication/PENDING_MANIFEST.json`으로검사하고,적용하려면`--apply`를추가한다. helper는commit/push/science를하지않는다. 적용된경로만commit하여같은branch에non-forcepush한다. HEAD전진/기존대상파일/다른작업의dirty상태이면멈추고diff를검토한새계약을만든다. 가짜Gitparent를만들지않는다.

## 2. 지금 필요한 실제 외부 작업: m64 하나

runtime/R4AH_M64_RUNTIME.zip은이전바이트그대로이며RUNTIME_REFERENCE의SHA와크기가정본이다. 새디렉터리에풀고원래handoff를읽는다. 재구현하지않는다. Linuxcgroup-v2,Python>=3.11,numpy/scipy/mpmath,C++17,GMP/GMPXX를실제관측한다.64CPU/128GB는사용자설명이지관측을대체하지않는다.

```
python verify_delivery.py .
export PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
python source/m64_launch.py prepare --session /absolute/new/r4ah_m64_session --workers 3
```

원resourceguard를완화하지않는다. prepare반환의환경/native/library/입력/BATCHSHA와출력경로를검토하고정확한m64범위를승인한뒤에만:

```
S=/absolute/new/r4ah_m64_session
H=$(sha256sum "$S/batch/BATCH.json" | cut -d ' ' -f1)
python source/m64_launch.py execute --session "$S" --confirm-batch-sha256 "$H" --authorize-native
python source/m64_launch.py bundle --session "$S" --output /absolute/new/R4AH_M64_RETURN.zip
```

실제z=-2049/64a0. point accuracy1e-16,source/native/geometry/epoch/cover/pole/cell완결성을반환한다. 실패·중단도원attempt를보존하고자동재시도하지않는다. 수락전remaining9를열지않으며후속9점은별도승인계약이다.

## 3. 새 R4AM reference code의 사용 경계

source/moments.py와weak_kernel.py는origin-safe기하/gradient/각도모멘트, cubature.py는explicitGaussianremainder다. source/run_reference.py는고정된actualcenter의singleentry전체cover를시도하는purePythonreference이며native성능을검증한것이아니다. 이실행은m64와별개이고현재미승인이다. 높은비용때문에다음localnativecellparity전에일괄실행하지않는다. actualcontext를준비할필요가있을때만:

```
python source/run_reference.py prepare --contract /absolute/new/K_REFERENCE_CONTRACT.json --output /absolute/new/K_REFERENCE_OUT
```

이명령은환경관측과계약만기록하며원자적분을하지않는다. 실행하려면같은파일의정확SHA를명시적으로승인해run에넘겨야한다. 원여유RAM2,415,919,104bytes/CPU2이상조건,degree32/rho2/wall1800/evaluation3,000,000/oneattempt가고정돼있다. 큰데이터에서완주나1e-16목표를충족한다는증거는아직없다. budget실패는0결과로처리하지말고partial기록을반환한다. 신규nativebackend로바꾸면옛source계약을수정하지말고새계약을만든다.

## 4. 반환과 다음 연구

source/contract/environment/RESERVATION,cover,모든cell의rootbracket·analyticmajorant·나머지·값,완료또는실패,실제wall/평가수/가능한RSS와manifest를함께반환한다. summary만으로승인하지않는다. referenceinput·수치enclosure·모델오차·state/window/basis/b/E의권위는별개다.

다음local=R4AN_WEAK_K_NATIVE_SINGLE_CELL_PARITY. 이미완성된수식을처음부터새로연구하도록맡기지않는다. 여기에서완료할수있는nativecell이식/증거와시간방향remainder연구가남아있다. NCP는실제자원설정·집중검토·승인실행·실행환경최적화와반환을맡는다. 원자표가완성됐다고하거나rei_bianchi를변경하지않는다.
