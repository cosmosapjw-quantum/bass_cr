# 백업·연결 대화 조사 — R1–R3 지원

관측일: 2026-10-27 KST. 범위는 `cosmosapjw-quantum/bass_cr`의 재개에 필요한 관련 과학 자료와 백업이다. 기준 science S=`4caf4273eefd51f2c605a8667c3533d8489dd0f5`, docs D=`b11b2e9255f2b10fb5582376412e045bd1e9151c`, central M=`3f287279c9ae4e8bcd4949a56b8c4cc0601b1eb8`를 출발점으로 삼았다. 이 조사는 새 과학 계산이나 gate 승격을 수행하지 않았다.

## 1. 조사 범위와 완전성

| 표면 | 실제 조사 | 정확한 완전성 범위 |
|---|---|---|
| Dropbox 연구 dossier root | `/BASS_DERIVATION_DOSSIERS_20260912` 직접 항목 3,428개, 6페이지 | 마지막 `has_more=false`; root 직접 항목 목록 완료. 59개 하위 폴더 전체를 모두 재귀 탐색한 것은 아니다. |
| Dropbox bass_cr | 동일 root의 `bass_cr` 재귀 99개, 1페이지 | `has_more=false`; 해당 하위 트리 목록 완료. |
| Dropbox REI backups | `/bianchi/research_backups/rei_bianchi` 재귀 181개, 1페이지 | `has_more=false`; 해당 하위 트리 목록 완료. |
| Library | `modified_after=2026-10-25T00:00:00Z` 재귀 314개, 2페이지 | 마지막 cursor=null. 이 시간창의 목록 완료; 관련 연구 후보 56개를 별도 보존했다. 다른 개인 자료는 산출 inventory에서 제외했다. |
| Drive bass_cr folder | `1V4ZQza59dWVC7apeRz9P1TL66eaVYyJy` 직접 81개 | 도구가 continuation/completeness flag를 제공하지 않아 반환된 범위로만 주장한다. |
| Drive 일반 BASS backup folder | `1fFxb-qgExWbEomt3EbbOjGKcslFpGv3y` 100개 | 제한된 반환으로 명시적으로 PARTIAL. |
| Drive C22C 분할 폴더 | `1dFvfDSGpXaOBOILUfVDUYRwQSZrBDfvS` 15개 | 14개 part +1 manifest의 실제 metadata를 확인. 이번 조사에서 14 part를 재다운로드하지 않았다. |
| 다른 대화 | Personal Context에 연구명·고정 SHA·누락 맥락을 명시해 실제 1회 호출 | `Personal context is unavailable for this conversation` 반환. 대화 전문 또는 전체 대화 목록을 읽었다고 주장할 수 없다. 공개된 인계서·보고서·PR comment를 대체 근거로 이용한다. |

Library의 포괄 semantic 검색은 알려진 파일을 안정적으로 찾지 못해 최근 목록으로 전환했다. Dropbox date-filtered search는 요청한 날짜 이전 항목을 반환했으므로 신선도·부재 증거에 사용하지 않았다. Drive `item_type=document`는 ZIP을 제외했으며, no-query 날짜 필터 검색은 직접 목록에 있는 파일에도 빈 결과를 내어 부재 판정에 사용하지 않았다. 완전성은 실제 cursor/has_more와 사용한 표면 범위에만 연결한다.

원 기록: `INVENTORY_FINAL.json`. 전체 raw Dropbox 목록은 크고 연구 백업 식별자를 포함하므로 공개 Git에는 필요한 요약/소스행만 가져오고, 전체 inventory는 사용자 백업 산출물로 보존하는 편이 적합하다.

## 2. 기존 bass_cr 과학 authority는 그대로

Dropbox bass_cr 재귀 목록과 Library 최신 시간창에서 기존 He4 source/closeout 두 ZIP 이후의 새 bass_cr 과학 ZIP은 발견되지 않았다. 기존 canonical source 29,763,489B와 closeout 861,631B의 ID/크기는 부모가 복구하는 고정 자료와 일치한다. 같은 자료를 중복 다운로드하지 않았다.

이 관측은 다음 H1 backfill과 구분된다. backfill은 새 저장 상태이며 과학 source 변경이 아니다.

## 3. 실제 새 H1/C22C 저장 상태

PR105 comment `6415035533`과 PR96 comment `6415034627`(2026-10-26)에 독립 백필이 게시돼 있다. `survey_bass/COMMENTS_105.json`, `COMMENTS_96.json`은 다른 조사자가 실제 회수한 comment 원문이다.

- H1 canonical ZIP: Drive `1eXKj4aQUXPW_XjMtKjPVvghseaT8pnpU`, 18,232,953B; 기존 기록 SHA256 `f1afdb40303b28a498a62f9f8d38858b8bea584d0ed8a4e63bd87e4e11d362c5`. 이 조사에서는 현재 metadata를 확인했고, 10/26의 164 payload/CRC/raw-readback receipt를 읽어 재사용했다. 18MB 원본 재다운로드는 하지 않았다.
- H1 final-authority JSON: Drive `1cwtOkPLqVoXrEj8r_ZepPQ-F5H3VcQHy`를 이번에 실제 raw GET했다. **38,849B**, SHA256 **`5f37395452dea969b9f35ec295b667daadf01928e98c6280dbb56d241d852a94`**로 기존 백필 증거와 일치한다.
- C22C: 14 contiguous parts와 복원 manifest를 Drive에서 실제 목록화했다. 이번에 raw GET한 manifest는 **3,568B**, SHA256 **`b67e89c889d579cae477a8d56a394bb2b4fc81905c4b5ac97de9f0d2bbf0c631`**이며 10/26 audit 값과 일치한다. 기록된 전체 ZIP은 114,019,304B, SHA256 `b8e3448a8cdba0f0b8512dc241098a1829400c37064917048d8438788655c3fb`; 이전 14 part 실제 GET/재조립/657 payload 검증을 재사용한다.
- 공통 audit ZIP: Drive `1Hw_ywJ8uLdSZPR60SdGWgaIt8K3-T-Gz`를 이번에 raw GET했다. **8,925B**, SHA256 **`71d6f50671f490e4c22dff356c8f7e0f479ec6db9a4be476a3f75742b588a888`**. ZIP CRC 및 내부 4/4 manifest payload의 크기/SHA256이 일치했다.

**역사적 `UNKNOWN_NO_ACK`는 보존한다.** 10/26 백필 관측은 별도 현재 증거다. 옛 H1 terminal은 재구성됐다고 주장하지 않으며, 새 저장 성공을 H1/He4 RR나 stopping의 물리적 완성으로 승격하지 않는다. 현재 조사에서도 C22C full parts, H1 full ZIP, 기존 Dropbox full ZIP의 새로운 raw GET은 수행하지 않았다.

## 4. 가장 유용한 신규 과학 입력: REI PR236 source-only 연산자

최신 IGM 보고서 원문을 Library에서 끝까지 읽었다(619 lines/13 pages; `libfile_3adb01969458819198c5212bb51b9c54`). 그 보고서가 관측한 PR236 head는 `ee94bef85b56d879dc38f184856a5c613575e9e1`이다. PR236의 최신 실제 SHA는 부모의 Git 조사에서 다시 고정해야 한다.

최신 Dropbox source ZIP **`REI_COUPLED_SOURCE_20261027_1b80efed0892.zip`**도 실제 회수했다.

- ID `id:BSpOijBcT10AAAAAAECMsg`
- **3,477,069B**
- SHA256 **`1b80efed0892f3368dc307e3cd6757b93dc444a4d7d2d186b352b926e230648a`**
- 307 ZIP members, CRC PASS.
- 실제 바이트의 Dropbox content hash `6ed577b650eaaeec06293c263b98858153d3f11fef5774a1ce1d07fd42c8a987`가 provider 값과 일치.
- 복원 경로 `rei_latest_read/`. 기존 실행 입력 manifest **9/9 +13/13** 및 최종 리뷰의 source/checker/successful runner/stdout/PNG **5개 binding**이 실제 파일 SHA256과 일치한다.
- 이는 복원/출처 확인이다. 원 검사를 재실행하지 않았고 신규 독립 과학 검토를 대신하지 않는다.

핵심 내용은 `research/rei_expanded_event_consumer/coupled_source_20261027/`의 REPORT, CONTRACT, ADMISSION, review/VALIDATION, BUDGET, HANDOFF에서 실제 읽었다.

21종 abundance에 비열적 전자수 \(\zeta\), 비열적 kinetic energy \(w_{nt}\), 외부 signed photon debit \(w_{ext}\), \(\log T\)를 더한 **25좌표** source/JVP다. Native `PW19HeIINetwork.evaluate(...)[photo_rhs]`를 소비하며 He3II 8→9 / He4II 11→12가 선택 사건이다. 전하 전자수는 \(q^T Y\), 열적 전자수는 \(q^TY-\zeta\), 열적 입자수는 \(\chi_{th}=(1+q)^TY-\zeta\)다. source-only에서 \(\dot\zeta=q^TP\)이므로 \(\dot\chi_{th}=0\), \(Q_{th}=0\)이면 \(\dot{\log T}=0\)이다. 이는 열화 전 순간 source identity다.

원 source는 z=2.479 donor, \(n_b=10.669321142818111\,m^{-3}\), \(T=14919.863839279506\,K\), photon 54.42–50000eV/primary 0–49945.58eV이며 He3/He4 elemental electronic equality는 조건부 모델이다. 실제 저장 관측은 birth `2.484719529390961e-19 m^-3 s^-1`, primary power `7.949751527088791e-37 W m^-3`. 원 attempt01의 28 PASS와 attempt03의 68 신규 check entries가 기록돼 있다. 이를 96개의 독립 고유 검사나 현재 실행 결과로 부르지 않는다.

다음 실제 의무는 **number와 energy의 assimilation 전달을 함께 공급하고 native RR/DR/Compton의 thermal-electron density와 맞추는 것**이다. source-only 기존 결과를 다시 만들 필요가 없다. \(Q_{nt}/3\le\dot P_{nt}\le2Q_{nt}/3\) 압력 구간은 constitutive stress 또는 stopping closure가 아니다.

이 producer의 planning ledger는 **12.196274495 CPU s**, 원 cap10/임시14 만료, main **595.225063/600 CPU s, NO_MORE_IVPs**다. bass_cr의 별도 예산과 합치거나 초기화하지 않는다. `REC-COUPLED=PARTIAL`, `L4=false`, count effect0이며 역사적 branch 선언32/88과 중앙27/88은 각각의 branch/body로 검증해야 한다.

## 5. 같이 발견했지만 현재 CR 완성으로 합치지 않을 결과

### VigilODE V6

Library delivery receipt `libfile_b903d9a89eac8191ad7c82c6a0e2e3ee`를 실제 읽었다. actual-point binding 3 pairs/RHS119/Jacobian7, wall38.8538746/120s가 기록돼 있다. source ZIP SHA256 `8779aef897595e2d4cbbe2e46ff18bae9f4521e8a66066379b864947c216d555`, 1,223,513B. Dropbox ID `id:BSpOijBcT10AAAAAAECM0w`는 현재181-entry 목록에도 있다. GitHub는 BLOCKED_EXTERNAL_NO_COMPLETION_ACK, Drive UNKNOWN_NO_ACK, native integration OPEN/V7 NOT_RUN/V8 false/production HOLD다. 새 callback 전체통합 또는 물리적 공급자 승인으로 사용하지 않는다. 이번에 이 ZIP 자체는 다운로드하지 않았다.

### BASS dual-lane 설계

`BASS_DUAL_LANE_RESEARCH_DAG_20261026.md`와 `BASS_HF_BF_DAG_PATCH_20261026.json`을 실제 읽었다. 15노드 additive **설계 제안**이며 원 source owner `cc602e209e7deeb511ab2a1f3b2268d55206c43c`를 참조한다. 기존 low/high multipole Schur memory, rank-9 Thomson gain, finite-amplitude opacity covariance의 toy 확인을 제시한다. 현재 중앙 DAG를 수정한 것이 아니므로 88의 분모에 이15를 합산하지 않는다. CR의 full heating이나 cosmological history 완료로 채택할 입력도 아니다.

## 6. 실행·보존 상태

이 child는 원격 mutation0, science execution0, 과거 suite replay0를 수행했다. 네 개의 작은/중간 새 source objects를 실제 다운로드했고 기존 고정 He4 두 ZIP의 다운로드는 부모에게 맡겼다. 해시/압축/텍스트 검사의 mechanical CPU는 별도 미계측이며 0이라고 주장하지 않는다.

사용 skill context: 현재 callable PhysMath1.3.0의 THEORY R1–R3 및 POLICY_INTEGRATION, 사용자가 붙인1.0의 근거재사용 규칙, Library/GoogleDrive/Dropbox find+inspect/PersonalContext. 새 이론·코딩 단계의 완료 선언, 독립 review-of-review, 임의 provider 활성화는 수행하지 않았다.

주요 산출물: `INVENTORY_FINAL.json`, `MECHANICAL_VERIFICATION.json`, `RAW_READBACK_NEW.json`, 본 문서와 Library 읽기 기록, 실제 audit/H1 authority/C22C manifest/REI ZIP 및 해제 소스. Signed transfer URLs은 사용 뒤 삭제했으며 보존 산출물에 없다.

다음 최소 행동: 부모가 최신 Git source와 중앙/producer DAG를 고정하고, 이 복원된 source-only 입출력·예산·gate를 재사용해 다음 CR 연구 단위의 계약을 선택한다.

