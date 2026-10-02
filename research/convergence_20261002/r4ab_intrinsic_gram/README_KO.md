# A1 / R4AB intrinsic Gram: 실행 완료

2026-10-02. 판정은 R4AB_INTRINSIC_AND_LOCAL_R8_EMPIRICAL_PASS다. 유한 저장 candidate의 intrinsic Gram/H0/A 및 saved-data S/H/D 재조립 범위에서 A1을 닫았다. 전역 operator/physical capture 승인은 아니다.

## 실제 산출

DAG.next_scientific_node=A1에 따라 exact Fraction Gram/J/T oracle,90/120자리 유리수·로그 inverse radial moments, strict FP64 Fortran 고정패널 커널, s+p 직접 각도 적분, immutable intrinsic cache와 일관된 ETF boost를 구현했다. source/8개와 tests/4개의 정확blob identity를 로컬 산출물과 확인했다. 실제 변경영역시험은17건 통과다.

기존 R4AA11위치의34완료payload에서 cross6와V_other를 bitwise그대로 재사용했다. 새 cross0회, V_other0회, 옛R4Z/R4AA계산·시험재실행0회다. S-only미분seal 후D를 비교했다. 새G를H와D의v²S항양쪽에반영했고 G를I로바꾸거나A를반에르미트화하지않았다.

FP64 Gram의 exact-rational 최대차는1.9942755287834335e-16이다. H0/A 고정밀비교 최대차는각각1.1102230246251565e-16Eh,1.3877787807814457e-17a0^-1이다. A+A†의1.9107173916696979e-16a0^-1결함은그대로남겼다. Gram비대각최대1.142160880438192e-15와대각1로부터의최대차1.199040866595169e-14를보존했다.

R4AA와동일한h=[1/64,1/128,1/256,1/512,1/1024]a0와R8두window를썼다. same-center S-only미분은bitwise0이다. D+D†대비최대spectral/Frobenius/max-entry잔차는2.0632051824529002e-13 /3.042975213008623e-13 /1.457001391596516e-13ta^-1이다. 두window Frobenius차이는q40/beta24:1.9796960448152007e-13, q48/beta24:1.6951765591564122e-13, q48/beta12:1.610017311211324e-13으로모두기존1e-12기준을통과했다.

독립검토681조건통과. endpoint/bubble beta적분으로G/J/T75항목을exact대조했고80자리R8독립재구성의최대차는1.197127703427732e-18이다. 같은세션의다른알고리즘이며별도인간/agent검토가아니다. H0/A고정밀일치는intervalcertificate가아니다.

최초v1preflight는parent stage-result해시를derivative-result파일과잘못연결한reader구현오류로과학계산전에차단됐다. 실패source/contract/context/log를보존하고새v2identity와회귀시험으로복구했다. 허용오차변경/자동재시도/물리호출없음. 성공stage1회와preflight실패1회를구별한다.

## 전체 재현 패키지와 실제 백업

파일: BASS_CR_R4AB_INTRINSIC_GRAM_PACKAGE_20261002_v1.zip
Bytes:43582954
SHA256:fbfaaee8181cf1b586f36207bb76c73c07b7826a421d5b0123a921ac488a2afb
153members의CRC와152payload SHA256확인. 완전한source/tests/유도/계약/실패와성공결과/independentreview/DBv14/이전R4AA및design원본ZIP포함.

Drive ID:1mh9RBGbpk6CDbtx-al98I6DN3pxFDiGV, parent:1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI. 실제ACK+metadata size43582954확인.
Dropbox ID:id:BSpOijBcT10AAAAAADxlKA. 실제completed ACK+size43582954확인.
Dropbox경로:/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/provenance/NCP_F1_DUAL_BACKUPS/BASS_CR_R4AB_INTRINSIC_GRAM_PACKAGE_20261002_v1.zip
둘다R1 UPLOAD_VERIFIED다. 원격checksum은반환되지않았고remote byte restore는하지않았으므로RESTORE_VERIFIED=false다.

Git게시범위는이번A1의source8개,tests4개와4개상태/설명파일이다. binary/native/상세원시결과/DB/완전계약과유도는위fullpackage에보존했다. 이전R4AA379파일원mapping전체를작업트리에적용한것이아니다. 과거fullsource-sync미완료를새A1게시로덮어쓰지않는다.

## 읽기 및 외부-runtime 계약

fullZIP을새폴더에푼뒤 `python tools/bundle_io.py verify .`와 `python tools/bundle_io.py restore-parent .`로byte검증/입력복원을할수있다. 과학계산은실행하지않는다. 과거run_v2는이미완료되어overwrite하지않는다. 다른환경에서는새native/source/environment/context를명시적으로pin하고영향받는시험만수행한다. 완료된R4Z/R4AA와R4AB를이유없이재실행하지않는다. 자세한command/return계약은ZIP의README_KO.md와EXTERNAL_RETURN_CONTRACT.json에있다.

## 유지된 상태와 다음 단계

G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO.
원R4AA실패, 원R2실패, C9/연속궤도/8점gate/physicalcandidate/capture/basis/rate미승인을보존했다. DBv14는기존13gap중G02근거만갱신했고다른12행은그대로다. SQLiteintegrity=ok. DBv14SHA256:7fb08305c644093462af3cc5fdc102252447c46a954f87fa0979314926d97cb8.

다음scientificnode는A2, 첫boundedsubstep은R4AC_SAMECENTER_VOTHER_INDEPENDENT_ERROR_CONTROL이다. 기존order20 V_other는이번에독립refinement하지않았다. 같은candidate/domain에서독립panel표현또는오차통제부터진행하며rawcrosscap0, 나머지7점/capture/enlargement자동확장금지다. C0actualreceiverbinding도별도pending이다. 포획count를자유전자/가열/전체HII생성률로해석하지않는다.
