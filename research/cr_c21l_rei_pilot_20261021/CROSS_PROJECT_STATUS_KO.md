# 7개 관련 저장소의 최신 상태 종합

이 문서는 **2026-10-21 05:24–05:38 UTC에 완료한 intake**를 공개 가능한 내용으로 요약한다. 종합 과정에서 원격 재조사, 과거 시험·과학 계산·NCP 작업 재실행은 하지 않았다. 이후 이 연구 단위에서 실행한 pilot 결과는 별도 결과 문서가 소유한다.

## 조사 범위와 수량

| 저장소 | branch metadata 페이지별 수 | 서로 다른 branch | updated 내림차순 최신 PR 조사 수 |
|---|---:|---:|---:|
| bass_cr | 100 + 66 | 166 | 50 |
| rei_bianchi | 100 + 100 + 53 | 253 | 30 |
| BASS_HE | 86 | 86 | 20 |
| WU088_HH | 100 + 35 | 135 | 10 |
| bass | 100 + 100 + 60 | 260 | 10 |
| rec_bianchi | 100 + 32 | 132 | 10 |
| vigilode | 100 + 83 | 183 | 20 |
| **합계** | **15개 페이지** | **1,215** | **150** |

보존된 GitHub branch API 응답에서 각 행의 branch 이름과 commit SHA를 확인했고, 저장소별 중복 이름은 없었다. 모든 저장소에서 마지막 페이지가 요청한 100개보다 작아 해당 조회의 pagination을 완료했다. **1,215는 branch metadata 수이며, 읽은 source 파일·실행 결과·검증한 branch 수가 아니다.** 목록은 순차 관측이므로 하나의 원자적 시점 snapshot도 아니다. 관련 최신 branch와 실행·분석 문서를 선별해 실제 내용을 읽었다. PR 조사는 위 개수로 제한되었으며 모든 과거 PR·모든 대화·미게시 작업트리를 열람했다는 뜻이 아니다. REI PR147처럼 선택한 과학 owner의 추가 직접 읽기는 최신 PR 150개 수에 합산하지 않았다.

## 실행 source와 문서 head를 구분한 상태

| 대상 | 고정 참조 | 실제 확인한 상태와 과학적 범위 |
|---|---|---|
| **CR C21K** | content `bab323983dad5206e162dbfdaefc167f2fabea45`; PR89 문서 head `dc1c0c0721b74454958e5d16264c24ec465ba1d8` | exact epoch opacity cache와 기존 focused 검증 완료 상태 재사용. 마지막 문서 commit은 실행 source와 구분한다. C21K 새 native 경로는 NOT_RUN, native 성능 NOT_EVALUATED, 전체 가속 NOT_ESTABLISHED, `global_error_bound=null`. |
| **REI pilot owner** | PR147 `3b85dedce84d37b3e165da00685a8a984950aafe`; canonical FV 부모 PR145 `54e29dff5a90c0a785cb6dcfb004403614ca403b` | non-tilted **LRS** Bianchi I의 기존 양의 canonical FV 및 gamma/nu hierarchy 경로. `donor=None`의 collisionless lane을 재사용할 수 있다. 일반 삼축 모델·양방향 H/He EoR·관측 posterior로 확대하지 않는다. |
| **REI LRS backlog** | PR198 문서 head `3360a345f8e0f2f9d2b6bdd42d21e584446ec9b8`; 고정 실행 `d234243a79e4e8e611aaf4ac61949c5ef9111468` | 과거 실제 native 131회: V12 44, V13 84, SSPRK 3. DAG 246 중 완료144·미실행100·의존차단2. 최신 head의 SSH 계약 변경은 새 native 실행이 아니다. V12의 원래 supervisor cap 초과 기록 유지. |
| **REI BE 비교** | PR199 `964b2e3c098f6e475999a4eddc7a6aa0f8f053cc`; 실행 source `4f13648985e417028c530892ea02be4f56018a31` | time8/16/32 실행과 원 validator 통과는 기존 근거로 재사용. 원래 0.005 정확도 비교 실패와 age/time 수렴 HOLD를 유지한다. |
| **HE29** | 실행 `802a32361288bf5aa0e0d1f63c912768f1a1d407`; 분석 `5eb38cbfeed7abf60e1827e358611c8f763c2da4`; 문서 `38493edccd9344c11fd66e63e1d938f77c2b093f`; PR81 복구 `fcdf56d9a66b2d159d42a9a72131f94040cd5891` | 기준해4쌍 및 packed canary1개 완료, 준비된 queue 없음. 182,280 native 호출은 이미 실행된 canary의 값이다. 새 소비자 분석은 solver/native 실행0. finite gate 통과를 continuous-spectrum·full EoR·일반 speedup으로 승격하지 않는다. |
| **WU PHYS73** | PR125 source `701cf85b80397aa51fabc56071ba90abf7ca5cfa`; PR126 최신 `367db1f18ed9e6ad5cd680e3dbd2a37ecdb0f049` | 최신 addendum은 실제 raw ZIP/ACK·4,681 payload·15 job receipt 무결성 채택을 기록한다. 이전 PR 본문과 초기 backup receipt의 미수령 상태보다 최신이다. 완료15·검증 reuse15·추가 child0. continuum/grid-error/source matching 및 HH_R10=OFF 유지. |
| **BASS S12** | scientific source `f4cd0d53760783e6a58c3b0a98c64311ca489d28`; 실행 패키지 `8247645d04695bdbfa48eb2fe74757dacf7d2636`; PR174 문서 `106a0153bf113fa4f0beea9743e84a744b65f424` | 새 NCP 반환 ZIP의 이름·크기·시각 metadata는 확인했으나 내용은 읽지 않았다. PR 본문의 NOT_RUN만으로 재실행하지도, archive 존재만으로 성공을 채택하지도 않는다. S12 short/tangent 검증과 native/reactive 전체 physics 의무를 구분한다. |
| **REC U4B** | 실행 `a09e1d249d4cf4b706c09571fa7f231c8084c251`; PR114 문서 `df95a074730ea0d13d609cf88d448f01f4a47ef1` | 74443→74475의32 accepted step 실제 반환 원문을 읽었다. `PASS_SCOPED_U4B_NUMERICAL_RESTART`, 경계 event 없음, U5/U6 미진입. 전체 allocation CPU/wall UNRESOLVED, REI activation false 및 물리·전역수렴 HOLD 유지. |
| **VigilODE** | 새 통합 source `45a1a418bcee767da982b0283016d786cd4eab07`; ledger head `de4c10a9f41321beef2313a3d7fb503bab35d714` | PR 목록에 없던 05:29UTC branch 변경을 발견했다. N01–N08 scoped 구현·failure accounting 수정과 최종 native298/doctest4/Python142 통과 기록을 읽었다. ignored5/skipped3은 별도다. 전체 workspace/native comparator/NCP benchmark는 미수행이며 광범위한 production·전역 정확도·일반 speed 승격 HOLD. |

모든 수치는 해당 원문이 소유한 실행·검증 범위다. 이 intake가 같은 scientific workload를 다시 수행한 결과가 아니다. PR의 draft/open 상태와 merge 여부도 관측 당시 정보이며, 향후 상태를 보장하지 않는다.

## 보존물 조사에서 확인한 차이

- **WU:** 최신 공개 verification은 raw ZIP/ACK의 실제 수령·검증과 Drive 전체 복원 검증을 기록한다. 이번 직접 metadata 조회도 해당 두 파일의 크기 41,903,920 / 639 bytes를 확인했다. 이번 intake에서 raw ZIP을 다시 내려받지 않았다.
- **BASS:** `BASS_S12_NCP_EXECUTION_20261021_8247645d_eb522092.zip`, 157,420,884 bytes, 수정 시각03:30:32UTC를 확인했다. **METADATA_ONLY**이며 scientific admission은 하지 않았다. 완료 여부는 이 반환을 담당하는 lane이 원문으로 판정한다.
- **HE/REC:** 각각 새 분석 보존물과 U4B 실행 보존물의 이름·크기를 직접 확인했다. 전체 raw hash 검증은 공개된 기존 receipt의 범위로 재사용했다.
- **REI:** 04:00UTC IGM 보고서와 04:25UTC SSH handoff 보존물을 발견했다. 이후 Git PR198 head가 더 최신이므로 이전 보고서를 현재 실행 source로 쓰지 않았다.
- **Drive 검색:** broad/recent 및 제목 검색이0개를 반환했지만, 알려진 WU 파일 ID의 직접 metadata 읽기는 성공했다. 이를 **검색 coverage gap**으로 기록한다. 검색0은 저장 파일 부재의 증거가 아니다.

이 공개 요약에는 개인 대화 원문, 이메일, signed URL, 인증정보, 비관련 파일 metadata와 비공개 저장처 ID를 포함하지 않았다.

## 이번 pilot에 대한 결정

기존 REI PR147/PR145의 실제 물리 owner를 사용하고, CR의 기여는 **독립 case 병렬 실행·불변 계산 재사용·물리량 변환·완료 결과 집계**에 집중한다. C21K 전체 campaign, 완료된 HE/WU 작업, REC 다음 continuation, VigilODE의 새3,221결과 benchmark를 오늘 pilot의 선행 의무로 추가하지 않는다. 새로운 가속 배율이나 전역 오차 상계도 이 intake에서 발행하지 않는다.

## 공개 primary 원문

- [CR PR89](https://github.com/cosmosapjw-quantum/bass_cr/pull/89)
- [REI PR147 response](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3b85dedce84d37b3e165da00685a8a984950aafe/research/rei_sigma_pi_response_20261015/response.py)
- [REI PR147 canonical FV](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3b85dedce84d37b3e165da00685a8a984950aafe/research/rei_bass_hierarchy_backreaction_20261015/canonical_fv_20261015/canonical_fv.py)
- [REI LRS 실행 보고서](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/3360a345f8e0f2f9d2b6bdd42d21e584446ec9b8/research/lrs_atomic_native_bridge_20261016/v14/vigilode_radau_20261019/parallel_campaign_20261020/ncp_backlog_20261021/REPORT_KO.md)
- [HE 현재 DAG](https://github.com/cosmosapjw-quantum/BASS_HE/blob/38493edccd9344c11fd66e63e1d938f77c2b093f/research/he29_survival_budget_20261018/DAG_STATUS.json)
- [WU 최신 raw verification](https://github.com/cosmosapjw-quantum/WU088_HH/blob/367db1f18ed9e6ad5cd680e3dbd2a37ecdb0f049/research/hh_phys73_return_intake_20261021/RETURN_VERIFICATION_20261021.json)
- [BASS PR174](https://github.com/cosmosapjw-quantum/bass/pull/174)
- [REC U4B 결과](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/df95a074730ea0d13d609cf88d448f01f4a47ef1/research/rec_r3t_u4b_20261021/ncp_execution_001/NCP_CAMPAIGN_RESULTS.json)
- [VigilODE 새 decision](https://github.com/cosmosapjw-quantum/vigilode/blob/45a1a418bcee767da982b0283016d786cd4eab07/research/production_reaudit_20261021/DECISION.json)

실행: 기존 intake 재사용, 종합 중 새 scientific run0. 게시: 이 요약은 parent 연구 단위의 게시에 포함할 준비물. 백업: 조사한 기존 보존물과 parent가 생성할 새 배송물을 구분. DAG: 관련 완료·미수행·HOLD를 위 source별로 유지하고 pilot 경로를 독립 연결한다.
