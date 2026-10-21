# C21L 성분 분리 단계 마감

**C21L의 기존 81개 trajectory를 재사용한 matter/radiation 성분 분리와 content
게시는 완료했다. 이 단계에서 새 물리 ODE는 실행하지 않았다.** 조사한 범위에서 원본을 회수하지 못한
미게시 후처리를 고정 raw에서 재구성했고, source·정규화·부호·tensor 합·경로 재현성을
검증한 뒤 PR90의 content로 게시했다. 최종 배송의 provider 확인은 별도 영수증에
결속하며, 아래의 미확정 상태를 ACK 완료로 해석하지 않는다.

## 게시와 source identity

| 항목 | 확인된 값 |
|---|---|
| Repository | `cosmosapjw-quantum/bass_cr` |
| Draft PR | [PR90](https://github.com/cosmosapjw-quantum/bass_cr/pull/90) |
| Branch | `research/cr-c21l-rei-sigma-pi-pilot-20261021` |
| Component content commit | `17244259d25f793a25e0874443a28806e7c31d17` |
| 원 81-case content | `60a3f1cb0d8f0875820d18c0d10c448d480334c4` |
| REI 고정 물리 source | `3b85dedce84d37b3e165da00685a8a984950aafe` |
| 원 run identity | `0090e1549b21b07e46001de2bf9cb2eab9bf0cba87ffe3d4d824ba117fecb44a` |
| 이 마감 문서의 commit | 외부 최종 게시 영수증에서 결속; 본문에 자기 SHA를 만들지 않음 |

원 content 340개 파일과 후속 component content 31개 파일을 합친 **371개 연구
content 파일**을 보존한다. 원 raw와 v1/v2 provenance를 바꾸지 않았다. 최신 REI
branch가 있어도 원 실행의 source는 위 SHA로 유지한다.

## 실제 수행과 결과

범위는 non-tilted, collisionless, LRS Bianchi I의 z20→4, 초기 massive 분포 A=0인
81개 ensemble이다. 이 분석을 독립 초기 (P_{m,0},P_{r,0}) sweep로 재분류하지 않는다.

Source의 `Pi_matter_J_m3`, `Pi_gamma_J_m3`, `Pi_nu_J_m3`는 signed scalar
`pi_s,X = Delta p_X/3`이다. 직교기저 tensor는
`diag(-pi_s,X,-pi_s,X,2*pi_s,X)`이며 full Frobenius norm은
`sqrt(6)*abs(pi_s,X)`다. Shear `diag(-s,-s,2s)`의 norm도 `sqrt(6)*abs(s)`다.
H가 s^-1이고 stress가 J/m^3이므로 signed 좌표는
`P_X = sqrt(6)*(8*pi*G/c^2)*pi_s,X/H^2`를 사용했다. 이는
`kappa=8*pi*G/c^4`, `H_geom=H/c` 표현과 같다. Half-contraction 값은 full의
1/sqrt(2)다. Scalar norm과 signed 좌표를 각각 보존했다.

Photon과 존재하는 massless neutrino를 따로 보존하고 radiation tensor로 합했다.
Dust는 source의 isotropic 모델 가정으로 stress가 0이며, UV와 진화시키지 않은
재이온화 gas는 absent/unavailable로 구분한다. 없는 species를 존재하는 수치 0으로
추가하지 않았다. Π_tot는 성분 norm의 합이 아니라 합한 tensor의 norm이다.

| z=4의 ensemble 최대 norm | 값 |
|---|---:|
| Sigma | `0.00481987955610218` |
| Pi_m | `3.828814781835141e-6` |
| Pi_r | `2.9216326786315474e-4` |
| Pi_tot | `2.9587955662661403e-4` |

각 최대값은 서로 다른 case일 수 있으며 보편적 상계가 아니다. Signed cancellation은
원 배열에 그대로 남겼다. 분모가 정확히 0인 cancellation은 undefined mask와 NaN으로
표현한다. 그림에서 사용한 표시 threshold는 범례에 명시했고 raw를 clipping하지 않았다.
수치와 해석의 근거는 [component 보고서](component_split_20261021/REPORT_KO.md),
[최종 summary](component_split_20261021/results_final_v4/SUMMARY.json)에 있다.

## 정확한 검산 범위

| 검사 | 실제 범위 | 확대하지 않는 주장 |
|---|---|---|
| 독립 tensor·SI·full/half 검사 | 81×101 = 8,181개 저장 시점 | 연속 시간·전체 parameter domain 증명이 아님 |
| 원 source field 재평가 | 81개 case의 시작·중간·끝 243상태, 13개 scalar/array field, rtol=atol=0의 수치 일치, 최대차 0 | 개별 FP64 bytes·signed-zero 비교라고 부르지 않음 |
| 외부 input/output 경로 재현 | Git 원 raw와 별도로 복원한 Drive raw에서 CSV/NPZ/PNG/PDF/manifest 11개 파일의 bytes 동일 | 새 ODE 재실행이 아님 |
| 원 solver와 재사용 solver의 대표3 전체 trajectory | 이전 실행의 bitwise 증거를 그대로 수용 | 이번 243상태 검사와 합쳐 확대하지 않음 |
| 그림 직접 검토 | 채택 PNG 3개 | PDF의 별도 raster 검토는 미실행 |

근거는 [REVIEW_COMPONENTS.json](component_split_20261021/REVIEW_COMPONENTS.json),
[PATH_REPRODUCTION_CHECK.json](component_split_20261021/PATH_REPRODUCTION_CHECK.json),
[검사 범위 명료화](component_split_20261021/CHECK_SCOPE_CLARIFICATION.json)다.

이번 문서 추가는 **문서만의 명료화**다. 243상태의 수치 일치와 별도의 bytes 일치를
구분하기 위한 것이며, 이미 게시된 report·review·raw를 수정하지 않았다. 새로운 field
평가, 테스트, ODE, benchmark도 실행하지 않았다. Hamiltonian의 작은 대수 잔차는
전체 적분 오차 상계가 아니다. `global_error_bound=null`을 유지한다.

## 백업 상태와 모호한 이전 전송의 보존

새 통합 배송본은 C21L 371개와 C21M 263개, 총 **634개 고정 연구 파일**을 담는다.
Wrapper와 manifest를 포함한 archive 파일은 642개다. 모든 연구 파일을 실제 Git
blob·크기·SHA256과 대조했고 ZIP CRC와 내부 manifest도 검증했다. 이 문서 마감에서
추가하는 파일은 뒤따르는 별도 문서 배송본에 결속한다.

```text
BASS_CR_C21LM_RESEARCH_DELIVERY_20261021T082802Z.zip
bytes  = 17539759
SHA256 = e0592be2859b7db606ec5a2ca008015c5ab02a3b2ff09fdd97fafe209cfe167a
```

| 저장처 | 실제 식별자와 상태 | 수행한 검증 |
|---|---|---|
| Library | `libfile_9ec015516fd48191bf149640f43bea7a`, `ACK_SUCCEEDED` | Provider 크기 일치. 실제 1회 다운로드 뒤 17,539,759 bytes와 SHA256 일치. |
| Dropbox | `id:BSpOijBcT10AAAAAAD_fqQ`, `ACK_COMPLETED` | Provider 크기 일치. 다운로드 재검증은 미수행. |
| Google Drive | ID 미수신, `UNKNOWN_NO_ACK` | 320초 대기 후 root가 응답 없는 호출을 중단. 정확한 폴더·파일명 조회 결과 0. 객체 부재나 업로드 실패를 확정하지 않음. |

Provider가 SHA256을 직접 반환한 것은 아니다. 위 SHA256은 로컬 ZIP과 Library에서
내려받은 bytes에 대해 각각 계산했다. [정규화 백업 영수증](component_closeout_20261021/BACKUP_RECEIPT.json)에
원 ACK 파일명과 검증 단계를 분리했다. [Library 다운로드 검증](component_closeout_20261021/LIBRARY_DOWNLOAD_REVALIDATION.json)도 보존했다.

이전 stage-B C21L ZIP의 Drive 호출도 1,216.3초 뒤 중단되었고 ACK를 받지 못했다.
그 호출은 `AMBIGUOUS_NO_ACK`로 남겼다. 같은 파일을 확인 없이 재업로드하지 않았다.
통합 배송은 C21M을 추가한 별도 버전이며 원 배송본을 덮어쓰지 않았다.
Drive의 두 모호한 반환은 해당 object를 조회하고, 발견되면 실제 bytes를 검증하여
해소해야 할 독립적인 미완료 백업 노드다. 과학·GitHub 게시 완료와 구분한다.

## 네 상태와 후속 연구 연결

| 상태 | 이번 마감의 의미 |
|---|---|
| EXECUTION | C21L component 후처리·검산 `COMPLETE_SCOPED`; 새 ODE 0 |
| PUBLICATION | Component content `17244259…`와 이 문서 commit은 PR90의 draft에 게시; 실제 document SHA는 외부 게시 영수증 참조 |
| BACKUP | Library 다운로드 bytes 일치, Dropbox 완료 ACK; Drive 모호성은 OPEN |
| DAG | C21L component 단계 완료; C21M의 별도 신규 pilot과 source lineage만 연결 |

후속 C21M의 신규26+재사용중심1 pilot27은 별도 [PR91](https://github.com/cosmosapjw-quantum/bass_cr/pull/91),
content `659c94312eb9c12ebb987de934459c12a63d67b0`에서 완료했다. NCP98는 선택적인
다음 refinement이며 C21L 단계의 미완료 항목으로 되돌리지 않는다. 실제 NCP
접속·자원 관측·science 실행은 key 부재로 `NOT_RUN`이며 현재 실자원은 미관측이다.

`C21L_FINAL_DAG.json`은 이 문서의 상태를 기계적으로 보존한다. 일반 triaxial,
full H/He/UV/stars 재이온화 및 완성 CMB 확장은 `HOLD`다. 기존 C21F/G/H/I/J/K의
원 science, 통과 범위, 실패 raw, 역사적 `NOT_PUBLISHED`와 `HOLD`를 바꾸지 않는다.
