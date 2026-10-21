# C21M 첫 독립 초기응력 pilot 마감

**Matter/radiation 독립 초기조건 builder와 첫 27점 pilot을 완료했다.** 실제 신규
적분은 26개이고 중심 1개는 C21L의 완료된 원 trajectory를 재사용했다. 두 성분의
signed stress, 각 tensor, norm, 상쇄와 부호 branch를 보존했으며 preliminary 그림을
완성했다. 이 문서는 scoped science와 실제 content 게시를 마감하고,
두 provider의 실제 백업 ACK 및 Drive의 미확정 상태를 구분해 결속한다.

## 권위 게시와 문서 계보

| 항목 | 확인된 식별자 |
|---|---|
| Draft PR | [BASS_CR PR91](https://github.com/cosmosapjw-quantum/bass_cr/pull/91) |
| C21M content commit | `659c94312eb9c12ebb987de934459c12a63d67b0` |
| C21M 연구 content 파일 수 | 263 |
| C21L component content | `17244259d25f793a25e0874443a28806e7c31d17` — PR90 |
| C21L 원 pilot content | `60a3f1cb0d8f0875820d18c0d10c448d480334c4` |
| REI 고정 물리 source | `3b85dedce84d37b3e165da00685a8a984950aafe` |
| 실제 신규26 run identity | `ff462f48e264b2032ec50018e9969a6eb1808c7a6fc2a60139b98efacb01c05a` |
| C21L document parent | `e954467132eef864a0fb86ba5de44f90f76b08e0` — 실제 문서 게시 영수증으로 결속 |
| C21M document SHA | 외부 최종 게시 영수증에서 결속; 본문에 자기 SHA를 만들지 않음 |

문서 마감 commit의 첫 parent는 C21M content이고 두 번째 parent는 C21L의 최종
문서 head로 결속한다. 이 문서 계보 연결은 C21L의 검사 범위 명료화와 마감 자료를
깨끗한 stack으로 수용하기 위한 것이다. 원 물리 source·solver·raw·분석 결과를
바꾸는 science commit으로 해석하지 않는다. 실제 parent와 document SHA는
외부 최종 게시 영수증과 Git commit object로 확인한다.

## 완료한 과학 단위

범위는 non-tilted, collisionless, LRS Bianchi I의 z20→4다. 원40성분 RHS, FP64,
DOP853 `n=101`, `rtol=3e-11`, `atol=3e-13`, L8, massive FV 24×12/Gauss3,
M/Tref=30, massive fraction 0.1을 유지했다.

초기 signed full Frobenius 격자는 S0=[−0.012,0,+0.012],
Pm0=Pr0=[−0.0002,0,+0.0002]의 직적이다. A를 바꿀 때마다 원 massive 분포의
weight·cell population·정규화를 다시 구성했다. A만 바꾸고 원 분포를 유지하는
shortcut을 사용하지 않았다. Photon과 실제 존재하는 massless neutrino는 공통 초기 k를
사용하지만 state와 결과에서 분리돼 있다.

원 source의 `Pi_*_J_m3`는 signed `pi_s=Delta p/3`다. Full tensor norm은
`sqrt(6)*abs(pi_s)`이며 source의 half norm보다 sqrt(2) 크다. H의 SI 단위를
반영한 signed 값과 nonnegative norm을 각각 기록했다. LRS 공통축의 signed
Ptot=Pm+Pr와 norm Pitot=abs(Pm+Pr)를 구별한다. 없는 UV와 별도 unmodeled gas를
존재하는 species의 수치 0으로 만들지 않았다.

중심은 C21L `s04_p04` raw를 재사용했다. 실제 초기 offset은
`Pm0=-2.111149637247e-19`, `Pr0=+2.1111496372470007e-19`이며 수정하지 않았다.
새 builder와 원 중심이 bitwise 같은 초기 상태라고 주장하지 않는다.

| z=4의 27점 ensemble 최대 norm | 실제 값 |
|---|---:|
| Sigma | `1.4449836382490454e-3` |
| Pi_m | `1.2574783729509532e-5` |
| Pi_r | `6.344480064794384e-5` |
| Pi_tot | `7.577499571350794e-5` |

초기 두 stress가 상쇄되는 S0=0의 두 case는 이후 Pi_m과 Pi_r의 서로 다른 진화로
최종 signed 총응력 약 ∓3.5632e-5와 shear 약 ∓2.4540e-5를 만든다. 이 현상은
독립 초기 성분 축을 유지해야 하는 물리적 이유다. 위 최대값은 이 ensemble에
한정되며 다른 초기 범위의 C21L 최대값과 성장률·성능 개선율로 비교하지 않는다.

과학 수치·정규화·그림의 상세 근거는 [REPORT_KO.md](REPORT_KO.md),
[analysis_pilot27/SUMMARY.json](analysis_pilot27/SUMMARY.json),
[INDEPENDENT_PILOT_REVIEW.json](INDEPENDENT_PILOT_REVIEW.json)에 있다.

## 검산과 독립 검토의 경계

| 검사 | 수행한 정확한 범위 |
|---|---|
| 초기 builder | 6개 focused 그룹과 독립 비구현자 검토; positivity·normalization·Hamiltonian·FLRW/r-only/m-only/opposing·domain refusal. 이 단계 ODE 0. |
| 실제 새 과학 실행 | Sandbox worker4가 신규26개 완료. 기존81과 원 중심을 다시 적분하지 않음. |
| 저장 trajectory의 물리 검사 | 신규26×101=2,626상태의 SI·tensor·full/half·cancellation·보존, 그리고 재사용 중심의 원 provenance 확인. |
| 원 unoptimized source 비교 | 시작·중간·끝 78상태에서 field scalar4,602개와 RHS3,120개를 FP64 bytes로 비교해 일치. 원 전체 trajectory를 재적분한 검사는 아님. |
| 복사 각분포 | 원64 Gauss angular nodes에서 L8 E/N을 복원한 672,256개 양수 값. 연속 각도·시간 positivity 증명이 아님. |
| 그림 검토 | 실제 PNG2개 직접 읽음. PDF의 별도 raster 검토는 `NOT_RUN`. |
| 다중 run 분석기 | 기존26+중심1에서 원 NPZ60개 배열·CSV 공통 값 동일, 중복 물리좌표 거부 fixture. 미래125 실행의 검증은 아님. |
| 공유 운영 검사 | Fake-worker, source binding, lease, queue, resume, 자원 계산의 focused 검사. 과학 적분이나 실제 NCP 성능 검증으로 집계하지 않음. |

초기축 최대 절대차는 `1.734723475976807e-18`, 저장 Hamiltonian 대수 잔차는
`2.220446049250313e-16`, massive comoving number 잔차는
`4.440892098500626e-16`이었다. Source에서 H를 constraint로 구성하므로 이 작은
Hamiltonian 값만으로 전체 적분 정확도를 증명하지 않는다.

C21L의 243상태 source field 비교는 **허용오차 0의 수치 일치**이며 별도의 byte
비교로 부르지 않는다. C21L 경로 재현11파일과 역사적 대표3 전체 trajectory의
bitwise 증거는 각각 구분한다. C21L 문서 parent에 추가한 scope clarification은
문서만의 수정이며 기존 게시 evidence를 바꾸지 않았다.

[INDEPENDENT_CLOSEOUT_REVIEW.json](INDEPENDENT_CLOSEOUT_REVIEW.json)은 이 범위에서
`PASS_SCOPED_PUBLICATION_READY`, promotion blocker 없음으로 기록했다. 본 문서 작성에서
새 테스트·ODE·benchmark를 수행하지 않았다. `global_error_bound=null`이다.

## 외부 방법과 결과의 수용

현재 관측 범위에서 일곱 관련 repo의 advertised branch1,224개를 열거하고 관련
source·입력·실행 반환·검토와 provider 자료를 조사했다. 접근하지 못한 다른 대화와
비공개 반환은 `UNAVAILABLE`이며 전역 부재를 주장하지 않는다.

REI PR198의 기존625 분해와 matter600+mixed6는 같은 PR147 physics를 쓰지만
reduced8-state·65시점·half-contraction provenance를 유지해 수용했다. 외부606 전체
raw의 신규 독립 검증으로 확대하지 않았다. HH63은 초기 A=0 control이다. REI213/
BASS176의729와 REC116의 후처리는 같은 C15 warm source-on 계열이므로 mirror와
후처리를 새 적분 수로 중복 계산하지 않는다. 자세한 SHA·toolchain·runtime·수용
범위는 [EXTERNAL_UPTAKE.json](EXTERNAL_UPTAKE.json)에 있다.

REC116의 축 재구성 방법을 실제 C21M27에서 별도로 검산했다. Support15만으로
예측하고 held-out mixed12×101시점에서 비교한 최대 절대잔차는 signed S
`1.2601685821e-9`, Pm `1.1647880057e-9`, Pr `1.4831875142e-9`, Ptot
`2.5829708927e-9`다. 작은 총응력 분모에서 pointwise 상대잔차가 5.425까지
커지는 사실도 보존했다. 임의 floor로 가리지 않았다.

최종 채택 경로는 `axis_response_diagnostic_results_v2/`다. v2는 Decimal80의
유한 정밀도 계산을 exact rational로 부르지 않도록 명칭을 바로잡았다. v1 source와
결과를 보존했고 NPZ와 두 CSV bytes는 같다. 외부 방법의 사후 진단을 수용한 것이며
solver 대체, production surrogate, 새 성능 개선 또는 전역 오차 상계를 승인하지 않았다.

## 다음 NCP 단위는 선택적인 신규98점

`grid_ncp_refinement98.json`은 nested5×5×5의125점에서 이미 완료한27점을 제외한
98개 신규 요청 좌표다. SHA256은
`768643862b317ba3d159af6503ebb80141028dc8c671fdb00a9d0a68b32fde04`다.
98개 초기 분포의 positivity·normalization·사상만 검사했으며 ODE는 `NOT_RUN`이다.
이는 첫 pilot27 마감의 필수 미완료분이 아니다.

현재 sandbox에 `/home/cosmosapjw/.ssh/ncp_key`가 없었고 key 내용은 읽지 않았다.
실제 NCP 접속·자원 probe·science 실행은 `NOT_RUN`, 현재 CPU/memory/load는
`UNOBSERVED`다. 준비된 `ncp_run.sh`와 `analyze_campaign.py`를 사용하면 NCP에서
독립 content checkout·현장 경로/환경 조정·실제 자원 관측 후98점을 실행하고
기존26+새98+원중심1의125점을 결합할 수 있다.

명목64CPU/128GB, worker62 요청 상한을 실제 할당이나 scaling 측정으로 해석하지
않는다. CPU55, coordinator 비용, single-thread 수치 library, 기존 공유 lease,
현재 quota·affinity·가용 RAM·부하를 고려한다. 다른 owner의 작업을 변경하거나
종료하지 않고 새 dispatch를 조절한다. 실제 세부 명령은
[NCP_REFINEMENT98_KO.md](NCP_REFINEMENT98_KO.md)와 별도 Codex handoff에 있다.

## 배송·provider와 네 상태

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
내려받은 bytes에 대해 각각 계산했다. [정규화 백업 영수증](../cr_c21l_rei_pilot_20261021/component_closeout_20261021/BACKUP_RECEIPT.json)에
원 ACK 파일명과 검증 단계를 분리했다. [Library 다운로드 검증](../cr_c21l_rei_pilot_20261021/component_closeout_20261021/LIBRARY_DOWNLOAD_REVALIDATION.json)도 보존했다.

이전 stage-B C21L ZIP의 Drive 호출도 1,216.3초 뒤 중단되었고 ACK를 받지 못했다.
그 호출은 `AMBIGUOUS_NO_ACK`로 남겼다. 같은 파일을 확인 없이 재업로드하지 않았다.
통합 배송은 C21M을 추가한 별도 버전이며 원 배송본을 덮어쓰지 않았다.
Drive의 두 모호한 반환은 해당 object를 조회하고, 발견되면 실제 bytes를 검증하여
해소해야 할 독립적인 미완료 백업 노드다. 과학·GitHub 게시 완료와 구분한다.

| 상태 | 이 문서 commit에서 보존한 상태 |
|---|---|
| EXECUTION | 신규26 + 기존 중심1 재사용으로 pilot27 완료; 기존81 ODE 재실행 없음 |
| PUBLICATION | C21L component 및 document, C21M content 및 이 document commit을 PR90/91의 draft에 게시 |
| BACKUP | 통합 연구 ZIP은 Library 다운로드 bytes 검증, Dropbox 완료 ACK. Drive ACK 복구는 OPEN |
| DAG | 첫 pilot27 COMPLETE_SCOPED_PRELIMINARY; 선택 NCP98 NOT_RUN; 일반화 확장 HOLD |

기계 판독 상태는 [FINAL_RESEARCH_DAG.json](FINAL_RESEARCH_DAG.json)을 따른다.
복사 가능한 명령은 [CODEX_NCP_HANDOFF_KO.md](CODEX_NCP_HANDOFF_KO.md), 다음 대화용
인계는 [NEXT_THREAD_HANDOFF_KO.md](NEXT_THREAD_HANDOFF_KO.md)에 있다. 자기 commit SHA는
외부 최종 권위 영수증 및 실제 SHA를 채운 배포용 두 파일에서 결속한다.

일반 triaxial, full H/He/UV/stars 재이온화 역사, 완성 CMB Einstein–Boltzmann 예측은
HOLD다. 기존 C21F/G/H/I/J/K의 source, 실패 raw, 역사적 NOT_PUBLISHED, 통과 범위와
HOLD는 그대로 보존했다. global_error_bound=null이다.
