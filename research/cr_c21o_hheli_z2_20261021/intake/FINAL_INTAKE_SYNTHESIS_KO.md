# C21O 최종 intake 합성: 게시 계보, 외부 반환, 재사용 근거

이 문서는 2026-10-21의 기존 intake·게시 영수증·완료 검증을 연결한 공개용 요약이다.
최신 Git ref 관측 시각은 **14:42:28 UTC**, 저장처·대화 검색 영수증은
**14:47:05 UTC**다. 이후 C21O의 새 51개 적분과 분석이 완료되어 그 상태를
덧붙였다. 문서를 쓰면서 추가 웹 전수조사, 과학 적분, 기존 검증 반복,
Git 변경 또는 provider 업로드를 수행하지 않았다.

## 1. 조사 범위와 권위의 구분

7개 저장소의 advertised branch head를 모두 수집했다. 관측한 1,246개 head는
직전 13:06 intake의 1,240개보다 6개 늘었고, 별도로 기존 head 4개가 변경됐다.
저장소는 `bass_cr`, `rei_bianchi`, `bass`, `BASS_HE`, `WU088_HH`,
`rec_bianchi`, `vigilode`다. 각 저장소에서 최근 갱신된 PR metadata 40개씩,
총 280개를 확인하고 새 변경분과 직접 관련된 원자·coupling 실행 소스를 읽었다.
**모든 branch의 모든 파일이나 모든 과거 PR 본문을 읽었다는 의미는 아니다.**
근거는 [LIVE_REFS.json](github/LIVE_REFS.json),
[LIVE_REF_DELTA.json](github/LIVE_REF_DELTA.json),
[INTAKE_LEDGER.json](github/INTAKE_LEDGER.json)이다.

과학 provenance의 권위는 고정 source·input·실행 manifest와 실제 raw의 hash,
그 범위에 결속된 검증이다. 최신 branch가 생겼다는 이유로 완료된 계산의 source를
바꾸지 않았다. Git content SHA와 document SHA, provider에 보관된 사본,
다른 스레드의 설명을 각각 구분한다. Provider에서 읽은 문서 text는 유용한
intake 단서지만 raw source/trajectory의 byte 검증을 대신하지 않는다.

## 2. C21L/M/N의 실제 게시 계보

아래 여섯 branch의 최종 head는 14:42 live-ref snapshot에서 다시 관측됐다.
표의 content/document 구분은 기존 실제 게시 영수증을 재사용한다.

| 단위·PR | 실제 content 또는 외부 반환 head | document head / 관측 branch head | 상태 |
|---|---|---|---|
| C21L 원 pilot, [PR90](https://github.com/cosmosapjw-quantum/bass_cr/pull/90) | 원 content `60a3f1cb0d8f0875820d18c0d10c448d480334c4`; 성분 분리 content `17244259d25f793a25e0874443a28806e7c31d17` | `e954467132eef864a0fb86ba5de44f90f76b08e0` | 원 81개 보존, 성분 분리 게시 완료 |
| C21M 독립응력 pilot, [PR91](https://github.com/cosmosapjw-quantum/bass_cr/pull/91) | `659c94312eb9c12ebb987de934459c12a63d67b0` | `b78a943e5d7ae341bbfe84f742a06a4ac36d0e43` | 26개 신규 + 원 중심 1개 재사용 완료 |
| C21M NCP98 반환, [PR92](https://github.com/cosmosapjw-quantum/bass_cr/pull/92) | 반환 branch head `645a7f1a960be10e10574a819d7fb35a4511d9fa` | 같은 반환 head | 실제 98개 완료 결과를 C21N에서 수용 |
| C21N mass-shell/cache, [PR93](https://github.com/cosmosapjw-quantum/bass_cr/pull/93) | `5ecb8a6c4961302b7066b06278e72ecd2d77f8c9` | `0f45d0a422d79ccead565a8abaab860fcc230687` | 새 ODE 없이 125개 결과의 source-bound 분석·준비 코드 완료 |
| NCP off-grid4 반환, [PR94](https://github.com/cosmosapjw-quantum/bass_cr/pull/94) | 반환 head `92b1b3f5575375580cf8de8039252ac492353b7e` | 같은 반환 head | 같은 네 입력의 외부 실행 반환 수용 |
| C21N off-grid4, [PR95](https://github.com/cosmosapjw-quantum/bass_cr/pull/95) | sandbox content `e7729092abc6edbe74f31d0ed82aa84d5506b8d5`; NCP 수용 addendum `038aa0c8e5790f5c94e596035ea816fbca588a15` | `8dc5031b3323d4be42a7444843294200aa8887f2` | 최종 branch 게시 확인; PR head metadata 불일치 별도 OPEN |

Branch 이름은 순서대로 다음과 같다.

- `research/cr-c21l-rei-sigma-pi-pilot-20261021`
- `research/cr-c21m-independent-stress-20261021`
- `research/cr-c21m-ncp98-refinement-20261021`
- `research/cr-c21n-mass-shell-cache-20261021`
- `research/cr-c21n-offgrid4-evidence-20261021`
- `research/cr-c21n-offgrid4-sandbox-20261021`

C21M document head는 C21M content와 C21L document head를 부모로 묶는다.
고정 REI physics source는 이 과거 collisionless 계보 전체에서
`3b85dedce84d37b3e165da00685a8a984950aafe`다. C21L 성분 분석의 추가 게시를
`60a3f1…`에 이미 들어 있었다고 간주하지 않는다. 실제 후속 content는
`17244259…`이며, 초기 원 content 340개 파일을 보존한 채 31개 파일을 추가했다.
근거는 고정된 [C21L 게시 영수증](https://github.com/cosmosapjw-quantum/bass_cr/blob/e954467132eef864a0fb86ba5de44f90f76b08e0/research/cr_c21l_rei_pilot_20261021/component_closeout_20261021/CONTENT_PUBLICATION_RECEIPT.json),
[C21L 마감 문서](https://github.com/cosmosapjw-quantum/bass_cr/blob/e954467132eef864a0fb86ba5de44f90f76b08e0/research/cr_c21l_rei_pilot_20261021/COMPONENT_CLOSEOUT_KO.md),
[C21M 게시 영수증](https://github.com/cosmosapjw-quantum/bass_cr/blob/b78a943e5d7ae341bbfe84f742a06a4ac36d0e43/research/cr_c21m_independent_stress_20261021/document_closeout_20261021/CONTENT_PUBLICATION_RECEIPT.json)이다.

PR95는 특별히 구분한다. 직접 branch ref와 Git ref는 `8dc5031…`이지만,
읽었던 PR metadata와 commit 목록은 첫 content `e772909…` 한 개에 머물렀다.
이는 source/raw 충돌이 아니라 **`PR_HEAD_METADATA_MISMATCH_UNRESOLVED`**다.
최종 세 commit이 PR diff에 모두 반영됐다고 주장하지 않으며, 이 문서에서
close/reopen이나 중복 push로 해결을 시도하지 않았다.

## 3. 실제 외부 실행 수용과 중복 계산 방지

### NCP98: 과거 NOT_RUN 이후 도착한 완료 결과

PR92의 98개 결과는 C21M science content `659c943…`, document base `b78a943…`,
고정 REI source `3b85ded…`에 결속된다. 입력 grid SHA256은
`768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04`다.
실제 canonical run identity는
`7f89b12adbeee64a70832e633ae563584bc2a68f6ac433dc56f759a1946eb718`이다.

원 문서 일부의 identity 전사 오류는 그대로 보존하고, canonical manifest와
98개 COMPLETE/RESULT/STARTED 등의 identity, source/manifest/vendor 검증
15/15(서로 다른 파일 14개), 입력 grid 일치 근거로 정정 기록을 추가했다.
따라서 C21M 최초 마감의 `NCP98 NOT_RUN`은 당시 snapshot으로 유지하고,
현재 DAG에는 실제 반환 수용을 추가한다. 26개+중심1개+98개는 **125개 고유 좌표**다.
[정정·수용 근거](https://github.com/cosmosapjw-quantum/bass_cr/blob/0f45d0a422d79ccead565a8abaab860fcc230687/research/cr_c21n_mass_shell_cache_20261021/intake/NCP98_CORRECTION_RECORD.json).

반환 receipt는 2026-10-21 10:50:11 UTC 시작, 관측 host `s1a0e5abed09`,
Python 3.12.3 / NumPy 2.3.5 / SciPy 1.17.0, FP64 DOP853,
`rtol=3e-11`, `atol=3e-13`, 40성분×101시점, z20→4를 기록한다.
61개 worker CPU를 배정한 기록은 완료 실행의 운영 근거이며 64-core scaling
벤치마크나 독점 자원 보장은 아니다. 기록된 elapsed 13.18초도 benchmark로
해석하지 않는다. 원 output manifest는 6/7 byte 일치였고 남은 CSV는
LF↔CRLF 126개 개행 차이만으로 광고된 hash가 재현됐다. 실제 복원 파일은
509개, SHA256SUMS 항목은 508개다. 원 문서의 614개 표기를 검증된 수로 반복하지 않는다.

### Off-grid4: 외부 실행 네 개를 새 고유 입력으로 다시 세지 않음

PR94의 실제 source 17개와 입력 4개, raw/seal을 수용했다. 실행 content는
`5ecb8a6…`, grid SHA256은
`2a74af40c5508fc332dd3671955ad2dda6fc3e8de51bc61dcc3730a6798913b5`다.
NCP identity는 `a07a95f85042f9db7df2e3e465288524b458bcb6f190e9d4f01db1869c139360`,
sandbox identity는 `f42cb88bea0ebc3ed6114f092751ea9343dee9c46fbf474215fef2c9375c9023`다.
site와 Python 3.12.3/3.12.14 차이를 각각 보존했다. 두 환경 모두 NumPy 2.3.5,
SciPy 1.17.0과 같은 40성분×101시점 DOP853 문제를 사용했다.

네 NPZ container 전체가 byte-identical이었다. 그 안의 236개 FP64 배열,
52,520개 값도 일치하여 최대 절대 차이는 0이다. 수용 과정에서 새 ODE를
호출하지 않았다. 관측 NCP 실행 시작은 13:10:26 UTC, host는 위와 같고
reported solver wall time은 각 case 약 0.019–0.022초 범위다. 이 네 개는
이미 sandbox에서 완료한 네 입력이므로 고유 입력 수는 **125+4=129**로 유지된다.
129는 125개 Cartesian grid와 off-grid 4개의 합이며 Cartesian 129-grid가 아니다.
[고정 수용 영수증](https://github.com/cosmosapjw-quantum/bass_cr/blob/8dc5031b3323d4be42a7444843294200aa8887f2/research/cr_c21n_offgrid4_20261021/external_ncp4/NCP_RETURN_ACCEPTANCE.json).

두 CSV의 LF/CRLF byte 차이와 `content_tree`라는 이름의 64-hex run identity를
별도 설명했다. 중복 125개가 포함된 combined129 NPZ는 의도적으로 회수하지
않았으므로 해당 원 subtree 전체 복원이나 combined prefix 재검증을 주장하지 않는다.
과거 `off-grid4 NOT_RUN` 기록 역시 삭제하거나 소급 수정하지 않았다.

## 4. 최신 다른 저장소 결과의 수용 수준

아래는 새 head/직접 관련 source를 읽어 분류한 결과다. 이 표의 다른 모델 결과를
C21O source나 완료 trajectory로 자동 편입하지 않았다. 원문·source pin은
[GitHub intake ledger](github/INTAKE_LEDGER.json)와
[구체적인 source 판독 보고서](github/COUPLED_SOURCE_FINDINGS_KO.md)에 결속된다.

| 결과·관측 pin | 확인된 범위 | C21O에 대한 결정 |
|---|---|---|
| BASS_HE PR84 HE31 head `88e415c45d8607c85cd3ab36aabeaed4378820ce`; execution pin `1c8a56aac89d0e40ede8770009f80ebca40a4d2c` | 원 full40+tau Python, donor-on/off/reference 세 성공 결과. z20→4의 HII=HeII=Q, HeIII=0 donor이며 이전 serialization 실패 시도도 보존 | electron→Thomson 연결 방법·소스 참고. z2 donor 또는 self-consistent HHeLi 해로 채택하지 않음 |
| REI PR150 `fd9a21c4d3886a495540b51d780a83b608e72ea2` | native H/D/T/He 13상태와 별도 Li6/7 q0..3 rate module. 21-state registry 자체는 coupled solver 미구현 | registry·rate-domain 근거. CI/RR/DR의 공통 domain 제약을 숨겨 낮은 T로 외삽하지 않음 |
| REI PR211 RUN19 head `c9deb933761a8d2593d1176aee028cd423bdbc05`; source `e540256ecf77df1c88fccb57b81d5d60110f367c` | 기존 RUN13 HHeD finite-volume 경로와 rates/cache/batch, Li/Be 호환 경로. RUN19 새 native IVP는 0 | 최적화·부분 source 참고. 핵반응19·LiBe·Einstein closure 완료로 승격하지 않음 |
| REI PR151 Unit8 head `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`; Unit8 content `6391f3f8bbf34f16c7b36013d424183786a51086` | Verner photo/Milne/total-RR Python Provider. 과거 z100000→10000 trace-Li/BeEC, 첫13상태 frozen bath; 독립 BDF 비교 HOLD | **Provider·공식 표만 byte 그대로 재사용.** 과거 초기조건·late history·실패 gate는 이식하지 않음 |
| REI PR199 `cce008b3fc32c298185b30550b2cd909d74fcd87` | native time8/16/32 반환 이미 완료. 지정 차이는 감소했으나 .005 기준 미달, convergence HOLD | 완료 계산 재실행 없음. 새로운 HHeLi z20→2 결과로 수용하지 않음 |
| REI PR215 `926bae816ef8339137e2813cc40f1d514b763e1f`, BASS PR178 `215bb3e66d81a7013d2132831d210aee36234ab4` | C++17 folded96×32 massive moments, 따뜻한 C15 별도 계보 | native 방법 참고. 현재 fixed FV/chemistry source를 자동 교체하지 않음 |
| REI PR217 `de73c5d6c7bd3498571e9226298040d8259e1acf`, BASS PR179 `d14652646c1da77b6513e7f97725ff5dd5c1db4e` | 같은 NCP5/two-step 반환의 대응 분석. a=.1999→.2의 짧은 구간, 분석 새 ODE 0 | 두 저장소 사본을 독립 실행으로 중복 계산하지 않음. 전체 EoR 결과가 아님 |
| REC PR118 `99f5f4fb57358a0347286f8299977125a2724774` | JVP/VJP·160-state tangent, 작은 2개 ODE 보고. 전체 구간 세 입력은 READY_NOT_SUBMITTED | sensitivity 방법 참고. 완료된 z20→2 대형 계산으로 표시하지 않음 |
| HH PR132 `d43cf2df2c4864ae05049f44301c5b389b80a49c` | 실제 한 captured-coefficient cell의 enclosure; NCP finite prefix 세 개 READY_NOT_RUN | 국소 수학 근거. trajectory 전역 error bound로 적용하지 않음 |

이전 REI PR198의 625개 재사용+606개 신규와 PR213의 warm729는 이전에
분류된 별도 결과다. PR198의 source `b140170ce0c58159368b6b81be49ac35ca764851`,
delivery `8bd35af5f11c7ea5945b656be1c013d1c1933498`는 collisionless z20→4다.
PR213 head `d32cd99fa19c65aa1ca63dbc8aab8741834270e8`의 warm729는 a=.1999→.2다.
13:00에 작성된 진행 PDF가 이들을 설명하지만, 그 사본은 최신 branch head나
이번 원자 coupling 완료를 증명하지 않는다. 이번 intake는 위 완료 ODE를 재실행하지 않았다.

## 5. 재사용한 source와 새 C21O 계보의 경계

선택 source 16개(302,905 bytes)를 고정 ref에서 회수했고, 14개는 별도 Git blob
identity·크기와 대조했다. 나머지 두 문서는 pinned raw hash 수준이다.
공식 Verner 파일 6개(396,115 bytes)는 실제 다운로드 bytes가 원 R9 계약의
SHA256·크기와 6/6 일치했다. C21O vendor의 source manifest는
[ATOMIC_SOURCE_MANIFEST.json](../ATOMIC_SOURCE_MANIFEST.json)이다.

문헌 조사에는 SciSpace·Exa의 실제 요청과 primary source 열람을 사용했다.
문헌 도구가 추출한 표의 clean text는 계수 판독 근거이며 원 whitespace가
보존된 파일이라는 주장은 하지 않는다. 이 단계의 제한과 별개로, 실행에 들어간
vendor 6개 파일은 위 byte-verified 회수 경로로 확보했다.
[문헌 영수증](../theory/PRIMARY_SOURCE_RECEIPT_SANITIZED.json),
[조건부 network 유도](../theory/CONDITIONAL_NETWORK_THEORY_KO.md).

C21O는 사용자가 명시적으로 확장한 **새 물리 문제**다. H/D/T, He3/4,
Li6/7의 neutral/positive charge 20개와 neutron 1개, 대수적 electron을 사용한다.
실제 반응은 선언된 photon cohort의 valence photoionization, Case-A RR,
초기 parent가 0인 sourced beta adapter다. Electronic isotope equality,
prescribed UV/T, 등방 gas stress, trace gas electron→Thomson coupling을 명시한다.
Core/Auger, CI/DR/CX, 분자, Be7·Li8/9, 활성 핵충돌·완전 thermal/UV feedback은
완료된 것으로 표현하지 않는다. 과거 collisionless source를 소급 변경한 것도 아니다.
[물리 계약](../PHYSICAL_CONTRACT_KO.md).

현재 실제 완료된 C21O 결과는 **45개 grid + 별도 control 6개**, z20→2,
201개 저장 시각이다. L8은 62상태, L12 control은 78상태이고 실행 identity는
`c60d734b0ed8cc7d1a147e181da27c282e3f47be90f8b0eb1d65c030faabea0f`다.
이들은 새 sandbox 실행이며 외부 반환으로 표시하지 않는다. Raw/seal·source·
물리 불변량 검증은 51/51 `PASS_SCOPED`; 분석에서 새 ODE는 0이다.
[검증 영수증](../checks/TRAJECTORY_VALIDATION.json),
[분석 summary](../analysis_v2/SUMMARY.json).

독립 source/algebra 검토와 독립 그림 검토를 완료했다. 최종 그림은
`analysis_v2`이며 v1의 label·가독성 문제와 원 산출물도 보존했다. 세 과학 payload
`ENSEMBLE45.npz`, `ENDPOINTS45.csv`, `ION_HISTORY45.csv`는 v1/v2 byte-identical이다.
독립 검토는 PNG 5개와 PDF 2개를 직접 읽었고 나머지 PDF는 별도 raster 검토를
주장하지 않는다. [독립 물리 검토](../checks/INDEPENDENT_PHYSICS_REVIEW.json),
[독립 그림 검토](../checks/INDEPENDENT_PLOT_REVIEW.json).

## 6. 저장처 사본과 접근 불가 범위

이번 저장처 intake는 지정된 폴더·bounded search 범위다. Drive의 지정 폴더에서
72개 항목, Dropbox의 지정 BASS_CR 폴더에서 46개 항목을 관측했다. Library의
14:18 이후 결과는 이미 알려진 off-grid4 최종 권위 영수증 한 개였다.
선택한 관련 문서 5개는 provider-readable text를 끝까지 읽었으며 별도 raw 다운로드
검증으로 승격하지 않았다. [저장처 검색 영수증](backups/SCOPED_INTAKE_RECEIPT.json),
[문서 사본 목록](backups/SOURCE_DOCUMENTS_INDEX.json).

개인/다른 대화 검색은 이번 실제 1회 호출에서
**`Personal context is unavailable for this conversation.`** 응답으로
`UNAVAILABLE`였다. 다른 세션에 새 결과가 없다는 뜻이 아니다. 검색되지 않은
폴더, 비공개 대화, 외부 host의 현재 disk/resource는 확인 범위 밖이다.
과거 NCP의 host·CPU·RAM·disk receipt를 현재 자원 예약으로 사용하지 않는다.

이전 C21L/M 합본 백업의 완료 수준은 Library 다운로드 후 bytes 검증,
Dropbox ACK, Drive `UNKNOWN_NO_ACK`였다. C21N 본문/문서 백업과 off-grid4
두 배송본은 각각 Library·Dropbox ACK가 있었고 Drive는 unresolved였다.
이번 지정 Drive 폴더 조회에서도 두 off-grid4 배송 ZIP의 exact-name match는
없었으나, 이 사실만으로 전역 부재나 업로드 실패를 단정하지 않는다.
PR94 공급자가 별도 tar에 대해 보고한 Drive/Dropbox ACK·readback은 그 공급자
tar의 근거이며, 우리 다른 ZIP의 미확정 Drive 업로드를 해결하지 않는다.

이 문서는 C21O의 새 provider ACK를 생성하지 않는다. C21O 최종 content/document
게시 및 백업의 실제 SHA·provider ID·검증 수준은 root의 후속 권위 영수증에 결속한다.

## 7. 네 상태와 DAG의 현재 연결

| 단위 | EXECUTION | PUBLICATION | BACKUP | DAG |
|---|---|---|---|---|
| C21L component | 기존81 결과 재사용, 후처리 완료 | PR90 성분 content와 document head 확인 | 기존 L/M 합본의 확인 수준 재사용 | `COMPLETE_SCOPED` |
| C21M pilot | 신규26+재사용1 완료 | PR91 content/document 확인 | 위 합본과 문서 배송의 실제 영수증 유지 | 독립 IC builder·첫27 완료 |
| NCP98 반환 | 실제98 수용, intake ODE0 | PR92 반환, PR93의 정정·수용 기록 | 회수 tar의 실제 hash/509파일 범위 확인 | combined125 `COMPLETE_SCOPED_ACCEPTED` |
| C21N theory/cache | 기존125 재사용, 이 단위 새 ODE0 | PR93 content/document 확인 | Library·Dropbox ACK, Drive 미확정 | 국소 이론·구현 완료; 전역 remainder 미확립 |
| Off-grid4 + 외부 반환 | sandbox4, 같은 입력 NCP4 수용; 고유129 유지 | PR95 최종 branch 확인, PR metadata는 OPEN | Library·Dropbox ACK, Drive 미확정 | 네 입력 완료·중복 실행 차단 |
| 새 C21O | sandbox45+6 완료, 분석·후처리 ODE0 | 본 문서는 게시 전 합성본; 최종 commit은 별도 영수증 | 새 ACK는 본 문서가 주장하지 않음 | 조건부 z20→2 pilot 완료; 완전 핵반응/thermal/UV/CMB 확장 별도 미완료 |

`global_error_bound=null`을 유지한다. C21F/G/H/I/J/K의 원 science source,
역사적 HOLD·실패·NOT_PUBLISHED와 이후 완료 전의 NOT_RUN snapshot을 바꾸지 않는다.
새 C21O의 조건부 완료는 일반 triaxial Bianchi I, 완전 핵반응망,
stellar/UV/thermal self-consistency 또는 완성된 CMB Einstein–Boltzmann 예측의
완료를 뜻하지 않는다.
