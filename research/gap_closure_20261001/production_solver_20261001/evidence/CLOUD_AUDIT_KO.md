# 관련 클라우드 데이터베이스 통합 감사 — 2026-10-01

**실제 bytes가 서로 다른 SQLite 11종을 대조했다.** CR v1–v6와 NUMERICS 중간본, HE v1–v3, WU088 acquisition v3다. 모두 저장된 읽기 전용 SQLite 검사에서 `integrity_check=ok`다. 파일명 대신 SHA256으로 판본과 중복을 구분했다. 전체 인덱스는 [CLOUD_CONTENT_INDEX.json](CLOUD_CONTENT_INDEX.json), 버전 표는 [DATABASE_VERSIONS.csv](DATABASE_VERSIONS.csv)에 있다. 인덱스의 경로는 `cloud_audit_20261001` 기준 상대경로이며 서명된 다운로드 URL을 포함하지 않는다.

| DB 판본 | 테이블 수 | SHA256 앞 12자리 | 확인한 차이 |
|---|---:|---|---|
| CR v1 | 14 | cfbf46fc28bb | sources 31, files 206 |
| CR v2 | 28 | 453a29bb1d15 | works 31, versions 54 |
| CR v3 | 30 | a8eea6a9136b1 | versions 68, files 1,185, 추가 업로드 4 |
| CR v4 NUMERICS 중간본 | 34 | 081e07fc18b2 | research_claims 8, research_events 5 |
| CR v4 최종본 | 34 | 8fedee41a316 | research_claims 17, research_events 16 |
| CR v5 | 34 | 6e40ceeae34c | research_claims 29, research_events 19 |
| CR v6 | 34 | 7635e9e17c80 | research_claims 36, research_events 26 |
| HE v1 | 7 | 1d9dd7d549f7 | 논문 대상 24, 코드 7, dataset 4, 검색 기록 197 |
| HE v2 | 3 | 59b4151aba2e | selected sources 39, 논문 확보 5 / 접근 차단 19 |
| HE v3 | 3 | 4a840a5c6fec | 논문 24 + dataset 6 + code 9 확보 |
| WU088 acquisition v3 | 35 | 6be04d2337d8 | 고유 출처 68, 판본 79, 파일 참조 66 |

CR v3의 기존 **30개 테이블은 NUMERICS 중간본과 최종 v4·v5·v6 각각에서 schema와 전체 행 multiset이 동일**하다. FTS 내부 테이블도 포함한다. 과거 수집 자료의 보존을 확인한 결과이며 연구 주장 자체의 증명은 아니다. 현재 원문 확보 상태는 `works/versions/files`에서 읽어야 한다. 31개 선정 문헌의 확보 상태가 모두 채워졌으므로 오래된 `sources/report_gaps` 미확보 표기를 현재 DOI 미확보 목록으로 재사용하면 안 된다. 증거: [E-CR-COMPARE](../dropbox/DATABASE_VERSION_COMPARISON.json).

NUMERICS는 별도 판본이다. 과거 v1 ZIP의 절단 오류는 그대로 남기고, 대체 v2 ZIP의 실제 1,694,351 bytes와 SHA `5e27c40a2d260276baf2d870e05fa34e0ebc1b293c950daaa8ecb698368c6bf9`를 확인했다. 그 안의 `v4_NUMERICS.sqlite`는 최종 v4와 bytes가 다르다. WU088의 원래 deep-research DB/v1은 회복되지 않았다. 현재 acquisition v3와 부분 report/schema 재구성본을 원 DB의 복구본으로 세지 않았다.

HE v2→v3는 선정 출처 수를 늘린 것이 아니라 **논문 19개의 접근 차단 상태를 원문 확보 상태로 바꾼 것**이다. v3의 선정 39개 payload는 다운로드한 ZIP의 실제 크기·SHA와 전부 일치했다. post-database 패키지 안의 v3 ZIP도 같은 SHA이므로 별도 원문 집합으로 중복 계산하지 않았다. HE 원문 백업 영수증은 과거 Drive R3 실제 복원과 Dropbox R0 ACK를 구별한다. 이번 감사는 Drive v3를 새로 읽었으며 Dropbox HE v3의 새 raw 복원을 주장하지 않는다. 증거: [E-HE-DB](../drive/DATABASE_REVIEW.json), [E-HE-PAYLOAD](../drive/HE_V3_CATALOG_PAYLOAD_CHECK.json), [E-HE-BACKUP](../drive/receipts/BASS_HE_BACKUP_RECEIPT_20261001_v3.json).

**가장 중요한 상태 정정은 HE B1의 P04 erratum이다.** 초기 v3의 “표를 찾지 못함” 판정은 현재 상태가 아니다. Minami 2008에는 Appendix A1–A12가 있으며, B1은 Table A3의 source-native **5 keV/u 비어 있지 않은 63개 cell**을 전사했다. 번호가 붙은 표 제목을 찾지 못한 구현상의 false-negative를 명시적으로 정정한다. B1 전체 보존 source cell은 1,131개(ScienceDB 743, P03 9, P04 63, P08 16, P09 300)다. 별도 P09 convergence 300 token은 단면적/표준편차 데이터로 더하지 않는다. 이번 감사는 이 전사 기록과 원문 bytes 근거를 읽었으며 PDF를 독립적으로 재전사한 것은 아니다. 증거: [E-HE-B1-ERRATA](../drive/intake/he_postdb/BASS_HE_POST_DATABASE_A1_B1_20261001_v1/B1/SOURCE_RECOVERY_ERRATA.json), [E-HE-B1-RESULT](../drive/intake/he_postdb/BASS_HE_POST_DATABASE_A1_B1_20261001_v1/B1/RESULT.json).

현재 남은 자료/적용 한계는 [CURRENT_GAPS.json](CURRENT_GAPS.json)에 구분했다.

- **CR 범위:** 31개 선정 문헌의 확보와 더 넓은 역사적 방법 문헌의 확보는 별개다. 새로 읽은 방법 문서 5개에서 DOI 13종을 찾았고 그중 11종은 이 31-work DB 밖이다. [추가 DOI 목록](ADDITIONAL_METHOD_DOI_LEADS.csv)은 기존 문서의 언급 목록이며 새 원문 확보 목록이나 전체 클라우드 미확보 목록이 아니다.
- **HE 수치 비교:** P04의 lab/CM, H(1s) 연결 근거, finite-mass 및 AOCC-A의 2차 출처 관계를 해소해야 한다. 저자 standalone raw와 Appendix A1–A12 전체 전사는 아직 없다. P09는 Tables 25–30을 전사했고 나머지 108개는 미전사다. P10 WPCCC 저자 raw는 미확보이며 기록된 에너지 범위는 요청한 5/0.5 keV/u 밖이다. ScienceDB 4파일의 단위·에너지 frame은 불명이며 native exact 5/0.5 grid가 없다. **검토한 제한된 source set에서 exact 0.5 keV/u의 비교 권위가 아직 확립되지 않았다.** 전 세계 문헌에 없다는 뜻은 아니다.
- **WU088:** 원 DB bytes, INTLAB raw package, COSY raw package가 남아 있다. COSY manual 확보는 소스 확보가 아니다. P04 기관 PostScript와 최종 출판판의 비교 및 5개 인용 URL의 원 snapshot도 미확정이다. 이번 v3 DB 패키지는 66개 payload의 참조를 보유하지만 별도 원문 archive 전체를 새로 내려받은 것은 아니다.

HE의 후속 자료에서는 C1B의 독립 좌표계 reference와 결합행렬, C2의 유한 R 검증, Fortran/OpenMP·MPI 최적화 기록을 추가로 읽었다. C2는 CR R4T보다 늦은 **별도 HE 프로젝트** 자료다. R≤4의 일부 점별 기준은 통과했지만 R8/R16 force quadrature와 m=0 overlap 연결이 미해결이고, D1 충돌전파·단면적은 `NOT_RUN`이다. 실제 NCP 64코어 scaling도 `NOT_RUN`이다. 독립 basis·quadrature·box 검증, MPI 독립 작업 분할, 고정 순서 FP64 kernel은 방법 설계의 참고가 되지만 서로 다른 물리계의 정확도나 속도 결과를 CR로 옮길 수는 없다. 증거: [E-HE-C2](../drive/intake/he_c2/BASS_HE_C2_FINITE_R_AUDIT_20261001_v1/C2_FINITE_R_AUDIT_KO.md), [E-HE-HPC](../drive/intake/he_ncp64/BASS_HE_NCP64_OPTIMIZATION_20261001_v1/REPORT_KO.md).

감사 범위는 다음과 같이 제한된다. Drive는 관측 metadata 1,769개 중 관련/DB 탐색 단서 705개를 정규화했고, document 검색 페이지는 끝까지 소진했다. 그러나 관측된 검색 도구는 ZIP/SQLite 본체를 누락했고 별도 folder 목록은 **1,000개 상한에 도달한 뒤 continuation을 주지 않았다.** Dropbox는 관련 객체 347개를 정규화했으며 11개 검색·목록 영수증의 2,571행과 각 마지막 `has_more=false`를 보존했다. 두 provider의 관련 metadata 객체 1,052개는 서로 다른 내용 1,052종을 뜻하지 않는다. 실제 내려받은 ZIP 11개와 SQLite 11종, 관련 CSV들은 SHA 기준으로 묶었다.

따라서 **접근 가능한 전체 Drive/Dropbox의 모든 binary DB를 전수 확인했다는 주장은 하지 않는다.** 지정 검색 범위 밖의 객체, 삭제/과거 revision, 모든 multipart payload와 과거 runtime tree, 원 논문 전체의 새 과학적 재검증은 범위 밖이다. 클라우드 수정·다운로드 코드 실행·새 물리계산·gate 승격은 이 감사에서 모두 0이다. 파일/해시/참조 검사 결과는 [VALIDATION.json](VALIDATION.json)에 있으며, 수치 solver의 새 실행 결과는 별도 연구 증거로 연결해야 한다.
