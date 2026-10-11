# PHYS02E source intake — PR33 실제 첫 실패 반환

이 문서는 read-only source intake다. 후보·acceptance 설계, 과학 코드 수정, G 생성, pulse 전파, 재시도와 원격 mutation은 수행하지 않았다. 관측한 Git/백업 원문 사실과 미확인 사항을 구분한다.

## 최신 source와 계보

- PR33: https://github.com/cosmosapjw-quantum/bass_cr/pull/33 (open draft).
- Head branch: `research/cr-phys02d-ncp-pulse-return-20261011`.
- 실제 최신 head: `20c2e6de7c58c3690efca6322489b811c99f3e99`; tree `d47ad3e29b96953aae45570c6bdb6f4a71bfc7dc`.
- 부모 payload commit: `716c64216c7af2056b0c5bae415f2a2584420335`; tree `773bab5f52462cd5ba866fbbc5ce14798dbe4d3a`.
- payload 부모: PR32 receipt `a2486869dba5c2d43257c13e33a31b66752d5e10`.
- matching-refs와 실제 Git commit 응답에서 이 관계를 확인했다. 최근 업데이트 PR 12개와 PHYS02D refs 범위에서 PR33 이후 pulse/amendment PR을 발견하지 않았다. 이는 모든 unpublished branch/local 작업의 부재를 주장하지 않는다.
- `PUBLICATION_RECEIPT.json`은 이전 payload commit 시점 영수증이어서 `final_receipt_commit_has_not_yet_been_created=true`가 남아 있다. 현재 head를 가리키는 문장이 아니며 실제 후속 receipt commit은 위 20c2e6d다.

## 실제 실행 사실 (원문 및 Git blob identity 확인)

원문 디렉터리는 `research/cr_phys02d_ncp_return_20261011/`이다. 주요 8개 원문을 `pr33/`에 그대로 저장했고 각각의 UTF-8 bytes에서 계산한 Git blob SHA1이 PR33 files API의 blob과 일치한다. SHA256/bytes/경로는 `SOURCE_INTAKE.json`에 있다.

- `actual_run/ACTUAL_EXIT.json`: launcher actual exit **1**, start `2026-10-11T00:27:45Z`, end `2026-10-11T00:29:29Z`, wall **103.79789273899951 s**, observed child exit 1, deadline 3600 s, deadline overflow 없음.
- `EXECUTION_SUMMARY.json`: execute invocation 1, build reservation 1, pulse reservation/call 0, fullBED constructor가 반환한 뒤 guard에서 실패. legacy 미시작. G 저장본 없음. 과거 ramp/과거 과학 suite 실행 0. wrapper exit 0은 실패 수집이 끝났다는 뜻이다.
- runtime: Python 3.12.3, NumPy 2.4.2, SciPy 1.17.0, 보고된 BLAS thread 1. resource admitted true; 수치 코드/허용값/입력/원래 운영 어댑터 변경 0; 자동 재시도 false.
- 첫 오류: `STORED_SOURCE_GRID_FIELDS_MISMATCH`, 위치 `ncp/launch_pulse.py:74`, 실제 false predicate `np.array_equal(cascade.E, saved energy_eV)`.
- `actual_run/operational_sidecars/GRID_DIAGNOSTIC.json`: fullBED와 legacy 저장 NPZ 각각에서 동일한 340/9600 energy nodes 불일치. 최대 절대차 `1.1368683772161603e-13 eV`. required fields, time shape/equality, source shape `(9611,2)`, birth tags는 모두 통과.
- 저장 E raw-byte SHA256: `6a76d3539115003b046a5861baca89b0a4ff966564627e04d9f6e8bc86be8292`.
- 재생성 E raw-byte SHA256: `870cfd5f3f2656371d5fad59e4b24f4b7aa051546b9d78f4f3a9de3197fcc0a4`.
- `INDEPENDENT_ACTUAL_RETURN_DECISION.json`: **HOLD**, SHA256 `ca5f3b8baba7605b5f857aef437b41ba61cfeea2facc1d00c4183e8c3e7534b4`. 독립 AST-isolated grid probe는 두 모형에서 최대 1 ULP를 기록했다. 이 intake는 그 probe를 재실행하지 않았다.
- CDF, 무한 시간 모멘트, ramp residual은 **UNAVAILABLE**. 작은 ULP 차이가 물리적으로 허용되는지 또는 G가 동등한지는 **미입증**. SIMD/libm/platform 원인도 **가설, unresolved**다.

## 기존 반환이 제안한 amendment (여기서 설계·승인하지 않음)

기존 독립 판정은 `PROPOSED_ONLY_NOT_AUTHORIZED_OR_IMPLEMENTED`로 두 경로를 열거한다: 모든 grid-dependent 연산 및 G 구성 전에 pinned saved E를 설치하는 검토된 생성자 경로, 또는 저장 E 전부를 정확히 재현하는 고정 runtime grid 경로. 양쪽 NPZ와 E hash를 G 이전에 검사해야 한다. E의 allclose 허용, 저장 NPZ 수정, G 생성 후 E 교체, unused old reservation 재사용, 자동 retry는 금지한다. 추가 G/pulse 승인 수는 각각 0이다. 새 제한 계약과 독립 심사 전 실제 실행은 HOLD다. 일곱 기존 gate는 변하지 않았다.

## 실제 백업 metadata

정확한 각 ID를 다시 조회하여 name/bytes/folder 또는 path/rev를 확인했다. provider checksum은 반환되지 않았고 이 intake는 ZIP byte materialization/remote restore를 수행하지 않았다. ZIP SHA256은 Git에 게시된 local archive receipt의 값으로 분류한다.

완전 실제 반환 ZIP:
- 이름: `CR_PHYS02D_PULSE_RETURN_20261011T003258Z_024b083109e648b38db699d06436f5e5.zip`
- bytes: **5350251**
- 게시된 SHA256: `2400e9a4350d03379b12fdad00c8990c93099011dfc95530b02ae2c26e8dc4c5`
- Drive ID: `18RE6v7GmGE33x1uQaFsLcvEac7Jcnd6E`
- Drive URL: https://drive.google.com/file/d/18RE6v7GmGE33x1uQaFsLcvEac7Jcnd6E/view
- Dropbox ID: `id:BSpOijBcT10AAAAAAD3-1Q`, rev `65d85bb5eb64b0af03d47`
- Dropbox path: `/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02D_PULSE_RETURN_20261011T003258Z_024b083109e648b38db699d06436f5e5.zip`

짧은 실행 요약:
- 이름: `CR_PHYS02D_NCP_EXECUTION_20261011T003258Z_024b0831_KO.md`
- bytes **3583**, 게시된 SHA256 `27f4e750785ba7501f7ae77522513ba181d9c5806f196b42bc456843339ce102`
- Drive ID `1y8tqVcpIokIlt8Dmk7eGKpUc6Npu70_p`
- Dropbox ID `id:BSpOijBcT10AAAAAAD3-1A`, rev `65d85bb5794d80af03d47`
- Dropbox path `/BASS_DERIVATION_DOSSIERS_20260912/CR_PHYS02D_NCP_EXECUTION_20261011T003258Z_024b0831_KO.md`

Drive 검색에서는 제목이 맞는 markdown 두 개만 반환되었고 ZIP은 exact ID get으로 확인했다. 검색 누락을 파일 부재로 해석하지 않는다.

## 관련 lane의 최신 metadata 선별

- BASS_HE PR20 `0633ec2c9aed37593b9f1c05abc7156727408583`: OFF/KF/GM의 2440 nodes × 첫 두 captured steps finite enclosure, 독립 PASS_SCOPED. physical/global/production, 새 gas evolution, photon/heat/recoil delivery 및 receiver adoption HOLD. CR frozen E 입력을 교체하거나 exact-grid 문제를 해소하는 dependency로 확인되지 않아 import하지 않았다.
- BASS_HE PR19 `2085aee95970d95f9b91610bd28e0dc5d0948aab`: selected first2 branch cover. PR updated date가 더 최근이므로 목록 순서와 연구 단계 순서를 혼동하지 않았다.
- WU088_HH PR35 `baf23360627bc1c6d10aac5317052f23edafd1b1`: energy-coordinate/finite mixed rectangle의 이론 및 exact reference 작업, actual W/native tube/연속 나머지 HOLD. CR E/source/atomic 입력을 대체하는 새 dependency로 확인되지 않아 import하지 않았다.

이 선별은 각 repo 최근 PR 3개의 제목·body·head metadata에 한정되며 대규모 재감사 또는 과학적 수신 승인으로 해석하지 않는다.

## 권위 문서 source 추가 확인

현재 main은 `77237751bdd2aed5934bf7fc3bc626d631a09058`로 이전 source와 같다. PR33의 49개 추가 파일은 전부 반환 unit 하위이므로 PR32의 root AGENTS 및 docs 정책 변경은 없다. root `AGENTS.md`를 원문으로 저장하고 tree blob `75274768eb74c2d5558a5bfc1d5bc0eb72de681f`와 확인했다. 실제 head root tree에는 `.codex` 항목이 없고 contents 및 `.codex/readback-policy.json` 원문 호출 모두 404였다. 이 확인은 `.codex` tier policy가 현재 존재하거나 확인되었다는 주장을 허용하지 않는다. 존재하는 `docs/READBACK_POLICY.md`, `docs/CHATGPT_CODEX_DIVISION_OF_LABOR_KO.md`, `docs/HPC_ACCURACY_POLICY_KO.md`의 exact blob은 JSON policy_check에 기록했다.

`pr33/RETURN_MANIFEST.json`도 exact head에서 받아 원문으로 저장하고 Git blob identity를 확인했다. 전체 반환 ZIP은 이 intake에서 다운로드하지 않았다.
