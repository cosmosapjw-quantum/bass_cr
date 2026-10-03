# R4AJ Codex 계승: 한국어 결과와 정확한 통합 patch

이 단계는 selected-1s selector/공진 reference의 이론 판별을 마쳤다. 현 원자 적분은 수행하지 않았다. source와 새 reference시험은 구현돼 있으므로 다시 처음부터 연구/구현하지 않는다. FINAL_STATE, REPORT_KO, DERIVATION_KO, NEXT_DAG, DBv22와 receipt를 먼저 읽는다. 직전 중국어 응답의 전체 한국어판은 docs/R4AI_PREVIOUS_REPLY_KO.md다.

## 다운로드와 복구

최종 전달 시작 prompt의 실제 Dropbox ID와 SHA-256을 사용해 ZIP을 받는다. 인증된 Dropbox 연결 또는 동기화 폴더에서 파일을 얻는다. 비밀키나 임시 bearer URL을 로그나 답변에 노출하지 않는다. 패키지 내 tools/download_dropbox.py는 사용자가 제공한 환경변수 token으로 공식 download API를 호출한다. 파일ID만으로 무인 인증이 된다고 가정하지 않는다.

패키지를 새 폴더에 푼 뒤 `python verify_release.py .`를 실행한다. parent/R4AI.zip은 hash로 고정된 이전 전체패키지다. 그 안에 actual m64 실행을 위한 원 R4AH/R4AG코드와입력이 있다. 새 R4AJ의 source/run_discriminator.py는 완료된 작은 판별이므로 다시 실행하지 않는다. source/independent_review.py도 이번반환검토를보존한것이며반복실행으로과학근거를늘리지않는다.

## Git 반영

배포root의 publication/COMBINED_R4AI_R4AJ_CREATE_ONLY.patch는 아직미게시인R4AI85파일과이번R4AJ파일을모두한번만추가한다. 원R4AIpatch와이통합patch중하나의경로만선택한다. 동일파일을두번적용하지않는다. 정확한상태는publication/PATCH_MANIFEST.json에서읽는다.

대상branch `research/r4q-gap-closure-20261001`, 기대HEAD `0d7bdbe76dc35d38668d750e6312919cecb09144`다. 먼저 실제 원격과 로컬 HEAD/clean 상태를 확인한다. 다른HEAD나기존target이있으면다른작업을덮어쓰지말고diff를읽어새계약을작성한다. 새branch/mainmerge/force금지다.

```sh
python tools/apply_checked_patch.py \
  --repo /absolute/path/to/bass_cr \
  --patch publication/COMBINED_R4AI_R4AJ_CREATE_ONLY.patch \
  --manifest publication/PATCH_MANIFEST.json
```

이명령은Gitworktree/index를검증·적용할뿐commit/push하지않는다. diff와manifest를검토한뒤동일branch에서commit하고non-forcepush하며원격commit/tree를receipt로반환한다. fullgitobjecthistory를갖춘후에만진짜gitbundle을만들수있다. 옛R4AD안전성차단mutation,R4AA379및다른기존mapping을추가적용하지않는다.

## 로컬 이론과 외부 실행은 병렬

다음local은 LOCAL_RESONANT_PAIR_WEAK_BRIDGE_ENVELOPE다. 측정P1s는유지하고T1s/P1s를같이진화시키는reference에서κ/B/Bdot/gamma와connection을연속bound로구성한다. 저장행렬gap0.373Eh를실제bridge에직접상속하지않는다. 다른retained상태와gapcrossing이생기면최소확대를별도판별한다. 물리bridge와누출오차,raw label과spectralprojector를구분한다.

외부첫node는원래대로R4AH m64다. parent/R4AI.zip을새폴더에추출하고그안의CODEX_HANDOFF_KO.md에따라R4AH runtime을추출한다. 실제NCP환경을observe/build/pin하고정확한BATCHSHA로m64만승인·실행한다. 테스트fixture메모리를실제승인에사용하지않는다. 기존중심점/M9/oldR8/old scientificsuite를반복하지않는다. m64완료후전체evidence와point반경을검토한뒤에만별도remaining9batch를승인한다. m64승인파일을all10으로수정하지않는다. R4AI runtime_tools/merge_returns.py는동일native/원runtimepath조건의읽기전용수집이며다른ABI나재배치archived과학검증을자동지원하지않는다.

## 반환과 claim

새코드mutation/실행이있다면exactsource/native/input/frame/unit/domain/attempt/output/실제resource와실패기록을반환한다. 입증되지않은physicalbridge와미완료stencil총상계는null이다. 논문identity또는정확산술helper만으로physicalsource를승인하지않는다. G02UNRESOLVED/productionHOLD/capturefalse/all_boundOPEN/b_gridNO_GO유지. 이중백업은두provider실제ACK/ID/크기성공시만완료로보고하며UPLOAD_VERIFIED와RESTORE_VERIFIED를구분한다.
