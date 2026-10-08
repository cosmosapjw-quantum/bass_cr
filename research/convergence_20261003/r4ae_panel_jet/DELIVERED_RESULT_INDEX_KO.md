# R4AE: window M9/Peano 상계 확보, S 표본 정확도는 미달

2026-10-03. 이 게시물은 새로운 R4AE 결과의 전달 인덱스다. 과거 safety-status가 차단한 R4AD patch를 게시하거나 다른 endpoint로 우회하는 작업이 아니다.

## 실제 결과

`VALID_ENCLOSURES_PILOT_ACCURACY_TARGET_NOT_MET`

같은 finite s+p candidate, b=2a0,100keV/u,z0=-32a0의 전체 shell-pair cover를 포함하는 interval-range provider를 구현하고, 한 geometry와 하나의 whole-window order9 jet batch를 실행했다. 전체1229triangle을 포함하며 point4916box, jet1229box다. firstpanel u/r의 정확 다항식 소거로 원점의 제거가능한 분모를 처리하고, entire-Q ring식에서 sqrt(Q)와 Bessel을 따로 미분하지 않았다. affine-R vertex와 signed Duffy Jacobian을 jet에 포함했다. 산술은 자체 Python 정수256fractional-bit outward interval이며 FLINT를 사용하지 않았다.

실제 M9 upper의 표시값은3.883051552022553e6 a0^-9다. 정확 rational upper는 패키지 WINDOW_JET.json에 있다. 이를 위쪽으로 간단히 반올림하면 M9<=3.884e6, R8 H=1/64와1/128의 절단오차는 각각1.864e-17,7.280e-20 ta^-1 이하다. window는[-2049/64,-2047/64]a0와 ideal t=z/v다. 같은 원래weights와Peano계수를 사용했으며 사전truncation배분1e-13을 통과했다.

첫 point의 full-cross Frobenius 반경 상계는22.17669173413154로 목표1e-16을 못맞췄다. 기존 저장 S에 대한 절대오차 상계도22.17931477651686으로 지나치게 넓다. 이는 실제오차가22라는 뜻이 아니다. range dependency와 cancellation 손실 때문에 좋은 정확도 인증을 얻지 못한 것이다. 넓은 interval 안에 옛 S가 있다는 사실을 고정밀검증으로 주장하지 않는다.

새시험29건, 독립Fraction norm/Peano/identity 검토1994조건, 기존 scalar error combiner에 새truncation packet2개 연결검사를 통과했다. 별도인간/에이전트검토나 proof-assistant검증은 아니다. 원래R8행렬/완료R4Z~R4AD계산·시험 재실행0, D/Vother0이다. 실제과학적attempt1회, 자동재시도0, wall576.071490319s,maxRSS99704KiB였다.

## 남은 상태

R4AD에서 없던 numeric M9/Peano term은 확보됐다. 그러나 두stencil의8sample slot과 oldstencil arithmetic은null이며 total_upper=null이다. 이번center geometry는shifted R8 sample이 아니므로 반경을여덟node에복사하지않았다.

G02=UNRESOLVED; production=HOLD; capture=false; all_bound=OPEN; b_grid=NO_GO. A1은옛범위CLOSED,A2PARTIAL,C0actualbindingpending이다. finite-candidate 내적의상계이며 physical basis/capture/rate 또는전체trajectory 인증이아니다.

## 다음 한 단계

`R4AF_CROSS_S_HIGH_ORDER_VALIDATED_CUBATURE_PILOT`.

같은completegeometry와origin/entire-Q표현에서 고차polynomial/cubature와실제나머지상계로S의폭을줄인다. 먼저analyticfixtures를검사하고새source/input/precision/environment/attempt/output계약을만든다. 초기actualcrosscap0,V/D/windowjetcap0이다. 동일한수학적target의동등성이확인되면이번M9를재사용하고windowjet을반복하지않는다. precision만높이거나전체uniform분할을무작정확대하지않는다. 첫point목표전에모든shifted sample/capture/basis/b/energy를열지않는다.

## 정확한 재현자료와 실제 백업

파일: BASS_CR_R4AE_PANEL_JET_PACKAGE_20261003_v1.zip
bytes:4815872
SHA256:c9b72cc239e8b93588b80de65ee751a2f9d236dbff74fbc0f62fa4ea501d917d
Drive ID:12ujkThVzpZzWU9BPX5dB5W6omDYb50-V
Drive parent:1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
Dropbox ID:id:BSpOijBcT10AAAAAADxnzA
Dropbox directory:/bianchi/BASS_CR_R3M10_LOCAL_REPRODUCTION_PACKAGE_20260921_v1/provenance/NCP_F1_DUAL_BACKUPS/

두provider의실제완료응답과4815872bytes를확인했다. R1_UPLOAD_VERIFIED이며원격checksum미반환/RESTORE_VERIFIED=false다. 로컬107members CRC와106payload SHA를검증했다. 모든R4AE입력4개, 소스6개,시험4개,전체결과·체크포인트·계약·DBv17·유도·검토·handoff가있다. 이미양쪽백업된약99MB부모R4AD는중첩하지않고exacthash/objectID로참조한다.

DBv17 SHA256:82b52e21890c088759e4d0750df4ece46cbfc4b93f568b39036eef9e902a3695. v16전체행과G02외12행을보존했으며13current rows/integrity_check=ok다.

## Git 게시 coverage

이Git변경은 전달인덱스와STATE_POINTER 두파일이다. source/tests/contracts/docs19파일의개별작업트리반영은아직수행하지않았다. 해당complete create-only patch와mapping은위두cloud의ZIP에있고, 격리디렉터리에서apply후모든바이트를검증했다. 두indexpath는fullmapping과겹치지않는다. 새로운HEAD를후속source반영의expectedparent로조회해야한다.

과거R4AD의안전성상태차단과R4AA379원파일전체동기화미완료는별도로보존한다. 이인덱스게시나cloud백업으로source-tree전체동기화를주장하지않는다. Bianchi재이온화scope, count/electron/heat구분과기존물리gate는변경하지않는다.
