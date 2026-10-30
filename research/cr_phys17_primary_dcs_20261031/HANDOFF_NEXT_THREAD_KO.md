# BASS_CR PHYS17 | 다음 대화 인계 (출처 기반 원전 DCS)

```text
PROJECT=cosmosapjw-quantum/bass_cr
PARENT_PR=141
IMMUTABLE_PARENT_HEAD=30020355677b66930856a385cf5cd4e9c3c3a24c
PARENT_FULL_SOURCE_SHA256=3b316c595fc1b40109f39d91af92873ba5a215281040d70bcb177dd1ab74a7dc
UNIT=CR_PHYS17_PRIMARY_1976_UB_2P_DCS_SOURCE_RECOIL
KINGSTON1976_ORIGINAL_PDF_SHA256=d7767365440f840e5638eec38a46223bfbbf3a27a4c0296ecc1d35b6ec1b1c78
WILLIAMS1976_ORIGINAL_PDF_SHA256=09d3cb9c950f74624e7cd35d75d6d8a154d22102f19d75ee42493ff9d4c586ed
ORIGINAL_RR_SOURCE_PHOTONS=6400
ORIGINAL_2P_VALID_SOURCE_ATOMS=2066_HE_ORIGIN
PRIMARY_TABLE_DATA=KINGSTON_TABLE5_2P_UB_NOT_CC;KINGSTON_TABLE4_2S_UB;WILLIAMS_TABLE1_N2_MEASURED_NOT_2P
NEW_SCIENCE_CSV_ROWS=4190
PHYS17_EMISSION_CLOSURES=KFB_UB2P_E1;KFB_UB2P_ISOTROPIC_EMISSION;PWBA_E1_PARENT
UNIQUE_2P_MAGNETIC_ALIGNMENT=UNBOUND
COMMON_EVOLVING_GAS_RADIATION_CLOCK_GEOMETRY=UNBOUND
PHYSICAL_K=UNBOUND
GLOBAL_HE_EXCLUSIVE=UNBOUND
FULL_RII_DETAILED_BALANCE=UNBOUND
CENTRAL_DAG=28/88_DELTA0
EXTENSION_DAG=0/3_DELTA0
PHYS17_AUXILIARY=1/1_CONDITIONAL_REVIEW_HOLD
SCOPED_R_C=18/20 (TRUE_DISTINCT_AUTHOR_R06_C09_NOT_RUN)
NATIVE_SUBAGENT=NOT_RUN
PRODUCTION=NATIVE25=L4=HOLD
NO_MERGE=true
NO_FORCE_PUSH=true
AUTO_NEXT_NODE=false
NEXT_CANDIDATE_ONLY=H_2P_MAGNETIC_SUBLEVEL_DENSITY_MATRIX_OR_2P_RESOLVED_EXACT_DCS_IN_SOURCE_WINDOW
```

## 최신 게시 링크와 current HEAD

최종 GitHub PR/commit과 양쪽 provider restore receipt는 외부 게재 후 별도 `PUBLICATION_RECEIPT_AND_HANDOFF_20261031.md`로 저장한다. 이 원본 패키지 안에는 아직 발생하지 않은 GitHub ack를 미리 기록하지 않는다.

## 새로운 과학 내용 및 남은 엄밀한 경계

Kingston p613 Table5 2p DCS는 **unitarized Born** original computed data이고 Williams p1526 Table1은 measured inclusive n=2 DCS. 본 루프는 source-owned 2066 H2p events의 각도 PDF를 prior PWBA로부터 original KFB UB table-conditioned interpolation으로 바꾸고 E1 q-axis alignment를 별도 가정으로 유지해 new time-ordered Lyα first-scattering spectrum을 계산했다. Williams data는 **독립 불일치 진단**으로만 사용한다. 19.58 eV에서 KFB 2p pure theory > measured n2 total central at 6/16 angular points, showing model deficiency. No measured pure 2p DCS or density matrix bound; therefore physical unique photon PDF and global radiative transfer are still open.

## 복원

Source-inclusive ZIP 압축 해제 후 `bash REPRODUCE.sh`. 이 스크립트는 SOURCE ZIP 속 원본 PR141 archive에서 PHYS15/PHYS16 필요한 parent files를 꺼내 clean scratch에서 전 계산을 재생성하며 normal/optimized tests, numerical+PNG SHA match를 수행한다. User-supplied full copyright PDF들은 배포하지 않는다: original PDF source identity SHA/DOI만 보존. R/C 20개 stage records는 동일 연구 단위 내 체크포인트일 뿐 20개 독립 실험을 뜻하지 않는다.
