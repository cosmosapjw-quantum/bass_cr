# R4AK 원자 전용 Codex 인계

최신 연구 SSOT는 이 패키지의 FINAL_STATE, RESULT_SUMMARY, DERIVATION_KO, NEXT_DAG, DBv24와 별도 DELIVERY_RECEIPT다. R4AJ 원자 전용 범위는 유지한다. Bianchi/재이온화 동역학은 rei_bianchi가 담당한다. source code를 처음부터 재구현하지 않는다.

## 1. 바이트 복원 및 게시

연결된 Dropbox 도구로 BASS_CR_R4AK_WEAK_PAIR_PACKAGE_20261003_v1.zip을 회수하고 별도 전달 receipt의 bytes/SHA256과 비교한다. 다운로드 URL/credential은 로그에 남기지 않는다. 완전한 부모 R4AJ v2가 필요하면 Dropbox id:BSpOijBcT10AAAAAADxq4w 또는 Drive1HmxYnGukae54l7GXQ9SpZTZq0B5W8a8s를 사용한다. 부모39928468bytes, SHA2563c6969694ff7ae8417ff7eeb664b0f52fe05cf9052cd2fb5c8ba93abd987658b. 그 안의 R4AH/R4AG 실행 자료는 이미 구현된 코드이며 완료계산을다시하지않는다.

현재 동일 연구 branch의 게시 기준:
repo cosmosapjw-quantum/bass_cr
branch research/r4q-gap-closure-20261001
HEAD333d6940adc2eaa3a44d6b22f7418fc7416b94ca
treeb623d20fb442eda92ae6cb312b9e8aa49ee15b26.

원R4AJ source2개와R4AK source3/test2/README1은이미게시됐다. publication/PENDING_CREATE_ONLY.patch는이8개파일을제외하고기존미게시144파일과이패키지의미게시산출물만추가한다. 원R4AI85patch,R4AI+R4AJ146patch를중복적용하지않는다.

먼저 git fetch와현재ref/diff를읽는다. HEAD가달라졌으면자동적용하지말고변경을분석한뒤새expected-parent 계약을만든다. 새branch/mainmerge/force/기존source덮어쓰기/옛R4AD차단mutation우회는금지한다. 이패키지의원자DAG가옛폴더에있는consumer/backreaction계획보다우선한다.

검증 및 적용:
python verify_package.py .
python tools/apply_pending.py --repository /absolute/bass_cr --manifest publication/PENDING_MANIFEST.json
python tools/apply_pending.py --repository /absolute/bass_cr --manifest publication/PENDING_MANIFEST.json --apply

두번째명령은drycheck,세번째는명시적create-onlyindex적용이다. helper는commit/push를하지않는다. 전체바이트/index와git diff를검토하고같은branch에명시적으로commit/non-force push한다. 원격HEAD/tree를확인해receipt를반환한다. 임시검증저장소에실제remote ancestry를가짜로생성하지않았다.

## 2. 다음 실제 원자 실행

외부첫노드는아직R4AH_m64다. 부모R4AJ v2의R4AI/R4AH실행패키지에있는m64launcher를사용해실제NCP환경/source/native/output을observe/build/pin한다. 승인파일없는상태에서자동실행하지않고,정확한BATCH SHA및m64한점범위의승인후에만실행한다. all10승인으로원허용범위를늘리지않는다. 새환경에영향받는범위만검토하며old과학suite를반복하지않는다. 첫m64를수락한뒤별도remaining9batch를만들고원m64를재사용한다.

## 3. 로컬 이론 후속과 필요한 입력

다음local은R4AL_FULL_FRAME_CONTINUOUS_S_K_TUBE_ENCLOSURE다. 동일candidate/등록bridge구간에서full18 S,K=H−iħD,Sdot의연속절대enclosure,fullGram하한,초기state와selector/embedding비교를고정한다. 단일점/fit/RMS/차수간차이를uniformremainder로넣지않는다. 여기에구현된pairprovider는이러한실제tube를받으면조건부상계를계산할수있지만현재실제입력은없다. 원0.373Eh저장gap과0.954pairGram하한은각각actualbridgegap/full18Gram하한이아니다.

source/tube_cli.py는정확히정의된polynomialreference및별도assumeduniformremainder만지원한다. contracts/SYNTHETIC_INPUT_EXAMPLE.json은fixture일뿐이다. actualdata가없으면initialstate/physicalbridge항은null로유지한다. run_r4ak.py의소비된run_v1은재실행하지않는다.

## 4. 반환

새게시commit/tree/diff,실제environment/native/contract,모든one-shotreservation/completed또는failure,각enclosure의bound_type/domain/units/sourceidentity와낮은차수보간잔차를포함한다. 원자nativepilot반환은요약만이아니라원evidence를보존한다. 완료cell을다시계산하지않는다. 새source의불일치/메모리차단/수치정확도미달/과학전제미확립을분리한다.

G02UNRESOLVED/productionHOLD/capturefalse/all_boundOPEN/b_gridNO_GO;physical_bridge_upper=null;full_stencil_total_upper=[null,null]. 전체원자데이터완료나production승인은별도다.
