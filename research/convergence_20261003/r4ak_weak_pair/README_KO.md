# R4AK: 원자 공진쌍 weak bridge 데이터 준비

먼저 REPORT_KO.md, DERIVATION_KO.md, FINAL_STATE.json, NEXT_DAG.json을 읽는다.

완료된 유한 candidate 계산과 synthetic 검산은 evidence에 있다. 이를 반복하지 않는다. 새 exact polynomial 입력은 source/tube_cli.py로 평가할 수 있다. 예시는 contracts/SYNTHETIC_INPUT_EXAMPLE.json이다. 이 입력은 실제 원자데이터가 아니다.

python source/tube_cli.py --input contracts/SYNTHETIC_INPUT_EXAMPLE.json --output /새경로/model_tube.json

필요패키지: Python3.11이상. weak_pair와tube_cli는표준라이브러리만,실제candidate입력에는numpy,새synthetic검산에는scipy,독립symbolic검토에는sympy/mpmath,변경영역시험에는pytest가필요하다.버전은evidence/POSTRUN_DEPENDENCIES.json.큰NCP실행코드는부모R4AJ v2의R4AH/R4AG자료를사용하며이패키지에서m64를자동실행하지않는다.

과학범위: 동일finitecandidate의pairGram/weak-formbound, exact-polynomial또는조건부remainderprovider. actualfull18bridge와source생산은미완료다. G02UNRESOLVED/productionHOLD/capturefalse/all_boundOPEN/b_gridNO_GO. Bianchi물리는rei_bianchi소유다.

게시/백업identity의정본은detachedDELIVERY_RECEIPT. publication의patch는현재기준부모와이미게시된2개R4AJsource를고려한다.원146patch와중복적용하지않는다.모든과거scope문서는역사로보존하며최신원자DAG가실행범위를정한다.

Git 게시본은 현재 핵심 source 3개와 테스트 2개, 이 README다. 전체 실행기·독립검토·입력·결과·DB·상세 문서는 재현 ZIP에 있다. 개별 Git 파일만으로 전체 replay를 승인하지 않는다.
